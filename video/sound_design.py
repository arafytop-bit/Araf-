"""Sound design: event-driven synthesized SFX + original lo-fi music bed (sidechain-ducked) under the voice-over.
Everything is synthesized here (no samples). Only the audio is rebuilt; the rendered video stream is copied.

usage: PROD=<workdir> python3 sound_design.py <video_in.mp4> <video_out.mp4> [--no-bed]
reads  PROD/audio_master.wav (VO + stings + outro), PROD/words.json, PROD/stings.json, story.py (event timeline)
writes PROD/sfx.wav, PROD/bed.wav, PROD/mix.wav, PROD/sfx_events.json, <video_out.mp4>"""
import os, sys, json, math, subprocess, wave, re
import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(__file__))
SR = 48000
RNG = np.random.default_rng(11)
PROD = os.environ.get("PROD", "/tmp/claude-0/-home-user-Araf-/43d1b1f7-89db-58b4-84f7-4143c9fb35e5/scratchpad/prod")

def db(x): return 10 ** (x / 20)
def T(d): return np.arange(int(d * SR)) / SR
def noise(d): return RNG.standard_normal(int(d * SR))
def env(n, a, d): t = np.arange(n) / SR; return (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / max(d, 1e-4))
def sos_f(kind, f, order=2): return signal.butter(order, f, btype=kind, fs=SR, output="sos")
def bp(x, lo, hi, o=2): return signal.sosfilt(sos_f("band", [lo, min(hi, SR / 2 - 100)], o), x)
def hp(x, f, o=2): return signal.sosfilt(sos_f("high", f, o), x)
def lp(x, f, o=2): return signal.sosfilt(sos_f("low", f, o), x)
def peak(x, pdb): return x / (np.abs(x).max() + 1e-12) * db(pdb)
def fadeout(x, d=0.01):
    n = min(len(x), int(d * SR)); x = x.copy(); x[-n:] *= np.linspace(1, 0, n); return x
def chirp_phase(f): return 2 * np.pi * np.cumsum(f) / SR

def shaped_noise(d, fc_fn, bw_oct=1.0, nper=512):
    """Noise through a band whose centre follows fc_fn(u), u in [0,1] (STFT shaping) -> whooshes, swipes, rustles."""
    x = noise(d + 0.06)
    f, tt, Z = signal.stft(x, SR, nperseg=nper, noverlap=nper * 3 // 4)
    lf = np.log2(f + 1.0)
    for k, tk in enumerate(tt):
        fc = fc_fn(min(max(tk / d, 0.0), 1.0))
        Z[:, k] *= np.exp(-0.5 * ((lf - math.log2(fc)) / (bw_oct / 2)) ** 2)
    _, y = signal.istft(Z, SR, nperseg=nper, noverlap=nper * 3 // 4)
    return y[:int(d * SR)]

def bell(f, d, partials=((1, 1.0, 1.0), (2.0, 0.35, 0.55), (2.76, 0.45, 0.4), (5.4, 0.15, 0.2))):
    t = T(d); return sum(a * np.sin(2 * np.pi * f * r * t) * env(len(t), 0.001, d * dk * 0.35) for r, a, dk in partials)

# ------------------------------------------------------------------ SFX palette (mono, returns array; level set later)
def s_pop(p=1.0):
    t = T(0.14); f = 600 * p * (1 + 1.1 * np.exp(-t / 0.011)); ph = chirp_phase(f)
    y = np.sin(ph) * env(len(t), 0.0015, 0.045) + 0.22 * np.sin(2 * ph) * env(len(t), 0.0015, 0.025)
    c = hp(noise(0.004), 2500) * 0.25; y[:len(c)] += c; return y
def s_pop_char(p=1.0):
    t = T(0.2); f = 420 * p * (1 + 0.6 * np.exp(-t / 0.02)) * (1 + 0.02 * np.sin(2 * np.pi * 22 * t)); ph = chirp_phase(f)
    return np.sin(ph) * env(len(t), 0.002, 0.07) + 0.3 * np.sin(2 * ph) * env(len(t), 0.002, 0.05)
def s_cut():
    return shaped_noise(0.17, lambda u: 1400 * (4.0 ** u), 1.4) * np.sin(np.pi * np.linspace(0, 1, int(0.17 * SR))) ** 2
def s_whoosh(d=0.4):
    d = min(max(d, 0.22), 1.2); n = int(d * SR); u = np.linspace(0, 1, n)
    y = shaped_noise(d, lambda v: 350 * (7.0 ** math.sin(math.pi * min(v * 1.15, 1.0))), 1.3)
    return y * (np.sin(np.pi * u ** 0.8) ** 2)
def s_tick(kind="pencil"):
    if kind == "pencil": y = bp(noise(0.03), 2800, 8000) * env(int(0.03 * SR), 0.001, 0.008)
    elif kind == "chalk":
        y = bp(noise(0.05), 1300, 4800) * env(int(0.05 * SR), 0.002, 0.014) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 90 * T(0.05))))
    else:   # keyboard
        y = hp(noise(0.003), 3000) * 0.8; body = bp(noise(0.02), 700, 2200) * env(int(0.02 * SR), 0.0005, 0.005)
        y = np.concatenate([y, np.zeros(len(body) - len(y))]) + body
    return y
def s_stamp():
    t = T(0.38); f = 92 * (1 + 0.9 * np.exp(-t / 0.018)); body = np.sin(chirp_phase(f)) * env(len(t), 0.0008, 0.085)
    slap = bp(noise(0.035), 700, 6000) * env(int(0.035 * SR), 0.0004, 0.008)
    body[:len(slap)] += 0.7 * slap; return body
def s_impact():
    t = T(0.6); f = 118 * (0.4 + 0.6 * np.exp(-t / 0.06)); body = np.sin(chirp_phase(f)) * env(len(t), 0.001, 0.16)
    hit = lp(noise(0.08), 900) * env(int(0.08 * SR), 0.0005, 0.02); body[:len(hit)] += 0.9 * hit
    tail = lp(noise(0.6), 400) * env(len(t), 0.02, 0.18) * 0.25; return body + tail
def s_ding():
    a = bell(1046.5, 0.9); b = bell(1568.0, 0.9); y = np.zeros(int(1.0 * SR)); y[:len(a)] += a * 0.8; o = int(0.075 * SR); y[o:o + len(b)] += b[:len(y) - o]
    return y
def s_xmark():
    one = lambda: shaped_noise(0.09, lambda u: 2200 * (2.0 ** u), 1.0) * np.sin(np.pi * np.linspace(0, 1, int(0.09 * SR)))
    y = np.zeros(int(0.25 * SR)); a = one(); b = one(); y[:len(a)] += a; o = int(0.12 * SR); y[o:o + len(b)] += b[:len(y) - o]; return y
def s_circle():
    d = 0.45; y = shaped_noise(d, lambda u: 1800 + 900 * math.sin(2 * math.pi * 2 * u), 0.8)
    return y * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * T(d))) * np.sin(np.pi * np.linspace(0, 1, len(y))) ** 0.7
def s_highlight():
    d = 0.3; y = shaped_noise(d, lambda u: 3000 + 600 * u, 0.7); return y * np.sin(np.pi * np.linspace(0, 1, len(y)))
def s_chaching():
    cha = bp(noise(0.06), 2000, 9000) * env(int(0.06 * SR), 0.0005, 0.015)
    t = T(0.7); ching = sum(a * np.sin(2 * np.pi * f * t) * env(len(t), 0.001, dk) for f, a, dk in ((2480, 1, 0.28), (3910, 0.7, 0.2), (5590, 0.45, 0.14), (7120, 0.3, 0.1)))
    y = np.zeros(int(0.8 * SR)); y[:len(cha)] += cha; o = int(0.08 * SR); y[o:o + len(ching)] += ching[:len(y) - o] * 0.8; return y
def s_coin():
    t = T(0.45); return sum(a * np.sin(2 * np.pi * f * t) * env(len(t), 0.0005, dk) for f, a, dk in ((4186, 1, 0.12), (6120, 0.6, 0.08), (8040, 0.35, 0.05)))
def s_rise(d=0.8):
    d = min(max(d, 0.25), 2.5); t = T(d); f = 260 * (4.2 ** (t / d)) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t)); ph = chirp_phase(f)
    e = np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.08); return (np.sin(ph) + 0.2 * np.sin(2 * ph)) * e
def s_zip(up=True, side=False):
    d = 0.17; t = T(d); f = (520 * (3.3 ** (t / d))) if up else (1700 * (0.3 ** (t / d)))
    y = np.sin(chirp_phase(f)) * env(len(t), 0.004, 0.07)
    if side: y = 0.5 * y + shaped_noise(d, lambda u: 2000 * (2 ** u), 1.0) * np.sin(np.pi * np.linspace(0, 1, len(t)))
    return y
def s_balloon_pop():
    burst = noise(0.02) * env(int(0.02 * SR), 0.0002, 0.006); t = T(0.15); thump = np.sin(2 * np.pi * 130 * t) * env(len(t), 0.001, 0.035)
    thump[:len(burst)] += 1.3 * hp(burst, 600); return thump
def s_poof():
    d = 0.45; return lp(noise(d), 1300) * env(int(d * SR), 0.012, 0.12)
def s_gavel():
    knock = lambda: bp(noise(0.05), 450, 1600, 2) * env(int(0.05 * SR), 0.0005, 0.012) + 0.6 * np.sin(2 * np.pi * 310 * T(0.05)) * env(int(0.05 * SR), 0.0005, 0.018)
    y = np.zeros(int(0.3 * SR)); a = knock(); y[:len(a)] += a; o = int(0.14 * SR); y[o:o + len(a)] += knock() * 0.8; return y
def s_screech():
    d = 0.7; t = T(d); f = 2200 * (0.75 ** (t / d)) * (1 + 0.03 * np.sin(2 * np.pi * 27 * t))
    return (np.sin(chirp_phase(f)) * 0.6 + 0.4 * bp(noise(d), 1800, 4200)) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.2)
def s_wind(d=2.0):
    d = min(max(d, 0.8), 3.0); y = shaped_noise(d, lambda u: 320 + 380 * math.sin(math.pi * u), 1.6)
    return y * np.sin(np.pi * np.linspace(0, 1, len(y))) ** 1.5
def s_zap():
    d = 0.32; t = T(d); saw = signal.sawtooth(2 * np.pi * 96 * t) + 0.5 * signal.sawtooth(2 * np.pi * 191 * t)
    gate = (RNG.random(len(t) // 240 + 1) > 0.35).repeat(240)[:len(t)]; y = hp(saw * gate + 0.5 * noise(d) * gate, 250)
    return y * env(len(t), 0.002, 0.12)
def s_thunder():
    d = 1.6; crack = hp(noise(0.05), 1500) * env(int(0.05 * SR), 0.0005, 0.01); rum = lp(noise(d), 180, 4) * env(int(d * SR), 0.03, 0.5) * 3
    rum[:len(crack)] += crack; return rum
def s_snip():
    c = lambda: bp(noise(0.03), 4000, 11000) * env(int(0.03 * SR), 0.0003, 0.006) + 0.4 * np.sin(2 * np.pi * 6200 * T(0.03)) * env(int(0.03 * SR), 0.0003, 0.01)
    y = np.zeros(int(0.2 * SR)); a = c(); y[:len(a)] += a; o = int(0.09 * SR); y[o:o + len(a)] += c(); return y
def s_freeze():
    d = 0.6; t = T(d); y = np.zeros(len(t))
    for k in range(9):
        o = int(RNG.uniform(0, 0.35) * SR); f = RNG.uniform(3000, 6500); n = len(t) - o
        y[o:] += np.sin(2 * np.pi * f * np.arange(n) / SR) * env(n, 0.001, 0.08) * RNG.uniform(0.3, 1)
    cr = (RNG.random(len(t)) > 0.996) * RNG.standard_normal(len(t)); return y + 2.5 * hp(cr, 2000)
def s_lock():
    def c():
        body = bp(noise(0.03), 1000, 3000) * env(int(0.03 * SR), 0.0005, 0.006); cl = hp(noise(0.004), 2500); body[:len(cl)] += cl; return body
    y = np.zeros(int(0.15 * SR)); a = c(); y[:len(a)] += a; o = int(0.065 * SR); b = c(); y[o:o + len(b)] += b * 1.2; return y
def s_staple():
    y = s_stamp()[:int(0.2 * SR)] * 0.6; cl = s_lock(); y[:len(cl)] += cl * 0.8; return y
def s_click_ding():
    c = s_lock()[:int(0.05 * SR)]; dg = s_ding(); y = np.zeros(len(dg) + int(0.06 * SR)); y[:len(c)] += c; y[int(0.06 * SR):] += dg * 0.8; return y
def s_murmur(d=1.6):
    t = T(d); y = np.zeros(len(t))
    for k in range(7):
        am = np.clip(np.sin(2 * np.pi * RNG.uniform(3.5, 6) * t + RNG.uniform(0, 6)), 0, 1) ** 2
        lo = RNG.uniform(280, 500); y += bp(noise(d), lo, lo * 2.6) * am * RNG.uniform(0.5, 1)
    return y * np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.4)
def s_paper():
    d = 0.2; y = shaped_noise(d, lambda u: 2600 + 2500 * u, 1.3)
    grains = np.clip(RNG.standard_normal(len(y) // 200 + 1), 0, None).repeat(200)[:len(y)]
    return y * grains * np.sin(np.pi * np.linspace(0, 1, len(y))) ** 0.6
def s_flip():
    d = 0.07; return shaped_noise(d, lambda u: 2500 + 1500 * u, 1.2) * env(int(d * SR), 0.003, 0.02)
def s_inflate(d=1.0):
    d = min(max(d, 0.5), 1.6); t = T(d); f = 380 * (2.0 ** (t / d)) * (1 + 0.04 * np.sin(2 * np.pi * 17 * t))
    return np.sin(chirp_phase(f)) * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.1)
def s_thump():
    t = T(0.25); return np.sin(chirp_phase(140 * (1 + 0.5 * np.exp(-t / 0.02)))) * env(len(t), 0.001, 0.06)

SFX = {"pop": s_pop, "pop_small": lambda p=1.0: s_pop(p * 1.25), "pop_char": s_pop_char, "cut": s_cut, "whoosh": s_whoosh, "stamp": s_stamp,
       "impact": s_impact, "ding": s_ding, "xmark": s_xmark, "circle": s_circle, "highlight": s_highlight, "chaching": s_chaching,
       "coin": s_coin, "rise": s_rise, "zip_up": lambda: s_zip(True), "zip_down": lambda: s_zip(False), "zip_side": lambda: s_zip(True, True),
       "balloon_pop": s_balloon_pop, "poof": s_poof, "gavel": s_gavel, "screech": s_screech, "wind": s_wind, "zap": s_zap,
       "thunder": s_thunder, "snip": s_snip, "freeze": s_freeze, "lock": s_lock, "staple": s_staple, "click_ding": s_click_ding,
       "murmur": s_murmur, "paper": s_paper, "flip": s_flip, "inflate": s_inflate, "thump": s_thump}
# peak level (dBFS, before final normalisation; voice peaks ~ -3 dBFS) and priority (higher wins collisions)
LEVEL = {"pop": -21, "pop_small": -24, "pop_char": -21, "cut": -26, "whoosh": -23, "tick_pencil": -29, "tick_chalk": -27, "tick_keys": -27, "stamp": -14, "impact": -13, "ding": -22, "xmark": -20, "circle": -23, "highlight": -25, "chaching": -19, "coin": -20, "rise": -24, "zip_up": -21, "zip_down": -21, "zip_side": -22, "balloon_pop": -14, "poof": -21, "gavel": -16, "screech": -21, "wind": -28, "zap": -23, "thunder": -19, "snip": -22, "freeze": -23, "lock": -20, "staple": -18, "click_ding": -19, "murmur": -31, "paper": -23, "flip": -26, "inflate": -27, "thump": -20}
PRIO = {"impact": 10, "stamp": 9, "balloon_pop": 9, "screech": 8, "thunder": 8, "gavel": 8, "chaching": 7, "click_ding": 7, "ding": 6,
        "xmark": 6, "staple": 6, "lock": 6, "snip": 6, "freeze": 6, "zap": 6, "coin": 5, "poof": 5, "zip_up": 4, "zip_down": 4, "zip_side": 4,
        "circle": 4, "highlight": 4, "paper": 3, "pop_char": 3, "pop": 2, "pop_small": 1, "cut": 1, "whoosh": 3, "wind": 3, "murmur": 2,
        "rise": 4, "flip": 2, "inflate": 3, "thump": 5}

APPEAR = {"person": "pop_char", "note": "pop_small", "stamp": "stamp", "xmark_a": "xmark", "check_a": "ding", "circle_a": "circle",
          "money_bag": "chaching", "cash": "chaching", "dollar": "chaching", "coin": "coin", "arrow_up": "zip_up", "arrow_down": "zip_down",
          "arrow_r": "zip_side", "poof": "poof", "burst": "impact", "gavel": "gavel", "car": "screech", "tumbleweed": "wind", "bolt": "zap",
          "storm": "thunder", "scissors": "snip", "ice_block": "freeze", "padlock": "lock", "stapler": "staple", "crowd": "murmur",
          "doc": "paper", "bill": "paper", "envelope": "paper", "papers": "paper", "quote_card": "paper", "calendar": "paper",
          "trophy": "ding", "label": None, "hline": None, "wires": None, "qmarks": "pop_small", "check": "ding"}

# ------------------------------------------------------------------ events from the storyboard
def extract_events(B):
    ev = []
    def add(t, kind, x=960, **kw): ev.append(dict(t=round(float(t), 4), kind=kind, pan=max(-0.6, min(0.6, (x - 960) / 960 * 0.7)), **kw))
    scenes = sorted(B.scenes, key=lambda s: s.t0)
    chapter_ts = [c["t_insert"] for c in json.load(open(f"{PROD}/stings.json"))["chapters"]]
    for si, sc in enumerate(scenes):
        if si > 0 and not any(abs(sc.t0 - c) < 0.2 for c in chapter_ts): add(sc.t0, "cut")
        for el in sc.els:
            k, b, t0 = el.kind, el.base, el.t0
            x = b.get("x", 960)
            if not x and "x0" in b: x = (b["x0"] + b.get("x1", b["x0"])) / 2
            typed = "chars" in b and b.get("chars") == 0
            if k == "hero":
                big = (b.get("color") == "#E4141C" and b.get("size", 0) >= 140) or b.get("size", 0) >= 200
                snd = None if typed else ("impact" if big else "pop")
            else:
                snd = APPEAR.get(k, "pop")
            if typed: snd = None if k not in ("browser", "comment_form", "chalkboard") else "pop"
            if snd: add(t0, snd, x)
            prev = dict(b)
            for (tk, dur, p) in el.keys:
                if "chars" in p and dur > 0 and k != "label":
                    n0 = int(prev.get("chars") or 0); n1 = int(p["chars"])
                    tick = "tick_chalk" if k == "chalkboard" else ("tick_keys" if k in ("browser", "comment_form") else "tick_pencil")
                    if n1 > n0:
                        for i in range(n1 - n0):
                            add(tk + dur * (i + 0.5) / (n1 - n0), tick, x)
                if "p" in p and dur > 0 and k in ("bar_chart", "line_chart"): add(tk, "rise", x, dur=dur)
                if "lit" in p and dur > 0:
                    n = int(p["lit"]) - int(prev.get("lit") or 0)
                    for i in range(max(0, n)): add(tk + dur * i / max(1, n), "pop_small", x, pitch=1.0 + 0.04 * i)
                if p.get("popped"): add(tk, "balloon_pop", x)
                if p.get("ghost"): add(tk, "poof", x)
                if "stamp_txt" in p: add(tk, "stamp", x)
                if "checks" in p and len(p["checks"]) > len(prev.get("checks") or ()): add(tk, "ding", x)
                if p.get("show_votes"): [add(tk + 0.06 * i, "pop_small", x, pitch=1 + 0.05 * i) for i in range(9)]
                if p.get("pressed"): add(tk, "click_ding", x)
                if "hi" in p: add(tk, "highlight", x)
                if "strike" in p: add(tk, "xmark", x)
                if "explode" in p or "n" in p or "pts2" in p or "price_on" in p or "money" in p or "cut" in p or "on" in p: add(tk, "pop", x)
                if "heavy" in p: add(tk, "thump", x)
                if "demand" in p: add(tk, "whoosh", x, dur=max(dur, 0.3))
                if k == "calendar" and "big" in p: add(tk, "flip", x)
                if k == "price_tag" and "text" in p: add(tk, "chaching", x)
                if k == "coin" and "text" in p: add(tk, "coin", x)
                if "mouth" in p and k == "chip": add(tk, "pop_small", x)
                if "wipe" in p and dur > 0: add(tk, "whoosh", x, dur=dur)
                if ("x" in p or "y" in p) and dur >= 0.25:
                    dist = math.hypot(p.get("x", prev.get("x", 0)) - prev.get("x", 0), p.get("y", prev.get("y", 0)) - prev.get("y", 0))
                    if dist / dur > 180: add(tk, "wind" if k == "tumbleweed" else "whoosh", x, dur=dur)
                if "s" in p and dur > 0:
                    s0 = prev.get("s", 1.0) or 1.0
                    if k == "balloon" and p["s"] > s0: add(tk, "inflate", x, dur=dur)
                    elif p["s"] < s0 * 0.8 and dur <= 1.4: add(tk, "whoosh", x, dur=dur)
                prev.update(p)
    ev.sort(key=lambda e: e["t"])
    return ev

def resolve(ev):
    """Collision rules: one strong sound per moment; a cut swish replaces simultaneous plain pops; rate-limit pops & cha-chings."""
    out = []; i = 0
    while i < len(ev):
        j = i
        while j + 1 < len(ev) and ev[j + 1]["t"] - ev[i]["t"] < 0.045 and not ev[j + 1]["kind"].startswith("tick"): j += 1
        grp = [e for e in ev[i:j + 1]]
        ticks = [e for e in grp if e["kind"].startswith("tick")]; grp = [e for e in grp if not e["kind"].startswith("tick")]
        if grp:
            grp.sort(key=lambda e: -PRIO.get(e["kind"], 1))
            keep = [grp[0]]
            special = [e for e in grp[1:] if PRIO.get(e["kind"], 1) >= 5 and e["kind"] != keep[0]["kind"]]
            if special: keep.append(special[0])
            if keep[0]["kind"] in ("pop", "pop_small", "pop_char") and any(e["kind"] == "cut" for e in grp):
                keep = [e for e in grp if e["kind"] == "cut"][:1]
            out += keep
        out += ticks
        i = j + 1
    out.sort(key=lambda e: e["t"])
    res = []; last = {}
    for e in out:
        k = e["kind"]
        if k == "chaching" and e["t"] - last.get("chaching", -9) < 2.0: e = dict(e, kind="coin")
        if k in ("pop", "pop_small", "pop_char") and e["t"] - last.get("pop", -9) < 0.07: continue
        if k == "cut" and e["t"] - last.get("any", -9) < 0.12: continue
        if k.startswith("tick") and e["t"] - last.get("tick", -9) < 0.025: continue
        res.append(e); last[e["kind"]] = e["t"]; last["any"] = e["t"]
        if k.startswith("pop"): last["pop"] = e["t"]
        if k.startswith("tick"): last["tick"] = e["t"]
    # pitch-step successive pops (staggers sound like a little cascade)
    run = 0; lastp = -9
    for e in res:
        if e["kind"].startswith("pop"):
            run = run + 1 if e["t"] - lastp < 0.35 else 0; lastp = e["t"]
            e.setdefault("pitch", 1.0 + 0.055 * min(run, 8))
    return res

def place_stereo(buf, y, t, pan):
    i = int(t * SR); n = min(len(y), len(buf) - i)
    if n <= 0 or i < 0: return
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:i + n, 0] += y[:n] * l * 1.4142; buf[i:i + n, 1] += y[:n] * r * 1.4142

def build_sfx(events, total):
    buf = np.zeros((int(total * SR) + SR, 2), np.float32); cache = {}
    for e in events:
        k = e["kind"]; lvl = LEVEL.get(k, -26) + RNG.uniform(-1.5, 1.0)
        if k.startswith("tick"):
            y = s_tick(k.split("_")[1]); y = peak(y, lvl + RNG.uniform(-3, 0))
        elif k in ("whoosh", "rise", "wind", "inflate", "murmur"):
            y = peak(SFX[k](e.get("dur", 0.4)) if k != "murmur" else SFX[k](), lvl)
        elif k in ("pop", "pop_small", "pop_char"):
            y = peak(SFX[k](e.get("pitch", 1.0) * RNG.uniform(0.94, 1.06)), lvl)
        else:
            if k not in cache or RNG.random() < 0.5: cache[k] = SFX[k]()
            y = peak(cache[k], lvl)
        place_stereo(buf, fadeout(y, 0.006), e["t"], e["pan"])
    return buf

# ------------------------------------------------------------------ music bed (original lo-fi)
BPM = 84.0; BEAT = 60 / BPM; BAR = 4 * BEAT
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
PROG = {"main":    [[57, 60, 64, 67, 71], [53, 57, 60, 64, 67], [48, 55, 59, 64], [55, 59, 62, 66]],     # Am9  Fmaj9  Cmaj7  G(maj7)
        "intro":   [[57, 60, 64, 67], [57, 60, 64, 67], [53, 57, 60, 64], [52, 56, 59, 62]],         # Am7 Am7 Fmaj7 E7
        "flash":   [[50, 53, 57, 60], [55, 59, 62, 65], [48, 52, 55, 59], [57, 60, 64, 67]],         # Dm7 G7 Cmaj7 Am7
        "tension": [[57, 60, 64], [53, 57, 60, 65], [50, 53, 57, 60], [52, 56, 59, 62]],             # Am F Dm7 E7
        "bright":  [[48, 52, 55, 59], [55, 59, 62, 64], [57, 60, 64, 67], [53, 57, 60, 64]]}         # Cmaj7 G6 Am7 Fmaj7
MOOD = {"1 · Cold open": ("intro", False), "2 · Stakes and setup": ("main", True), "3 · The engine": ("main", True),
        "5 · The history parallel": ("flash", False), "6 · The escalation": ("tension", True), "7 · The payoff": ("bright", True),
        "8 · The ask": ("bright", True), "9 · The last line": ("bright", True)}

def rhodes(f, d, vel, wow=False):
    t = T(d); fm = 1.0 + (0.0025 * np.sin(2 * np.pi * 0.55 * t) if wow else 0)
    ph = chirp_phase(f * fm * np.ones(len(t))); mod = 1.1 * np.exp(-t / 0.22) * np.sin(ph)
    y = np.sin(ph + mod) + 0.12 * np.sin(2 * ph)
    e = (1 - np.exp(-t / 0.006)) * (0.55 * np.exp(-t / 0.4) + 0.45 * np.exp(-t / 2.8)); r = min(len(t), int(0.3 * SR)); e[-r:] *= np.linspace(1, 0, r)
    return y * e * (1 + 0.07 * np.sin(2 * np.pi * 4.3 * t)) * vel

def build_bed(total, sections, end_t):
    buf = np.zeros((int(total * SR) + SR, 2), np.float32); drums = np.zeros_like(buf)
    nbars = int(end_t / BAR) + 1
    def mood_at(t):
        cur = None
        for name, st in sections:
            if st <= t + 1e-6: cur = name
        return MOOD.get(cur, ("main", True))
    for bi in range(nbars):
        t0 = bi * BAR; mood, drum_on = mood_at(t0 + 0.01); wow = mood == "flash"
        chord = PROG[mood][bi % 4]
        for strike, (off, dur, vel) in enumerate(((0.0, BAR * 1.05, 0.5), (2.5 * BEAT, 1.5 * BEAT, 0.28))):
            for ni, n in enumerate(chord):
                y = rhodes(midi(n), dur + 0.3, vel * RNG.uniform(0.8, 1.0) / len(chord) * 3, wow)
                place_stereo(buf, y, t0 + off + ni * 0.012 + RNG.uniform(0, 0.006), (-0.25 + 0.5 * ni / max(1, len(chord) - 1)))
        root = midi(chord[0] - 24 if chord[0] >= 52 else chord[0] - 12)
        for off, dur in ((0.0, 1.6 * BEAT), (2.5 * BEAT, 0.9 * BEAT), (3.5 * BEAT, 0.45 * BEAT)):
            t = T(dur); y = (np.sin(2 * np.pi * root * t) + 0.25 * np.sin(4 * np.pi * root * t)) * (1 - np.exp(-t / 0.01)) * np.exp(-t / 0.9)
            place_stereo(buf, fadeout(y, 0.04) * 0.42, t0 + off, 0.0)
        if drum_on:
            for b4 in range(4):
                tb = t0 + b4 * BEAT
                if b4 in (0, 2):
                    tt = T(0.3); k = np.sin(chirp_phase(52 * (1 + 1.6 * np.exp(-tt / 0.03)))) * env(len(tt), 0.001, 0.09)
                    place_stereo(drums, k * 0.55, tb, 0.0)
                if b4 in (1, 3):
                    sn = bp(noise(0.16), 1200, 5200) * env(int(0.16 * SR), 0.001, 0.045) * 0.22 + np.sin(2 * np.pi * 190 * T(0.16)) * env(int(0.16 * SR), 0.001, 0.03) * 0.18
                    place_stereo(drums, sn, tb, 0.05)
                for h in (0, 1):
                    th = tb + h * BEAT * 0.58
                    hat = hp(noise(0.04), 7000) * env(int(0.04 * SR), 0.0005, 0.012) * (0.10 if h == 0 else 0.07) * RNG.uniform(0.7, 1.0)
                    place_stereo(drums, hat, th, 0.25)
    # vinyl crackle (very sparse)
    nclick = int(total * 5); pos = RNG.integers(0, len(buf) - 10, nclick)
    cr = np.zeros(len(buf)); cr[pos] = RNG.standard_normal(nclick) * RNG.uniform(0.2, 1, nclick); cr = bp(cr, 1000, 7000) * 0.05
    bed = buf + drums * 0.8; bed[:, 0] += cr; bed[:, 1] += cr
    # tone: warm low-pass; tape-ish flashback (extra low-pass) handled by mood-wise mixing
    warm = np.stack([lp(bed[:, c], 5500, 2) for c in (0, 1)], 1)
    dark = np.stack([lp(bed[:, c], 2000, 2) for c in (0, 1)], 1)
    fl = np.zeros(len(bed))
    for name, st in sections:
        if MOOD.get(name, ("", 0))[0] == "flash":
            nxt = [s for n2, s in sections if s > st]; en = min(nxt) if nxt else total
            a, b_ = int(st * SR), int(en * SR); fl[a:b_] = 1.0
    fl = np.convolve(fl, np.ones(SR // 2) / (SR // 2), mode="same")
    bed = warm * (1 - fl[:, None]) + dark * fl[:, None]
    # small stereo reverb
    ir_n = int(1.6 * SR); tt = np.arange(ir_n) / SR
    irs = [lp(RNG.standard_normal(ir_n), 4000) * np.exp(-tt / 0.45) for _ in (0, 1)]
    wet = np.stack([signal.oaconvolve(bed[:, c], irs[c] / np.abs(irs[c]).sum() * 40, mode="full")[:len(bed)] for c in (0, 1)], 1)
    bed = np.tanh((bed + 0.22 * wet) * 1.2) / 1.2
    return bed

def vo_envelope(vo, total):
    """0..1 'voice active' curve (attack 30 ms, release 350 ms) from the VO track."""
    m = vo.mean(1); hop = int(0.01 * SR); k = len(m) // hop
    e = 20 * np.log10(np.sqrt((m[:k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-9)
    act = np.clip((e + 48) / 14, 0, 1)
    sm = np.zeros(k); a, r = 1 - math.exp(-1 / 3), 1 - math.exp(-1 / 35)
    for i in range(1, k):
        sm[i] = sm[i - 1] + (a if act[i] > sm[i - 1] else r) * (act[i] - sm[i - 1])
    g = np.interp(np.arange(len(m)) / hop, np.arange(k), sm)
    return g

def read(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, w.getnchannels())

def write(p, x):
    y = (np.clip(x, -1, 1) * 32767).astype(np.int16); w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()

def lufs(p):
    s = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", s)[-1]); pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", s)[-1]); return I, pk

def main():
    vin, vout = sys.argv[1], sys.argv[2]; no_bed = "--no-bed" in sys.argv
    import story
    B = story.build()
    vo = read(f"{PROD}/audio_master.wav"); total = len(vo) / SR
    S = json.load(open(f"{PROD}/stings.json")); W = json.load(open(f"{PROD}/words.json"))
    events = resolve(extract_events(B))
    json.dump(events, open(f"{PROD}/sfx_events.json", "w"))
    from collections import Counter
    print("sfx events:", len(events), dict(Counter(e["kind"] for e in events).most_common()))
    sfx = build_sfx(events, total)[:len(vo)]
    duck = vo_envelope(vo, total)[:len(vo)]
    sfx *= db(-3.0 * duck)[:, None]          # light ducking for intelligibility
    write(f"{PROD}/sfx.wav", sfx)
    mix = vo.copy() + sfx
    if not no_bed:
        sections = []
        for w in W:
            if not sections or sections[-1][0] != w["sec"]: sections.append((w["sec"], w["s"]))
        bed_end = S["endcard_start"]
        bed = build_bed(total, sections, bed_end)[:len(vo)]
        write(f"{PROD}/bed_raw.wav", bed / (np.abs(bed).max() + 1e-9) * 0.5)
        I_raw, _ = lufs(f"{PROD}/bed_raw.wav"); g = db(-27.0 - I_raw) * 0.5 / (np.abs(bed).max() + 1e-9)
        bed = bed * g
        gain = db(-8.0 * duck)                              # sidechain: -8 dB under speech
        t = np.arange(len(bed)) / SR
        for c in S["chapters"]:                             # drop out for chapter stings
            a, b_ = c["t_insert"] - 0.05, c["t_insert"] + c["gap"] - 0.1
            gain *= 1 - np.clip(np.minimum((t - a) / 0.12, (b_ - t) / 0.25), 0, 1)
        gain *= np.clip(t / 1.2, 0, 1) * np.clip((bed_end - t) / 2.5, 0, 1)    # fade in / fade out before end card
        bed *= gain[:, None]
        write(f"{PROD}/bed.wav", bed)
        mix += bed
    write(f"{PROD}/mix_pre.wav", mix * 0.9)
    I, pk = lufs(f"{PROD}/mix_pre.wav"); corr = -14.0 - I
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{PROD}/mix_pre.wav", "-af", f"volume={corr:.2f}dB,alimiter=limit=0.85:attack=1:release=60:level=false",
                    "-ar", str(SR), "-c:a", "pcm_s16le", f"{PROD}/mix.wav"], check=True)
    I2, pk2 = lufs(f"{PROD}/mix.wav"); print(f"mix: {I2:.1f} LUFS, peak {pk2:.1f} dBFS")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vin, "-i", f"{PROD}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", vout], check=True)
    print("wrote", vout)

if __name__ == "__main__":
    main()
