"""Render note data with a General MIDI soundfont (MuseScore General, MIT licence) through FluidSynth.

A Part is one instrument: notes are (start_s, dur_s, pitch, velocity), ccs are (t, controller, value),
bends are (t, value in -8192..8191). Times are absolute seconds; the MIDI file uses 120 BPM / 960 ppq,
so 1 s = 1920 ticks exactly. Rendering is cached by content hash.
"""
import hashlib
import os
import subprocess
from dataclasses import dataclass, field

import mido
import numpy as np
import soundfile as sf

from .dsp import SR

SOUNDFONT = '/usr/share/sounds/sf3/MuseScore_General_Full.sf3'
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.cache', 'sf')
TPS = 1920  # ticks per second


@dataclass
class Part:
    name: str
    program: int = 0
    bank: int = 0
    drum: bool = False          # channel 10; program selects the kit (0 standard, 25 TR-808, 48 orchestra, 56 marching snare ...)
    notes: list = field(default_factory=list)
    ccs: list = field(default_factory=list)
    bends: list = field(default_factory=list)
    volume: int = 100           # CC7
    pan: int = 64               # CC10

    def n(self, t, dur, pitch, vel=90):
        if dur > 0 and 0 <= pitch <= 127:
            self.notes.append((float(t), float(dur), int(pitch), int(max(1, min(127, vel)))))
        return self

    def cc(self, t, ctl, val):
        self.ccs.append((float(t), int(ctl), int(max(0, min(127, val)))))
        return self

    def swell(self, t0, t1, v0, v1, steps=24, ctl=11):
        for k in range(steps + 1):
            u = k / steps
            self.cc(t0 + (t1 - t0) * u, ctl, v0 + (v1 - v0) * u)
        return self


def _track(part, ch):
    ev = []
    if not part.drum:
        ev.append((0, 0, mido.Message('control_change', channel=ch, control=0, value=part.bank)))
        ev.append((0, 1, mido.Message('control_change', channel=ch, control=32, value=0)))
    ev.append((0, 2, mido.Message('program_change', channel=ch, program=part.program)))
    ev.append((0, 3, mido.Message('control_change', channel=ch, control=7, value=part.volume)))
    ev.append((0, 4, mido.Message('control_change', channel=ch, control=10, value=part.pan)))
    ev.append((0, 5, mido.Message('control_change', channel=ch, control=11, value=127)))
    for t, ctl, val in part.ccs:
        ev.append((int(t * TPS), 6, mido.Message('control_change', channel=ch, control=ctl, value=val)))
    for t, val in part.bends:
        ev.append((int(t * TPS), 6, mido.Message('pitchwheel', channel=ch, pitch=int(max(-8192, min(8191, val))))))
    for t, d, p, v in part.notes:
        a = int(t * TPS)
        b = max(a + 1, int((t + d) * TPS))
        ev.append((a, 8, mido.Message('note_on', channel=ch, note=p, velocity=v)))
        ev.append((b, 7, mido.Message('note_off', channel=ch, note=p, velocity=0)))
    ev.sort(key=lambda e: (e[0], e[1]))
    tr = mido.MidiTrack()
    last = 0
    for tick, _, msg in ev:
        msg.time = tick - last
        last = tick
        tr.append(msg)
    return tr


def _files(parts):
    """Group parts into MIDI files: <=15 melodic channels, one drum kit per file."""
    melodic = [p for p in parts if not p.drum and p.notes]
    drums = [p for p in parts if p.drum and p.notes]
    kits = {}
    for p in drums:
        kits.setdefault(p.program, []).append(p)
    groups = [melodic[i:i + 15] for i in range(0, len(melodic), 15)] or [[]]
    out = []
    for gi, g in enumerate(groups):
        out.append((g, None))
    for k, ps in kits.items():
        merged = Part('drums_%d' % k, program=k, drum=True, notes=sum((p.notes for p in ps), []),
                      ccs=sum((p.ccs for p in ps), []), volume=ps[0].volume)
        out.append(([], merged))
    return [o for o in out if o[0] or o[1]]


def _write(melodic, drum, path):
    mid = mido.MidiFile(ticks_per_beat=960)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    mid.tracks.append(meta)
    chans = [c for c in range(16) if c != 9]
    for p, ch in zip(melodic, chans):
        mid.tracks.append(_track(p, ch))
    if drum is not None:
        mid.tracks.append(_track(drum, 9))
    mid.save(path)


def render(parts, duration=None, gain=0.45, soundfont=SOUNDFONT):
    """Render parts to a stereo float32 array at 48 kHz (cached)."""
    os.makedirs(CACHE, exist_ok=True)
    total = None
    for melodic, drum in _files(parts):
        tmp = os.path.join(CACHE, 'tmp_%d.mid' % os.getpid())
        _write(melodic, drum, tmp)
        h = hashlib.sha1(open(tmp, 'rb').read() + f'{gain}{soundfont}'.encode()).hexdigest()[:20]
        wav = os.path.join(CACHE, h + '.wav')
        if not os.path.exists(wav):
            r = subprocess.run(['fluidsynth', '-ni', '-q', '-R', '0', '-C', '0', '-g', str(gain), '-r', str(SR), '-O', 'float',
                                '-T', 'wav', '-o', 'synth.polyphony=2048', '-F', wav + '.part', soundfont, tmp],
                               capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError('fluidsynth failed: ' + r.stderr[-400:])
            os.replace(wav + '.part', wav)
        x, sr = sf.read(wav, dtype='float32', always_2d=True)
        assert sr == SR
        if total is None:
            total = x
        else:
            n = max(len(total), len(x))
            a = np.zeros((n, 2), np.float32)
            a[:len(total)] += total
            a[:len(x)] += x
            total = a
    if total is None:
        total = np.zeros((1, 2), np.float32)
    if duration is not None:
        n = int(round(duration * SR))
        if len(total) < n:
            total = np.concatenate([total, np.zeros((n - len(total), 2), np.float32)])
        total = total[:n]
    return total


# GM drum map (channel 10)
KICK, KICK2, STICK, SNARE, CLAP, SNARE2 = 35, 36, 37, 38, 39, 40
TOM_LF, HAT, TOM_HF, PEDAL, TOM_L, OHAT, TOM_LM, TOM_HM, CRASH, TOM_H, RIDE, CHINA = 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52
RIDE_BELL, TAMB, SPLASH, COWBELL, CRASH2 = 53, 54, 55, 56, 57
BONGO_H, BONGO_L, CONGA_M, CONGA_H, CONGA_L = 60, 61, 62, 63, 64
CLAVES, WOOD_H, WOOD_L, TRI_M, TRI_O, SHAKER = 75, 76, 77, 80, 81, 70
SCRATCH_PUSH, SCRATCH_PULL, STICKS = 29, 30, 31
