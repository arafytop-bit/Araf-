"""Per-frame audio features for the mix and each Demucs stem on the video clock.

hop = 44100/30 = 1470 samples, so audio index N <-> video frame N (both streams start at pts 0).
Outputs analysis/data/audio_frames.csv and analysis/data/audio_summary.json
"""
import json, numpy as np, soundfile as sf, librosa, pyloudnorm as pyln, subprocess, re

SR = 44100; HOP = 1470; NFR = 16731
names = ['mix', 'vocals', 'drums', 'bass', 'other']
paths = {'mix': 'work/ref/audio_44k.wav', **{n: f'work/stems/{n}.wav' for n in names[1:]}}
st = {}
for n in names:
    x, sr = sf.read(paths[n], dtype='float32', always_2d=True); assert sr == SR
    st[n] = x
st['music'] = st['drums'] + st['bass'] + st['other']
names.append('music')

def frame_rms_db(mono):
    # RMS over the 1470-sample block that starts at N*1470 (block N covers [N/30, (N+1)/30) s)
    n = NFR
    pad = np.zeros(n*HOP, np.float32); m = min(len(mono), n*HOP); pad[:m] = mono[:m]
    blk = pad.reshape(n, HOP)
    rms = np.sqrt((blk**2).mean(1) + 1e-12)
    return 20*np.log10(rms + 1e-9)

meter = pyln.Meter(SR)
summary = {'sample_rate': SR, 'hop': HOP, 'stems': {}}
cols = {}
for n in names:
    x = st[n]; mono = x.mean(1)
    cols[f'{n}_rms_db'] = frame_rms_db(mono)
    lufs = meter.integrated_loudness(x.astype(np.float64))
    peak = float(np.abs(x).max())
    rms_all = float(np.sqrt((mono**2).mean()))
    mid = (x[:, 0]+x[:, 1])/2; side = (x[:, 0]-x[:, 1])/2
    width = float(np.sqrt((side**2).mean())/(np.sqrt((mid**2).mean())+1e-12))
    corr = float(np.corrcoef(x[:, 0], x[:, 1])[0, 1])
    summary['stems'][n] = dict(integrated_lufs=round(lufs, 2), sample_peak_dbfs=round(20*np.log10(peak+1e-12), 2),
                               crest_factor_db=round(20*np.log10(peak/(rms_all+1e-12)), 2),
                               side_to_mid_rms_ratio=round(width, 4), lr_correlation=round(corr, 4))
    print(n, summary['stems'][n], flush=True)

# spectral features per frame for vocals / other / drums (mono, 44.1k, n_fft 2048, hop 1470, centred on block centre)
for n in ['vocals', 'other', 'drums', 'music']:
    mono = st[n].mean(1)
    S = np.abs(librosa.stft(mono, n_fft=4096, hop_length=HOP, center=True))[:, :NFR]
    S = np.pad(S, ((0, 0), (0, max(0, NFR - S.shape[1]))))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=4096)
    cen = (S*freqs[:, None]).sum(0)/(S.sum(0)+1e-9)
    cols[f'{n}_centroid_hz'] = cen
    flux = np.r_[0, np.maximum(0, np.diff(np.log1p(S), axis=1)).sum(0)]
    cols[f'{n}_flux'] = flux
    # band energies (dB): sub <60, low 60-250, mid 250-2k, high 2k-8k, air >8k
    for b, (lo, hi) in dict(sub=(20, 60), low=(60, 250), mid=(250, 2000), high=(2000, 8000), air=(8000, 20000)).items():
        idx = (freqs >= lo) & (freqs < hi)
        cols[f'{n}_{b}_db'] = 10*np.log10((S[idx]**2).sum(0)+1e-12)

# per-stem LRA / true peak with ffmpeg ebur128
for n in ['mix', 'vocals', 'drums', 'bass', 'other']:
    out = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-i', paths[n], '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    tail = out[out.rfind('Summary'):]
    lra = re.search(r'LRA:\s+([-\d.]+)', tail); tp = re.search(r'Peak:\s+([-\d.]+)', tail); I = re.search(r'I:\s+([-\d.]+)', tail)
    summary['stems'][n].update(ffmpeg_I=float(I.group(1)), LRA_LU=float(lra.group(1)), true_peak_dbfs=float(tp.group(1)))

import csv
with open('analysis/data/audio_frames.csv', 'w', newline='') as f:
    w = csv.writer(f); keys = list(cols.keys()); w.writerow(['frame'] + keys)
    for i in range(NFR):
        w.writerow([i] + [round(float(cols[k][i]), 3) for k in keys])
json.dump(summary, open('analysis/data/audio_summary.json', 'w'), indent=1)
print('DONE')
