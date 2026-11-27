"""Designed transition/impact SFX (layered like trailer sound design: sub + body + transient + tail).

These replace the thin v2 one-layer synths for the editing kit: title hits, callout hits, whooshes, risers, pops, stamps,
impacts, dings. All stereo float32 at 48 kHz, peak-normalised to 0.9.
"""
import functools

import numpy as np

from .dsp import SR, lp, hp, bp, white, reverb, saturate, n_of, to_stereo


def _t(dur):
    return np.arange(n_of(dur)) / SR


def _norm(x, peak=0.9):
    return (x / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def _sweep_sine(f0, f1, dur, curve=6.0):
    t = _t(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (dur / curve))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _haas(mono, ms=9.0, amount=0.5):
    d = n_of(ms / 1000)
    r = np.concatenate([np.zeros(d), mono[:-d]]) if d else mono
    return np.stack([mono, mono * (1 - amount) + r * amount], 1).astype(np.float32)


@functools.lru_cache(maxsize=8)
def hit_title(seed=0):
    """Cinematic boom with a bright attack and ~1 s tail (reference: one bright hit on every title card)."""
    dur = 2.4
    t = _t(dur)
    sub = _sweep_sine(110, 34, dur, 10) * np.exp(-t / 0.55)
    body = lp(white(len(t), seed) * np.exp(-t / 0.09), 1400) * 0.9
    snap = hp(white(len(t), seed + 1) * np.exp(-t / 0.012), 2500) * 0.8
    ring = sum(np.sin(2 * np.pi * f * t + k) * np.exp(-t / d) for k, (f, d) in
               enumerate(((1130, 0.35), (1730, 0.28), (2610, 0.22), (3390, 0.18)))) * 0.10
    x = saturate(sub * 1.1, 1.8) + body + snap + ring
    st = reverb(_haas(x, 11, 0.4), 'hall', wet=0.35)[: len(t)]
    return _norm(st)


@functools.lru_cache(maxsize=8)
def hit_small(seed=0):
    dur = 0.6
    t = _t(dur)
    thump = _sweep_sine(160, 55, dur, 8) * np.exp(-t / 0.09)
    snap = bp(white(len(t), seed + 3) * np.exp(-t / 0.008), 1800, 7000)
    x = saturate(thump, 1.5) * 0.9 + snap * 0.7
    return _norm(reverb(to_stereo(x), 'room', wet=0.15)[: len(t)])


@functools.lru_cache(maxsize=8)
def whoosh(dur=0.55, seed=0, bright=1.0):
    """Air whoosh: white noise shaped in the STFT domain by a smooth time-varying band-pass (no block seams)."""
    import scipy.signal as ss
    t = _t(dur)
    n = len(t)
    nz = white(n + 2048, seed + 7)
    f, tt, Z = ss.stft(nz, SR, nperseg=1024, noverlap=768)
    u = np.clip(tt / dur, 0, 1)
    fc = 350 + 2600 * bright * np.sin(np.pi * u) ** 1.3
    bw = 0.9
    mask = np.exp(-0.5 * (np.log2(np.maximum(f[:, None], 20) / fc[None, :]) / bw) ** 2)
    env = np.sin(np.pi * u) ** 1.6 * np.where(u < 0.62, (u / 0.62) ** 0.6, 1.0)
    _, y = ss.istft(Z * mask * env[None, :], SR, nperseg=1024, noverlap=768)
    y = y[:n]
    k = n_of(0.01)
    y[:k] *= np.linspace(0, 1, k)
    y[-k:] *= np.linspace(1, 0, k)
    pan = np.clip(t / dur, 0, 1)
    st = np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1)
    return _norm(st)


@functools.lru_cache(maxsize=4)
def riser(dur=1.2, seed=0):
    t = _t(dur)
    k = t / dur
    sweep = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (3.2 * k)) / SR) * k ** 2 * 0.5
    nz = hp(white(len(t), seed + 9), 1500) * k ** 3
    x = sweep + nz * 0.6
    x[-n_of(0.01):] *= np.linspace(1, 0, n_of(0.01))
    return _norm(reverb(_haas(x, 13, 0.5), 'plate', wet=0.25)[: len(t)])


@functools.lru_cache(maxsize=8)
def pop(seed=0, pitch=1.0):
    dur = 0.12
    t = _t(dur)
    x = _sweep_sine(1100 * pitch, 380 * pitch, dur, 5) * np.exp(-t / 0.028)
    x += hp(white(len(t), seed + 5) * np.exp(-t / 0.002), 3000) * 0.3
    return _norm(to_stereo(x), 0.8)


@functools.lru_cache(maxsize=4)
def stamp(seed=0):
    dur = 1.1
    t = _t(dur)
    thud = _sweep_sine(95, 45, dur, 9) * np.exp(-t / 0.16)
    knock = bp(white(len(t), seed + 13) * np.exp(-t / 0.03), 280, 1100) * 0.8
    slap = hp(white(len(t), seed + 14) * np.exp(-t / 0.006), 2500) * 0.6
    x = saturate(thud, 1.6) + knock + slap
    return _norm(reverb(to_stereo(x), 'room', wet=0.22)[: len(t)])


@functools.lru_cache(maxsize=4)
def impact(seed=0):
    dur = 1.4
    t = _t(dur)
    sub = _sweep_sine(80, 30, dur, 9) * np.exp(-t / 0.35)
    crunch = lp(white(len(t), seed + 17) * np.exp(-t / 0.05), 3500)
    crunch = saturate(crunch * 3.0, 2.5) * 0.35         # grit by soft saturation (bit-crush steps clicked)
    x = saturate(sub, 2.0) + crunch * 0.6
    return _norm(reverb(_haas(x, 8, 0.3), 'hall', wet=0.22)[: len(t)])


@functools.lru_cache(maxsize=4)
def ding(seed=0, f0=1320.0):
    dur = 1.6
    t = _t(dur)
    x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / d) for r, a, d in
            ((1.0, 1.0, 0.7), (2.76, 0.45, 0.35), (5.40, 0.25, 0.2), (8.93, 0.12, 0.12)))
    x *= np.minimum(1, t / 0.002)
    return _norm(reverb(to_stereo(x), 'plate', wet=0.2)[: len(t)], 0.7)


@functools.lru_cache(maxsize=4)
def text_hit(seed=0):
    """Callout / kinetic word hit: punchy, short, sits under the voice."""
    dur = 0.45
    t = _t(dur)
    x = _sweep_sine(140, 60, dur, 7) * np.exp(-t / 0.07) * 0.9
    x += bp(white(len(t), seed + 21) * np.exp(-t / 0.012), 2000, 8000) * 0.55
    x += np.sin(2 * np.pi * 880 * t) * np.exp(-t / 0.05) * 0.12
    return _norm(reverb(to_stereo(x), 'room', wet=0.12)[: len(t)])


@functools.lru_cache(maxsize=4)
def scratch(seed=0):
    """Record scratch (pitch-wobbled noise + tone)."""
    dur = 0.5
    t = _t(dur)
    rate = 1 + 0.9 * np.sin(2 * np.pi * 7 * t)
    tone = np.sin(2 * np.pi * np.cumsum(420 * rate) / SR) * 0.5
    nz = bp(white(len(t), seed + 31), 600, 4000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * t)))
    x = (tone + nz) * np.exp(-t / 0.25)
    return _norm(to_stereo(x), 0.8)


DESIGNED = dict(hit_title=hit_title, hit_word=text_hit, callout=text_hit, whoosh=lambda seed=0: whoosh(0.55, seed),
                whoosh_short=lambda seed=0: whoosh(0.32, seed, 1.2), whoosh_long=lambda seed=0: whoosh(0.9, seed, 0.9),
                riser=riser, pop=pop, pop_soft=lambda seed=0: pop(seed, 1.3), stamp=stamp, impact=impact, ding=ding,
                thud=hit_small, record_scratch=scratch)
