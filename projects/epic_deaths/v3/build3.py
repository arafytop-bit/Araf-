"""v3 build: compile the word-keyed board, plan host shots, lay out overlays, render, QA.

  python3 build3.py plan                       # compile + stats + layout QA (no rendering)
  python3 build3.py stills F1,F2,...           # render frames to v3/stills/
  python3 build3.py range T0 T1 OUT.mp4        # render a time range (preview quality)
  python3 build3.py prender N                  # final-quality parallel render -> v3/video_noaudio.mp4
"""
import json
import math
import os
import random
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..')))

import skia  # noqa: E402
import timeline as TL  # noqa: E402
from timeline import FPS, W, H, fr, find, cut_frame, word_on, resolve_all, WORDS, SENTS, TOTAL_F  # noqa: E402
import shots as S  # noqa: E402
from engine.premium import overlays as O, look as L, motion as M  # noqa: E402
import board as BD  # noqa: E402

MAX_HOLD = int(3.5 * FPS)
LENIENT = os.environ.get('V3_LENIENT') == '1'
MISSING = set()
NO_CALLOUT_KINDS = {'title', 'kinetic', 'text', 'list', 'quote', 'band', 'trio', 'versus', 'end'}


# ---------------- compile ----------------
WI = {}


def resolve_sequence():
    """Resolve every trigger (beats, callouts, host hints, stamps, overlays) in board order with one running cursor,
    so a short cue ('Again', 'Ever.') can only match narration AFTER the previous cue."""
    items = [it for lst in (BD.BEATS, BD.CALLS, BD.HOSTS, BD.STAMPS, BD.OVERLAYS) for it in lst]
    items.sort(key=lambda it: it['seq'])
    cursor = 0
    for it in items:
        start = max(0, cursor - 16)          # small slack: a callout may be written after the beat of its own sentence
        if it.get('from'):
            start = find(it['from'], start)
        i = find(it['trigger'], start)
        WI[it['seq']] = i
        cursor = max(cursor, i)


def compile_beats():
    if not WI:
        resolve_sequence()
    beats = []
    for b in BD.BEATS:
        i = WI[b['seq']]
        b = resolve_all(dict(b), i)
        b['wi'] = i
        b['f0'] = cut_frame(i) + b.get('shift', 0)
        if b.get('until') is not None:
            if isinstance(b['until'], int):
                b['f1'] = b['until']
            else:
                j = find(b['until'], i + 1)
                if j - i > 120:
                    raise ValueError(f"'until' {b['until']!r} of beat {b['trigger']!r} resolves {j - i} words later (typo?)")
                b['f1'] = cut_frame(j)
        elif b.get('hold'):
            b['f1'] = b['f0'] + int(round(b['hold'] * FPS))
        else:
            s = SENTS[WORDS[i]['sid']] if False else None
            b['f1'] = b['f0'] + 60
        if b['kind'] == 'end':
            b['f1'] = TOTAL_F
            b['logo'] = fr(TL.LAST_WORD_END + 0.2)
        if b['kind'] == 'quote':
            b['word_frames'] = quote_frames(b, i)
        missing = []
        if b['kind'] in ('photo', 'title') and not L.exists(b.get('img')):
            missing.append(b.get('img'))
        if b['kind'] in ('scene', 'text', 'list', 'quote', 'count') and b.get('bg') and not L.exists(b['bg']):
            missing.append(b['bg'])
        for p_ in b.get('people', []):
            if not L.exists(p_['img']):
                missing.append(p_['img'])
        if missing:
            if not LENIENT:
                raise FileNotFoundError(f"image missing for beat {b['trigger']!r}: {missing}")
            MISSING.update(missing)
            b['_missing'] = missing
            if b['kind'] == 'photo':
                b['kind'] = 'text'
                b['lines'] = [('MISSING IMAGE', 'red', 0.05 * H), (str(b.get('img')).upper(), 'white', 0.05 * H)]
            elif b['kind'] == 'title':
                b['img'] = 'harald_portrait'
            elif b.get('bg'):
                b['bg'] = None
            for p_ in b.get('people', []):
                if not L.exists(p_['img']):
                    p_['img'] = 'harald_portrait'
        beats.append(b)
    beats.sort(key=lambda b: b['f0'])
    for a, nb in zip(beats, beats[1:]):
        if a['f1'] > nb['f0']:
            a['f1'] = nb['f0']
        elif nb['f0'] - a['f1'] < 15:
            a['f1'] = nb['f0']              # never leave a sub-0.5 s host flash between two beats
    for b in beats:
        if b['f1'] - b['f0'] < 8:
            raise ValueError(f"beat too short ({b['f1'] - b['f0']} frames): {b['trigger']!r} at {TL.tc(b['f0'])}")
    return beats


def quote_frames(b, i):
    j = find(b['quote_at'], i) if b.get('quote_at') else i
    wf = []
    for qw in b['text'].split():
        if not TL.norm(qw):
            wf.append(wf[-1] if wf else word_on(j))
            continue
        try:
            j = find(qw, j)
            wf.append(word_on(j))
            j += 1
        except KeyError:
            wf.append(wf[-1] if wf else b['f0'])
    return wf


def compile_calls(beats):
    calls = []
    for cl in BD.CALLS:
        i = WI[cl['seq']]
        f0 = word_on(i) if not cl.get('cut') else cut_frame(i)
        f1 = cut_frame(find(cl['until'], i)) if cl.get('until') else f0 + int(cl['hold'] * FPS)
        calls.append(dict(cl, f0=f0, f1=f1))
    calls.sort(key=lambda c: c['f0'])
    for a, b in zip(calls, calls[1:]):
        a['f1'] = min(a['f1'], b['f0'])
    issues = []
    for cl in calls:                        # callouts never sit on top of text-led shots
        for b in beats:
            if b['kind'] in NO_CALLOUT_KINDS and b['f0'] < cl['f1'] and cl['f0'] < b['f1']:
                if cl['f0'] >= b['f0']:
                    issues.append(f"callout {cl['text']!r} at {TL.tc(cl['f0'])} starts inside a {b['kind']} beat")
                cl['f1'] = min(cl['f1'], b['f0']) if cl['f0'] < b['f0'] else cl['f0']
    calls = [c for c in calls if c['f1'] - c['f0'] >= 12]
    for cl in calls:                        # framed photos under a callout use the lowered layout
        for b in beats:
            if b['kind'] == 'photo' and b.get('mode', 'frame') != 'full' and b['f0'] < cl['f1'] and cl['f0'] < b['f1']:
                b['lowered'] = True
    return calls, issues


SENTI = [
    (r"\b(dies|died|dead|death|killed|blood|crucified|bullet|choked|executed|tortured|grave|corpse|severed|head)\b",
     ['shock', 'grimace', 'sad', 'talk']),
    (r"\b(insane|crazy|craziest|wild|ridiculous|legendary|epic|hardcore|unhinged)\b", ['shock', 'grin', 'talk', 'talk2']),
    (r"\b(respectfully|translation|leave|anyway|apparently|roughly|basically|literally|embarrassing|threat)\b",
     ['smug', 'skeptic', 'deadpan', 'talk']),
    (r"\?", ['skeptic', 'talk2', 'talk']),
    (r"\b(rich|richest|gold|fortune|money|subscription)\b", ['smug', 'grin', 'talk']),
]
DEFAULT_EXPR = ['talk', 'talk2', 'smile', 'talk', 'neutral', 'talk2', 'grin']
POSES = ['idle', 'hips', 'point', 'idle', 'hips', 'shrug', 'chin', 'wave']
FRAMES_CYCLE = ['M', 'CU', 'M', 'MS', 'M', 'CU']


def plan_hosts(beats, calls):
    rng = random.Random(7)
    gaps, t, prev = [], 0, None
    for b in beats:
        if b['f0'] > t:
            gaps.append((t, b['f0'], prev))
        if b['f1'] >= t:
            prev = b
        t = max(t, b['f1'])
    if t < TOTAL_F:
        gaps.append((t, TOTAL_F, prev))
    hints = []
    for h in BD.HOSTS:
        i = WI[h['seq']]
        hints.append((cut_frame(i), h))
    hosts = []
    last_framing = None
    sent_starts = [fr(s['start']) - 1 for s in SENTS]
    for g0, g1, pb in gaps:
        cuts = {g0}
        for f in sent_starts:
            if g0 + 45 <= f <= g1 - 30:
                cuts.add(f)
        for cl in calls:
            for f in (cl['f0'] - 1, cl['f1']):
                if g0 + 12 <= f <= g1 - 12:
                    cuts.add(f)
        for f, h in hints:
            if g0 + 10 <= f <= g1 - 10:
                cuts.add(f)
        cuts = sorted(cuts)
        merged = [cuts[0]]
        for f in cuts[1:]:
            if f - merged[-1] >= 24 or any(abs(f - (cl['f0'] - 1)) <= 1 for cl in calls):
                merged.append(f)
        cuts = merged + [g1]
        # max hold: split long sub-shots at word onsets
        final = [cuts[0]]
        for a, z in zip(cuts, cuts[1:]):
            cur = a
            while z - cur > MAX_HOLD:
                target = cur + min(int(2.6 * FPS), (z - cur) // 2)
                ons = [word_on(k) - 1 for k in TL.words_between(cur + 30, z - 30)]
                if not ons:
                    break
                nxt = min(ons, key=lambda x: abs(x - target))
                if nxt <= cur + 20:
                    break
                final.append(nxt)
                cur = nxt
            final.append(z)
        cuts = sorted(set(final))
        for k, (a, z) in enumerate(zip(cuts, cuts[1:])):
            if z - a < 6:
                continue
            hint = None
            for f, h in hints:
                if a - 6 <= f <= a + 10:
                    hint = h
            ws = TL.words_between(a, z)
            text = ' '.join(WORDS[w]['w'] for w in ws).lower()
            pool = DEFAULT_EXPR
            for pat, pl in SENTI:
                if re.search(pat, text):
                    pool = pl
                    break
            under_call = any(cl['f0'] - 2 <= z and a < cl['f1'] - 1 and cl['f0'] <= a + 3 for cl in calls) or \
                any(cl['f0'] < z and a < cl['f1'] for cl in calls)
            if under_call:
                framing = 'LOW'
            elif hint and hint.get('framing'):
                framing = hint['framing']
            else:
                dur = (z - a) / FPS
                opts = ['CU', 'ECU'] if dur < 1.3 and rng.random() < 0.25 else (['CU', 'MS'] if dur < 2.0 else ['M', 'MS', 'CU'])
                if rng.random() < 0.45:
                    opts = ['M']
                opts = [o for o in opts if o != last_framing] or ['M' if last_framing != 'M' else 'CU']
                framing = rng.choice(opts)
            if framing == last_framing and not (hint and hint.get('framing')):
                framing = {'M': 'CU', 'CU': 'M', 'MS': 'M', 'ECU': 'M', 'LOW': 'LOW'}[framing]
            pose = (hint or {}).get('pose') or rng.choice(POSES)
            first = (hint or {}).get('expr') or rng.choice(pool)
            exprs = [(a, first)]
            lastf = a
            for w in ws:
                f = word_on(w) - 1
                if f - lastf >= rng.randint(26, 38) and z - f > 10:
                    nxt = rng.choice([e for e in pool if e != exprs[-1][1]] or pool)
                    exprs.append((f, nxt))
                    lastf = f
            over = None
            if pb is not None and pb['kind'] == 'photo' and pb['f1'] == a and k == 0 and rng.random() < 0.3:
                over = pb['img']
            hosts.append(dict(kind='host', f0=a, f1=z, framing=framing, pose=pose, exprs=exprs, over=over,
                              look=(hint or {}).get('look', (0.0, 0.0)), trigger=f'host@{TL.tc(a)}',
                              pip=(hint or {}).get('pip'), pip_at=a))
            last_framing = framing
        last_framing = None if g1 - g0 > 0 else last_framing
    return hosts


def compile_all():
    beats = compile_beats()
    calls, issues = compile_calls(beats)
    hosts = plan_hosts(beats, calls)
    tl = sorted(beats + hosts, key=lambda b: b['f0'])
    for a, b in zip(tl, tl[1:]):
        if a['kind'] == 'host' and b['kind'] == 'host' and a['framing'] == b['framing'] and a['f1'] == b['f0']:
            b['framing'] = {'M': 'CU', 'CU': 'M', 'MS': 'M', 'ECU': 'M', 'LOW': 'LOW', 'L': 'R', 'R': 'L'}[b['framing']]
    stamps = []
    for st in BD.STAMPS:
        i = WI[st['seq']]
        stamps.append(dict(st, f0=word_on(i) + st.get('off', 0), f1=word_on(i) + st.get('off', 0) + int(st.get('hold', 1.6) * FPS)))
    overlays = []
    for o in BD.OVERLAYS:
        i = WI[o['seq']]
        o2 = resolve_all(dict(o), i)
        o2['f0'] = word_on(i)
        o2['f1'] = o2['until'] if isinstance(o2.get('until'), int) else cut_frame(find(o['until'], i))
        overlays.append(o2)
    OVERLAYS[:] = overlays
    return tl, calls, stamps, issues


OVERLAYS = []


# ---------------- compose ----------------
def compose(c, f, shot_, calls_on, stamps_on, qa=None, overlays_on=()):
    c.clear(skia.ColorBLACK)
    ctx = dict(occ=[], tags=[], photo=False, avoid=[O.callout_layout(cl['text'])[2] for cl in calls_on])
    cam = shot_.get('cam', [])
    dx = dy = 0.0
    sc = 1.0
    for ev in cam:
        kind, at = ev[0], ev[1]
        if kind == 'shake':
            ddx, ddy = M.shake(f - at, amp=ev[2] if len(ev) > 2 else 12, frames=10)
            dx, dy = dx + ddx, dy + ddy
        elif kind == 'punch':
            sc *= M.punch(f - at, ev[2] if len(ev) > 2 else 0.04)
    c.save()
    if dx or dy or sc != 1.0:
        c.translate(W / 2 + dx, H / 2 + dy)
        c.scale(sc, sc)
        c.translate(-W / 2, -H / 2)
    S.SHOTS[shot_['kind']](c, shot_, f, ctx)
    c.restore()
    for cl in calls_on:
        lines, cap, box = O.callout_layout(cl['text'])
        if ctx['photo']:
            c.drawImage(L.top_scrim(min(0.48, (box.bottom() + 0.1 * H) / H)), 0, 0)
        O.callout(c, cl['text'], f - cl['f0'], style=cl.get('style', 'red'))
        if qa is not None and f - cl['f0'] in (5, 30):
            for kind, r in ctx['occ']:
                if kind == 'face' and skia.Rect.Intersects(r, box):
                    qa.append(dict(f=f, tc=TL.tc(f), kind='callout_over_face', text=cl['text'], shot=shot_.get('trigger')))
    for o in overlays_on:
        if o['kind'] == 'timer':
            S.draw_timer(c, o, f)
    for st in stamps_on:
        O.stamp(c, st['text'], st.get('x', W / 2), st.get('y', 0.5 * H), f - st['f0'], sub=st.get('sub'),
                cap=st.get('cap', 74))
    return ctx


def find_shot(tl, f, si=[0]):
    i = si[0] if si[0] < len(tl) and tl[si[0]]['f0'] <= f else 0
    while i + 1 < len(tl) and tl[i + 1]['f0'] <= f:
        i += 1
    si[0] = i
    return tl[i]


def render(f_start, f_end, out, crf=18, preset='medium'):
    tl, calls, stamps, _ = compile_all()
    qa = []
    ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', preset, '-crf', str(crf),
                           '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                           out], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    t0 = time.time()
    for f in range(f_start, f_end):
        sh = find_shot(tl, f)
        con = [cl for cl in calls if cl['f0'] <= f < cl['f1']]
        son = [st for st in stamps if st['f0'] <= f < st['f1']]
        compose(surf.getCanvas(), f, sh, con, son, qa, [o for o in OVERLAYS if o['f0'] <= f < o['f1']])
        ff.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
        if (f - f_start) % 600 == 0:
            el = time.time() - t0
            print(f'frame {f} ({f - f_start}/{f_end - f_start})  {el / 60:.1f} min  {(f - f_start + 1) / max(el, 1e-3):.1f} fps',
                  flush=True)
    ff.stdin.close()
    ff.wait()
    json.dump(qa, open(out + '.qa.json', 'w'), indent=0)
    return out


def stills(frames, outdir=None):
    import cv2
    tl, calls, stamps, _ = compile_all()
    outdir = outdir or os.path.join(HERE, 'stills')
    os.makedirs(outdir, exist_ok=True)
    surf = skia.Surface(W, H)
    paths = []
    for f in frames:
        sh = find_shot(tl, f)
        compose(surf.getCanvas(), f, sh, [cl for cl in calls if cl['f0'] <= f < cl['f1']],
                [st for st in stamps if st['f0'] <= f < st['f1']], None, [o for o in OVERLAYS if o['f0'] <= f < o['f1']])
        p = os.path.join(outdir, f'f{f:05d}.jpg')
        cv2.imwrite(p, surf.makeImageSnapshot().toarray()[:, :, :3], [cv2.IMWRITE_JPEG_QUALITY, 88])
        paths.append(p)
    return paths


def sheet(frames, out, cols=4, tile_w=480):
    import cv2
    import numpy as np
    ps = stills(frames)
    tiles = []
    for f, p in zip(frames, ps):
        im = cv2.imread(p)
        im = cv2.resize(im, (tile_w, int(tile_w * 9 / 16)), interpolation=cv2.INTER_AREA)
        cv2.putText(im, TL.tc(f), (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
        tiles.append(im)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
    return out


def prender(n=4, crf=16, preset='slow'):
    edges = [round(TOTAL_F * k / n) for k in range(n + 1)]
    tmp = os.path.join(HERE, 'chunks')
    os.makedirs(tmp, exist_ok=True)
    t = time.time()
    procs = []
    for k in range(n):
        out = os.path.join(tmp, f'c{k}.mp4')
        procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), 'chunk', str(edges[k]), str(edges[k + 1]), out,
                                       str(crf), preset], stdout=open(os.path.join(tmp, f'c{k}.log'), 'w'), stderr=subprocess.STDOUT))
    for p in procs:
        p.wait()
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file 'c{k}.mp4'\n" for k in range(n)))
    out = os.path.join(HERE, 'video_noaudio.mp4')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out],
                   check=True)
    qa = []
    for k in range(n):
        qp = os.path.join(tmp, f'c{k}.mp4.qa.json')
        if os.path.exists(qp):
            qa += json.load(open(qp))
    json.dump(qa, open(os.path.join(HERE, 'render_qa.json'), 'w'), indent=0)
    print(f'rendered {TOTAL_F} frames in {(time.time() - t) / 60:.1f} min -> {out}; layout QA issues: {len(qa)}')
    return out


def plan():
    tl, calls, stamps, issues = compile_all()
    import numpy as np
    kinds = {}
    for s in tl:
        kinds.setdefault(s['kind'], [0, 0])
        kinds[s['kind']][0] += 1
        kinds[s['kind']][1] += (s['f1'] - s['f0']) / FPS
    tot = sum(v[1] for v in kinds.values())
    for k, (n, d) in sorted(kinds.items(), key=lambda x: -x[1][1]):
        print(f'{k:8s} {n:4d} shots {d:7.1f}s {100 * d / tot:5.1f}%')
    durs = np.array([(s['f1'] - s['f0']) / FPS for s in tl])
    print(f'shots {len(tl)}  median {np.median(durs):.2f}s  mean {durs.mean():.2f}s  max {durs.max():.2f}s  total {tot / 60:.2f} min  '
          f'callouts {len(calls)}  stamps {len(stamps)}')
    longest = sorted(tl, key=lambda s: s['f0'] - s['f1'])[:8]
    for s in longest:
        print(f"   long: {TL.tc(s['f0'])} {s['kind']:7s} {(s['f1'] - s['f0']) / FPS:5.2f}s  {s.get('trigger')}")
    for i in issues:
        print('  ISSUE', i)
    if MISSING:
        print('  MISSING IMAGES:', sorted(MISSING))
    return tl, calls


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    if cmd == 'plan':
        plan()
    elif cmd == 'stills':
        print(stills([int(x) for x in sys.argv[2].split(',')]))
    elif cmd == 'sheet':
        print(sheet([int(x) for x in sys.argv[2].split(',')], sys.argv[3]))
    elif cmd == 'range':
        print(render(fr(float(sys.argv[2])), fr(float(sys.argv[3])), sys.argv[4], crf=20, preset='veryfast'))
    elif cmd == 'chunk':
        print(render(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], crf=int(sys.argv[5]), preset=sys.argv[6]))
    elif cmd == 'prender':
        prender(int(sys.argv[2]) if len(sys.argv) > 2 else 4)


def beatsheet(t0, t1, out, per_beat=1, include_hosts=False, cols=5):
    tl, calls, stamps, _ = compile_all()
    frames = []
    for b in tl:
        if not (fr(t0) <= b['f0'] < fr(t1)):
            continue
        if b['kind'] == 'host' and not include_hosts:
            continue
        d = b['f1'] - b['f0']
        for k in range(per_beat):
            frames.append(b['f0'] + int(d * (0.75 if per_beat == 1 else (k + 1) / (per_beat + 1))))
    return sheet(frames, out, cols=cols, tile_w=384)


if __name__ == '__main__' and sys.argv[1] == 'beatsheet':
    print(beatsheet(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 1))
