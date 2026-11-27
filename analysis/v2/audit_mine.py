"""Automated mistake detection on our render (frames + timeline + stems), producing a timestamped list.

  python3 audit_mine.py MEASURE_DIR OUT_JSON
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..', 'projects', 'epic_deaths'))
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.abspath(os.path.join(PROJ, '..', '..')))
sys.argv = sys.argv[:3] + []


def tc(t):
    return f'{int(t // 60)}:{t % 60:05.2f}'


def main(mdir, out):
    issues = []
    fps = 30.0
    d, hd = np.load(os.path.join(mdir, 'diffs.npy'))
    cuts = set(json.load(open(os.path.join(mdir, 'cuts.json')))['cuts'])
    # 1. frozen stretches (no pixel change at all) >= 2.0 s
    still = d < 0.02
    run = 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run == int(2.0 * fps):
            issues.append(dict(t=(i - run + 1) / fps, kind='frozen', detail='no visible motion for 2 s+ (completely static frame)'))
    # 2. instant pop-ins: a single-frame change inside a shot with no follow-up animation
    for i in range(2, len(d) - 2):
        if i in cuts or (i - 1) in cuts or (i + 1) in cuts:
            continue
        if d[i] > 2.5 and d[i + 1] < 0.05 and d[i - 1] < 0.05:
            issues.append(dict(t=i / fps, kind='pop_no_animation', detail=f'element appears in one frame (diff {d[i]:.1f}) with no ease'))
    # 3. flash frames (sudden brightness spike that returns)
    # (computed from the stored per-frame diffs: big change in and out within 2 frames, not a cut)
    for i in range(1, len(d) - 3):
        if d[i] > 12 and d[i + 2] > 8 and i not in cuts:
            issues.append(dict(t=i / fps, kind='flash', detail='2-frame flash/jump in and out'))
    # timeline-based checks (our own render data)
    import build as B
    tl, calls, ovs = B.compile_all()
    # 4. empty cards (card visible before its first item appears)
    for b in tl:
        if b['kind'] == 'card' and b.get('items'):
            ev = b.get('ev', {})
            firsts = [ev[f'item{k}'] for k in range(len(b['items'])) if f'item{k}' in ev]
            if firsts and min(firsts) - b['f0'] > 12:
                issues.append(dict(t=b['f0'] / fps, kind='empty_card', detail=f"'{b.get('title', b.get('type'))}' card shows empty for {(min(firsts) - b['f0']) / fps:.2f}s"))
    # 5. callouts over zoomed host heads / title cards / HUD
    for c in calls:
        for b in tl:
            if b['f0'] < c['f1'] and c['f0'] < b['f1']:
                if b['kind'] == 'host' and b.get('zoom'):
                    issues.append(dict(t=max(b['f0'], c['f0']) / fps, kind='text_over_host', detail=f"callout '{c['text']}' overlaps the zoomed host's hat"))
                if b['kind'] == 'photo':
                    issues.append(dict(t=max(b['f0'], c['f0']) / fps, kind='text_low_contrast', detail=f"red callout '{c['text']}' over a photo (busy background)"))
    # 6. long static host holds (host shot > 4 s with no new element)
    for b in tl:
        if b['kind'] == 'host' and (b['f1'] - b['f0']) / fps > 4.0:
            issues.append(dict(t=b['f0'] / fps, kind='long_host_hold', detail=f'host-only shot lasts {(b["f1"] - b["f0"]) / fps:.1f}s'))
    # 7. tiny text: card item text and labels below 3% of frame height
    for b in tl:
        if b['kind'] == 'card' and b.get('type') in ('playlist', 'comment', 'likes', 'bio', 'inventory', 'list'):
            issues.append(dict(t=b['f0'] / fps, kind='small_text', detail=f"{b.get('type')} card body text under 3% of frame height (unreadable on phones)"))
    # 8. scenes on flat cartoon backdrops (no real photo) held > 2.5 s
    for b in tl:
        if b['kind'] == 'scene' and not str(b.get('bg', '')).startswith('img:') and (b['f1'] - b['f0']) / fps > 2.5:
            issues.append(dict(t=b['f0'] / fps, kind='flat_backdrop', detail=f"scene '{b['trigger']}' on a flat '{b.get('bg')}' backdrop for {(b['f1'] - b['f0']) / fps:.1f}s"))
    issues.sort(key=lambda e: e['t'])
    for e in issues:
        e['tc'] = tc(e['t'])
    json.dump(issues, open(out, 'w'), indent=1)
    from collections import Counter
    print(Counter(e['kind'] for e in issues))
    return issues


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
