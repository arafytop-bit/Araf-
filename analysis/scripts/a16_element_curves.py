"""Per-frame geometry of representative overlay elements (template keyframes).

For white elements (tags, bubbles, outlined labels): mask = bright & low-saturation pixels in ROI that were not bright
in the 'before' frame. For red stamps: red-dominant pixels. Geometry from cv2.minAreaRect of the mask union:
centre (px, %), width/height (px, % of frame), angle (deg), pixel count (opacity/coverage proxy).
Arrow: count of new white pixels (draw-on progress).
"""
import json, numpy as np, cv2
def load(i): return cv2.imread(f'work/frames/f_{i:05d}.png')
def mask_white(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    return ((hsv[..., 2] > 215) & (hsv[..., 1] < 50)).astype(np.uint8)
def mask_red(im):
    b, g, r = [im[..., k].astype(int) for k in range(3)]
    return ((r - g > 70) & (r - b > 60) & (r > 140)).astype(np.uint8)
def measure(name, f_before, f0, f1, roi, kind):
    x0, y0, x1, y1 = roi
    B = load(f_before)[y0:y1, x0:x1]
    mb = mask_white(B) if kind != 'red' else mask_red(B)
    out = []
    for i in range(f0, f1+1):
        I = load(i)[y0:y1, x0:x1]
        m = mask_white(I) if kind != 'red' else mask_red(I)
        m = (m & (1-mb)).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        n = int(m.sum())
        if n < 15:
            out.append(dict(f=i, n=n)); continue
        pts = cv2.findNonZero(m)
        (cx, cy), (w, h), ang = cv2.minAreaRect(pts)
        if w < h:
            w, h = h, w; ang = ang - 90
        if ang < -45: ang += 90
        if ang > 45: ang -= 90
        bx, by, bw, bh = cv2.boundingRect(pts)
        out.append(dict(f=i, n=n, cx=round(cx+x0, 1), cy=round(cy+y0, 1), w=round(w, 1), h=round(h, 1), ang=round(ang, 2),
                        bbox_w=bw, bbox_h=bh, cx_pct=round((cx+x0)/854*100, 2), cy_pct=round((cy+y0)/480*100, 2), w_pct=round(w/854*100, 2)))
    return out
jobs = {
    'name_tag_DUTCH': (1630, 1631, 1652, (60, 10, 470, 110), 'white'),
    'name_tag_HOSEA': (1720, 1721, 1740, (40, 30, 470, 150), 'white'),
    'label_SMALLTIME': (905, 908, 920, (520, 70, 854, 210), 'white'),
    'label_YEARSLATER': (1080, 1082, 1096, (520, 100, 760, 200), 'white'),
    'bubble_WATCHED': (1112, 1113, 1126, (460, 150, 800, 330), 'white'),
    'bubble_WILDONE': (1855, 1856, 1866, (280, 10, 520, 120), 'white'),
    'stamp_TROUBLE': (1477, 1478, 1492, (60, 0, 470, 160), 'red'),
    'stamp_MASSACRE': (4892, 4893, 4905, (360, 40, 854, 240), 'red'),
    'stamp_MOSTWANTED': (218, 219, 232, (0, 0, 480, 160), 'red'),
}
res = {}
for k, (fb, f0, f1, roi, kind) in jobs.items():
    res[k] = measure(k, fb, f0, f1, roi, kind)
    print('==', k)
    for r in res[k]:
        print('  ', r)
# arrow draw-on after SMALL-TIME CROOK: new white pixels in the arrow ROI over time
fb = 913; roi = (380, 150, 560, 280)
B = mask_white(load(fb)[roi[1]:roi[3], roi[0]:roi[2]])
arr = []
for i in range(913, 930):
    m = mask_white(load(i)[roi[1]:roi[3], roi[0]:roi[2]]) & (1-B)
    arr.append(dict(f=i, new_white_px=int(m.sum())))
res['arrow_SMALLTIME'] = arr
print('== arrow', arr)
json.dump(res, open('analysis/data/element_curves.json', 'w'), indent=1)
