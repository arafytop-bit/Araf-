"""Focused font pass: deskewed name tag, outline-aware (candidate dilation) title/label, joint title score."""
import json, glob, os, numpy as np, cv2, sys
sys.path.insert(0, 'analysis/scripts')
from a11_font_match import render, iou, TTF_DIR
def binar(fr, box, pol, deskew=False):
    im = cv2.imread(f'work/frames/f_{fr:05d}.png')
    x0, y0, x1, y1 = box
    crop = im[y0:y1, x0:x1]
    crop = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    if deskew:
        # angle from the bright tag body
        _, wm = cv2.threshold(g, 200, 255, cv2.THRESH_BINARY)
        cnts, _ = cv2.findContours(wm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = max(cnts, key=cv2.contourArea); (cx, cy), (w, h), ang = cv2.minAreaRect(c)
        if w < h: ang += 90
        if ang > 45: ang -= 90
        M = cv2.getRotationMatrix2D((g.shape[1]/2, g.shape[0]/2), ang, 1.0)
        g = cv2.warpAffine(g, M, (g.shape[1], g.shape[0]), flags=cv2.INTER_CUBIC, borderValue=255)
        print('deskew angle', round(ang, 2))
    flag = cv2.THRESH_BINARY if pol == 'light' else cv2.THRESH_BINARY_INV
    _, m = cv2.threshold(g, 0, 255, flag + cv2.THRESH_OTSU)
    rows = (m > 0).sum(1); on = np.where(rows > rows.max()*0.2)[0]
    runs = []; s = on[0]; p = on[0]
    for y in on[1:]:
        if y > p+6: runs.append((s, p)); s = y
        p = y
    runs.append((s, p)); a, b = max(runs, key=lambda r: (m[r[0]:r[1]+1] > 0).sum())
    m2 = np.zeros_like(m); m2[a:b+1] = m[a:b+1]
    n, lab, st, _ = cv2.connectedComponentsWithStats(m2); keep = np.zeros_like(m2)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 30: keep[lab == i] = 255
    ys, xs = np.where(keep > 0)
    return keep[ys.min():ys.max()+1, xs.min():xs.max()+1]
def best_for(R, txt, fams, tracks=(0.0,), dil=(0, 2, 4, 6)):
    h, w = R.shape; res = []
    for f in sorted(glob.glob(f'{TTF_DIR}/*.ttf')):
        b = os.path.basename(f)
        if not any(b.startswith(fa + '-latin') for fa in fams): continue
        best = (-9, 0, 0)
        for tr in tracks:
            C = render(f, txt, tr)
            if C is None: continue
            for d in dil:
                Cd = cv2.dilate(C, np.ones((2*d+1, 2*d+1), np.uint8)) if d else C
                ys, xs = np.where(Cd > 127); Cd = Cd[ys.min():ys.max()+1, xs.min():xs.max()+1]
                s = iou(R, cv2.resize(Cd, (w, h), interpolation=cv2.INTER_AREA)) - 0.8*abs(np.log((Cd.shape[1]/Cd.shape[0])/(w/h)))
                if s > best[0]: best = (s, tr, d)
        res.append((b.replace('.ttf', ''), round(best[0], 4), best[1], best[2]))
    return sorted(res, key=lambda r: -r[1])
serif_slab = ['bitter', 'alegreya', 'alegreya-sc', 'literata', 'aleo', 'zilla-slab', 'roboto-slab', 'arvo', 'rokkitt', 'crete-round', 'kreon', 'solway', 'source-serif-4', 'patua-one', 'sanchez', 'podkova', 'merriweather', 'domine', 'bree-serif', 'kameron', 'enriqueta', 'noticia-text', 'coustard', 'alfa-slab-one', 'ultra', 'vollkorn', 'fraunces', 'besley', 'young-serif', 'rye']
sans = ['alegreya-sans', 'alegreya-sans-sc', 'fira-sans', 'fira-sans-condensed', 'fira-sans-extra-condensed', 'barlow-semi-condensed', 'barlow-condensed', 'asap-condensed', 'roboto-condensed', 'saira-semi-condensed', 'encode-sans-semi-condensed', 'sofia-sans-semi-condensed', 'ibm-plex-sans-condensed', 'pt-sans-narrow', 'archivo-narrow', 'signika', 'cabin-condensed', 'source-sans-3', 'open-sans', 'mukta', 'hind', 'catamaran', 'heebo', 'assistant', 'karla']
out = {}
RA = binar(60, (55, 318, 262, 358), 'light'); RM = binar(60, (52, 372, 264, 406), 'light')
a = dict((r[0], r) for r in best_for(RA, 'ARTHUR', serif_slab, tracks=(0.05, 0.1, 0.15, 0.2)))
m = dict((r[0], r) for r in best_for(RM, 'MORGAN', serif_slab, tracks=(0.05, 0.1, 0.15, 0.2)))
joint = sorted([(k, round((a[k][1]+m[k][1])/2, 4), a[k][2], a[k][3]) for k in a if k in m], key=lambda r: -r[1])
out['title_joint'] = joint[:8]; print('TITLE joint', joint[:6])
RT = binar(1660, (150, 34, 368, 70), 'dark', deskew=True)
cv2.imwrite('analysis/fonts/mask_tag_deskew.png', RT)
out['tag_name'] = best_for(RT, 'DUTCH VAN DER LINDE', sans, dil=(0, 2))[:8]; print('TAG', out['tag_name'][:6])
RG = binar(1160, (565, 134, 698, 158), 'light')
out['label_gold'] = best_for(RG, 'YEARS LATER', sans, dil=(0, 2, 4))[:8]; print('LABEL', out['label_gold'][:6])
RB = binar(1160, (552, 212, 712, 237), 'dark')
out['bubble'] = best_for(RB, 'I watched him die.', sans, dil=(0, 2))[:8]; print('BUBBLE', out['bubble'][:6])
json.dump(out, open('analysis/fonts/font_match_focus.json', 'w'), indent=1)
