"""YouTube thumbnails for "Most Epic Deaths" (1280x720 deliverables, composed at 1920x1080).

A: "WON WHILE DEAD"         - Arrichion, crowned as a corpse, X-eyes and a grin; the host in shock.
B: "KILLED BY A NOSEBLEED"  - Attila, the most feared man in Europe, nose pouring blood.
C: "5 EPIC DEATHS"          - the five, X-eyed, in spotlights (listicle hook).

  python3 thumbnail.py            -> thumbnails/thumb_{A,B,C}.jpg (+ _master.png) and a mobile-size preview sheet
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
from engine.text import font, size_for_cap, glyph_layout  # noqa: E402
from engine.roundhead import draw_character, DETECTIVE as HOST  # noqa: E402
from engine.props import draw_prop  # noqa: E402
from cast import ARRICHION_WREATH, ATTILA, HARALD, CRASSUS, YI  # noqa: E402

TW, TH = 1920, 1080
OUT = os.path.join(HERE, 'thumbnails')


# ---------------------------------------------------------------- building blocks
def radial(c, center, radius, colors, stops):
    sh = skia.GradientShader.MakeRadial(center, radius, [rgb(x) for x in colors], stops)
    c.drawRect(skia.Rect(0, 0, TW, TH), skia.Paint(Shader=sh))


def rays(c, center, n=16, alpha=24, rot=0.0, color='#FFFFFF', length=2600):
    cx, cy = center
    p = skia.Path()
    for k in range(n):
        a0 = math.radians(rot + k * 360 / n)
        a1 = math.radians(rot + (k + 0.5) * 360 / n)
        p.moveTo(cx, cy)
        p.lineTo(cx + length * math.cos(a0), cy + length * math.sin(a0))
        p.lineTo(cx + length * math.cos(a1), cy + length * math.sin(a1))
        p.close()
    c.drawPath(p, paint(color, alpha=alpha))


def vignette(c, strength=200, inner=0.45):
    sh = skia.GradientShader.MakeRadial((TW / 2, TH / 2), TW * 0.62, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, strength)],
                                        [inner, 1.0])
    c.drawRect(skia.Rect(0, 0, TW, TH), skia.Paint(Shader=sh))


def glow(c, x, y, r, color='#FFF1A8', alpha=220):
    col = rgb(color)
    sh = skia.GradientShader.MakeRadial((x, y), r, [skia.ColorSetA(col, alpha), skia.ColorSetA(col, 0)], [0.0, 1.0])
    c.drawCircle(x, y, r, skia.Paint(Shader=sh))


def _text_path(s, size, tracking):
    f = font(size)
    xs, _ = glyph_layout(s, size, tracking)
    p = skia.Path()
    for ch, x in zip(s, xs):
        g = f.getPath(f.textToGlyphs(ch)[0]) if ch != ' ' else None
        if g is not None:
            g.offset(x, 0)
            p.addPath(g)
    return p


def text_width(s, size, tracking):
    return glyph_layout(s, size, tracking)[1]


def big_text(c, runs, x, y, cap, stroke=0.15, tracking=0.02, align='left', rot=0.0, shadow=True, inner=None):
    """runs: [(text, fill)] drawn on one baseline. Thick black outline, optional thin inner stroke, drop shadow."""
    size = size_for_cap(cap)
    full = ''.join(t for t, _ in runs)
    wfull = text_width(full, size, tracking)
    x0 = x - wfull / 2 if align == 'center' else x - wfull if align == 'right' else x
    c.save()
    c.translate(x0, y)
    if rot:
        c.rotate(rot, wfull / 2, -cap / 2)
    paths = []
    off = 0.0
    for t, fill in runs:
        p = _text_path(t, size, tracking)
        p.offset(off, 0)
        paths.append((p, fill))
        off += text_width(t + ' ', size, tracking) - text_width(' ', size, tracking) + text_width(' ', size, tracking) * (1 if t.endswith(' ') else 0)
        off = text_width(full[:sum(len(tt) for tt, _ in runs[:len(paths)])], size, tracking)
    sw = cap * stroke
    if shadow:
        sp = paint('#000000', alpha=190)
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, cap * 0.08))
        for p, _ in paths:
            q = skia.Path(p)
            q.offset(cap * 0.06, cap * 0.09)
            c.drawPath(q, sp)
            st = paint('#000000', stroke=sw * 2, alpha=190, join='round')
            st.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, cap * 0.08))
            c.drawPath(q, st)
    for p, _ in paths:
        c.drawPath(p, paint('#000000', stroke=sw * 2, join='round'))
    if inner:
        for p, _ in paths:
            c.drawPath(p, paint(inner, stroke=sw * 0.75, join='round'))
    for p, fill in paths:
        if isinstance(fill, tuple):                       # vertical gradient fill
            b = p.getBounds()
            sh = skia.GradientShader.MakeLinear([(0, b.top()), (0, b.bottom())], [rgb(fill[0]), rgb(fill[1])])
            c.drawPath(p, skia.Paint(Shader=sh, AntiAlias=True))
        else:
            c.drawPath(p, paint(fill))
    c.restore()
    return wfull


def fit_cap(s, width, tracking=0.02, cap=220):
    while cap > 40 and text_width(s, size_for_cap(cap), tracking) > width:
        cap -= 2
    return cap


def star(c, x, y, r, color='#FFF6C8', alpha=255):
    p = skia.Path()
    for k in range(8):
        a = math.radians(k * 45 - 90)
        rr = r if k % 2 == 0 else r * 0.28
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close()
    c.drawPath(p, paint(color, alpha=alpha))


def medal(c, x, y, r, ribbon_top):
    rb = skia.Path()
    rb.moveTo(x - r * 0.9, ribbon_top)
    rb.lineTo(x - r * 0.25, y - r * 0.6)
    rb.lineTo(x + r * 0.25, y - r * 0.6)
    rb.lineTo(x + r * 0.9, ribbon_top)
    rb.lineTo(x + r * 0.45, ribbon_top)
    rb.lineTo(x, y - r * 1.05)
    rb.lineTo(x - r * 0.45, ribbon_top)
    rb.close()
    c.drawPath(rb, paint('#C8102E'))
    c.drawPath(rb, paint('#151515', stroke=r * 0.09, join='round'))
    glow(c, x, y, r * 2.2, '#FFE680', 150)
    sh = skia.GradientShader.MakeLinear([(x - r, y - r), (x + r, y + r)], [rgb('#FFF3A0'), rgb('#F2B705'), rgb('#B37800')], [0, 0.5, 1])
    c.drawCircle(x, y, r, skia.Paint(Shader=sh, AntiAlias=True))
    c.drawCircle(x, y, r, paint('#151515', stroke=r * 0.1))
    c.drawCircle(x, y, r * 0.72, paint('#9A6A00', stroke=r * 0.05))
    size = size_for_cap(r * 0.9)
    w = text_width('1', size, 0)
    c.drawPath(_shift(_text_path('1', size, 0), x - w / 2 - r * 0.03, y + r * 0.45), paint('#7A4E00'))


def _shift(p, dx, dy):
    q = skia.Path(p)
    q.offset(dx, dy)
    return q


def nosebleed(c, cx, cy, R):
    """Two thick blood streams from the middle of the face over the mustache + drops."""
    red, dark = '#D3101C', '#5A0006'
    for side in (-1, 1):
        p = skia.Path()
        x0 = cx + side * 0.055 * R
        y0 = cy + 0.10 * R
        p.moveTo(x0 - 0.035 * R, y0)
        p.cubicTo(x0 - 0.05 * R, y0 + 0.2 * R, x0 + side * 0.02 * R - 0.06 * R, y0 + 0.42 * R, x0 + side * 0.05 * R - 0.05 * R, y0 + 0.62 * R)
        p.arcTo(skia.Rect(x0 + side * 0.05 * R - 0.075 * R, y0 + 0.58 * R, x0 + side * 0.05 * R + 0.075 * R, y0 + 0.73 * R), 180, -180, False)
        p.cubicTo(x0 + side * 0.03 * R + 0.06 * R, y0 + 0.42 * R, x0 + 0.05 * R, y0 + 0.2 * R, x0 + 0.035 * R, y0)
        p.close()
        c.drawPath(p, paint(red))
        c.drawPath(p, paint(dark, stroke=0.018 * R, join='round'))
        c.drawCircle(x0 - 0.008 * R, y0 + 0.2 * R, 0.012 * R, paint('#FF8A8A'))
    for k, (dx, dy, rr) in enumerate([(-0.02, 0.95, 0.045), (0.09, 1.12, 0.035), (-0.06, 1.3, 0.028)]):
        x, y, r = cx + dx * R, cy + dy * R, rr * R
        d = skia.Path()
        d.moveTo(x, y - r * 2.1)
        d.cubicTo(x + r * 0.9, y - r * 0.7, x + r, y + r, x, y + r)
        d.cubicTo(x - r, y + r, x - r * 0.9, y - r * 0.7, x, y - r * 2.1)
        c.drawPath(d, paint(red))
        c.drawPath(d, paint(dark, stroke=0.012 * R))


def sweat(c, x, y, r):
    d = skia.Path()
    d.moveTo(x, y - r * 2.0)
    d.cubicTo(x + r * 0.9, y - r * 0.6, x + r, y + r, x, y + r)
    d.cubicTo(x - r, y + r, x - r * 0.9, y - r * 0.6, x, y - r * 2.0)
    c.drawPath(d, paint('#8FD8FF'))
    c.drawPath(d, paint('#151515', stroke=r * 0.18))
    c.drawCircle(x - r * 0.3, y - r * 0.1, r * 0.22, paint('#FFFFFF'))


def ring(c, x, y, rx, ry, color='#FF2A2A', w=14):
    p = skia.Path()
    p.addOval(skia.Rect(x - rx, y - ry, x + rx, y + ry))
    c.drawPath(p, paint('#000000', stroke=w + 10, alpha=200))
    c.drawPath(p, paint(color, stroke=w))


def arrow(c, p0, p1, bend=0.25, w=34, color='#FF2A2A'):
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    cx, cy = mx + nx * bend, my + ny * bend
    dx, dy = x1 - cx, y1 - cy
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    hl, hw = w * 2.3, w * 1.7
    bx, by = x1 - ux * hl, y1 - uy * hl
    shaft = skia.Path()
    shaft.moveTo(x0, y0)
    shaft.quadTo(cx, cy, bx, by)
    head = skia.Path()
    head.moveTo(x1, y1)
    head.lineTo(bx - uy * hw, by + ux * hw)
    head.lineTo(bx + uy * hw, by - ux * hw)
    head.close()
    for col, extra in (('#000000', 16), (color, 0)):
        c.drawPath(shaft, paint(col, stroke=w + extra, cap='round'))
        hp = paint(col)
        if extra:
            hp.setStyle(skia.Paint.kStrokeAndFill_Style)
            hp.setStrokeWidth(extra)
            hp.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawPath(head, hp)


# ---------------------------------------------------------------- thumbnails
def thumb_A(c):
    """WON WHILE DEAD"""
    radial(c, (1290, 560), 1250, ['#FFE27A', '#F59A1B', '#C3151B', '#3A0507'], [0.0, 0.2, 0.55, 1.0])
    rays(c, (1290, 560), 18, 30, rot=4)
    vignette(c, 170, 0.5)
    hx, hy, R = 1320, 560, 232
    glow(c, hx, hy - 40, R * 2.0, '#FFF4B8', 230)
    for (dx, dy, r) in [(-1.45, -0.55, 36), (1.42, -0.85, 44), (1.62, 0.25, 28), (0.15, -1.42, 30)]:
        star(c, hx + dx * R, hy + dy * R, r)
    draw_character(c, hx, hy, R, 'wave', 'ko_grin', ARRICHION_WREATH, look=(0.0, 0.0))
    medal(c, hx + 0.02 * R, hy + 1.72 * R, 0.36 * R, hy + 1.05 * R)
    draw_character(c, 410, 660, 145, 'point', 'shock', HOST, look=(0.25, -0.05))
    sweat(c, 410 + 0.55 * 145, 660 - 0.55 * 145, 24)
    s = 'WON WHILE DEAD'
    cap = fit_cap(s, 1800, 0.02, 190)
    big_text(c, [('WON WHILE ', '#FFFFFF'), ('DEAD', ('#FFF27A', '#FFB300'))], TW / 2, 40 + cap, cap, align='center', tracking=0.02)


def thumb_B(c):
    """KILLED BY A NOSEBLEED"""
    radial(c, (1180, 640), 1300, ['#9BE2FF', '#2E86E0', '#0C2A60', '#040A18'], [0.0, 0.25, 0.6, 1.0])
    rays(c, (1180, 640), 16, 26, rot=-3)
    vignette(c, 160, 0.5)
    hx, hy, R = 1200, 650, 245
    c.save()
    c.translate(hx + 1.25 * R, hy + 0.9 * R)
    c.rotate(-38)
    draw_prop(c, 'sword', 0, 0, 340, glow=True)
    c.restore()
    draw_character(c, hx, hy, R, 'shrug', 'shock', ATTILA, look=(0.0, 0.03))
    nosebleed(c, hx, hy, R)
    sweat(c, hx + 0.62 * R, hy - 0.45 * R, 30)
    draw_character(c, 300, 770, 125, 'point', 'grimace', HOST, look=(0.3, 0.0))
    l1, l2 = 'KILLED BY A', 'NOSEBLEED'
    cap2 = fit_cap(l2, 1700, 0.02, 200)
    cap1 = min(105, fit_cap(l1, 1200, 0.03, 120))
    big_text(c, [(l1, '#FFFFFF')], TW / 2, 30 + cap1, cap1, align='center', tracking=0.03)
    big_text(c, [(l2, ('#FF5A4E', '#D60F1A'))], TW / 2, 30 + cap1 + 34 + cap2, cap2, align='center', tracking=0.02, inner='#FFFFFF')


def thumb_C(c):
    """5 EPIC DEATHS"""
    radial(c, (960, 820), 1200, ['#7A1116', '#2A0406', '#000000'], [0.0, 0.5, 1.0])
    xs = [215, 588, 960, 1332, 1705]
    for x in xs:
        beam = skia.Path()
        beam.moveTo(x - 60, 0)
        beam.lineTo(x + 60, 0)
        beam.lineTo(x + 230, TH)
        beam.lineTo(x - 230, TH)
        beam.close()
        sh = skia.GradientShader.MakeLinear([(0, 0), (0, TH)], [skia.Color(255, 245, 220, 70), skia.Color(255, 245, 220, 8)])
        c.drawPath(beam, skia.Paint(Shader=sh, AntiAlias=True))
    cast = [(HARALD, 'ko'), (ATTILA, 'ko_o'), (CRASSUS, 'ko'), (ARRICHION_WREATH, 'ko_grin'), (YI, 'ko')]
    y, R = 735, 150
    for x, (pal, ex) in zip(xs, cast):
        glow(c, x, y, R * 1.7, '#FFE9C0', 70)
        draw_character(c, x, y, R, 'idle', ex, pal)
    # signature props: arrow (Harald), nosebleed (Attila), molten gold (Crassus), medal (Arrichion), drum (Yi)
    arrow_prop = xs[0]
    c.save()
    c.translate(arrow_prop + 0.5 * R, y + 0.95 * R)
    c.rotate(-28)
    draw_prop(c, 'arrow', 0, 0, 170)
    c.restore()
    nosebleed(c, xs[1], y, R)
    gold = skia.Path()
    gx, gy = xs[2], y + 0.38 * R
    gold.addRRect(skia.RRect.MakeRectXY(skia.Rect(gx - 0.18 * R, gy - 0.04 * R, gx + 0.18 * R, gy + 0.55 * R), 0.12 * R, 0.12 * R))
    sh = skia.GradientShader.MakeLinear([(0, gy), (0, gy + 0.55 * R)], [rgb('#FFF08A'), rgb('#E0A100')])
    c.drawPath(gold, skia.Paint(Shader=sh, AntiAlias=True))
    c.drawPath(gold, paint('#5A3A00', stroke=0.03 * R))
    medal(c, xs[3], y + 1.6 * R, 0.3 * R, y + 1.02 * R)
    draw_prop(c, 'drum', xs[4] + 1.0 * R, y + 1.45 * R, 120)
    for k, x in enumerate(xs):
        s = f'#{k + 1}'
        big_text(c, [(s, '#FFFFFF')], x, y - 1.55 * R, 52, align='center', stroke=0.2, shadow=False)
    vignette(c, 150, 0.55)
    s1, s2 = '5 EPIC', 'DEATHS'
    cap1 = 120
    cap2 = fit_cap(s2, 1250, 0.03, 200)
    big_text(c, [(s1, '#FFFFFF')], TW / 2, 40 + cap1, cap1, align='center', tracking=0.04)
    big_text(c, [(s2, ('#FF4A3D', '#C90F18'))], TW / 2, 40 + cap1 + 30 + cap2, cap2, align='center', tracking=0.03, rot=-3, inner='#FFFFFF')


def render(fn, name):
    surf = skia.Surface(TW, TH)
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    fn(c)
    img = surf.makeImageSnapshot().toarray()[:, :, :3]
    os.makedirs(OUT, exist_ok=True)
    cv2.imwrite(os.path.join(OUT, f'thumb_{name}_master.png'), img)
    small = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_AREA)
    path = os.path.join(OUT, f'thumb_{name}.jpg')
    cv2.imwrite(path, small, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return img, path


def preview(imgs):
    """How the thumbnails read on YouTube: home feed (~360 px), search (~246 px), suggested (~168 px)."""
    rows = []
    for img in imgs:
        row = []
        for w in (640, 360, 246, 168):
            h = int(w * 9 / 16)
            t = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
            pad = np.full((380, w + 20, 3), 255, np.uint8)
            pad[10:10 + h, 10:10 + w] = t
            row.append(pad)
        rows.append(np.hstack(row))
    sheet = np.vstack(rows)
    cv2.imwrite(os.path.join(OUT, 'preview_sizes.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == '__main__':
    imgs = []
    for fn, name in ((thumb_A, 'A'), (thumb_B, 'B'), (thumb_C, 'C')):
        img, path = render(fn, name)
        imgs.append(img)
        print(path, os.path.getsize(path) // 1024, 'KB')
    preview(imgs)
