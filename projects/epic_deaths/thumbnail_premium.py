"""Premium thumbnails: layered compositing with lighting, depth of field and grading.

Each layer is drawn with skia onto a transparent surface, then composited in numpy (premultiplied BGRA float):
  background plate (real painting, defocused + graded + light)  ->  side characters (shadow, rim light, shading)
  ->  title  ->  hero host (contact shadow, glow, rim light, shading, detailed face + hands)  ->  ghost title
  ->  foreground bokeh  ->  grade (curve, saturation, bloom, vignette, grain, sharpen)

  python3 thumbnail_premium.py
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
from engine.roundhead import draw_character, DETECTIVE as HOST  # noqa: E402
from engine.props import draw_prop  # noqa: E402
from cast import HARALD, ARRICHION_WREATH, ATTILA, CRASSUS, NEPHEW  # noqa: E402
from thumbnail import medal, nosebleed  # noqa: E402
from thumbnail_tmb import title_layout, _stroke, sweat  # noqa: E402

TW, TH = 1920, 1080
OUT = os.path.join(HERE, 'thumbnails')
IMG = os.path.join(HERE, 'assets', 'picked')
INK = '#121212'


# ================================================================ layer plumbing (premultiplied BGRA float32)
def surface():
    s = skia.Surface(TW, TH)
    s.getCanvas().clear(skia.ColorTRANSPARENT)
    return s


def arr(s):
    """skia's toarray() is un-premultiplied BGRA; convert to premultiplied float for correct compositing."""
    x = s.makeImageSnapshot().toarray().astype(np.float32) / 255.0
    x[..., :3] *= x[..., 3:4]
    return x


def over(dst, src):
    return src + dst * (1.0 - src[..., 3:4])


def blur(x, sigma):
    return cv2.GaussianBlur(x, (0, 0), sigma) if sigma > 0 else x


def shift(a, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(a, M, (TW, TH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def solid(alpha, bgr, opacity=1.0):
    a = np.clip(alpha * opacity, 0, 1)
    out = np.empty((TH, TW, 4), np.float32)
    for k in range(3):
        out[..., k] = a * bgr[k]
    out[..., 3] = a
    return out


def hexbgr(h):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return np.array([b, g, r], np.float32) / 255.0


def character_fx(layer, light=(1.0, -0.55), rim='#FFE2A8', rim_w=7, rim_amt=0.85, shadow=(26, 30, 26, 0.6), glow=None,
                 shade=0.28, shade_top=0.55):
    """Contact/drop shadow, optional outer glow, vertical volume shading and a rim light on the edge facing the light."""
    a = layer[..., 3]
    res = np.zeros_like(layer)
    dx, dy, sb, so = shadow
    res = over(res, solid(blur(shift(a, dx, dy), sb), (0, 0, 0), so))
    if glow is not None:
        col, size, op = glow
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size * 2 + 1, size * 2 + 1))
        res = over(res, solid(blur(cv2.dilate(a, k), size * 1.2), hexbgr(col), op))
    ch = layer.copy()
    ys = np.linspace(0, 1, TH, dtype=np.float32)[:, None]
    rows = np.where(a.any(1))[0]
    if len(rows):
        y0, y1 = rows[0] / TH, rows[-1] / TH
        u = np.clip((ys - (y0 + (y1 - y0) * shade_top)) / max(1e-3, (y1 - y0) * (1 - shade_top)), 0, 1)
        ch[..., :3] *= (1 - shade * u)[..., None]
    lx, ly = light
    n = math.hypot(lx, ly)
    lx, ly = lx / n, ly / n
    edge = a * (1 - shift(a, -lx * rim_w, -ly * rim_w))
    edge = blur(edge, rim_w * 0.35) * a * rim_amt
    rc = hexbgr(rim)
    for k in range(3):
        ch[..., k] = ch[..., k] + edge * (rc[k] * a - ch[..., k]) * 0.75
    return over(res, ch)


# ================================================================ backgrounds
def plate(key, sigma=7.0, focus=(0.5, 0.5), zoom=1.0):
    img = cv2.imread(os.path.join(IMG, key + '.jpg')).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    k = max(TW / w, TH / h) * zoom
    img = cv2.resize(img, (int(w * k + 1), int(h * k + 1)), interpolation=cv2.INTER_CUBIC)
    h, w = img.shape[:2]
    x0 = int(np.clip(focus[0] * w - TW / 2, 0, w - TW))
    y0 = int(np.clip(focus[1] * h - TH / 2, 0, h - TH))
    img = blur(img[y0:y0 + TH, x0:x0 + TW], sigma)
    out = np.ones((TH, TW, 4), np.float32)
    out[..., :3] = img
    return out


def grade(img, lift=(0, 0, 0), gain=(1, 1, 1), gamma=1.0, sat=1.0, contrast=1.0):
    x = img[..., :3]
    x = np.clip(x * np.array(gain, np.float32) + np.array(lift, np.float32), 0, 1) ** (1 / gamma)
    m = x.mean(2, keepdims=True)
    x = np.clip(m + (x - m) * sat, 0, 1)
    x = np.clip(0.5 + (x - 0.5) * contrast, 0, 1)
    out = img.copy()
    out[..., :3] = x * img[..., 3:4]
    return out


def light_pool(img, cx, cy, r, col, amt):
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    g = np.clip(1 - d, 0, 1) ** 2 * amt
    c = hexbgr(col)
    out = img.copy()
    for k in range(3):
        out[..., k] = 1 - (1 - out[..., k]) * (1 - g * c[k])          # screen
    return out


def bg_vignette(img, amount=0.5):
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    d = np.sqrt(((xx - TW / 2) / (TW / 2)) ** 2 + ((yy - TH * 0.55) / (TH * 0.62)) ** 2)
    out = img.copy()
    out[..., :3] *= (1 - amount * np.clip(d - 0.45, 0, 1) ** 1.4)[..., None]
    return out


def top_shade(img, depth=0.42, amount=0.45):
    ys = np.linspace(0, 1, TH, dtype=np.float32)[:, None]
    f = 1 - amount * np.clip(1 - ys / depth, 0, 1) ** 1.4
    out = img.copy()
    out[..., :3] *= f[..., None]
    return out


def god_rays(cx, cy, n=22, length=2400, alpha=0.09, col='#FFE9C2', seed=3):
    s = surface()
    c = s.getCanvas()
    rng = np.random.default_rng(seed)
    for k in range(n):
        a0 = math.radians(k * 360 / n + rng.uniform(-4, 4))
        w = math.radians(rng.uniform(2.5, 6))
        p = skia.Path()
        p.moveTo(cx, cy)
        p.lineTo(cx + length * math.cos(a0 - w), cy + length * math.sin(a0 - w))
        p.lineTo(cx + length * math.cos(a0 + w), cy + length * math.sin(a0 + w))
        p.close()
        c.drawPath(p, paint(col, alpha=int(255 * alpha * rng.uniform(0.5, 1.2))))
    x = arr(s)
    x[..., :4] = blur(x, 6)
    return x


# ================================================================ detailed drawing (faces, hands, props)
def mouth_open(c, mx, my, rx, ry, R, teeth=True, tongue=True):
    m = skia.Path()
    m.addOval(skia.Rect(mx - rx, my - ry, mx + rx, my + ry))
    sh = skia.GradientShader.MakeRadial((mx, my - ry * 0.1), max(rx, ry), [rgb('#0D0403'), rgb('#2A100B'), rgb('#4A1D14')], [0.0, 0.6, 1.0])
    c.drawPath(m, skia.Paint(Shader=sh, AntiAlias=True))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    if teeth:
        tp = skia.Path()
        tp.addRRect(skia.RRect.MakeRectXY(skia.Rect(mx - rx * 0.78, my - ry * 1.05, mx + rx * 0.78, my - ry * 0.72), rx * 0.12, rx * 0.12))
        c.drawPath(tp, paint('#F4F1EA'))
        for k in range(-2, 3):
            c.drawLine(mx + k * rx * 0.26, my - ry * 1.0, mx + k * rx * 0.26, my - ry * 0.74, paint('#B9B4AA', stroke=0.008 * R))
    if tongue:
        tg = skia.Path()
        tg.addOval(skia.Rect(mx - rx * 0.72, my + ry * 0.28, mx + rx * 0.72, my + ry * 1.3))
        tsh = skia.GradientShader.MakeLinear([(0, my + ry * 0.3), (0, my + ry * 1.0)], [rgb('#FF9DB4'), rgb('#D9667F')])
        c.drawPath(tg, skia.Paint(Shader=tsh, AntiAlias=True))
        c.drawLine(mx, my + ry * 0.45, mx, my + ry * 0.85, paint('#B24F66', stroke=0.012 * R, cap='round'))
        c.drawOval(skia.Rect(mx - rx * 0.32, my + ry * 0.4, mx - rx * 0.08, my + ry * 0.55), paint('#FFFFFF', alpha=110))
    c.restore()
    c.drawPath(m, _stroke(0.032 * R))


def brow(c, x0, y0, x1, y1, bend, w):
    p = skia.Path()
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - bend
    p.moveTo(x0, y0)
    p.quadTo(mx, my, x1, y1)
    c.drawPath(p, paint(INK, stroke=w, cap='round'))


def eye(c, ex, ey, R, rx=0.085, ry=0.105, lid=None, side=1, shine=True, pupil=None):
    if pupil:                                  # white eye with a tiny pupil (terror)
        c.drawOval(skia.Rect(ex - rx * R, ey - ry * R, ex + rx * R, ey + ry * R), paint('#FFFFFF'))
        c.drawOval(skia.Rect(ex - rx * R, ey - ry * R, ex + rx * R, ey + ry * R), _stroke(0.022 * R))
        c.drawCircle(ex + pupil[0] * R, ey + pupil[1] * R, pupil[2] * R, paint(INK))
        return
    c.drawOval(skia.Rect(ex - rx * R, ey - ry * R, ex + rx * R, ey + ry * R), paint(INK))
    if shine:
        c.drawCircle(ex + 0.03 * R, ey - 0.04 * R, 0.026 * R, paint('#FFFFFF'))
        c.drawCircle(ex - 0.025 * R, ey + 0.035 * R, 0.011 * R, paint('#FFFFFF', alpha=200))
    if lid is not None:
        ly = ey - ry * R + lid * 2 * ry * R
        a = (ex - (rx + 0.05) * R, ly - side * 0.05 * R)
        b = (ex + (rx + 0.05) * R, ly + side * 0.05 * R)
        lp = skia.Path()
        lp.moveTo(*a)
        lp.lineTo(*b)
        lp.lineTo(b[0], ey - (ry + 0.09) * R)
        lp.lineTo(a[0], ey - (ry + 0.09) * R)
        lp.close()
        c.drawPath(lp, paint('#F5F5F0'))
        c.drawLine(a[0], a[1], b[0], b[1], _stroke(0.028 * R))
        bag = skia.Path()
        bag.moveTo(ex - rx * R * 0.9, ey + ry * R + 0.035 * R)
        bag.quadTo(ex, ey + ry * R + 0.09 * R, ex + rx * R * 0.9, ey + ry * R + 0.035 * R)
        c.drawPath(bag, _stroke(0.015 * R))


def x_eye(c, ex, ey, R, s=0.09):
    for d in (1, -1):
        c.drawLine(ex - s * R, ey - d * s * R, ex + s * R, ey + d * s * R, paint(INK, stroke=0.045 * R, cap='round'))


def face_shading(c, cx, cy, R, hands=None, top=-0.45):
    c.save()
    clip = skia.Path()
    clip.addCircle(cx, cy, R * 0.965)
    if hands:
        hp = skia.Path()
        for hx, hy, hr in hands:
            hp.addCircle(hx, hy, hr)
        clip = skia.Op(clip, hp, skia.PathOp.kDifference_PathOp)
    c.clipPath(clip, doAntiAlias=True)
    c.clipRect(skia.Rect(cx - R, cy + top * R, cx + R, cy + R))
    sh = skia.GradientShader.MakeRadial((cx - 0.22 * R, cy - 0.28 * R), 1.3 * R,
                                        [skia.Color(255, 255, 255, 0), skia.Color(255, 255, 255, 0), skia.Color(140, 146, 160, 120),
                                         skia.Color(80, 86, 100, 185)], [0.0, 0.5, 0.82, 1.0])
    c.drawRect(skia.Rect(cx - R, cy - R, cx + R, cy + R), skia.Paint(Shader=sh))
    for side in (-1, 1):                                                       # cheek warmth
        bl = skia.GradientShader.MakeRadial((cx + side * 0.48 * R, cy + 0.2 * R), 0.22 * R, [skia.Color(255, 120, 120, 60), skia.Color(255, 120, 120, 0)])
        c.drawCircle(cx + side * 0.48 * R, cy + 0.2 * R, 0.22 * R, skia.Paint(Shader=bl))
    c.restore()


def grime(c, cx, cy, R, seed=1, n=10):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = cx + rng.uniform(-0.6, 0.6) * R, cy + rng.uniform(-0.3, 0.7) * R
        if math.hypot(x - cx, y - cy) > 0.85 * R:
            continue
        c.drawCircle(x, y, rng.uniform(0.006, 0.018) * R, paint('#7A7F8A', alpha=int(rng.uniform(60, 140))))
    for k in range(3):
        x, y = cx + rng.uniform(0.35, 0.62) * R, cy + rng.uniform(-0.15, 0.25) * R
        for j in range(3):
            c.drawLine(x + j * 0.025 * R, y, x + j * 0.025 * R + 0.05 * R, y + 0.09 * R, paint('#C94040', stroke=0.008 * R, alpha=150, cap='round'))


def hand(c, x, y, s, angle, mirror=False):
    """White cartoon glove hand, fingers pointing 'up' in local space."""
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    if mirror:
        c.scale(-1, 1)
    shape = skia.Path()
    shape.addOval(skia.Rect(-0.46 * s, -0.25 * s, 0.46 * s, 0.6 * s))
    fingers = [(-0.31, -0.55, 0.13, -10), (-0.1, -0.68, 0.13, -3), (0.12, -0.66, 0.13, 4), (0.32, -0.52, 0.12, 11)]
    for fx, fy, fw, fa in fingers:
        f = skia.Path()
        f.addRRect(skia.RRect.MakeRectXY(skia.Rect(fx * s - fw * s, fy * s, fx * s + fw * s, 0.15 * s), fw * s, fw * s))
        m = skia.Matrix()
        m.setRotate(fa, fx * s, 0.1 * s)
        f.transform(m)
        shape = skia.Op(shape, f, skia.PathOp.kUnion_PathOp)
    th = skia.Path()
    th.addRRect(skia.RRect.MakeRectXY(skia.Rect(0.3 * s, 0.05 * s, 0.85 * s, 0.32 * s), 0.13 * s, 0.13 * s))
    m = skia.Matrix()
    m.setRotate(28, 0.3 * s, 0.18 * s)
    th.transform(m)
    shape = skia.Op(shape, th, skia.PathOp.kUnion_PathOp)
    sh = skia.GradientShader.MakeLinear([(0, -0.6 * s), (0, 0.6 * s)], [rgb('#FFFFFF'), rgb('#D8DBE2')])
    c.drawPath(shape, skia.Paint(Shader=sh, AntiAlias=True))
    c.drawPath(shape, paint(INK, stroke=0.075 * s, join='round'))
    for fx in (-0.2, 0.01, 0.22):
        c.drawLine(fx * s, -0.12 * s, fx * s, 0.12 * s, paint(INK, stroke=0.045 * s, cap='round'))
    c.restore()


# ---------------------------------------------------------------- hero host
def hero(face='scream', cx=960, cy=640, R=345):
    s = surface()
    c = s.getCanvas()
    draw_character(c, cx, cy, R, 'cheeks', 'blank', HOST, show_rim=False)
    hands = [(cx - 0.92 * R, cy + 0.40 * R, 0.34 * R), (cx + 0.92 * R, cy + 0.40 * R, 0.34 * R)]
    face_shading(c, cx, cy, R, hands)
    if face == 'scream':
        for side in (-1, 1):
            eye(c, cx + side * 0.25 * R, cy - 0.10 * R, R, lid=0.42, side=side)
            brow(c, cx + side * 0.13 * R, cy - 0.30 * R, cx + side * 0.36 * R, cy - 0.36 * R, 0.03 * R * side * 0 + 0.02 * R, 0.03 * R)
        mouth_open(c, cx, cy + 0.36 * R, 0.21 * R, 0.29 * R, R, teeth=True)
        grime(c, cx, cy, R, 2, 14)
    elif face == 'terror':
        for side in (-1, 1):
            eye(c, cx + side * 0.25 * R, cy - 0.09 * R, R, rx=0.12, ry=0.15, pupil=(side * -0.0 + 0.0, 0.0, 0.03))
            brow(c, cx + side * 0.12 * R, cy - 0.30 * R, cx + side * 0.38 * R, cy - 0.40 * R, 0.05 * R, 0.032 * R)
        mouth_open(c, cx, cy + 0.38 * R, 0.24 * R, 0.24 * R, R, teeth=True)
        grime(c, cx, cy, R, 5, 16)
    else:                                                                  # shock
        for side in (-1, 1):
            eye(c, cx + side * 0.24 * R, cy - 0.07 * R, R, rx=0.11, ry=0.135)
            brow(c, cx + side * 0.12 * R, cy - 0.30 * R, cx + side * 0.36 * R, cy - 0.32 * R, 0.07 * R, 0.03 * R)
        mouth_open(c, cx + 0.02 * R, cy + 0.36 * R, 0.12 * R, 0.15 * R, R, teeth=False)
    for side in (-1, 1):                                                   # cheek folds
        p = skia.Path()
        p.moveTo(cx + side * 0.27 * R, cy + 0.14 * R)
        p.cubicTo(cx + side * 0.35 * R, cy + 0.26 * R, cx + side * 0.35 * R, cy + 0.46 * R, cx + side * 0.27 * R, cy + 0.58 * R)
        c.drawPath(p, _stroke(0.018 * R))
    hand(c, cx - 0.86 * R, cy + 0.36 * R, 0.33 * R, 18, mirror=False)
    hand(c, cx + 0.86 * R, cy + 0.36 * R, 0.33 * R, -18, mirror=True)
    sweat(c, cx - 0.64 * R, cy - 0.28 * R, 0.07 * R, -20)
    sweat(c, cx + 0.68 * R, cy - 0.10 * R, 0.058 * R, 25)
    sweat(c, cx + 0.47 * R, cy - 0.40 * R, 0.045 * R, 15)
    return arr(s)


# ---------------------------------------------------------------- side characters (detailed faces + death details)
def side_harald(x=360, y=600, R=165):
    s = surface()
    c = s.getCanvas()
    c.save()
    c.rotate(-11, x, y + 3 * R)
    draw_character(c, x, y, R, 'cheeks', 'blank', HARALD, show_rim=False)
    face_shading(c, x, y, R, [(x - 0.92 * R, y + 0.4 * R, 0.3 * R), (x + 0.92 * R, y + 0.4 * R, 0.3 * R)], top=-0.2)
    for side in (-1, 1):
        ex, ey = x + side * 0.25 * R, y - 0.05 * R
        p = skia.Path()                                                # squeezed > < eyes
        p.moveTo(ex - side * 0.1 * R, ey - 0.08 * R)
        p.lineTo(ex + side * 0.06 * R, ey)
        p.lineTo(ex - side * 0.1 * R, ey + 0.08 * R)
        c.drawPath(p, paint(INK, stroke=0.045 * R, cap='round', join='round'))
    mouth_open(c, x, y + 0.42 * R, 0.17 * R, 0.17 * R, R, teeth=True)
    hand(c, x - 0.86 * R, y + 0.36 * R, 0.33 * R, 18)
    hand(c, x + 0.86 * R, y + 0.36 * R, 0.33 * R, -18, mirror=True)
    c.restore()
    # the arrow: through the neck (front half drawn over, back half sticking out)
    c.save()
    c.translate(x + 0.15 * R, y + 1.12 * R)
    c.rotate(-24)
    L = 2.4 * R
    c.drawLine(-L * 0.55, 0, L * 0.45, 0, paint(INK, stroke=0.11 * R, cap='round'))
    c.drawLine(-L * 0.55, 0, L * 0.45, 0, paint('#9A6A3A', stroke=0.055 * R, cap='round'))
    head = skia.Path()
    head.moveTo(L * 0.45 + 0.22 * R, 0)
    head.lineTo(L * 0.45 - 0.02 * R, -0.1 * R)
    head.lineTo(L * 0.45 - 0.02 * R, 0.1 * R)
    head.close()
    c.drawPath(head, paint('#D5DAE2'))
    c.drawPath(head, paint(INK, stroke=0.03 * R, join='round'))
    for sg in (-1, 1):
        f = skia.Path()
        f.moveTo(-L * 0.55 + 0.25 * R, 0)
        f.lineTo(-L * 0.55 - 0.05 * R, sg * 0.15 * R)
        f.lineTo(-L * 0.55 + 0.08 * R, 0)
        f.close()
        c.drawPath(f, paint('#F4F4F4'))
        c.drawPath(f, paint(INK, stroke=0.025 * R, join='round'))
    for k, (bx, by) in enumerate(((0.05, 0.2), (0.12, 0.42), (0.02, 0.62))):
        c.drawCircle(bx * R, by * R, (0.05 - 0.01 * k) * R, paint('#C8101C'))
    c.restore()
    return arr(s)


def side_arrichion(x=1560, y=585, R=160):
    s = surface()
    c = s.getCanvas()
    draw_character(c, x, y, R, 'wave', 'blank', ARRICHION_WREATH, show_rim=False)
    face_shading(c, x, y, R, top=-0.2)
    for side in (-1, 1):
        x_eye(c, x + side * 0.24 * R, y - 0.04 * R, R)
    m = skia.Path()                                                    # big happy grin with teeth
    m.moveTo(x - 0.25 * R, y + 0.22 * R)
    m.quadTo(x, y + 0.62 * R, x + 0.25 * R, y + 0.22 * R)
    m.close()
    c.drawPath(m, paint('#2A100B'))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    c.drawRect(skia.Rect(x - 0.3 * R, y + 0.2 * R, x + 0.3 * R, y + 0.3 * R), paint('#F4F1EA'))
    c.drawOval(skia.Rect(x - 0.13 * R, y + 0.36 * R, x + 0.13 * R, y + 0.6 * R), paint('#F39BB1'))
    c.restore()
    c.drawPath(m, _stroke(0.032 * R))
    medal(c, x + 0.02 * R, y + 1.72 * R, 0.36 * R, y + 1.05 * R)
    return arr(s)


def side_attila(x=370, y=615, R=165):
    s = surface()
    c = s.getCanvas()
    draw_character(c, x, y, R, 'cheeks', 'blank', ATTILA, show_rim=False)
    face_shading(c, x, y, R, [(x - 0.92 * R, y + 0.4 * R, 0.3 * R), (x + 0.92 * R, y + 0.4 * R, 0.3 * R)], top=-0.15)
    for side in (-1, 1):
        eye(c, x + side * 0.24 * R, y - 0.05 * R, R, rx=0.11, ry=0.13, pupil=(0.0, 0.01, 0.028))
        brow(c, x + side * 0.12 * R, y - 0.24 * R, x + side * 0.36 * R, y - 0.31 * R, 0.04 * R, 0.035 * R)
    nosebleed(c, x, y, R)
    hand(c, x - 0.86 * R, y + 0.36 * R, 0.33 * R, 18)
    hand(c, x + 0.86 * R, y + 0.36 * R, 0.33 * R, -18, mirror=True)
    return arr(s)


def side_crassus(x=1555, y=600, R=160):
    s = surface()
    c = s.getCanvas()
    draw_character(c, x, y, R, 'shrug', 'blank', CRASSUS, show_rim=False)
    face_shading(c, x, y, R, top=-0.3)
    for side in (-1, 1):
        x_eye(c, x + side * 0.24 * R, y - 0.06 * R, R)
    mx, my = x, y + 0.38 * R
    m = skia.Path()
    m.addOval(skia.Rect(mx - 0.13 * R, my - 0.15 * R, mx + 0.13 * R, my + 0.15 * R))
    gsh = skia.GradientShader.MakeRadial((mx - 0.03 * R, my - 0.04 * R), 0.16 * R, [rgb('#FFF6B0'), rgb('#F2B705'), rgb('#9A6200')])
    c.drawPath(m, skia.Paint(Shader=gsh, AntiAlias=True))
    c.drawPath(m, _stroke(0.03 * R))
    for k, (dx, ln) in enumerate(((-0.06, 0.32), (0.05, 0.42))):         # gold dripping down the chin
        d = skia.Path()
        d.addRRect(skia.RRect.MakeRectXY(skia.Rect(mx + dx * R - 0.03 * R, my + 0.1 * R, mx + dx * R + 0.03 * R, my + ln * R), 0.03 * R, 0.03 * R))
        c.drawPath(d, paint('#F2B705'))
        c.drawPath(d, paint('#6A4300', stroke=0.012 * R))
    # the ladle pouring molten gold
    st = skia.Path()
    st.moveTo(mx - 0.05 * R, my - 1.25 * R)
    st.cubicTo(mx - 0.1 * R, my - 0.7 * R, mx + 0.05 * R, my - 0.3 * R, mx - 0.02 * R, my - 0.05 * R)
    st.lineTo(mx + 0.06 * R, my - 0.05 * R)
    st.cubicTo(mx + 0.14 * R, my - 0.35 * R, mx + 0.06 * R, my - 0.8 * R, mx + 0.12 * R, my - 1.25 * R)
    st.close()
    sh = skia.GradientShader.MakeLinear([(mx - 0.1 * R, 0), (mx + 0.15 * R, 0)], [rgb('#FFF59A'), rgb('#F2A900'), rgb('#B36B00')], [0, 0.5, 1])
    c.drawPath(st, skia.Paint(Shader=sh, AntiAlias=True))
    c.drawPath(st, paint('#5A3A00', stroke=0.02 * R))
    c.save()
    c.translate(mx + 0.03 * R, my - 1.35 * R)
    c.rotate(-35)
    bowl = skia.Path()
    bowl.addArc(skia.Rect(-0.38 * R, -0.3 * R, 0.38 * R, 0.3 * R), 0, 180)
    bowl.close()
    bsh = skia.GradientShader.MakeLinear([(-0.38 * R, 0), (0.38 * R, 0)], [rgb('#B8C0CA'), rgb('#6E7681')])
    c.drawPath(bowl, skia.Paint(Shader=bsh, AntiAlias=True))
    c.drawPath(bowl, paint(INK, stroke=0.035 * R))
    c.drawLine(0.34 * R, 0, 1.3 * R, -0.6 * R, paint(INK, stroke=0.12 * R, cap='round'))
    c.drawLine(0.34 * R, 0, 1.3 * R, -0.6 * R, paint('#8C939C', stroke=0.06 * R, cap='round'))
    c.restore()
    return arr(s)


def side_arrichion_lying(x=230, y=880, R=130):
    s = surface()
    c = s.getCanvas()
    c.save()
    c.rotate(-90, x, y)
    draw_character(c, x, y - 30, R, 'idle', 'blank', ARRICHION_WREATH, show_rim=False)
    c.restore()
    hx, hy = x - 30, y                                               # head centre after the rotation
    for side in (-1, 1):
        x_eye(c, hx - 0.05 * R, hy + side * 0.24 * R, R)
    m = skia.Path()
    m.moveTo(hx + 0.22 * R, hy - 0.25 * R)
    m.quadTo(hx + 0.62 * R, hy, hx + 0.22 * R, hy + 0.25 * R)
    m.close()
    c.drawPath(m, paint('#2A100B'))
    c.drawPath(m, _stroke(0.032 * R))
    medal(c, hx + 1.55 * R, hy - 0.05 * R, 0.33 * R, hy - 0.7 * R)
    return arr(s)


def side_nephew(x=1560, y=610, R=150):
    s = surface()
    c = s.getCanvas()
    draw_character(c, x, y, R, 'wave', 'blank', NEPHEW, show_rim=False)
    face_shading(c, x, y, R, top=-0.25)
    for side in (-1, 1):
        eye(c, x + side * 0.24 * R, y - 0.03 * R, R, rx=0.08, ry=0.09)
        brow(c, x + side * 0.1 * R, y - 0.13 * R, x + side * 0.36 * R, y - 0.24 * R, -0.02 * R, 0.045 * R)
    mouth_open(c, x, y + 0.38 * R, 0.16 * R, 0.13 * R, R, teeth=True, tongue=False)
    sweat(c, x + 0.62 * R, y - 0.2 * R, 0.06 * R, 20)
    draw_prop(c, 'drum', x + 1.25 * R, y + 1.35 * R, 1.0 * R, hit=True)
    return arr(s)


# ================================================================ title
def title_layers(s, style='white', top=0.025):
    path, cap = title_layout(s, top_frac=top)
    t = surface()
    t.getCanvas().drawPath(path, paint('#FFFFFF' if style == 'white' else '#0A0A0A'))
    a = arr(t)
    if style == 'white':
        sh = solid(blur(shift(a[..., 3], 0, cap * 0.045), cap * 0.1), (0, 0, 0), 0.85)
        edge = solid(blur(a[..., 3], cap * 0.03), (0, 0, 0), 0.7)
        full = over(over(sh, edge), a)
    else:
        full = a
    ghost = a * (0.42 if style == 'white' else 0.32)
    return full, ghost


# ================================================================ finishing
def finish(img, bloom=0.32, vignette=0.38, grain=0.018, sat=1.08, curve=0.12, seed=0):
    x = img[..., :3].copy()
    x = x - curve * (x - 0.5) * (1 - 4 * (x - 0.5) ** 2) * -1          # gentle S-curve
    m = x.mean(2, keepdims=True)
    x = np.clip(m + (x - m) * sat, 0, 1)
    lum = x.max(2)
    hi = np.clip((lum - 0.72) / 0.28, 0, 1)[..., None] * x
    x = 1 - (1 - x) * (1 - blur(hi, 22) * bloom)
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    d = np.sqrt(((xx - TW / 2) / (TW / 2)) ** 2 + ((yy - TH * 0.55) / (TH * 0.62)) ** 2)
    x *= (1 - vignette * np.clip(d - 0.55, 0, 1) ** 1.6)[..., None]
    rng = np.random.default_rng(seed)
    x += rng.normal(0, grain, (TH, TW, 1)).astype(np.float32)
    x = np.clip(x, 0, 1)
    sharp = np.clip(x + 0.35 * (x - blur(x, 1.6)), 0, 1)
    return (sharp * 255).astype(np.uint8)


def bokeh(n=30, col='#FFB65C', seed=4, region=(0, TW, 0, TH), rmin=8, rmax=34, sigma=4, alpha=(0.15, 0.6)):
    s = surface()
    c = s.getCanvas()
    rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = rng.uniform(region[0], region[1]), rng.uniform(region[2], region[3])
        r = rng.uniform(rmin, rmax)
        c.drawCircle(x, y, r, paint(col, alpha=int(255 * rng.uniform(*alpha))))
    a = arr(s)
    return blur(a, sigma)


# ================================================================ thumbnails
def t1():
    """EPIC DEATHS - Arbo's Battle of Stamford Bridge, defocused, golden backlight."""
    bg = plate('stamford_arbo', 6.0, focus=(0.52, 0.42), zoom=1.15)
    bg = grade(bg, lift=(0.0, 0.0, 0.02), gain=(0.85, 0.98, 1.15), gamma=0.95, sat=1.35, contrast=1.12)
    bg = light_pool(bg, 960, 470, 760, '#FFB45E', 0.45)
    bg = over(bg, god_rays(960, 500, 24, alpha=0.06))
    bg = top_shade(bg, 0.42, 0.5)
    bg = bg_vignette(bg, 0.55)
    bg = over(bg, bokeh(22, '#FFD08A', 3, (0, TW, 300, 900), 5, 18, 3, (0.2, 0.6)))
    img = bg
    img = over(img, character_fx(side_harald(), light=(1, -0.5), rim='#FFD9A0', shadow=(18, 24, 20, 0.55)))
    img = over(img, character_fx(side_arrichion(), light=(-1, -0.5), rim='#FFF2B8', shadow=(-18, 24, 20, 0.5),
                                 glow=('#FFF1B0', 14, 0.55)))
    full, ghost = title_layers('EPIC DEATHS', 'white')
    img = over(img, full)
    img = over(img, character_fx(hero('scream', 960, 628, 348), light=(0.2, -1), rim='#FFE4B0', rim_w=9, rim_amt=0.9,
                                 shadow=(0, 34, 34, 0.7), glow=('#FFE7B8', 12, 0.3), shade=0.32, shade_top=0.62))
    img = over(img, ghost)
    return finish(img, bloom=0.3, vignette=0.0, sat=1.12, seed=1)


def t2():
    """INSANE DEATHS - Hubert Robert's Fire of Rome, defocused, ember-lit."""
    bg = plate('fire_rome', 5.5, focus=(0.5, 0.55), zoom=1.1)
    bg = grade(bg, lift=(0.04, 0.01, 0.0), gain=(0.9, 0.95, 1.25), gamma=1.15, sat=1.35, contrast=1.12)
    bg = light_pool(bg, 960, 560, 760, '#FF7A2A', 0.6)
    bg = bg_vignette(bg, 0.6)
    bg = over(bg, bokeh(55, '#FF9A3A', 6, (0, TW, 200, TH), 4, 16, 2.5, (0.25, 0.8)))
    img = bg
    img = over(img, character_fx(side_attila(), light=(1, -0.4), rim='#FF9A4A', shadow=(18, 26, 22, 0.6)))
    img = over(img, character_fx(side_crassus(), light=(-1, -0.4), rim='#FFC266', shadow=(-18, 26, 22, 0.6),
                                 glow=('#FFC34A', 12, 0.45)))
    full, ghost = title_layers('INSANE DEATHS', 'white')
    img = over(img, full)
    img = over(img, character_fx(hero('terror', 960, 628, 348), light=(0, -1), rim='#FFB070', rim_w=10, rim_amt=0.95,
                                 shadow=(0, 34, 36, 0.75), glow=('#FF9F5A', 12, 0.28), shade=0.38, shade_top=0.6))
    img = over(img, ghost)
    return finish(img, bloom=0.4, vignette=0.0, seed=2)


def t3():
    """LEGENDARY DEATHS - white title band over Raphael's golden fresco, defocused."""
    bg = plate('leo_attila', 6.5, focus=(0.5, 0.52), zoom=1.25)
    bg = grade(bg, lift=(0.0, 0.01, 0.03), gain=(0.82, 0.98, 1.12), gamma=1.05, sat=1.3, contrast=1.1)
    bg = light_pool(bg, 960, 520, 820, '#FFE2A0', 0.45)
    bg = bg_vignette(bg, 0.45)
    bg = over(bg, bokeh(24, '#FFE3A0', 5, (0, TW, 250, 950), 4, 14, 2.5, (0.2, 0.6)))
    yy = np.mgrid[0:TH, 0:TW][0].astype(np.float32)
    band = np.zeros((TH, TW, 4), np.float32)
    a = np.clip(1 - (yy - TH * 0.19) / (TH * 0.13), 0, 1)
    band[..., :3] = a[..., None]
    band[..., 3] = a
    img = over(bg, band)
    img = over(img, character_fx(side_arrichion_lying(), light=(1, -1), rim='#FFF2C0', shadow=(10, 18, 14, 0.5),
                                 glow=('#FFF1B0', 10, 0.45)))
    img = over(img, character_fx(side_nephew(), light=(-1, -0.4), rim='#FFD08A', shadow=(-16, 24, 20, 0.55)))
    full, ghost = title_layers('LEGENDARY DEATHS', 'black', top=0.03)
    img = over(img, full)
    img = over(img, character_fx(hero('shock', 960, 612, 338), light=(0.3, -1), rim='#FFF0D0', rim_w=8, rim_amt=0.8,
                                 shadow=(0, 30, 32, 0.6), glow=('#FFFFFF', 10, 0.3), shade=0.3, shade_top=0.62))
    img = over(img, ghost)
    return finish(img, bloom=0.3, vignette=0.0, sat=1.1, seed=3)


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    cv2.imwrite(os.path.join(OUT, name + '_master.png'), img)
    small = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(OUT, name + '.jpg'), small, [cv2.IMWRITE_JPEG_QUALITY, 94])
    return small


if __name__ == '__main__':
    outs = [save(t1(), 'premium_1_epic_deaths'), save(t2(), 'premium_2_insane_deaths'), save(t3(), 'premium_3_legendary_deaths')]
    ref = sys.argv[1] if len(sys.argv) > 1 else None
    if ref:
        refs = [cv2.resize(cv2.imread(os.path.join(ref, n + '.png')), (640, 360)) for n in ('crazy_places', 'unknown', 'ancient_mysteries')]
        ours = [cv2.resize(o, (640, 360), interpolation=cv2.INTER_AREA) for o in outs]
        cv2.imwrite(os.path.join(OUT, 'premium_vs_reference.jpg'), np.vstack([np.hstack(refs), np.hstack(ours)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print('done')
