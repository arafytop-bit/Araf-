"""Cut / transition detection and shot list from per-frame metrics (+ PySceneDetect cross-check).

Conventions: a cut 'at frame N' means N is the FIRST frame of the new shot (frames N-1 and N differ).
Outputs: analysis/data/cuts.json, analysis/data/shots_auto.csv
"""
import json, numpy as np, pandas as pd

m = pd.read_csv('analysis/data/frame_metrics.csv')
N = len(m)
th = np.load('work/thumbs64.npy').astype(np.float32)   # (N,36,64,3)

hd = m.hist_dist.fillna(0).values; ss = m.ssim.fillna(1).values; mad = m.mad.fillna(0).values
inl = m.aff_inl.fillna(0).values; ym = m.y_mean.values; fb = m.frac_black.values; fw = m.frac_white.values

def local_med(x, k=15):
    return pd.Series(x).rolling(2*k+1, center=True, min_periods=1).median().values

# --- hard-cut candidates: abrupt, isolated change ---
hd_rel = hd - local_med(hd); mad_rel = mad - local_med(mad)
cand = (hd > 0.30) & (ss < 0.55) & (mad > 12) & (hd_rel > 0.2)
# 1-frame isolation: the change must not continue (else it's a transition/motion)
cuts = []
for i in np.where(cand)[0]:
    if i == 0:
        continue
    # require neighbours to be much more similar than the jump
    prev_ok = (i-1 < 1) or hd[i-1] < hd[i]*0.6
    next_ok = (i+1 >= N) or hd[i+1] < hd[i]*0.6
    if prev_ok and next_ok:
        cuts.append(int(i))

# --- also accept strong cuts where only part of the frame changes (same background, new framing) ---
cand2 = (ss < 0.45) & (inl < 25) & (mad > 18)
for i in np.where(cand2)[0]:
    if i not in cuts and all(abs(i-c) > 2 for c in cuts):
        if (i+1 >= N or ss[i+1] > 0.7) and (ss[i-1] > 0.7):
            cuts.append(int(i))
cuts = sorted(set(cuts))

# --- fades through black / white, flashes ---
black = fb > 0.97
white = (fw > 0.6)
fades = []
i = 0
while i < N:
    if black[i]:
        j = i
        while j+1 < N and black[j+1]:
            j += 1
        # walk outwards while luma keeps rising monotonically (fade-out before / fade-in after)
        a = i
        while a-1 >= 0 and ym[a-1] > ym[a] + 0.3 and not any(c == a for c in cuts):
            a -= 1
        b = j
        while b+1 < N and ym[b+1] > ym[b] + 0.3 and not any(c == b+1 for c in cuts):
            b += 1
        fades.append(dict(kind='black', fade_out_start=int(a), black_start=int(i), black_end=int(j), fade_in_end=int(b)))
        i = j+1
    else:
        i += 1
flashes = []
dy = np.r_[0, np.diff(ym)]
for i in range(1, N-1):
    if dy[i] > 25 and ym[i] > 150:
        flashes.append(int(i))

# --- dissolve test: frame k ~ (1-a)*A + a*B between two stable anchors ---
def blend_fit(a, b):
    A = th[a].ravel(); B = th[b].ravel(); D = B - A
    res = []
    for k in range(a+1, b):
        X = th[k].ravel() - A
        al = float((X*D).sum()/((D*D).sum()+1e-6))
        err = float(np.sqrt(((X - al*D)**2).mean()))
        res.append((k, al, err))
    return res
dissolves = []
# candidate windows: runs of 3..30 frames with elevated but not cut-like hist change
rel = (hd > 0.06) & (hd < 0.35)
i = 1
while i < N:
    if rel[i]:
        j = i
        while j+1 < N and rel[j+1]:
            j += 1
        L = j - i + 1
        if 3 <= L <= 30:
            a, b = max(0, i-1), min(N-1, j+1)
            fit = blend_fit(a, b)
            if fit:
                als = np.array([f[1] for f in fit]); errs = np.array([f[2] for f in fit])
                mono = np.all(np.diff(als) > -0.05)
                tot = float(np.sqrt(((th[b]-th[a])**2).mean()))
                if mono and tot > 20 and errs.max() < 0.35*tot and als[0] < 0.5 and als[-1] > 0.5:
                    dissolves.append(dict(start=int(a), end=int(b), frames=int(b-a-1), alpha=[round(x, 2) for x in als], max_resid=round(float(errs.max()), 2), total_change=round(tot, 1)))
        i = j+1
    else:
        i += 1

# --- PySceneDetect cross-check ---
psd = []
try:
    from scenedetect import open_video, SceneManager
    from scenedetect.detectors import ContentDetector, AdaptiveDetector
    v = open_video('work/ref/ref.mp4'); sm = SceneManager()
    sm.add_detector(AdaptiveDetector(adaptive_threshold=3.0, min_scene_len=3))
    sm.detect_scenes(v)
    psd = [int(s[0].get_frames()) for s in sm.get_scene_list()][1:]
except Exception as e:
    print('pyscenedetect failed', e)

both = [c for c in cuts if any(abs(c-p) <= 1 for p in psd)]
only_mine = [c for c in cuts if not any(abs(c-p) <= 1 for p in psd)]
only_psd = [p for p in psd if not any(abs(c-p) <= 1 for c in cuts)]
out = dict(convention='cut frame = first frame of new shot', n_cuts=len(cuts), cuts=cuts, pyscenedetect=psd,
           agree_within_1f=len(both), only_metrics=only_mine, only_pyscenedetect=only_psd,
           fades=fades, flashes=flashes, dissolves=dissolves)
json.dump(out, open('analysis/data/cuts_auto.json', 'w'), indent=1)
print('cuts', len(cuts), 'psd', len(psd), 'agree', len(both), 'only_mine', len(only_mine), 'only_psd', len(only_psd))
print('fades', len(fades), 'flashes', len(flashes), 'dissolves', len(dissolves))
