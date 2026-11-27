"""Final cut/transition list + shot list with per-shot camera motion, luma/sat and palette.

Decisions from visual verification (analysis/frames_events/ambiguous_cuts_*.jpg) are encoded below.
"""
import json, glob, numpy as np, pandas as pd, cv2
from sklearn.cluster import KMeans

m = pd.read_csv('analysis/data/frame_metrics.csv'); N = len(m)
cc = pd.read_csv('work/cut_candidates.csv')
auto = json.load(open('analysis/data/cuts_auto.json'))

# black-card intervals (chapter cards / end) from fades: frames where the whole frame is (almost) black are not cuts
black = set()
for f in auto['fades']:
    black.update(range(f['fade_out_start'], f['fade_in_end']+1))

EXCLUDE = {9100, 14021, 14044, 14100, 14116, 14131, 534, 960, 961, 962, 963, 11687, 11691, 2637, 2638, 12375, 9101}
FORCE = {4236, 4368, 7671, 9806, 13688, 12374}
cuts = []
for _, r in cc.iterrows():
    f = int(r.f)
    if f in EXCLUDE or f in black:
        continue
    if f in FORCE or (r.ratio >= 7 and r.one_minus_ssim >= 0.2):
        cuts.append(f)
for f in FORCE:
    if f not in cuts:
        cuts.append(f)
cuts = sorted(set(cuts))

# soft transitions (verified on frames / agent logs); 'boundary' = frame where the new shot is considered to start
transitions = [
    dict(kind='zoom_through_into_picture', start=528, end=533, boundary=534, note='camera zooms into the storybook illustration until its frame border leaves the screen'),
    dict(kind='zoom_out_of_picture_to_book', start=420, end=427, boundary=420, note='pull-out reveals the shot is an illustration in the storybook'),
    dict(kind='camera_flash_white', start=960, end=962, boundary=963, note='photo flash: 3 frames white (luma ~235) hides the cut to the polaroid'),
    dict(kind='photo_develop_flash_sepia', start=2196, end=2208, boundary=2196, note='white flash then desaturate to sepia polaroid'),
    dict(kind='fade_through_cream_white', start=2637, end=2646, boundary=2639, note='after orange glass-crack effect; solid white 2638-2640'),
    dict(kind='fade_to_white_then_stamp', start=5629, end=5636, boundary=5636, note='radial white flash into TWO DAYS LATER'),
    dict(kind='dissolve', start=6630, end=6640, boundary=6630, note='scene darkens under comment panel'),
    dict(kind='dissolve', start=6922, end=6935, boundary=6936, note='comment panel dissolves out'),
    dict(kind='zoom_through_thought_bubble', start=8091, end=8092, boundary=8092, note='thought-bubble image becomes the next shot'),
    dict(kind='haze_dissolve_pose_swap', start=11687, end=11691, boundary=11687, note='white haze cross-dissolve, same scene'),
    dict(kind='whip_1frame', start=12374, end=12374, boundary=12374, note='1 intermediate frame between shots'),
    dict(kind='gun_flash_white', start=12819, end=12824, boundary=12819, note='muzzle-flash whiteout masks the cut'),
    dict(kind='silhouette_to_colour_dissolve', start=12986, end=12989, boundary=12986, note='same shot, lighting change'),
    dict(kind='bloom_then_fade_black', start=15150, end=15170, boundary=15170, note='warm bloom then fade to black before CHAPTER IX'),
    dict(kind='dissolve_to_end_screen', start=16439, end=16443, boundary=16439, note='storybook end screen cross-dissolves in'),
    dict(kind='fade_to_black_end', start=16714, end=16727, boundary=16727, note='video ends on black'),
]
for f in auto['fades']:
    if f['black_start'] < 16700:
        transitions.append(dict(kind='chapter_card_fade_black', start=f['fade_out_start'], end=f['fade_in_end'], boundary=f['black_start'],
                                note=f"fade out {f['fade_out_start']}-{f['black_start']-1}, black/card {f['black_start']}-{f['black_end']}, fade in {f['black_end']+1}-{f['fade_in_end']}",
                                card_start=f['black_start'], card_end=f['black_end']))

bounds = sorted(set([0] + cuts + [t['boundary'] for t in transitions if t['kind'] not in ('haze_dissolve_pose_swap', 'silhouette_to_colour_dissolve', 'fade_to_black_end')] +
                    [t['end']+1 for t in transitions if t['kind'] == 'chapter_card_fade_black']))
bounds = [b for b in bounds if 0 <= b < N]
shots = []
th = None
for k, s in enumerate(bounds):
    e = (bounds[k+1]-1) if k+1 < len(bounds) else N-1
    seg = m.iloc[s:e+1]
    # camera: cumulative similarity from consecutive estimates (skip first frame of shot, which compares across the cut)
    a = seg.iloc[1:]
    good = a[(a.aff_inl >= 40)]
    sc = np.where(a.aff_inl >= 40, a.aff_s.fillna(1.0), 1.0)
    tx = np.where(a.aff_inl >= 40, a.aff_tx.fillna(0.0), 0.0); ty = np.where(a.aff_inl >= 40, a.aff_ty.fillna(0.0), 0.0)
    rot = np.where(a.aff_inl >= 40, a.aff_rot.fillna(0.0), 0.0)
    cum_s = float(np.prod(sc)) if len(sc) else 1.0
    kind = []
    if cum_s > 1.01: kind.append('push_in')
    if cum_s < 0.99: kind.append('pull_out')
    if abs(tx.sum()) > 6: kind.append('pan_' + ('left' if tx.sum() > 0 else 'right'))   # content moves right => camera pans left
    if abs(ty.sum()) > 6: kind.append('tilt_' + ('up' if ty.sum() > 0 else 'down'))
    if not kind: kind.append('static')
    shots.append(dict(shot=k, start=int(s), end=int(e), frames=int(e-s+1), seconds=round((e-s+1)/30, 2),
                      cam_scale_total=round(cum_s, 4), cam_zoom_pct_per_s=round((cum_s**(30/max(1, len(sc)))-1)*100, 3),
                      cam_tx_total_px=round(float(tx.sum()), 1), cam_ty_total_px=round(float(ty.sum()), 1), cam_rot_total_deg=round(float(rot.sum()), 3),
                      cam_kind='+'.join(kind), tracked_frac=round(float((a.aff_inl >= 40).mean()) if len(a) else 0, 2),
                      y_mean=round(float(seg.y_mean.mean()), 1), y_std=round(float(seg.y_std.mean()), 1), sat_mean=round(float(seg.s_mean.mean()), 1),
                      edge_density=round(float(seg.edge_density.mean()), 4)))

# palette per shot (k-means k=6 on the middle frame at 1/4 res), hex sorted by share
for sh in shots:
    mid = (sh['start']+sh['end'])//2
    im = cv2.imread(f'work/frames/f_{mid:05d}.png')[:, :, ::-1]
    px = cv2.resize(im, (214, 120), interpolation=cv2.INTER_AREA).reshape(-1, 3).astype(np.float32)
    km = KMeans(n_clusters=6, n_init=3, random_state=0).fit(px)
    cnt = np.bincount(km.labels_, minlength=6); order = np.argsort(-cnt)
    sh['palette'] = ['#%02x%02x%02x' % tuple(int(v) for v in km.cluster_centers_[i]) for i in order]
    sh['palette_share'] = [round(float(cnt[i]/cnt.sum()), 3) for i in order]
    sh['mid_frame'] = int(mid)

# attach agent descriptions (shot lines overlapping most)
ag = []
for f in sorted(glob.glob('analysis/visual_review/part_*.jsonl')):
    for line in open(f):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('type') == 'shot':
            ag.append(r)
for sh in shots:
    best, bo = None, 0
    for r in ag:
        f0 = int(r['f0']); f1 = int(r['f1']) if r.get('f1') is not None else f0
        ov = min(f1, sh['end']) - max(f0, sh['start']) + 1
        if ov > bo:
            best, bo = r, ov
    sh['content'] = (best or {}).get('note', '')
    sh['framing'] = (best or {}).get('where', '')

json.dump(dict(convention='cut frame = first frame of new shot; frame N = N/30 s', n_hard_cuts=len(cuts), hard_cuts=cuts,
               transitions=sorted(transitions, key=lambda t: t['start'])), open('analysis/data/cuts.json', 'w'), indent=1)
df = pd.DataFrame(shots)
df.to_csv('analysis/data/shots.csv', index=False)
json.dump(shots, open('analysis/data/shots.json', 'w'), indent=1)
L = df.frames.values
print('shots', len(df), 'hard cuts', len(cuts))
print('shot length frames: median %.0f mean %.1f p10 %.0f p90 %.0f min %d max %d' % (np.median(L), L.mean(), np.percentile(L, 10), np.percentile(L, 90), L.min(), L.max()))
print(df.cam_kind.value_counts().head(12))
print(df[['shot', 'start', 'end', 'frames', 'cam_scale_total', 'cam_zoom_pct_per_s', 'cam_tx_total_px', 'cam_ty_total_px', 'cam_kind', 'tracked_frac']].head(40).to_string())
