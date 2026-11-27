"""SFX candidate detection on non-vocal stems + per-event measurements.

Onsets: librosa spectral-flux onsets (hop 735 = 1/60 s) on drums and other stems separately, backtracked.
A candidate is kept as SFX-like if its short-term peak exceeds the stem's local (+-3 s) median level by >= CONTRAST dB.
Video frame of an event = floor(onset_sample / 1470).
Per event: peak dBFS, attack (10->90 % of envelope peak, ms), decay (peak -> -20 dB, ms), duration (> peak-30 dB), centroid at
start/peak/end (Hz) -> pitch movement, band ratios, spectral flatness, stereo pan & width.
Output: analysis/data/sfx_candidates.csv
"""
import numpy as np, soundfile as sf, librosa, pandas as pd, sys

SR = 44100; HOP_V = 1470; HOP = 735
CONTRAST = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
stems = {n: sf.read(f'work/stems/{n}.wav', dtype='float32', always_2d=True)[0] for n in ['drums', 'other', 'bass', 'vocals']}

def env_db(x, win=220):  # 5 ms RMS envelope (dB) at 220-sample hop
    n = len(x)//win
    b = x[:n*win].reshape(n, win)
    return 20*np.log10(np.sqrt((b**2).mean(1)) + 1e-9)

rows = []
for stem in ['drums', 'other']:
    st = stems[stem]; mono = st.mean(1)
    oenv = librosa.onset.onset_strength(y=mono, sr=SR, hop_length=HOP, n_fft=2048, lag=1, max_size=3, aggregate=np.median)
    ons = librosa.onset.onset_detect(onset_envelope=oenv, sr=SR, hop_length=HOP, backtrack=True, units='samples',
                                     pre_max=6, post_max=6, pre_avg=30, post_avg=30, delta=0.25, wait=4)
    e = env_db(mono)                                   # 5 ms frames
    med = pd.Series(e).rolling(int(6.0/0.005), center=True, min_periods=1).median().values   # +-3 s
    for s in ons:
        k0 = s//220; k1 = min(len(e)-1, k0 + int(0.12/0.005))
        if k1 <= k0:
            continue
        pk_i = k0 + int(np.argmax(e[k0:k1+1])); pk = e[pk_i]
        contrast = pk - med[pk_i]
        if contrast < CONTRAST or pk < -60:
            continue
        # attack: last frame before peak where env < pk-20dB (search back up to 300 ms from peak)
        lo = max(0, pk_i - 60)
        pre = e[lo:pk_i+1]
        lin = 10**(pre/20); pl = 10**(pk/20)
        try:
            a10 = lo + np.where(lin < 0.1*pl)[0][-1]
        except IndexError:
            a10 = lo
        a90 = lo + np.where(lin >= 0.9*pl)[0][0]
        attack_ms = max(0.0, (a90 - a10)*5.0)
        post = e[pk_i:pk_i+int(3.0/0.005)]
        floor = med[pk_i]
        d20 = np.where(post < pk-20)[0]; decay_ms = float(d20[0]*5.0) if len(d20) else float(len(post)*5.0)
        dfl = np.where(post < max(pk-30, floor+3))[0]; dur_ms = float(dfl[0]*5.0 + (pk_i-a10)*5.0) if len(dfl) else float(len(post)*5.0)
        # spectral shape over the event
        seg0 = int(a10*220); seg1 = int(min(len(mono), (pk_i*220) + max(4410, int(dur_ms/1000*SR))))
        seg = mono[seg0:seg1]
        if len(seg) < 2048:
            seg = np.pad(seg, (0, 2048-len(seg)))
        S = np.abs(librosa.stft(seg, n_fft=2048, hop_length=512))
        fr = librosa.fft_frequencies(sr=SR, n_fft=2048)
        cen = (S*fr[:, None]).sum(0)/(S.sum(0)+1e-9)
        en = (S**2).sum(0); kpk = int(np.argmax(en))
        tot = (S**2).sum()+1e-12
        band = lambda a, b: float((S[(fr >= a) & (fr < b)]**2).sum()/tot)
        flat = float(librosa.feature.spectral_flatness(S=S).mean())
        valid = en > en.max()*0.01
        c_start = float(cen[valid][0]) if valid.any() else float(cen[0]); c_end = float(cen[valid][-1]) if valid.any() else float(cen[-1])
        # stereo
        w0, w1 = seg0, seg1
        L = st[w0:w1, 0]; R = st[w0:w1, 1]
        rl = np.sqrt((L**2).mean())+1e-12; rr = np.sqrt((R**2).mean())+1e-12
        mid = (L+R)/2; side = (L-R)/2
        rows.append(dict(stem=stem, onset_s=round(s/SR, 4), frame=int(s//HOP_V), peak_frame=int((pk_i*220)//HOP_V),
                         peak_dbfs=round(pk, 1), contrast_db=round(contrast, 1), attack_ms=round(attack_ms, 1), decay20_ms=round(decay_ms, 1),
                         dur_ms=round(dur_ms, 1), centroid_peak_hz=round(float(cen[kpk]), 0), centroid_start_hz=round(c_start, 0),
                         centroid_end_hz=round(c_end, 0), sub_lt60=round(band(20, 60), 3), low_60_250=round(band(60, 250), 3),
                         mid_250_2k=round(band(250, 2000), 3), high_2k_8k=round(band(2000, 8000), 3), air_gt8k=round(band(8000, 22050), 3),
                         flatness=round(flat, 4), pan_R_minus_L_db=round(20*np.log10(rr/rl), 2),
                         side_mid=round(float(np.sqrt((side**2).mean())/(np.sqrt((mid**2).mean())+1e-12)), 3)))

df = pd.DataFrame(rows).sort_values('onset_s').reset_index(drop=True)

def classify(r):
    c = r.centroid_peak_hz; slope = r.centroid_end_hz - r.centroid_start_hz
    if r.attack_ms >= 250 and slope > 800:
        return 'riser'
    if r.attack_ms >= 60 and r.flatness > 0.05 and r.dur_ms >= 150:
        return 'whoosh'
    if (r.sub_lt60 + r.low_60_250) > 0.45 and r.attack_ms < 30 and r.decay20_ms >= 120:
        return 'impact/thud'
    if r.dur_ms < 90 and c > 2500:
        return 'click/tick'
    if r.dur_ms < 150 and r.attack_ms < 20:
        return 'pop/hit'
    if r.flatness < 0.01 and c > 1500 and r.decay20_ms > 200:
        return 'ding/chime (tonal)'
    if r.flatness > 0.1 and r.dur_ms > 300:
        return 'noise (swish/paper/crowd)'
    return 'other'

df['category_guess'] = df.apply(classify, axis=1)
# merge near-duplicate detections across stems (same event within 2 frames): keep the louder, list both stems
df = df.sort_values(['frame', 'peak_dbfs'], ascending=[True, False])
keep = []; last = -99
for i, r in df.iterrows():
    if keep and abs(r.frame - df.loc[keep[-1], 'frame']) <= 1:
        df.loc[keep[-1], 'stem'] = df.loc[keep[-1], 'stem'] + '+' + r.stem if r.stem not in df.loc[keep[-1], 'stem'] else df.loc[keep[-1], 'stem']
        continue
    keep.append(i)
df = df.loc[keep].sort_values('onset_s').reset_index(drop=True)
df.to_csv('analysis/data/sfx_candidates.csv', index=False)
print(len(df), 'candidates'); print(df.category_guess.value_counts())
print(df.head(40).to_string())
