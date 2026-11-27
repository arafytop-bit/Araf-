"""Calibration check: measure the rebuild with the same tools used on the reference; list mismatches > 1 frame.

usage: python a20_calibrate.py <rebuild_frame_dir> <tag>
Checks: (1) cuts, (2) camera/layer motion timing + position error, (3) title element timings, (4) list-item text/icon
timings + icon scale curve, (5) reward suffix changes, (6) SFX onsets (synth from blueprint recipes vs reference drums stem).
"""
import sys, json, numpy as np, cv2, soundfile as sf, librosa, pandas as pd
RB, TAG = sys.argv[1], sys.argv[2]
bp = json.load(open('analysis/blueprint.json')); cal = bp['calibration']
ref = lambda i: cv2.imread(f'work/frames/f_{i:05d}.png')
reb = lambda i: cv2.imread(f'{RB}/element-{i:03d}.png')
N = 150
out = {'tag': TAG}; mism = []
def flag(cat, item, ref_f, reb_f, note=''):
    d = None if (ref_f is None or reb_f is None) else int(reb_f - ref_f)
    both_na = ref_f is None and reb_f is None
    row = dict(category=cat, item=item, reference_frame=ref_f, rebuild_frame=reb_f, delta_frames=d, mismatch=(not both_na) and (d is None or abs(d) > 1),
               note=(note + ' n/a in both (outside calibration window)').strip() if both_na else note)
    mism.append(row); return row

# (1) cuts: big global change
def cut_frames(load):
    prev = None; res = []
    for i in range(N):
        g = cv2.cvtColor(cv2.resize(load(i), (214, 120)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            mad = np.abs(g - prev).mean()
            hist = cv2.compareHist(cv2.calcHist([g.astype(np.uint8)], [0], None, [32], [0, 256]), cv2.calcHist([prev.astype(np.uint8)], [0], None, [32], [0, 256]), cv2.HISTCMP_BHATTACHARYYA)
            res.append((i, mad, hist))
        prev = g
    return res
cr = cut_frames(ref); cb = cut_frames(reb)
def pick_cuts(r):
    mads = np.array([x[1] for x in r]); med = np.median(mads)
    return [x[0] for x in r if x[1] > max(25, 6*med) and x[2] > 0.25]
rc, bc = pick_cuts(cr), pick_cuts(cb)
out['cuts'] = dict(reference=rc, rebuild=bc)
for c in rc:
    m = min(bc, key=lambda b: abs(b-c)) if bc else None
    flag('cut', f'hard cut', c, m)
for b in bc:
    if not any(abs(b-c) <= 1 for c in rc): flag('cut', 'extra cut in rebuild', None, b)

# (2) camera: SIFT direct registration to frame 75 (poster) and frame 0 hero/background region
sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02); bf = cv2.BFMatcher(cv2.NORM_L2); C = np.array([427.0, 240.0])
def track(load, refi, f0, f1, box):
    x0, y0, x1, y1 = box
    g0 = cv2.cvtColor(load(refi), cv2.COLOR_BGR2GRAY); mask = np.zeros_like(g0); mask[y0:y1, x0:x1] = 255
    k0, d0 = sift.detectAndCompute(g0, mask); res = {}
    for i in range(f0, f1+1):
        g = cv2.cvtColor(load(i), cv2.COLOR_BGR2GRAY); k1, d1 = sift.detectAndCompute(g, None)
        try:
            mt = bf.knnMatch(d0, d1, k=2); good = [a for a, b in (x for x in mt if len(x) == 2) if a.distance < 0.75*b.distance]
            p0 = np.float32([k0[m.queryIdx].pt for m in good]); p1 = np.float32([k1[m.trainIdx].pt for m in good])
            M, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=1.5)
            s = float(np.hypot(M[0, 0], M[1, 0])); t = M[:, 2] + M[:, :2] @ C - C
            res[i] = (s, float(t[0]), float(t[1]), int(inl.sum()))
        except Exception:
            res[i] = (np.nan, np.nan, np.nan, 0)
    return res
P_ref = pd.read_csv('analysis/data/tracks/s1_poster_75_68_176.csv').set_index('frame')
P_reb = track(reb, 75, 68, 149, (250, 0, 610, 480))
A_ref = pd.read_csv('analysis/data/tracks/s0_arthur_0_0_67.csv').set_index('frame')
A_reb = track(reb, 0, 0, 67, (400, 40, 760, 470))
cam_rows = []
for i in range(68, 150):
    rs, rtx, rty = P_ref.loc[i, ['s', 'tx', 'ty']]; bs, btx, bty, n = P_reb[i]
    cam_rows.append(dict(frame=i, ref_s=rs, reb_s=bs, ref_ty=rty, reb_ty=bty, ds_pct=100*(bs-rs)/rs, dty_px=bty-rty, inl=n))
for i in range(0, 68):
    rs = A_ref.loc[i, 's']; bs = A_reb[i][0]
    cam_rows.append(dict(frame=i, ref_s=rs, reb_s=bs, ref_ty=np.nan, reb_ty=np.nan, ds_pct=100*(bs-rs)/rs, dty_px=np.nan, inl=A_reb[i][3]))
cam = pd.DataFrame(cam_rows).sort_values('frame')
hold = cam[(cam.frame >= 73) & (cam.frame <= 81)]
cam['dty_px'] = (cam.reb_ty - hold.reb_ty.median()) - (cam.ref_ty - hold.ref_ty.median())
cam.to_csv(f'analysis/calibration/{TAG}_camera_compare.csv', index=False)
# timing of moves: frame where progress crosses 10/50/90 %
def crossings(series, f0, f1, v0, v1):
    out = {}
    for q in (0.1, 0.5, 0.9):
        thr = v0 + q*(v1-v0); hit = None
        for f in range(f0, f1+1):
            v = series(f)
            if v is None or np.isnan(v): continue
            if (v1 > v0 and v >= thr) or (v1 < v0 and v <= thr): hit = f; break
        out[q] = hit
    return out
moves = [('poster settle scale', 68, 74, 's', 1.22, 1.0), ('push-in scale', 82, 92, 's', 1.0, 1.42), ('push-in ty', 82, 92, 'ty', -2.5, -123.3),
         ('nudge 1 ty', 111, 119, 'ty', -123.3, -143.3), ('nudge 2 ty', 126, 135, 'ty', -144.7, -162.0), ('pull-out scale', 139, 149, 's', 1.419, 1.0)]
for name, f0, f1, prop, v0, v1 in moves:
    rser = lambda f: float(P_ref.loc[f, prop])
    bser = lambda f: P_reb[f][0] if prop == 's' else P_reb[f][2]
    # thresholds from each series' own start/end values (robust to constant offsets)
    rv0, rv1 = rser(f0), rser(min(f1, 149)); bv0, bv1 = bser(f0), bser(min(f1, 149))
    if prop == 's' and name.startswith('pull-out'): rv1, bv1 = v1, v1
    rcx = crossings(rser, f0, f1, rv0, rv1); bcx = crossings(bser, f0, f1, bv0, bv1)
    for q in (0.1, 0.5, 0.9):
        flag('motion', f'{name} {int(q*100)}%', rcx[q], bcx[q])
hero = [('hero push phase a', 0, 33, 1.0, 1.052), ('hero push phase b', 34, 50, 1.053, 1.103)]
for name, f0, f1, v0, v1 in hero:
    rcx = crossings(lambda f: float(A_ref.loc[f, 's']), f0, f1, v0, v1); bcx = crossings(lambda f: A_reb[f][0], f0, f1, v0, v1)
    for q in (0.1, 0.5, 0.9): flag('motion', f'{name} {int(q*100)}%', rcx[q], bcx[q])
sel = cam[(cam.frame >= 72) & (cam.frame <= 149)]
out['camera_error'] = dict(max_abs_ds_pct=round(float(sel.ds_pct.abs().max()), 2), median_abs_ds_pct=round(float(sel.ds_pct.abs().median()), 2),
                           max_abs_dty_px=round(float(sel.dty_px.abs().max()), 1), median_abs_dty_px=round(float(sel.dty_px.abs().median()), 1),
                           hero_max_abs_ds_pct=round(float(cam[cam.frame < 68].ds_pct.abs().max()), 2))

# (3) title timings (band luminance rise relative to frame 34 of the same video)
def L(img): return 0.2126*img[..., 2]+0.7152*img[..., 1]+0.0722*img[..., 0]
bands = {'title ARTHUR': (322, 354, 40, 265), 'title MORGAN': (375, 403, 40, 265)}
def band_times(load):
    B = L(load(34).astype(np.float32)); res = {}
    for k, (a, b, x0, x1) in bands.items():
        vals = [float(np.clip(L(load(i).astype(np.float32))[a:b, x0:x1]-B[a:b, x0:x1], 0, None).mean()) for i in range(34, 60)]
        v = np.array(vals); fin = v[-5:].mean()
        first = next((34+j for j, x in enumerate(v) if x > 0.08*fin), None); half = next((34+j for j, x in enumerate(v) if x > 0.5*fin), None); full = next((34+j for j, x in enumerate(v) if x > 0.92*fin), None)
        res[k] = (first, half, full)
    return res
tr, tb = band_times(ref), band_times(reb)
for k in bands:
    for j, nm in enumerate(['first visible', '50%', '92% settled']):
        flag('text', f'{k} {nm}', tr[k][j], tb[k][j])
# rule: horizontal span of new bright pixels (draw-from-centre); sub-line: 95th-pct contrast (robust to grass/dust)
def rule_and_sub(load):
    B = L(load(34).astype(np.float32)); spans = []; subs = []
    for i in range(34, 60):
        D = L(load(i).astype(np.float32)) - B
        col = D[414:423, 40:275].max(0); on = np.where(col > 25)[0]
        spans.append(float(on[-1]-on[0]+1) if len(on) > 1 else 0.0)
        subs.append(float(np.percentile(np.clip(D[437:451, 115:205], 0, None), 95)))
    sp = np.array(spans); su = np.array(subs); fs, fu = sp[-5:].mean(), su[-5:].mean()
    g = lambda v, fin, q: next((34+j for j, x in enumerate(v) if x > q*fin), None)
    return (g(sp, fs, 0.05), g(sp, fs, 0.5), g(sp, fs, 0.92)), (g(su, fu, 0.3), g(su, fu, 0.5), g(su, fu, 0.92))
(rr_, rs_), (br_, bs_) = rule_and_sub(ref), rule_and_sub(reb)
for j, nm in enumerate(['first visible', '50% width', '92% width']): flag('text', f'title rule {nm}', rr_[j], br_[j])
for j, nm in enumerate(['first visible', '50%', '92% settled']): flag('text', f"title (that's you) {nm}", rs_[j], bs_[j])

# (4)+(5) list items & reward: stabilise each video with its own poster track, then measure red icon width and text contrast
def stab(load, track_fn, i):
    s, tx, ty = track_fn(i)
    I = load(i).astype(np.float32); H2, W2 = 960, 1708
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)/2
    pf = np.stack([xx-C[0], yy-C[1]], -1)*s + C + np.array([tx, ty])
    return cv2.remap(I, pf[..., 0].astype(np.float32), pf[..., 1].astype(np.float32), cv2.INTER_LINEAR)
ref_tr = lambda i: tuple(P_ref.loc[i, ['s', 'tx', 'ty']])
reb_tr = lambda i: P_reb[i][:3]
rows = {'TRAINS': (312, 84, 95), 'BANKS': (349.5, 113, 124), 'HALF THE WEST': (386.5, 129, 140)}
def item_times(load, trf):
    res = {}
    for nm, (cy, fa, fb) in rows.items():
        B = stab(load, trf, fa)
        tx_series = []; icon_series = []
        for i in range(fa, fb+1):
            I = stab(load, trf, i)
            D = np.abs(I-B).sum(2)
            tx_series.append(float(D[int((cy-12)*2):int((cy+12)*2), 360*2:470*2].mean()))
            P = I[int((cy-25)*2):int((cy+25)*2), (334-45)*2:(334+45)*2]
            red = (P[..., 2]-P[..., 1] > 60) & (P[..., 2]-P[..., 0] > 50)
            Q = B[int((cy-25)*2):int((cy+25)*2), (334-45)*2:(334+45)*2]; redb = (Q[..., 2]-Q[..., 1] > 60) & (Q[..., 2]-Q[..., 0] > 50)
            ys, xs = np.where(red & ~redb)
            icon_series.append((xs.max()-xs.min())/2 if len(xs) > 30 else 0.0)
        t = np.array(tx_series); fin = t[-3:].mean()
        tfirst = fa + int(np.argmax(t > 0.1*fin)); thalf = fa + int(np.argmax(t > 0.5*fin))
        ic = np.array(icon_series); icfirst = fa + int(np.argmax(ic > 5)) if (ic > 5).any() else None
        final_w = np.median(ic[-3:]); settle = None
        if icfirst is not None:
            for j in range(int(np.argmax(ic > 5)), len(ic)):
                if abs(ic[j]-final_w) <= 0.06*final_w: settle = fa+j; break
        res[nm] = dict(text_first=tfirst, text_50=thalf, icon_first=icfirst, icon_settled=settle, icon_width_series=[round(float(x), 1) for x in ic])
    return res
ir, ib = item_times(ref, ref_tr), item_times(reb, reb_tr)
for nm in rows:
    for key in ['text_first', 'text_50', 'icon_first', 'icon_settled']:
        flag('list item', f'{nm} {key}', ir[nm][key], ib[nm][key])
out['list_items'] = dict(reference=ir, rebuild=ib)
def reward_changes(load, trf):
    r = []
    for i in range(72, 142):
        I = stab(load, trf, i)[425*2:452*2, 440*2:520*2]; r.append(int((I[..., 2]-I[..., 1] > 50).sum()))
    r = np.array(r); res = []
    for j in range(1, len(r)-3):
        # a persistent step: next 3 frames stay above the previous level + 60 % of the jump, and the jump is >= 15 %
        jump = r[j] - r[j-1]
        if jump > max(30, 0.15*r[j-1]) and min(r[j:j+3]) > r[j-1] + 0.6*jump and all(abs(72+j-x) > 2 for x in res):
            res.append(72+j)
    return res
rr, rb = reward_changes(ref, ref_tr), reward_changes(reb, reb_tr)
out['reward_changes'] = dict(reference=rr, rebuild=rb)
for f in rr:
    m = min(rb, key=lambda b: abs(b-f)) if rb else None; flag('text', 'reward ? appended', f, m)

# (6) SFX: synthesise from blueprint recipes, detect onsets, compare with reference drums-stem onsets (0-160 f)
SR = 44100
def synth(recipe, rng):
    r = cal['sfx_recipes'][recipe]; n = int(0.6*SR); t = np.arange(n)/SR; y = np.zeros(n)
    def bp_noise(lo, hi, length):
        x = rng.standard_normal(length); X = np.fft.rfft(x); fr = np.fft.rfftfreq(length, 1/SR); X[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(X, length)
    att = r.get('attack_ms', 3)/1000; env = np.minimum(1, t/att) * np.exp(-np.maximum(0, t-att)/(r.get('decay_tau_ms', 40)/1000))
    if 'noise_band_hz' in r: y += bp_noise(*r['noise_band_hz'], n) * env
    if 'sine_sweep_hz' in r:
        f0, f1 = r['sine_sweep_hz']; sw = r['sweep_ms']/1000; fi = f0 + (f1-f0)*np.minimum(1, t/sw); y += 2.5*np.sin(2*np.pi*np.cumsum(fi)/SR) * env
        y += bp_noise(*r['click_band_hz'], n) * np.exp(-t/(r['click_ms']/1000))
    if 'low_thump' in r: y += 2*np.sin(2*np.pi*r['low_thump']['hz']*t) * np.exp(-t/(r['low_thump']['ms']/1000))
    if 'band_hz' in r: y += bp_noise(*r['band_hz'], n) * np.exp(-t/(r['ms']/1000))
    if 'am_hz' in r: y *= 0.6 + 0.4*np.sin(2*np.pi*r['am_hz']*t)
    y /= np.abs(y).max() + 1e-9; return y * 10**(r['peak_dbfs']/20)
rng = np.random.default_rng(1); track_len = int(5.5*SR); sfxtrack = np.zeros(track_len)
for c in cal['sfx']:
    y = synth(c['recipe'], rng); a = int(c['f']*1470); b = min(track_len, a+len(y)); sfxtrack[a:b] += y[:b-a]
sf.write(f'analysis/calibration/{TAG}_sfx_track.wav', sfxtrack.astype(np.float32), SR)
def onsets(x):
    o = librosa.onset.onset_detect(y=x.astype(np.float32), sr=SR, hop_length=735, backtrack=True, units='samples', delta=0.3, wait=4)
    return sorted(set(int(s//1470) for s in o))
dr = sf.read('work/stems/drums.wav', dtype='float32', always_2d=True)[0].mean(1)[:int(5.4*SR)]
ref_on = [f for f in onsets(dr) if f >= 60]   # >= 60: before the poster shot the drums stem carries the score's cymbal, not SFX
reb_on = onsets(sfxtrack)
out['sfx'] = dict(reference_onsets=ref_on, rebuild_onsets=reb_on)
for f in [c['f'] for c in cal['sfx']]:
    m = min(ref_on, key=lambda r: abs(r-f)) if ref_on else None
    flag('sfx', f'cue at plan frame {f}', m, min(reb_on, key=lambda r: abs(r-f)) if reb_on else None, note='reference onset = nearest drums-stem onset')
for r in ref_on:
    if r <= 160 and not any(abs(r-c['f']) <= 2 for c in cal['sfx']): flag('sfx', 'reference onset without a planned cue', r, None)

df = pd.DataFrame(mism); df.to_csv(f'analysis/calibration/{TAG}_mismatches.csv', index=False)
out['summary'] = dict(checks=len(df), mismatches_gt1f=int(df.mismatch.sum()), within_1f=int((~df.mismatch).sum()))
json.dump(out, open(f'analysis/calibration/{TAG}_report.json', 'w'), indent=1, default=lambda o: None if o is None else (float(o) if isinstance(o, (np.floating,)) else int(o)))
pd.set_option('display.width', 200); print(df.to_string()); print(out['summary']); print('camera', out['camera_error']); print('reward', out['reward_changes']); print('sfx', out['sfx'])
