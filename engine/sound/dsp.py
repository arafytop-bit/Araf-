"""DSP helpers shared by the score, SFX and mixer (48 kHz, float32, stereo = (n, 2))."""
import functools

import numpy as np
import scipy.signal as ss

SR = 48000


def secs(n):
    return n / SR


def n_of(t):
    return int(round(t * SR))


def rng(seed):
    return np.random.default_rng(seed)


def t_axis(dur):
    return np.arange(n_of(dur)) / SR


# ---------------- filters ----------------
@functools.lru_cache(maxsize=256)
def _sos(kind, f1, f2=None, order=2):
    nyq = SR / 2
    if kind == 'band':
        return ss.butter(order, [max(10, f1) / nyq, min(f2, nyq * 0.98) / nyq], 'band', output='sos')
    return ss.butter(order, min(f1, nyq * 0.98) / nyq, kind, output='sos')


def lp(x, f, order=2):
    return ss.sosfilt(_sos('low', float(f), None, order), x, axis=0)


def hp(x, f, order=2):
    return ss.sosfilt(_sos('high', float(f), None, order), x, axis=0)


def bp(x, f1, f2, order=2):
    return ss.sosfilt(_sos('band', float(f1), float(f2), order), x, axis=0)


def resonator(x, f, q=20.0):
    b, a = ss.iirpeak(f / (SR / 2), q)
    return ss.lfilter(b, a, x, axis=0)


# ---------------- sources ----------------
def white(n, seed=0):
    return rng(seed).standard_normal(n).astype(np.float32)


def pink(n, seed=0):
    w = rng(seed).standard_normal(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return (ss.lfilter(b, a, w) * 4).astype(np.float32)


def brown(n, seed=0):
    w = rng(seed).standard_normal(n)
    y = ss.lfilter([1], [1, -0.995], w)
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)


def chirp_sine(f0, f1, dur, curve='exp', phase=0.0):
    t = t_axis(dur)
    if curve == 'exp':
        f = f0 * (f1 / f0) ** (t / max(dur, 1e-6))
    else:
        f = f0 + (f1 - f0) * (t / max(dur, 1e-6))
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase).astype(np.float32)


def sine_f(freq_curve):
    return np.sin(2 * np.pi * np.cumsum(freq_curve) / SR).astype(np.float32)


def partials(freqs, amps, decays, dur, seed=0):
    """Inharmonic additive tone (bells, metal, glass)."""
    t = t_axis(dur)
    r = rng(seed)
    out = np.zeros_like(t)
    for f, a, d in zip(freqs, amps, decays):
        out += a * np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)) * np.exp(-t / d)
    return out.astype(np.float32)


# ---------------- envelopes ----------------
def exp_env(dur, decay, attack=0.002):
    t = t_axis(dur)
    return (np.minimum(1.0, t / max(attack, 1e-5)) * np.exp(-t / decay)).astype(np.float32)


def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.1):
    n = n_of(dur)
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-5), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-5), s))
    rel = n_of(r)
    if rel and rel < n:
        e[-rel:] *= np.linspace(1, 0, rel)
    return e.astype(np.float32)


def fade(x, fin=0.005, fout=0.02):
    x = np.array(x, dtype=np.float32, copy=True)
    a, b = n_of(fin), n_of(fout)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim > 1 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim > 1 else np.linspace(1, 0, b)
    return x


# ---------------- spatial ----------------
def pan(mono, p=0.0):
    """Equal-power pan, p in [-1, 1]. p may be an array (moving source)."""
    mono = np.asarray(mono, dtype=np.float32)
    p = np.clip(p, -1, 1)
    th = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(th), mono * np.sin(th)], 1).astype(np.float32)


def widen(mono, ms=11.0, amount=0.35, seed=0):
    """Decorrelated stereo from mono (short all-pass smear on one side)."""
    d = n_of(ms / 1000)
    side = np.concatenate([np.zeros(d, np.float32), mono[:-d]]) if d else mono
    side = hp(side, 300)
    return np.stack([mono + amount * side, mono - amount * side], 1).astype(np.float32)


def to_stereo(x):
    x = np.asarray(x, dtype=np.float32)
    return np.stack([x, x], 1) if x.ndim == 1 else x


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return (x * (peak / m)).astype(np.float32) if m > 0 else x


def rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x, dtype=np.float64))) + 1e-12))


def db(g):
    return 10 ** (g / 20)


def saturate(x, drive=2.0):
    return (np.tanh(x * drive) / np.tanh(drive)).astype(np.float32)


# ---------------- reverb (synthetic impulse responses) ----------------
@functools.lru_cache(maxsize=8)
def impulse(kind='hall', seed=3):
    """Stereo IR: early reflections + exponentially decaying noise whose highs die faster."""
    cfg = dict(hall=(2.6, 0.020, 6500), room=(0.55, 0.006, 5000), plate=(1.6, 0.0, 9000),
               outdoor=(1.2, 0.045, 3500), small=(0.25, 0.003, 7000), cathedral=(4.5, 0.03, 4500))[kind]
    rt60, pre, lpf = cfg
    n = n_of(rt60 * 1.1 + pre)
    r = rng(seed)
    t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    decay = np.exp(-6.9 * t / rt60)
    for ch in range(2):
        nz = r.standard_normal(n) * decay
        lo = lp(nz, lpf * 0.35)
        hi = nz - lo
        hi *= np.exp(-6.9 * t / (rt60 * 0.45))   # highs decay faster
        tail = lo + hi
        p0 = n_of(pre)
        tail[:p0] = 0
        for k in range(10):                      # early reflections
            i = p0 + n_of(r.uniform(0.002, 0.06 if kind != 'small' else 0.02))
            if i < n:
                tail[i] += r.uniform(0.3, 0.8) * (1 if r.random() < 0.5 else -1)
        out[:, ch] = tail
    out /= np.sqrt(np.sum(out ** 2) / 2)
    return out


def reverb(x, kind='hall', wet=0.25, dry=1.0):
    x = to_stereo(x)
    ir = impulse(kind)
    w = np.stack([ss.fftconvolve(x[:, c], ir[:, c])[: len(x) + len(ir) - 1] for c in range(2)], 1)
    out = np.zeros_like(w)
    out[: len(x)] += dry * x
    out += wet * w
    return out.astype(np.float32)


def place(dst, src, t, gain=1.0):
    """Add src (stereo) into dst at time t (seconds), clipped to bounds."""
    i = n_of(t)
    if i >= len(dst) or len(src) == 0:
        return
    j0 = max(0, -i)
    i = max(0, i)
    k = min(len(src) - j0, len(dst) - i)
    if k > 0:
        dst[i:i + k] += gain * src[j0:j0 + k]
