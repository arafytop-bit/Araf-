"""v3 sound design: one bed per entry (cut on the downbeat at each title), SFX keyed to the rendered events,
ambience per real-photo location, silence before the big reveals, voice chain, light mastering to -14 LUFS / -1 dBTP.

Sources, in order of preference for every sound:
  1. the user's uploads (music beds + SFX)               assets/user_audio/
  2. recorded effects from Wikimedia Commons (CC BY 4.0)   assets/sfx/          (credited in the description)
  3. engine.sound.trap beds / engine.sound.sfx procedural fallbacks

  python3 sound3.py            -> v3/mix.wav (+ stems/, sound_report.json)
"""
import glob
import json
import math
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from engine.sound.dsp import SR, n_of, place, to_stereo, pan as pan_mono, reverb, lp, hp, db, rms_db  # noqa: E402
from engine.sound import trap, sfx as X, design as DZ  # noqa: E402
from engine.sound.mixer import load_voice, process_voice, speech_activity, loudnorm  # noqa: E402
import timeline as TL  # noqa: E402
from timeline import FPS  # noqa: E402

ASSETS = os.path.join(os.path.dirname(HERE), 'assets')
USER_AUDIO = os.path.join(ASSETS, 'user_audio')
CC_SFX = os.path.join(ASSETS, 'sfx')


# ======================= sample library =======================
def decode(path):
    """Any audio file -> stereo float32 at 48 kHz (ffmpeg)."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


_CACHE = {}

# name -> filename prefixes searched in user_audio/ then sfx/ (first match wins), else procedural X.get(name)
ALIASES = {
    'hit_title': ['hit_title', 'cinematic_hit', 'impact_big', 'boom'],
    'hit_word': ['hit_word', 'hit_small', 'impact_small', 'punch'],
    'callout': ['callout', 'text_hit', 'impact_small', 'hit_small'],
    'whoosh': ['whoosh', 'swoosh'],
    'whoosh_short': ['whoosh_short', 'swish', 'whoosh'],
    'whoosh_long': ['whoosh_long', 'whoosh_big', 'whoosh'],
    'pop': ['pop', 'click'],
    'pop_soft': ['pop_soft', 'pop', 'click'],
    'impact': ['impact', 'boom', 'hit'],
    'thud': ['thud', 'impact_small', 'punch'],
    'stamp': ['stamp', 'impact_big', 'boom'],
    'riser': ['riser', 'reverse_cymbal'],
    'ding': ['ding', 'bell'],
    'arrow': ['arrow'],
    'arrow_hit': ['arrow_hit', 'arrow_impact', 'thunk'],
    'sword_clash': ['sword_clash', 'sword'],
    'door_crash': ['door_crash', 'wood_crash', 'wood'],
    'metal_clang': ['metal_clang', 'metal', 'chains'],
    'splash': ['splash', 'water'],
    'wood_crack': ['wood_crack', 'wood_crash', 'wood'],
    'coins': ['coins', 'coin', 'cash'],
    'cannon': ['cannon', 'explosion'],
    'gunshot': ['gunshot', 'gun', 'musket'],
    'crowd_cheer': ['crowd_cheer', 'cheer', 'crowd'],
    'war_drum': ['war_drum', 'taiko', 'drum'],
    'record_scratch': ['record_scratch', 'scratch'],
}


def _find(dirs, name):
    for d in dirs:
        for pref in ALIASES.get(name, [name]):
            hits = sorted(glob.glob(os.path.join(d, pref + '*')))
            hits = [h for h in hits if os.path.splitext(h)[1].lower() in ('.wav', '.mp3', '.ogg', '.flac', '.aif', '.aiff', '.m4a')]
            if hits:
                return hits
    return []


def sample(name, seed=0):
    """user upload > designed editing-kit sound > recorded CC BY foley (Commons) > procedural fallback."""
    key = (name, seed)
    if key in _CACHE:
        return _CACHE[key]
    x = None
    hits = _find([USER_AUDIO], name)
    if hits:
        x = decode(hits[seed % len(hits)])
        SOURCES[name] = 'user'
    elif name in DZ.DESIGNED:
        x = DZ.DESIGNED[name](seed=seed % 3)
        SOURCES[name] = 'designed'
    else:
        hits = _find([CC_SFX], name)
        if hits:
            x = decode(hits[seed % len(hits)])
            SOURCES[name] = 'commons:' + os.path.basename(hits[seed % len(hits)])
        elif name == 'war_drum':
            x = to_stereo(trap.taiko(seed % 3))
            SOURCES[name] = 'designed'
        else:
            x = to_stereo(X.get(name if name in X.GEN else 'pop', seed=seed))
            SOURCES[name] = 'procedural'
    x = x.astype(np.float32)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    _CACHE[key] = x
    return x


SOURCES = {}


# ======================= events from the compiled timeline =======================
def tsec(f):
    return f / FPS


def collect(tl, calls, stamps, overlays):
    """-> list of (t, name, gain_db, pan)"""
    ev = []

    def E(f, name, g, p=0.0):
        if f is not None:
            ev.append((tsec(f), name, g, p))
    for b in tl:
        k = b['kind']
        f0 = b['f0']
        if k == 'title':
            E(f0 - 9, 'whoosh_long', -14, 0.0)
            E(f0, 'hit_title', -1, 0.0)
        elif k == 'kinetic':
            for ln in b['lines']:
                for w in ln['words']:
                    E(w['at'], 'hit_word', -9 if not w.get('red') else -6, 0.0)
            for a in b.get('actors', []):
                if a.get('enter'):
                    E(a['enter']['at'], 'whoosh_short', -20, 0.4)
        for ln in b.get('klines', []):
            for w in ln['words']:
                E(w['at'], 'hit_word', -8 if not w.get('red') else -5, 0.0)
        if k == 'text':
            for i, ln in enumerate(b['lines']):
                at = ln[3] if len(ln) > 3 and ln[3] is not None else f0 + 3 * i
                E(at, 'impact' if b.get('anim') == 'slam' else 'callout', -6 if b.get('anim') == 'slam' else -12, 0.0)
        elif k == 'list':
            for it in b['items']:
                E(it.get('at'), 'pop', -14 if it.get('mark', b.get('mark')) != 'x' else -12, 0.0)
        elif k == 'count':
            E(f0, 'riser', -16)
            E(f0 + b.get('dur', 26), 'ding', -12)
        elif k == 'quote':
            E(f0, 'riser', -20)
        elif k == 'versus':
            for side, p in (('left', -0.4), ('right', 0.4)):
                E(b[side].get('at', f0), 'whoosh_short', -14, p)
        elif k == 'trio':
            for i, pp in enumerate(b['people']):
                E(pp.get('at'), 'pop', -16, -0.4 + 0.4 * i)
                if pp.get('crown') is not None:
                    E(pp['crown'] + 7, 'ding', -12)
        elif k == 'gallery':
            for pp in b['people']:
                E(pp['at'], 'callout', -12)
        elif k == 'map':
            for st in b.get('stops', [])[1:]:
                E(st[2], 'whoosh_short', -16)
            for st in b.get('stops', [])[:1] + [tuple(p) for p in b.get('pins', [])]:
                E(st[2], 'pop', -16)
        elif k == 'ships':
            E(f0, 'pop', -14)
            if b.get('change') is not None:
                E(b['change'], 'whoosh_long', -10)
        elif k == 'photo':
            for mk in b.get('marks', []):
                E(mk[-1], 'pop_soft' if mk[0] == 'label' else 'whoosh_short', -18)
        elif k == 'formation':
            E(b.get('wrap'), 'whoosh_long', -10)
            E(b.get('wipe'), 'cannon', -8)
        elif k == 'sub':
            E(f0, 'pop', -10)
        elif k == 'album':
            E(f0, 'impact', -6)
        elif k == 'comment':
            for j in range(8):
                E(f0 + 6 + j, 'pop_soft', -26, 0.2)
        elif k == 'end':
            E(b['logo'], 'whoosh', -12)
            E(b['logo'] + 9, 'thud', -8)
            E(b['logo'] + 15, 'pop', -8)
            if b.get('slot_at'):
                E(b['slot_at'], 'pop', -12)
        # characters, props, fx inside scenes
        first_pop = True
        for a in b.get('actors', []):
            en = a.get('enter') or {}
            if en.get('kind') == 'run':
                E(en['at'], 'whoosh_short', -18, -0.3)
            elif en.get('kind') == 'drop':
                E(en['at'] + int(en.get('dur', 13) * 0.55), 'thud', -6)
            elif en.get('kind') == 'pop' and first_pop:
                E(en['at'], 'pop_soft', -20)
                first_pop = False
            for ac in a.get('acts', []):
                if ac['kind'] in ('fall', 'die'):
                    E(ac['at'] + ac.get('dur', 9), 'thud', -7)
            ex = a.get('exit') or {}
            if ex.get('kind') == 'run':
                E(ex['at'], 'whoosh_short', -18, 0.3)
        for p in b.get('props', []):
            en = p.get('enter') or {}
            ex = p.get('exit') or {}
            if p['name'] == 'arrow' and en.get('kind') == 'fly':
                E(en['at'], 'arrow', -10, 0.5)
                E(en['at'] + en.get('dur', 7), 'arrow_hit', -8)
            elif p['name'] == 'coin' and en.get('kind') == 'fly':
                E(en['at'], 'coins', -18)
            elif p['name'] == 'tombstone' and en.get('kind') == 'drop':
                E(en['at'] + int(en.get('dur', 13) * 0.55), 'thud', -4)
            elif p['name'] == 'wreath' and en.get('kind') == 'fly' and en.get('until') is not None:
                E(en['until'], 'ding', -12)
            elif en.get('kind') == 'pop':
                E(en['at'], 'pop_soft', -22)
            if p['name'] == 'jail' and ex.get('kind') == 'fly':
                E(ex['at'], 'metal_clang', -6)
            if p['name'] == 'door' and ex.get('kind') == 'fly':
                E(ex['at'], 'door_crash', -4)
            if p['name'] == 'jail' and en.get('kind') == 'drop':
                E(en['at'] + int(en.get('dur', 13) * 0.55), 'metal_clang', -6)
        for fx in b.get('fx', []) + b.get('fx_under', []):
            at = fx.get('at', f0)
            if fx['kind'] == 'split':
                E(at, 'wood_crack', -6)
                E(at + 8, 'splash', -8)
            elif fx['kind'] == 'rain_gold':
                E(at, 'coins', -12)
            elif fx['kind'] == 'censor':
                E(at, 'pop', -12)
            elif fx['kind'] == 'pour':
                E(at, 'sizzle', -14)
            elif fx['kind'] == 'bodycam':
                E(f0, 'rec_beep', -16)
            elif fx['kind'] == 'flash' and not b.get('cam'):
                E(at, 'impact', -8)
        for c in b.get('cam', []):
            if c[0] == 'shake':
                E(c[1], 'impact', -7)
            elif c[0] == 'punch':
                E(c[1], 'hit_word', -10)
        if b.get('drum'):                              # war drum synced to the drummer's arms (pose phase = 2*pi*f/14)
            for f in range(b['f0'], b['f1']):
                if f % 7 == 0:
                    ev.append((tsec(f), 'war_drum', -11 if (f // 7) % 2 else -13, 0.25))
    for cl in calls:
        ev.append((tsec(cl['f0']), 'callout', -11, 0.0))
    for st in stamps:
        ev.append((tsec(st['f0']), 'stamp', -2, 0.0))
        ev.append((tsec(st['f0']) + 0.02, 'impact', -8, 0.0))
    for o in overlays:
        if o['kind'] == 'timer':
            ev.append((tsec(o['f0']), 'pop', -12, 0.5))
            if o.get('stop'):
                ev.append((tsec(o['stop']), 'ding', -10, 0.5))
    ev.sort()
    # de-clutter: within 70 ms keep only the loudest event
    out = []
    for e in ev:
        if out and e[0] - out[-1][0] < 0.07 and e[1] != 'war_drum' and out[-1][1] != 'war_drum':
            if e[2] > out[-1][2]:
                out[-1] = e
            continue
        out.append(e)
    return out


# ======================= ambience per location =======================
AMB = {'olympia_stadium': ('stadium', -31), 'puszta': ('wind', -33), 'grey_cattle': ('wind', -33), 'stamford_river': ('river', -31),
       'yorkshire_field': ('birds', -33), 'turtle_ship': ('sea', -28), 'night_sea': ('sea', -28), 'fire_rome': ('fire', -28),
       'carrhae': ('desert', -31), 'feast_attila': ('feast', -32), 'hagia_sophia': ('hall', -34), 'gyeongbokgung': ('wind', -34),
       'golden_horn': ('sea', -31), 'fjord': ('wind', -32), 'norway_forest': ('birds', -32), 'dungeon': ('hall', -32),
       'roman_forum': ('wind', -34), 'greek_theater': ('wind', -34), 'old_door': ('hall', -34), 'st_sophia_kyiv': ('birds', -34),
       'seoul_gwanghwamun': ('wind', -34), 'olav_stiklestad': ('battle', -30), 'stamford_arbo': ('battle', -30)}


def ambience_segments(tl):
    segs = []
    for b in tl:
        key = b.get('bg') if b['kind'] in ('scene', 'ships', 'formation') else (b.get('img') if b['kind'] == 'photo' and b.get('mode') == 'full' else None)
        if key in AMB:
            segs.append((tsec(b['f0']), tsec(b['f1']), AMB[key][0], AMB[key][1]))
        if any(fx['kind'] == 'fire' for fx in b.get('fx', [])):
            segs.append((tsec(b['f0']), tsec(b['f1']), 'fire', -30))
    return segs


# ======================= music: one bed per entry =======================
def sections(tl):
    titles = [b for b in tl if b['kind'] == 'title']
    mid_i = TL.find('Okay, quick pause')
    out_i = TL.find("So, that's part one")
    bounds = [(0.0, 'intro')]
    names = ['harald', 'attila', 'crassus', 'arrichion']
    for b, nm in zip(titles[:4], names):
        bounds.append((tsec(b['f0']), nm))
    bounds.append((TL.WORDS[mid_i]['s'] - 0.25, 'midroll'))
    bounds.append((tsec(titles[4]['f0']), 'yi'))
    bounds.append((TL.WORDS[out_i]['s'] - 0.15, 'outro'))
    segs = []
    for k, (t0, nm) in enumerate(bounds):
        t1 = bounds[k + 1][0] if k + 1 < len(bounds) else TL.LAST_WORD_END + 0.1
        segs.append((t0, t1, nm))
    return segs


def user_bed(name):
    """A user-uploaded bed for this section, if any (filenames containing the section name, or generic 'bed'/'music')."""
    if not os.path.isdir(USER_AUDIO):
        return None
    for pat in (f'*{name}*', '*bed*', '*music*', '*beat*'):
        hits = [h for h in sorted(glob.glob(os.path.join(USER_AUDIO, pat)))
                if os.path.splitext(h)[1].lower() in ('.wav', '.mp3', '.flac', '.ogg', '.m4a')]
        if hits:
            return hits[0]
    return None


def loop_to(x, dur, xfade=0.05):
    n = n_of(dur)
    if len(x) >= n:
        return x[:n]
    out = np.zeros((n, 2), np.float32)
    i = 0
    f = n_of(xfade)
    while i < n:
        k = min(len(x), n - i)
        seg = x[:k].copy()
        if i > 0 and k > f:
            seg[:f] *= np.linspace(0, 1, f)[:, None]
            out[i - f:i] *= np.linspace(1, 0, f)[:, None] if i - f >= 0 else 1
        out[i:i + k] += seg
        i += k - f if k > f else k
    return out


def music_bus(tl, total_s, reveals):
    mus = np.zeros((n_of(total_s), 2), np.float32)
    used = []
    segs = sections(tl)
    for k, (t0, t1, nm) in enumerate(segs):
        end = t1
        if k + 1 < len(segs) and segs[k + 1][2] == 'yi':
            end = t1 - 0.65                          # the music drops out completely before the final entry (reference)
        dur = max(0.5, end - t0)
        ub = user_bed(nm)
        if ub:
            x = loop_to(decode(ub), dur + 0.2)
            used.append((nm, os.path.basename(ub)))
        else:
            x = trap.bed(nm, dur + 0.2, seed=k + 3, intro_bars=0 if nm != 'midroll' else 1)
            used.append((nm, f'trap:{nm}'))
        x = x[: n_of(dur)].copy()
        fi, fo = n_of(0.01 if k else 0.002), n_of(0.12)
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        place(mus, x, t0, 1.0)
    # silence before the biggest reveals: music dips to nothing, then comes back on the payoff
    g = np.ones(len(mus), np.float32)
    for (a, b) in reveals:
        i0, i1 = n_of(a), n_of(b)
        f = n_of(0.25)
        g[max(0, i0 - f):i0] = np.minimum(g[max(0, i0 - f):i0], np.linspace(1, 0, min(f, i0)))
        g[i0:i1] = 0.0
        g[i1:i1 + f] = np.minimum(g[i1:i1 + f], np.linspace(0, 1, min(f, len(g) - i1)))
    mus *= g[:, None]
    # outro sting: punchy beat 6.5 s, entering 0.2 s after the last word (reference end screen)
    st = trap.sting('outro', 6.5, seed=9)
    place(mus, st, TL.LAST_WORD_END + 0.2, 1.0)
    return mus, used


def widen_stereo(x, amount=0.55):
    """Mid/side widening above 300 Hz (bass stays mono): library beds are wide, ours were too narrow (corr 0.997)."""
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2
    d = n_of(0.012)
    hi = hp(mid, 300)
    dec = np.concatenate([np.zeros(d, np.float32), hi[:-d]]) - np.concatenate([np.zeros(2 * d, np.float32), hi[:-2 * d]])
    side = side + amount * dec.astype(np.float32)
    return np.stack([mid + side, mid - side], 1).astype(np.float32)


def comedic_dropouts():
    """Short music drop-outs on the punchlines (the reference has 43 silences >= 150 ms; the last mix had 7)."""
    lines = ["That's it", 'Embarrassing', 'At all', 'Respectfully: what', "That's a threat", "They're not", 'please leave',
             "That's the entire plan", 'Per year', 'Translation', "Yi didn't", 'Ever', 'How rich', 'Again']
    out = []
    cur = 0
    for ln in lines:
        try:
            i = TL.find(ln, 0)
        except KeyError:
            continue
        n = len([x for x in ln.split() if TL.norm(x)])
        a = TL.WORDS[i]['s'] - 0.06
        b = TL.WORDS[i + n - 1]['e'] + 0.22
        out.append((a, b))
    return out


def reveal_windows():
    """(t0, t1) spans where the music cuts out to make room for the biggest reveals."""
    def w(i):
        return TL.WORDS[i]
    spans = []
    i = TL.find("That's it")                         # Harald: the arrow -> "That's it." (silence on the beat)
    spans.append((w(i)['s'] - 0.12, w(i + 1)['e'] + 0.35))
    i = TL.find('They crowned the corpse')            # Arrichion payoff
    spans.append((w(i)['s'] - 0.9, w(i)['s'] - 0.02))
    i = TL.find('And his last words were')            # Yi: silence under his last words, the drum brings it back
    j = TL.find('He was fifty-three')
    spans.append((w(i)['s'] - 0.1, w(j)['s'] - 0.05))
    i = TL.find('Nobody knew')                        # "Nobody knew. Not his sailors. Not the enemy." over the drum only
    j = TL.find('The fleet fought on')
    spans.append((w(i)['s'] - 0.05, w(j)['s'] - 0.05))
    return spans


# ======================= mix =======================
def voice_chain(v):
    """HPF, de-mud, presence and air, gentle 1.8:1 compression, de-ess. Dry and close like the reference narrator."""
    from pedalboard import Pedalboard, Compressor, HighpassFilter, PeakFilter, HighShelfFilter, LowShelfFilter
    from engine.sound.mixer import deess
    board = Pedalboard([HighpassFilter(80), LowShelfFilter(140, 1.5, 0.7), PeakFilter(260, -2.5, 1.0), PeakFilter(3300, 2.5, 0.9),
                        HighShelfFilter(9500, 2.0, 0.7), Compressor(threshold_db=-21, ratio=1.8, attack_ms=8, release_ms=120)])
    y = board(v[None, :], SR)[0]
    return deess(y)


def voice_ride(n):
    """Sentence-level vocal ride (what a mix engineer does for delivery): punchlines/titles up, intimate lines down."""
    import re
    g = np.zeros(n, np.float32)
    serious = re.compile(r"\b(son|mother|mourn|last words|weeping|beating his chest|announce my death|should have died|crying|blood of men)\b", re.I)
    titles = {'Harald Hardrada.', 'Attila the Hun.', 'Marcus Licinius Crassus.', 'Arrichion of Phigalia.', 'Yi Sun-sin.'}
    for s_ in TL.SENTS:
        txt = s_['text'].strip()
        words = len(txt.split())
        if txt in titles:
            val = 2.5
        elif serious.search(txt):
            val = -2.5
        elif words <= 4 and txt.endswith(('.', '?', '!')):
            val = 1.8
        elif txt.endswith('?'):
            val = 0.8
        elif words >= 22:
            val = -0.8
        else:
            val = 0.0
        a, b = n_of(s_['start'] - 0.03), n_of(s_['end'] + 0.03)
        g[max(0, a):min(n, b)] = val
    # smooth (60 ms) so rides never click
    k = n_of(0.06)
    g = np.convolve(g, np.ones(k) / k, 'same').astype(np.float32)
    return (10 ** (g / 20)).astype(np.float32)


def title_swells(tl, n):
    """Music lifts +4 dB for ~2 s after each title hit, easing back (the beat drops on the card)."""
    g = np.ones(n, np.float32)
    for b in tl:
        if b['kind'] == 'title':
            i0 = n_of(tsec(b['f0']))
            L = n_of(2.2)
            seg = 10 ** ((4.0 * np.exp(-np.arange(L) / n_of(0.9))) / 20)
            g[i0:i0 + L] *= seg[: max(0, min(L, n - i0))]
    return g


def mix(out_path=None):
    import build3 as B3
    tl, calls, stamps, _ = B3.compile_all()
    overlays = B3.OVERLAYS
    total = TL.TOTAL_S
    n = n_of(total)
    report = {}
    # voice
    v = load_voice(os.path.join(HERE, 'voice.wav'), TL.VOICE_OFFSET, total)
    v = voice_chain(v)
    v = v * voice_ride(len(v))
    act = speech_activity(v)
    voice = np.stack([v, v], 1)
    # music
    reveals = reveal_windows() + comedic_dropouts()
    mus, used = music_bus(tl, total, reveals)
    report['beds'] = used
    # level: bed sits ~17 LU under the voice before ducking; ducks another 5 dB under speech
    v_l = rms_db(v[act > 0.5]) if (act > 0.5).any() else rms_db(v)
    m_l = rms_db(mus.mean(1)[np.abs(mus.mean(1)) > 1e-5]) if np.any(np.abs(mus) > 1e-5) else -60
    mus = widen_stereo(mus)
    mus *= db((v_l - 15.0) - m_l)
    duck = 1.0 - (1 - db(-5.0)) * act
    mus *= duck[:, None]
    mus *= title_swells(tl, len(mus))[:, None]
    # sfx
    events = collect(tl, calls, stamps, overlays)
    fxbus = np.zeros((n, 2), np.float32)
    from engine.sound.mixer import loud_window_db
    lvl_cache = {}
    for t, name, g, p in events:
        sd = int(t * 7) % 5
        s_ = sample(name, seed=sd)
        if (name, sd) not in lvl_cache:
            lvl_cache[(name, sd)] = loud_window_db(s_, 0.1)
        if p:
            s_ = s_ * np.array([math.cos((p + 1) * math.pi / 4), math.sin((p + 1) * math.pi / 4)], np.float32)[None, :] * math.sqrt(2)
        place(fxbus, s_, t, db(v_l + g - lvl_cache[(name, sd)]))
    fx_wet = reverb(fxbus, 'room', wet=0.12)[:n]
    # ambience
    amb = np.zeros((n, 2), np.float32)
    for t0, t1, kind, g in ambience_segments(tl):
        d = t1 - t0
        if d < 0.3:
            continue
        a = to_stereo(X.bed(kind, d, seed=int(t0) % 7))[: n_of(d)].copy()
        f = min(n_of(0.3), len(a) // 3)
        a[:f] *= np.linspace(0, 1, f)[:, None]
        a[-f:] *= np.linspace(1, 0, f)[:, None]
        a *= db(v_l + g - rms_db(a.mean(1)))
        place(amb, a, t0, 1.0)
    master = voice + mus + fx_wet + amb
    # light glue (no heavy bus compression: the last version measured LRA 1.8 LU vs the reference 3.2)
    from pedalboard import Pedalboard, Compressor, HighpassFilter
    master = Pedalboard([HighpassFilter(28)])(master.T.copy(), SR).T
    raw = os.path.join(HERE, 'mix_raw.wav')
    sf.write(raw, master.astype(np.float32), SR, subtype='FLOAT')
    out_path = out_path or os.path.join(HERE, 'mix.wav')
    loud = loudnorm(raw, out_path, I=-14.0, TP=-1.2)
    os.remove(raw)
    os.makedirs(os.path.join(HERE, 'stems'), exist_ok=True)
    for nm, x in (('voice', voice), ('music', mus), ('sfx', fx_wet), ('amb', amb)):
        sf.write(os.path.join(HERE, 'stems', nm + '.wav'), x.astype(np.float32), SR, subtype='PCM_24')
    report['sfx_sources'] = SOURCES
    report.update(loudness=loud, events=len(events), events_per_min=round(len(events) / (total / 60), 1),
                  reveals=[(round(a, 2), round(b, 2)) for a, b in reveals])
    json.dump(report, open(os.path.join(HERE, 'sound_report.json'), 'w'), indent=1, default=str)
    print(json.dumps(report, indent=1, default=str))
    return out_path


if __name__ == '__main__':
    mix()
