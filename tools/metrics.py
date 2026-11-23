import numpy as np, cv2, sys, pandas as pd
fr = np.load(sys.argv[1], mmap_mode='r'); out = sys.argv[2]
N = fr.shape[0]; fps = 24.0
rows = []; prev_g = None; prev_h = None
for i in range(N):
    f = np.asarray(fr[i])
    g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32)
    hsv = cv2.cvtColor(f, cv2.COLOR_RGB2HSV)
    h = cv2.calcHist([hsv],[0,1,2],None,[16,8,8],[0,180,0,256,0,256]); cv2.normalize(h,h)
    edges = cv2.Canny(g.astype(np.uint8), 80, 160)
    r = dict(i=i, t=i/fps, Y=g.mean(), Ystd=g.std(), R=f[...,0].mean(), G=f[...,1].mean(), B=f[...,2].mean(),
             S=hsv[...,1].mean(), edge=(edges>0).mean())
    if prev_g is not None:
        d = np.abs(g - prev_g)
        r['mad'] = d.mean(); r['chg'] = (d > 20).mean()
        r['hcorr'] = cv2.compareHist(prev_h, h, cv2.HISTCMP_CORREL)
    else:
        r['mad'] = 0; r['chg'] = 0; r['hcorr'] = 1
    rows.append(r); prev_g = g; prev_h = h
df = pd.DataFrame(rows); df.to_csv(out, index=False)
print(df.describe().T[['mean','std','min','50%','max']].round(3))
