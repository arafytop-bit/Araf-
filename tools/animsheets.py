import numpy as np, pandas as pd, sys, os
from PIL import Image, ImageDraw, ImageFont
fr = np.load(sys.argv[1], mmap_mode='r'); ev = pd.read_csv(sys.argv[2]); outdir = sys.argv[3]; os.makedirs(outdir, exist_ok=True)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
an = ev[(ev.kind == 'anim') | ((ev.kind == 'cut') & (ev.nfr >= 3))].reset_index(drop=True)
TW, TH = 224, 126; per_row = 2; rows_per = 10
for si in range(0, len(an), per_row*rows_per):
    chunk = an.iloc[si:si+per_row*rows_per]
    sheet = Image.new('RGB', (TW*4*per_row + 20, (TH+16)*rows_per), (30,30,30)); d = ImageDraw.Draw(sheet)
    for k, r in enumerate(chunk.itertuples()):
        s, e = int(r.start), int(r.end)
        idx = [s-1, s + (e-s)//3, s + 2*(e-s)//3, e]
        x0 = (k % per_row) * (TW*4 + 20); y0 = (k // per_row) * (TH+16)
        d.text((x0+2, y0), f"A{si+k} t={s/24:.2f}-{(e+1)/24:.2f}s n={r.nfr} {r.kind}", fill=(255,220,0), font=font)
        for j, i in enumerate(idx):
            im = Image.fromarray(np.asarray(fr[i])).resize((TW, TH)); sheet.paste(im, (x0 + j*TW, y0+16))
            d.rectangle([x0+j*TW, y0+16, x0+(j+1)*TW-1, y0+16+TH-1], outline=(90,90,90))
    sheet.save(f"{outdir}/anims_{si//(per_row*rows_per):02d}.png")
print(len(an), 'anim events')
