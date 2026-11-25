"""Model sheet for the channel host (renders design/host_character_sheet.png).

Usage: python3 design/make_sheet.py [before_png]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))

import numpy as np  # noqa: E402
import skia  # noqa: E402
from engine.core import W, H, new_surface, draw_background, paint, rgb  # noqa: E402
from engine.character import (draw_character, HOST, AGENT, subject, R_NORMAL, R_ZOOM, R_PIP,  # noqa: E402
                              NORMAL_CENTER, ZOOM_CENTER)
from engine.text import draw_text, draw_callout  # noqa: E402

SW, SH = 2400, 1600
BG = '#0E0E0F'
PANEL = '#17181B'


def label(c, s, x, y, cap=20, color='#BDBDBD', center=False):
    from engine.text import text_width, size_for_cap
    size = size_for_cap(cap)
    if center:
        x -= text_width(s, size, 0.05) / 2
    draw_text(c, s, x, y, size, style=color, tracking=0.05, shadow=False, grunge=False)


def panel(c, x0, y0, x1, y1, title=None):
    r = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 18, 18)
    c.drawRRect(r, paint(PANEL))
    if title:
        label(c, title, x0 + 22, y0 + 40, cap=19, color='#FFC83D')


def frame_image(fn):
    s = new_surface()
    c = s.getCanvas()
    draw_background(c)
    fn(c)
    return s.makeImageSnapshot()


def put(c, img, x, y, w, h):
    c.drawImageRect(img, skia.Rect(x, y, x + w, y + h),
                    skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    c.drawRect(skia.Rect(x, y, x + w, y + h), paint('#2E2F33', stroke=2))


def main(before_png=None):
    surf = skia.Surface(SW, SH)
    c = surf.getCanvas()
    c.clear(rgb(BG))
    # header
    draw_text(c, 'CHANNEL HOST', 60, 92, 64, style='silver', tracking=0.05, grunge=False)
    label(c, 'MODEL SHEET V1  ·  ORIGINAL DESIGN  ·  RIG: ENGINE/CHARACTER.PY', 860, 86, cap=20, color='#8E8E8E')

    # A: front view + palette
    panel(c, 40, 130, 740, 1100, 'FRONT VIEW  ·  DEFAULT')
    c.drawOval(skia.Rect(255, 955, 525, 995), paint('#000000', alpha=120))
    draw_character(c, 390, 470, 165, 'hips', 'talk')
    panel(c, 40, 1140, 740, 1560, 'PALETTE')
    sw = [('#FFC83D', 'HOODIE'), ('#E9A92A', 'SHADE'), ('#3A3F4B', 'JEANS'), ('#F4F4F4', 'SNEAKERS'),
          ('#FBF6EE', 'SKIN'), ('#2B1F1B', 'HAIR'), ('#141414', 'OUTLINE'), ('#FF8A8A', 'BLUSH')]
    for i, (hx, nm) in enumerate(sw):
        x = 70 + (i % 4) * 166
        y = 1210 + (i // 4) * 165
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + 140, y + 90), 12, 12), paint(hx))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + 140, y + 90), 12, 12), paint('#3A3A3A', stroke=2))
        label(c, nm, x, y + 118, cap=13, color='#BDBDBD')
        label(c, hx.upper(), x, y + 142, cap=13, color='#7A7A7A')

    # B1: expressions (busts)
    panel(c, 780, 130, 2360, 710, 'EXPRESSIONS  ·  SWAP EVERY ~1 S AT PHRASE POINTS (NO LIP-SYNC)')
    exprs = ['talk', 'talk2', 'o', 'smile', 'grin', 'skeptic', 'frown', 'grimace', 'shock', 'evil']
    for i, e in enumerate(exprs):
        x = 940 + (i % 5) * 290
        y = 300 + (i // 5) * 260
        c.save()
        c.clipRect(skia.Rect(x - 135, y - 125, x + 135, y + 100))
        draw_character(c, x, y, 72, 'hips', e)
        c.restore()
        label(c, e.upper(), x, y + 132, cap=16, color='#9A9A9A', center=True)

    # B2: poses
    panel(c, 780, 740, 2360, 1110, 'POSES')
    poses = [('hips', 'talk', {}), ('wave', 'smile', {}), ('point', 'talk', {}), ('chin', 'skeptic', {}),
             ('nerd', 'skeptic', {'glint': True}), ('shrug', 'grimace', {}), ('cheeks', 'shock', {})]
    for i, (pz, e, kw) in enumerate(poses):
        x = 900 + i * 215
        draw_character(c, x, 890, 60, pz, e, **kw)
        label(c, ('PUSH GLASSES' if pz == 'nerd' else pz.upper()), x, 1095, cap=15, color='#9A9A9A', center=True)

    # B3: in the format (1080p frames, scaled)
    panel(c, 780, 1140, 1900, 1560, 'IN THE FORMAT  ·  SAME FRAMING AS THE BLUEPRINT')
    f1 = frame_image(lambda k: (draw_character(k, *NORMAL_CENTER, R_NORMAL, 'wave', 'talk'),
                                draw_callout(k, '$5 MILLION')))
    f2 = frame_image(lambda k: draw_character(k, *ZOOM_CENTER, R_ZOOM, 'cheeks', 'shock'))

    def pip(k):
        r = skia.Rect(330, 150, 1590, 860)
        sh = skia.GradientShader.MakeLinear(points=[(0, 150), (0, 860)], colors=[rgb('#5A5F66'), rgb('#2C2F33')])
        k.drawRect(r, paint('#FFFFFF', shader=sh))
        for i in range(6):
            k.drawRect(skia.Rect(420 + i * 190, 260 + i * 18, 520 + i * 190, 760 - i * 10), paint('#787D85', alpha=90))
        for y in range(150, 860, 6):
            k.drawLine(330, y, 1590, y, paint('#000000', stroke=1, alpha=40))
        label(k, 'CAM 03  2019-08-15 14:02:31', 360, 200, cap=26, color='#E8E8E8')
        k.drawRect(r, paint('#111111', stroke=4))
        draw_character(k, 420, 900, R_PIP, 'hips', 'o')
    f3 = frame_image(pip)
    for i, (img, nm) in enumerate([(f1, 'NORMAL  1.00'), (f2, 'PUNCH-IN  1.52'), (f3, 'PIP  0.47')]):
        x = 810 + i * 365
        put(c, img, x, 1210, 340, 191)
        label(c, nm, x + 170, 1445, cap=16, color='#9A9A9A', center=True)

    # B4: before / after
    panel(c, 1930, 1140, 2360, 1560, 'BEFORE  ->  AFTER')
    if before_png and os.path.exists(before_png):
        import cv2
        b = cv2.imread(before_png)[:, :, ::-1]
        b = np.dstack([b, np.full(b.shape[:2], 255, np.uint8)]).copy()
        bi = skia.Image.fromarray(b, colorType=skia.ColorType.kRGBA_8888_ColorType)
        c.drawImageRect(bi, skia.Rect(1955, 1200, 1955 + 170, 1200 + 227), skia.SamplingOptions(skia.FilterMode.kLinear))
    draw_character(c, 2250, 1290, 46, 'hips', 'smile')
    label(c, 'OLD', 2040, 1480, cap=15, color='#7A7A7A', center=True)
    label(c, 'NEW HOST', 2250, 1480, cap=15, color='#FFC83D', center=True)
    label(c, 'TOO SIMILAR', 2040, 1515, cap=11, color='#6A6A6A', center=True)
    label(c, 'ORIGINAL', 2250, 1515, cap=11, color='#6A6A6A', center=True)

    out = os.path.join(HERE, 'host_character_sheet.png')
    img = surf.makeImageSnapshot().toarray()
    import cv2
    cv2.imwrite(out, img[:, :, :3])
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
