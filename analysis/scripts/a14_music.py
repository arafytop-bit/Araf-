"""Music analysis on Demucs stems (drums+bass+other = music+SFX bed).

1. Cue segmentation: novelty on chroma+MFCC (1 s hop) of other+bass, peaks -> boundaries; plus silence gaps.
2. Per segment: tempo (beat_track) + tempo confidence, beat frames, key (Krumhansl-Kessler), level (LUFS), brightness.
3. Ducking: music level (other+bass, 400 ms RMS) event-locked to voice onsets/offsets around pauses >= 0.6 s.
Outputs: analysis/data/music.json, analysis/data/beats.json, analysis/plots/music_*.png
"""
import json, numpy as np, soundfile as sf, librosa, pyloudnorm as pyln, scipy.signal as sg
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SR = 44100; HOP_V = 1470
st = {n: sf.read(f'work/stems/{n}.wav', dtype='float32', always_2d=True)[0] for n in ['drums', 'bass', 'other', 'vocals']}
mus = st['other'] + st['bass']; mus_all = mus + st['drums']
mono = mus.mean(1); mono_all = mus_all.mean(1)
y22 = librosa.resample(mono, orig_sr=SR, target_sr=22050); ya22 = librosa.resample(mono_all, orig_sr=SR, target_sr=22050)
hop = 22050  # 1 s
C = librosa.feature.chroma_cqt(y=y22, sr=22050, hop_length=2205*2)   # 0.2 s
M = librosa.feature.mfcc(y=y22, sr=22050, n_mfcc=13, hop_length=2205*2)
rms = librosa.feature.rms(y=y22, frame_length=8820, hop_length=4410)[0]
feat = np.vstack([librosa.util.normalize(C, axis=0), (M - M.mean(1, keepdims=True))/(M.std(1, keepdims=True)+1e-6)*0.3])
# smoothed checkerboard novelty on SSM
F = librosa.util.normalize(feat, axis=0)
Fs = sg.medfilt2d(F, (1, 5))
SSM = Fs.T @ Fs
L = 20  # 4 s kernel half-width
g = np.outer(sg.windows.gaussian(2*L, L/2), sg.windows.gaussian(2*L, L/2))
ker = g*np.kron(np.array([[1, -1], [-1, 1]]), np.ones((L, L)))
n = SSM.shape[0]; nov = np.zeros(n)
P = np.pad(SSM, L, mode='edge')
for i in range(n):
    nov[i] = (P[i:i+2*L, i:i+2*L]*ker).sum()
nov = np.maximum(nov, 0); nov /= nov.max()
pk, _ = sg.find_peaks(nov, height=0.25, distance=40)   # >= 8 s apart
bt = pk*0.2
# silence gaps in music (rms < -55 dBFS for >= 0.4 s)
rdb = 20*np.log10(rms+1e-9); sil = rdb < -55
gaps = []
i = 0
while i < len(sil):
    if sil[i]:
        j = i
        while j+1 < len(sil) and sil[j+1]: j += 1
        if (j-i+1)*0.2 >= 0.4: gaps.append((round(i*0.2, 2), round((j+1)*0.2, 2)))
        i = j+1
    else: i += 1
bounds = sorted(set([0.0] + [round(b, 1) for b in bt] + [g[0] for g in gaps] + [g[1] for g in gaps] + [len(mono)/SR]))
# merge boundaries closer than 3 s
mb = [bounds[0]]
for b in bounds[1:]:
    if b - mb[-1] >= 3.0: mb.append(b)
    else: mb[-1] = b if b == len(mono)/SR else mb[-1]
KK_major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
meter = pyln.Meter(SR)
segs = []; all_beats = []
for a, b in zip(mb[:-1], mb[1:]):
    i0, i1 = int(a*SR), int(b*SR)
    x = mono_all[i0:i1]; xh = mono[i0:i1]
    lvl = float(20*np.log10(np.sqrt((xh**2).mean())+1e-9))
    seg = dict(start_s=round(a, 2), end_s=round(b, 2), start_f=int(round(a*30)), end_f=int(round(b*30))-1, rms_dbfs=round(lvl, 1))
    if b - a >= 3 and lvl > -55:
        try:
            seg['lufs'] = round(float(meter.integrated_loudness(mus_all[i0:i1].astype(np.float64))), 1)
        except Exception:
            pass
        x22 = ya22[int(a*22050):int(b*22050)]
        oenv = librosa.onset.onset_strength(y=x22, sr=22050, hop_length=735)
        tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=22050, hop_length=735, start_bpm=110, tightness=100)
        tempo = float(np.atleast_1d(tempo)[0])
        # tempo confidence: autocorrelation peak strength at the beat period
        ac = librosa.autocorrelate(oenv - oenv.mean()); ac /= ac[0] + 1e-9
        lag = int(round(60/tempo*30)) if tempo > 0 else 0
        conf = float(ac[lag-1:lag+2].max()) if 2 < lag < len(ac)-2 else 0.0
        seg.update(bpm=round(tempo, 1), tempo_conf=round(conf, 3), n_beats=int(len(beats)))
        bf = [int(seg['start_f'] + b_) for b_ in beats]    # hop 735 @22.05k = 1 video frame
        all_beats += [dict(frame=f, seg_start_f=seg['start_f']) for f in bf]
        seg['beat_frames_first8'] = bf[:8]
        chroma = librosa.feature.chroma_cens(y=librosa.resample(xh, orig_sr=SR, target_sr=22050), sr=22050).mean(1)
        sc = []
        for k in range(12):
            sc.append(('maj', k, np.corrcoef(np.roll(KK_major, k), chroma)[0, 1])); sc.append(('min', k, np.corrcoef(np.roll(KK_minor, k), chroma)[0, 1]))
        sc.sort(key=lambda r: -r[2])
        seg['key'] = f"{names[sc[0][1]]} {'major' if sc[0][0] == 'maj' else 'minor'}"; seg['key_corr'] = round(float(sc[0][2]), 3)
        seg['key_2nd'] = f"{names[sc[1][1]]} {'major' if sc[1][0] == 'maj' else 'minor'}"
        cen = librosa.feature.spectral_centroid(y=xh[::2], sr=22050)[0]
        seg['centroid_hz_median'] = round(float(np.median(cen)), 0)
        dr = st['drums'][i0:i1].mean(1); seg['drums_rms_dbfs'] = round(float(20*np.log10(np.sqrt((dr**2).mean())+1e-9)), 1)
        bs = st['bass'][i0:i1].mean(1); seg['bass_rms_dbfs'] = round(float(20*np.log10(np.sqrt((bs**2).mean())+1e-9)), 1)
    segs.append(seg)

# ---- ducking analysis ----
words = json.load(open('analysis/data/words.json'))
v_on = []; v_off = []
for k in range(1, len(words)):
    if words[k]['start_s'] - words[k-1]['end_s'] >= 0.6:
        v_on.append(words[k]['start_s']); v_off.append(words[k-1]['end_s'])
def env_db(x, win_s=0.1):
    w = int(win_s*SR); n = len(x)//w
    return 20*np.log10(np.sqrt((x[:n*w].reshape(n, w)**2).mean(1))+1e-9)
E = env_db(mono, 0.05)   # 50 ms
def locked(times, pre=1.0, post=1.5):
    rows = []
    for t in times:
        a = int((t-pre)/0.05); b = int((t+post)/0.05)
        if a >= 0 and b < len(E): rows.append(E[a:b])
    R = np.array(rows); return np.median(R, 0), np.arange(-pre, post, 0.05)[:R.shape[1]], len(rows)
on_curve, tax, n_on = locked(v_on); off_curve, tax2, n_off = locked(v_off, 1.5, 1.0)
# voice active vs inactive music level
vact = np.zeros(len(E), bool)
for w in words:
    vact[int(w['start_s']/0.05):int(w['end_s']/0.05)+1] = True
duck = dict(music_rms_db_voice_active_median=round(float(np.median(E[vact & (E > -70)])), 1),
            music_rms_db_voice_inactive_median=round(float(np.median(E[~vact & (E > -70)])), 1),
            n_onsets=n_on, n_offsets=n_off,
            onset_locked_curve_db=[round(float(v), 1) for v in on_curve], onset_locked_t_s=[round(float(t), 2) for t in tax],
            offset_locked_curve_db=[round(float(v), 1) for v in off_curve], offset_locked_t_s=[round(float(t), 2) for t in tax2])
pre = np.median(on_curve[(tax > -0.8) & (tax < -0.2)]); post = np.median(on_curve[(tax > 0.4) & (tax < 1.2)])
duck['onset_depth_db'] = round(float(post - pre), 1)
out = dict(segments=segs, silence_gaps_s=gaps, novelty_peaks_s=[round(float(b), 1) for b in bt], ducking=duck)
json.dump(out, open('analysis/data/music.json', 'w'), indent=1)
json.dump(all_beats, open('analysis/data/beats.json', 'w'))
for s in segs:
    print({k: v for k, v in s.items() if k != 'beat_frames_first8'})
print('gaps', gaps)
print('ducking', {k: v for k, v in duck.items() if 'curve' not in k and '_t_' not in k})
fig, ax = plt.subplots(2, 1, figsize=(20, 7))
ax[0].plot(np.arange(len(nov))*0.2*30, nov); [ax[0].axvline(b*30, color='r', lw=.8) for b in mb]; ax[0].set_title('music novelty (x = frame), red = cue boundaries')
ax[1].plot(tax, on_curve, label=f'music level locked to voice onset after pause>=0.6s (n={n_on})'); ax[1].plot(tax2, off_curve, label=f'locked to voice offset (n={n_off})'); ax[1].axvline(0, color='k'); ax[1].legend(); ax[1].set_xlabel('s'); ax[1].set_ylabel('dBFS (other+bass)')
plt.tight_layout(); plt.savefig('analysis/plots/music_novelty_ducking.png', dpi=70)
