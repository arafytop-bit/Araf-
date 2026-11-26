"""Procedural SFX library (all synthesized here, so they are original and royalty-free).

Every generator returns stereo float32 (n, 2) at 48 kHz, peak-normalised to 0.9; the mixer sets levels.
`get(name, seed, **kw)` caches results.
"""
import functools

import numpy as np
import scipy.signal as ss

from .dsp import (SR, n_of, t_axis, white, pink, brown, chirp_sine, partials, pan, widen, to_stereo, norm, lp, hp,
                  bp, resonator, reverb, saturate, fade, rng)


def fit(x, n):
    """Trim or zero-pad (n, 2) audio to n samples (reverb tails make outputs longer than their inputs)."""
    if len(x) >= n:
        return x[:n]
    pad = np.zeros((n - len(x),) + x.shape[1:], np.float32)
    return np.concatenate([x, pad])


def _env_ar(n, peak_frac=0.5, a_pow=2.0, r_pow=1.2):
    u = np.linspace(0, 1, n)
    pk = max(1e-3, peak_frac)
    return np.where(u < pk, (u / pk) ** a_pow, ((1 - u) / (1 - pk)) ** r_pow).astype(np.float32)


def _moving_band(x, fc, bw_frac=0.8, env=None, nper=1024):
    """Filter noise with a time-varying Gaussian band (STFT domain). fc: array over STFT frames or callable(u)."""
    f, t, Z = ss.stft(x, SR, nperseg=nper, noverlap=nper * 3 // 4)
    u = np.linspace(0, 1, len(t))
    c = fc(u) if callable(fc) else np.interp(u, np.linspace(0, 1, len(fc)), fc)
    G = np.exp(-0.5 * ((f[:, None] - c[None, :]) / (bw_frac * c[None, :] + 30)) ** 2)
    if env is not None:
        G = G * (env(u) if callable(env) else np.interp(u, np.linspace(0, 1, len(env)), env))[None, :]
    _, y = ss.istft(Z * G, SR, nperseg=nper, noverlap=nper * 3 // 4)
    return y[:len(x)].astype(np.float32)


# ============================================================ movement
def whoosh(dur=0.5, lo=260, hi=3600, seed=0, direction=1, width=0.8, peak=0.6):
    n = n_of(dur)
    x = white(n, seed)

    def fc(u):
        return np.where(u < peak, lo * (hi / lo) ** (u / peak), hi * ((lo * 1.8) / hi) ** ((u - peak) / (1 - peak)))
    y = _moving_band(x, fc, 0.7, env=lambda u: np.where(u < peak, (u / peak) ** 2.2, ((1 - u) / (1 - peak)) ** 1.4))
    y += 0.25 * lp(brown(n, seed + 1), 180) * _env_ar(n, peak, 2, 1.5)
    p = direction * np.linspace(-width, width, n)
    return norm(pan(y, p))


def swish(seed=0, direction=1):
    return whoosh(0.22, 900, 6000, seed, direction, 0.5, 0.55)


def riser(dur=1.6, seed=0):
    n = n_of(dur)
    u = np.linspace(0, 1, n)
    x = _moving_band(white(n, seed), lambda v: 250 * (7000 / 250) ** (v ** 1.4), 0.5)
    tone = chirp_sine(110, 880, dur) * 0.35 + chirp_sine(165, 1320, dur) * 0.2
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(4 + 14 * u ** 2) / SR)
    y = (x + tone) * (u ** 2.2) * trem
    y[-n_of(0.01):] *= np.linspace(1, 0, n_of(0.01))
    return norm(widen(y, 9, 0.5, seed))


def reverse_cymbal(dur=1.3, seed=0):
    n = n_of(dur)
    u = np.linspace(0, 1, n)
    x = hp(white(n, seed), 2500) + 0.4 * bp(white(n, seed + 3), 5000, 11000)
    y = x * np.exp(-(1 - u) * 5.5) * u ** 0.5
    y[-n_of(0.008):] *= np.linspace(1, 0, n_of(0.008))
    return norm(widen(y, 13, 0.7, seed))


def sub_drop(dur=1.6):
    t = t_axis(dur)
    y = chirp_sine(72, 24, dur) * np.exp(-t / (dur * 0.42)) * (1 - np.exp(-t / 0.004))
    return norm(to_stereo(saturate(y, 1.6)))


# ============================================================ UI / graphic sounds
def pop(f0=700, seed=0):
    d = 0.11
    t = t_axis(d)
    f = f0 * (1 + 0.85 * (1 - np.exp(-t / 0.010)))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.028) * (1 - np.exp(-t / 0.0012))
    y += 0.35 * hp(white(len(t), seed), 2000) * np.exp(-t / 0.0013)
    return norm(to_stereo(y))


def click(seed=0, f=3800):
    d = 0.04
    t = t_axis(d)
    y = hp(white(len(t), seed), 1500) * np.exp(-t / 0.0011) + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006)
    return norm(to_stereo(y))


def bell(f=2093.0, dur=1.2, bright=1.0, seed=0):
    ratios = [1, 2.0, 2.76, 4.07, 5.43, 6.8]
    amps = [1, 0.45 * bright, 0.5 * bright, 0.25 * bright, 0.18 * bright, 0.1 * bright]
    dec = [dur * 0.55, dur * 0.35, dur * 0.3, dur * 0.18, dur * 0.12, dur * 0.08]
    y = partials([f * r for r in ratios], amps, dec, dur, seed)
    t = t_axis(dur)
    y += 0.3 * hp(white(len(t), seed), 3000) * np.exp(-t / 0.002)
    return norm(widen(y, 7, 0.25, seed))


def ding(seed=0):
    a = bell(1975.5, 1.1, 0.8, seed)
    b = bell(2637.0, 1.0, 0.7, seed + 1)
    out = np.zeros((len(a) + n_of(0.09), 2), np.float32)
    out[:len(a)] += a * 0.8
    out[n_of(0.09):n_of(0.09) + len(b)] += b
    return norm(out)


def notify(seed=0):
    return ding(seed)


def buzzer(dur=0.42):
    t = t_axis(dur)
    y = ss.sawtooth(2 * np.pi * 98 * t) + 0.6 * ss.sawtooth(2 * np.pi * 147 * t)
    y *= 0.65 + 0.35 * np.sign(np.sin(2 * np.pi * 31 * t))
    y = lp(y, 2600) * np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.03)
    return norm(to_stereo(y.astype(np.float32)))


def marker(dur=0.38, seed=0):
    n = n_of(dur)
    t = t_axis(dur)
    x = bp(white(n, seed), 1800, 6000)
    jit = lp(rng(seed).standard_normal(n), 45)
    jit = 0.55 + 0.45 * np.tanh(jit * 8)
    sq = resonator(white(n, seed + 1), 2600 + 300 * np.sin(2 * np.pi * 3 * t[0]), 35) * 0.5
    y = (x + sq) * jit * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.04)
    return norm(pan(y, np.linspace(-0.3, 0.3, n)))


def text_hit(seed=0, weight=1.0):
    d = 0.35
    t = t_axis(d)
    thump = chirp_sine(150, 46, d) * np.exp(-t / (0.05 * weight))
    snap = hp(white(len(t), seed), 2500) * np.exp(-t / 0.004) * 0.55
    air = lp(white(len(t), seed + 1), 6000) * np.exp(-t / 0.05) * 0.18
    y = saturate(thump + snap + air, 1.5)
    return norm(reverb(y, 'small', 0.12))


def impact(seed=0, size=1.0):
    d = 1.6
    t = t_axis(d)
    sub = chirp_sine(95, 32, d) * np.exp(-t / (0.28 * size))
    body = lp(white(len(t), seed), 900) * np.exp(-t / 0.08) * 0.8
    crack = hp(white(len(t), seed + 1), 3000) * np.exp(-t / 0.006) * 0.6
    y = saturate(sub + body + crack, 2.0)
    return norm(reverb(y, 'hall', 0.22))


def thud(seed=0, size=1.0):
    d = 0.6
    t = t_axis(d)
    y = chirp_sine(115, 42, d) * np.exp(-t / (0.09 * size))
    y += lp(white(len(t), seed), 500) * np.exp(-t / 0.05) * 0.7
    y += bp(white(len(t), seed + 1), 900, 4000) * np.exp(-t / 0.22) * 0.12
    return norm(reverb(saturate(y, 1.3), 'room', 0.12))


# ============================================================ objects / foley
def coins(seed=0, n_clinks=12, dur=0.6):
    r = rng(seed)
    out = np.zeros(n_of(dur + 0.3), np.float32)
    for k in range(n_clinks):
        f = r.uniform(2400, 4800)
        c = partials([f, f * 2.32, f * 3.91, f * 5.4], [1, .5, .35, .2], [0.12, 0.08, 0.05, 0.03], 0.3, seed + k)
        c *= r.uniform(0.3, 1.0)
        i = n_of(r.uniform(0, dur) ** 1.3 / dur ** 0.3)
        out[i:i + len(c)] += c[:len(out) - i]
    return norm(widen(hp(out, 1200), 8, 0.6, seed))


def cha_ching(seed=0):
    drawer = bp(white(n_of(0.25), seed), 300, 2200) * _env_ar(n_of(0.25), 0.2, 1, 2)
    d1 = bell(1568, 0.9, 0.9, seed)[:, 0]
    d2 = bell(2093, 1.2, 0.9, seed + 1)[:, 0]
    out = np.zeros(n_of(1.6), np.float32)
    out[:len(drawer)] += drawer * 0.5
    out[n_of(0.12):n_of(0.12) + len(d1)] += d1 * 0.8
    out[n_of(0.24):n_of(0.24) + len(d2)] += d2
    c = coins(seed + 2, 10, 0.5)[:, 0]
    out[n_of(0.15):n_of(0.15) + len(c)] += c[:len(out) - n_of(0.15)] * 0.5
    return norm(widen(out, 6, 0.4, seed))


def sparkle(seed=0, dur=0.8):
    r = rng(seed)
    out = np.zeros(n_of(dur + 0.5), np.float32)
    for k in range(10):
        f = 3000 * 2 ** (k / 10 * 1.4) * r.uniform(0.97, 1.03)
        c = partials([f, f * 2.4], [1, .3], [r.uniform(.15, .4), .08], 0.5, seed + k)
        i = n_of(k / 10 * dur)
        out[i:i + len(c)] += c * r.uniform(0.4, 1.0)
    sh = hp(white(len(out), seed), 8000) * _env_ar(len(out), 0.3, 1.5, 2) * 0.25
    return norm(widen(out + sh, 10, 0.8, seed))


def sword_shing(seed=0):
    d = 0.9
    n = n_of(d)
    scrape = _moving_band(white(n, seed), lambda u: 2000 * (9000 / 2000) ** np.minimum(1, u * 2.2), 0.25,
                          env=lambda u: np.where(u < 0.4, (u / 0.4) ** 1.5, np.exp(-(u - 0.4) * 9)))
    ring = partials([1720, 4260, 6110, 8930], [1, .7, .5, .3], [.5, .35, .25, .15], d, seed)
    ring[:n_of(0.3)] *= np.linspace(0, 1, n_of(0.3))
    return norm(pan(scrape * 0.8 + ring * 0.5, np.linspace(-0.4, 0.4, n)))


def sword_clash(seed=0):
    r = rng(seed)
    d = 1.0
    out = np.zeros(n_of(d), np.float32)
    for k, dt in enumerate((0.0, 0.085)):
        f0 = r.uniform(850, 1100)
        rs = [1, 2.31, 3.68, 5.12, 7.34, 9.1]
        c = partials([f0 * x * r.uniform(0.98, 1.02) for x in rs], [1, .8, .6, .45, .3, .2], [.5, .4, .3, .22, .15, .1], d, seed + k)
        c += hp(white(n_of(d), seed + k), 2000) * np.exp(-t_axis(d) / 0.004) * 1.2
        i = n_of(dt)
        out[i:] += c[:len(out) - i] * (1.0 if k == 0 else 0.7)
    return norm(reverb(widen(out, 5, 0.5, seed), 'outdoor', 0.2))


def arrow(seed=0, direction=-1):
    d = 0.42
    n = n_of(d)
    x = _moving_band(white(n, seed), lambda u: 1500 - 500 * u, 0.12, env=lambda u: np.sin(np.pi * u) ** 1.5)
    tone = chirp_sine(2300, 1500, d) * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * 0.15
    return norm(pan(x + tone, direction * np.linspace(-0.8, 0.8, n)))


def thunk(seed=0):
    d = 0.35
    t = t_axis(d)
    y = chirp_sine(210, 120, d) * np.exp(-t / 0.04)
    y += bp(white(len(t), seed), 300, 1000) * np.exp(-t / 0.03) * 0.8
    y += hp(white(len(t), seed + 1), 3000) * np.exp(-t / 0.002) * 0.5
    return norm(reverb(to_stereo(y), 'small', 0.1))


def arrow_hit(seed=0):
    a = arrow(seed)
    b = thunk(seed + 1)
    out = np.zeros((len(a) + len(b), 2), np.float32)
    out[:len(a)] += a * 0.8
    out[n_of(0.36):n_of(0.36) + len(b)] += b
    return norm(out)


def fire_bed(dur=6.0, seed=0, intensity=1.0):
    n = n_of(dur)
    r = rng(seed)
    out = np.zeros(n, np.float32)
    k = int(18 * dur * intensity)
    for i in r.integers(0, n - 400, k):
        L = int(r.uniform(40, 220))
        g = np.exp(r.normal(-1.2, 0.8))
        burst = bp(white(L, int(i)), 1500, 7500) * np.exp(-np.arange(L) / (L * 0.25))
        out[i:i + L] += burst * g
    roar = lp(brown(n, seed), 380) * (0.6 + 0.4 * lp(r.standard_normal(n), 1.5) * 8)
    hiss = bp(white(n, seed + 2), 2000, 6000) * 0.05
    y = out * 0.5 + roar * 0.5 * intensity + hiss
    return norm(widen(y.astype(np.float32), 12, 0.7, seed))


def fire_whoosh(seed=0):
    d = 1.4
    n = n_of(d)
    sw = _moving_band(brown(n, seed) * 3 + white(n, seed) * 0.3, lambda u: 200 * (2500 / 200) ** np.minimum(1, u * 1.6), 0.9,
                      env=lambda u: np.where(u < 0.35, (u / 0.35) ** 1.5, np.exp(-(u - 0.35) * 3)))
    bed = fire_bed(d, seed + 1)[:, 0] * np.linspace(0.2, 1, n)
    return norm(widen(sw + 0.5 * bed, 10, 0.6, seed))


def door_crash(seed=0):
    r = rng(seed)
    d = 1.3
    out = np.zeros(n_of(d), np.float32)
    for k in range(7):
        L = n_of(r.uniform(0.008, 0.02))
        b = bp(white(L, seed + k), 700, 3600) * np.exp(-np.arange(L) / (L * 0.3))
        i = n_of(r.uniform(0, 0.12))
        out[i:i + L] += b * r.uniform(0.5, 1.0)
    t = t_axis(d)
    out += chirp_sine(125, 48, d) * np.exp(-t / 0.12) * 0.9
    for k in range(25):
        i = n_of(0.08 + r.uniform(0, 0.7) ** 1.5)
        L = n_of(r.uniform(0.003, 0.01))
        if i + L < len(out):
            out[i:i + L] += lp(white(L, seed + 50 + k), 3500) * r.uniform(0.05, 0.3)
    return norm(reverb(widen(saturate(out, 1.4), 8, 0.5, seed), 'room', 0.25))


def metal_clang(seed=0, f0=240.0, dur=2.2):
    r = rng(seed)
    fs = [f0 * x for x in (1, 1.58, 2.21, 2.97, 3.64, 4.53, 5.71, 6.92, 8.3, 9.9)]
    y = partials([f * r.uniform(0.99, 1.01) for f in fs], [1, .8, .7, .6, .5, .4, .3, .25, .2, .15],
                 [dur * .6, dur * .5, dur * .4, dur * .35, dur * .3, dur * .2, dur * .15, dur * .1, .1, .08], dur, seed)
    y += hp(white(len(y), seed), 1500) * np.exp(-t_axis(dur) / 0.005)
    y += chirp_sine(90, 50, dur) * np.exp(-t_axis(dur) / 0.08) * 0.6
    return norm(reverb(widen(y, 9, 0.6, seed), 'room', 0.25))


def chain_rattle(seed=0, dur=0.8):
    r = rng(seed)
    out = np.zeros(n_of(dur + 0.2), np.float32)
    for k in range(45):
        f = r.uniform(2800, 7000)
        c = partials([f, f * 1.9], [1, .4], [r.uniform(.015, .04), .01], 0.08, seed + k)
        i = n_of(r.uniform(0, dur))
        out[i:i + len(c)] += c * r.uniform(0.2, 1.0)
    return norm(widen(out, 6, 0.8, seed))


def splash(seed=0, size=1.0):
    d = 1.1 * size
    n = n_of(d)
    x = _moving_band(white(n, seed), lambda u: 5500 * (700 / 5500) ** u, 0.9,
                     env=lambda u: np.where(u < 0.04, u / 0.04, np.exp(-(u - 0.04) * 4.5)))
    r = rng(seed)
    out = x.copy()
    for k in range(14):
        L = n_of(r.uniform(0.02, 0.05))
        b = chirp_sine(r.uniform(280, 500), r.uniform(800, 1400), L / SR) * np.exp(-np.arange(L) / (L * 0.4))
        i = n_of(0.05 + r.uniform(0, d * 0.7))
        if i + L < n:
            out[i:i + L] += b * r.uniform(0.05, 0.25)
    out += lp(brown(n, seed), 200) * np.exp(-t_axis(d) / 0.1) * 0.6
    return norm(widen(out, 10, 0.6, seed))


def wood_crack(seed=0):
    r = rng(seed)
    d = 1.6
    n = n_of(d)
    t = t_axis(d)
    jit = 0.5 + 0.5 * np.tanh(lp(r.standard_normal(n), 25) * 10)
    creak = bp(white(n, seed), 250, 900) * jit * np.minimum(1, t / 0.5) * (t < 0.6)
    crack = np.zeros(n, np.float32)
    for k in range(9):
        L = n_of(r.uniform(0.01, 0.03))
        i = n_of(0.6 + r.uniform(0, 0.15))
        crack[i:i + L] += bp(white(L, seed + k), 500, 4000) * np.exp(-np.arange(L) / (L * 0.3)) * r.uniform(0.5, 1)
    boom = chirp_sine(100, 40, d) * np.exp(-np.maximum(0, t - 0.6) / 0.15) * (t > 0.6) * 0.8
    return norm(reverb(widen(creak * 0.5 + crack + boom, 9, 0.5, seed), 'outdoor', 0.2))


def ship_crash(seed=0):
    a = wood_crack(seed)
    b = splash(seed + 1, 1.2)
    out = np.zeros((max(len(a), n_of(0.7) + len(b)), 2), np.float32)
    out[:len(a)] += a
    out[n_of(0.7):n_of(0.7) + len(b)] += b * 0.7
    return norm(out)


def cannon(seed=0):
    d = 3.0
    t = t_axis(d)
    sub = chirp_sine(68, 27, d) * np.exp(-t / 0.45)
    blast = lp(white(len(t), seed), 1800) * np.exp(-t / 0.12) * 1.2
    crack = hp(white(len(t), seed + 1), 3500) * np.exp(-t / 0.004)
    rumble = lp(brown(len(t), seed + 2), 220) * np.exp(-t / 1.4) * 0.7
    y = saturate(sub + blast + crack + rumble, 2.2)
    return norm(reverb(widen(y, 11, 0.4, seed), 'outdoor', 0.45))


def gunshot(seed=0):
    d = 2.2
    t = t_axis(d)
    crack = hp(white(len(t), seed), 1500) * (np.exp(-t / 0.003) + 0.6 * np.exp(-np.maximum(0, t - 0.004) / 0.003) * (t > 0.004))
    blast = bp(white(len(t), seed + 1), 300, 4000) * np.exp(-t / 0.06)
    boom = chirp_sine(95, 40, d) * np.exp(-t / 0.18)
    y = saturate(crack + blast + boom * 0.8, 2.5)
    return norm(reverb(widen(y, 7, 0.4, seed), 'outdoor', 0.6))


def heartbeat(n_beats=4, bpm=62, seed=0, slow=0.0):
    beat = 60.0 / bpm
    out = np.zeros(n_of(n_beats * beat * (1 + slow) + 0.6), np.float32)
    tt = 0.0
    for k in range(n_beats):
        for dt, f0, f1, g in ((0, 72, 44, 1.0), (0.19, 60, 38, 0.75)):
            d = 0.16
            t = t_axis(d)
            s = chirp_sine(f0, f1, d) * np.exp(-t / 0.045) * (1 - np.exp(-t / 0.004)) * g
            i = n_of(tt + dt)
            out[i:i + len(s)] += s
        tt += beat * (1 + slow * k / max(1, n_beats - 1))
    return norm(to_stereo(lp(out, 160)))


def boxing_bell(n=3, seed=0):
    out = np.zeros(n_of(0.18 * n + 2.0), np.float32)
    for k in range(n):
        b = bell(1250, 1.6, 1.0, seed + k)[:, 0]
        out[n_of(0.18 * k):n_of(0.18 * k) + len(b)] += b
    return norm(widen(out, 6, 0.3, seed))


def bonk(seed=0):
    d = 0.6
    t = t_axis(d)
    y = partials([520, 1340, 2610], [1, .6, .3], [.12, .06, .04], d, seed)
    y += chirp_sine(180, 110, d) * np.exp(-t / 0.05) * 0.8
    y += hp(white(len(t), seed), 2500) * np.exp(-t / 0.002)
    return norm(to_stereo(y))


def boing(seed=0):
    d = 0.75
    t = t_axis(d)
    vib = 1 + 0.18 * np.sin(2 * np.pi * 11 * t) * np.exp(-t / 0.3)
    f = (240 - 50 * t / d) * vib
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35) * np.minimum(1, t / 0.004)
    y += 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * np.exp(-t / 0.2)
    return norm(to_stereo(y.astype(np.float32)))


def slide_whistle(down=True, seed=0):
    d = 0.7
    t = t_axis(d)
    f0, f1 = (1500, 420) if down else (420, 1500)
    f = (f0 * (f1 / f0) ** (t / d)) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.05)
    y += bp(white(len(t), seed), 800, 3000) * 0.05
    return norm(to_stereo(y.astype(np.float32)))


def punch(seed=0):
    sw = swish(seed)[:n_of(0.12), 0] * 0.4
    d = 0.4
    t = t_axis(d)
    y = chirp_sine(125, 52, d) * np.exp(-t / 0.06)
    y += bp(white(len(t), seed), 1000, 5000) * np.exp(-t / 0.008) * 0.8
    y += lp(white(len(t), seed + 1), 400) * np.exp(-t / 0.03) * 0.6
    out = np.zeros(len(sw) + len(y), np.float32)
    out[:len(sw)] += sw
    out[len(sw) - n_of(0.01):len(sw) - n_of(0.01) + len(y)] += saturate(y, 1.8)
    return norm(reverb(to_stereo(out), 'small', 0.12))


def bone_crack(seed=0):
    r = rng(seed)
    d = 0.4
    out = np.zeros(n_of(d), np.float32)
    for k in range(5):
        i = n_of(r.uniform(0, 0.03))
        L = n_of(0.0015)
        out[i:i + L] += hp(white(L, seed + k), 2500) * r.uniform(0.6, 1)
    for k in range(30):
        i = n_of(r.uniform(0.005, 0.07))
        L = n_of(r.uniform(0.001, 0.004))
        out[i:i + L] += bp(white(L, seed + 40 + k), 2500, 8000) * r.uniform(0.1, 0.4)
    t = t_axis(d)
    out += chirp_sine(300, 150, d) * np.exp(-t / 0.02) * 0.4
    return norm(to_stereo(out))


def stone_slam(seed=0):
    d = 1.2
    t = t_axis(d)
    y = chirp_sine(82, 38, d) * np.exp(-t / 0.16)
    y += lp(white(len(t), seed), 2500) * np.exp(-t / 0.05) * 0.8
    grit = hp(brown(len(t), seed + 1), 300) * np.exp(-t / 0.35) * 0.35
    return norm(reverb(widen(saturate(y + grit, 1.6), 8, 0.4, seed), 'room', 0.2))


def coffin_thud(seed=0):
    d = 0.7
    t = t_axis(d)
    y = chirp_sine(142, 96, d) * np.exp(-t / 0.09)
    y += bp(white(len(t), seed), 200, 1200) * np.exp(-t / 0.05) * 0.8
    return norm(reverb(to_stereo(y), 'room', 0.3))


def shovel(seed=0):
    r = rng(seed)
    d = 0.55
    out = np.zeros(n_of(d), np.float32)
    for k in range(70):
        i = n_of(r.uniform(0, 0.28))
        L = n_of(r.uniform(0.002, 0.008))
        out[i:i + L] += lp(white(L, seed + k), 2500) * r.uniform(0.1, 0.6)
    t = t_axis(d)
    out += chirp_sine(160, 70, d) * np.exp(-t / 0.05) * 0.5
    return norm(widen(out, 6, 0.4, seed))


def page_flip(seed=0):
    d = 0.32
    n = n_of(d)
    t = t_axis(d)
    flutter = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * (35 + 25 * t / d) * t))
    y = bp(white(n, seed), 1500, 7000) * flutter * _env_ar(n, 0.35, 1.3, 1.5)
    return norm(pan(y, np.linspace(0.4, -0.4, n)))


def quill(seed=0, dur=0.7):
    r = rng(seed)
    n = n_of(dur)
    y = bp(white(n, seed), 3000, 8500) * (0.3 + 0.7 * (lp(r.standard_normal(n), 30) > 0.02))
    return norm(to_stereo(y * _env_ar(n, 0.1, 1, 0.5)))


def gallop(dur=2.0, seed=0, rate=2.6):
    r = rng(seed)
    out = np.zeros(n_of(dur + 0.3), np.float32)
    tt = 0.0
    while tt < dur:
        for dt, g in ((0.0, 0.6), (0.075, 0.8), (0.19, 1.0)):
            d = 0.06
            t = t_axis(d)
            s = (np.sin(2 * np.pi * r.uniform(260, 320) * t) * np.exp(-t / 0.018)
                 + bp(white(len(t), seed + int(tt * 100)), 600, 2600) * np.exp(-t / 0.01) * 0.8)
            i = n_of(tt + dt)
            out[i:i + len(s)] += s * g * r.uniform(0.8, 1.0)
        tt += 1 / rate
    out += lp(brown(len(out), seed), 300) * 0.15
    return norm(pan(out, np.linspace(-0.7, 0.7, len(out))))


def clock_tick(dur=4.0, period=0.5, seed=0):
    out = np.zeros(n_of(dur), np.float32)
    k = 0
    tt = 0.0
    while tt < dur - 0.05:
        f = 3100 if k % 2 == 0 else 2600
        d = 0.04
        t = t_axis(d)
        s = resonator(white(len(t), seed + k), f, 18) * np.exp(-t / 0.006)
        i = n_of(tt)
        out[i:i + len(s)] += s
        tt += period
        k += 1
    return norm(widen(out, 4, 0.2, seed))


def censor_beep(dur=0.32):
    t = t_axis(dur)
    y = np.sin(2 * np.pi * 1000 * t) * np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.005)
    return norm(to_stereo(y.astype(np.float32)))


def rec_beep():
    return censor_beep(0.12) * 0.8


def radio_static(dur=0.6, seed=0):
    n = n_of(dur)
    r = rng(seed)
    y = bp(white(n, seed), 800, 3500) * (0.5 + 0.5 * (r.random(n) > 0.97))
    return norm(to_stereo(y * _env_ar(n, 0.1, 1, 1)))


def camera_shutter(seed=0):
    a = click(seed, 2500)[:, 0]
    out = np.zeros(n_of(0.12), np.float32)
    out[:len(a)] += a
    out[n_of(0.045):n_of(0.045) + len(a)] += a * 0.8
    out += bp(white(len(out), seed), 2000, 8000) * _env_ar(len(out), 0.3, 1, 2) * 0.2
    return norm(to_stereo(out))


def snore(seed=0):
    d = 2.4
    n = n_of(d)
    t = t_axis(d)
    inhale = resonator(lp(white(n, seed), 1800), 700, 4) * np.clip((t - 0.0) / 1.0, 0, 1) * (t < 1.1)
    buzz = (1 + np.sign(np.sin(2 * np.pi * 28 * t))) * 0.5
    exhale = lp(white(n, seed + 1) * buzz, 650) * np.clip((t - 1.1) / 0.2, 0, 1) * np.clip((2.3 - t) / 0.9, 0, 1) * (t >= 1.1)
    whistle = np.sin(2 * np.pi * 950 * t) * np.clip((t - 1.4) / 0.2, 0, 1) * np.clip((2.3 - t) / 0.5, 0, 1) * 0.15 * (t >= 1.4)
    return norm(to_stereo((inhale * 0.6 + exhale * 1.2 + whistle).astype(np.float32)))


def gulp(seed=0):
    d = 0.35
    t = t_axis(d)
    f = 320 * (150 / 320) ** (t / 0.12)
    y = np.sin(2 * np.pi * np.cumsum(np.maximum(f, 150)) / SR) * np.exp(-t / 0.06) * np.minimum(1, t / 0.005)
    y = resonator(y, 600, 3) + y * 0.5
    return norm(to_stereo(y.astype(np.float32)))


def sizzle(dur=1.4, seed=0):
    n = n_of(dur)
    y = hp(white(n, seed), 3000) * _env_ar(n, 0.05, 1, 1.5)
    y += fire_bed(dur, seed)[:, 0] * 0.3
    return norm(widen(y.astype(np.float32), 8, 0.6, seed))


# ============================================================ voices without words (crowds)
VOWELS = dict(ah=(730, 1090, 2440), eh=(530, 1840, 2480), oh=(570, 840, 2410), ee=(270, 2290, 3010), oo=(300, 870, 2240))


def _voice(dur, f0, vowel, seed, contour=None, breath=0.15):
    n = n_of(dur)
    r = rng(seed)
    t = t_axis(dur)
    c = contour(t / dur) if contour else 1.0
    jit = 1 + 0.02 * lp(r.standard_normal(n), 8) * 6
    f = f0 * c * jit * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(f) / SR
    src = (ph % 1.0) * 2 - 1
    src = lp(src, 3500) + breath * white(n, seed)
    F1, F2, F3 = VOWELS[vowel]
    y = resonator(src, F1, 6) + 0.7 * resonator(src, F2, 9) + 0.35 * resonator(src, F3, 12)
    return y.astype(np.float32)


def crowd_cheer(dur=2.6, seed=0, size=26):
    r = rng(seed)
    out = np.zeros((n_of(dur), 2), np.float32)
    for k in range(size):
        a = r.uniform(0, 0.35)
        d = dur - a - r.uniform(0, 0.4)
        f0 = r.uniform(150, 340) * (0.6 if r.random() < 0.4 else 1)
        v = _voice(d, f0, r.choice(['ah', 'eh', 'oh', 'ee']), seed + k,
                   contour=lambda u: 1 + 0.25 * np.sin(np.pi * np.minimum(1, u * 1.6)), breath=0.25)
        env = _env_ar(len(v), r.uniform(0.15, 0.45), 1.5, 1.2)
        i = n_of(a)
        out[i:i + len(v)] += pan(v * env * r.uniform(0.4, 1), r.uniform(-0.9, 0.9))
    out += fit(applause(dur, seed + 99, 30), len(out)) * 0.5
    return norm(reverb(out, 'hall', 0.25))


def crowd_gasp(seed=0, size=18):
    r = rng(seed)
    dur = 0.9
    out = np.zeros((n_of(dur), 2), np.float32)
    for k in range(size):
        d = r.uniform(0.35, 0.6)
        n = n_of(d)
        src = white(n, seed + k)
        F1, F2, F3 = VOWELS['ah']
        y = resonator(src, F1 * r.uniform(.9, 1.1), 5) + 0.8 * resonator(src, F2 * r.uniform(.9, 1.1), 7) + 0.4 * resonator(src, F3, 10)
        y *= _env_ar(n, 0.25, 0.8, 2)
        i = n_of(r.uniform(0, 0.12))
        out[i:i + n] += pan(y, r.uniform(-0.8, 0.8)) * r.uniform(0.5, 1)
    return norm(reverb(out, 'hall', 0.2))


def crowd_murmur(dur=8.0, seed=0, size=14):
    r = rng(seed)
    n = n_of(dur)
    out = np.zeros((n, 2), np.float32)
    for k in range(size):
        f0 = r.uniform(110, 260)
        v = _voice(dur, f0, r.choice(list(VOWELS)), seed + k, breath=0.35)
        am = np.clip(lp(r.standard_normal(n), 5) * 9 + 0.3, 0, 1)
        out += pan(v * am * r.uniform(0.3, 1), r.uniform(-1, 1))
    out = lp(out, 2600)
    return norm(reverb(out, 'room', 0.35))


def applause(dur=3.0, seed=0, people=34):
    r = rng(seed)
    n = n_of(dur)
    out = np.zeros((n, 2), np.float32)
    for p in range(people):
        period = r.uniform(0.17, 0.3)
        fres = r.uniform(900, 2500)
        tt = r.uniform(0, period)
        pp = r.uniform(-0.9, 0.9)
        L = n_of(0.03)
        clap = resonator(white(L, seed + p), fres, 3) * np.exp(-np.arange(L) / (L * 0.12))
        clap += hp(white(L, seed + p + 500), 1500) * np.exp(-np.arange(L) / (L * 0.05)) * 0.6
        st_ = pan(clap.astype(np.float32), pp)
        while tt < dur - 0.03:
            i = n_of(tt)
            out[i:i + L] += st_ * r.uniform(0.5, 1.0)
            tt += period * r.uniform(0.9, 1.1)
    env = np.minimum(1, t_axis(dur) / 0.25) * np.minimum(1, (dur - t_axis(dur)) / 0.8)
    out *= env[:, None]
    return norm(reverb(out, 'room', 0.3))


def crickets(dur=4.0, seed=0):
    r = rng(seed)
    n = n_of(dur)
    out = np.zeros((n, 2), np.float32)
    for c in range(3):
        f = r.uniform(4300, 4900)
        tt = r.uniform(0, 0.4)
        pp = r.uniform(-0.6, 0.6)
        while tt < dur - 0.2:
            for k in range(4):
                d = 0.012
                t = t_axis(d)
                s = np.sin(2 * np.pi * f * t) * np.sin(np.pi * t / d) ** 2
                i = n_of(tt + k * 0.028)
                out[i:i + len(s)] += pan(s.astype(np.float32), pp) * 0.6
            tt += r.uniform(0.55, 0.85)
    out += widen(hp(white(n, seed), 6000) * 0.01, 9, 0.8, seed)
    return norm(out)


# ============================================================ ambience beds (loopable)
def _loop(fn, dur, seed, seg=10.0, **kw):
    """Tile an ambience generator with crossfades so long beds don't need huge synthesis."""
    xf = n_of(1.0)
    n = n_of(dur)
    out = np.zeros((n, 2), np.float32)
    pos = 0
    k = 0
    while pos < n:
        s = fn(seg + 1.0, seed + k, **kw)
        L = len(s)
        w = np.ones(L, np.float32)
        w[:xf] = np.linspace(0, 1, xf)
        w[-xf:] = np.linspace(1, 0, xf)
        m = min(L, n - pos)
        out[pos:pos + m] += s[:m] * w[:m, None]
        pos += L - xf
        k += 1
    return out


def _wind(dur, seed, band=(180, 900), gusty=1.0):
    n = n_of(dur)
    r = rng(seed)
    x = white(n, seed)
    mod = lp(r.standard_normal(n), 0.4) * 30 * gusty
    c = (band[0] + band[1]) / 2 * (1 + 0.35 * np.tanh(mod))
    frames = c[::256]
    y = _moving_band(x, frames, 0.6)
    amp = 0.55 + 0.45 * np.tanh(lp(r.standard_normal(n), 0.6) * 25)
    return widen((y * amp).astype(np.float32), 14, 0.8, seed)


def wind_bed(dur=8, seed=0):
    return norm(_loop(_wind, dur, seed))


def desert_bed(dur=8, seed=0):
    def f(d, s):
        return fit(_wind(d, s, (500, 1400), 1.3), n_of(d)) + widen(hp(white(n_of(d), s), 5000) * 0.05, 9, 0.9, s)
    return norm(_loop(f, dur, seed))


def _birds(dur, seed):
    r = rng(seed)
    n = n_of(dur)
    out = np.zeros((n, 2), np.float32)
    for k in range(int(dur * 1.2)):
        tt = r.uniform(0, dur - 0.6)
        f0 = r.uniform(2400, 5200)
        notes = r.integers(2, 6)
        pp = r.uniform(-0.8, 0.8)
        for j in range(notes):
            d = r.uniform(0.04, 0.1)
            s = chirp_sine(f0 * r.uniform(0.9, 1.1), f0 * r.uniform(1.1, 1.5), d) * np.sin(np.pi * np.linspace(0, 1, n_of(d))) ** 2
            i = n_of(tt + j * r.uniform(0.07, 0.13))
            if i + len(s) < n:
                out[i:i + len(s)] += pan(s, pp) * r.uniform(0.1, 0.35)
    return out


def birds_bed(dur=8, seed=0):
    def f(d, s):
        return _birds(d, s) + fit(_wind(d, s + 7, (200, 700), 0.5), n_of(d)) * 0.25
    return norm(_loop(f, dur, seed))


def river_bed(dur=8, seed=0):
    def f(d, s):
        n = n_of(d)
        r = rng(s)
        out = np.zeros(n, np.float32)
        for k in range(int(d * 90)):
            L = n_of(r.uniform(0.01, 0.04))
            fr = r.uniform(300, 1600)
            b = chirp_sine(fr, fr * r.uniform(1.1, 1.6), L / SR) * np.sin(np.pi * np.linspace(0, 1, L)) ** 2
            i = r.integers(0, n - L)
            out[i:i + L] += b * r.uniform(0.02, 0.12)
        out += bp(white(n, s), 300, 2500) * 0.12
        return widen(out, 12, 0.8, s) + fit(_birds(d, s + 3), n) * 0.5
    return norm(_loop(f, dur, seed))


def sea_bed(dur=8, seed=0):
    def f(d, s):
        n = n_of(d)
        r = rng(s)
        t = t_axis(d)
        swell = np.zeros(n, np.float32)
        tt = 0.0
        while tt < d:
            per = r.uniform(3.5, 6.0)
            u = np.clip((t - tt) / per, 0, 1)
            swell += (np.sin(np.pi * u) ** 3) * (t >= tt) * (t < tt + per)
            tt += per * r.uniform(0.55, 0.8)
        low = lp(brown(n, s), 500) * (0.4 + swell)
        wash = bp(white(n, s + 1), 900, 6000) * swell ** 2 * 0.25
        return widen((low + wash).astype(np.float32), 15, 0.9, s)
    return norm(_loop(f, dur, seed))


def night_bed(dur=8, seed=0):
    def f(d, s):
        out = crickets(d, s) * 0.6 + fit(_wind(d, s + 2, (150, 500), 0.4), n_of(d)) * 0.3
        r = rng(s)
        if r.random() < 0.5:
            tt = r.uniform(1, d - 2)
            for j, dt in enumerate((0, 0.45)):
                dd = 0.35
                tx = t_axis(dd)
                h = np.sin(2 * np.pi * 390 * tx) * np.sin(np.pi * tx / dd) ** 2
                h = resonator(h, 400, 5) * 0.2
                i = n_of(tt + dt)
                out[i:i + len(h)] += pan(h, -0.4)
        return out
    return norm(_loop(f, dur, seed))


def hall_bed(dur=8, seed=0):
    def f(d, s):
        n = n_of(d)
        tone = widen(lp(pink(n, s), 400) * 0.25, 12, 0.6, s)
        return tone + fit(fire_bed(d, s + 5, 0.4), len(tone)) * 0.25
    return norm(_loop(f, dur, seed))


def stadium_bed(dur=8, seed=0):
    return norm(_loop(lambda d, s: fit(crowd_murmur(d, s, 12), n_of(d)), dur, seed))


def feast_bed(dur=8, seed=0):
    def f(d, s):
        out = fit(crowd_murmur(d, s, 10), n_of(d)) * 0.8
        r = rng(s)
        for k in range(int(d * 0.8)):
            c = partials([r.uniform(1800, 3500)] * 1, [1], [0.15], 0.2, s + k)
            i = n_of(r.uniform(0, d - 0.3))
            out[i:i + len(c)] += pan(c, r.uniform(-0.7, 0.7)) * 0.15
        return out + fit(fire_bed(d, s + 9, 0.3), len(out)) * 0.2
    return norm(_loop(f, dur, seed))


def battle_bed(dur=8, seed=0):
    def f(d, s):
        n = n_of(d)
        r = rng(s)
        out = fit(crowd_murmur(d, s, 10), n) * 0.5
        for k in range(int(d * 1.5)):
            c = sword_clash(s + k)
            c = lp(c, 3500) * r.uniform(0.1, 0.35)
            i = n_of(r.uniform(0, d - 1))
            m = min(len(c), n - i)
            out[i:i + m] += c[:m]
        out += widen(lp(brown(n, s), 200) * 0.3, 10, 0.5, s)
        return out
    return norm(_loop(f, dur, seed))


# ============================================================ registry
GEN = dict(whoosh=whoosh, swish=swish, riser=riser, reverse_cymbal=reverse_cymbal, sub_drop=sub_drop, pop=pop, click=click,
           ding=ding, notify=notify, buzzer=buzzer, marker=marker, text_hit=text_hit, impact=impact, thud=thud, coins=coins,
           cha_ching=cha_ching, sparkle=sparkle, sword_shing=sword_shing, sword_clash=sword_clash, arrow=arrow, thunk=thunk,
           arrow_hit=arrow_hit, fire_whoosh=fire_whoosh, door_crash=door_crash, metal_clang=metal_clang,
           chain_rattle=chain_rattle, splash=splash, wood_crack=wood_crack, ship_crash=ship_crash, cannon=cannon,
           gunshot=gunshot, heartbeat=heartbeat, boxing_bell=boxing_bell, bonk=bonk, boing=boing, slide_whistle=slide_whistle,
           punch=punch, bone_crack=bone_crack, stone_slam=stone_slam, coffin_thud=coffin_thud, shovel=shovel,
           page_flip=page_flip, quill=quill, gallop=gallop, clock_tick=clock_tick, censor_beep=censor_beep, rec_beep=rec_beep,
           radio_static=radio_static, camera_shutter=camera_shutter, snore=snore, gulp=gulp, sizzle=sizzle,
           crowd_cheer=crowd_cheer, crowd_gasp=crowd_gasp, crowd_murmur=crowd_murmur, applause=applause, crickets=crickets,
           bell=bell)
BEDS = dict(wind=wind_bed, desert=desert_bed, birds=birds_bed, river=river_bed, sea=sea_bed, night=night_bed, hall=hall_bed,
            stadium=stadium_bed, feast=feast_bed, battle=battle_bed, fire=lambda dur=8, seed=0: fire_bed(dur, seed))


@functools.lru_cache(maxsize=512)
def _cached(name, seed, items):
    kw = dict(items)
    return GEN[name](seed=seed, **kw) if 'seed' in GEN[name].__code__.co_varnames else GEN[name](**kw)


def get(name, seed=0, **kw):
    return _cached(name, seed, tuple(sorted(kw.items())))


def bed(name, dur, seed=0):
    return BEDS[name](dur=dur, seed=seed)
