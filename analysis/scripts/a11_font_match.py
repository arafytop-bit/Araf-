"""Font identification by rendering: compare binarized reference text crops against every candidate font file.

Score = IoU of glyph masks (candidate rendered with the same string, tracking swept, resized to the reference box)
        - 0.5*|log(aspect ratio mismatch at zero tracking)| is NOT used; tracking is fitted instead.
Outputs analysis/fonts/font_match.json (top 8 per reference) and comparison sheets for the top 4.
"""
import os, glob, json, io, numpy as np, cv2
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

REFS = json.load(open('analysis/fonts/refs.json'))
FONT_DIR = 'work/fontsrc/node_modules/@fontsource'
TTF_DIR = 'work/fonts_ttf'; os.makedirs(TTF_DIR, exist_ok=True)

def convert_all():
    out = []
    for fam in sorted(os.listdir(FONT_DIR)):
        for f in glob.glob(f'{FONT_DIR}/{fam}/files/{fam}-latin-[0-9]*-*.woff2'):
            base = os.path.basename(f).replace('.woff2', '.ttf')
            dst = f'{TTF_DIR}/{base}'
            if not os.path.exists(dst):
                try:
                    t = TTFont(f); t.flavor = None; t.save(dst)
                except Exception as e:
                    continue
            out.append(dst)
    return sorted(out)

def ref_mask(key):
    fr, box, pol, txt = REFS[key]
    im = cv2.imread(f'work/frames/f_{fr:05d}.png')[box[1]:box[3], box[0]:box[2]]
    im = cv2.resize(im, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    if pol == 'light':
        _, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # keep the dominant text line: rows band with most ink
    rows = (m > 0).sum(1)
    thr = rows.max()*0.15
    on = np.where(rows > thr)[0]
    # largest contiguous run
    runs = []; s = on[0]; p = on[0]
    for y in on[1:]:
        if y > p+6: runs.append((s, p)); s = y
        p = y
    runs.append((s, p))
    a, b = max(runs, key=lambda r: (m[r[0]:r[1]+1] > 0).sum())
    m2 = np.zeros_like(m); m2[a:b+1] = m[a:b+1]
    # drop tiny specks
    n, lab, st, _ = cv2.connectedComponentsWithStats(m2)
    keep = np.zeros_like(m2)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 30:
            keep[lab == i] = 255
    ys, xs = np.where(keep > 0)
    return keep[ys.min():ys.max()+1, xs.min():xs.max()+1], txt

def render(fontfile, txt, tracking_em=0.0, size=160):
    try:
        F = ImageFont.truetype(fontfile, size)
    except Exception:
        return None
    # draw glyph by glyph to apply tracking
    widths = [F.getlength(ch) for ch in txt]
    W = int(sum(widths) + abs(tracking_em)*size*len(txt) + size*2); H = int(size*2.2)
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
    x = size*0.5
    for ch, w in zip(txt, widths):
        d.text((x, size*0.4), ch, font=F, fill=255)
        x += w + tracking_em*size
    a = np.array(img)
    ys, xs = np.where(a > 127)
    if len(xs) == 0:
        return None
    return a[ys.min():ys.max()+1, xs.min():xs.max()+1]

def iou(a, b):
    a = a > 127; b = b > 127
    return float((a & b).sum()/max(1, (a | b).sum()))

REFM = {}
def score(args):
    fontfile, key = args
    R, txt = REFM[key]
    h, w = R.shape
    best = (-1, 0)
    for tr in ([0.0] if key not in ('chapter_num', 'poster_wantedfor', 'title_ARTHUR', 'title_MORGAN') else [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]):
        C = render(fontfile, txt, tr)
        if C is None:
            return (fontfile, key, -1, 0, 0)
        ar_c = C.shape[1]/C.shape[0]; ar_r = w/h
        Cr = cv2.resize(C, (w, h), interpolation=cv2.INTER_AREA)
        s = iou(R, Cr) - 0.8*abs(np.log(ar_c/ar_r))
        if s > best[0]:
            best = (s, tr, ar_c/ar_r)
    return (fontfile, key, round(best[0], 4), best[1], round(best[2], 3))

if __name__ == '__main__':
    fonts = convert_all()
    print('fonts', len(fonts))
    for k in REFS:
        REFM[k] = ref_mask(k)
        cv2.imwrite(f'analysis/fonts/mask_{k}.png', REFM[k][0])
    jobs = [(f, k) for k in REFS for f in fonts]
    with Pool(3) as p:
        res = p.map(score, jobs, chunksize=40)
    out = {}
    for k in REFS:
        rs = sorted([r for r in res if r[1] == k], key=lambda r: -r[2])[:10]
        out[k] = [dict(font=os.path.basename(r[0]).replace('.ttf', ''), score=r[2], tracking_em=r[3], aspect_ratio_rel=r[4]) for r in rs]
        print(k, [(o['font'], o['score'], o['tracking_em']) for o in out[k][:5]])
    json.dump(out, open('analysis/fonts/font_match.json', 'w'), indent=1)
    # comparison sheets: reference mask vs top-4 renders
    for k in REFS:
        R, txt = REFM[k]; h, w = R.shape
        tiles = [255-R]
        for o in out[k][:4]:
            C = render(f'{TTF_DIR}/{o["font"]}.ttf', txt, o['tracking_em'])
            tiles.append(255-cv2.resize(C, (w, h), interpolation=cv2.INTER_AREA))
        sheet = np.vstack([np.pad(t, ((4, 4), (4, 4)), constant_values=128) for t in tiles])
        cv2.imwrite(f'analysis/fonts/cmp_{k}.png', sheet)
