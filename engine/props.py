"""Prop library in the round-head inked style. Each prop is a list of Parts in local units
(about 1 unit = half the prop's size) drawn with roundhead.render_parts."""
import math
import skia
from .roundhead import Part, P, oval, line, poly, quad, cubic, render_parts, INK, _shade


def _rr(x0, y0, x1, y1, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r))
    return p


def longship(sail='#B23A32', stripe='#F1E6D0', hull='#7A5434', t=0.0):
    out = [Part(line((0.0, 0.25), (0.0, -1.35)), tube=0.07, fill='#5A3B26')]
    sail_pts = [(-0.62, -1.20), (0.62, -1.20), (0.66, -0.30), (-0.66, -0.30)]
    out.append(Part(poly(sail_pts), fill=sail, ow=0.05))
    for x in (-0.33, 0.33):
        out.append(Part(poly([(x - 0.11, -1.19), (x + 0.11, -1.19), (x + 0.115, -0.31), (x - 0.115, -0.31)]), fill=stripe, ow=0, rim=False))
    out.append(Part(poly(sail_pts), ow=0.05, rim=False))
    h = skia.Path()
    h.moveTo(-1.45, -0.42); h.quadTo(-1.30, 0.25, -0.70, 0.32); h.lineTo(0.70, 0.32); h.quadTo(1.30, 0.25, 1.45, -0.42)
    h.quadTo(1.12, -0.05, 0.80, -0.05); h.lineTo(-0.80, -0.05); h.quadTo(-1.12, -0.05, -1.45, -0.42); h.close()
    out.append(Part(h, fill=hull, grad=(-0.45, 0.32, 1.15, 0.8)))
    for k in range(7):
        x = -0.72 + k * 0.24
        out.append(Part(oval(x, 0.06, 0.11, 0.11), fill=('#C9A050' if k % 2 else '#3E6BB5'), ow=0.035))
    head = P([(1.40, -0.42), (1.52, -0.72), (1.68, -0.78), (1.74, -0.66), (1.58, -0.60), (1.50, -0.40)], tension=0.6)
    out.append(Part(head, fill=hull, ow=0.045))
    return out


def turtle_ship(t=0.0):
    out = []
    for k in range(6):
        x = -0.9 + k * 0.36
        out.append(Part(line((x, 0.25), (x - 0.18, 0.62)), ow=0.05, rim=False))
    hull = P([(-1.45, -0.05), (1.40, -0.05), (1.25, 0.35), (-1.25, 0.35)], tension=0.3)
    out.append(Part(hull, fill='#7A5434', grad=(-0.05, 0.35, 1.15, 0.8)))
    roof = skia.Path(); roof.moveTo(-1.30, -0.05); roof.cubicTo(-1.10, -0.95, 1.10, -0.95, 1.30, -0.05); roof.close()
    out.append(Part(roof, fill='#4F6B5A', grad=(-0.75, -0.05, 1.2, 0.85)))
    for k in range(9):
        a = math.pi * (0.12 + k * 0.095)
        x, y = -math.cos(a) * 1.18, -math.sin(a) * 0.62 - 0.05
        out.append(Part(poly([(x - 0.05, y + 0.02), (x, y - 0.13), (x + 0.05, y + 0.02)]), fill='#B9BDC2', ow=0.025, rim=False))
    for k in range(4):
        out.append(Part(oval(-0.75 + k * 0.5, 0.15, 0.06, 0.06), fill=INK, ow=0, rim=False))
    head = P([(1.30, -0.15), (1.55, -0.38), (1.78, -0.30), (1.70, -0.08), (1.42, 0.05)], tension=0.6)
    out.append(Part(head, fill='#C9A050', ow=0.045))
    out.append(Part(oval(1.62, -0.27, 0.035, 0.035), fill=INK, ow=0, rim=False))
    out.append(Part(poly([(1.70, -0.12), (1.86, -0.10), (1.72, -0.04)]), fill='#C0392B', ow=0.02, rim=False))
    return out


def jp_ship(t=0.0):
    out = [Part(line((0.0, 0.0), (0.0, -1.3)), tube=0.06, fill='#4A3326')]
    out.append(Part(poly([(-0.55, -1.20), (0.55, -1.20), (0.55, -0.45), (-0.55, -0.45)]), fill='#EDE6D3', ow=0.045))
    out.append(Part(oval(0.0, -0.82, 0.20, 0.20), fill='#C0392B', ow=0.03, rim=False))
    out.append(Part(poly([(-0.75, -0.40), (0.55, -0.40), (0.55, -0.05), (-0.75, -0.05)]), fill='#5A3B26', ow=0.04))
    hull = P([(-1.40, -0.15), (1.45, -0.20), (1.20, 0.32), (-1.20, 0.32)], tension=0.3)
    out.append(Part(hull, fill='#3E2A1F', grad=(-0.2, 0.32, 1.2, 0.8)))
    return out


def coin(t=0.0):
    return [Part(oval(0, 0, 1.0, 1.0), fill='#E8B83A', grad=(-1, 1, 1.15, 0.85)),
            Part(oval(0, 0, 0.72, 0.72), ow=0.06, rim=False, color='#B8862A', ink=False)]


def gold_pile(t=0.0, n=9):
    out = []
    for row, cnt in enumerate((4, 3, 2)):
        for k in range(cnt):
            x = (k - (cnt - 1) / 2) * 0.62
            y = 0.40 - row * 0.32
            out.append(Part(poly([(x - 0.30, y), (x + 0.30, y), (x + 0.22, y - 0.30), (x - 0.22, y - 0.30)]),
                            fill='#E8B83A', grad=(y - 0.3, y, 1.2, 0.85), ow=0.045))
    for k, (x, y) in enumerate([(-1.05, 0.30), (1.05, 0.28), (-0.85, 0.52), (0.95, 0.52), (0.0, 0.55)]):
        out.append(Part(oval(x, y, 0.18, 0.09), fill='#F2C94C', ow=0.035))
    return out


def crown_prop(t=0.0):
    pts = [(-0.9, 0.5), (-0.95, -0.45), (-0.5, 0.0), (0.0, -0.65), (0.5, 0.0), (0.95, -0.45), (0.9, 0.5)]
    return [Part(poly(pts), fill='#E8B83A', grad=(-0.65, 0.5, 1.2, 0.85)),
            Part(oval(0, 0.25, 0.12, 0.10), fill='#C0392B', ow=0.03, rim=False)]


def sword(t=0.0, glow=False):
    out = []
    if glow:
        out.append(Part(oval(0, -0.3, 0.55, 1.35), fill='#FFE9A8', ow=0, rim=False, alpha=90))
    out.append(Part(poly([(-0.09, 0.42), (0.09, 0.42), (0.09, -1.30), (0.0, -1.48), (-0.09, -1.30)]), fill='#D7DCE1', grad=(-1.48, 0.42, 1.1, 0.8)))
    out.append(Part(_rr(-0.42, 0.38, 0.42, 0.52, 0.05), fill='#8A6A3A'))
    out.append(Part(line((0.0, 0.52), (0.0, 0.92)), tube=0.10, fill='#5A3B26'))
    out.append(Part(oval(0.0, 0.98, 0.09, 0.09), fill='#C9A050'))
    return out


def arrow(t=0.0):
    return [Part(line((-1.3, 0.0), (1.1, 0.0)), tube=0.05, fill='#8A6A3A'),
            Part(poly([(1.05, -0.14), (1.42, 0.0), (1.05, 0.14)]), fill='#9AA3AD', ow=0.035),
            Part(poly([(-1.30, 0.0), (-1.05, -0.20), (-0.85, -0.20), (-1.10, 0.0)]), fill='#E6E1D3', ow=0.03),
            Part(poly([(-1.30, 0.0), (-1.05, 0.20), (-0.85, 0.20), (-1.10, 0.0)]), fill='#E6E1D3', ow=0.03)]


def shield(t=0.0, c='#3E6BB5', c2='#E6E1D3'):
    out = [Part(oval(0, 0, 1.0, 1.0), fill=c)]
    for k in range(4):
        a0 = math.radians(k * 90)
        p = skia.Path(); p.moveTo(0, 0); p.arcTo(skia.Rect(-1, -1, 1, 1), math.degrees(a0), 45, False); p.close()
        out.append(Part(p, fill=c2, ow=0, rim=False))
    out.append(Part(oval(0, 0, 1.0, 1.0), ow=0.07, rim=False))
    out.append(Part(oval(0, 0, 0.25, 0.25), fill='#9AA3AD', ow=0.05))
    return out


def book(t=0.0, c='#7A3B2E'):
    return [Part(_rr(-0.75, -1.0, 0.75, 1.0, 0.08), fill=c, grad=(-1, 1, 1.15, 0.85)),
            Part(poly([(-0.62, -0.92), (-0.62, 0.92), (-0.70, 0.92), (-0.70, -0.92)]), fill=_shade(c, 0.7), ow=0, rim=False),
            Part(_rr(-0.45, -0.55, 0.55, -0.05, 0.04), fill='#E8D7A8', ow=0.035, rim=False)]


def tombstone(t=0.0):
    p = skia.Path(); p.moveTo(-0.8, 1.0); p.lineTo(-0.8, -0.3); p.cubicTo(-0.8, -1.25, 0.8, -1.25, 0.8, -0.3); p.lineTo(0.8, 1.0); p.close()
    return [Part(p, fill='#9DA3A8', grad=(-1.0, 1.0, 1.15, 0.8)),
            Part(_rr(-1.0, 0.92, 1.0, 1.12, 0.04), fill='#6E5A45')]


def coffin(t=0.0, c='#C9A050'):
    pts = [(-0.45, -1.2), (0.45, -1.2), (0.62, -0.55), (0.40, 1.2), (-0.40, 1.2), (-0.62, -0.55)]
    return [Part(poly(pts), fill=c, grad=(-1.2, 1.2, 1.2, 0.75)),
            Part(line((0.0, -0.75), (0.0, -0.05)), ow=0.07, rim=False, color=_shade(c, 0.6), ink=False),
            Part(line((-0.22, -0.50), (0.22, -0.50)), ow=0.07, rim=False, color=_shade(c, 0.6), ink=False)]


def wreath(t=0.0):
    out = []
    for side in (-1, 1):
        for k in range(8):
            a = math.radians(100 + k * 20) if side < 0 else math.radians(80 - k * 20)
            x, y = math.cos(a), -math.sin(a) * 0.95 + 0.1
            lf = oval(0, 0, 0.24, 0.10)
            m = skia.Matrix(); m.setRotate(-math.degrees(a) + (75 if side < 0 else -75)); m.postTranslate(x, -y * -1)
            lf.transform(m)
            out.append(Part(lf, fill='#7FA650' if k % 2 else '#93B862', ow=0.035))
    out.append(Part(oval(0.0, 1.0, 0.12, 0.10), fill='#B23A32', ow=0.03))
    return out


def house(t=0.0, burning=False):
    out = [Part(poly([(-0.85, 1.0), (-0.85, -0.25), (0.85, -0.25), (0.85, 1.0)]), fill='#D9C29A', grad=(-0.25, 1, 1.05, 0.85)),
           Part(poly([(-1.05, -0.20), (0.0, -1.05), (1.05, -0.20)]), fill='#B0563E', grad=(-1.05, -0.2, 1.1, 0.85))]
    for x in (-0.45, 0.45):
        out.append(Part(_rr(x - 0.18, 0.05, x + 0.18, 0.38, 0.03), fill='#5B4A3A', ow=0.04))
    out.append(Part(_rr(-0.17, 0.48, 0.17, 1.0, 0.03), fill='#6E4A2E', ow=0.04))
    if burning:
        out += flames(t, scale=1.0, base=-0.2)
    return out


def flames(t=0.0, scale=1.0, base=0.0):
    out = []
    for k, (x, h) in enumerate([(-0.55, 0.9), (0.0, 1.25), (0.55, 0.95)]):
        f = 1.0 + 0.12 * math.sin(t * 9 + k * 2.1)
        hh = h * f * scale
        outer = P([(x - 0.32, base), (x - 0.22, base - hh * 0.55), (x, base - hh), (x + 0.24, base - hh * 0.5), (x + 0.32, base)], tension=0.8)
        out.append(Part(outer, fill='#F07A2A', ow=0.04))
        inner = P([(x - 0.16, base), (x - 0.08, base - hh * 0.45), (x, base - hh * 0.7), (x + 0.10, base - hh * 0.35), (x + 0.16, base)], tension=0.8)
        out.append(Part(inner, fill='#FFD45A', ow=0, rim=False))
    return out


def jail_bars(t=0.0, n=7, broken=False):
    out = [Part(_rr(-1.6, -1.1, 1.6, -0.95, 0.03), fill='#5E6469'), Part(_rr(-1.6, 0.95, 1.6, 1.1, 0.03), fill='#5E6469')]
    for k in range(n):
        x = -1.4 + k * 2.8 / (n - 1)
        if broken and k in (n // 2 - 1, n // 2):
            out.append(Part(line((x, -0.95), (x + (0.5 if k == n // 2 else -0.5), -0.15)), tube=0.08, fill='#7C8287'))
        else:
            out.append(Part(line((x, -0.95), (x, 0.95)), tube=0.08, fill='#7C8287'))
    return out


def chain(t=0.0, n=9):
    out = []
    for k in range(n):
        x = -1.6 + k * 0.4
        if k % 2:
            out.append(Part(_rr(x - 0.22, -0.06, x + 0.22, 0.06, 0.06), ow=0.07, fill=None, color='#3E4247'))
        else:
            out.append(Part(oval(x, 0, 0.24, 0.13), ow=0.08, fill=None, color='#5E6469'))
    return out


def bridge(t=0.0):
    out = [Part(poly([(-1.8, -0.10), (1.8, -0.10), (1.8, 0.10), (-1.8, 0.10)]), fill='#8A6A45', grad=(-0.1, 0.1, 1.1, 0.85))]
    for x in (-1.4, -0.5, 0.5, 1.4):
        out.append(Part(line((x, 0.10), (x, 0.95)), tube=0.12, fill='#6E5236'))
    out.append(Part(line((-1.8, -0.45), (1.8, -0.45)), tube=0.05, fill='#8A6A45'))
    for x in (-1.5, -0.75, 0.0, 0.75, 1.5):
        out.append(Part(line((x, -0.45), (x, -0.10)), tube=0.04, fill='#8A6A45'))
    return out


def barrel(t=0.0):
    return [Part(P([(-0.55, -0.85), (0.55, -0.85), (0.72, 0.0), (0.55, 0.85), (-0.55, 0.85), (-0.72, 0.0)], tension=0.7),
                 fill='#9A6B3F', grad=(-0.85, 0.85, 1.15, 0.85)),
            Part(quad((-0.64, -0.45), (0.0, -0.38), (0.64, -0.45)), ow=0.07, rim=False, color='#4A4A4A', ink=False),
            Part(quad((-0.64, 0.45), (0.0, 0.52), (0.64, 0.45)), ow=0.07, rim=False, color='#4A4A4A', ink=False)]


def sun(t=0.0):
    out = []
    for k in range(12):
        a = k * math.pi / 6 + t * 0.4
        out.append(Part(line((math.cos(a) * 1.15, math.sin(a) * 1.15), (math.cos(a) * 1.5, math.sin(a) * 1.5)),
                        ow=0.09, rim=False, color='#F2C94C', ink=False))
    out.append(Part(oval(0, 0, 0.95, 0.95), fill='#F7D564', grad=(-0.95, 0.95, 1.08, 0.92), ow=0.05))
    return out


def dust(t=0.0):
    out = []
    for k, (x, y, r) in enumerate([(-1.2, 0.2, 0.5), (-0.5, -0.1, 0.65), (0.3, 0.0, 0.7), (1.05, 0.2, 0.55), (0.0, 0.35, 0.6)]):
        rr = r * (1 + 0.05 * math.sin(t * 3 + k))
        out.append(Part(oval(x, y, rr, rr * 0.7), fill='#C9B48E', ow=0.04, alpha=230))
    return out


def salt_shaker(t=0.0):
    return [Part(P([(-0.45, 1.0), (-0.50, -0.30), (-0.38, -0.62), (0.38, -0.62), (0.50, -0.30), (0.45, 1.0)], tension=0.5),
                 fill='#EEF2F5', grad=(-0.6, 1.0, 1.0, 0.85)),
            Part(P([(-0.38, -0.62), (-0.30, -0.95), (0.30, -0.95), (0.38, -0.62)], tension=0.5), fill='#B9C0C7'),
            Part(oval(-0.12, -0.80, 0.04, 0.03), fill=INK, ow=0, rim=False), Part(oval(0.12, -0.80, 0.04, 0.03), fill=INK, ow=0, rim=False),
            Part(oval(0.0, 0.35, 0.22, 0.22), fill='#FFFFFF', ow=0.03, rim=False)]


def drum(t=0.0, hit=False):
    out = [Part(_rr(-0.85, -0.45, 0.85, 0.70, 0.08), fill='#A0412F', grad=(-0.45, 0.7, 1.15, 0.8)),
           Part(oval(0.0, -0.45, 0.85, 0.22), fill='#E8DCC0'),
           Part(oval(0.0, 0.70, 0.85, 0.20), fill=None, ow=0.05, rim=False)]
    for k in range(5):
        x = -0.68 + k * 0.34
        out.append(Part(line((x, -0.40), (x + 0.17, 0.62)), ow=0.035, rim=False, color='#E8C27A', ink=False))
    a = -0.9 if hit else -0.4
    out.append(Part(line((0.35, -0.5), (0.35 + math.cos(a) * 0.9, -0.5 + math.sin(a) * 0.9)), tube=0.07, fill='#6E4A2E'))
    return out


def plate(t=0.0, c='#C9CED3'):
    return [Part(oval(0, 0, 1.0, 0.42), fill=c, grad=(-0.42, 0.42, 1.15, 0.85)), Part(oval(0, -0.02, 0.62, 0.24), fill=None, ow=0.04, rim=False)]


def cup(t=0.0, c='#E8B83A'):
    return [Part(P([(-0.55, -0.80), (0.55, -0.80), (0.35, 0.10), (-0.35, 0.10)], tension=0.4), fill=c, grad=(-0.8, 0.1, 1.2, 0.8)),
            Part(line((0.0, 0.10), (0.0, 0.70)), tube=0.12, fill=c), Part(oval(0.0, 0.78, 0.40, 0.10), fill=c)]


def tv(t=0.0):
    return [Part(_rr(-1.5, -1.0, 1.5, 1.0, 0.12), fill='#3A3D44'), Part(_rr(-1.3, -0.82, 1.3, 0.82, 0.06), fill='#9BC7E8', ow=0.04),
            Part(line((-0.3, 1.0), (-0.6, 1.35)), ow=0.07, rim=False), Part(line((0.3, 1.0), (0.6, 1.35)), ow=0.07, rim=False)]


def car(t=0.0, c='#C0392B'):
    body = P([(-1.6, 0.30), (-1.55, -0.10), (-0.85, -0.20), (-0.45, -0.70), (0.55, -0.70), (0.95, -0.20), (1.6, -0.12), (1.62, 0.30)], tension=0.4)
    return [Part(body, fill=c, grad=(-0.7, 0.3, 1.15, 0.8)),
            Part(P([(-0.35, -0.60), (0.10, -0.60), (0.10, -0.22), (-0.70, -0.22)], tension=0.3), fill='#BFE3FF', ow=0.035),
            Part(P([(0.22, -0.60), (0.48, -0.60), (0.80, -0.22), (0.22, -0.22)], tension=0.3), fill='#BFE3FF', ow=0.035),
            Part(oval(-0.95, 0.32, 0.30, 0.30), fill='#2A2A2A'), Part(oval(0.95, 0.32, 0.30, 0.30), fill='#2A2A2A'),
            Part(oval(-0.95, 0.32, 0.12, 0.12), fill='#BDBDBD', ow=0.02, rim=False), Part(oval(0.95, 0.32, 0.12, 0.12), fill='#BDBDBD', ow=0.02, rim=False)]


def chariot(t=0.0):
    out = [Part(P([(-1.0, 0.30), (-1.05, -0.55), (0.30, -0.55), (0.75, 0.30)], tension=0.3), fill='#C0392B', grad=(-0.55, 0.3, 1.15, 0.8))]
    for y in (-0.30, -0.10):
        out.append(Part(line((-1.0, y), (0.55, y)), ow=0.05, rim=False, color='#FFFFFF', ink=False))
    out.append(Part(oval(-0.25, 0.45, 0.48, 0.48), fill='#8A6A45'))
    for k in range(4):
        a = k * math.pi / 4 + t * 4
        out.append(Part(line((-0.25 - math.cos(a) * 0.42, 0.45 - math.sin(a) * 0.42), (-0.25 + math.cos(a) * 0.42, 0.45 + math.sin(a) * 0.42)),
                        ow=0.04, rim=False))
    out.append(Part(line((0.70, 0.10), (1.55, -0.05)), tube=0.07, fill='#6E5236'))
    return out


def stage(t=0.0):
    out = [Part(_rr(-2.2, 0.85, 2.2, 1.15, 0.03), fill='#7A5434')]
    for sx in (-1, 1):
        cur = P([(sx * 2.2, -1.3), (sx * 1.25, -1.3), (sx * 1.40, -0.2), (sx * 1.15, 0.85), (sx * 2.2, 0.85)], tension=0.5)
        out.append(Part(cur, fill='#8E1F2A', grad=(-1.3, 0.85, 1.15, 0.75)))
    out.append(Part(_rr(-2.25, -1.45, 2.25, -1.15, 0.03), fill='#6E1720'))
    return out


def eagle_standard(t=0.0):
    out = [Part(line((0.0, -0.45), (0.0, 1.6)), tube=0.08, fill='#6E5236')]
    out.append(Part(_rr(-0.45, -0.55, 0.45, -0.38, 0.03), fill='#C9A050'))
    wing = P([(0.0, -0.95), (-0.95, -1.40), (-0.70, -0.95), (-0.35, -0.70), (0.35, -0.70), (0.70, -0.95), (0.95, -1.40)], tension=0.5)
    out.append(Part(wing, fill='#E8B83A', grad=(-1.4, -0.7, 1.2, 0.85)))
    out.append(Part(oval(0.0, -1.05, 0.17, 0.22), fill='#E8B83A'))
    return out


def bed(t=0.0):
    return [Part(_rr(-1.6, -0.05, 1.6, 0.45, 0.06), fill='#8A6A45'), Part(_rr(-1.55, -0.30, 1.40, 0.05, 0.08), fill='#E8E2D4'),
            Part(_rr(-1.75, -0.90, -1.55, 0.80, 0.04), fill='#6E5236'), Part(_rr(1.55, -0.55, 1.75, 0.80, 0.04), fill='#6E5236'),
            Part(_rr(-1.45, -0.55, -0.85, -0.25, 0.12), fill='#FFFFFF')]


def door(t=0.0, broken=False):
    out = [Part(_rr(-0.7, -1.2, 0.7, 1.2, 0.05), fill='#7A5434', grad=(-1.2, 1.2, 1.1, 0.85))]
    for x in (-0.25, 0.25):
        out.append(Part(line((x, -1.15), (x, 1.15)), ow=0.035, rim=False, color='#5A3B26', ink=False))
    out.append(Part(oval(0.48, 0.05, 0.07, 0.07), fill='#C9A050', ow=0.03, rim=False))
    if broken:
        out.append(Part(poly([(-0.2, -0.3), (0.05, 0.0), (-0.1, 0.2), (0.25, 0.55)]), ow=0.05, rim=False))
    return out


def shovel(t=0.0):
    return [Part(line((0.0, -1.3), (0.0, 0.35)), tube=0.09, fill='#8A6A45'),
            Part(P([(-0.38, 0.30), (0.38, 0.30), (0.30, 1.0), (0.0, 1.25), (-0.30, 1.0)], tension=0.5), fill='#9AA3AD'),
            Part(_rr(-0.25, -1.45, 0.25, -1.25, 0.06), fill='#5A3B26')]


def roof_tile(t=0.0):
    p = skia.Path(); p.moveTo(-1.0, 0.4); p.cubicTo(-1.0, -0.7, 1.0, -0.7, 1.0, 0.4); p.lineTo(0.75, 0.4); p.cubicTo(0.75, -0.4, -0.75, -0.4, -0.75, 0.4); p.close()
    return [Part(p, fill='#B0563E', grad=(-0.6, 0.4, 1.15, 0.8))]


def pedestal(t=0.0):
    return [Part(_rr(-0.9, -0.3, 0.9, 0.3, 0.03), fill='#B7B2A8', grad=(-0.3, 0.3, 1.1, 0.85)), Part(_rr(-1.05, 0.3, 1.05, 0.5, 0.03), fill='#9A958B')]


def icon(t=0.0, kind='x'):
    if kind == 'x':
        return [Part(line((-0.8, -0.8), (0.8, 0.8)), tube=0.28, fill='#E0393E'), Part(line((0.8, -0.8), (-0.8, 0.8)), tube=0.28, fill='#E0393E')]
    if kind == 'check':
        return [Part(line((-0.8, 0.0), (-0.2, 0.6)), tube=0.28, fill='#4CAF50'), Part(line((-0.2, 0.6), (0.9, -0.7)), tube=0.28, fill='#4CAF50')]
    if kind == 'heart':
        p = skia.Path(); p.moveTo(0, 0.9); p.cubicTo(-1.4, -0.1, -0.6, -1.2, 0, -0.45); p.cubicTo(0.6, -1.2, 1.4, -0.1, 0, 0.9); p.close()
        return [Part(p, fill='#E0393E', grad=(-1, 0.9, 1.15, 0.85))]
    if kind == 'skull':
        return [Part(P([(-0.75, 0.15), (-0.80, -0.40), (-0.40, -0.85), (0.40, -0.85), (0.80, -0.40), (0.75, 0.15), (0.40, 0.40),
                        (0.40, 0.75), (-0.40, 0.75), (-0.40, 0.40)], tension=0.6), fill='#F2EFE6'),
                Part(oval(-0.32, -0.15, 0.20, 0.22), fill=INK, ow=0, rim=False), Part(oval(0.32, -0.15, 0.20, 0.22), fill=INK, ow=0, rim=False),
                Part(poly([(0.0, 0.10), (-0.08, 0.28), (0.08, 0.28)]), fill=INK, ow=0, rim=False)]
    if kind == 'question':
        return [Part(cubic((-0.45, -0.45), (-0.45, -1.1), (0.6, -1.1), (0.45, -0.4)), ow=0.0, tube=0.22, fill='#F2C94C'),
                Part(cubic((0.45, -0.4), (0.35, -0.05), (0.0, 0.0), (0.0, 0.35)), tube=0.22, fill='#F2C94C'),
                Part(oval(0.0, 0.85, 0.16, 0.16), fill='#F2C94C')]
    if kind == 'recycle':
        out = []
        for k in range(3):
            a = math.radians(k * 120 - 90)
            b = a + math.radians(95)
            p = skia.Path(); p.arcTo(skia.Rect(-0.9, -0.9, 0.9, 0.9), math.degrees(a), 95, True)
            out.append(Part(p, ow=0.0, tube=0.22, fill='#4CAF50'))
            tip = (math.cos(b) * 0.9, math.sin(b) * 0.9)
            out.append(Part(poly([(tip[0] + math.cos(b + 1.57) * 0.0 + math.cos(b) * 0.25, tip[1] + math.sin(b) * 0.25),
                                  (tip[0] - math.cos(b) * 0.25, tip[1] - math.sin(b) * 0.25),
                                  (tip[0] + math.cos(b + 1.57) * 0.32, tip[1] + math.sin(b + 1.57) * 0.32)]), fill='#4CAF50', ow=0.04))
        return out
    if kind == 'bang':
        return [Part(_rr(-0.16, -1.0, 0.16, 0.35, 0.12), fill='#E0393E'), Part(oval(0.0, 0.75, 0.17, 0.17), fill='#E0393E')]
    raise ValueError(kind)


PROPS = dict(longship=longship, turtle_ship=turtle_ship, jp_ship=jp_ship, coin=coin, gold_pile=gold_pile,
             crown=crown_prop, sword=sword, arrow=arrow, shield=shield, book=book, tombstone=tombstone, coffin=coffin,
             wreath=wreath, house=house, flames=flames, jail=jail_bars, chain=chain, bridge=bridge, barrel=barrel,
             sun=sun, dust=dust, salt=salt_shaker, drum=drum, plate=plate, cup=cup, tv=tv, car=car, chariot=chariot,
             stage=stage, eagle=eagle_standard, bed=bed, door=door, shovel=shovel, tile=roof_tile, pedestal=pedestal,
             icon=icon)


def draw_prop(canvas, name, x, y, size, t=0.0, rot=0.0, alpha=255, flip=False, rim=True, **kw):
    parts = PROPS[name](t=t, **kw)
    render_parts(canvas, parts, x, y, size, flip=flip, alpha=alpha, show_rim=rim, rot=rot)
