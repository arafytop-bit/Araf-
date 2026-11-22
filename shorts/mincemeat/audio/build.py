# Sound for "The Agent With No Pulse": the user's voice (unchanged) + an original spy-comedy score (pizzicato,
# vibes, brushes, a fife-and-drum gag, comic tuba for Hitler, a sad trombone, a warm ending) ducked under the voice
# + synthesized SFX on the picture's frames (src/videos/mincemeat/story.ts / cast.ts).
# Standard mix: music +3 dB, SFX -6 dB (relative to the house levels below), voice untouched.
# Writes mix.wav (48 kHz stereo 24-bit, exactly TOTAL / 30 s), stems and cues.md.
import os, json
import numpy as np
from dsp import (SR, ns, tt, rng, lp, hp, bp, colored, smooth_noise, fades, phase, pan, st, place, make_ir, convolve_st,
                 integrated, true_peak, read_wav, write_wav, dbg, shape, peq)
from instruments import m2f, brass, glock, vibes, musicbox, triangle, fife, snare, snare_roll, cymbal, timpani, brush, pluck, pad
from sfx_gen import whoosh, splash_big, hammer_hit, bird_chirps, breeze, water_bed, bubbles, clink, vox, whoa, stroll_step

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, TOTAL = 30, 2650
DUR = TOTAL / FPS
N = ns(DUR)
F = lambda f: f / FPS
WORDS = json.load(open(os.path.join(HERE, "..", "voice", "words.json")))
CUES = []


def log_cue(t, name, desc):
    CUES.append((t, name, desc))


# ================================================================ voice
def load_voice():
    v, sr = read_wav(os.path.join(HERE, "..", "voice", "voice.wav"))
    v = v.mean(axis=0)
    assert sr == 24000, sr
    from scipy.signal import resample_poly
    v = resample_poly(v, 2, 1)  # 24 kHz -> 48 kHz
    out = np.zeros(N)
    out[: min(N, len(v))] = v[:N]
    return st(out)


# ================================================================ music
class Bus:
    def __init__(self):
        self.x = np.zeros((2, N))

    def add(self, y, t, p=0.0, g=1.0):
        y = np.asarray(y, float)
        place(self.x, pan(y, p) if y.ndim == 1 else y, t, g)


BPM = 108
BEAT = 60 / BPM
DM = [62, 65, 69]            # D minor
A7 = [57, 61, 64, 67]
GM = [55, 58, 62]
BB = [58, 62, 65]
DMAJ = [62, 66, 69]
GMAJ = [55, 59, 62]
AMAJ = [57, 61, 64]


def sneak(b, r, t0, t1, root_seq=(38, 45, 41, 45), vib=True, vel=0.75):
    """spy pizzicato walk: bass plucks on every beat, brushes on 2 and 4, vibes stabs on the and-of-4"""
    t, k = t0, 0
    while t < t1 - 0.05:
        n = root_seq[k % len(root_seq)]
        b.add(pluck(m2f(n), vel, r, 0.7, 0.35), t, -0.15, 0.9)
        if k % 2 == 1:
            b.add(brush(0.35, r, 0.3), t, 0.3, 0.6)
        if vib and k % 4 == 3:
            for m in DM:
                b.add(vibes(m2f(m + 12), 0.28, r, 0.5, damp=0.25), t + BEAT / 2, 0.25, 0.5)
        t += BEAT; k += 1


def tiptoe(b, r, t0, notes, vel=0.5, inst="glock"):
    """melody line: list of (beat offset, midi, beats)"""
    for off, m, d in notes:
        fn = glock if inst == "glock" else vibes if inst == "vibes" else musicbox
        b.add(fn(m2f(m), vel, r, max(0.4, d * BEAT * 1.4)), t0 + off * BEAT, 0.2, 0.55)


THEME = [(0, 74, 0.5), (0.5, 77, 0.5), (1, 76, 0.5), (1.5, 74, 1.5), (4, 74, 0.5), (4.5, 77, 0.5), (5, 81, 0.5), (5.5, 80, 1.5),
         (8, 79, 0.5), (8.5, 76, 0.5), (9, 77, 0.5), (9.5, 74, 1.5), (12, 73, 0.5), (12.5, 74, 0.5), (13, 76, 1.0), (14, 69, 1.5)]


def oompah(b, r, t0, t1, chords, vel=0.6):
    t, k = t0, 0
    while t < t1 - 0.05:
        ch = chords[(k // 2) % len(chords)]
        if k % 2 == 0:
            b.add(brass(m2f(ch[0] - 12), BEAT * 0.6, vel, r, "tuba"), t, -0.1, 0.9)
        else:
            for m in ch[1:]:
                b.add(brass(m2f(m), BEAT * 0.35, vel * 0.5, r, "stab"), t, 0.2, 0.35)
        t += BEAT; k += 1


def fife_band(b, r, t0, t1):
    """the tiny marching band crossing the map: fife tune + snare + bass drum, 2 steps/s"""
    tune = [74, 76, 77, 79, 81, 79, 77, 76, 74, 76, 77, 74, 72, 74, 69, 69]
    step = 0.5
    t, k = t0, 0
    while t < t1 - 0.1:
        b.add(fife(m2f(tune[k % len(tune)] + 12), step * 0.85, 0.42, r), t, 0.1, 0.55)
        b.add(snare(0.45 if k % 2 else 0.6, r, 0.2, 1.3), t, -0.1, 0.55)
        if k % 2 == 0:
            b.add(timpani(m2f(38), 0.35, r, 0.5), t, 0, 0.5)
        t += step; k += 1


def roll(b, r, t0, t1, v0, v1):
    for t, v in snare_roll(t0, t1, v0, v1, r):
        b.add(snare(v, r, 0.18, 1.1, buzz=True), t, 0.0, 0.5)


def sad_trombone(b, r, t0):
    for i, (m, d) in enumerate([(58, 0.45), (57, 0.45), (56, 0.45), (55, 1.4)]):
        b.add(brass(m2f(m - 12), d, 0.6, r, "soft", scoop=-30, fall=(-1.0 if i == 3 else 0.0)), t0 + i * 0.47, 0.0, 1.0)
    log_cue(t0, "music", "sad trombone (dead and still in debt)")


def build_music():
    b, r = Bus(), rng(7)
    words = {w["s"]: w["w"] for w in WORDS}
    # hook (0-7.3): sneak + theme
    sneak(b, r, 0.0, 7.3)
    tiptoe(b, r, 0.0, THEME[:12], 0.4, "vibes")
    # Hitler (7.3-9.8): comic tuba
    oompah(b, r, 7.33, 9.75, [DM, A7], 0.55)
    b.add(cymbal(0.35, r, 1.5), F(220), 0, 0.5)
    # the plan (9.8-15.0): sneak + glock theme
    sneak(b, r, 9.75, 15.0)
    tiptoe(b, r, 9.75, THEME[:8], 0.38)
    # marching band gag (15.0-19.2)
    fife_band(b, r, F(451), F(577))
    # officers / the plan (19.2-33.7)
    sneak(b, r, F(577), 33.6, (38, 45, 43, 45))
    tiptoe(b, r, F(577), THEME, 0.36)
    tiptoe(b, r, F(679) + 4 * BEAT, THEME[:12], 0.34, "vibes")
    roll(b, r, F(679) - 0.95, F(679) - 0.05, 0.1, 0.5)  # roll into "Get a dead body"
    # Glyndwr (33.7-38.9): bare music box, minor
    for i, (m, d) in enumerate([(74, 1), (72, 1), (70, 2), (69, 1), (67, 1), (69, 2)]):
        b.add(musicbox(m2f(m), 0.4, r, d * BEAT * 1.6), 33.75 + i * BEAT * 1.2, 0.1, 0.6)
    b.add(pad([m2f(m) for m in [50, 57, 62, 65]], 5.0, 0.22, r, att=1.0, rel=1.0, warm=700), 33.75, 0, 1.0)
    # fake life (38.9-51.5): lighter sneak in F major-ish + glock
    sneak(b, r, 38.95, 51.4, (41, 48, 46, 48))
    tiptoe(b, r, 38.95, [(o, m + 3, d) for o, m, d in THEME], 0.36)
    tiptoe(b, r, 38.95 + 16 * BEAT, [(o, m + 3, d) for o, m, d in THEME[:8]], 0.34)
    # dead and still in debt
    sad_trombone(b, r, F(1546) + 0.05)
    # sea at dawn (53.5-59.9): pad + soft timpani swell
    b.add(pad([m2f(m) for m in [50, 57, 62, 66, 69]], 6.5, 0.24, r, att=1.5, rel=1.5, warm=900), 53.5, 0, 1.0)
    b.add(timpani(m2f(38), 0.45, r, 2.5), F(1700), 0, 0.7)
    # Germans copy / letters (59.9-67.5): sneak again with snare ticks
    sneak(b, r, 59.95, 67.45, (38, 45, 41, 45))
    tiptoe(b, r, 59.95, THEME[:12], 0.36, "vibes")
    # would Hitler bite (67.5-70.7): tuba suspense + hit on "whole"
    for i, m in enumerate([38, 39, 38, 39, 38, 39]):
        b.add(brass(m2f(m), BEAT * 0.45, 0.45, r, "tuba"), F(2024) + i * BEAT * 0.75, 0, 0.8)
    b.add(cymbal(0.6, r, 2.0), F(2093), 0, 0.6); b.add(timpani(m2f(38), 0.8, r, 2.0), F(2093), 0, 0.9)
    # reinforcements (70.7-73.2): oompah march; "Sicily got none" (73.2): stop
    oompah(b, r, F(2121), F(2195), [DM, A7, DM, GM], 0.6)
    roll(b, r, F(2121), F(2190), 0.2, 0.45)
    # grave (75.1-83.1): warm D major pad + vibes theme slowly
    b.add(pad([m2f(m) for m in [50, 57, 62, 66]], 8.4, 0.24, r, att=1.6, rel=1.4, warm=900), F(2254), 0, 1.0)
    for i, (m, d) in enumerate([(74, 2), (78, 2), (76, 2), (74, 3), (71, 2), (73, 2), (74, 4)]):
        b.add(vibes(m2f(m), 0.42, r, d * BEAT * 1.5), F(2254) + 0.3 + i * BEAT * 2.0, 0.15, 0.6)
    # ending (83.1-88.3): theme in D major, bloom, final chord
    sneak(b, r, F(2492), F(2596), (38, 45, 42, 45), vib=False, vel=0.6)
    tiptoe(b, r, F(2492), [(o, m + (4 if m in (77, 80) else 0), d) for o, m, d in THEME[:6]], 0.4)
    b.add(pad([m2f(m) for m in [50, 57, 62, 66, 69, 74]], 3.2, 0.3, r, att=0.6, rel=1.6, warm=1400), F(2596), 0, 1.0)
    for m in [62, 66, 69, 74]:
        b.add(glock(m2f(m + 12), 0.45, r, 2.4), F(2620), 0.2, 0.6)
    b.add(cymbal(0.35, r, 2.6), F(2596), 0, 0.45)
    y = b.x
    ir = make_ir(1.1, 3, hf=0.7)
    y = y + 0.18 * convolve_st(y, ir)[:, :N]
    return y


# ================================================================ SFX
def buzz(dur, r):
    t = tt(dur)
    f0 = 210 + 25 * smooth_noise(len(t), r, 3.0)
    saw = np.sign(np.sin(phase(f0))) * 0.5 + np.sin(2 * phase(f0)) * 0.3
    am = 0.6 + 0.4 * smooth_noise(len(t), r, 6.0)
    return fades(bp(saw, 300, 4000, 1) * am * 0.5, 0.05, 0.2)


def boing(r, f0=180, dur=0.7):
    t = tt(dur)
    f = f0 * (1 + 0.35 * np.sin(TAU_ * 9 * t) * np.exp(-t / 0.25)) * (1 + 0.6 * t)
    return fades(np.sin(phase(f)) * np.exp(-t / 0.3) * 0.8, 0.002, 0.1)


TAU_ = 2 * np.pi


def poof(r, dur=0.55):
    t = tt(dur)
    nz = colored(len(t), r, 1.0)
    return fades(lp(nz, 900) * np.exp(-t / 0.14) * (1 - np.exp(-t / 0.01)) * 1.4, 0.0, 0.1)


def paper(r, dur=0.25, bright=3000):
    t = tt(dur)
    nz = r.standard_normal(len(t))
    am = np.clip(smooth_noise(len(t), r, 40.0), 0, None)
    return fades(bp(nz, 1200, bright + 3000, 1) * am * np.exp(-t / (dur * 0.5)) * 0.6, 0.002, 0.05)


def slap(r):
    t = tt(0.18)
    nz = r.standard_normal(len(t))
    return fades((bp(nz, 500, 5000, 1) * np.exp(-t / 0.012) + np.sin(phase(140)) * np.exp(-t / 0.03) * 0.5), 0, 0.05)


def scratch(r, dur):
    t = tt(dur)
    nz = r.standard_normal(len(t))
    am = 0.5 + 0.5 * np.abs(np.sin(TAU_ * 7 * t))
    return fades(bp(nz, 2500, 7000, 1) * am * 0.35, 0.01, 0.05)


def click(r):
    t = tt(0.09)
    return fades(bp(r.standard_normal(len(t)), 1500, 9000, 1) * np.exp(-t / 0.006) + np.sin(phase(2400)) * np.exp(-t / 0.01) * 0.4, 0, 0.02)


def flash_whine(r):
    t = tt(0.7)
    return fades(np.sin(phase(3000 + 2500 * t)) * np.exp(-t / 0.25) * 0.15, 0.01, 0.2)


def quack(r):
    t = tt(0.24)
    n = len(t)
    f0 = 420 * (1 - 0.25 * t / 0.24)
    forms = np.tile(np.array([700, 1200, 2600, 3400], float), (n, 1))
    amp = np.sin(np.pi * t / 0.24) ** 0.6
    y = vox(f0, forms, amp, r, scale=1.0, tilt=0.6, breath=0.3)
    return fades(peq(y, 1500, 9, 2.0) * 0.4, 0.003, 0.03)


def reel(r, dur):
    out = np.zeros(ns(dur))
    k = 0.0
    while k < dur - 0.03:
        c = clink(r, 3600, 0.03, 0.8) * 0.25
        i = ns(k); out[i:i + len(c)] += c[: len(out) - i]
        k += 0.035 + 0.02 * k / dur
    return out


def gulp(r):
    t = tt(0.4)
    f = 260 * np.exp(-t / 0.12) + 70
    return fades(np.sin(phase(f)) * np.exp(-t / 0.12) * 0.9 + lp(r.standard_normal(len(t)), 600) * np.exp(-t / 0.02) * 0.3, 0, 0.05)


def rumble(dur, r):
    t = tt(dur)
    return fades(lp(colored(len(t), r, 2.0), 140, 2) * (0.6 + 0.4 * smooth_noise(len(t), r, 1.0)) * 2.0, 0.3, 0.5)


def twinkle(r):
    return triangle(0.3, r, 0.6, 2600 + 600 * r.uniform())


def dizzy(r):
    t = tt(0.9)
    f = 1400 * np.exp(-t / 0.5) + 300 + 60 * np.sin(TAU_ * 7 * t)
    return fades(np.sin(phase(f)) * np.exp(-t / 0.5) * 0.35, 0.01, 0.15)


def moth(dur, r):
    t = tt(dur)
    return fades(bp(r.standard_normal(len(t)), 200, 900, 1) * (0.5 + 0.5 * np.sin(TAU_ * 18 * t)) * 0.4, 0.05, 0.1)


def waves(dur, r, level=1.0):
    n = ns(dur)
    out = np.zeros((2, n))
    for ch in range(2):
        sw = 0.5 + 0.5 * np.sin(TAU_ * np.arange(n) / SR / 6.5 + r.uniform(0, 6))
        out[ch] = lp(colored(n, r, 1.0), 1400, 2) * (0.3 + 0.7 * sw ** 2) * level
    return out


def gulls(dur, r):
    y = np.zeros(ns(dur))
    tm = r.uniform(0.3, 1.0)
    while tm < dur - 0.6:
        for j in range(r.integers(2, 4)):
            L = 0.22
            tl = tt(L)
            f = 1500 * (1 + 0.5 * np.sin(np.pi * tl / L))
            c = (np.sin(phase(f)) + 0.4 * np.sin(2 * phase(f))) * np.sin(np.pi * tl / L) ** 2 * 0.25
            i = ns(tm + j * 0.25); y[i:i + len(c)] += c[: len(y) - i]
        tm += r.exponential(2.0) + 1.0
    return y


def traffic(dur, r):
    n = ns(dur)
    return np.stack([lp(colored(n, r, 1.5), 500, 2) * (0.5 + 0.3 * smooth_noise(n, r, 0.3)) for _ in range(2)]) * 0.6


def tick_clock(dur, r):
    y = np.zeros(ns(dur))
    k = 0.0
    while k < dur:
        c = clink(r, 2800, 0.04, 0.4) * 0.12
        i = ns(k); y[i:i + len(c)] += c[: len(y) - i]
        k += 1.0
    return y


def build_sfx():
    b, r = Bus(), rng(11)
    # camera moves: soft whooshes on glides, a little air on cuts
    glides = [96, 244, 322, 520, 640, 786, 830, 1046, 1210, 1340, 1405, 1470, 1828, 1955, 2062, 2326, 2436, 2598]
    cuts = [180, 366, 1113, 1648, 2195]
    for f in glides:
        b.add(whoosh(0.8, r, 0.35, 300, 1500, 0.8, 0.25, 0.1), F(f) - 0.3, r.uniform(-0.4, 0.4), 0.18)
        log_cue(F(f), "whoosh", "camera glide")
    for f in cuts:
        b.add(whoosh(0.4, r, 0.08, 600, 2600, 0.7, 0.15, 0.2), F(f) - 0.05, 0, 0.16)
    # place changes: a slightly bigger swish
    for f in [220, 293, 406, 451, 577, 884, 941, 1010, 1169, 1253, 1546, 1605, 1735, 1799, 1882, 2024, 2121, 2254, 2388, 2492, 2558]:
        b.add(whoosh(0.7, r, 0.3, 400, 2400, 0.8, 0.2, 0.25), F(f) - 0.28, r.uniform(-0.3, 0.3), 0.3)
        log_cue(F(f), "swish", "place change")
    # room tone: a slow office clock in the London war room shots
    for a, z in [(0, 220), (293, 406), (451, 1010), (1169, 1605), (1882, 2024)]:
        b.add(tick_clock(F(z - a), r), F(a), 0.4, 0.5)
    # the fly (172-220)
    b.add(buzz(F(48), r), F(172), 0.2, 0.55); log_cue(F(172), "fly", "fly circles the agent")
    # flash after the hook
    b.add(triangle(0.5, r, 1.4, 2900), F(220), 0, 0.5)
    # map arrow drawn (326-350), the band's tiny drum is in the score
    b.add(scratch(r, 0.8), F(326), 0.1, 0.5); log_cue(F(326), "scratch", "arrow to Sicily")
    # "got weird"
    b.add(boing(r, 170), F(647), 0, 0.6); log_cue(F(647), "boing", "got weird")
    # dressing the body
    b.add(poof(r), F(712), 0, 0.9); b.add(poof(r, 0.4), F(788), -0.2, 0.6); log_cue(F(712), "poof", "uniform on")
    b.add(paper(r, 0.8, 2000), F(831), 0.2, 0.6); b.add(slap(r), F(856), -0.2, 0.5); log_cue(F(831), "paper", "plans into briefcase")
    # Spanish coast: waves + gulls (884-1010)
    b.add(waves(F(126), r, 0.5), F(884), 0, 0.6); b.add(gulls(F(126), r), F(884), 0.4, 0.5)
    # London street (1010-1169, 2492-2558): traffic + sparrows; dizzy poison + twinkling stars
    for a, z in [(1010, 1169), (2492, 2558)]:
        b.add(traffic(F(z - a), r), F(a), 0, 0.35); b.add(bird_chirps(F(z - a), r, 0.6), F(a), -0.4, 0.25)
    b.add(dizzy(r), F(1115), 0, 0.6); log_cue(F(1115), "dizzy", "rat poison")
    for k in range(5):
        b.add(twinkle(r), F(1125) + k * 0.33, r.uniform(-0.3, 0.3), 0.3)
    for k, f in enumerate([2492 + 10, 2492 + 32]):
        for s in range(4):
            b.add(stroll_step(r, 0.4), F(f) + s * 0.5, -0.3 + 0.2 * k, 0.25)
    # pocket litter pops on the desk
    for f in [1253, 1257, 1321, 1328, 1360, 1417, 1459]:
        b.add(slap(r), F(f), r.uniform(-0.3, 0.3), 0.55); b.add(paper(r, 0.2), F(f) + 0.02, 0, 0.35)
        log_cue(F(f), "pop", "pocket litter item lands")
    # moth (1562-1605)
    b.add(moth(1.4, r), F(1562), 0.3, 0.5)
    # submarine at dawn: waves, engine hum, the splash
    b.add(waves(F(1735 - 1605), r, 0.6), F(1605), 0, 0.6); b.add(rumble(F(130), r) * 0.25, F(1605), 0, 0.5)
    b.add(splash_big(r) * 0.35, F(1700), -0.2, 0.7); log_cue(F(1700), "splash", "body into the sea")
    # fisherman
    b.add(waves(F(64), r, 0.45), F(1735), 0, 0.6)
    b.add(whoa(r, 160) * 0.5, F(1761), -0.2, 0.55); log_cue(F(1761), "whoa", "fisherman finds him")
    # spy camera: shutter clicks + flash whine
    for f in [1834, 1855]:
        b.add(click(r), F(f), 0.2, 0.7); b.add(flash_whine(r), F(f), 0.2, 0.4); log_cue(F(f), "shutter", "Germans copy the letters")
    # letters point to Greece / Sardinia (arrows drawn), the duck decoy
    b.add(scratch(r, 0.8), F(1910), 0.3, 0.5); b.add(scratch(r, 0.75), F(1932), -0.3, 0.5)
    for k in range(2):
        b.add(quack(r), F(1996) + k * 0.32, 0.1, 0.55)
    log_cue(F(1996), "quack", "duck decoy on Sicily")
    # the hook: reel whir down, gulp, thump
    b.add(reel(r, 1.05), F(2026), 0.1, 0.6); b.add(gulp(r), F(2069), 0, 0.8); b.add(slap(r), F(2093), 0, 0.6)
    log_cue(F(2069), "gulp", "he swallowed it whole")
    # tanks rumble to Greece and Sardinia, a tumbleweed in Sicily
    b.add(rumble(F(70), r) * 0.5, F(2121), 0, 0.6)
    for k in range(10):
        b.add(clink(r, 1800 + 300 * (k % 3), 0.05, 0.6) * 0.2, F(2125) + k * 0.2, r.uniform(-0.5, 0.5), 0.5)
    b.add(breeze(F(60), r, 1.0, 0.4, 1400), F(2195), 0, 0.5); log_cue(F(2200), "wind", "tumbleweed")
    # the grave: breeze + blackbirds; chisel taps
    for a, z in [(2254, 2492), (2558, TOTAL)]:
        b.add(breeze(F(z - a), r, 0.5, 0.2, 900), F(a), 0, 0.4); b.add(bird_chirps(F(z - a), r, 0.35, "blackbird"), F(a), 0.4, 0.2)
    for f in [2442, 2453, 2464]:
        b.add(hammer_hit(r, 0.5), F(f), -0.2, 0.55); log_cue(F(f), "chisel", "his real name carved")
    return b.x


# ================================================================ mix
def main():
    voice = load_voice()
    music = build_music()
    sfx = build_sfx()
    Lv = integrated(voice)
    # house levels: music bed -13 LU under the voice, then the user's standard +3 dB; SFX -6 dB from house level
    Lm = integrated(music)
    g_music = dbg((Lv - 13.0) - Lm + 3.0)
    # duck the music -3 dB while words are spoken (smoothed 60 ms)
    duck = np.ones(N)
    for w in WORDS:
        a, b = ns(max(0.0, w["s"] - 0.05)), ns(w["e"] + 0.08)
        duck[a:b] = dbg(-3.0)
    from scipy.ndimage import uniform_filter1d
    duck = uniform_filter1d(duck, ns(0.12))
    music = music * g_music * duck
    # SFX house level 9 LU under the voice, then the user's standard -6 dB
    g_sfx = dbg((Lv - 9.0) - integrated(sfx) - 6.0)
    sfx = sfx * g_sfx
    # master: one gain for the whole mix to -15 LUFS (balance unchanged), look-ahead limiter to <= -1.2 dBTP
    pre = voice + music + sfx
    g = dbg(-15.0 - integrated(pre))
    voice, music, sfx = voice * g, music * g, sfx * g
    mix = (voice + music + sfx)
    from scipy.ndimage import minimum_filter1d
    thr = dbg(-1.6)
    need = np.minimum(1.0, thr / np.maximum(np.abs(mix).max(axis=0), 1e-9))
    env = minimum_filter1d(need, ns(0.006))
    env = uniform_filter1d(env, ns(0.004))
    env = np.minimum(env, minimum_filter1d(need, ns(0.002)))
    mix = mix * env
    write_wav(os.path.join(HERE, "mix.wav"), mix)
    for name, x in [("voice", voice), ("music", music), ("sfx", sfx)]:
        write_wav(os.path.join(HERE, f"stem_{name}.wav"), x)
    rep = [f"# Cues — The Agent With No Pulse", "", f"Duration {DUR:.3f} s, 48 kHz stereo.", "",
           f"Loudness: voice {integrated(voice):.1f} LUFS, music {integrated(music):.1f} LUFS ({integrated(music) - integrated(voice):+.1f} LU vs voice), "
           f"sfx {integrated(sfx):.1f} LUFS, mix {integrated(mix):.1f} LUFS, true peak {true_peak(mix):.1f} dBTP.", "",
           "| t (s) | frame | sound | why |", "|---|---|---|---|"]
    for t, n, d in sorted(CUES):
        rep.append(f"| {t:.2f} | {round(t * FPS)} | {n} | {d} |")
    open(os.path.join(HERE, "cues.md"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep[:6]))


if __name__ == "__main__":
    main()
