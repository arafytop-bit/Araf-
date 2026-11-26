"""Original score engine. A cue = (start, end, style, mood, intensity, ending); the engine arranges
bar-by-bar parts (drone, pad, bass, ostinato, lead motif, percussion, accents) from a per-culture style
(scale, leitmotifs, instruments, drum idioms) and renders them through the soundfont as stems.

All material here is original (leitmotifs written for this channel); instruments are General MIDI
presets from MuseScore General (MIT).
"""
import math
from dataclasses import dataclass

import numpy as np

from .sf import Part, render
from . import sf as K

# ---------------------------------------------------------------- theory
PC = dict(C=0, Db=1, D=2, Eb=3, E=4, F=5, Gb=6, G=7, Ab=8, A=9, Bb=10, B=11)
MODES = dict(aeolian=[0, 2, 3, 5, 7, 8, 10], dorian=[0, 2, 3, 5, 7, 9, 10], phrygdom=[0, 1, 4, 5, 7, 8, 10],
             harmonic=[0, 2, 3, 5, 7, 8, 11], ionian=[0, 2, 4, 5, 7, 9, 11], minpent=[0, 3, 5, 7, 10],
             majpent=[0, 2, 4, 7, 9], mixolydian=[0, 2, 4, 5, 7, 9, 10])


class Scale:
    def __init__(self, root, mode, octave=4):
        self.root = PC[root] + 12 * (octave + 1)
        self.iv = MODES[mode]

    def deg(self, d, octave_shift=0):
        n = len(self.iv)
        o, k = divmod(int(d), n)
        return self.root + 12 * (o + octave_shift) + self.iv[k]

    def chord(self, d, kind='triad'):
        """Pitch classes (as midi in base octave) of a diatonic chord on degree d."""
        if kind == 'power':
            steps = [0, 4]
        elif kind == 'sus2':
            steps = [0, 1, 4]
        elif kind == 'seventh':
            steps = [0, 2, 4, 6]
        else:
            steps = [0, 2, 4]
        return [self.deg(d + s) for s in steps]


def voice(pcs, lo, hi, n=4):
    """Spread chord tones (midi numbers, any octave) into [lo, hi], low to high, n notes."""
    cls = sorted({p % 12 for p in pcs}, key=lambda c: (c - pcs[0] % 12) % 12)
    out = []
    p = lo
    i = 0
    root = pcs[0] % 12
    while p % 12 != root:
        p += 1
    out.append(p)
    cyc = [(c - root) % 12 for c in cls]
    while len(out) < n:
        i += 1
        step = cyc[i % len(cyc)] + 12 * (i // len(cyc))
        q = out[0] + step
        if q > hi:
            break
        if q - out[-1] >= (3 if q < 55 else 2):
            out.append(q)
    return out


# ---------------------------------------------------------------- styles
# Motifs: list of (beat, dur_beats, degree in the style's melody scale) over 4 bars (16 beats).
def M(*notes):
    return [tuple(x) for x in notes]


STYLES = {
    'viking': dict(
        root='D', mode='dorian', mmode='dorian', tempo=100,
        prog=dict(mystery=[0, 0, 6, 5], adventure=[0, 6, 3, 0], battle=[0, 5, 6, 0], tragic=[0, 5, 2, 6],
                  tension=[0, 0, 5, 5], pastoral=[2, 6, 0, 5], triumph=[2, 6, 0, 0]),
        motifA=M((0, 1, 0), (1, .5, 2), (1.5, .5, 3), (2, 2, 4), (4, 1, 6), (5, 1, 4), (6, 1, 3), (7, 1, 2),
                 (8, 1.5, 3), (9.5, .5, 2), (10, 1, 1), (11, 1, -1), (12, 3, 0), (15, 1, -3)),
        progA=[0, 2, 6, 0],
        motifB=M((0, 1, 4), (1, 1, 6), (2, 1.5, 7), (3.5, .5, 6), (4, 2, 4), (6, 1, 3), (7, 1, 2),
                 (8, 1, 3), (9, 1, 2), (10, 1, 1), (11, 1, 0), (12, 4, 0)),
        progB=[0, 2, 5, 0],
        ins=dict(drone=[(0, 42), (0, 43)], pad=[(0, 49)], choir=(0, 52), bass=(0, 43), ost=(0, 48), pizz=(0, 45),
                 lead=(0, 110), lead_epic=(0, 60), lead_soft=(0, 73), color=(0, 46), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70)),
        drum_kit=48, perc='viking'),
    'hun': dict(
        root='E', mode='phrygdom', mmode='phrygdom', tempo=92,
        prog=dict(mystery=[0, 0, 1, 0], adventure=[0, 6, 0, 1], battle=[0, 1, 0, 6], tragic=[3, 1, 5, 0],
                  tension=[0, 0, 1, 1], pastoral=[3, 1, 0, 0], triumph=[0, 1, 0, 0], feast=[0, 3, 1, 0]),
        motifA=M((0, .5, 4), (.5, .5, 5), (1, 1, 4), (2, .5, 2), (2.5, .5, 1), (3, 1, 0), (4, 1.5, 1), (5.5, .5, 2),
                 (6, 2, 3), (8, 1, 4), (9, 1, 3), (10, 1, 2), (11, 1, 1), (12, 4, 0)),
        progA=[0, 6, 0, 0],
        motifB=M((0, 1, 7), (1, .5, 6), (1.5, .5, 5), (2, 2, 4), (4, 1, 5), (5, 1, 4), (6, 1, 3), (7, 1, 2),
                 (8, 2, 1), (10, 2, 2), (12, 4, 0)),
        progB=[0, 3, 1, 0],
        ins=dict(drone=[(0, 43), (0, 53)], pad=[(0, 49)], choir=(0, 53), bass=(0, 43), ost=(0, 48), pizz=(0, 45),
                 lead=(0, 77), lead_epic=(0, 111), lead_soft=(0, 77), color=(0, 15), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70)),
        drum_kit=48, perc='hun'),
    'roman': dict(
        root='C', mode='aeolian', mmode='aeolian', tempo=108,
        prog=dict(mystery=[0, 0, 5, 4], adventure=[2, 6, 5, 6], battle=[0, 5, 3, 4], tragic=[0, 5, 2, 6],
                  tension=[0, 0, 5, 5], pastoral=[2, 5, 6, 2], triumph=[2, 6, 5, 6], comedic=[0, 0, 3, 4]),
        motifA=M((0, .75, 0), (.75, .25, 0), (1, 1, 4), (2, 1.5, 7), (3.5, .5, 9), (4, 1, 8), (5, 1, 7), (6, 2, 6),
                 (8, 1, 5), (9, 1, 4), (10, 1, 3), (11, 1, 2), (12, 3, 4), (15, .5, 4), (15.5, .5, 6)),
        progA=[0, 6, 5, 4],
        motifB=M((0, 1, 7), (1, 1, 9), (2, 1.5, 8), (3.5, .5, 7), (4, 2, 6), (6, 1, 5), (7, 1, 4),
                 (8, 1, 5), (9, 1, 3), (10, 1, 2), (11, 1, 1), (12, 4, 0)),
        progB=[0, 6, 3, 0],
        sneak=[(0, .35, 0), (1, .35, 3), (1.5, .35, 5), (2, .35, 6), (2.5, .9, 7), (4, .35, 10), (4.5, .35, 9), (5, .35, 7),
               (6, 1.4, 3), (8, .35, 0), (9, .35, 3), (9.5, .35, 5), (10, .35, 6), (10.5, .9, 7), (12, .35, 6),
               (12.5, .35, 5), (13, .35, 3), (14, 1.4, 0)],
        ins=dict(drone=[(0, 42), (0, 43)], pad=[(0, 49)], choir=(0, 52), bass=(0, 43), ost=(0, 48), pizz=(0, 45),
                 lead=(0, 56), lead_epic=(0, 61), lead_soft=(0, 68), color=(0, 46), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70), comic2=(0, 71)),
        drum_kit=56, perc='roman'),
    'greek': dict(
        root='A', mode='dorian', mmode='dorian', tempo=112,
        prog=dict(mystery=[0, 3, 0, 3], adventure=[0, 6, 2, 3], battle=[0, 5, 2, 6], tragic=[0, 5, 2, 6],
                  tension=[0, 0, 5, 5], pastoral=[0, 3, 0, 3], triumph=[0, 3, 4, 0], comedic=[0, 3, 0, 4]),
        motifA=M((0, 1, 4), (1, .5, 3), (1.5, .5, 2), (2, 1, 1), (3, 1, 0), (4, 1.5, 2), (5.5, .5, 3), (6, 2, 4),
                 (8, 1, 5), (9, 1, 4), (10, 1, 3), (11, 1, 2), (12, 2, 1), (14, 2, 0)),
        progA=[0, 2, 3, 0],
        motifB=M((0, 1, 0), (1, 1, 2), (2, 1, 4), (3, 1, 7), (4, 2, 6), (6, 1, 5), (7, 1, 4), (8, 1, 3), (9, 1, 4),
                 (10, 2, 5), (12, 4, 4)),
        progB=[0, 2, 3, 4],
        ins=dict(drone=[(0, 42), (0, 43)], pad=[(0, 49)], choir=(0, 52), bass=(0, 32), ost=(0, 46), pizz=(0, 45),
                 lead=(0, 68), lead_epic=(0, 56), lead_soft=(0, 75), color=(0, 24), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70)),
        drum_kit=48, perc='greek'),
    'korean': dict(
        root='D', mode='aeolian', mmode='minpent', tempo=100,
        prog=dict(mystery=[0, 0, 5, 6], adventure=[0, 6, 5, 6], battle=[0, 5, 6, 0], tragic=[0, 5, 2, 6],
                  tension=[0, 0, 5, 5], pastoral=[2, 6, 0, 0], triumph=[5, 6, 0, 0]),
        motifA=M((0, 1.5, 3), (1.5, .5, 4), (2, 1, 5), (3, 1, 4), (4, 2, 3), (6, 1, 2), (7, 1, 1),
                 (8, 1, 2), (9, .5, 3), (9.5, .5, 2), (10, 1, 1), (11, 1, 0), (12, 4, 0)),
        progA=[2, 0, 3, 0],
        motifB=M((0, 1, 0), (1, 1, 1), (2, 2, 2), (4, 1, 3), (5, 1, 4), (6, 2, 5), (8, 1, 4), (9, 1, 3), (10, 1, 2),
                 (11, 1, 3), (12, 4, 3)),
        progB=[0, 4, 2, 4],
        ins=dict(drone=[(0, 42), (0, 43)], pad=[(0, 49)], choir=(0, 52), bass=(0, 43), ost=(8, 107), pizz=(0, 45),
                 lead=(0, 77), lead_epic=(0, 60), lead_soft=(0, 77), color=(8, 107), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70), reed=(0, 111)),
        drum_kit=48, perc='korean'),
    'modern': dict(
        root='A', mode='harmonic', mmode='harmonic', tempo=90,
        prog=dict(mystery=[0, 5, 3, 4], adventure=[0, 5, 2, 6], battle=[0, 5, 3, 4], tragic=[0, 5, 2, 6],
                  tension=[0, 0, 5, 5], pastoral=[0, 5, 2, 6], triumph=[5, 6, 0, 0]),
        motifA=M((0, .5, 7), (.5, .5, 9), (1, 1, 11), (2, .5, 10), (2.5, 1.5, 9), (4, 1, 8), (5, 1, 7), (6, 2, 9),
                 (8, .5, 5), (8.5, .5, 7), (9, 1, 9), (10, .5, 8), (10.5, 1.5, 7), (12, 1, 6), (13, 1, 8), (14, 2, 11)),
        progA=[0, 5, 3, 4],
        motifB=M((0, .5, 7), (.5, .5, 9), (1, 1, 11), (2, 2, 12), (4, 1, 11), (5, 1, 10), (6, 2, 9),
                 (8, 1, 10), (9, 1, 9), (10, 1, 8), (11, 1, 6), (12, 4, 7)),
        progB=[0, 5, 3, 0],
        ins=dict(drone=[(8, 80)], pad=[(0, 91), (0, 49)], choir=(0, 52), bass=(8, 80), ost=(0, 0), pizz=(0, 45),
                 lead=(0, 10), lead_epic=(0, 48), lead_soft=(0, 8), color=(0, 14), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70)),
        drum_kit=25, perc='trap'),
    'lofi': dict(
        root='Eb', mode='ionian', mmode='majpent', tempo=80,
        prog=dict(mystery=[0, 5, 3, 4], adventure=[0, 5, 3, 4]),
        motifA=M((0, 1, 4), (1, 1, 3), (2, 2, 2), (4, 1, 1), (5, 1, 2), (6, 2, 0), (8, 1, 4), (9, 1, 5), (10, 2, 4),
                 (12, 2, 3), (14, 2, 2)),
        progA=[0, 5, 3, 4],
        motifB=M((0, 2, 2), (2, 2, 1), (4, 4, 0), (8, 1, 3), (9, 1, 2), (10, 2, 1), (12, 4, 0)),
        progB=[0, 5, 3, 4],
        ins=dict(drone=[(0, 89)], pad=[(0, 4)], choir=(0, 53), bass=(0, 32), ost=(0, 4), pizz=(0, 45),
                 lead=(0, 11), lead_epic=(0, 11), lead_soft=(0, 11), color=(0, 11), brass=(0, 61), low_brass=(0, 57),
                 timp=(0, 47), taiko=(0, 116), tom=(0, 117), comic=(0, 70)),
        drum_kit=40, perc='lofi'),
}

# Per-instrument level trims (velocity multiplier) so presets sit together.
TRIM = {(0, 116): 0.95, (0, 117): 0.8, (0, 52): 0.8, (0, 53): 0.85, (0, 111): 0.7, (0, 77): 0.85, (0, 110): 0.85,
        (0, 61): 0.85, (0, 56): 0.8, (8, 80): 1.0, (0, 10): 0.75, (0, 14): 0.6, (0, 0): 0.8, (0, 46): 0.9}

# 16-step percussion patterns: {intensity: [(instrument_key, note, {step: vel})]}
PERC = {
    'viking': {
        1: [('taiko', 41, {0: 95, 10: 55})],
        2: [('taiko', 41, {0: 105, 3: 55, 6: 80, 8: 100, 11: 55, 14: 80}), ('kit', K.KICK, {0: 70})],
        3: [('taiko', 41, {0: 120, 2: 70, 4: 100, 6: 70, 8: 120, 10: 70, 12: 100, 13: 80, 14: 105, 15: 90}),
            ('taiko', 48, {3: 70, 7: 80, 11: 70, 15: 85}), ('kit', K.KICK, {0: 100, 8: 95})],
    },
    'hun': {
        1: [('taiko', 40, {0: 95, 8: 60})],
        2: [('taiko', 40, {0: 105, 2: 55, 3: 75, 4: 95, 6: 55, 7: 75, 8: 105, 10: 55, 11: 75, 12: 95, 14: 55, 15: 75})],
        3: [('taiko', 40, {0: 120, 2: 70, 3: 90, 4: 110, 6: 70, 7: 90, 8: 120, 10: 70, 11: 90, 12: 110, 14: 70, 15: 90}),
            ('taiko', 36, {0: 120, 8: 110}), ('kit', K.KICK, {0: 100, 8: 95})],
    },
    'roman': {
        1: [('kit', K.SNARE, {0: 55, 8: 45})],
        2: [('kit', K.SNARE, {0: 95, 2: 45, 3: 50, 4: 85, 6: 45, 7: 55, 8: 95, 10: 45, 12: 85, 13: 50, 14: 75, 15: 60}),
            ('taiko', 36, {0: 90, 8: 80})],
        3: [('kit', K.SNARE, {s: (110 if s % 4 == 0 else 70) for s in range(16)}), ('taiko', 36, {0: 115, 6: 80, 8: 110, 14: 85})],
    },
    'greek': {
        1: [('taiko', 45, {0: 80, 6: 55, 8: 70, 12: 60}), ('kit2', K.TAMB, {4: 45, 12: 45})],
        2: [('taiko', 45, {0: 100, 6: 70, 8: 90, 12: 75}), ('kit2', K.TAMB, {s: (60 if s % 4 == 2 else 40) for s in range(0, 16, 2)}),
            ('kit2', K.CLAP, {4: 85, 12: 90}), ('kit2', K.KICK, {0: 100, 6: 70, 8: 95})],
        3: [('taiko', 45, {0: 120, 3: 70, 6: 90, 8: 115, 11: 70, 14: 95}), ('kit2', K.TAMB, {s: 70 for s in range(16)}),
            ('kit2', K.CLAP, {4: 100, 12: 105}), ('kit2', K.KICK, {0: 115, 6: 80, 8: 110, 10: 70})],
    },
    'korean': {
        1: [('taiko', 38, {0: 100, 11: 55})],
        2: [('taiko', 38, {0: 110, 6: 60, 8: 95, 11: 70, 14: 85}), ('kit2', K.CONGA_H, {3: 55, 4: 65, 12: 60, 13: 50}),
            ('kit2', K.CONGA_L, {7: 60, 15: 65})],
        3: [('taiko', 38, {0: 125, 3: 75, 6: 95, 8: 120, 10: 70, 11: 85, 14: 105, 15: 90}), ('taiko', 34, {0: 120, 8: 115}),
            ('kit2', K.CONGA_H, {2: 60, 3: 70, 4: 75, 10: 60, 12: 75, 13: 60}), ('kit2', K.CONGA_L, {7: 75, 15: 80})],
    },
    'trap': {
        1: [('kit', K.KICK2, {0: 100, 10: 85}), ('kit', K.HAT, {s: 45 for s in range(0, 16, 2)})],
        2: [('kit', K.KICK2, {0: 110, 7: 80, 10: 100}), ('kit', K.CLAP, {8: 100}), ('kit', K.SNARE, {8: 70}),
            ('kit', K.HAT, {s: (62 if s % 4 == 0 else 48) for s in range(0, 16, 2)}), ('kit', K.OHAT, {14: 55})],
        3: [('kit', K.KICK2, {0: 115, 3: 80, 7: 85, 10: 105}), ('kit', K.CLAP, {8: 110}), ('kit', K.SNARE, {8: 85}),
            ('kit', K.HAT, {s: (66 if s % 4 == 0 else 50) for s in range(16)}), ('kit', K.OHAT, {6: 55, 14: 60})],
    },
    'lofi': {
        1: [('kit', K.KICK, {0: 80, 10: 70}), ('kit', K.SNARE, {4: 60, 12: 66}), ('kit', K.HAT, {0: 40, 3: 30, 4: 40, 7: 30, 8: 40, 11: 30, 12: 40, 15: 30})],
        2: [('kit', K.KICK, {0: 85, 7: 60, 10: 75}), ('kit', K.SNARE, {4: 70, 12: 74}), ('kit', K.HAT, {s: 40 for s in range(0, 16, 2)})],
    },
}


@dataclass
class Cue:
    t0: float
    t1: float
    style: str
    mood: str
    intensity: int = 1
    ending: str = 'cut'          # cut | button | ring | fade
    tempo: float = None
    seed: int = 0
    ramp: tuple = None           # (intensity at start, at end) for builds


class Arranger:
    """Collects parts for the whole video (merged by instrument) grouped into stems."""

    def __init__(self):
        self.parts = {}

    def part(self, stem, ins, drum=False, kit=0, volume=100):
        key = (stem, 'drum' if drum else 'mel', kit if drum else ins)
        if key not in self.parts:
            bank, prog = (0, kit) if drum else ins
            self.parts[key] = Part(name=str(key), bank=bank, program=prog, drum=drum, volume=volume)
        return self.parts[key]

    def note(self, stem, ins, t, dur, pitch, vel):
        v = vel * TRIM.get(ins, 1.0)
        self.part(stem, ins).n(t, dur, pitch, v)

    def drum(self, stem, kit, t, note, vel, dur=0.3):
        self.part(stem, None, drum=True, kit=kit).n(t, dur, note, vel)

    def stems(self):
        out = {}
        for (stem, _, _), p in self.parts.items():
            out.setdefault(stem, []).append(p)
        return out

    def render(self, duration):
        res = {}
        for stem, parts in self.stems().items():
            res[stem] = render(parts, duration=duration)
        return res


# ---------------------------------------------------------------- cue arrangement
ARCH = {  # mood -> archetype + flags
    'still': 'still', 'scholar': 'still', 'grief': 'still',
    'mystery': 'mystery', 'intrigue': 'mystery', 'saga': 'mystery', 'mystic': 'mystery', 'reveal': 'mystery',
    'injustice': 'mystery', 'dread': 'mystery', 'cold': 'mystery',
    'adventure': 'adventure', 'heroic': 'adventure', 'saga_heroic': 'adventure', 'march': 'adventure', 'gallop': 'adventure',
    'speedrun': 'adventure', 'feast': 'adventure', 'feast_light': 'adventure', 'anthem': 'adventure', 'recap': 'adventure',
    'groove': 'adventure', 'outro': 'adventure', 'legacy': 'adventure',
    'tension': 'tension', 'build': 'tension', 'battle_tense': 'tension', 'struggle': 'tension', 'epic_build': 'tension',
    'disaster': 'tension', 'drum_rise': 'tension', 'resolve': 'tension',
    'battle': 'battle', 'war': 'battle', 'climax': 'battle', 'funeral_epic': 'battle', 'night_battle': 'battle', 'epic': 'battle',
    'tragic': 'tragic',
    'triumph': 'triumph', 'pomp': 'triumph', 'parade': 'triumph',
    'pastoral': 'pastoral', 'lyre': 'pastoral', 'theater': 'pastoral',
    'comedic': 'comedic', 'heist': 'comedic', 'comedic_fight': 'comedic',
    'lofi': 'lofi',
}


def arrange(A, cue):
    st = STYLES[cue.style]
    tempo = cue.tempo or st['tempo'] * (1.3 if cue.mood == 'speedrun' else 1.0)
    beat = 60.0 / tempo
    bar = 4 * beat
    arch = ARCH.get(cue.mood, 'mystery')
    hs = Scale(st['root'], st['mode'], 3)
    ms = Scale(st['root'], st['mmode'], 4)
    if arch == 'triumph' and st['mode'] in ('aeolian', 'dorian', 'harmonic'):
        hs = Scale(st['root'], 'ionian', 3)
        ms = Scale(st['root'], 'ionian', 4)
    ins = st['ins']
    r = np.random.default_rng(cue.seed + int(cue.t0 * 10))
    nbars = max(1, int(math.ceil((cue.t1 - cue.t0) / bar - 1e-6)))
    prog = st['prog'].get(cue.mood, st['prog'].get(arch, st['prog']['mystery']))
    use_motif = arch in ('adventure', 'battle', 'triumph', 'pastoral', 'tragic', 'mystery', 'lofi')
    I0, I1 = cue.ramp if cue.ramp else (cue.intensity, cue.intensity)

    def clip_note(stem, inst, t, dur, p, v):
        if t >= cue.t1 - 0.02:
            return
        dur = min(dur, cue.t1 - t + (0.0 if cue.ending == 'cut' else 1.2))
        A.note(stem, inst, t, dur, p, v)

    for b in range(nbars):
        tb = cue.t0 + b * bar
        if tb >= cue.t1 - 0.05:
            break
        u = b / max(1, nbars - 1)
        inten = I0 + (I1 - I0) * u
        I = int(round(inten))
        period = b % 8
        phrase = 'A' if (b // 4) % 2 == 0 else 'B'
        if use_motif and arch not in ('mystery',):
            pr = st['prog' + phrase]
        else:
            pr = prog
        deg = pr[b % 4]
        chord = hs.chord(deg)
        if cue.style == 'roman' and deg == 4 and st['mode'] == 'aeolian' and arch != 'triumph':
            chord = [hs.deg(4), hs.deg(4) + 4, hs.deg(4) + 7]       # major dominant (harmonic minor)
        if cue.style == 'lofi':
            chord = hs.chord(deg, 'seventh')
        root = chord[0]
        vel_base = 55 + 18 * I
        swell = 0.0

        # ---- drone / pad
        if arch in ('still', 'mystery', 'tension', 'tragic', 'battle', 'pastoral', 'adventure', 'triumph', 'lofi'):
            if b % 2 == 0 and arch in ('still', 'mystery', 'tension', 'tragic', 'battle'):
                for inst in ins['drone']:
                    lowr = root - 12 if inst == (0, 43) else root
                    clip_note('harm', inst, tb, 2 * bar + 0.15, lowr, 50 + 12 * I)
                    clip_note('harm', inst, tb, 2 * bar + 0.15, lowr + 7, 42 + 10 * I)
            pad_inst = ins['pad'][0]
            lo, hi = (55, 74) if arch != 'lofi' else (58, 76)
            if arch in ('tragic', 'still', 'battle', 'triumph', 'pastoral', 'adventure', 'lofi') or (arch == 'mystery' and I >= 1):
                for p in voice(chord, lo, hi, 4 if arch in ('battle', 'triumph', 'lofi') else 3):
                    clip_note('harm', pad_inst, tb, bar + 0.1, p, 44 + 12 * I)
            if arch in ('battle', 'tragic', 'triumph') or (arch == 'tension' and I >= 2):
                for p in voice(chord, 60, 79, 3):
                    clip_note('harm', ins['choir'], tb, bar + 0.1, p, 40 + 14 * I)

        # ---- bass
        bass_inst = ins['bass']
        broot = root - 12 if root >= 48 else root
        while broot > 45:
            broot -= 12
        if arch == 'comedic':
            # staccato walking pizzicato: root, fifth, octave, chromatic approach to next root
            nxt = hs.chord(pr[(b + 1) % 4])[0] - 12
            while nxt > 45:
                nxt -= 12
            walk = [broot, broot + 7, broot + 12, nxt - 1 if nxt - 1 != broot + 12 else nxt + 1]
            for k, p in enumerate(walk):
                clip_note('bass', ins['pizz'], tb + k * beat, beat * 0.45, p, 78 + 8 * I)
        elif cue.style == 'modern':
            for st_ in (0, 10) if I < 3 else (0, 7, 10):
                clip_note('bass', bass_inst, tb + st_ * beat / 4, beat * (2.2 if st_ == 0 else 1.2), broot, 100)
        elif cue.style == 'lofi':
            clip_note('bass', bass_inst, tb, beat * 1.8, broot + 12 if broot < 36 else broot, 85)
            clip_note('bass', bass_inst, tb + 2.5 * beat, beat * 1.2, broot + 7 + (12 if broot < 36 else 0), 70)
        elif arch == 'still' or (arch in ('mystery', 'tragic', 'pastoral') and I <= 1):
            if b % 2 == 0:
                clip_note('bass', bass_inst, tb, 2 * bar, broot, 60 + 10 * I)
        elif arch in ('mystery', 'tension'):
            for k in range(4):
                clip_note('bass', bass_inst, tb + k * beat, beat * 0.6, broot, 70 + 10 * I - (8 if k % 2 else 0))
        elif cue.mood == 'gallop' or st.get('perc') == 'hun' and arch == 'battle':
            for s in (0, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15):
                clip_note('bass', bass_inst, tb + s * beat / 4, beat * 0.22, broot, 90 if s % 4 == 0 else 70)
        else:
            for k in range(8):
                p = broot + (12 if (arch == 'battle' and k in (3, 7)) else 0)
                clip_note('bass', bass_inst, tb + k * beat / 2, beat * 0.42, p, (92 if k % 2 == 0 else 76) + 6 * (I - 2))

        # ---- ostinato
        if arch in ('adventure', 'battle', 'tension') and I >= 2 or (arch == 'pastoral') or (cue.style == 'korean' and arch == 'mystery'):
            o_inst = ins['ost'] if arch != 'pastoral' else ins['color'] if cue.style not in ('greek',) else ins['ost']
            tones = voice(chord, 62 if arch != 'pastoral' else 57, 84, 4)
            if arch == 'battle' or (arch == 'tension' and I >= 3):
                cell = [0, 2, 1, 2] * 4
                step = beat / 4
            elif arch == 'pastoral' or cue.style == 'korean':
                cell = [0, 1, 2, 3, 2, 1, 0, 2]
                step = beat / 2
            else:
                cell = [0, 1, 2, 1, 0, 2, 1, 2]
                step = beat / 2
            for k, ix in enumerate(cell):
                p = tones[ix % len(tones)]
                v = (70 if k % 4 == 0 else 56) + 8 * (I - 2)
                clip_note('harm', o_inst, tb + k * step, step * (0.55 if arch != 'pastoral' else 1.6), p, v)

        # ---- lead motif
        if use_motif and (I >= 2 or arch in ('pastoral', 'tragic', 'lofi') or (arch == 'mystery' and period in (2, 3, 6, 7))):
            motif = st['motif' + phrase]
            if arch == 'comedic':
                motif = st.get('sneak', st['motifA'])
            lead = ins['lead']
            if arch in ('battle', 'triumph'):
                lead = ins['lead_epic']
            elif arch in ('pastoral', 'mystery', 'tragic') and cue.style != 'modern':
                lead = ins['lead_soft'] if arch != 'tragic' else ins['lead']
            q = b % 4
            vel = 66 + 12 * I if arch != 'mystery' else 52
            for bt, du, d in motif:
                if q * 4 <= bt < (q + 1) * 4:
                    t = tb + (bt - q * 4) * beat
                    p = ms.deg(d) if arch != 'comedic' else ms.root - 12 + int(d)
                    if arch == 'tragic':
                        p -= 12 if cue.style in ('viking', 'roman') and lead == ins['lead'] else 0
                    clip_note('lead', lead, t, du * beat * 0.97, p, vel)
                    if arch in ('battle', 'triumph') and I >= 3:
                        clip_note('lead', ins['brass'], t, du * beat * 0.95, p - 12, vel - 10)
            if cue.style == 'korean' and arch in ('battle', 'adventure') and I >= 3 and phrase == 'B':
                for bt, du, d in motif:
                    if q * 4 <= bt < (q + 1) * 4:
                        clip_note('lead', ins['reed'], tb + (bt - q * 4) * beat, du * beat * 0.95, ms.deg(d) + 12, 60)
        elif arch == 'comedic':
            q = b % 4
            for bt, du, d in st.get('sneak', []):
                if q * 4 <= bt < (q + 1) * 4:
                    clip_note('lead', ins['comic'], tb + (bt - q * 4) * beat, du * beat, ms.root - 12 + int(d), 82)

        # ---- percussion
        kind = st['perc']
        pat = PERC.get(kind, {}).get(min(3, max(1, I)), []) if I >= 1 and arch not in ('still', 'tragic') else []
        if arch == 'comedic':
            for s in (2, 6, 10, 14):
                A.drum('perc', 0, tb + s * beat / 4, K.WOOD_H if s % 8 == 2 else K.WOOD_L, 62)
        elif arch == 'pastoral' and kind not in ('greek',):
            pat = [x for x in pat if x[0] != 'kit'][:1]
        for src, note, steps in pat:
            for s, v in steps.items():
                t = tb + s * beat / 4
                if t >= cue.t1 - 0.02:
                    continue
                if src == 'taiko':
                    A.note('perc', ins['taiko'], t, 0.6, note, v)
                elif src == 'kit':
                    A.drum('perc', st['drum_kit'], t, note, v)
                else:
                    A.drum('perc', 0, t, note, v)
        if I >= 2 and arch in ('battle', 'tension', 'adventure') and kind not in ('trap', 'lofi'):
            if period == 0:
                A.drum('perc', 48 if st['drum_kit'] != 56 else 58, tb, K.CRASH, 70 + 10 * I)
            if arch in ('battle', 'tension') and b % 4 == 0:
                A.note('perc', ins['timp'], tb, beat * 0.9, broot + 12 if broot + 12 <= 57 else broot, 85 + 8 * I)
            if arch == 'tension' and (b % 4 == 3) and I >= 2:
                for k in range(16):  # timpani roll crescendo into the next phrase
                    A.note('perc', ins['timp'], tb + k * beat / 4, beat / 4, broot + 12 if broot + 12 <= 57 else broot, 50 + 4 * k)
        if kind == 'trap' and I >= 2 and b % 4 == 3:
            for k in range(8):
                A.drum('perc', st['drum_kit'], tb + 3 * beat + k * beat / 8, K.HAT, 50 + 3 * k)

    # ---- endings
    end = cue.t1
    if cue.ending == 'button':
        ch = hs.chord(prog[0] if arch != 'adventure' else 0)
        for p in voice(ch, 55, 76, 4):
            A.note('hits', ins['brass'], end, 0.35, p, 105)
            A.note('hits', ins['pad'][0], end, 0.3, p + 12, 95)
        A.note('hits', ins['low_brass'], end, 0.4, ch[0] - 12, 110)
        A.note('hits', ins['timp'], end, 0.8, ch[0] - 12 if ch[0] - 12 >= 40 else ch[0], 120)
        A.drum('hits', 48, end, K.CRASH, 100)
        A.drum('hits', 48, end, K.KICK, 110)


# ---------------------------------------------------------------- stingers (one-shot musical moments)
def stinger(A, kind, t, style='viking', **kw):
    st = STYLES.get(style, STYLES['viking'])
    hs = Scale(st['root'], st['mode'], 3)
    root = hs.deg(0)
    while root < 48:
        root += 12

    if kind == 'title_hit':          # tutti stab on the new section's tonic + timpani + cymbal + taiko
        ch = hs.chord(0)
        for p in voice(ch, 50, 79, 5):
            A.note('hits', (0, 61), t, 0.55, p, 118)
            A.note('hits', (0, 48), t, 0.45, p + 12, 110)
            A.note('hits', (0, 52), t, 0.9, p + 12, 95)
        A.note('hits', (0, 57), t, 0.7, root - 12, 120)
        A.note('hits', (0, 58), t, 0.8, root - 24, 115)
        A.note('hits', (0, 47), t, 1.2, root - 12 if root - 12 >= 40 else root, 127)
        A.note('hits', (0, 116), t, 1.0, 38, 127)
        A.drum('hits', 48, t, K.CRASH, 112)
        A.drum('hits', 48, t, K.KICK, 120)
        A.note('hits', (0, 119), t - 1.25, 1.3, 60, 85)          # reverse cymbal into the hit
    elif kind == 'braam':
        for p in (root - 24, root - 12, root - 5):
            A.note('hits', (0, 61), t, 2.6, p, 120)
            A.note('hits', (0, 57), t, 2.6, p, 118)
        A.note('hits', (0, 58), t, 2.8, root - 24, 125)
        A.note('hits', (0, 43), t, 2.8, root - 24, 115)
        A.note('hits', (0, 116), t, 1.5, 34, 127)
        A.note('hits', (0, 47), t, 1.6, root - 12 if root - 12 >= 40 else root, 120)
        A.note('hits', (0, 119), t - 1.25, 1.3, 60, 80)
    elif kind == 'death':            # recurring death motif: low brass DUN + choir swell + church bell
        ch = hs.chord(0)
        A.note('hits', (0, 57), t, 1.6, root - 12, 122)
        A.note('hits', (0, 58), t, 1.8, root - 24, 122)
        A.note('hits', (0, 61), t, 1.4, root - 5, 108)
        A.note('hits', (0, 47), t, 2.0, root - 12 if root - 12 >= 40 else root, 127)
        A.note('hits', (0, 116), t, 1.2, 34, 127)
        p = A.part('hits', (0, 52))
        for q in voice(ch, 57, 76, 4):
            p.n(t + 0.05, 3.2, q, 92)
        p.swell(t, t + 0.9, 40, 127)
        p.swell(t + 2.2, t + 3.3, 127, 0)
        p.cc(t + 3.4, 11, 127)
        A.note('hits', (8, 14), t + 0.35, 4.0, root - 12 if root - 12 >= 48 else root, 100)
    elif kind == 'dun3':             # dramatic "dun dun dunnn"
        for k, (dp, du) in enumerate([(0, .28), (-1, .28), (-3, 1.4)]):
            tt = t + k * 0.34
            for p in (root - 12 + dp * 1, root + dp, root + 7 + dp):
                A.note('hits', (0, 61), tt, du, p, 115)
            A.note('hits', (0, 47), tt, du, root - 12 + dp if root - 12 + dp >= 40 else root + dp, 120)
            A.note('hits', (0, 57), tt, du, root - 24 + dp, 115)
        A.drum('hits', 48, t + 0.68, K.CRASH, 95)
    elif kind == 'sad_trombone':     # wah wah wah wahhh (descending, last note with vibrato)
        p = A.part('hits', (0, 57))
        notes = [(58, .42), (57, .42), (56, .42), (55, 1.5)]
        tt = t
        for k, (n, du) in enumerate(notes):
            p.n(tt, du * 0.95, n, 100)
            tt += du * 0.85 if k < 3 else 0
        tv = t + 3 * 0.42 * 0.85
        for k in range(36):
            p.bends.append((tv + 0.2 + k * 0.035, int(500 * math.sin(k * 1.4))))
        p.bends.append((tv + 0.2 + 36 * 0.035, 0))
        p.bends.append((t - 0.01, 0))
    elif kind == 'rimshot':
        A.drum('hits', 0, t, K.SNARE, 112)
        A.drum('hits', 0, t + 0.17, K.TOM_LM, 105)
        A.drum('hits', 0, t + 0.17, K.KICK, 110)
        A.drum('hits', 0, t + 0.36, K.CRASH, 105)
    elif kind == 'boss':             # video-game boss intro: 8-bit arpeggio + brass hit
        for k, n in enumerate([62, 65, 69, 74, 77, 81]):
            A.note('hits', (0, 80), t + k * 0.055, 0.05, n, 80)
        for p in (38, 50, 57, 62):
            A.note('hits', (0, 61), t + 0.33, 1.2, p, 120)
        A.note('hits', (0, 47), t + 0.33, 1.4, 38 + 12, 125)
        A.drum('hits', 48, t + 0.33, K.CRASH, 105)
        A.note('hits', (0, 116), t + 0.33, 1.0, 34, 127)
    elif kind == 'fanfare':          # short brass fanfare in the style's major
        ms = Scale(st['root'], 'ionian', 4)
        seq = [(0, .14, 0), (.15, .14, 2), (.3, .14, 4), (.45, 1.2, 7)]
        for dt, du, d in seq:
            for o in (0, -12):
                A.note('hits', (0, 56), t + dt, du, ms.deg(d) + o, 112)
        for p in voice(ms.chord(0), 55, 76, 4):
            A.note('hits', (0, 61), t + 0.45, 1.2, p, 108)
        A.note('hits', (0, 47), t + 0.45, 1.2, ms.deg(0) - 24, 120)
        A.drum('hits', 48, t + 0.45, K.CRASH, 100)
    elif kind == 'metal':            # heavy-metal power chords (2.6 s)
        p = (0, 30)
        e = 40
        for k in range(16):
            tt = t + k * 0.125
            n = e if k not in (6, 7, 14) else (e + 3 if k in (6, 7) else e + 5)
            for q in (n, n + 7, n + 12):
                A.note('hits', p, tt, 0.115, q, 118 if k % 4 == 0 else 100)
        for q in (e, e + 7, e + 12):
            A.note('hits', p, t + 2.0, 0.6, q, 120)
        for k in range(8):
            A.drum('hits', 16, t + k * 0.25, K.KICK, 120)
            A.drum('hits', 16, t + k * 0.25 + 0.125, K.KICK, 95)
            if k % 2 == 1:
                A.drum('hits', 16, t + k * 0.25, K.SNARE, 120)
        A.drum('hits', 16, t, K.CRASH, 120)
        A.drum('hits', 16, t + 2.0, K.CRASH, 120)
        A.drum('hits', 16, t + 2.0, K.CHINA, 115)
    elif kind == 'pomp_fanfare':     # pompous British-style fanfare (original)
        ms = Scale('D', 'ionian', 4)
        seq = [(0, .2, 4), (.22, .2, 4), (.44, .2, 4), (.66, .55, 7), (1.25, .2, 6), (1.47, .2, 5), (1.69, .9, 4)]
        for dt, du, d in seq:
            A.note('hits', (0, 56), t + dt, du, ms.deg(d), 105)
            A.note('hits', (0, 56), t + dt, du, ms.deg(d - 2), 95)
        for k in range(10):
            A.drum('hits', 56, t + k * 0.11, K.SNARE, 60 + 4 * k)
        A.drum('hits', 48, t + 1.69, K.CRASH, 90)
    elif kind == 'jig':              # pirate accordion jig (original, 6/8 feel)
        ms = Scale('G', 'mixolydian', 4)
        seq = [0, 2, 4, 4, 2, 4, 5, 4, 2, 0, 1, 2, 1, -1, -3]
        for k, d in enumerate(seq):
            A.note('hits', (0, 21), t + k * 0.13, 0.12, ms.deg(d), 95)
        for k in range(6):
            A.note('hits', (0, 58), t + k * 0.39, 0.18, ms.deg(0) - 24 if k % 2 == 0 else ms.deg(4) - 24, 100)
    elif kind == 'harp_gliss':
        ms = Scale(st['root'], st['mmode'], 4)
        for k in range(15):
            A.note('hits', (0, 46), t + k * 0.04, 1.2, ms.deg(k - 3), 70 + 3 * k)
    elif kind == 'swell':            # heroic major swell (choir + strings + horns)
        ms = Scale(st['root'], 'ionian', 3)
        for inst, lo, v in (((0, 52), 57, 100), ((0, 49), 50, 100), ((0, 60), 50, 95)):
            p = A.part('hits', inst)
            for q in voice(ms.chord(kw.get('degree', 0)), lo, lo + 22, 4):
                p.n(t, kw.get('dur', 3.5), q, v)
            p.swell(t, t + kw.get('dur', 3.5) * 0.7, 20, 127)
            p.swell(t + kw.get('dur', 3.5), t + kw.get('dur', 3.5) + 0.3, 127, 127)
        A.note('hits', (0, 47), t + kw.get('dur', 3.5) * 0.7, 1.2, ms.deg(0) - 12 if ms.deg(0) - 12 >= 40 else ms.deg(0), 110)
    elif kind == 'button':           # tiny comedic pizzicato button (plink-plonk)
        A.note('hits', (0, 45), t, 0.2, root + 7, 100)
        A.note('hits', (0, 45), t + 0.18, 0.3, root, 105)
    elif kind == 'outro_sting':      # 6.5 s punchy beat with the channel motif (BLUEPRINT 7)
        sty = STYLES['modern']
        ms = Scale(sty['root'], sty['mmode'], 4)
        hs2 = Scale(sty['root'], sty['mode'], 3)
        beat = 60 / 108.0
        for b in range(3):
            tb = t + b * 4 * beat
            ch = hs2.chord([0, 5, 4][b])
            for k in range(4):
                A.drum('hits', 25, tb + k * beat, K.KICK2, 120 if k % 2 == 0 else 100)
                if k % 2 == 1:
                    A.drum('hits', 25, tb + k * beat, K.CLAP, 115)
                for h in range(2):
                    A.drum('hits', 25, tb + k * beat + h * beat / 2, K.HAT, 70)
            for q in voice(ch, 57, 76, 4):
                A.note('hits', (0, 61), tb, beat * 0.5, q, 110)
                A.note('hits', (0, 61), tb + 2.5 * beat, beat * 0.5, q, 100)
            A.note('hits', (8, 80), tb, 4 * beat, ch[0] - 12 if ch[0] - 12 >= 33 else ch[0], 115)
        for bt, du, d in sty['motifA'][:8]:
            A.note('hits', (0, 10), t + bt * beat, du * beat, ms.deg(d) + 12, 95)
        endt = t + 12 * beat
        for q in voice(hs2.chord(0), 55, 79, 5):
            A.note('hits', (0, 61), endt, 0.9, q, 120)
        A.drum('hits', 48, endt, K.CRASH, 115)
        A.note('hits', (0, 47), endt, 1.0, 45, 120)
    else:
        raise KeyError(kind)
