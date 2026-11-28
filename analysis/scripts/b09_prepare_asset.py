"""Asset intake: cut-out, cleanup and upscale for user-supplied / generated illustrations.

usage: python b09_prepare_asset.py <in.png> <out.png> [--min-height 2100]
1. alpha: use the PNG alpha if present and non-trivial; else key flat green (#00FF00-ish) with a soft chroma matte
2. despill: remove green cast from semi-transparent edge pixels
3. defringe: erode alpha by 1 px, then 0.6 px feather; decontaminate edge colour from the background
4. upscale 4x with Real-ESRGAN anime 6B (tiled, CPU) until height >= --min-height, then Lanczos to exactly the target
5. trim to the alpha bounding box + 2 % margin; save RGBA PNG; write a QA sheet (on black, on white, on magenta) next to it
"""
import sys, argparse, numpy as np, cv2, torch
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('--min-height', type=int, default=2100); a = ap.parse_args()
im = Image.open(a.inp).convert('RGBA'); rgba = np.array(im).astype(np.float32)/255
rgb, alpha = rgba[..., :3], rgba[..., 3]
if alpha.min() > 0.99:   # no transparency -> chroma key green
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = g - np.maximum(r, b)                     # > 0.35 on the screen
    alpha = np.clip(1 - (green - 0.08)/(0.30 - 0.08), 0, 1)
    # despill: clamp green to max(r, b) where the pixel is partly keyed or near the edge
    edge = cv2.dilate((alpha < 0.999).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    g2 = np.where(edge, np.minimum(g, np.maximum(r, b)), g)
    rgb = np.stack([r, g2, b], -1)
# defringe: erode 1 px, feather 0.6 px; decontaminate colour by pulling edge pixels toward the nearest opaque colour
a8 = (alpha*255).astype(np.uint8)
a8 = cv2.erode(a8, np.ones((3, 3), np.uint8), iterations=1)
alpha = cv2.GaussianBlur(a8.astype(np.float32)/255, (0, 0), 0.6)
solid = (alpha > 0.98).astype(np.uint8)
inpaint = cv2.inpaint((np.clip(rgb, 0, 1)*255).astype(np.uint8), (1-solid).astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32)/255
rgb = np.where(alpha[..., None] < 0.98, inpaint, rgb)

def esrgan(x):
    import spandrel
    m = spandrel.ModelLoader().load_from_file('work/models/RealESRGAN_x4plus_anime_6B.pth').model.eval(); torch.set_num_threads(4)
    H, W, _ = x.shape; t = 192; ov = 16; out = np.zeros((H*4, W*4, 3), np.float32); wsum = np.zeros((H*4, W*4, 1), np.float32)
    for y in range(0, H, t-2*ov):
        for xx in range(0, W, t-2*ov):
            y0, x0 = max(0, y-ov), max(0, xx-ov); y1, x1 = min(H, y0+t), min(W, x0+t)
            tile = torch.from_numpy(x[y0:y1, x0:x1].transpose(2, 0, 1)[None].copy())
            with torch.no_grad(): o = m(tile)[0].numpy().transpose(1, 2, 0)
            wgt = np.ones(o.shape[:2] + (1,), np.float32)
            out[y0*4:y1*4, x0*4:x1*4] += o*wgt; wsum[y0*4:y1*4, x0*4:x1*4] += wgt
    return np.clip(out/np.maximum(wsum, 1e-6), 0, 1)
H0 = rgb.shape[0]
if H0 < a.min_height:
    up = esrgan(np.clip(rgb, 0, 1).astype(np.float32))
    al = cv2.resize(alpha, (up.shape[1], up.shape[0]), interpolation=cv2.INTER_CUBIC)
    al = np.clip(cv2.GaussianBlur(al, (0, 0), 0.8), 0, 1)
    scale = a.min_height/up.shape[0] if up.shape[0] > a.min_height else 1.0
    if scale != 1.0:
        up = cv2.resize(up, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4); al = cv2.resize(al, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
    rgb, alpha = up, np.clip(al, 0, 1)
ys, xs = np.where(alpha > 0.02); m = int(0.02*max(rgb.shape[:2]))
y0, y1, x0, x1 = max(0, ys.min()-m), min(rgb.shape[0], ys.max()+m), max(0, xs.min()-m), min(rgb.shape[1], xs.max()+m)
rgb, alpha = rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]
out = np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])
Image.fromarray((out*255).round().astype(np.uint8)).save(a.out)
qa = []
for bg in ([0, 0, 0], [1, 1, 1], [1, 0, 1]):
    comp = rgb*alpha[..., None] + np.array(bg)*(1-alpha[..., None]); qa.append(comp)
sheet = np.hstack([cv2.resize(q, (int(q.shape[1]*600/q.shape[0]), 600), interpolation=cv2.INTER_AREA) for q in qa])
Image.fromarray((np.clip(sheet, 0, 1)*255).astype(np.uint8)).save(a.out.replace('.png', '_QA.jpg'))
print('saved', a.out, out.shape)
