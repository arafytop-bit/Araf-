import numpy as np, pandas as pd, sys
fr = np.load(sys.argv[1], mmap_mode='r'); ev = pd.read_csv(sys.argv[2])
def g(i): return np.asarray(fr[i]).astype(np.int16).mean(-1)
kinds = []; boilfrac = []
for r in ev.itertuples():
    s, e = int(r.start), int(r.end)
    k = None; bf = np.nan
    if r.nfr <= 2 and r.net_chg < 0.25:
        a = g(e); m = np.abs(a - g(s - 1)) > 25
        if m.sum() > 0:
            best = 1.0
            for lag in (16, 18, 32):
                if e - lag >= 0:
                    back = np.abs(a - g(e - lag)) > 25
                    best = min(best, back[m].mean())
            bf = best
            if best < 0.05: k = 'boil'
    if k is None:
        k = 'cut' if r.net_chg > 0.25 else ('anim' if r.nfr > 2 else 'pop')
    kinds.append(k); boilfrac.append(bf)
ev['kind'] = kinds; ev['boilmatch'] = boilfrac
ev.to_csv(sys.argv[3], index=False)
print(ev.kind.value_counts())
b = ev[ev.kind=='boil'].start.values; d = np.diff(b)
print('boil intervals (frames):', pd.Series(d).value_counts().head(8).to_dict())
