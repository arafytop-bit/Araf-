"""Dark hip-hop / trap library-style beds (the reference's genre: low-register pulse at ~100 BPM, a different track per entry).

Drums are synthesized the way trap drums actually are made (808 sine bass with a pitch drop and saturation, layered claps,
metallic closed hats with rolls); pads and leads come from the MuseScore General soundfont through FluidSynth.
Every track is one continuous piece per section (never a new cue every 15 s), arranged in 8-bar phrases with fills.

  bed(track_name, duration, seed) -> stereo float32 (48 kHz), first downbeat at t = 0
"""
import functools
import math

import numpy as np

from .dsp import SR, lp, hp, bp, white, place, reverb, saturate, n_of, to_stereo, pan
from .sf import Part, render

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
MODES = {'minor': [0, 2, 3, 5, 7, 8, 10], 'phrygian': [0, 1, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10],
         'harmonic': [0, 2, 3, 5, 7, 8, 11], 'major': [0, 2, 4, 5, 7, 9, 11]}


def midi(key, octave):
    return 12 * (octave + 1) + NOTE[key]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ======================= drum one-shots =======================
@functools.lru_cache(maxsize=64)
def s808(freq, dur=0.9, drive=2.4, glide_from=None):
    n = n_of(dur)
    t = np.arange(n) / SR
    f = freq * (1 + 1.6 * np.exp(-t / 0.016))
    if glide_from:
        f = f + (glide_from - freq) * np.exp(-t / 0.06)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / (dur * 0.55))
    x = saturate(x, drive)
    click = hp(white(n, 3) * np.exp(-t / 0.0015), 1800) * 0.25
    x = x + click
    x[-n_of(0.02):] *= np.linspace(1, 0, n_of(0.02))
    return x.astype(np.float32)


@functools.lru_cache(maxsize=8)
def kick(seed=0):
    n = n_of(0.35)
    t = np.arange(n) / SR
    f = 52 * (1 + 2.6 * np.exp(-t / 0.022))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    x += hp(white(n, seed) * np.exp(-t / 0.003), 2500) * 0.35
    return saturate(x, 1.6)


@functools.lru_cache(maxsize=8)
def clap(seed=0):
    n = n_of(0.45)
    t = np.arange(n) / SR
    env = np.zeros(n)
    for k, d in enumerate((0.0, 0.011, 0.022)):
        i = n_of(d)
        env[i:] += np.exp(-(t[: n - i]) / 0.006) * (0.8 if k < 2 else 1.0)
    env += np.exp(-np.maximum(t - 0.022, 0) / 0.11) * (t >= 0.022) * 0.6
    x = bp(white(n, 11 + seed) * env, 900, 4200, order=2)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05) * 0.25
    x = (x + body) / max(1e-6, np.max(np.abs(x + body)))
    return x.astype(np.float32)


@functools.lru_cache(maxsize=8)
def snare(seed=0):
    n = n_of(0.3)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t / 0.045)
    nz = hp(white(n, 21 + seed), 1400) * np.exp(-t / 0.13)
    x = 0.55 * tone + 0.75 * nz
    return (x / np.max(np.abs(x))).astype(np.float32)


@functools.lru_cache(maxsize=8)
def hat(open_=False, seed=0):
    dur = 0.32 if open_ else 0.06
    n = n_of(dur)
    t = np.arange(n) / SR
    ratios = [205.3, 304.4, 369.6, 522.7, 540.0, 800.0]
    sq = sum(np.sign(np.sin(2 * np.pi * r * 6.1 * t + k)) for k, r in enumerate(ratios))
    x = bp(sq + 0.6 * white(n, 31 + seed), 7200, 15500, order=2)
    x = x * np.exp(-t / (0.11 if open_ else 0.018))
    return (x / np.max(np.abs(x))).astype(np.float32)


@functools.lru_cache(maxsize=8)
def taiko(seed=0):
    n = n_of(1.2)
    t = np.arange(n) / SR
    f = 62 * (1 + 0.9 * np.exp(-t / 0.05))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.42)
    x += lp(white(n, 41 + seed) * np.exp(-t / 0.02), 1800) * 0.6
    return saturate(x, 1.4)


@functools.lru_cache(maxsize=8)
def rim(seed=0):
    n = n_of(0.08)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 1700 * t) + 0.6 * np.sin(2 * np.pi * 820 * t)) * np.exp(-t / 0.012)
    x += hp(white(n, 51), 3000) * np.exp(-t / 0.004) * 0.5
    return (x / np.max(np.abs(x))).astype(np.float32)


# ======================= tracks (one per entry) =======================
# prog: scale-degree roots (0-based in the mode) per bar; pad/lead: GM programs; hats: 'trap' (rolls) | 'boom' (8ths)
TRACKS = {
    'intro':     dict(key='A', mode='minor', bpm=100, prog=[0, 5, 2, 6], pad=89, pad2=None, lead=14, hats='trap', kit=1.0,
                      motif=[(0, 7, 0.5), (1, 6, 0.5), (2, 4, 1.0), (4, 3, 0.5), (6, 4, 1.0)], oct808=1),
    'harald':    dict(key='D', mode='minor', bpm=98, prog=[0, 0, 5, 6], pad=52, pad2=48, lead=None, hats='trap', kit=1.0,
                      taiko=True, drone=True, oct808=1),
    'attila':    dict(key='C#', mode='phrygian', bpm=96, prog=[0, 1, 0, 6], pad=50, pad2=None, lead=71, hats='trap', kit=0.9,
                      motif=[(0, 7, 1.0), (2, 8, 0.5), (3, 7, 0.5), (4, 5, 1.0), (6, 4, 1.0)], taiko=True, oct808=1),
    'crassus':   dict(key='F', mode='minor', bpm=102, prog=[0, 3, 5, 4], pad=48, pad2=None, lead=45, hats='boom', kit=0.95,
                      motif=[(0, 0, 0.25), (0.5, 2, 0.25), (1, 4, 0.25), (1.5, 2, 0.25), (2, 5, 0.5), (3, 4, 0.5)], oct808=1),
    'arrichion': dict(key='A', mode='harmonic', bpm=100, prog=[0, 6, 5, 4], pad=89, pad2=48, lead=46, hats='trap', kit=1.0,
                      motif=[(0, 0, 0.5), (0.5, 2, 0.5), (1, 4, 0.5), (1.5, 6, 0.5), (2, 7, 1.0)], build=True, oct808=1),
    'midroll':   dict(key='F', mode='major', bpm=84, prog=[0, 5, 3, 4], pad=4, pad2=None, lead=None, hats='lofi', kit=0.8,
                      sevenths=True, swing=0.16, oct808=2),
    'yi':        dict(key='E', mode='minor', bpm=96, prog=[0, 5, 2, 6], pad=48, pad2=52, lead=77, hats='trap', kit=1.0,
                      motif=[(0, 4, 1.0), (1, 3, 0.5), (1.5, 2, 0.5), (2, 0, 1.5), (4, 4, 0.5), (4.5, 5, 0.5), (5, 4, 2.0)],
                      taiko=True, epic=True, oct808=1),
    'outro':     dict(key='A', mode='minor', bpm=108, prog=[0, 5, 2, 6], pad=89, pad2=None, lead=14, hats='trap', kit=1.1,
                      motif=[(0, 7, 0.5), (0.5, 9, 0.5), (1, 7, 0.5), (2, 4, 1.0)], oct808=1),
}


def degree(cfg, d, octave):
    sc = MODES[cfg['mode']]
    k, o = d % 7, d // 7
    return midi(cfg['key'], octave + o) + sc[k]


def chord(cfg, root_deg, octave=3, seventh=False):
    degs = [root_deg, root_deg + 2, root_deg + 4] + ([root_deg + 6] if seventh else [])
    return [degree(cfg, d, octave) for d in degs]


def bed(name, duration, seed=0, intensity=1.0, intro_bars=0, end_fill=True):
    """Render one continuous section bed. Downbeat at t=0. Returns stereo float32 of `duration` seconds."""
    cfg = TRACKS[name]
    bpm = cfg['bpm']
    beat = 60.0 / bpm
    bar = 4 * beat
    nbars = int(math.ceil(duration / bar)) + 1
    n = n_of(duration + 2.0)
    drums = np.zeros((n, 2), np.float32)
    bass = np.zeros((n, 2), np.float32)
    rng = np.random.default_rng(seed + hash(name) % 1000)
    swing = cfg.get('swing', 0.0)
    pad = Part('pad', program=cfg['pad'], volume=92, pan=64)
    pad2 = Part('pad2', program=cfg['pad2'], volume=80, pan=64) if cfg.get('pad2') else None
    lead = Part('lead', program=cfg['lead'], volume=88, pan=70) if cfg.get('lead') else None
    drone = Part('drone', program=48, volume=70) if cfg.get('drone') else None
    prog = cfg['prog']
    k_hat, k_hat_o, k_clap, k_kick, k_rim = hat(False), hat(True), clap(), kick(), rim()
    k_snare = snare()
    for b in range(nbars):
        t0 = b * bar
        if t0 >= duration + 0.5:
            break
        phrase_pos = b % 8
        root = prog[b % len(prog)]
        sparse = b < intro_bars                          # intro bars: pad + hats only
        build = cfg.get('build') and b < 4
        # ---- pad (sustained chord per bar, voiced low and dark) ----
        for m in chord(cfg, root, 3, seventh=cfg.get('sevenths', False)):
            pad.n(t0, bar * 0.98, m, 64 if not cfg.get('epic') else 72)
        if pad2:
            for m in chord(cfg, root, 4):
                pad2.n(t0, bar * 0.98, m, 52)
        if drone and b % 2 == 0:
            drone.n(t0, bar * 2, degree(cfg, 0, 2), 58)
        # ---- lead motif (every other 4-bar phrase, sparse; the bed sits ~24 dB under the voice) ----
        if lead and cfg.get('motif') and (b // 4) % 2 == 1 and phrase_pos % 4 == 0:
            for (bt, d, du) in cfg['motif']:
                lead.n(t0 + bt * beat, du * beat * 0.95, degree(cfg, d + root * 0, 5), 70)
        # ---- 808 bass ----
        r808 = degree(cfg, root, cfg.get('oct808', 1))
        if not sparse:
            pat = [0, 1.5, 2.75] if cfg['hats'] != 'lofi' else [0, 2.5]
            if phrase_pos == 7:
                pat = [0, 1.5, 2.5, 3.25]
            for k, bt in enumerate(pat):
                dur = beat * (1.4 if k < len(pat) - 1 else 1.0)
                glide = hz(r808 + 12) if (phrase_pos == 7 and k == len(pat) - 1) else None
                place(bass, to_stereo(s808(round(hz(r808), 2), dur=min(1.1, dur + 0.3), glide_from=glide)), t0 + bt * beat, 0.9)
                if k == 0 or bt == 2.75:
                    place(drums, to_stereo(k_kick), t0 + bt * beat, 0.55)
        # ---- claps / snares on 2 and 4 (half-time trap feel on 3 for 'trap') ----
        if not sparse and not build:
            hits = [2] if cfg['hats'] == 'trap' else [1, 3]
            for bt in hits:
                place(drums, pan(reverb(k_clap, 'room', 0.18)[:, 0] if False else k_clap, 0.0), t0 + bt * beat, 0.62)
                place(drums, to_stereo(k_snare), t0 + bt * beat, 0.25)
            if phrase_pos == 7:                         # snare roll into the next phrase
                for k in range(4):
                    place(drums, to_stereo(k_snare), t0 + (3 + k * 0.25) * beat, 0.12 + 0.05 * k)
        # ---- hats ----
        if cfg['hats'] == 'trap':
            step = beat / 4
            for k in range(16):
                tt = t0 + k * step
                v = 0.20 if k % 4 == 0 else (0.13 if k % 2 == 0 else 0.085)
                if sparse:
                    v *= 0.7
                place(drums, pan(k_hat, -0.25 + 0.5 * ((k % 4) / 3)), tt, v)
            if phrase_pos in (3, 7) and not sparse:     # trap roll (32nds / triplets) at the end of phrases
                for k in range(6):
                    place(drums, pan(k_hat, 0.3), t0 + 3 * beat + k * beat / 6, 0.10 + 0.02 * k)
            if phrase_pos % 2 == 1 and not sparse:
                place(drums, pan(k_hat_o, -0.2), t0 + 3.5 * beat, 0.12)
        elif cfg['hats'] == 'boom':
            for k in range(8):
                sw = swing * beat / 2 if k % 2 else 0.0
                place(drums, pan(k_hat, 0.2), t0 + k * beat / 2 + sw, 0.22 if k % 2 == 0 else 0.14)
            place(drums, pan(k_rim, -0.3), t0 + 1.75 * beat, 0.18)
        elif cfg['hats'] == 'lofi':
            for k in range(8):
                sw = 0.16 * beat if k % 2 else 0.0
                place(drums, pan(k_hat, 0.15), t0 + k * beat / 2 + sw, 0.16 if k % 2 == 0 else 0.10)
            place(drums, to_stereo(k_kick), t0, 0.5)
            place(drums, to_stereo(k_kick), t0 + 2.5 * beat, 0.4)
        # ---- war drums (taiko) for battle tracks, every 2 bars, plus a phrase-end fill ----
        if cfg.get('taiko') and not sparse and b % 2 == 0:
            place(drums, pan(taiko(), -0.15), t0, 0.42)
            if phrase_pos == 6:
                for k in range(3):
                    place(drums, pan(taiko(k + 1), 0.15), t0 + bar + (2 + k * 0.5) * beat, 0.30)
    # ---- soundfont layers ----
    parts = [p for p in (pad, pad2, lead, drone) if p is not None and p.notes]
    tonal = render(parts, duration=duration + 2.0, gain=0.55) if parts else np.zeros((n, 2), np.float32)
    tonal = lp(tonal, 7500 if not cfg.get('epic') else 9000)
    tonal = hp(tonal, 160)
    hats_hi = hp(drums, 5000)
    drums = hp(drums, 30) + hats_hi * 1.4          # brighter top end: hats and clap transients carry on phone speakers
    bass = lp(bass, 900)
    mix = drums * 1.25 * cfg.get("kit", 1.0) + bass * 0.24 + tonal * 2.2
    mix = reverb(mix, 'room', wet=0.08)[: n]
    out = mix[: n_of(duration)]
    peak = np.max(np.abs(out)) + 1e-9
    return (out / peak * 0.8).astype(np.float32)


def sting(name='outro', dur=6.5, seed=0):
    """Outro sting: punchy full beat for ~6.5 s with a 0.5 s fade (reference end screen)."""
    x = bed(name, dur + 0.6, seed=seed)
    n = n_of(dur)
    x = x[:n].copy()
    f = n_of(0.5)
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    return x
