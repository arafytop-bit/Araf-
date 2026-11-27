"""QA for the v3 render: automated checks on the actual video file + the render's layout log.

  python3 audit_v3.py VIDEO MEASURE_DIR RENDER_QA_JSON OUT_MD

Checks (all on the rendered file unless noted):
  frozen       no pixel change for >= 2.0 s (ffmpeg freezedetect, n=0.001)
  black        black frames >= 0.1 s (ffmpeg blackdetect)
  pop          one-frame change inside a shot with no animation before/after (diff > 2.5, neighbours < 0.05)
  flash        2-frame jump in and out (not a cut)
  dead_window  5 s windows with no visual change event
  layout       callout over a face, text under 4.5 % of frame height (from the render log)
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

FPS = 30.0


def tc(t):
    return f'{int(t // 60)}:{t % 60:05.2f}'


def ff_detect(path, filt):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-vf', filt, '-an', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return r


def main(video, mdir, qa_json, out_md):
    issues = []
    d, hd = np.load(os.path.join(mdir, 'diffs.npy'))
    cuts = set(json.load(open(os.path.join(mdir, 'cuts.json')))['cuts'])
    near_cut = set()
    for c in cuts:
        near_cut.update((c - 1, c, c + 1))
    # frozen (ffmpeg)
    fr = ff_detect(video, 'freezedetect=n=0.001:d=2')
    for m in re.finditer(r'freeze_start: ([\d.]+)', fr):
        issues.append(dict(t=float(m.group(1)), kind='frozen', detail='no visible motion for >= 2 s'))
    # black frames
    bl = ff_detect(video, 'blackdetect=d=0.1:pix_th=0.06')
    for m in re.finditer(r'black_start:([\d.]+) black_end:([\d.]+)', bl):
        issues.append(dict(t=float(m.group(1)), kind='black', detail=f'black for {float(m.group(2)) - float(m.group(1)):.2f}s'))
    # one-frame pops without easing
    for i in range(2, len(d) - 2):
        if i in near_cut:
            continue
        if d[i] > 2.5 and d[i + 1] < 0.05 and d[i - 1] < 0.05:
            issues.append(dict(t=i / FPS, kind='pop', detail=f'one-frame change (diff {d[i]:.1f}) with no ease in/out'))
    # flash frames
    for i in range(1, len(d) - 3):
        if i in near_cut or (i + 2) in near_cut:
            continue
        if d[i] > 12 and d[i + 2] > 8:
            issues.append(dict(t=i / FPS, kind='flash', detail='2-frame jump in and out'))
    # dead 5 s windows (no change event at all)
    ch = json.load(open(os.path.join(mdir, 'changes.json')))
    per5 = ch['per5']
    for k, v in enumerate(per5):
        if v == 0:
            issues.append(dict(t=k * 5.0, kind='dead_window', detail='5 s window without a visual change'))
    # layout log from the renderer
    if qa_json and os.path.exists(qa_json):
        for q in json.load(open(qa_json)):
            if q['kind'] == 'callout_over_face':
                issues.append(dict(t=q['f'] / FPS, kind='text_over_face', detail=f"callout '{q['text']}' touches a face"))
            elif q['kind'] == 'small_text':
                issues.append(dict(t=q['f'] / FPS, kind='small_text', detail=f"'{q['text']}' cap {q['cap_px']}px (< 49 px = 4.5 % H)"))
    issues.sort(key=lambda e: e['t'])
    from collections import Counter
    cnt = Counter(e['kind'] for e in issues)
    lines = [f'# Automated QA of {os.path.basename(video)}', '', '| Check | Count |', '|---|---|']
    for k in ('frozen', 'black', 'pop', 'flash', 'dead_window', 'text_over_face', 'small_text'):
        lines.append(f'| {k} | {cnt.get(k, 0)} |')
    lines += ['', '| Time | Check | Detail |', '|---|---|---|']
    for e in issues:
        lines.append(f"| {tc(e['t'])} | {e['kind']} | {e['detail']} |")
    open(out_md, 'w').write('\n'.join(lines) + '\n')
    print(dict(cnt))
    return issues


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4] if len(sys.argv) > 4 else 'qa.md')
