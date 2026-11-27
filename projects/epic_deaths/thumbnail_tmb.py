"""Thumbnails in the Trust-Me-Bro thumbnail format (see thumbnails/REFERENCE_ANALYSIS.md), with our own host.

1  EPIC DEATHS       bright sunset battlefield; host screaming; Harald (arrow) + Arrichion (crowned corpse)
2  INSANE DEATHS     night palace + fire; host terrified; Attila (nosebleed) + Crassus (molten gold)
3  LEGENDARY DEATHS  white title band, split world (Olympia | sea battle); host shocked; Arrichion + Yi's drummer

  python3 thumbnail_tmb.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import skia  # noqa: E402

from engine.core import paint, rgb  # noqa: E402
from engine.text import size_for_cap  # noqa: E402
from engine.roundhead import draw_character, DETECTIVE as HOST  # noqa: E402
from engine.props import draw_prop  # noqa: E402
from cast import HARALD, ARRICHION_WREATH, ATTILA, CRASSUS, NEPHEW  # noqa: E402
from thumbnail import _text_path, text_width, glow, medal, nosebleed, star  # noqa: E402

TW, TH = 1920, 1080
OUT = os.path.join(HERE, 'thumbnails')
INK = '#141414'


# ---------------------------------------------------------------- title (full width, ghost layer)
def title_layout(s, width_frac=0.97, top_frac=0.025, tracking=0.015):
    cap = 300.0
    while text_width(s, size_for_cap(cap), tracking) > TW * width_frac:
        cap -= 1
    size = size_for_cap(cap)
    w = text_width(s, size, tracking)
    p = _text_path(s, size, tracking)
    p.offset((TW - w) / 2, TH * top_frac + cap)
    return p, cap


def title_full(c, path, cap, style='white'):
    if style == 'white':
        sh = paint('#000000', alpha=150)
        sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, cap * 0.07))
        q = skia.Path(path)
        q.offset(0, cap * 0.035)
        c.drawPath(q, sh)
        st = paint('#000000', stroke=cap * 0.05, alpha=90, join='round')
        st.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, cap * 0.03))
        c.drawPath(path, st)
        c.drawPath(path, paint('#FFFFFF'))
    else:
        c.drawPath(path, paint('#0A0A0A'))


def title_ghost(c, path, style='white', alpha=112):
    c.drawPath(path, paint('#FFFFFF' if style == 'white' else '#0A0A0A', alpha=alpha))


def white_band(c, h_frac=0.20, fade_frac=0.13):
    y1 = TH * h_frac
    y2 = TH * (h_frac + fade_frac)
    c.drawRect(skia.Rect(0, 0, TW, y1), paint('#FFFFFF'))
    sh = skia.GradientShader.MakeLinear([(0, y1), (0, y2)], [skia.Color(255, 255, 255, 255), skia.Color(255, 255, 255, 0)])
    c.drawRect(skia.Rect(0, y1, TW, y2), skia.Paint(Shader=sh))


# ---------------------------------------------------------------- thumbnail-grade faces
def head_shading(c, cx, cy, R, top_cut=-0.42, hands=True):
    c.save()
    clip = skia.Path()
    clip.addCircle(cx, cy, R * 0.965)
    if hands:                                   # keep the shading off the hands pressed on the cheeks
        hp = skia.Path()
        for side in (-1, 1):
            hp.addCircle(cx + side * 0.92 * R, cy + 0.40 * R, 0.30 * R)
        clip = skia.Op(clip, hp, skia.PathOp.kDifference_PathOp)
    c.clipPath(clip, doAntiAlias=True)
    c.clipRect(skia.Rect(cx - R, cy + top_cut * R, cx + R, cy + R))
    sh = skia.GradientShader.MakeRadial((cx - 0.18 * R, cy - 0.2 * R), 1.25 * R,
                                        [skia.Color(255, 255, 255, 0), skia.Color(255, 255, 255, 0), skia.Color(150, 155, 165, 120),
                                         skia.Color(95, 100, 110, 170)], [0.0, 0.55, 0.85, 1.0])
    c.drawRect(skia.Rect(cx - R, cy - R, cx + R, cy + R), skia.Paint(Shader=sh))
    c.restore()


def _stroke(w):
    return paint(INK, stroke=w, cap='round', join='round')


def lidded_eye(c, ex, ey, R, side, rx=0.085, ry=0.105, lid=0.42, droop=0.05, white_dot=True):
    c.drawOval(skia.Rect(ex - rx * R, ey - ry * R, ex + rx * R, ey + ry * R), paint(INK))
    if white_dot:
        c.drawCircle(ex + 0.028 * R, ey - 0.035 * R, 0.022 * R, paint('#FFFFFF'))
    # drooping upper lid: skin-coloured cap over the top of the eye + a black lid line, sloping down outward
    ly = ey - ry * R + lid * 2 * ry * R
    a = (ex - (rx + 0.05) * R, ly - side * droop * R)
    b = (ex + (rx + 0.05) * R, ly + side * droop * R)
    lidp = skia.Path()
    lidp.moveTo(*a)
    lidp.lineTo(*b)
    lidp.lineTo(b[0], ey - (ry + 0.08) * R)
    lidp.lineTo(a[0], ey - (ry + 0.08) * R)
    lidp.close()
    c.drawPath(lidp, paint('#F7F7F2'))
    c.drawLine(a[0], a[1], b[0], b[1], _stroke(0.028 * R))
    bag = skia.Path()
    bag.moveTo(ex - rx * R * 0.9, ey + ry * R + 0.035 * R)
    bag.quadTo(ex, ey + ry * R + 0.085 * R, ex + rx * R * 0.9, ey + ry * R + 0.035 * R)
    c.drawPath(bag, _stroke(0.016 * R))


def scream_face(c, cx, cy, R, mouth=1.0):
    head_shading(c, cx, cy, R)
    for side in (-1, 1):
        lidded_eye(c, cx + side * 0.25 * R, cy - 0.10 * R, R, side, droop=0.045)
    mx, my = cx, cy + 0.36 * R
    rx, ry = 0.22 * R * mouth, 0.29 * R * mouth
    m = skia.Path()
    m.addOval(skia.Rect(mx - rx, my - ry, mx + rx, my + ry))
    c.drawPath(m, paint('#2B140F'))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    c.drawOval(skia.Rect(mx - rx * 0.55, my - ry * 0.75, mx + rx * 0.55, my + ry * 0.2), paint('#140805'))
    c.drawOval(skia.Rect(mx - rx * 0.72, my + ry * 0.38, mx + rx * 0.72, my + ry * 1.25), paint('#F39BB1'))
    c.drawLine(mx, my + ry * 0.48, mx, my + ry * 0.8, paint('#C9677F', stroke=0.014 * R, cap='round'))
    c.restore()
    c.drawPath(m, _stroke(0.034 * R))
    for side in (-1, 1):                                            # cheek folds: short brackets around the mouth
        p = skia.Path()
        p.moveTo(cx + side * 0.27 * R, cy + 0.14 * R)
        p.cubicTo(cx + side * 0.35 * R, cy + 0.26 * R, cx + side * 0.35 * R, cy + 0.46 * R, cx + side * 0.27 * R, cy + 0.58 * R)
        c.drawPath(p, _stroke(0.02 * R))
    for k, dx in enumerate((-0.12, 0.12)):                           # chin creases
        p = skia.Path()
        p.moveTo(cx + dx * R - 0.07 * R, cy + 0.78 * R)
        p.quadTo(cx + dx * R, cy + 0.83 * R, cx + dx * R + 0.07 * R, cy + 0.78 * R)
        c.drawPath(p, _stroke(0.014 * R))
    rng = np.random.default_rng(4)
    for k in range(9):                                              # stubble dots
        c.drawCircle(cx + rng.uniform(-0.18, 0.18) * R, cy + rng.uniform(0.72, 0.9) * R, 0.009 * R, paint(INK))


def shock_face(c, cx, cy, R):
    head_shading(c, cx, cy, R)
    for side in (-1, 1):
        ex, ey = cx + side * 0.24 * R, cy - 0.06 * R
        c.drawOval(skia.Rect(ex - 0.11 * R, ey - 0.135 * R, ex + 0.11 * R, ey + 0.135 * R), paint(INK))
        c.drawCircle(ex + 0.04 * R, ey - 0.05 * R, 0.035 * R, paint('#FFFFFF'))
        c.drawCircle(ex - 0.03 * R, ey + 0.05 * R, 0.014 * R, paint('#FFFFFF'))
        br = skia.Path()                                            # raised brows
        br.moveTo(ex - 0.12 * R, ey - 0.25 * R + side * 0.0)
        br.quadTo(ex, ey - 0.33 * R, ex + 0.12 * R, ey - 0.25 * R)
        c.drawPath(br, _stroke(0.03 * R))
    mx, my = cx + 0.02 * R, cy + 0.36 * R
    m = skia.Path()
    m.addOval(skia.Rect(mx - 0.12 * R, my - 0.13 * R, mx + 0.12 * R, my + 0.15 * R))
    c.drawPath(m, paint('#2B140F'))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    c.drawOval(skia.Rect(mx - 0.1 * R, my + 0.02 * R, mx + 0.1 * R, my + 0.22 * R), paint('#F39BB1'))
    c.restore()
    c.drawPath(m, _stroke(0.03 * R))


def sweat(c, x, y, r, tilt=0.0):
    d = skia.Path()
    d.moveTo(x, y - r * 2.1)
    d.cubicTo(x + r * 0.95, y - r * 0.6, x + r, y + r, x, y + r)
    d.cubicTo(x - r, y + r, x - r * 0.95, y - r * 0.6, x, y - r * 2.1)
    c.save()
    c.rotate(tilt, x, y)
    c.drawPath(d, paint('#8ED3FF'))
    c.drawPath(d, _stroke(r * 0.2))
    c.drawCircle(x - r * 0.3, y - r * 0.05, r * 0.22, paint('#FFFFFF'))
    c.restore()


def big_host(c, cx, cy, R, face='scream', pose='cheeks'):
    draw_character(c, cx, cy, R, pose, 'blank', HOST, show_rim=False)
    if face == 'scream':
        scream_face(c, cx, cy, R)
        sweat(c, cx - 0.62 * R, cy - 0.30 * R, 0.07 * R, -20)
        sweat(c, cx + 0.66 * R, cy - 0.12 * R, 0.055 * R, 25)
        sweat(c, cx + 0.48 * R, cy - 0.40 * R, 0.045 * R, 15)
    else:
        shock_face(c, cx, cy, R)
        sweat(c, cx + 0.62 * R, cy - 0.32 * R, 0.065 * R, 20)


# ---------------------------------------------------------------- illustrated scenery
def outline_path(c, p, fill, w=7):
    c.drawPath(p, paint(fill))
    c.drawPath(p, paint(INK, stroke=w, join='round'))


def hills(c, y, amp, color, seed, w=7, bumps=4):
    rng = np.random.default_rng(seed)
    p = skia.Path()
    p.moveTo(-20, TH + 20)
    xs = np.linspace(-20, TW + 20, bumps * 2 + 1)
    p.lineTo(-20, y)
    for k in range(bumps):
        x0, x1, x2 = xs[2 * k], xs[2 * k + 1], xs[2 * k + 2]
        p.quadTo(x1, y - amp * rng.uniform(0.6, 1.2), x2, y + rng.uniform(-amp * 0.2, amp * 0.2))
    p.lineTo(TW + 20, TH + 20)
    p.close()
    outline_path(c, p, color, w)


def cloud(c, x, y, s, color='#FFFFFF', alpha=255):
    p = skia.Path()
    for dx, dy, r in ((-0.6, 0.1, 0.42), (-0.2, -0.15, 0.55), (0.3, -0.05, 0.5), (0.7, 0.12, 0.38)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    p2 = skia.Path()
    p2.addRect(skia.Rect(x - 0.9 * s, y + 0.1 * s, x + 0.95 * s, y + 0.45 * s))
    u = skia.Op(p, p2, skia.PathOp.kUnion_PathOp)
    c.drawPath(u, paint(color, alpha=alpha))
    c.drawPath(u, paint(INK, stroke=6, alpha=alpha))


def arrow_in_ground(c, x, y, ang, L=170):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawLine(0, 0, 0, -L, paint(INK, stroke=14, cap='round'))
    c.drawLine(0, 0, 0, -L, paint('#8A5A2E', stroke=7, cap='round'))
    for s in (-1, 1):
        f = skia.Path()
        f.moveTo(0, -L + 8)
        f.lineTo(s * 22, -L - 26)
        f.lineTo(0, -L - 12)
        f.close()
        outline_path(c, f, '#F2F2F2', 5)
    c.restore()


def tombstone(c, x, y, s, text='R.I.P.'):
    p = skia.Path()
    p.moveTo(x - s, y)
    p.lineTo(x - s, y - 1.3 * s)
    p.arcTo(skia.Rect(x - s, y - 2.3 * s, x + s, y - 0.3 * s), 180, 180, False)
    p.lineTo(x + s, y)
    p.close()
    outline_path(c, p, '#A7ABB3', 8)
    sz = size_for_cap(0.36 * s)
    w = text_width(text, sz, 0.02)
    q = _text_path(text, sz, 0.02)
    q.offset(x - w / 2, y - 1.15 * s)
    c.drawPath(q, paint('#4A4E57'))


def column(c, x, base, h, w=70):
    p = skia.Path()
    p.addRect(skia.Rect(x - w / 2, base - h, x + w / 2, base))
    outline_path(c, p, '#EFE6D2', 7)
    for k in (-0.25, 0, 0.25):
        c.drawLine(x + k * w, base - h + 25, x + k * w, base - 12, paint('#C9BFA8', stroke=5))
    cap = skia.Path()
    cap.addRect(skia.Rect(x - w * 0.75, base - h - 26, x + w * 0.75, base - h))
    outline_path(c, cap, '#EFE6D2', 7)


def fire(c, x, y, s, seed=0):
    rng = np.random.default_rng(seed)
    for k, (col, sc) in enumerate((('#E8361E', 1.0), ('#FF8A1F', 0.72), ('#FFD84A', 0.45))):
        p = skia.Path()
        n = 5
        p.moveTo(x - s * sc, y)
        for i in range(n):
            u = (i + 0.5) / n
            px = x - s * sc + 2 * s * sc * u
            p.quadTo(px - s * sc * 0.25, y - s * sc * rng.uniform(1.2, 2.2), px + s * sc * 0.2 / n, y - s * sc * rng.uniform(0.4, 0.8))
        p.lineTo(x + s * sc, y)
        p.close()
        c.drawPath(p, paint(col))
        if k == 0:
            c.drawPath(p, paint(INK, stroke=7, join='round'))


def flying_arrow(c, x, y, ang, L=150):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawLine(-L / 2, 0, L / 2, 0, paint(INK, stroke=11, cap='round'))
    c.drawLine(-L / 2, 0, L / 2, 0, paint('#8A5A2E', stroke=5, cap='round'))
    head = skia.Path()
    head.moveTo(L / 2 + 24, 0)
    head.lineTo(L / 2 - 4, -12)
    head.lineTo(L / 2 - 4, 12)
    head.close()
    outline_path(c, head, '#C9CED6', 4)
    for sgn in (-1, 1):
        f = skia.Path()
        f.moveTo(-L / 2 + 26, 0)
        f.lineTo(-L / 2 - 6, sgn * 16)
        f.lineTo(-L / 2 + 8, 0)
        f.close()
        outline_path(c, f, '#F2F2F2', 4)
    c.restore()


def bush(c, x, y, s, color='#3E7F35'):
    p = skia.Path()
    for dx, dy, r in ((-0.5, 0.05, 0.45), (0.0, -0.18, 0.55), (0.5, 0.05, 0.45)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    outline_path(c, skia.Op(p, skia.Path(), skia.PathOp.kUnion_PathOp), color, 6)


def shield(c, x, y, s, ang=0, col='#B23A2E'):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawCircle(0, 0, s, paint(col))
    c.drawCircle(0, 0, s, paint(INK, stroke=7))
    c.drawCircle(0, 0, s * 0.25, paint('#C9A050'))
    c.drawCircle(0, 0, s * 0.25, paint(INK, stroke=5))
    c.restore()


def embers(c, x0, x1, y0, y1, n=40, seed=5):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(3, 8)
        glow(c, x, y, r * 3, '#FF9A3A', 120)
        c.drawCircle(x, y, r, paint('#FFD27A'))


def smoke(c, x, y, s, alpha=150):
    for k, (dx, dy, r) in enumerate(((0, 0, 0.5), (0.25, -0.55, 0.6), (-0.1, -1.15, 0.75), (0.35, -1.8, 0.9))):
        c.drawCircle(x + dx * s, y + dy * s, r * s, paint('#5A5560', alpha=alpha - 25 * k))


def birds(c, pts):
    for x, y, s in pts:
        p = skia.Path()
        p.moveTo(x - s, y)
        p.quadTo(x - s / 2, y - s * 0.6, x, y)
        p.quadTo(x + s / 2, y - s * 0.6, x + s, y)
        c.drawPath(p, paint(INK, stroke=6, cap='round', join='round'))


def ladle_pour(c, x, y, s):
    """A golden ladle tipped over a mouth at (x, y): molten gold stream."""
    st = skia.Path()
    st.moveTo(x - 0.05 * s, y - 1.25 * s)
    st.cubicTo(x - 0.12 * s, y - 0.8 * s, x + 0.08 * s, y - 0.4 * s, x, y)
    st.cubicTo(x + 0.16 * s, y - 0.42 * s, x + 0.06 * s, y - 0.85 * s, x + 0.12 * s, y - 1.25 * s)
    st.close()
    sh = skia.GradientShader.MakeLinear([(x - 0.1 * s, 0), (x + 0.15 * s, 0)], [rgb('#FFF27A'), rgb('#F2A900'), rgb('#C47800')], [0, 0.5, 1])
    c.drawPath(st, skia.Paint(Shader=sh, AntiAlias=True))
    c.drawPath(st, paint('#5A3A00', stroke=5))
    glow(c, x, y - 0.2 * s, 0.6 * s, '#FFE680', 120)
    c.save()
    c.translate(x + 0.03 * s, y - 1.35 * s)
    c.rotate(-35)
    bowl = skia.Path()
    bowl.addArc(skia.Rect(-0.35 * s, -0.3 * s, 0.35 * s, 0.3 * s), 0, 180)
    bowl.close()
    outline_path(c, bowl, '#8C939C', 6)
    c.drawLine(0.32 * s, 0, 1.3 * s, -0.55 * s, paint(INK, stroke=22, cap='round'))
    c.drawLine(0.32 * s, 0, 1.3 * s, -0.55 * s, paint('#8C939C', stroke=12, cap='round'))
    c.restore()


# ---------------------------------------------------------------- thumbnails
def tmb_1(c):
    """EPIC DEATHS - sunset battlefield."""
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, 760)], [rgb('#FF6A2E'), rgb('#FFA94D'), rgb('#FFE0A0')], [0, 0.55, 1])
    c.drawRect(skia.Rect(0, 0, TW, TH), skia.Paint(Shader=sky))
    glow(c, 960, 620, 950, '#FFF3C4', 210)
    cloud(c, 180, 300, 90, '#FFE9D2')
    cloud(c, 1760, 280, 100, '#FFE9D2')
    hills(c, 690, 150, '#7E5BA8', 3, 7, 3)
    for x, y, a in ((160, 420, 20), (420, 300, 28), (1530, 330, 160), (1790, 450, 150), (1250, 250, 165), (640, 230, 24)):
        flying_arrow(c, x, y, a)
    hills(c, 800, 90, '#5E9C4A', 5, 7, 4)
    c.drawRect(skia.Rect(0, 900, TW, TH), paint('#4F8A3C'))
    for x, y, sc in ((560, 900, 70), (1400, 905, 64), (90, 860, 60), (1860, 870, 66)):
        bush(c, x, y, sc)
    for x, y, a in ((150, 1010, 18), (590, 980, -14), (1350, 995, 12), (1820, 960, -20)):
        arrow_in_ground(c, x, y, a)
    shield(c, 560, 1030, 60, 20)
    shield(c, 1420, 1050, 54, -30, '#3E6BB5')
    tombstone(c, 1850, 1085, 78)
    path, cap = title_layout('EPIC DEATHS')
    title_full(c, path, cap, 'white')
    # Harald: arrow through the neck, keeling over
    c.save()
    c.rotate(-12, 380, 1000)
    draw_character(c, 380, 610, 150, 'cheeks', 'ko_o', HARALD, show_rim=False)
    c.restore()
    flying_arrow(c, 420, 790, -28, 300)
    # Arrichion: crowned corpse, waving, gold medal
    glow(c, 1560, 560, 300, '#FFF6C0', 180)
    draw_character(c, 1560, 590, 146, 'wave', 'ko_grin', ARRICHION_WREATH, show_rim=False)
    medal(c, 1563, 590 + 1.72 * 146, 0.36 * 146, 590 + 1.05 * 146)
    star(c, 1410, 420, 28)
    star(c, 1730, 470, 32)
    big_host(c, 960, 625, 345, 'scream', 'cheeks')
    title_ghost(c, path, 'white')


def tmb_2(c):
    """INSANE DEATHS - night palace and fire."""
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, 820)], [rgb('#0A0F26'), rgb('#1B2650'), rgb('#3A2350')], [0, 0.6, 1])
    c.drawRect(skia.Rect(0, 0, TW, TH), skia.Paint(Shader=sky))
    rng = np.random.default_rng(2)
    for k in range(60):
        c.drawCircle(rng.uniform(0, TW), rng.uniform(170, 600), rng.uniform(1.5, 3.5), paint('#FFFFFF', alpha=int(rng.uniform(90, 220))))
    glow(c, 1530, 390, 260, '#FFF5D6', 120)
    c.drawCircle(1530, 390, 120, paint('#F4EBD0'))
    c.drawCircle(1530, 390, 120, paint(INK, stroke=7))
    for x, y, r in ((1490, 360, 18), (1570, 420, 24), (1545, 340, 10)):
        c.drawCircle(x, y, r, paint('#DCD1B2'))
    pal = skia.Path()                                               # palace silhouette, left
    pal.addRect(skia.Rect(-10, 560, 520, 1100))
    pal.addRect(skia.Rect(60, 470, 200, 560))
    pal.addRect(skia.Rect(320, 500, 470, 560))
    outline_path(c, pal, '#241A33', 7)
    for wx in (100, 220, 360):
        c.drawRect(skia.Rect(wx, 640, wx + 60, 730), paint('#FFB43A'))
        c.drawRect(skia.Rect(wx, 640, wx + 60, 730), paint(INK, stroke=6))
    glow(c, 260, 980, 520, '#FF7A2A', 170)
    fire(c, 160, 1090, 150, 1)
    fire(c, 430, 1090, 110, 2)
    hills(c, 930, 60, '#1F1830', 8, 7, 3)
    for x in (1380, 1520, 1660, 1800):                               # Roman columns, right (Crassus)
        column(c, x, 1000, 290, 64)
    embers(c, 0, 700, 380, 1000, 45, 7)
    smoke(c, 330, 470, 120, 120)
    path, cap = title_layout('INSANE DEATHS')
    title_full(c, path, cap, 'white')
    draw_character(c, 375, 630, 150, 'cheeks', 'shock', ATTILA, show_rim=False)
    nosebleed(c, 375, 630, 150)
    draw_character(c, 1550, 625, 148, 'shrug', 'ko_o', CRASSUS, show_rim=False)
    ladle_pour(c, 1550, 625 + 0.36 * 148, 140)
    big_host(c, 960, 625, 345, 'scream', 'cheeks')
    title_ghost(c, path, 'white')


def tmb_3(c):
    """LEGENDARY DEATHS - white title band, split world."""
    c.drawRect(skia.Rect(0, 0, TW / 2, TH), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 200), (0, 860)], [rgb('#5CC2FF'), rgb('#C8ECFF')])))
    c.drawRect(skia.Rect(TW / 2, 0, TW, TH), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 200), (0, 860)], [rgb('#B0221B'), rgb('#FF9B4A')])))
    # left: Olympia
    cloud(c, 260, 360, 90)
    birds(c, [(560, 330, 26), (630, 300, 20), (520, 290, 16)])
    for x in (110, 230, 350, 470):
        column(c, x, 860, 330, 62)
    roof = skia.Path()
    roof.moveTo(50, 505)
    roof.lineTo(285, 400)
    roof.lineTo(530, 505)
    roof.close()
    outline_path(c, roof, '#EFE6D2', 7)
    sand = skia.Path()
    sand.addRect(skia.Rect(-10, 850, TW / 2, TH + 10))
    outline_path(c, sand, '#E9C98A', 7)
    # right: sea battle
    glow(c, 1500, 640, 520, '#FFD27A', 150)
    sea = skia.Path()
    sea.addRect(skia.Rect(TW / 2, 820, TW + 10, TH + 10))
    outline_path(c, sea, '#2F7FC4', 7)
    for k in range(9):
        x = TW / 2 + 60 + k * 110
        wv = skia.Path()
        wv.moveTo(x, 900 + (k % 2) * 60)
        wv.quadTo(x + 30, 880 + (k % 2) * 60, x + 60, 900 + (k % 2) * 60)
        c.drawPath(wv, paint('#BFE3F7', stroke=6))
    draw_prop(c, 'jp_ship', 1720, 800, 170, burning=True) if False else draw_prop(c, 'jp_ship', 1720, 800, 170)
    fire(c, 1720, 760, 70, 4)
    smoke(c, 1740, 640, 90, 140)
    embers(c, 1500, 1900, 420, 820, 25, 9)
    draw_prop(c, 'turtle_ship', 1300, 860, 190)
    c.drawLine(TW / 2, 0, TW / 2, TH, paint(INK, stroke=8))
    white_band(c, 0.205, 0.12)
    path, cap = title_layout('LEGENDARY DEATHS', top_frac=0.03)
    title_full(c, path, cap, 'black')
    # Arrichion lying dead, crowned, medal on chest
    c.save()
    c.rotate(-90, 200, 885)
    draw_character(c, 200, 855, 118, 'idle', 'ko_grin', ARRICHION_WREATH, show_rim=False)
    c.restore()
    medal(c, 350, 868, 0.32 * 118, 868 - 0.6 * 118)
    star(c, 150, 700, 26)
    star(c, 430, 690, 22)
    # Yi's nephew beating the war drum on deck
    draw_character(c, 1545, 640, 140, 'wave', 'angry', NEPHEW, show_rim=False)
    draw_prop(c, 'drum', 1750, 810, 140, hit=True)
    big_host(c, 960, 600, 335, 'shock', 'cheeks')
    title_ghost(c, path, 'black', alpha=90)


def render(fn, name):
    surf = skia.Surface(TW, TH)
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    fn(c)
    img = surf.makeImageSnapshot().toarray()[:, :, :3]
    os.makedirs(OUT, exist_ok=True)
    cv2.imwrite(os.path.join(OUT, f'{name}_master.png'), img)
    small = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(OUT, f'{name}.jpg'), small, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return img


def compare(imgs, refs):
    """Side-by-side with the reference format, plus phone sizes."""
    tiles = [cv2.resize(r, (640, 360)) for r in refs[:3]] + [cv2.resize(i, (640, 360), interpolation=cv2.INTER_AREA) for i in imgs]
    sheet = np.vstack([np.hstack(tiles[0:3]), np.hstack(tiles[3:6])])
    cv2.imwrite(os.path.join(OUT, 'tmb_vs_reference.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    rows = []
    for img in imgs:
        row = []
        for w in (360, 246, 168):
            h = int(w * 9 / 16)
            pad = np.full((210, w + 16, 3), 255, np.uint8)
            pad[8:8 + h, 8:8 + w] = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
            row.append(pad)
        rows.append(np.hstack(row))
    cv2.imwrite(os.path.join(OUT, 'tmb_phone_sizes.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == '__main__':
    imgs = [render(tmb_1, 'tmb_1_epic_deaths'), render(tmb_2, 'tmb_2_insane_deaths'), render(tmb_3, 'tmb_3_legendary_deaths')]
    ref_dir = sys.argv[1] if len(sys.argv) > 1 else None
    refs = [cv2.imread(os.path.join(ref_dir, n + '.png')) for n in ('crazy_places', 'unknown', 'lost_history')] if ref_dir else []
    if refs and all(r is not None for r in refs):
        compare(imgs, refs)
    print('done')
