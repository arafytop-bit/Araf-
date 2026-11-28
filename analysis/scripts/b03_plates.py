"""Procedural texture plates for the calibration rebuild (style_bible.md §5-§7). All outputs are original, code-generated.

render/public/hq/sky_portrait.png   3840x2160 dithered sky gradient (screen space)
render/public/hq/wall.png           world texture for the poster shot: 3 px per ref px, world x -427..1281, y -240..720
render/public/hq/paper_main.png     poster paper RGBA (3 px per ref px) incl. torn alpha + notch + edge burn + stains + folds
render/public/hq/paper_side_{k}.png side-poster papers (other seeds)
render/public/hq/ink_wear.png       tileable grunge mask (white = ink kept)
"""
import numpy as np, cv2, os, json
from PIL import Image
OUT = 'render/public/hq'; os.makedirs(OUT, exist_ok=True)
rng0 = np.random.default_rng(7)
def hx(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32)
def save(img, path, alpha=None):
    # triangular dither before 8-bit quantisation (kills banding)
    img = np.clip(img + rng0.triangular(-1, 0, 1, img.shape).astype(np.float32), 0, 255)
    arr = img.astype(np.uint8)
    if alpha is not None:
        arr = np.dstack([arr, np.clip(alpha*255, 0, 255).astype(np.uint8)])
    Image.fromarray(arr).save(path, optimize=False, compress_level=4)
def fbm(h, w, scale, octaves=5, seed=0, aniso=(1.0, 1.0)):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        sy = max(2, int(h/(scale*aniso[1])*2**o)); sx = max(2, int(w/(scale*aniso[0])*2**o))
        n = rng.standard_normal((sy, sx)).astype(np.float32)
        out += amp*cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp; amp *= 0.5
    out /= tot; return out/(out.std()+1e-6)

# ---------------- sky (screen space, 3840x2160) ----------------
W, H = 3840, 2160; k = H/480
stops = [(0, '#381a2e'), (25, '#4e2036'), (50, '#6c2638'), (75, '#8e3238'), (100, '#a83e38'), (125, '#bf4e38'), (150, '#d0603c'),
         (175, '#de6c3c'), (200, '#e67840'), (225, '#ec8642'), (255, '#f09248'), (290, '#f5a250'), (330, '#f7aa56'), (480, '#f7aa56')]
ys = np.array([s[0]*k for s in stops]); cols = np.array([hx(s[1]) for s in stops])
yy = np.arange(H)
sky = np.stack([np.interp(yy, ys, cols[:, c]) for c in range(3)], 1)[:, None, :].repeat(W, 1).astype(np.float32)
# warm horizontal lift toward the sun side + very soft large-scale variation (no clouds in the reference)
xx = np.arange(W)[None, :, None]
sun = np.array([325*k, 286*k])
d = np.sqrt(((np.arange(W)[None, :]-sun[0])**2)*0.6 + ((np.arange(H)[:, None]-sun[1])**2))
glow = np.exp(-(d/(260*k))**2)[..., None]
sky = sky*(1-0.35*glow) + hx('#fbb15c')*0.35*glow
sky += fbm(H, W, 700, 3, seed=3)[..., None]*3.5
save(sky, f'{OUT}/sky_portrait.png')

# ---------------- wall (world texture, 3 px per ref px) ----------------
S = 3; X0, X1, Y0, Y1 = -427, 1281, -240, 720
WW, WH = (X1-X0)*S, (Y1-Y0)*S
rng = np.random.default_rng(11)
plank_w = 66.7*S
tones = [hx('#843e16'), hx('#7c3a14'), hx('#883f18'), hx('#803c16'), hx('#7a3814'), hx('#863e18')]
wall = np.zeros((WH, WW, 3), np.float32)
# plank boundaries aligned with the reference gap positions (x = 45,112,178,245 ref at frame 75 -> period 66.7, phase 45)
first = (45 - X0) % 66.7
edges = np.arange(first*S - plank_w, WW + plank_w, plank_w)
grainN = fbm(WH, WW, 60, 4, seed=5, aniso=(0.08, 3.0))   # long vertical streak noise
fine = fbm(WH, WW, 6, 3, seed=6)
for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
    a0, b0 = int(max(0, a)), int(min(WW, b))
    if b0 <= a0: continue
    t = tones[rng.integers(len(tones))] * (1 + rng.uniform(-0.03, 0.03))
    wall[:, a0:b0] = t
    # subtle per-plank vertical shading (slightly darker towards both edges)
    xs = (np.arange(a0, b0) - a)/plank_w
    edge_d = np.minimum(np.arange(a0, b0) - a, b - np.arange(a0, b0))
    wall[:, a0:b0] *= ((1 - 0.03*np.abs(xs-0.5)*2) * (1 - 0.08*np.clip(1 - edge_d/14, 0, 1)))[None, :, None]
wall *= (1 + 0.008*grainN + 0.03*fbm(WH, WW, 120, 3, seed=19))[..., None]
wall += fine[..., None]*0.2
# grain streaks: sparse thin darker wavy lines
for _ in range(int(WW/plank_w*6)):
    x = rng.uniform(0, WW); y = rng.uniform(0, WH); L = rng.uniform(60, 260)*S
    ph = rng.uniform(0, 6)
    pts = [(x + 0.7*np.sin(s_*3 + ph), y + s_*L) for s_ in np.linspace(0, 1, 30)]   # straight, thin vertical grain lines (reference)
    cv2.polylines(wall, [np.int32(pts)], False, (wall[int(min(WH-1, y)), int(min(WW-1, x))]*0.83).tolist(), thickness=2, lineType=cv2.LINE_AA)
# plank seams are drawn as crisp vector strokes in CalibrationHQ.tsx (WallSeams), so they stay sharp at every camera zoom like the reference's
# knots (from the reference: near (87,28) and (218,477) ref) plus a few more
for (kx, ky) in [(87, 28), (218, 477), (-260, 330), (640, -150), (1050, 120), (420, 610), (-120, -60), (930, 560)]:
    cx, cy = int((kx-X0)*S), int((ky-Y0)*S)
    kn = np.zeros(wall.shape[:2], np.float32); cv2.ellipse(kn, (cx, cy), (15, 26), rng.uniform(-8, 8), 0, 360, 1.0, -1, cv2.LINE_AA)
    kn = cv2.GaussianBlur(kn, (0, 0), 2.2); wall = wall*(1-0.9*kn[..., None]) + hx('#2e1404')*0.9*kn[..., None]
    cv2.ellipse(wall, (cx, cy), (19, 31), 0, 0, 360, (hx('#a05a2a')).tolist(), 2, cv2.LINE_AA)
# nail-hole row at y=272 ref, one per plank, plus a second row near the top
for e in edges:
    for yy_ in (272, -150, 640):
        cx, cy = int(e + plank_w*rng.uniform(0.35, 0.65)), int((yy_ + rng.uniform(-3, 3) - Y0)*S)
        if 0 <= cx < WW and 0 <= cy < WH:
            nl = np.zeros((40, 40), np.float32); cv2.circle(nl, (20, 20), 6, 1.0, -1, cv2.LINE_AA); nl = cv2.GaussianBlur(nl, (0, 0), 1.6)
            y0_, x0_ = cy-20, cx-20
            if 0 <= y0_ and y0_+40 <= WH and 0 <= x0_ and x0_+40 <= WW:
                wall[y0_:y0_+40, x0_:x0_+40] = wall[y0_:y0_+40, x0_:x0_+40]*(1-0.8*nl[..., None]) + hx('#2a1208')*0.8*nl[..., None]
wall = cv2.GaussianBlur(wall, (0, 0), 0.6)
save(wall, f'{OUT}/wall.png')

# ---------------- paper ----------------
def paper(seed, w_ref=315.3, h_ref=453.3, notch=True, aged=1.0, avoid=None):
    rng = np.random.default_rng(seed); w, h = int(w_ref*S), int(h_ref*S)
    gy = np.linspace(0, 1, h)[:, None, None]
    img = (hx('#ecca86')*(1-gy*0.4) + hx('#e8c27e')*gy*0.4) * np.ones((h, w, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    centre = np.exp(-(((xx-w/2)/(0.42*w))**2 + ((yy-h*0.45)/(0.45*h))**2))
    img *= (0.94 + 0.11*centre)[..., None]                       # lit centre (reference: p95 202 vs median 188 in the list area)
    img += fbm(h, w, 5, 3, seed=seed+2)[..., None]*0.15          # barely-there fibre
    # round, evenly translucent disc stains (reference look), kept off the portrait box
    placed = 0; tries = 0
    while placed < int(5*aged) and tries < 200:
        tries += 1
        cx, cy = rng.uniform(0.08*w, 0.92*w), rng.uniform(0.12*h, 0.95*h); rx = rng.uniform(70, 130); ry = rx*rng.uniform(0.75, 1.25)
        if avoid is not None and avoid[0]-rx*0.5 < cx < avoid[2]+rx*0.5 and avoid[1]-ry*0.5 < cy < avoid[3]+ry*0.5: continue
        dd = np.sqrt(((xx-cx)/rx)**2 + ((yy-cy)/ry)**2)
        m = cv2.GaussianBlur((dd < 1).astype(np.float32), (0, 0), 4.5)
        a_ = rng.uniform(0.4, 0.55); col = hx('#d0a262')
        img = img*(1-a_*m[..., None]) + col*a_*m[..., None]; placed += 1
    fx = int(w*0.5 + rng.uniform(-4, 4))
    img[:, fx-1:fx+2] *= 0.88; img[:, fx+2:fx+5] *= 1.03
    fy = int(h*0.56); img[fy:fy+2, :] *= 0.94; img[fy+2:fy+4, :] *= 1.03
    def edge(n, amp, seed_, hf=0.05):
        r_ = np.random.default_rng(seed_)
        v = cv2.GaussianBlur(r_.normal(0, 1, n).reshape(1, -1).astype(np.float32), (0, 0), 22).ravel()
        v = v/(np.abs(v).max()+1e-6)*amp
        v += cv2.GaussianBlur(r_.normal(0, 1, n).reshape(1, -1).astype(np.float32), (0, 0), 2).ravel()*amp*hf
        return v
    pad = 20
    top = edge(w, 4.5, seed+10, 0.04); bot = edge(w, 7, seed+11, 0.16); left = edge(h, 3.5, seed+12, 0.06); right = edge(h, 7, seed+13, 0.12)
    xs = np.arange(pad, w-pad, 3); ys = np.arange(pad, h-pad, 3)
    poly = [(x, pad + top[x]) for x in xs] + [(w - pad - right[y], y) for y in ys]
    bpts = [(x, h - pad - bot[x]) for x in xs[::-1]]
    if notch:
        nx = int((533-278+6.7)/w_ref*w); nw = 44; nd = 56
        bpts = [(x, y - nd*(1-abs(x-nx)/nw)) if abs(x-nx) < nw else (x, y) for (x, y) in bpts]
    poly += bpts + [(pad + left[y], y) for y in ys[::-1]]
    alpha = np.zeros((h, w), np.uint8); cv2.fillPoly(alpha, [np.int32(poly)], 255, cv2.LINE_AA)
    alpha = cv2.GaussianBlur(alpha.astype(np.float32)/255, (0, 0), 0.6)
    dist = cv2.distanceTransform((alpha > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    tint = np.clip(1 - dist/95, 0, 1)**1.7
    img = img*(1-0.55*tint[..., None]*aged) + hx('#b47436')*0.55*tint[..., None]*aged
    lip = np.clip(1 - dist/2.5, 0, 1); img = img*(1-0.45*lip[..., None]) + hx('#f3dcae')*0.45*lip[..., None]
    return img, alpha
img, a = paper(21, avoid=((328-278+6.7)*S, (98-22+6.7)*S, (528-278+6.7)*S, (232-22+6.7)*S)); save(img, f'{OUT}/paper_main.png', a)
for kk in range(4):
    img, a = paper(100+kk, 213.3, 293.3, notch=bool(kk % 2), aged=1.3); save(img, f'{OUT}/paper_side_{kk}.png', a)

# ---------------- ink wear mask (tileable 1024) ----------------
n = 1024; m = fbm(n, n, 3, 2, seed=77); m2 = fbm(n, n, 30, 3, seed=78)
wear = np.clip(1.0 - (np.clip(m - 1.6, 0, None)*0.9 + np.clip(m2 - 1.2, 0, None)*0.35), 0, 1)
Image.fromarray((wear*255).astype(np.uint8)).save(f'{OUT}/ink_wear.png')
json.dump(dict(wall=dict(px_per_ref=S, world=[X0, Y0, X1, Y1]), paper=dict(px_per_ref=S, main_world_box=[278, 22, 580, 462], pad_px=20)), open(f'{OUT}/plates.json', 'w'), indent=1)
print('ok')
