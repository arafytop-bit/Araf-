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
sun = np.array([325*k, 289.5*k])
d = np.sqrt(((np.arange(W)[None, :]-sun[0])**2)*0.6 + ((np.arange(H)[:, None]-sun[1])**2))
glow = np.exp(-(d/(260*k))**2)[..., None]
sky = sky*(1-0.35*glow) + hx('#fbb15c')*0.35*glow
sky += fbm(H, W, 700, 3, seed=3)[..., None]*3.5
# ---- static radial overlays baked here in float + dither, instead of 8-bit SVG gradients (those left 1-level contour rings) ----
# Each reproduces the CalibrationHQ SVG element it replaces: same centre, radius, stops, opacity and blend.
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
def radial(cx, cy, r, st):            # st: [(offset, '#hex', opacity)] -> (rgb HxWx3 in 0..255, alpha HxW), pad beyond 1
    t = np.sqrt((XX-cx*k)**2 + (YY-cy*k)**2)/(r*k); offs = [o for o, _, _ in st]
    rgb = np.stack([np.interp(t, offs, [hx(c)[ch] for _, c, _ in st]) for ch in range(3)], -1).astype(np.float32)
    return rgb, np.interp(t, offs, [a for _, _, a in st]).astype(np.float32)
def screen(b, c, a):                  # b, c in 0..255; a = alpha 0..1 (SVG mix-blend-mode screen with element opacity)
    sc = 255 - (255-b)*(255-c)/255; return b + (sc-b)*a[..., None]
def over(b, c, a): return b*(1-a[..., None]) + c*a[..., None]
c_, a_ = radial(0, 0, 330, [(0, '#14041a', 0.18), (1, '#14041a', 0)]); sky = over(sky, c_, a_)                      # tlDark
inside = lambda cx, cy, r: (np.sqrt((XX-cx*k)**2 + (YY-cy*k)**2) <= r*k).astype(np.float32)
c_, a_ = radial(360, 300, 280, [(0, '#ff9c48', 0.5), (1, '#ff8a3c', 0)]); sky = screen(sky, c_, a_*0.75*inside(360, 300, 280))   # hazeGlow
disc = cv2.GaussianBlur(inside(325, 289.5, 108), (0, 0), 3.5*k); sky = screen(sky, hx('#ffc880')[None, None, :], disc*0.1)          # halo disc (soft2)
c_, a_ = radial(325, 289.5, 130, [(0, '#ffc870', 0.55), (0.45, '#ffa850', 0.22), (1, '#ff8c40', 0)]); sky = screen(sky, c_, a_*0.8*inside(325, 289.5, 130))  # bloomWide
save(sky, f'{OUT}/sky_portrait.png')
# tight sun bloom (drawn over the disc): premultiplied screen layer, black = no effect
c_, a_ = radial(325, 289.5, 50, [(0, '#fff6d6', 0.95), (0.55, '#ffe3a0', 0.55), (1, '#ffc070', 0)])
save(c_*(a_*0.22*inside(325, 289.5, 50))[..., None], f'{OUT}/sun_bloom.png')
# sky vignette (normal blend over everything in the portrait): constant colour, dithered alpha
c_, a_ = radial(427, 250, 600, [(0, '#1a0610', 0), (0.6, '#1a0610', 0.08), (1, '#1a0610', 0.42)])
va = np.clip(a_*255 + rng0.triangular(-1, 0, 1, a_.shape).astype(np.float32), 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([np.broadcast_to(hx('#1a0610').astype(np.uint8), (H, W, 3)), va])).save(f'{OUT}/vig_sky.png', compress_level=4)
# wall shot (screen space): warm pool (screen) and vignette (normal), same parameters as the SVG gradients they replace
c_, a_ = radial(427, 230, 360, [(0, '#ffb060', 0.1), (1, '#ffb060', 0)])
save(c_*a_[..., None], f'{OUT}/warm_pool.png')
# vignette fitted to the reference wall at f075 (blocks outside the poster, 2D): factor = 1 - amax * min(t, 1.6)^g,
# t = elliptical radius about (cx, cy) with radii (rx, ry); rms error 0.05 of the luma ratio
VF = dict(cx=364.5, cy=251.8, rx=472.0, ry=266.1, amax=0.435, g=1.77)
t_ = np.sqrt(((XX/k - VF['cx'])/VF['rx'])**2 + ((YY/k - VF['cy'])/VF['ry'])**2)
a_ = np.clip(VF['amax']*np.minimum(t_, 1.6)**VF['g'], 0, 0.97).astype(np.float32); c_ = np.broadcast_to(hx('#0a0300'), (H, W, 3))
va = np.clip(a_*255 + rng0.triangular(-1, 0, 1, a_.shape).astype(np.float32), 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([np.clip(c_, 0, 255).astype(np.uint8), va])).save(f'{OUT}/vig_wall.png', compress_level=4)
del YY, XX

# ---------------- wall (world texture, 3 px per ref px) ----------------
S = 3; X0, X1, Y0, Y1 = -427, 1281, -240, 720
WW, WH = (X1-X0)*S, (Y1-Y0)*S
rng = np.random.default_rng(11)
plank_w = 66.7*S
tones = [hx('#84431a'), hx('#804118'), hx('#86441a'), hx('#824218'), hx('#7e4018'), hx('#85431a')]
wall = np.zeros((WH, WW, 3), np.float32)
# plank boundaries aligned with the reference gap positions (x = 45,112,178,245 ref at frame 75 -> period 66.7, phase 45)
first = (45 - X0) % 66.7
edges = np.arange(first*S - plank_w, WW + plank_w, plank_w)
grainN = fbm(WH, WW, 60, 4, seed=5, aniso=(0.08, 3.0))   # long vertical streak noise
fine = fbm(WH, WW, 6, 3, seed=6)
for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
    a0, b0 = int(max(0, a)), int(min(WW, b))
    if b0 <= a0: continue
    t = tones[rng.integers(len(tones))] * (1 + rng.uniform(-0.015, 0.015))
    wall[:, a0:b0] = t
    # subtle per-plank vertical shading (slightly darker towards both edges)
    xs = (np.arange(a0, b0) - a)/plank_w
    edge_d = np.minimum(np.arange(a0, b0) - a, b - np.arange(a0, b0))
    wall[:, a0:b0] *= ((1 - 0.03*np.abs(xs-0.5)*2) * (1 - 0.08*np.clip(1 - edge_d/14, 0, 1)))[None, :, None]
wall *= (1 + 0.004*grainN + 0.015*fbm(WH, WW, 120, 3, seed=19) + 0.02*fbm(WH, WW, 90, 3, seed=23, aniso=(3.0, 0.25)))[..., None]   # + soft horizontal banding
wall += fine[..., None]*0.2
# grain streaks: sparse thin darker wavy lines
for _ in range(int(WW/plank_w*4)):
    x = rng.uniform(0, WW); y = rng.uniform(0, WH); L = rng.uniform(120, 300)*S
    ph = rng.uniform(0, 6)
    pts = [(x + 0.7*np.sin(s_*3 + ph), y + s_*L) for s_ in np.linspace(0, 1, 30)]   # straight, thin vertical grain lines (reference)
    cv2.polylines(wall, [np.int32(pts)], False, (wall[int(min(WH-1, y)), int(min(WW-1, x))]*0.83).tolist(), thickness=2, lineType=cv2.LINE_AA)
# plank seams are drawn as crisp vector strokes in CalibrationHQ.tsx (WallSeams), so they stay sharp at every camera zoom like the reference's
# knots (from the reference: near (87,28) and (218,477) ref) plus a few more
for (kx, ky) in [(87, 28), (218, 477), (-260, 330), (640, -150), (1050, 120), (420, 610), (-120, -60), (930, 560)]:
    cx, cy = int((kx-X0)*S), int((ky-Y0)*S)
    kn = np.zeros(wall.shape[:2], np.float32); cv2.ellipse(kn, (cx, cy), (15, 26), rng.uniform(-8, 8), 0, 360, 1.0, -1, cv2.LINE_AA)
    kn = cv2.GaussianBlur(kn, (0, 0), 1.2); wall = wall*(1-0.85*kn[..., None]) + hx('#4c1e12')*0.85*kn[..., None]   # deep maroon interior
    cv2.ellipse(wall, (cx, cy), (15, 26), 0, 0, 360, (hx('#2a0e06')).tolist(), 3, cv2.LINE_AA)                  # darker thin outline (reference)
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
def paper(seed, w_ref=315.3, h_ref=453.3, notch=True, aged=1.0, avoid=None, light=None):
    rng = np.random.default_rng(seed); w, h = int(w_ref*S), int(h_ref*S)
    gy = np.linspace(0, 1, h)[:, None, None]
    img = (hx('#ecca86')*(1-gy*0.4) + hx('#e8c27e')*gy*0.4) * np.ones((h, w, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    centre = np.exp(-(((xx-w/2)/(0.9*w))**2 + ((yy-h*0.4)/(0.42*h))**2))   # reference: even left-right, falls off toward the bottom
    img *= (0.90 + 0.15*centre)[..., None]                       # lit centre
    if light is not None:                                        # measured correction field (reference f075 85th-pct luma / previous render)
        u_, v_ = xx/w, yy/h; B = [np.ones_like(u_, dtype=np.float32), u_, v_, u_*u_, u_*v_, v_*v_, u_**3, u_*u_*v_, u_*v_*v_, v_**3]
        img *= np.clip(sum(c*b for c, b in zip(light, B)), 0.7, 1.15)[..., None]
    img += fbm(h, w, 5, 3, seed=seed+2)[..., None]*0.15          # barely-there fibre
    # round, evenly translucent disc stains (reference look), kept off the portrait box
    placed = 0; tries = 0
    while placed < int(5*aged) and tries < 200:
        tries += 1
        cx, cy = rng.uniform(0.08*w, 0.92*w), rng.uniform(0.12*h, 0.95*h); rx = rng.uniform(70, 130); ry = rx*rng.uniform(0.75, 1.25)
        if avoid is not None and avoid[0]-rx*0.5 < cx < avoid[2]+rx*0.5 and avoid[1]-ry*0.5 < cy < avoid[3]+ry*0.5: continue
        dd = np.sqrt(((xx-cx)/rx)**2 + ((yy-cy)/ry)**2)
        m = cv2.GaussianBlur((dd < 1).astype(np.float32), (0, 0), 4.5)
        a_ = rng.uniform(0.5, 0.62); col = hx('#c8944e')   # reference stain/paper ratio per channel 0.90 / 0.85 / 0.76
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
    top = edge(w, 6.5, seed+10, 0.04); bot = edge(w, 5, seed+11, 0.05); left = edge(h, 4, seed+12, 0.06); right = edge(h, 7.5, seed+13, 0.1)
    xs = np.arange(pad, w-pad, 3); ys = np.arange(pad, h-pad, 3)
    poly = [(x, pad + top[x]) for x in xs] + [(w - pad - right[y], y) for y in ys]
    bpts = [(x, h - pad - bot[x]) for x in xs[::-1]]
    if notch:
        nx = int((533-278+6.7)/w_ref*w); nw = 60; nd = 56
        bpts = [(x, y - nd*(1-abs(x-nx)/nw)) if abs(x-nx) < nw else (x, y) for (x, y) in bpts]
    poly += bpts + [(pad + left[y], y) for y in ys[::-1]]
    alpha = np.zeros((h, w), np.uint8); cv2.fillPoly(alpha, [np.int32(poly)], 255, cv2.LINE_AA)
    alpha = cv2.GaussianBlur(alpha.astype(np.float32)/255, (0, 0), 0.6)
    dist = cv2.distanceTransform((alpha > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    # burn: narrow along the top and sides, deep along the bottom (reference f075: mid-left margin #f1ce91, band above the bottom edge #b99558)
    Dy = 36 + 104*(yy/h)**3                                       # burn depth in plate px: 36 at the top -> 140 at the bottom
    tint = np.clip(1 - dist/Dy, 0, 1)**1.5
    img = img*(1-0.72*tint[..., None]*aged) + hx('#a8742e')*0.72*tint[..., None]*aged
    lip = np.clip(1 - dist/4, 0, 1); img = img*(1-0.6*lip[..., None]) + hx('#f3dcae')*0.6*lip[..., None]
    return img, alpha
# half-strength: the reference's poster light is partly screen-space (the same paper point is ~4% darker at f143 than at f075),
# so a paper-bound correction fitted at f075 alone over-brightens f143; 50% splits the difference
LIGHT = [0.5*c + (0.5 if i == 0 else 0.0) for i, c in enumerate(json.load(open('analysis/lookdev/paper_light_fit.json'))['coef'])]
img, a = paper(21, h_ref=446.8, light=LIGHT, avoid=((328-278+6.7)*S, (98-22+6.7)*S, (528-278+6.7)*S, (232-22+6.7)*S)); save(img, f'{OUT}/paper_main.png', a)
for kk in range(4):
    img, a = paper(100+kk, 213.3, 293.3, notch=bool(kk % 2), aged=1.3); save(img, f'{OUT}/paper_side_{kk}.png', a)

# ---------------- ink wear mask (tileable 1024) ----------------
n = 1024; m = fbm(n, n, 3, 2, seed=77); m2 = fbm(n, n, 30, 3, seed=78)
wear = np.clip(1.0 - (np.clip(m - 1.6, 0, None)*0.9 + np.clip(m2 - 1.2, 0, None)*0.35), 0, 1)
Image.fromarray((wear*255).astype(np.uint8)).save(f'{OUT}/ink_wear.png')
# ---------------- dither tile: zero-mean +-1.5-level overlay that breaks 8-bit SVG gradient steps (glows, rays, vignettes) ----------------
# values {126,127,128,129} with weights 1:2:2:1 (mean 127.5 = identity under 'overlay'); one tile pixel = one 4K pixel
rd = np.random.default_rng(91)
tile = rd.choice(np.array([126, 127, 128, 129], np.uint8), size=(1024, 1024), p=[1/6, 2/6, 2/6, 1/6])
Image.fromarray(tile, 'L').save(f'{OUT}/dither_tile.png')
json.dump(dict(wall=dict(px_per_ref=S, world=[X0, Y0, X1, Y1]), paper=dict(px_per_ref=S, main_world_box=[278, 22, 580, 462], pad_px=20)), open(f'{OUT}/plates.json', 'w'), indent=1)
print('ok')
