"""Poster text layout with fit checks and auto-shrink (offline, from the real font advance widths).

usage: python analysis/scripts/b07_poster_layout.py  ->  render/src/data/poster_layout.json

Coordinates are poster-local reference px (854x480 world, before CalibrationHQ's POSTER_DX content offset).
Targets come from the reference at f075 / f143 (camera inverted), measured with dark-pixel extents:
  WANTED        231 px wide, cap ~34.5            -> tracking solved for that width
  ARTHUR MORGAN 219 px wide, cap 17.5             -> tracking solved for that width
  list items    'TRAINS' / 'BANKS' 5% wider than untracked Bitter 900 at the same cap -> +0.04 em tracking;
                'HALF THE WEST' is set smaller in the reference (row height 19 vs 22 px): it auto-shrinks to the
                list's measured right limit (x 526 local)
Every string must sit inside its container; the script fails loudly otherwise.
"""
import json, sys
from PIL import ImageFont
from fontTools.ttLib import TTFont

F = 'render/public/fonts/bitter-latin-900-normal.ttf'
t = TTFont(F); CAP = t['OS/2'].sCapHeight / t['head'].unitsPerEm
PF = ImageFont.truetype(F, 400)


def adv(txt, size, tr_em):
    return PF.getlength(txt) * size / 400 + tr_em * size * (len(txt) - 1)


def solve_tracking(txt, cap, target_w):
    size = cap / CAP
    return (target_w - adv(txt, size, 0)) / (size * (len(txt) - 1))


specs = {
    # key: (text, cap ref px, tracking em or ('solve', width), align, x, container)
    'WANTED': ('WANTED', 34.5, ('solve', 233.0), 'centre', 428, (306, 552)),
    'NAME': ('ARTHUR MORGAN', 17.5, ('solve', 220.0), 'centre', 428, (306, 552)),
    'WANTED_FOR': ('WANTED FOR', 6.8, 0.30, 'centre', 428, (380, 476)),
    'ITEM0': ('TRAINS', 16, 0.04, 'left', 361, (361, 526)),
    'ITEM1': ('BANKS', 16, 0.04, 'left', 361, (361, 526)),
    'ITEM2': ('HALF THE WEST', 16, 0.04, 'left', 361, (361, 526)),
    'REWARD': ('REWARD', 8.0, 0.32, 'left', 350, (348, 432)),
    'VALUE': ('$????', 19.5, 0.06, 'left', 443, (443, 548)),
    'SIDE_WANTED': ('WANTED', 22, 0.06, 'centre', 0, (-95, 95)),
    'SIDE_DOA': ('DEAD OR ALIVE', 5.2, 0.25, 'centre', 0, (-90, 90)),
    'SIDE_NAME': ('ARTHUR MORGAN', 11.5, 0.0, 'centre', 0, (-95, 95)),
    'SIDE_REWARD': ('REWARD', 5.2, 0.30, 'centre', 0, (-60, 60)),
    'SIDE_VALUE': ('$?', 12, 0.04, 'centre', 0, (-60, 60)),
}
L = {}; ok = True
for k, (txt, cap, tr, align, x, (c0, c1)) in specs.items():
    if isinstance(tr, tuple):
        tr = round(solve_tracking(txt, cap, tr[1]), 4)
    size = cap / CAP; w = adv(txt, size, tr); shrunk = False
    if w > (c1 - c0):
        s_ = (c1 - c0) / w; size *= s_; w *= s_; cap *= s_; shrunk = True
    x0 = x - w / 2 if align == 'centre' else x
    inside = x0 >= c0 - 0.01 and x0 + w <= c1 + 0.01
    L[k] = dict(text=txt, font_size_ref=round(size, 3), cap_ref=round(cap, 2), tracking_em=tr, align=align, x=x, width_ref=round(w, 2),
                container=[c0, c1], auto_shrunk=shrunk, left=round(x0, 2), right=round(x0 + w, 2), inside=inside)
    ok &= inside
json.dump(dict(font='Bitter 900', cap_em=CAP, items=L, all_inside=ok), open('render/src/data/poster_layout.json', 'w'), indent=1)
for k, v in L.items():
    if not k.startswith('SIDE'):
        print(f"{k:11s} cap {v['cap_ref']:6.2f} size {v['font_size_ref']:7.3f} track {v['tracking_em']:+.4f}em  {v['left']:7.2f}-{v['right']:7.2f}  {'SHRUNK' if v['auto_shrunk'] else ''}")
print('ALL INSIDE', ok)
if not ok:
    sys.exit('layout overflow: a string does not fit its container')
