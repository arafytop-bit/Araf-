"""Build "Most Epic Deaths" (1920x1080 @30): resolve word triggers, compile shots, auto-fill host
shots, render with frame caching, mix audio.

  python3 build.py plan                 # compile + print shot stats
  python3 build.py stills 10,200,900    # render selected frames to stills/
  python3 build.py render [t0 t1]       # render (optionally a time range in seconds) -> out.mp4
"""
import json
import math
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))

import numpy as np  # noqa: E402
import skia  # noqa: E402
from engine.core import W, H, FPS, new_surface, draw_background  # noqa: E402
from engine import shots  # noqa: E402
from engine.shots import RENDERERS  # noqa: E402
from engine.roundhead import draw_character, R_NORMAL, R_ZOOM, NORMAL_CENTER, ZOOM_CENTER  # noqa: E402
from engine.text import draw_callout, text_width, size_for_cap, draw_text  # noqa: E402
from engine.cards import KineticTitle  # noqa: E402
import storyboard as SB  # noqa: E402
from cast import HOST  # noqa: E402
import retention as RT  # noqa: E402

VOICE_OFFSET = 0.10
shots.IMG_DIR = os.path.join(HERE, 'assets', 'picked')
shots.HOST_PAL = HOST
RT.install_background_hook(shots, draw_background)

# ---------------- words & triggers ----------------
WORDS = json.load(open(os.path.join(HERE, 'words.json')))
SENTS = json.load(open(os.path.join(HERE, 'sentences.json')))
for w in WORDS:
    w['s'] += VOICE_OFFSET
    w['e'] += VOICE_OFFSET
for s in SENTS:
    s['start'] += VOICE_OFFSET
    s['end'] += VOICE_OFFSET


def norm(t):
    t = t.lower().replace('’', "'").replace('‘', "'")
    return re.sub(r"[^a-z0-9']", '', t).strip("'")


NW = [norm(w['w']) for w in WORDS]
LAST_WORD_END = SENTS[-1]['end']
TOTAL_S = LAST_WORD_END + 7.2          # outro sting: enters 0.2 s after the last word, 6.5 s + 0.5 s fade


def find(phrase, start=0):
    toks = [norm(x) for x in phrase.split() if norm(x)]
    n = len(toks)
    for i in range(start, len(NW) - n + 1):
        if NW[i:i + n] == toks:
            return i
    raise KeyError(f'trigger not found after word {start}: {phrase!r}')


def fr(t):
    return int(round(t * FPS))


def cut_frame(i):            # one frame before the word onset (measured on the source)
    return max(0, fr(WORDS[i]['s']) - 1)


def sent_end_frame(i):
    return fr(SENTS[WORDS[i]['sid']]['end']) + 4


# ---------------- compile ----------------
def compile_beats():
    beats = []
    cursor = 0
    for b in SB.BEATS:
        b = dict(b)
        i = find(b['trigger'], cursor)
        cursor = i
        b['wi'] = i
        b['f0'] = cut_frame(i)
        evs = {}

        def sub(phrase, key, from_i=i):
            j = find(phrase, from_i)
            evs[key] = cut_frame(j)
            return j
        if b['kind'] == 'kinetic':
            lines = []
            for base, words, width in b['lines']:
                lines.append((base, [(wd, cap, st, cut_frame(find(tr, i))) for wd, cap, st, tr in words], W * width))
            b['kin'] = KineticTitle(lines)
        for k, it in enumerate(b.get('items', [])):
            if isinstance(it, dict) and it.get('at'):
                sub(it['at'], f'item{k}')
            if isinstance(it, dict) and it.get('strike_at'):
                sub(it['strike_at'], f'strike{k}')
        for k, ln in enumerate(b.get('lines_', [])):
            pass
        if b['kind'] == 'card' and b.get('type') == 'bio':
            for k, ln in enumerate(b.get('lines', [])):
                if isinstance(ln, dict) and ln.get('at'):
                    sub(ln['at'], f'item{k}')
        if b.get('strike_at'):
            sub(b['strike_at'], 'strike')
        if b.get('overlay_at'):
            sub(b['overlay_at'], 'overlay')
        if b.get('circle_at'):
            sub(b['circle_at'], 'circle')
        for k, ch in enumerate(b.get('chars', [])):
            if ch.get('at'):
                sub(ch['at'], f'c{k}')
            if ch.get('exit_at'):
                sub(ch['exit_at'], f'c{k}_exit')
            if ch.get('say_at'):
                sub(ch['say_at'], f'say{k}')
            ex = ch.get('expr')
            if isinstance(ex, list):
                for trig, _ in ex:
                    if trig:
                        sub(trig, 'x:' + trig)
        for k, p in enumerate(b.get('props', [])):
            if p.get('at'):
                sub(p['at'], f'p{k}')
            if p.get('exit_at'):
                sub(p['exit_at'], f'p{k}_exit')
        for k, lab in enumerate(b.get('labels', [])):
            sub(lab[3], f'label{k}')
        for k, st in enumerate(b.get('stops', [])):
            if st[2]:
                sub(st[2], f'stop{k}')
        for n, label, trig in b.get('pins', []):
            if trig:
                sub(trig, 'pin_' + n)
        for k, im in enumerate(b.get('img_at', [])):
            sub(im, f'img{k}')
        if b.get('change_at'):
            sub(b['change_at'], 'change')
        if b.get('quote_at'):
            j = find(b['quote_at'], i)
            wf = []
            for qw in b['text'].split():
                if not norm(qw):
                    continue
                try:
                    j = find(qw, j)
                    wf.append(cut_frame(j) + 1)
                    j += 1
                except KeyError:
                    wf.append(wf[-1] if wf else b['f0'])
            b['word_frames'] = wf
        b['ev'] = evs
        # end frame
        if b.get('until'):
            b['f1'] = cut_frame(find(b['until'], i + 1))
        elif b.get('hold'):
            b['f1'] = b['f0'] + int(b['hold'] * FPS)
        else:
            b['f1'] = min(max(sent_end_frame(i), b['f0'] + 36), b['f0'] + 150)
        if b['kind'] == 'end':
            b['f1'] = fr(TOTAL_S)
            evs['logo'] = fr(LAST_WORD_END + 0.2)
        if b['kind'] == 'photo' and not os.path.exists(os.path.join(shots.IMG_DIR, b['img'] + '.jpg')):
            continue          # image not available: the host fills this moment
        beats.append(b)
    beats.sort(key=lambda b: b['f0'])
    for a, nb in zip(beats, beats[1:]):
        if a['f1'] > nb['f0']:
            a['f1'] = nb['f0']
        elif nb['f0'] - a['f1'] < 15:
            a['f1'] = nb['f0']
    beats = [b for b in beats if b['f1'] - b['f0'] >= 6]
    return beats


SENTI = [
    (r"\b(dies|died|dead|death|killed|murder|blood|crucified|strangled|bullet|choked|executed|tortured|grave|corpse)\b", ['shock', 'sad', 'grimace']),
    (r"\b(insane|crazy|craziest|wild|ridiculous|legendary|epic)\b", ['shock', 'grin', 'talk']),
    (r"\b(respectfully|translation|please leave|anyway|apparently|roughly|basically|literally)\b", ['smug', 'skeptic', 'deadpan']),
    (r"\?", ['skeptic', 'talk2']),
    (r"\b(rich|gold|fortune|money)\b", ['smug', 'grin']),
]
DEFAULT_EXPR = ['talk', 'talk2', 'smile', 'talk', 'neutral', 'talk2']
POSES = ['idle', 'hips', 'wave', 'point', 'idle', 'hips', 'shrug', 'chin']


def host_shots(beats):
    rng = random.Random(7)
    total_f = fr(TOTAL_S)
    gaps = []
    t = 0
    prev = None
    for b in beats:
        if b['f0'] > t:
            gaps.append((t, b['f0'], prev))
        if b['f1'] >= t:
            prev = b
        t = max(t, b['f1'])
    if t < total_f:
        gaps.append((t, total_f, prev))
    rng_over = random.Random(11)
    forced = []
    cur = 0
    for h in SB.HOSTS:
        i = find(h['trigger'], 0)
        forced.append((cut_frame(i), h))
    hs = []
    for g0, g1, pb in gaps:
        # HOST_OVER (BLUEPRINT 5.4): sometimes the host stays over a blurred copy of the photo that was just on screen
        over = pb['img'] if (pb is not None and pb['kind'] == 'photo' and pb['f1'] == g0 and rng_over.random() < 0.4) else None
        # split points: sentence starts inside the gap (keep shots >= 1.6 s), plus forced host settings
        cuts = [g0]
        for s in SENTS:
            f = fr(s['start']) - 1
            if g0 + 48 <= f <= g1 - 40 and f - cuts[-1] >= 75:
                cuts.append(f)
        for f, h in forced:
            if g0 + 12 <= f <= g1 - 12 and all(abs(f - c) > 12 for c in cuts):
                cuts.append(f)
        cuts = sorted(set(cuts)) + [g1]
        for a, z in zip(cuts, cuts[1:]):
            if z - a < 3:
                continue
            fh = None
            for f, h in forced:
                if a - 6 <= f <= z - 6:
                    fh = h
                    break
            ws = [k for k, w in enumerate(WORDS) if a <= fr(w['s']) < z]
            text = ' '.join(WORDS[k]['w'] for k in ws).lower()
            pool = DEFAULT_EXPR
            for pat, pl in SENTI:
                if re.search(pat, text):
                    pool = pl + DEFAULT_EXPR[:2]
                    break
            zoom = (fh or {}).get('zoom', rng.random() < 0.28 and (z - a) < 110)
            pose = (fh or {}).get('pose', rng.choice(POSES))
            first = (fh or {}).get('expr', rng.choice(pool))
            exprs = [(a, first)]
            last = a
            for k in ws:
                f = fr(WORDS[k]['s']) - 1
                if f - last >= rng.randint(28, 42) and z - f > 12:
                    nxt = rng.choice([e for e in pool if e != exprs[-1][1]] or pool)
                    exprs.append((f, nxt))
                    last = f
            hs.append(dict(kind='host', f0=a, f1=z, zoom=zoom, pose=pose, exprs=exprs, over=over if a == g0 else None,
                           look=(fh or {}).get('look', (0.0, 0.0)), bob=(rng.uniform(-0.03, 0.03), rng.uniform(-0.02, 0.02))))
    return hs


def compile_all():
    beats = compile_beats()
    hosts = host_shots(beats)
    timeline = sorted(beats + hosts, key=lambda b: b['f0'])
    calls = []
    cur = 0
    for c in SB.CALLS:
        i = find(c['trigger'], 0)
        f0 = cut_frame(i)
        calls.append(dict(f0=f0, f1=f0 + int(c['hold'] * FPS), text=c['text']))
    calls.sort(key=lambda c: c['f0'])
    for a, b in zip(calls, calls[1:]):
        a['f1'] = min(a['f1'], b['f0'])
    for t in [b for b in timeline if b['kind'] in ('title', 'kinetic', 'end')]:   # title cards stay clean
        for c in calls:
            if c['f0'] < t['f0'] < c['f1']:
                c['f1'] = t['f0']
    calls = [c for c in calls if c['f1'] - c['f0'] >= 8]
    overlays = []
    for o in SB.OVERLAYS:
        i = find(o['trigger'], 0)
        overlays.append(dict(o, f0=cut_frame(i), f1=cut_frame(find(o['until'], i))))
    return timeline, calls, overlays


# ---------------- render ----------------
def render_host(c, h, f):
    if h.get('over') and os.path.exists(os.path.join(shots.IMG_DIR, h['over'] + '.jpg')):
        c.drawImage(shots.blur_bg(h['over']), 0, 0)
    else:
        shots.draw_background(c)
    e = h['exprs'][0][1]
    for f0, ex in h['exprs']:
        if f >= f0:
            e = ex
    e = RT.host_expr(h, f, e)
    sy = RT.host_bounce(h, f)
    push = 1.0 if h['zoom'] else 1.0 + 0.005 * (f - h['f0']) / FPS
    (cx, cy), R = (ZOOM_CENTER, R_ZOOM) if h['zoom'] else (NORMAL_CENTER, R_NORMAL)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(push, push)
    c.translate(-W / 2, -H / 2)
    feet = cy + 3.05 * R
    c.translate(cx, feet)
    c.scale(1 / math.sqrt(sy), sy)
    c.translate(-cx, -feet)
    draw_character(c, cx, cy, R, h['pose'], e, HOST, bob=h['bob'], look=h['look'])
    c.restore()
    return e


def draw_timer(c, o, f):
    t = (f - o['f0']) / FPS
    s = f'{int(t // 60):02d}:{t % 60:06.3f}'
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(W - 640, 40, W - 60, 190), 16, 16), skia.Paint(Color=skia.Color(0, 0, 0, 190), AntiAlias=True))
    draw_text(c, s, W - 610, 112, size_for_cap(50), style='#7FFF6A', tracking=0.02, shadow=False, grunge=False)
    draw_text(c, 'HARALD% SPEEDRUN', W - 610, 168, size_for_cap(22), style='#FFFFFF', tracking=0.08, shadow=False, grunge=False)


def frame_key(shot, f, calls_on, ovs_on):
    if shot['kind'] == 'host':
        e = shot['exprs'][0][1]
        for f0, ex in shot['exprs']:
            if f >= f0:
                e = ex
        if ovs_on:
            return None
        ck = tuple((c['text'], min(5, f - c['f0'])) for c in calls_on)
        return ('host', shot['f0'], e, ck)
    return None


def compose(c, surf, f, shot, calls_on, ovs_on, rt):
    RT.CUR_F[0] = f
    c.clear(skia.ColorBLACK)
    if shot is None:
        shots.draw_background(c)
    elif shot['kind'] == 'host':
        render_host(c, shot, f)
    else:
        try:
            RENDERERS[shot['kind']](c, shot, f)
        except Exception as ex:
            print('render error', shot['kind'], shot.get('trigger'), ex, flush=True)
            shots.draw_background(c)
    if shot is not None and shot.get('teaser'):
        rt.teaser(c, surf, shot, f)
    for o in ovs_on:
        draw_timer(c, o, f)
    for cl in calls_on:
        draw_callout(c, cl['text'], progress=(f - cl['f0'] + 1) / 5.0)
    rt.apply_camera(c, surf, f)
    rt.death_overlay(c, surf, f)
    if shot is None or shot['kind'] not in ('title', 'end', 'kinetic'):
        rt.hud(c, f)


def render(t0=0.0, t1=None, out=None, frames=None):
    timeline, calls, overlays = compile_all()
    rt = RT.Retention(timeline, calls, overlays, sys.modules[__name__])
    total_f = fr(TOTAL_S)
    f_start, f_end = frames if frames else (fr(t0), fr(t1) if t1 else total_f)
    out = out or os.path.join(HERE, 'video_noaudio.mp4')
    ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                           '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out],
                          stdin=subprocess.PIPE)
    surf = new_surface()
    si = 0
    import time
    t_start = time.time()
    for f in range(f_start, f_end):
        while si + 1 < len(timeline) and timeline[si + 1]['f0'] <= f:
            si += 1
        shot = timeline[si] if timeline[si]['f0'] <= f else None
        calls_on = [c for c in calls if c['f0'] <= f < c['f1']]
        ovs_on = [o for o in overlays if o['f0'] <= f < o['f1']]
        c = surf.getCanvas()
        compose(c, surf, f, shot, calls_on, ovs_on, rt)
        ff.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
        if f % 900 == 0:
            el = time.time() - t_start
            print(f'frame {f}/{f_end}  {el / 60:.1f} min elapsed', flush=True)
    ff.stdin.close()
    ff.wait()
    return out


# ---------------- audio ----------------
MOODS = {'intro': dict(bpm=108, key=0, seed=11), 'Harald Hardrada': dict(bpm=112, key=-2, seed=12),
         'Attila the Hun': dict(bpm=100, key=3, seed=13, under=-1), 'Marcus Licinius Crassus': dict(bpm=104, key=1, seed=14),
         'Arrichion of Phigalia': dict(bpm=116, key=-1, seed=15), 'midroll': dict(bpm=96, key=5, seed=16, under=2),
         'Yi Sun-sin': dict(bpm=110, key=2, seed=17, under=-2), 'outro': dict(bpm=108, key=0, seed=18)}


def audio_plan(timeline, overlays):
    titles = [b for b in timeline if b['kind'] == 'title']
    t_title = {b['trigger'].rstrip('.'): b['f0'] / FPS for b in titles}
    secs = []
    for snt in SENTS:
        if not secs or secs[-1][0] != snt['section']:
            secs.append([snt['section'], max(0.0, snt['start'] - 0.3)])
    bounds = []
    for k, (name, t0) in enumerate(secs):
        t0 = t_title.get(name, t0) if k else 0.0
        bounds.append([t0, name])
    sections = []
    for k, (t0, name) in enumerate(bounds):
        t1 = bounds[k + 1][0] if k + 1 < len(bounds) else LAST_WORD_END
        sections.append((t0, t1, MOODS.get(name, dict(bpm=108, key=0, seed=k + 1))))
    events = []
    for k, b in enumerate(titles):          # the same bright hit on every title card, exactly on the cut frame
        t = b['f0'] / FPS
        events.append(dict(t=t, kind='hit', gain=4))
        if k == len(titles) - 1:            # music drops out completely before the final entry
            events.append(dict(t=t - 0.5, kind='dropout', dur=0.5))
    for b in timeline:
        spec = SB.SFX.get(b.get('trigger'))
        if spec is None and b.get('sfx') and b['kind'] != 'title':
            spec = [(b['sfx'], None, 0, -6)]
        for kind, key, delay, gain in spec or []:
            f = b['f0'] if key is None else b.get('ev', {}).get(key, b['f0'])
            events.append(dict(t=(f + delay) / FPS, kind=kind, gain=gain))
        if b.get('drum'):
            for f in range(b['f0'], b['f1'], 12):
                events.append(dict(t=f / FPS, kind='drum', gain=-12))
    for o in overlays:
        events.append(dict(t=o['f0'] / FPS, kind='pop', gain=-8))
    events.append(dict(t=LAST_WORD_END + 0.2, kind='sting', gain=8, bpm=108))
    return sections, events


def mix():
    from engine import audio
    timeline, calls, overlays = compile_all()
    sections, events = audio_plan(timeline, overlays)
    for t0, t1, cfg in sections:
        print(f'  bed {t0:8.2f}-{t1:8.2f}  {cfg}')
    print('  events:', len(events), {k: sum(1 for e in events if e['kind'] == k) for k in {e['kind'] for e in events}})
    raw = os.path.join(HERE, 'mix_raw.wav')
    vp = os.path.join(HERE, 'voice.wav')
    vp = vp if os.path.exists(vp) else os.path.join(HERE, 'voice.flac')
    audio.mix_long(vp, TOTAL_S, VOICE_OFFSET, sections, events, raw)
    m = audio.loudnorm(raw, os.path.join(HERE, 'mix.wav'))
    os.remove(raw)
    print('  loudness:', m)
    return os.path.join(HERE, 'mix.wav')


def mux(video=None, audio_path=None, out=None):
    video = video or os.path.join(HERE, 'video_noaudio.mp4')
    audio_path = audio_path or os.path.join(HERE, 'mix.wav')
    out = out or os.path.join(HERE, 'most_epic_deaths.mp4')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-i', audio_path, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', '-shortest', out], check=True)
    return out


def prender(n=4):
    """Render in n parallel chunks, then join them losslessly (stream copy)."""
    import time
    total_f = fr(TOTAL_S)
    edges = [round(total_f * k / n) for k in range(n + 1)]
    tmp = os.path.join(HERE, 'chunks')
    os.makedirs(tmp, exist_ok=True)
    t = time.time()
    procs = []
    for k in range(n):
        out = os.path.join(tmp, f'c{k}.mp4')
        procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), 'render_f', str(edges[k]), str(edges[k + 1]), out],
                                      stdout=open(os.path.join(tmp, f'c{k}.log'), 'w'), stderr=subprocess.STDOUT))
    for pr in procs:
        pr.wait()
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file 'c{k}.mp4'\n" for k in range(n)))
    out = os.path.join(HERE, 'video_noaudio.mp4')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True)
    print(f'rendered {total_f} frames in {(time.time() - t) / 60:.1f} min ->', out)
    return out


def describe():
    """YouTube description helper: chapters from the title cards + image credits."""
    timeline, _, _ = compile_all()
    def ts(t):
        return f'{int(t // 60)}:{int(t % 60):02d}'
    rows = [('0:00', 'Intro')]
    for b in timeline:
        if b['kind'] == 'title':
            rows.append((ts(b['f0'] / FPS), f"#{b['num']} " + b['trigger'].rstrip('.')))
    mid = [snt for snt in SENTS if snt['section'] == 'outro'][0]['start']
    rows.append((ts(mid), 'Recap'))
    out = ['CHAPTERS'] + [f'{a} {b}' for a, b in rows] + ['']
    used = []
    for b in timeline:
        ks = [b.get('img'), b.get('over')] + [it.get('img') for it in b.get('items', []) if isinstance(it, dict)]
        bg = str(b.get('bg', ''))
        if bg.startswith('img:'):
            ks.append(bg[4:].split('|')[0])
        for k in ks:
            if k and k not in used and os.path.exists(os.path.join(shots.IMG_DIR, k + '.jpg')):
                used.append(k)
    import importlib.util
    spec = importlib.util.spec_from_file_location('fetch2', os.path.join(HERE, 'assets', 'fetch2.py'))
    f2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f2)
    f2.write_credits(used)
    cp = os.path.join(HERE, 'CREDITS.md')
    if os.path.exists(cp):
        out += open(cp).read().splitlines()
    open(os.path.join(HERE, 'DESCRIPTION.md'), 'w').write('\n'.join(out) + '\n')
    return os.path.join(HERE, 'DESCRIPTION.md')


def plan():
    timeline, calls, overlays = compile_all()
    kinds = {}
    for s in timeline:
        kinds.setdefault(s['kind'], [0, 0])
        kinds[s['kind']][0] += 1
        kinds[s['kind']][1] += (s['f1'] - s['f0']) / FPS
    tot = sum(v[1] for v in kinds.values())
    for k, (n, d) in sorted(kinds.items(), key=lambda x: -x[1][1]):
        print(f'{k:8s} shots {n:4d}  {d:7.1f}s  {100 * d / tot:5.1f}%')
    durs = np.array([(s['f1'] - s['f0']) / FPS for s in timeline])
    print(f'shots {len(timeline)}, median {np.median(durs):.2f}s, mean {durs.mean():.2f}s, total {tot / 60:.2f} min; callouts {len(calls)}')
    missing = sorted({s['img'] for s in timeline if s.get('img') and not os.path.exists(os.path.join(shots.IMG_DIR, s['img'] + '.jpg'))})
    print('missing images:', missing)
    return timeline


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    if cmd == 'plan':
        plan()
    elif cmd == 'stills':
        import cv2
        timeline, calls, overlays = compile_all()
        rt = RT.Retention(timeline, calls, overlays, sys.modules[__name__])
        os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
        surf = new_surface()
        for f in [int(x) for x in sys.argv[2].split(',')]:
            shot = [s for s in timeline if s['f0'] <= f][-1]
            c = surf.getCanvas()
            compose(c, surf, f, shot, [c_ for c_ in calls if c_['f0'] <= f < c_['f1']], [o for o in overlays if o['f0'] <= f < o['f1']], rt)
            cv2.imwrite(os.path.join(HERE, 'stills', f'f{f:05d}.jpg'), surf.makeImageSnapshot().toarray()[:, :, :3], [cv2.IMWRITE_JPEG_QUALITY, 85])
        print('stills done')
    elif cmd == 'render_f':
        print('wrote', render(frames=(int(sys.argv[2]), int(sys.argv[3])), out=sys.argv[4]))
    elif cmd == 'prender':
        prender(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif cmd == 'final':
        prender(4)
        import sound_design
        sound_design.main()
        print('wrote', mux())
    elif cmd == 'describe':
        print(open(describe()).read())
    elif cmd == 'mix':
        print('wrote', mix())
    elif cmd == 'mux':
        print('wrote', mux())
    elif cmd == 'render':
        t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        t1 = float(sys.argv[3]) if len(sys.argv) > 3 else None
        print('wrote', render(t0, t1))
