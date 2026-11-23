# Filmstrips of selected events: every frame from 1 before start to 2 after end (subsampled to <=12), cropped to changed bbox.
import numpy as np, pandas as pd, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
src, evf, outdir = sys.argv[1], sys.argv[2], sys.argv[3]; times = [float(x) for x in sys.argv[4].split(',')]
os.makedirs(outdir, exist_ok=True)
ev = pd.read_csv(evf); fps = 24.0; W, H = 1280, 720
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
def grab(f0, n):
    p = subprocess.run(['ffmpeg','-v','error','-ss',f'{f0/fps:.4f}','-i',src,'-frames:v',str(n),'-f','rawvideo','-pix_fmt','rgb24','-'], capture_output=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)
for t in times:
    r = ev.iloc[(ev.end/fps - t).abs().argmin()]
    s, e = int(r.start), int(r.end)
    fr = grab(s - 1, e - s + 4)
    g = fr.mean(-1); m = (np.abs(g - g[0]).max(0) > 25)
    ys, xs = np.where(m)
    if len(xs) == 0: continue
    x0, y0, x1, y1 = max(0, xs.min()-20), max(0, ys.min()-20), min(W, xs.max()+20), min(H, ys.max()+20)
    idx = np.unique(np.linspace(0, len(fr)-1, min(len(fr), 12)).round().astype(int))
    tw = 300; th = int(tw * (y1-y0) / max(1,(x1-x0))); th = max(60, min(th, 260))
    sheet = Image.new('RGB', (tw*min(6,len(idx)), (th+20)*((len(idx)+5)//6)), (60,60,60)); d = ImageDraw.Draw(sheet)
    for k, i in enumerate(idx):
        im = Image.fromarray(fr[i][y0:y1, x0:x1]).resize((tw, th))
        x = (k%6)*tw; y = (k//6)*(th+20); sheet.paste(im, (x, y+20))
        d.text((x+4, y+2), f"f{s-1+i} (+{i-1})", fill=(255,255,0), font=font)
    sheet.save(f"{outdir}/ev_{r.t0:07.2f}.png")
    print(f"{r.t0:.2f}s nfr={r.nfr} kind={r.kind} bbox={x0},{y0},{x1},{y1}")
