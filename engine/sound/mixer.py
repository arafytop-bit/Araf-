"""Final mix: voice chain, music bus (stems, hall reverb, voice-keyed ducking, tape stops / scratches / muffles /
drops), SFX bus (level-matched events, panning, reverb sends), ambience bus, master + loudness.
"""
import os
import re
import subprocess

import numpy as np
import scipy.signal as ss
import soundfile as sf
from pedalboard import (Pedalboard, Compressor, HighpassFilter, LowpassFilter, PeakFilter, HighShelfFilter, Limiter,
                        Convolution, Gain)

from .dsp import SR, n_of, impulse, rms_db, db, place, white, bp
from . import sfx as X

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.cache', 'sf')


# ---------------------------------------------------------------- voice
def load_voice(path, offset, duration):
    v, sr = sf.read(path, dtype='float32', always_2d=False)
    if v.ndim > 1:
        v = v.mean(1)
    if sr != SR:
        v = ss.resample_poly(v, SR, sr).astype(np.float32)
    out = np.zeros(n_of(duration), np.float32)
    i = n_of(offset)
    m = min(len(v), len(out) - i)
    out[i:i + m] = v[:m]
    return out


def deess(x, f_lo=5200, f_hi=10500, thresh_db=-30, ratio=4.0):
    band = bp(x, f_lo, f_hi, 4)
    env = np.sqrt(ss.lfilter([0.002], [1, -0.998], band.astype(np.float64) ** 2) + 1e-12)
    lvl = 20 * np.log10(env + 1e-9)
    over = np.maximum(0, lvl - thresh_db)
    red = db(-over * (1 - 1 / ratio))
    return (x - band + band * red).astype(np.float32)


def process_voice(v):
    board = Pedalboard([HighpassFilter(75), PeakFilter(240, -2.5, 1.0), PeakFilter(3200, 2.5, 0.8), HighShelfFilter(9000, 2.0, 0.7),
                        Compressor(threshold_db=-24, ratio=2.8, attack_ms=4, release_ms=70)])
    y = board(v[None, :], SR)[0]
    return deess(y)


def speech_activity(v, attack=0.015, release=0.35):
    """0..1 envelope of the voice (for ducking)."""
    win = n_of(0.01)
    e = np.sqrt(np.convolve(v.astype(np.float64) ** 2, np.ones(win) / win, 'same'))
    lvl = 20 * np.log10(e + 1e-9)
    act = np.clip((lvl + 52) / 18, 0, 1)
    out = np.empty_like(act)
    a = np.exp(-1 / (attack * SR))
    r = np.exp(-1 / (release * SR))
    y = 0.0
    # one-pole follower with separate attack/release (vectorised via lfilter on decimated signal)
    dec = 48
    ad = act[::dec]
    od = np.empty_like(ad)
    a2, r2 = a ** dec, r ** dec
    for i, x in enumerate(ad):
        y = (a2 * y + (1 - a2) * x) if x > y else (r2 * y + (1 - r2) * x)
        od[i] = y
    out = np.interp(np.arange(len(act)), np.arange(len(ad)) * dec, od)
    return out.astype(np.float32)


# ---------------------------------------------------------------- helpers
def _conv(x, kind, wet):
    path = os.path.join(CACHE, f'ir_{kind}.wav')
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        sf.write(path, impulse(kind), SR, subtype='FLOAT')
    board = Pedalboard([Convolution(path, mix=1.0)])
    w = board(x.T.copy(), SR).T
    return (x + wet * w).astype(np.float32)


def loud_window_db(x, win=0.1):
    m = x.mean(1) if x.ndim > 1 else x
    w = n_of(win)
    if len(m) <= w:
        return rms_db(m)
    e = np.convolve(m.astype(np.float64) ** 2, np.ones(w) / w, 'valid')
    return float(10 * np.log10(e.max() + 1e-12))


def balance(x, p):
    if p == 0:
        return x
    th = (np.clip(p, -1, 1) + 1) * np.pi / 4
    g = np.array([np.cos(th), np.sin(th)], np.float32) * np.sqrt(2)
    return x * g[None, :]


def ramp_gain(n, segments, fade=0.03):
    """Piecewise gain curve from [(t0, t1, gain)] (gain multiplies), with short fades at edges."""
    g = np.ones(n, np.float32)
    f = n_of(fade)
    for t0, t1, val in segments:
        a, b = max(0, n_of(t0)), min(n, n_of(t1))
        if b <= a:
            continue
        g[a:b] *= val
        if f and a - f >= 0:
            g[a - f:a] *= np.linspace(1, val, f)
        if f and b + f <= n:
            g[b:b + f] *= np.linspace(val, 1, f)
    return g


# ---------------------------------------------------------------- music FX
def tape_stop(mus, t, dur=0.8):
    i0, L = n_of(t), n_of(dur)
    if i0 + L >= len(mus):
        return
    speed = (1 - np.linspace(0, 1, L)) ** 1.6
    pos = i0 + np.cumsum(speed)
    idx = np.arange(len(mus))
    seg = np.stack([np.interp(pos, idx[i0:i0 + L + 2], mus[i0:i0 + L + 2, c]) for c in range(2)], 1)
    seg = ss.sosfilt(ss.butter(2, 6000 / (SR / 2), output='sos'), seg, axis=0)
    mus[i0:i0 + L] = seg * np.linspace(1, 0.2, L)[:, None]
    mus[i0 + L:i0 + L + n_of(0.02)] *= np.linspace(1, 0, min(n_of(0.02), len(mus) - i0 - L))[:, None]


def scratch(mus, t, seed=0):
    """Vinyl scratch built from the music itself: forward-back-forward rubs + friction noise."""
    i0 = n_of(t)
    shape = [(0.05, 1.0), (0.09, -2.6), (0.08, 2.8), (0.10, -2.2), (0.06, 1.4), (0.08, -0.6)]
    sp = np.concatenate([np.full(n_of(d), v, np.float32) for d, v in shape])
    sp = np.convolve(sp, np.hanning(n_of(0.012)) / np.hanning(n_of(0.012)).sum(), 'same')
    L = len(sp)
    if i0 + L >= len(mus) or i0 < n_of(0.6):
        return
    pos = i0 + np.cumsum(sp)
    lo = int(pos.min()) - 2
    hi = int(pos.max()) + 2
    idx = np.arange(lo, hi)
    seg = np.stack([np.interp(pos, idx, mus[lo:hi, c]) for c in range(2)], 1)
    nz = white(L, seed) * np.abs(sp)
    nz = bp(nz, 600, 3500) * 0.25
    mus[i0:i0 + L] = (seg * 1.4 + nz[:, None]) * np.hanning(L * 2)[L:][:, None] ** 0.3
    mus[i0 + L:i0 + L + n_of(0.01)] *= 0


def muffle(bus, t0, t1, f_lo=420.0, ramp_in=1.4, ramp_out=0.25):
    """Progressive low-pass (blacking out / underwater), block-processed with a moving cutoff."""
    a, b = n_of(t0), n_of(t1 + ramp_out)
    if b <= a:
        return
    seg = bus[a:b].T.copy()
    out = np.zeros_like(seg)
    blk = 1024
    lpf = LowpassFilter(18000)
    board = Pedalboard([lpf])
    for k in range(0, seg.shape[1], blk):
        tt = t0 + k / SR
        if tt < t0 + ramp_in:
            u = (tt - t0) / ramp_in
            fc = 18000 * (f_lo / 18000) ** u
        elif tt < t1:
            fc = f_lo
        else:
            u = (tt - t1) / ramp_out
            fc = f_lo * (18000 / f_lo) ** min(1, u)
        lpf.cutoff_frequency_hz = float(fc)
        out[:, k:k + blk] = board(seg[:, k:k + blk], SR, reset=False)
    bus[a:b] = out.T


# ---------------------------------------------------------------- main
def mix(voice_path, voice_offset, duration, music_stems, music_fx, sfx_events, amb_segments, out_path,
        music_under_db=17.0, duck_db=6.5, amb_under_db=27.0, report=print, stems_dir=None):
    n = n_of(duration)
    report('voice')
    v = process_voice(load_voice(voice_path, voice_offset, duration))
    speech = v[np.abs(v) > 1e-4]
    v_db = rms_db(speech)
    act = speech_activity(v)

    # ---- music bus
    report('music bus')
    trims = dict(harm=0.0, bass=1.5, lead=-1.0, perc=0.0, hits=2.0)
    mus = np.zeros((n, 2), np.float32)
    for k, x in music_stems.items():
        x = x[:n] if len(x) >= n else np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])
        mus += x * db(trims.get(k, 0.0))
    mus = Pedalboard([HighpassFilter(28), PeakFilter(420, -1.5, 0.9), PeakFilter(2600, -3.0, 0.7)])(mus.T.copy(), SR).T
    mus = _conv(mus, 'hall', 0.20)[:n]
    present = np.abs(mus).max(1) > 1e-4
    m_db = rms_db(mus[present]) if present.any() else -60
    mus *= db(v_db - music_under_db - m_db)
    for fx in sorted(music_fx, key=lambda e: e['t']):
        if fx['kind'] == 'tapestop':
            tape_stop(mus, fx['t'], fx.get('dur', 0.8))
        elif fx['kind'] == 'scratch':
            scratch(mus, fx['t'], fx.get('seed', 0))
    drops = [(fx['t'], fx['t'] + fx['dur'], fx.get('gain', 0.0)) for fx in music_fx if fx['kind'] in ('drop', 'duck')]
    gdrop = ramp_gain(n, [(a, b, db(g) if g < 0 else g) for a, b, g in drops], 0.03)
    duck = db(-duck_db * act)
    mus *= (gdrop * duck)[:, None]

    # ---- ambience bus
    report('ambience')
    amb = np.zeros((n, 2), np.float32)
    for seg in amb_segments:
        d = seg['t1'] - seg['t0'] + 0.8
        if d <= 0.3:
            continue
        b = X.bed(seg['bed'], d, seg.get('seed', 0))
        f = n_of(0.35)
        w = np.ones(len(b), np.float32)
        w[:f] = np.linspace(0, 1, f)
        w[-f:] = np.linspace(1, 0, f)
        lvl = rms_db(b)
        place(amb, b * w[:, None], seg['t0'] - 0.2, db(v_db - amb_under_db + seg.get('gain', 0.0) - lvl))
    amb *= db(-4.0 * act)[:, None]

    # ---- sfx bus (+ reverb sends)
    report('sfx (%d events)' % len(sfx_events))
    sfxb = np.zeros((n, 2), np.float32)
    sends = {k: np.zeros((n, 2), np.float32) for k in ('room', 'hall', 'outdoor')}
    for e in sfx_events:
        x = X.get(e['name'], e.get('seed', 0), **e.get('kw', {}))
        lvl = loud_window_db(x)
        g = db(v_db + e.get('gain', -8.0) - lvl)
        x = balance(x, e.get('pan', 0.0))
        place(sfxb, x, e['t'] - e.get('lead', 0.0), g)
        if e.get('verb'):
            place(sends[e['verb']], x, e['t'] - e.get('lead', 0.0), g * e.get('send', 0.35))
    for k, s in sends.items():
        if np.abs(s).max() > 0:
            sfxb += (_conv(s, k, 1.0)[:n] - s)
    sfxb *= db(-2.0 * act)[:, None]

    # ---- muffles (blackout effect on everything but the voice)
    for fx in music_fx:
        if fx['kind'] == 'muffle':
            for bus in (mus, amb, sfxb):
                muffle(bus, fx['t'], fx['t'] + fx['dur'], fx.get('f', 420.0))

    # ---- QA: bus levels vs. the voice in speech and in gaps
    on, off = act > 0.6, act < 0.05
    def lv(x, m):
        return round(rms_db(x[m]) - v_db, 1) if m.any() and np.abs(x[m]).max() > 0 else None
    report('levels vs voice (speech / gaps): music %s / %s, sfx %s / %s, amb %s / %s' % (
        lv(mus, on), lv(mus, off), lv(sfxb, on), lv(sfxb, off), lv(amb, on), lv(amb, off)))
    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        for name, x in (('voice', v), ('music', mus), ('sfx', sfxb), ('amb', amb)):
            sf.write(os.path.join(stems_dir, name + '.flac'), np.clip(x, -1, 1), SR, subtype='PCM_16')

    # ---- master
    report('master')
    mixd = mus + amb + sfxb + v[:, None]
    mixd = Pedalboard([Compressor(threshold_db=-20, ratio=1.7, attack_ms=25, release_ms=220),
                       Limiter(threshold_db=-2.0, release_ms=120)])(mixd.T.copy(), SR).T
    fo = n_of(0.3)
    mixd[-fo:] *= np.linspace(1, 0, fo)[:, None]
    raw = out_path + '.raw.wav'
    sf.write(raw, mixd.astype(np.float32), SR, subtype='FLOAT')
    stats = loudnorm(raw, out_path)
    os.remove(raw)
    return stats


def loudnorm(in_path, out_path, I=-14.0, TP=-1.5):
    def measure(path):
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                           capture_output=True, text=True).stderr
        summ = r[r.rindex('Summary:'):]
        return (float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)),
                float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1)))
    i0, tp0 = measure(in_path)
    lim = 10 ** ((TP - 0.5) / 20)
    af = f'volume={I - i0:.2f}dB,aresample=192000,alimiter=limit={lim:.4f}:attack=3:release=90:level=disabled,aresample=48000'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', in_path, '-af', af, '-c:a', 'pcm_s24le', out_path],
                   check=True)
    i1, tp1 = measure(out_path)
    return dict(input_i=i0, input_tp=tp0, output_i=i1, output_tp=tp1)
