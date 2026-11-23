# Contact sheets: one thumbnail per stable state (frame after each event), labeled with time, event type and spoken words.
import numpy as np, pandas as pd, json, sys, os
from PIL import Image, ImageDraw, ImageFont
fr = np.load(sys.argv[1], mmap_mode='r'); ev = pd.read_csv(sys.argv[2]); asr = json.load(open(sys.argv[3])); outdir = sys.argv[4]
os.makedirs(outdir, exist_ok=True)
words = asr['words']; fps = 24.0
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
fontb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
# states: frame 0 + after each event
ev = ev[ev.kind != 'boil']
states = [(0, 'start', 0)] + [(int(r.end), r.kind, int(r.nfr)) for r in ev.itertuples()]
TW, TH, CAP = 256, 144, 34; COLS, ROWS = 6, 5
def words_between(t0, t1):
    return ' '.join(w['word'] for w in words if w['start'] >= t0 - 0.05 and w['start'] < t1)
per = COLS * ROWS
for si in range(0, len(states), per):
    sheet = Image.new('RGB', (COLS*TW, ROWS*(TH+CAP)), (40,40,40)); d = ImageDraw.Draw(sheet)
    for k, (f, kind, n) in enumerate(states[si:si+per]):
        idx = si + k
        nxt = states[idx+1][0] if idx + 1 < len(states) else len(fr)-1
        im = Image.fromarray(np.asarray(fr[min(f, len(fr)-1)])).resize((TW, TH))
        x = (k % COLS) * TW; y = (k // COLS) * (TH + CAP)
        sheet.paste(im, (x, y))
        col = {'cut': (255,90,90), 'pop': (120,200,255), 'anim': (255,210,80), 'start': (200,200,200)}[kind]
        d.rectangle([x, y, x+TW-1, y+TH-1], outline=col, width=2)
        t0 = f/fps; t1 = nxt/fps
        d.text((x+3, y+TH+1), f"#{idx} {t0:6.2f}s {kind}{'x'+str(n) if n>1 else ''} dur {t1-t0:.2f}", fill=col, font=fontb)
        txt = words_between(t0, t1)
        d.text((x+3, y+TH+16), (txt[:44] + ('…' if len(txt) > 44 else '')), fill=(230,230,230), font=font)
    sheet.save(f"{outdir}/sheet_{si//per:02d}.png")
print(len(states), 'states ->', (len(states)+per-1)//per, 'sheets')
