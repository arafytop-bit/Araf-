"""Audio QA on a mix: clicks (HF spikes in quiet passages), clipping, abrupt music starts/stops at section joints.

  python3 audio_qa.py MIX.wav [MUSIC_STEM.wav]
"""
import json
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf


def main(mix, music=None):
    x, sr = sf.read(mix, dtype='float32', always_2d=True)
    m = x.mean(1)
    out = {}
    out['sample_peak_dbfs'] = round(float(20 * np.log10(np.abs(x).max() + 1e-12)), 2)
    out['clipped_samples'] = int((np.abs(x) >= 0.999).sum())
    # clicks: 4th-order high-pass at 6 kHz, look for isolated spikes far above the local HF floor
    sos = ss.butter(4, 6000 / (sr / 2), 'high', output='sos')
    hf = np.abs(ss.sosfilt(sos, m))
    win = int(0.02 * sr)
    floor = ss.medfilt(hf[::40], 101).repeat(40)[:len(hf)] + 1e-5
    ratio = hf / floor
    cand = np.where(ratio > 60)[0]
    clicks, last = [], -sr
    for i in cand:
        if i - last > sr * 0.05:
            loc = m[max(0, i - win):i + win]
            if np.sqrt((loc ** 2).mean()) < 0.05:          # only audible in quieter passages
                clicks.append(round(i / sr, 3))
            last = i
    out['click_candidates'] = clicks[:50]
    out['click_count'] = len(clicks)
    if music:
        y, _ = sf.read(music, dtype='float32', always_2d=True)
        ym = np.abs(y.mean(1))
        env = np.sqrt(ss.lfilter([0.01], [1, -0.99], ym ** 2))
        # abrupt edges: envelope jumps > 18 dB within 5 ms
        db = 20 * np.log10(env + 1e-6)
        step = int(0.005 * sr)
        jumps = np.where(np.abs(db[step:] - db[:-step]) > 18)[0]
        edges, last = [], -sr
        for i in jumps:
            if i - last > sr * 0.2 and max(db[i], db[i + step]) > -40:
                edges.append(round(i / sr, 2))
                last = i
        out['music_abrupt_edges'] = edges[:40]
    print(json.dumps(out, indent=1))
    return out


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
