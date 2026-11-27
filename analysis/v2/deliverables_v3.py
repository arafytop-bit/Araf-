"""Deliverables for the v3 rebuild: side-by-side contact sheet (reference vs v3, matched by shot type) and the
second-by-second retention map.

  python3 deliverables_v3.py sheet  REF_VIDEO OUR_VIDEO OUT_JPG
  python3 deliverables_v3.py retention OUR_VIDEO MEASURE_DIR OUT_MD
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.abspath(os.path.join(HERE, '..', '..', 'projects', 'epic_deaths', 'v3'))
sys.path.insert(0, V3)


def grab(path, t, h=360):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                       capture_output=True)
    im = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)
    return cv2.resize(im, (int(h * 16 / 9), h), interpolation=cv2.INTER_AREA)


def label(im, text, sub=None):
    out = im.copy()
    cv2.rectangle(out, (0, 0), (out.shape[1], 34), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 1, cv2.LINE_AA)
    if sub:
        cv2.putText(out, sub, (out.shape[1] - 150, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 1, cv2.LINE_AA)
    return out


def our_moments():
    import build3 as B3
    import timeline as TL
    tl, calls, stamps, _ = B3.compile_all()
    fps = TL.FPS

    def first(pred, frac=0.6):
        for b in tl:
            if pred(b):
                return (b['f0'] + (b['f1'] - b['f0']) * frac) / fps
        return None
    callout_low = None
    for cl in calls:
        for b in tl:
            if b['kind'] == 'host' and b.get('framing') == 'LOW' and b['f0'] <= cl['f0'] + 6 < b['f1']:
                callout_low = (cl['f0'] + 12) / fps
                break
        if callout_low:
            break
    return {
        'hook': 1.95,
        'kinetic': first(lambda b: b['kind'] == 'kinetic', 0.95),
        'host_m': first(lambda b: b['kind'] == 'host' and b.get('framing') == 'M' and not b.get('over')),
        'host_cu': first(lambda b: b['kind'] == 'host' and b.get('framing') in ('CU', 'ECU')),
        'framed_photo': first(lambda b: b['kind'] == 'photo' and b.get('mode', 'frame') == 'frame'),
        'scene_photo': first(lambda b: b['kind'] == 'scene' and b.get('bg') == 'hagia_sophia'),
        'callout_low': callout_low,
        'title': first(lambda b: b['kind'] == 'title', 0.8),
        'band': first(lambda b: b['kind'] == 'band', 0.8),
        'map': first(lambda b: b['kind'] == 'map', 0.85),
        'bigtext': first(lambda b: b['kind'] == 'text' and b.get('anim') == 'slam', 0.7),
        'end': TL.TOTAL_S - 2.0,
    }


REF = {  # measured reference moments (style bible + 4 fps sheets)
    'hook': 2.5, 'kinetic': 3.25, 'host_m': 4.0, 'host_cu': 9.25, 'framed_photo': 145.0, 'scene_photo': 366.0,
    'callout_low': 487.0, 'title': 70.0, 'band': 362.5, 'map': 369.75, 'bigtext': 21.5, 'end': 900.0,
}
NAMES = {'hook': 'Hook (first 2 s)', 'kinetic': 'Kinetic title', 'host_m': 'Host, normal framing', 'host_cu': 'Host, punch-in',
         'framed_photo': 'Framed photo on blur-fill', 'scene_photo': 'Characters on a real photo', 'callout_low': 'Callout, host lowered',
         'title': 'Entry title card', 'band': 'Meme band', 'map': 'Map', 'bigtext': 'Big statement text', 'end': 'End screen'}


def sheet(ref, ours, out):
    om = our_moments()
    rows = []
    for k in NAMES:
        if om.get(k) is None:
            continue
        a = label(grab(ref, REF[k]), f'REFERENCE  {NAMES[k]}', f'{int(REF[k] // 60)}:{REF[k] % 60:05.2f}')
        b = label(grab(ours, om[k]), f'V3  {NAMES[k]}', f'{int(om[k] // 60)}:{om[k] % 60:05.2f}')
        gap = np.full((a.shape[0], 12, 3), 40, np.uint8)
        rows.append(np.hstack([a, gap, b]))
        rows.append(np.full((10, rows[-1].shape[1], 3), 40, np.uint8))
    img = np.vstack(rows[:-1])
    cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return out


def retention(ours, mdir, out):
    import build3 as B3
    import timeline as TL
    import sound3 as S3
    tl, calls, stamps, _ = B3.compile_all()
    fps = TL.FPS
    ch = json.load(open(os.path.join(mdir, 'changes.json')))['changes']
    changes_per_s = np.bincount((np.array(ch) / fps).astype(int), minlength=int(TL.TOTAL_S) + 1)
    events = S3.collect(tl, calls, stamps, B3.OVERLAYS)
    sfx_per_s = np.bincount([int(e[0]) for e in events if e[1] != 'war_drum'], minlength=int(TL.TOTAL_S) + 1)
    W = TL.WORDS

    def at(phrase):
        return W[TL.find(phrase)]['s']
    loops = [
        ('Open loop 1: "wins a fight after he\'s already dead"', 'One of these guys', 'They crowned the corpse'),
        ('Open loop 2: "another wins a battle the same way"', 'Another wins a battle', 'Then his nephew picked up the war drum'),
        ('Escalation promise: "every entry tops the last"', 'And every entry tops', 'Think about that'),
        ('Speedrun timer (visual loop)', 'let me speedrun his', "And that's just the warm-up"),
        ('"Here\'s the problem with this story"', "here's the problem with this story", 'So, grain of salt'),
        ('"Here\'s the craziest part"', "But here's the craziest part", 'he dies at the Battle of Hastings'),
        ('"Why is a nosebleed on this list?"', 'So why is a list of epic deaths', 'The funeral is why'),
        ('"That\'s not even the wild part"', "And that's not even the wild part", 'uses it as the prop'),
        ('"Our last guy pulled it off with an entire fleet"', 'But our last guy', 'The fleet fought on and won'),
        ('"The most epic death in recorded history"', 'the most epic death in recorded', 'Do not announce my death'),
        ('"Here\'s the part that gets me"', "And here's the part that gets me", 'pretty much alone'),
        ('Part two (mid-roll)', 'And the five that got cut', 'part two is mapped out'),
    ]
    lines = ['# Retention map (v3)', '',
             'Second-by-second plan of what holds attention, measured on the rendered file (visual change events from '
             '`measure.py`) and from the compiled timeline (shot, sound events).', '',
             '## Hook (0:00-0:06)', '',
             '- 0:00.0 frame 1 is mid-action: the crowned corpse on a real Olympia photo; the loser is already hopping, the olive wreath is falling.',
             '- 0:00.9-0:02.0 the on-screen hook lights up word by word as it is spoken: WON A FIGHT / AFTER / DYING (red).',
             '- 0:02.5 hard cut to a night battle on a real turtle ship: the drummer, fire, embers; WON A BATTLE / THE SAME WAY.',
             '- 0:04.3 kinetic title (the reference\'s opening move): THE MOST EPIC DEATHS IN HUMAN HISTORY while the five victims run in.', '',
             '## Open loops and payoffs', '', '| Opens | Loop | Pays off |', '|---|---|---|']
    for name, a, b in loops:
        try:
            ta, tb = at(a), at(b)
            lines.append(f'| {TL.tc(TL.fr(ta))} | {name} | {TL.tc(TL.fr(tb))} |')
        except KeyError:
            pass
    lines += ['', '## Escalation', '', '1. Harald: dies to an arrow on the one day he skipped armor.',
              '2. Attila: least epic death, most epic funeral.', '3. Crassus: his head becomes a stage prop.',
              '4. Arrichion: wins an Olympic final after dying.', '5. Yi Sun-sin: wins a whole war after dying.', '',
              '## Second by second', '', '| Second | On screen | Visual changes | SFX hits | Retention device |', '|---|---|---|---|---|']
    titles = {b['f0'] // int(fps): b for b in tl if b['kind'] == 'title'}
    stamp_s = {st['f0'] // int(fps) for st in stamps}
    call_s = {cl['f0'] // int(fps): cl['text'] for cl in calls}
    j = 0
    for sec in range(int(TL.TOTAL_S)):
        f = int(sec * fps + fps / 2)
        while j + 1 < len(tl) and tl[j + 1]['f0'] <= f:
            j += 1
        b = tl[j]
        what = b['kind'] if b['kind'] != 'host' else f"host ({b.get('framing')})"
        if b['kind'] not in ('host',):
            what += f": {str(b.get('trigger'))[:38]}"
        dev = []
        if sec < 4:
            dev.append('HOOK')
        if sec in titles:
            dev.append('title hit (new entry)')
        if sec in stamp_s:
            dev.append('death stamp (payoff)')
        if sec in call_s:
            dev.append(f'callout: {call_s[sec]}')
        if changes_per_s[sec] == 0 and sfx_per_s[sec] == 0:
            dev.append('-')
        lines.append(f'| {TL.tc(sec * int(fps))[:-3]} | {what} | {int(changes_per_s[sec])} | {int(sfx_per_s[sec])} | {"; ".join(dev)} |')
    open(out, 'w').write('\n'.join(lines) + '\n')
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        print(sheet(sys.argv[2], sys.argv[3], sys.argv[4]))
    elif sys.argv[1] == 'retention':
        print(retention(sys.argv[2], sys.argv[3], sys.argv[4]))
