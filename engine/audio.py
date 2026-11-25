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


def music_bed(duration, bpm=110.0, seed=1):
    """Dark, low-register pulse: sub-bass + soft kick + quiet hats + low-passed minor pad (stereo)."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    L = np.zeros(n); Rr = np.zeros(n)
    beat = 60.0 / bpm
    bar = 4 * beat
    roots = [55.0, 43.65, 65.41, 49.0]                     # A1 F1 C2 G1
    chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [261.6, 329.6, 392.0], [196.0, 246.9, 293.7]]
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
