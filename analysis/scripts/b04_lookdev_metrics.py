"""Art-director metrics: rebuild vs reference at the reference's native scale (854x480).

Per region: edge density (Canny 60/150), fine texture (std of luma minus Gaussian(1.0)), RMS contrast (std luma/255),
colourfulness (Hasler-Suesstrunk), mean CIELAB and CIEDE2000 between region means. Targets: ratios 0.8-1.2, dE00 < 6.
usage: python b04_lookdev_metrics.py <tag>   (reads work/hq/<tag>_f<frame>.png produced by the renderer)
"""
import sys, json, numpy as np, cv2
TAG = sys.argv[1] if len(sys.argv) > 1 else 'v1'

def srgb_to_lab(rgb):
    c = rgb/255.0
    c = np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216/24389, np.cbrt(xyz), (24389/27*xyz + 16)/116)
    return np.stack([116*f[..., 1]-16, 500*(f[..., 0]-f[..., 1]), 200*(f[..., 1]-f[..., 2])], -1)

def de2000(a, b):
    L1, a1, b1 = a; L2, a2, b2 = b
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2); Cb = (C1+C2)/2
    G = 0.5*(1-np.sqrt(Cb**7/(Cb**7+25**7)))
    a1p, a2p = (1+G)*a1, (1+G)*a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p, h2p = np.degrees(np.arctan2(b1, a1p)) % 360, np.degrees(np.arctan2(b2, a2p)) % 360
    dLp, dCp = L2-L1, C2p-C1p
    dh = h2p-h1p
    if C1p*C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dHp = 2*np.sqrt(C1p*C2p)*np.sin(np.radians(dh/2))
    Lbp, Cbp = (L1+L2)/2, (C1p+C2p)/2
    hbp = (h1p+h2p)/2 if abs(h1p-h2p) <= 180 else (h1p+h2p+360)/2
    if C1p*C2p == 0: hbp = h1p+h2p
    Tt = 1-0.17*np.cos(np.radians(hbp-30))+0.24*np.cos(np.radians(2*hbp))+0.32*np.cos(np.radians(3*hbp+6))-0.20*np.cos(np.radians(4*hbp-63))
    dtheta = 30*np.exp(-((hbp-275)/25)**2); Rc = 2*np.sqrt(Cbp**7/(Cbp**7+25**7))
    Sl = 1+0.015*(Lbp-50)**2/np.sqrt(20+(Lbp-50)**2); Sc = 1+0.045*Cbp; Sh = 1+0.015*Cbp*Tt; Rt = -np.sin(np.radians(2*dtheta))*Rc
    return float(np.sqrt((dLp/Sl)**2+(dCp/Sc)**2+(dHp/Sh)**2+Rt*(dCp/Sc)*(dHp/Sh)))

def metrics(rgb):
    L = 0.2126*rgb[..., 0]+0.7152*rgb[..., 1]+0.0722*rgb[..., 2]
    e = cv2.Canny(L.astype(np.uint8), 60, 150)
    fine = L - cv2.GaussianBlur(L, (0, 0), 1.0)
    rg = rgb[..., 0]-rgb[..., 1]; yb = 0.5*(rgb[..., 0]+rgb[..., 1])-rgb[..., 2]
    colf = np.sqrt(rg.std()**2+yb.std()**2)+0.3*np.sqrt(rg.mean()**2+yb.mean()**2)
    return dict(edge_density=float((e > 0).mean()), fine_texture=float(fine.std()), contrast=float(L.std()/255), colorfulness=float(colf), lab=srgb_to_lab(rgb.reshape(-1, 3)).mean(0))

def load_ours(path):
    im = cv2.imread(path)[:, :, ::-1].astype(np.float32)
    return cv2.resize(im, (854, 480), interpolation=cv2.INTER_AREA)
def load_ref(fr):
    return cv2.imread(f'work/frames/f_{fr:05d}.png')[:, :, ::-1].astype(np.float32)

SCENES = {
  'poster_f143': dict(frame=143, regions={'list_block (text+icons+paper)': (280, 150, 560, 330), 'paper (blank)': (470, 158, 552, 200), 'wood (left wall)': (20, 60, 220, 420), 'whole_frame': (0, 0, 854, 480)}, de=['paper (blank)', 'wood (left wall)']),
  'poster_f075': dict(frame=75, regions={'paper (list area, empty)': (330, 290, 530, 410), 'wood (left wall)': (0, 0, 250, 480), 'poster_top (WANTED)': (300, 40, 556, 100), 'whole_frame_minus_portrait': None}, de=['paper (list area, empty)', 'wood (left wall)']),
  'portrait_f030': dict(frame=30, regions={'sky': (0, 0, 300, 200), 'mountains': (120, 228, 255, 330), 'mesa': (0, 280, 105, 340), 'ground': (0, 372, 250, 470), 'background_left_of_hero': (0, 0, 300, 480)}, de=['sky', 'mountains', 'ground']),
}
rows = []
for name, sc in SCENES.items():
    import os
    path = f'work/hq/{TAG}_f{sc["frame"]:03d}.png'
    if not os.path.exists(path): continue
    O, R = load_ours(path), load_ref(sc['frame'])
    for rn, box in sc['regions'].items():
        if box is None:
            mask = np.ones((480, 854), bool); mask[98:232, 328:528] = False   # exclude the (pending) portrait print
            o, r = O[mask], R[mask]
            mo, mr = metrics(o.reshape(1, -1, 3)), metrics(r.reshape(1, -1, 3))
        else:
            x0, y0, x1, y1 = box; mo, mr = metrics(O[y0:y1, x0:x1]), metrics(R[y0:y1, x0:x1])
        row = dict(scene=name, region=rn)
        for k in ['edge_density', 'fine_texture', 'contrast', 'colorfulness']:
            row[k+'_ratio'] = round(mo[k]/max(mr[k], 1e-6), 2); row[k+'_ok'] = 0.8 <= row[k+'_ratio'] <= 1.2
        row['dE00'] = round(de2000(mr['lab'], mo['lab']), 2); row['dE_target'] = rn in sc['de']; row['dE_ok'] = (row['dE00'] < 6) if row['dE_target'] else None
        row['ref_lab'] = [round(float(v), 1) for v in mr['lab']]; row['ours_lab'] = [round(float(v), 1) for v in mo['lab']]
        rows.append(row)
json.dump(rows, open(f'analysis/lookdev/metrics_{TAG}.json', 'w'), indent=1)
hdr = f"{'scene':14s} {'region':34s} {'edge':>6s} {'fine':>6s} {'contr':>6s} {'colour':>6s} {'dE00':>6s}"
print(hdr)
for r in rows:
    flag = lambda k: '' if r[k+'_ok'] else '*'
    print(f"{r['scene']:14s} {r['region']:34s} {r['edge_density_ratio']:6.2f}{flag('edge_density')} {r['fine_texture_ratio']:6.2f}{flag('fine_texture')} {r['contrast_ratio']:6.2f}{flag('contrast')} {r['colorfulness_ratio']:6.2f}{flag('colorfulness')} {r['dE00']:6.2f}{'' if not r['dE_target'] else ('' if r['dE_ok'] else '*')}")
