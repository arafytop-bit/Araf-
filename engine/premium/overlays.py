"""Text overlays in the reference grammar, sized for phones (min cap 4.5 % of frame height = 49 px).

callout : red caps, centred, top at 11 % H, cap 9 % H (reference 8.5-9.6 %), soft shadow, 5-frame settle
tag     : name tag, white caps on a black pill, pops in (cap 4.5 % H)
caption : photo caption pill under a framed photo
speech  : character line, white caps with a black outline (cap 4.5 % H)
band    : meme caption, black caps on a full-width white band (26-33 % H)
stamp   : red rubber stamp, slams in (scale 1.5 -> 1.0 in 3 frames)
"""
import math

import skia

from engine.core import W, H, rgb
from engine.premium import typo as TY
from engine.premium import motion as M

MIN_CAP = 49.0
CALLOUT_CAP = 97.0
CALLOUT_TOP = 0.11 * H
SAFE_X = 0.045 * W


def callout_layout(text, cap=CALLOUT_CAP, max_w=0.91 * W, weight=800):
    """-> (lines, cap, box rect). Two balanced lines if one is too wide; cap never below 6.4 % H."""
    lines, cap2 = [text], cap
    if TY.width(text, cap, weight) > max_w:
        lines, cap2 = TY.balance(text, cap, max_w, weight)
        cap2 = max(cap2, 69.0)
        if max(TY.width(ln, cap2, weight) for ln in lines) > max_w:
            lines, cap2 = TY.wrap(text, 69.0, max_w, weight, max_lines=3)
    lh = cap2 * 1.38
    wmax = max(TY.width(ln, cap2, weight) for ln in lines)
    top = CALLOUT_TOP
    box = skia.Rect(W / 2 - wmax / 2, top, W / 2 + wmax / 2, top + cap2 + lh * (len(lines) - 1))
    return lines, cap2, box


def callout(c, text, df, style='red', top=None, weight=800, cap=CALLOUT_CAP):
    lines, cap2, box = callout_layout(text, cap, weight=weight)
    if top is not None:
        box.offset(0, top - box.top())
    s, a = M.settle(df, frames=5)
    if a <= 0:
        return box
    lh = cap2 * 1.38
    cy = (box.top() + box.bottom()) / 2
    c.save()
    c.translate(W / 2, cy)
    c.scale(s, s)
    c.translate(-W / 2, -cy)
    for k, ln in enumerate(lines):
        TY.draw(c, ln, W / 2, box.top() + cap2 + k * lh, cap2, style=style, weight=weight, align='center',
                alpha=int(255 * a), shadow=0.95, tracking=0.015)
    c.restore()
    return box


def pill(c, rect, color='#0A0A0A', alpha=0.92, radius=None, border=None):
    p = skia.Paint(AntiAlias=True, Color=rgb(color))
    p.setAlphaf(alpha)
    r = radius if radius is not None else rect.height() * 0.22
    sh = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    sh.setAlphaf(0.45 * alpha)
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, rect.height() * 0.18))
    c.drawRRect(skia.RRect.MakeRectXY(rect.makeOffset(0, rect.height() * 0.08), r, r), sh)
    c.drawRRect(skia.RRect.MakeRectXY(rect, r, r), p)
    if border:
        bp = skia.Paint(AntiAlias=True, Color=rgb(border[0]), Style=skia.Paint.kStroke_Style, StrokeWidth=border[1])
        bp.setAlphaf(alpha)
        c.drawRRect(skia.RRect.MakeRectXY(rect, r, r), bp)


def tag(c, text, cx, bottom, df, cap=MIN_CAP, color='#FFFFFF', bg='#0A0A0A', accent=None, max_w=None):
    """Name tag centred at cx with its bottom edge at `bottom`. Returns its rect."""
    weight = 800
    w = TY.width(text, cap, weight)
    if max_w and w > max_w:
        cap *= max_w / w
        w = max_w
    padx, pady = cap * 0.62, cap * 0.52
    cx = min(max(cx, SAFE_X + w / 2 + padx), W - SAFE_X - w / 2 - padx)
    rect = skia.Rect(cx - w / 2 - padx, bottom - cap - 2 * pady, cx + w / 2 + padx, bottom)
    s, a = M.pop(df, 0.6)
    if a <= 0:
        return rect
    c.save()
    c.translate(cx, rect.bottom())
    c.scale(s, s)
    c.translate(-cx, -rect.bottom())
    c.saveLayerAlpha(None, int(255 * a))
    pill(c, rect, bg, 0.92)
    if accent:
        ap = skia.Paint(AntiAlias=True, Color=rgb(accent))
        c.drawRect(skia.Rect(rect.left(), rect.bottom() - cap * 0.14, rect.right(), rect.bottom()), ap)
    TY.draw(c, text, cx, rect.bottom() - pady - (cap * 0.14 if accent else 0), cap, style=color, weight=weight, align='center', shadow=0)
    c.restore()
    c.restore()
    return rect


def speech(c, text, cx, bottom, df, cap=MIN_CAP, max_w=0.62 * W):
    """Character line: white caps with a thick black outline, up to 2 lines, bottom edge at `bottom`."""
    lines, cap2 = TY.balance(text, cap, max_w, 800, max_lines=2)
    lh = cap2 * 1.32
    wmax = max(TY.width(ln, cap2, 800) for ln in lines)
    cx = min(max(cx, SAFE_X + wmax / 2), W - SAFE_X - wmax / 2)
    top = bottom - cap2 - lh * (len(lines) - 1)
    s, a = M.pop(df, 0.55)
    rect = skia.Rect(cx - wmax / 2, top, cx + wmax / 2, bottom)
    if a <= 0:
        return rect
    c.save()
    c.translate(cx, bottom)
    c.scale(s, s)
    c.translate(-cx, -bottom)
    for k, ln in enumerate(lines):
        TY.draw(c, ln, cx, top + cap2 + k * lh, cap2, style='#FFFFFF', weight=800, align='center', alpha=int(255 * a),
                shadow=0.8, stroke=cap2 * 0.30, stroke_color='#0B0B0B')
    c.restore()
    return rect


def band(c, text, df, h_frac=0.28, cap=None):
    """Meme band: full-width white band at the top with black caps (reference: 26-33 % H, emoji allowed)."""
    bh = H * h_frac
    cap = cap or 0.078 * H
    lines, cap2 = TY.balance(text, cap, 0.92 * W, 900, max_lines=2)
    if len(lines) == 1 and TY.width(lines[0], cap2, 900) > 0.92 * W:
        cap2 *= 0.92 * W / TY.width(lines[0], cap2, 900)
    lh = cap2 * 1.30
    k = M.ease_out_cubic((df + 1) / 4)
    y0 = -bh * (1 - k)
    p = skia.Paint(AntiAlias=True, Color=rgb('#FFFFFF'))
    c.drawRect(skia.Rect(0, y0, W, y0 + bh), p)
    total = cap2 + lh * (len(lines) - 1)
    top = y0 + (bh - total) / 2
    for i, ln in enumerate(lines):
        TY.draw(c, ln, W / 2, top + cap2 + i * lh, cap2, style='#0B0B0B', weight=900, align='center', shadow=0, tracking=0.01)
    return skia.Rect(0, 0, W, bh)


def stamp(c, text, cx, cy, df, cap=72.0, angle=-7.0, color='#E0262B', sub=None):
    """Red stamp that slams in: 150 % -> 100 % in 3 frames, then holds (with a soft inner texture)."""
    if df < 0:
        return None
    t = min(1.0, (df + 1) / 3)
    s = 1.5 - 0.5 * M.ease_out_cubic(t)
    if df >= 3:
        s = 1 + 0.03 * M.decay_osc((df - 3) / 30, 6, 12)
    a = min(1.0, (df + 1) / 2)
    lines = [text] + ([sub] if sub else [])
    caps = [cap] + ([cap * 0.52] if sub else [])
    ws = [TY.width(ln, cp, 900) for ln, cp in zip(lines, caps)]
    padx, pady = cap * 0.55, cap * 0.45
    w = max(ws) + 2 * padx
    hgt = sum(caps) + (len(lines) - 1) * cap * 0.42 + 2 * pady
    c.save()
    c.translate(cx, cy)
    c.rotate(angle)
    c.scale(s, s)
    c.saveLayerAlpha(None, int(255 * a))
    rect = skia.Rect(-w / 2, -hgt / 2, w / 2, hgt / 2)
    bg = skia.Paint(AntiAlias=True, Color=rgb('#0B0B0B'))
    bg.setAlphaf(0.55)
    c.drawRRect(skia.RRect.MakeRectXY(rect, cap * 0.18, cap * 0.18), bg)
    bp = skia.Paint(AntiAlias=True, Color=rgb(color), Style=skia.Paint.kStroke_Style, StrokeWidth=cap * 0.13)
    c.drawRRect(skia.RRect.MakeRectXY(rect, cap * 0.18, cap * 0.18), bp)
    y = -hgt / 2 + pady
    for ln, cp in zip(lines, caps):
        y += cp
        TY.draw(c, ln, 0, y, cp, style=color, weight=900, align='center', shadow=0)
        y += cp * 0.42
    c.restore()
    c.restore()
    return skia.Rect(cx - w / 2, cy - hgt / 2, cx + w / 2, cy + hgt / 2)


def draw_check(c, x, y, size, color='#3DDC84', df=99):
    k = M.draw_on(df, 6)
    p = skia.Path()
    p.moveTo(x - size * 0.45, y)
    p.lineTo(x - size * 0.12, y + size * 0.32)
    p.lineTo(x + size * 0.48, y - size * 0.38)
    _stroke_partial(c, p, k, size * 0.2, color)


def draw_x(c, x, y, size, color='#E0393E', df=99):
    k = M.draw_on(df, 6)
    p1 = skia.Path(); p1.moveTo(x - size * 0.38, y - size * 0.38); p1.lineTo(x + size * 0.38, y + size * 0.38)
    p2 = skia.Path(); p2.moveTo(x + size * 0.38, y - size * 0.38); p2.lineTo(x - size * 0.38, y + size * 0.38)
    _stroke_partial(c, p1, min(1.0, k * 2), size * 0.2, color)
    if k > 0.5:
        _stroke_partial(c, p2, (k - 0.5) * 2, size * 0.2, color)


def _stroke_partial(c, path, k, width, color):
    if k <= 0:
        return
    pm = skia.PathMeasure(path, False)
    ln = pm.getLength()
    dst = skia.Path()
    pm.getSegment(0, ln * k, dst, True)
    sp = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 1.6,
                    StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    sp.setAlphaf(0.55)
    sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, width * 0.4))
    c.drawPath(dst, sp)
    p = skia.Paint(AntiAlias=True, Color=rgb(color), Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    c.drawPath(dst, p)


def stroke_partial(c, path, k, width, color, shadow=True):
    _stroke_partial(c, path, k, width, color)


def arrow(c, x0, y0, x1, y1, df, color='#E0393E', width=16, frames=8, bend=0.18):
    """Hand-drawn style annotation arrow that draws on, then the head pops."""
    k = M.draw_on(df, frames)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0) * bend, (x1 - x0) * bend
    p = skia.Path()
    p.moveTo(x0, y0)
    p.quadTo(mx + nx, my + ny, x1, y1)
    _stroke_partial(c, p, k, width, color)
    if k >= 0.98:
        ang = math.atan2(y1 - (my + ny), x1 - (mx + nx))
        hl = width * 2.6
        h = skia.Path()
        h.moveTo(x1 + math.cos(ang - 2.55) * hl, y1 + math.sin(ang - 2.55) * hl)
        h.lineTo(x1, y1)
        h.lineTo(x1 + math.cos(ang + 2.55) * hl, y1 + math.sin(ang + 2.55) * hl)
        _stroke_partial(c, h, 1.0, width, color)


def ring(c, cx, cy, rx, ry, df, color='#E0393E', width=12, frames=9):
    """Hand-drawn circle annotation that draws on (slightly overshooting its start)."""
    k = M.draw_on(df, frames)
    p = skia.Path()
    n = 48
    for i in range(n + 6):
        a = -math.pi / 2 + 2 * math.pi * i / n
        wob = 1 + 0.03 * math.sin(i * 0.9)
        x, y = cx + math.cos(a) * rx * wob, cy + math.sin(a) * ry * wob
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    _stroke_partial(c, p, k, width, color)
