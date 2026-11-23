import numpy as np, cv2, pandas as pd, json, sys
fr = np.load(sys.argv[1], mmap_mode='r'); df = pd.read_csv(sys.argv[2]); out = sys.argv[3]
N = len(df); fps = 24.0
mad = df.mad.values
moving = mad > 0.05
# group moving frames into events, bridging gaps <= 2 static frames
ev = []; i = 1
while i < N:
    if moving[i]:
        s = i; e = i; j = i + 1
        while j < N:
            if moving[j]: e = j; j += 1
            elif j + 2 < N and (moving[j+1] or moving[j+2]) and j - e <= 2: j += 1
            else: break
        ev.append([s, e]); i = e + 1
    else: i += 1
rows = []
for s, e in ev:
    a = cv2.cvtColor(np.asarray(fr[s-1]), cv2.COLOR_RGB2GRAY).astype(np.int16)
    b = cv2.cvtColor(np.asarray(fr[e]), cv2.COLOR_RGB2GRAY).astype(np.int16)
    d = np.abs(b - a) > 25
    net = d.mean()
    ys, xs = np.where(d)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
    # per-frame max change inside event
    seg = df.iloc[s:e+1]
    rows.append(dict(start=s, end=e, t0=round(s/fps,3), t1=round((e+1)/fps,3), nfr=e-s+1, net_chg=round(float(net),4),
                     max_frame_chg=round(float(seg.chg.max()),4), max_mad=round(float(seg.mad.max()),2), bbox=bbox,
                     Ybefore=round(float(df.Y[s-1]),1), Yafter=round(float(df.Y[e]),1)))
pd.DataFrame(rows).to_csv(out, index=False)
r = pd.DataFrame(rows)
print('events', len(r)); print(r.nfr.describe().round(2))
print('big composition changes (net_chg>0.25):', (r.net_chg > 0.25).sum())
print('single-frame events:', (r.nfr == 1).sum(), ' single-frame & big:', ((r.nfr==1)&(r.net_chg>0.25)).sum())
print('multi-frame big:', ((r.nfr>1)&(r.net_chg>0.25)).sum())
