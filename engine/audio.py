"""Audio: synthesized dark music bed, title-card hit SFX, mixing and loudness
(BLUEPRINT 7: bed ~20-25 dB under the voice; one bright hit on every title card)."""
import numpy as np
import scipy.signal as ss
import soundfile as sf

SR = 48000


def _env(n, a, d, sr=SR):
    t = np.arange(n) / sr
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-t / d)
    return e


def music_bed(duration, bpm=110.0, seed=1, key=0):
    """Dark, low-register pulse: sub-bass + soft kick + quiet hats + low-passed minor pad (stereo)."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    L = np.zeros(n); Rr = np.zeros(n)
    beat = 60.0 / bpm
    bar = 4 * beat
    kk = 2 ** (key / 12.0)
    roots = [r * kk for r in [55.0, 43.65, 65.41, 49.0]]   # A1 F1 C2 G1 (transposed)
    chords = [[n * kk for n in ch] for ch in [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [261.6, 329.6, 392.0], [196.0, 246.9, 293.7]]]
    t_all = np.arange(n) / SR
    nb = int(duration / beat) + 2
    for b in range(nb):
        t0 = b * beat
        i0 = int(t0 * SR)
        if i0 >= n:
            break
        bi = int(t0 / bar) % 4
        # sub bass pluck on every beat
        m = min(n - i0, int(beat * SR))
        tt = np.arange(m) / SR
        f = roots[bi]
        bass = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)) * _env(m, 0.01, 0.35)
        L[i0:i0 + m] += 0.55 * bass; Rr[i0:i0 + m] += 0.55 * bass
        # kick on 1 and 3
        if b % 2 == 0:
            m2 = min(n - i0, int(0.35 * SR)); tt = np.arange(m2) / SR
            fk = 45 + 70 * np.exp(-tt / 0.04)
            kick = np.sin(2 * np.pi * np.cumsum(fk) / SR) * _env(m2, 0.002, 0.12)
            L[i0:i0 + m2] += 0.8 * kick; Rr[i0:i0 + m2] += 0.8 * kick
        # hats on 8ths (stereo-spread)
        for h in range(2):
            j0 = int((t0 + h * beat / 2) * SR)
            if j0 >= n:
                continue
            m3 = min(n - j0, int(0.06 * SR))
            nz = rng.normal(0, 1, m3)
            nz = ss.lfilter(*ss.butter(2, 7000 / (SR / 2), 'high'), nz) * _env(m3, 0.001, 0.018)
            pan = 0.35 if h else -0.35
            L[j0:j0 + m3] += 0.10 * nz * (1 - pan); Rr[j0:j0 + m3] += 0.10 * nz * (1 + pan)
    # pad: detuned saws per bar, low-passed, slow attack
    for k in range(int(duration / bar) + 1):
        i0 = int(k * bar * SR)
        if i0 >= n:
            break
        m = min(n - i0, int(bar * SR))
        tt = np.arange(m) / SR
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.3)
        padL = np.zeros(m); padR = np.zeros(m)
        for fr in chords[k % 4]:
            padL += ss.sawtooth(2 * np.pi * fr * 0.997 * tt)
            padR += ss.sawtooth(2 * np.pi * fr * 1.003 * tt)
        bl, al = ss.butter(2, 700 / (SR / 2))
        L[i0:i0 + m] += 0.07 * ss.lfilter(bl, al, padL) * env
        Rr[i0:i0 + m] += 0.07 * ss.lfilter(bl, al, padR) * env
    st = np.stack([L, Rr], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.5


def hit_sfx(seed=4):
    """Bright cinematic hit: transient + band noise (centroid ~4-5 kHz) + metallic ring + low thump, ~1 s tail."""
    rng = np.random.default_rng(seed)
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    nz = rng.normal(0, 1, n)
    bright = ss.lfilter(*ss.butter(2, [2500 / (SR / 2), 9000 / (SR / 2)], 'band'), nz) * np.exp(-t / 0.22)
    click = ss.lfilter(*ss.butter(2, 4000 / (SR / 2), 'high'), nz) * np.exp(-t / 0.004)
    ring = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in
               [(1230, 0.25, 0.35), (2890, 0.30, 0.30), (4710, 0.28, 0.25), (6350, 0.15, 0.18)])
    fth = 50 + 60 * np.exp(-t / 0.05)
    thump = np.sin(2 * np.pi * np.cumsum(fth) / SR) * np.exp(-t / 0.18)
    tail = ss.lfilter(*ss.butter(2, [1500 / (SR / 2), 7000 / (SR / 2)], 'band'), rng.normal(0, 1, n)) * np.exp(-t / 0.45) * 0.25
    mono = 0.9 * bright + 0.6 * click + ring + 0.8 * thump + tail
    # slight stereo width (decorrelated tails) - the source SFX lives in the side channel too
    side = ss.lfilter(*ss.butter(2, [2000 / (SR / 2), 8000 / (SR / 2)], 'band'), rng.normal(0, 1, n)) * np.exp(-t / 0.3) * 0.35
    st = np.stack([mono + side, mono - side], 1)
    return st / np.abs(st).max()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


def mix(voice_path, duration, voice_offset, hits, bed_under_db=22.0, out_path='mix.wav', fade_out=0.35):
    v, vsr = sf.read(voice_path)
    if v.ndim > 1:
        v = v.mean(1)
    v = ss.resample_poly(v, SR, vsr) if vsr != SR else v
    n = int(duration * SR)
    voice = np.zeros(n)
    i0 = int(voice_offset * SR)
    m = min(len(v), n - i0)
    voice[i0:i0 + m] = v[:m]
    speech = voice[np.abs(voice) > 1e-4]
    v_db = rms_db(speech) if len(speech) else -20
    bed = music_bed(duration)
    bed *= 10 ** ((v_db - bed_under_db - rms_db(bed)) / 20)
    out = bed + voice[:, None]
    h = hit_sfx()
    for t in hits:
        j = int(t * SR)
        k = min(len(h), n - j)
        out[j:j + k] += h[:k] * 10 ** ((v_db + 4 - rms_db(h[:int(0.25 * SR)])) / 20)
    fo = int(fade_out * SR)
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    out /= max(1.0, np.abs(out).max() / 0.95)
    sf.write(out_path, out.astype(np.float32), SR)
    return out_path


def pop_sfx():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 900 + 1400 * np.exp(-t / 0.02)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)
    return np.stack([x, x], 1) / np.abs(x).max()


def thud_sfx(seed=2):
    rng = np.random.default_rng(seed)
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 55 + 90 * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    x += ss.lfilter(*ss.butter(2, 3000 / (SR / 2)), rng.normal(0, 1, n)) * np.exp(-t / 0.02) * 0.6
    return np.stack([x, x], 1) / np.abs(x).max()


def drum_sfx(seed=3):
    rng = np.random.default_rng(seed)
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 70 + 60 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    x += ss.lfilter(*ss.butter(2, [200 / (SR / 2), 1200 / (SR / 2)], 'band'), rng.normal(0, 1, n)) * np.exp(-t / 0.05) * 0.5
    return np.stack([x, x], 1) / np.abs(x).max()


def whoosh_sfx(seed=6):
    rng = np.random.default_rng(seed)
    n = int(0.45 * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * t / t[-1]) ** 2
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    for k in range(0, n, 1024):
        fc = 600 + 3500 * (k / n)
        b, a = ss.butter(2, [fc / (SR / 2), min(0.99, fc * 1.8 / (SR / 2))], 'band')
        out[k:k + 1024] = ss.lfilter(b, a, x[k:k + 1024])
    out *= env
    return np.stack([out, out * 0.8], 1) / np.abs(out).max()


def sting_sfx(duration=6.5, bpm=108.0, key=0, seed=9):
    """Outro sting (BLUEPRINT 7): punchy ~108 BPM beat - four-on-the-floor kick, claps on 2/4, driving bass,
    bright chord stabs - 6.5 s, ending in a 0.5 s fade."""
    rng = np.random.default_rng(seed)
    n = int((duration + 0.5) * SR)
    L = np.zeros(n); Rr = np.zeros(n)
    beat = 60.0 / bpm
    kk = 2 ** (key / 12.0)
    roots = [r * kk for r in [55.0, 43.65, 65.41, 49.0]]
    stabs = [[n_ * kk for n_ in ch] for ch in [[440.0, 523.3, 659.3], [349.2, 440.0, 523.3], [523.3, 659.3, 784.0], [392.0, 493.9, 587.3]]]
    nb = int(duration / beat) + 1
    for b in range(nb):
        i0 = int(b * beat * SR)
        bar = (b // 4) % 4
        m = min(n - i0, int(0.4 * SR)); tt = np.arange(m) / SR
        fk = 48 + 110 * np.exp(-tt / 0.035)
        kick = np.sin(2 * np.pi * np.cumsum(fk) / SR) * _env(m, 0.001, 0.14)
        L[i0:i0 + m] += kick; Rr[i0:i0 + m] += kick
        if b % 2 == 1:   # clap
            m2 = min(n - i0, int(0.25 * SR)); tt = np.arange(m2) / SR
            nz = ss.lfilter(*ss.butter(2, [900 / (SR / 2), 6000 / (SR / 2)], 'band'), rng.normal(0, 1, m2))
            env = sum(np.exp(-np.maximum(0, tt - d) / 0.012) * (tt >= d) for d in (0, 0.011, 0.022)) * 0.5 + np.exp(-tt / 0.09) * 0.6
            L[i0:i0 + m2] += 0.55 * nz * env; Rr[i0:i0 + m2] += 0.55 * nz * env
        for h in range(2):   # 8th bass + hats
            j0 = int((b * beat + h * beat / 2) * SR)
            if j0 >= n:
                continue
            m3 = min(n - j0, int(beat / 2 * SR)); tt = np.arange(m3) / SR
            f = roots[bar] * (2 if h else 1)
            bass = ss.sawtooth(2 * np.pi * f * tt) * _env(m3, 0.003, 0.12)
            bass = ss.lfilter(*ss.butter(2, 900 / (SR / 2)), bass)
            L[j0:j0 + m3] += 0.45 * bass; Rr[j0:j0 + m3] += 0.45 * bass
            m4 = min(n - j0, int(0.05 * SR))
            hz = ss.lfilter(*ss.butter(2, 8000 / (SR / 2), 'high'), rng.normal(0, 1, m4)) * _env(m4, 0.001, 0.015)
            L[j0:j0 + m4] += 0.18 * hz * (1.3 if h else 0.7); Rr[j0:j0 + m4] += 0.18 * hz * (0.7 if h else 1.3)
        if b % 4 in (0, 3):  # chord stab
            m5 = min(n - i0, int(0.32 * SR)); tt = np.arange(m5) / SR
            stL = sum(ss.square(2 * np.pi * fr_ * 0.996 * tt, 0.3) for fr_ in stabs[bar])
            stR = sum(ss.square(2 * np.pi * fr_ * 1.004 * tt, 0.3) for fr_ in stabs[bar])
            bl, al = ss.butter(2, 3200 / (SR / 2))
            e5 = _env(m5, 0.004, 0.13)
            L[i0:i0 + m5] += 0.12 * ss.lfilter(bl, al, stL) * e5; Rr[i0:i0 + m5] += 0.12 * ss.lfilter(bl, al, stR) * e5
    st = np.stack([L, Rr], 1)
    t = np.arange(n) / SR
    st *= np.clip((duration + 0.5 - t) / 0.5, 0, 1)[:, None]
    return st / (np.abs(st).max() + 1e-9)


def mix_long(voice_path, duration, voice_offset, sections, events, out_path, bed_under_db=22.0):
    """Long-form mix.
    sections: [(t0, t1, cfg)] music beds, cfg = dict(bpm, key, seed, under=extra dB under the voice)
    events:   dicts with t (s), kind in hit/pop/thud/drum/whoosh/sting/dropout, gain (dB vs. voice RMS), dur (dropout)."""
    v, vsr = sf.read(voice_path)
    if v.ndim > 1:
        v = v.mean(1)
    v = ss.resample_poly(v, SR, vsr) if vsr != SR else v
    n = int(duration * SR)
    voice = np.zeros(n)
    i0 = int(voice_offset * SR)
    m = min(len(v), n - i0)
    voice[i0:i0 + m] = v[:m]
    speech = voice[np.abs(voice) > 1e-4]
    v_db = rms_db(speech)
    bed = np.zeros((n, 2))
    xf = int(0.6 * SR)
    for t0, t1, cfg in sections:
        a, z = int(t0 * SR), min(n, int(t1 * SR) + xf)
        seg = music_bed((z - a) / SR + 0.1, bpm=cfg.get('bpm', 110), seed=cfg.get('seed', 1), key=cfg.get('key', 0))[:z - a]
        seg *= 10 ** ((v_db - bed_under_db - cfg.get('under', 0) - rms_db(seg)) / 20)
        fade = np.ones(len(seg))
        k = min(xf, len(seg) // 2)
        fade[:k] = np.linspace(0, 1, k)
        fade[-k:] = np.minimum(fade[-k:], np.linspace(1, 0, k))
        bed[a:a + len(seg)] += seg * fade[:, None]
    gate = np.ones(n)
    for e in events:
        if e['kind'] == 'dropout':                    # music drops out completely (e.g. before the last title card)
            a = int(e['t'] * SR); z = min(n, int((e['t'] + e['dur']) * SR)); r = int(0.03 * SR)
            gate[a:z] = 0
            gate[max(0, a - r):a] = np.minimum(gate[max(0, a - r):a], np.linspace(1, 0, a - max(0, a - r)))
    out = bed * gate[:, None] + voice[:, None]
    sfx = dict(hit=hit_sfx(), pop=pop_sfx(), thud=thud_sfx(), drum=drum_sfx(), whoosh=whoosh_sfx())
    for e in events:
        if e['kind'] == 'dropout':
            continue
        h = sting_sfx(bpm=e.get('bpm', 108)) if e['kind'] == 'sting' else sfx[e['kind']]
        j = int(e['t'] * SR); k = min(len(h), n - j)
        if k <= 0:
            continue
        ref = rms_db(h[:int(1.0 * SR)]) if e['kind'] == 'sting' else rms_db(h[:int(0.15 * SR)])
        out[j:j + k] += h[:k] * 10 ** ((v_db + e.get('gain', 0) - ref) / 20)
    fo = int(0.25 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    out /= max(1.0, np.abs(out).max() / 0.97)
    sf.write(out_path, out.astype(np.float32), SR, subtype='FLOAT')
    return out_path


def loudnorm(in_path, out_path, I=-14.0, TP=-1.5):
    """Measure integrated loudness (EBU R128), apply static gain to hit the target, then a brick-wall limiter
    (4x oversampled) so hits and the outro sting stay under the true-peak ceiling. Keeps the mix's dynamics."""
    import re as _re
    import subprocess

    def measure(path):
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                           capture_output=True, text=True).stderr
        summ = r[r.rindex('Summary:'):]
        i_ = float(_re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1))
        tp = float(_re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1))
        return i_, tp
    i0, tp0 = measure(in_path)
    gain = I - i0
    lim = 10 ** ((TP - 0.5) / 20)
    af = (f'volume={gain:.2f}dB,aresample=192000,alimiter=limit={lim:.4f}:attack=3:release=80:level=disabled,'
          f'aresample=48000')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', in_path, '-af', af, '-c:a', 'pcm_s24le', out_path],
                   check=True)
    i1, tp1 = measure(out_path)
    return dict(input_i=i0, input_tp=tp0, gain=gain, output_i=i1, output_tp=tp1)
