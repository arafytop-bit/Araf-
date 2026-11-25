"""Model sheet for the channel host in the round-head cartoon style.

Renders design/host_character_sheet.png. Usage: python3 design/make_sheet.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))

import skia  # noqa: E402
from engine.core import new_surface, draw_background, paint, rgb  # noqa: E402
from engine.roundhead import (draw_character, DETECTIVE, REPORTER, SLEUTH, R_NORMAL, R_ZOOM, R_PIP,  # noqa: E402
                              NORMAL_CENTER, ZOOM_CENTER)
from engine.text import draw_text, draw_callout, draw_speech, text_width, size_for_cap  # noqa: E402

SW, SH = 2400, 1600
BG, PANEL = '#0E0E0F', '#17181B'


def label(c, s, x, y, cap=20, color='#BDBDBD', center=False):
    size = size_for_cap(cap)
    if center:
        x -= text_width(s, size, 0.05) / 2
    draw_text(c, s, x, y, size, style=color, tracking=0.05, shadow=False, grunge=False)


def panel(c, x0, y0, x1, y1, title=None):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 18, 18), paint(PANEL))
    if title:
        label(c, title, x0 + 22, y0 + 40, cap=19, color='#D9B56E')


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


def main():
    surf = skia.Surface(SW, SH)
    c = surf.getCanvas()
    c.clear(rgb(BG))
    draw_text(c, 'CHANNEL HOST', 60, 92, 64, style='silver', tracking=0.05, grunge=False)
    label(c, 'MODEL SHEET V2  ·  ROUND-HEAD CARTOON STYLE', 860, 86, cap=20, color='#8E8E8E')

    # front view + speech caption sample
    panel(c, 40, 130, 740, 1100, 'FRONT VIEW  ·  THE DETECTIVE')
    c.drawOval(skia.Rect(160, 935, 440, 975), paint('#000000', alpha=120))
    draw_character(c, 300, 440, 150, 'hips', 'talk', DETECTIVE)
    draw_speech(c, 'I did the research.', 440, 214, cap_px=26, tail=((470, 232), (446, 264)), rot=-3)

    # palette
    panel(c, 40, 1130, 740, 1560, 'PALETTE')
    sw = [('#6A4A38', 'FEDORA'), ('#2A221E', 'HAT BAND'), ('#C9A26B', 'TRENCH'), ('#7D5B3A', 'BELT'),
          ('#B23A32', 'TIE'), ('#EFEAE0', 'SHIRT'), ('#3D414C', 'PANTS'), ('#4A3329', 'SHOES'),
          ('#F8F8F5', 'SKIN'), ('#151515', 'INK')]
    for i, (hx, nm) in enumerate(sw):
        x = 66 + (i % 5) * 134
        y = 1200 + (i // 5) * 170
        r = skia.RRect.MakeRectXY(skia.Rect(x, y, x + 110, y + 80), 12, 12)
        c.drawRRect(r, paint(hx))
        c.drawRRect(r, paint('#3A3A3A', stroke=2))
        label(c, nm, x, y + 106, cap=11, color='#BDBDBD')
        label(c, hx.upper(), x, y + 130, cap=11, color='#7A7A7A')

    # expressions
    panel(c, 780, 130, 2360, 720, 'EXPRESSIONS  ·  EYES DO THE ACTING, MOUTH ONLY WHEN NEEDED')
    exprs = ['neutral', 'talk', 'talk2', 'smile', 'grin', 'smug', 'deadpan', 'skeptic', 'angry', 'evil',
             'sad', 'cry', 'nervous', 'grimace', 'shock']
    for i, e in enumerate(exprs):
        x = 905 + (i % 5) * 305
        y = 268 + (i // 5) * 178
        c.save()
        c.clipRect(skia.Rect(x - 130, y - 96, x + 130, y + 62))
        draw_character(c, x, y, 50, 'idle', e, DETECTIVE)
        c.restore()
        label(c, e.upper(), x + 95, y + 10, cap=14, color='#9A9A9A')

    # poses
    panel(c, 780, 750, 2360, 1110, 'POSES')
    poses = [('idle', 'talk'), ('hips', 'smug'), ('wave', 'smile'), ('point', 'talk'), ('chin', 'skeptic'),
             ('inspect', 'neutral'), ('shrug', 'nervous'), ('cheeks', 'shock')]
    for i, (pz, e) in enumerate(poses):
        x = 885 + i * 198
        draw_character(c, x, 870, 50, pz, e, DETECTIVE)
        label(c, ('MAGNIFIER' if pz == 'inspect' else pz.upper()), x, 1090, cap=14, color='#9A9A9A', center=True)

    # in the format
    panel(c, 780, 1140, 1900, 1560, 'IN THE FORMAT  ·  SAME FRAMING AS THE BLUEPRINT')
    f1 = frame_image(lambda k: (draw_character(k, *NORMAL_CENTER, R_NORMAL, 'wave', 'talk', DETECTIVE),
                                draw_callout(k, '$5 MILLION')))
    f2 = frame_image(lambda k: draw_character(k, *ZOOM_CENTER, R_ZOOM, 'cheeks', 'shock', DETECTIVE))

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
        draw_character(k, 420, 890, R_PIP, 'idle', 'talk2', DETECTIVE, look=(0.25, -0.05))
    f3 = frame_image(pip)
    for i, (img, nm) in enumerate([(f1, 'NORMAL  1.00'), (f2, 'PUNCH-IN  1.52'), (f3, 'PIP  0.47')]):
        x = 810 + i * 365
        put(c, img, x, 1210, 340, 191)
        label(c, nm, x + 170, 1445, cap=16, color='#9A9A9A', center=True)

    # outfit options
    panel(c, 1930, 1140, 2360, 1560, 'OUTFIT OPTIONS')
    for i, (pal, ab, nm) in enumerate([(DETECTIVE, 'A', 'DETECTIVE'), (REPORTER, 'B', 'REPORTER'), (SLEUTH, 'C', 'SLEUTH')]):
        x = 2010 + i * 135
        draw_character(c, x, 1260, 34, 'idle', 'smile' if i == 0 else 'neutral', pal)
        col = '#D9B56E' if i == 0 else '#9A9A9A'
        label(c, ab, x, 1418, cap=16, color=col, center=True)
        label(c, nm, x, 1446, cap=10, color=col, center=True)
    label(c, 'SAME RIG · SWAP IN ONE LINE', 2145, 1500, cap=12, color='#6A6A6A', center=True)

    out = os.path.join(HERE, 'host_character_sheet.png')
    import cv2
    cv2.imwrite(out, surf.makeImageSnapshot().toarray()[:, :, :3])
    print('wrote', out)


if __name__ == '__main__':
    main()
