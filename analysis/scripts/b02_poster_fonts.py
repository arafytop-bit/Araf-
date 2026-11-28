"""Focused poster-typeface match (slab/heavy serif candidates, ink-spread via dilation, tracking sweep)."""
import sys, glob, os, json, numpy as np, cv2
sys.path.insert(0, 'analysis/scripts')
from a11_font_match import convert_all, render, iou, TTF_DIR
from a11b_font_match_focus import binar
convert_all()
fams = ['kameron', 'alfa-slab-one', 'arvo', 'bitter', 'zilla-slab', 'roboto-slab', 'rokkitt', 'crete-round', 'patua-one', 'sanchez', 'noticia-text', 'domine', 'enriqueta',
        'podkova', 'aleo', 'glegoo', 'ultra', 'rye', 'coustard', 'trocchi', 'bree-serif', 'kreon', 'solway', 'source-serif-4', 'literata', 'merriweather', 'hepta-slab',
        'holtwood-one-sc', 'bevan', 'sansita', 'slabo-27px', 'antic-slab', 'chonburi', 'besley', 'vidaloka', 'abhaya-libre', 'fjord-one', 'rozha-one', 'old-standard-tt', 'alegreya', 'fraunces', 'young-serif']
refs = {'WANTED': (75, (310, 46, 548, 94), 'dark'), 'TRAINS': (143, (330, 168, 470, 200), 'dark'), 'HALF THE WEST': (143, (330, 272, 572, 304), 'dark'), 'ARTHUR MORGAN': (143, (268, 83, 585, 115), 'dark')}
res = {}
for txt, (fr, box, pol) in refs.items():
    R = binar(fr, box, pol); h, w = R.shape; scores = []
    for f in sorted(glob.glob(f'{TTF_DIR}/*.ttf')):
        b = os.path.basename(f)
        if not any(b.startswith(fa + '-latin') for fa in fams): continue
        best = (-9, 0, 0)
        for tr in (0.0, 0.03, 0.06, 0.1):
            C = render(f, txt, tr)
            if C is None: continue
            for d in (0, 2, 4):
                Cd = cv2.dilate(C, np.ones((2*d+1, 2*d+1), np.uint8)) if d else C
                ys, xs = np.where(Cd > 127); Cd = Cd[ys.min():ys.max()+1, xs.min():xs.max()+1]
                s = iou(R, cv2.resize(Cd, (w, h), interpolation=cv2.INTER_AREA)) - 0.8*abs(np.log((Cd.shape[1]/Cd.shape[0])/(w/h)))
                if s > best[0]: best = (s, tr, d)
        scores.append((b.replace('.ttf', ''), round(best[0], 4), best[1], best[2]))
    scores.sort(key=lambda r: -r[1]); res[txt] = scores[:8]
    print(txt, scores[:6])
# joint ranking across the four poster strings
agg = {}
for txt, sc in res.items():
    pass
allsc = {}
for txt, (fr, box, pol) in refs.items():
    pass
json.dump(res, open('analysis/fonts/poster_font_match.json', 'w'), indent=1)
