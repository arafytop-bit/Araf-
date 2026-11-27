"""Audio measurements, identical for the reference and our renders.

  python3 audio_measure.py VIDEO CUTS_JSON FPS OUT_JSON

- loudness: integrated LUFS, LRA, true peak (ffmpeg ebur128)
- mid/side: the narrator sits in the mid channel; music beds/SFX widen into the side channel
- bed-under-voice: side-channel level vs. mid-channel level in speech (dB)
- silences: stretches below -45 dBFS RMS (>= 150 ms)
- transient SFX candidates: broadband onsets far above the local flux baseline; share landing within 2 frames of a cut
- tempo of the side channel (music bed) from onset-envelope autocorrelation
"""
import json
import re
import subprocess
import sys

import numpy as np
import scipy.signal as ss

SR = 48000


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def ebur(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-map', '0:a', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rindex('Summary:'):]
    g = lambda pat: float(re.search(pat, s).group(1))  # noqa: E731
    return dict(integrated_lufs=g(r'I:\s+(-?[\d.]+) LUFS'), lra_lu=g(r'LRA:\s+(-?[\d.]+) LU'), true_peak_dbtp=g(r'Peak:\s+(-?[\d.]+) dBFS'))


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-9))


def main(path, cuts_json, fps, out):
    x = load(path)
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2
    hop = 480                                   # 10 ms
    n = len(mid) // hop
    m_rms = np.sqrt((mid[:n * hop].reshape(n, hop) ** 2).mean(1))
    s_rms = np.sqrt((side[:n * hop].reshape(n, hop) ** 2).mean(1))
    t_rms = np.sqrt(((mid ** 2 + side ** 2)[:n * hop].reshape(n, hop)).mean(1))
    speech = db(m_rms) > (np.percentile(db(m_rms), 60) - 12)
    res = dict(loudness=ebur(path))
    res['mid_speech_rms_db'] = round(float(db(np.sqrt((m_rms[speech] ** 2).mean()))), 1)
    res['side_rms_db_in_speech'] = round(float(db(np.sqrt((s_rms[speech] ** 2).mean()))), 1)
    res['side_minus_mid_db'] = round(res['side_rms_db_in_speech'] - res['mid_speech_rms_db'], 1)
    res['stereo_correlation'] = round(float(np.corrcoef(x[::50, 0], x[::50, 1])[0, 1]), 3)
    # silences
    sil = db(t_rms) < -45
    runs, start = [], None
    for i, v in enumerate(sil):
        if v and start is None:
            start = i
        if not v and start is not None:
            if i - start >= 15:
                runs.append((start / 100, (i - start) / 100))
            start = None
    res['silences_ge_150ms'] = len(runs)
    res['silence_total_s'] = round(sum(d for _, d in runs), 2)
    res['silences_list'] = [[round(a, 2), round(d, 2)] for a, d in runs[:60]]
    # pauses inside narration (speech gaps 120-600 ms) -> narration tightness
    gaps, start = [], None
    for i, v in enumerate(speech):
        if not v and start is None:
            start = i
        if v and start is not None:
            if 12 <= i - start <= 60:
                gaps.append((i - start) / 100)
            start = None
    res['speech_gaps_120_600ms_per_min'] = round(len(gaps) / (n / 100 / 60), 1)
    res['median_speech_gap_s'] = round(float(np.median(gaps)), 3) if gaps else None
    # transient SFX candidates: broadband spectral flux (2-10 kHz) peaks well above local baseline
    f, t, Z = ss.stft(mid + side * 0.5, SR, nperseg=1024, noverlap=1024 - 480)
    band = (f > 2000) & (f < 10000)
    mag = np.abs(Z[band])
    flux = np.maximum(0, np.diff(np.log1p(mag * 50), axis=1)).sum(0)
    base = ss.medfilt(flux, 101)
    pk, _ = ss.find_peaks(flux, height=base * 4 + np.percentile(flux, 90), distance=20)
    times = t[1:][pk]
    cuts = np.array(json.load(open(cuts_json))['cuts']) / fps
    near = [bool(len(cuts) and np.min(np.abs(cuts - tt)) <= 2 / fps) for tt in times]
    res['sfx_transients'] = int(len(times))
    res['sfx_per_min'] = round(len(times) / (len(mid) / SR / 60), 2)
    res['sfx_on_cuts_pct'] = round(100 * float(np.mean(near)) if len(near) else 0, 1)
    res['cuts_with_sfx_pct'] = round(100 * float(np.mean([np.min(np.abs(times - c)) <= 2 / fps for c in cuts])) if len(times) and len(cuts) else 0, 1)
    res['sfx_times_first_120s'] = [round(float(v), 2) for v in times if v < 120]
    # music-bed tempo from the side channel onset envelope (60-180 BPM)
    env = np.maximum(0, np.diff(s_rms))
    env = env - env.mean()
    ac = np.correlate(env[:60000], env[:60000], 'full')[len(env[:60000]) - 1:]
    lags = np.arange(len(ac)) / 100.0
    sel = (lags > 60 / 180) & (lags < 60 / 60)
    if sel.any() and np.abs(ac[sel]).max() > 0:
        lag = lags[sel][np.argmax(ac[sel])]
        res['bed_tempo_bpm_estimate'] = round(60 / lag, 1)
        res['bed_tempo_confidence'] = round(float(ac[sel].max() / (ac[0] + 1e-12)), 3)
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ('silences_list', 'sfx_times_first_120s')}, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4])
