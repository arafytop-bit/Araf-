"""Round-head character rig in the reference cartoon style (user-supplied screenshots).

Style rules measured from the references (1080p frames):
- big white circle head, inked black outline ~0.06 R, head = 42-49 % of total height
- eyes: two small black shapes (~0.12 R) set close together, shifted toward the look
  direction; moods via lidded / slanted / tearful shapes + thin brows; mouth often absent
- identity carried by hat, hair and outfit; muted earthy palette with soft gradients;
  white mitten hands; tube limbs

Units: head radius R = 1, origin = head centre, y down.
"""
import math
import skia
from .core import paint, catmull_rom_path, rgb

INK = '#151515'
OL = 0.06                 # outline width (measured 0.058-0.065 R)
RIM, RIM_COLOR = 0.02, '#777777'   # light rim so dark clothes read on the black stage
HEAD_FILL = '#F8F8F5'
JITTER = (0.045, 0.0035)  # inked-line wobble: segment length, deviation (R units), fixed seed


def _shade(hexc, k):
    h = hexc.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return '#%02X%02X%02X' % (max(0, min(255, int(r * k))), max(0, min(255, int(g * k))), max(0, min(255, int(b * k))))


# ---------------- outfits / cast ----------------
DETECTIVE = dict(hat='fedora', hat_color='#6A4A38', hat_band='#2A221E', hair=None,
                 top='trench', top_color='#C9A26B', belt='#7D5B3A', tie='#B23A32', shirt='#EFEAE0',
                 pants='#3D414C', shoes='#4A3329', hands='#F8F8F5', look=(0.0, 0.0))
REPORTER = dict(hat='newsboy', hat_color='#6E6A63', hat_band=None, hair=None,
                top='vest', top_color='#EDE7DA', vest='#4E5A6B', belt=None, tie='#8C2E2A', shirt='#EDE7DA',
                pants='#3A3530', shoes='#2E2A27', hands='#F8F8F5', look=(0.0, 0.0))
SLEUTH = dict(hat='beanie', hat_color='#B4442F', hat_band=None, hair=None,
              top='bomber', top_color='#4F5E3E', belt=None, tie=None, shirt='#2B2B2B',
              pants='#2F3440', shoes='#E8E8E8', hands='#F8F8F5', look=(0.0, 0.0))
AGENT = dict(hat='cap', hat_color='#25304B', hat_band=None, cap_text='FBI', cap_text_color='#F2C230', hair=None,
             top='windbreaker', top_color='#25304B', belt=None, tie=None, shirt='#EFEAE0',
             pants='#262A33', shoes='#1E1E1E', hands='#F8F8F5', look=(0.0, 0.0))


def subject(hair='short', hair_color='#2A211C', top='suit', top_color='#5B5E66', tie='#2B2B2B',
            pants='#2E3038', shoes='#2A2420', hat=None, hat_color='#555555'):
    return dict(hat=hat, hat_color=hat_color, hat_band=None, hair=hair, hair_color=hair_color, top=top,
                top_color=top_color, belt=None, tie=tie, shirt='#EFEAE0', pants=pants, shoes=shoes,
                hands='#F8F8F5', look=(0.0, 0.0))


HOST = DETECTIVE


# ---------------- primitives ----------------
class Part:
    __slots__ = ('path', 'fill', 'ow', 'tube', 'rim', 'color', 'cap', 'alpha', 'grad', 'ink')

    def __init__(self, path, fill=None, ow=OL, tube=0.0, rim=True, color=INK, cap='round', alpha=255,
                 grad=None, ink=True):
        self.path, self.fill, self.ow, self.tube, self.rim = path, fill, ow, tube, rim
        self.color, self.cap, self.alpha, self.grad, self.ink = color, cap, alpha, grad, ink


def P(pts, tension=0.9, closed=True):
    return catmull_rom_path(pts, closed=closed, tension=tension)


def oval(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def line(*pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def cubic(p0, c1, c2, p1):
    p = skia.Path()
    p.moveTo(*p0)
    p.cubicTo(c1[0], c1[1], c2[0], c2[1], p1[0], p1[1])
    return p


def quad(p0, c, p1):
    p = skia.Path()
    p.moveTo(*p0)
    p.quadTo(c[0], c[1], p1[0], p1[1])
    return p


def poly(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


# ---------------- face ----------------
EYE_R, EYE_DX = 0.125, 0.155


def _eye_shape(kind, cx, cy, side):
    """side: -1 left eye, +1 right eye (screen)."""
    r = EYE_R
    if kind == 'dot':
        return [Part(oval(cx, cy, r * 0.92, r), fill=INK, ow=0, rim=False)]
    if kind == 'wide':
        return [Part(oval(cx, cy, r * 1.25, r * 1.32), fill=INK, ow=0, rim=False),
                Part(oval(cx + r * 0.45, cy - r * 0.5, r * 0.38, r * 0.38), fill='#FFFFFF', ow=0, rim=False)]
    if kind in ('lid', 'angry', 'sad', 'smug'):
        # half-disc with a cut top edge; slope sets the mood
        slope = {'lid': 0.0, 'angry': -0.55 * side, 'sad': 0.45 * side, 'smug': 0.15 * side}[kind]
        top = cy - (0.15 if kind == 'smug' else 0.02) * r
        p = skia.Path()
        rr = r * 1.15
        p.moveTo(cx - rr, top - slope * rr)
        p.lineTo(cx + rr, top + slope * rr)
        p.arcTo(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr * 0.95), 0, 180, False)
        p.close()
        clip = oval(cx, cy, rr, rr * 0.95)
        out = skia.Op(p, clip, skia.PathOp.kIntersect_PathOp) if hasattr(skia, 'Op') else p
        return [Part(out, fill=INK, ow=0, rim=False)]
    if kind == 'happy':
        return [Part(quad((cx - r, cy + r * 0.3), (cx, cy - r * 1.1), (cx + r, cy + r * 0.3)), ow=0.07, rim=False)]
    if kind == 'closed':
        return [Part(line((cx - r, cy), (cx + r, cy)), ow=0.065, rim=False)]
    if kind == 'x':                        # knocked-out / dead cartoon eyes
        rr = r * 0.95
        return [Part(line((cx - rr, cy - rr), (cx + rr, cy + rr)), ow=0.07, rim=False),
                Part(line((cx - rr, cy + rr), (cx + rr, cy - rr)), ow=0.07, rim=False)]
    raise ValueError(kind)


EXPR = {
    #  name: (eye kind, brows, mouth, extras)
    'neutral': ('dot', None, None, ()),
    'talk': ('dot', None, 'open', ()),
    'talk2': ('dot', None, 'o', ()),
    'smile': ('dot', None, 'smile', ()),
    'grin': ('happy', None, 'grin', ('cheeks',)),
    'smug': ('smug', 'smug', 'smirk', ()),
    'deadpan': ('lid', 'flat', 'line', ()),
    'angry': ('angry', 'angry', None, ()),
    'sad': ('sad', 'sad', 'wavy', ()),
    'cry': ('sad', 'sad', 'grimace', ('tears',)),
    'shock': ('wide', 'up', 'o', ()),
    'nervous': ('dot', 'sad', 'wavy', ('sweat',)),
    'grimace': ('dot', 'angry', 'grimace', ()),
    'evil': ('angry', 'angry', 'evil', ()),
    'skeptic': ('lid', 'skeptic', 'line', ()),
    'sleep': ('closed', None, None, ()),
    'dead': ('closed', None, 'wavy', ()),
    'ko': ('x', None, 'wavy', ()),
    'ko_grin': ('x', None, 'grin', ()),
    'ko_o': ('x', None, 'o', ()),
}

for _k, _v in list(EXPR.items()):            # blink variants: same face, eyes closed
    if _v[0] != 'closed':
        EXPR[_k + '_blink'] = ('closed',) + tuple(_v[1:])


def face_parts(expr, look=(0.0, 0.0)):
    eye, brows, mouth, extras = EXPR[expr]
    fx, fy = look
    ey = fy - 0.02
    parts = []
    for side in (-1, 1):
        parts += _eye_shape(eye, fx + side * EYE_DX, ey, side)
    # brows: thin strokes above the eyes
    if brows:
        for side in (-1, 1):
            cx = fx + side * EYE_DX
            by = ey - 0.27
            if brows == 'angry':
                a, b = (cx - side * 0.12, by + 0.07 * 1), (cx + side * 0.10, by - 0.04)
                a, b = (cx - 0.11, by + (0.06 if side > 0 else -0.04)), (cx + 0.11, by + (-0.04 if side > 0 else 0.06))
            elif brows == 'sad':
                a, b = (cx - 0.11, by + (-0.05 if side > 0 else 0.05)), (cx + 0.11, by + (0.05 if side > 0 else -0.05))
            elif brows == 'up':
                a, b = (cx - 0.10, by - 0.06), (cx + 0.10, by - 0.06)
            elif brows == 'flat':
                a, b = (cx - 0.10, by + 0.04), (cx + 0.10, by + 0.04)
            elif brows == 'smug':
                a, b = (cx - 0.10, by + (0.02 if side < 0 else -0.06)), (cx + 0.10, by + (0.02 if side < 0 else -0.08))
            elif brows == 'skeptic':
                a, b = ((cx - 0.10, by - 0.10), (cx + 0.10, by - 0.14)) if side > 0 else ((cx - 0.10, by + 0.05), (cx + 0.10, by + 0.05))
            parts.append(Part(line(a, b), ow=0.045, rim=False))
    my = ey + 0.33
    if mouth == 'open':
        p = skia.Path(); p.moveTo(fx - 0.12, my - 0.04); p.quadTo(fx, my - 0.07, fx + 0.12, my - 0.04)
        p.cubicTo(fx + 0.11, my + 0.13, fx - 0.11, my + 0.13, fx - 0.12, my - 0.04); p.close()
        parts.append(Part(p, fill=INK, ow=0, rim=False))
    elif mouth == 'o':
        parts.append(Part(oval(fx, my, 0.055, 0.07), fill=INK, ow=0, rim=False))
    elif mouth == 'smile':
        parts.append(Part(quad((fx - 0.13, my - 0.03), (fx, my + 0.10), (fx + 0.13, my - 0.03)), ow=0.045, rim=False))
    elif mouth == 'grin':
        p = skia.Path(); p.moveTo(fx - 0.17, my - 0.05); p.quadTo(fx, my - 0.01, fx + 0.17, my - 0.05)
        p.cubicTo(fx + 0.15, my + 0.17, fx - 0.15, my + 0.17, fx - 0.17, my - 0.05); p.close()
        parts.append(Part(p, fill=INK, ow=0, rim=False))
    elif mouth == 'smirk':
        parts.append(Part(quad((fx - 0.02, my + 0.02), (fx + 0.10, my + 0.05), (fx + 0.17, my - 0.05)), ow=0.04, rim=False))
    elif mouth == 'line':
        parts.append(Part(line((fx - 0.07, my), (fx + 0.07, my)), ow=0.04, rim=False))
    elif mouth == 'wavy':
        p = skia.Path(); p.moveTo(fx - 0.13, my + 0.02); p.cubicTo(fx - 0.07, my - 0.06, fx - 0.02, my + 0.07, fx + 0.03, my)
        p.cubicTo(fx + 0.07, my - 0.05, fx + 0.10, my - 0.02, fx + 0.13, my + 0.02)
        parts.append(Part(p, ow=0.04, rim=False))
    elif mouth == 'grimace':
        rr = skia.Path(); rr.addRRect(skia.RRect.MakeRectXY(skia.Rect(fx - 0.19, my - 0.07, fx + 0.19, my + 0.09), 0.05, 0.05))
        parts.append(Part(rr, fill='#FFFFFF', ow=0.045, rim=False))
        parts.append(Part(line((fx - 0.18, my + 0.01), (fx + 0.18, my + 0.01)), ow=0.03, rim=False, cap='butt'))
    elif mouth == 'evil':
        p = skia.Path(); p.moveTo(fx - 0.18, my - 0.03); p.quadTo(fx, my + 0.05, fx + 0.20, my - 0.07)
        p.quadTo(fx + 0.04, my + 0.18, fx - 0.18, my - 0.03); p.close()
        parts.append(Part(p, fill=INK, ow=0, rim=False))
    for ex in extras:
        if ex == 'tears':
            for side in (-1, 1):
                cx = fx + side * (EYE_DX + 0.05)
                d = P([(cx, ey + 0.08), (cx + 0.05, ey + 0.20), (cx, ey + 0.26), (cx - 0.05, ey + 0.20)], tension=0.8)
                parts.append(Part(d, fill='#9ED8FF', ow=0.03, rim=False))
        elif ex == 'sweat':
            d = P([(0.62, -0.42), (0.70, -0.24), (0.62, -0.16), (0.54, -0.24)], tension=0.8)
            parts.append(Part(d, fill='#9ED8FF', ow=0.035, rim=False))
        elif ex == 'cheeks':
            for side in (-1, 1):
                cx = fx + side * 0.36
                parts.append(Part(line((cx - 0.03, my - 0.02), (cx + 0.02, my - 0.08)), ow=0.03, rim=False))
    return parts


# ---------------- hats & hair ----------------
def hat_parts(st):
    h = st.get('hat')
    c = st.get('hat_color', '#555555')
    out = []
    if h == 'fedora':
        crown = P([(-0.78, -0.60), (-0.86, -0.98), (-0.74, -1.30), (-0.40, -1.44), (-0.14, -1.33), (0.0, -1.27),
                   (0.14, -1.33), (0.40, -1.44), (0.74, -1.30), (0.86, -0.98), (0.78, -0.60)], tension=0.8)
        out.append(Part(crown, fill=c, grad=(-1.44, -0.6, 1.12, 0.86)))
        out.append(Part(poly([(-0.84, -0.86), (0.84, -0.86), (0.80, -0.63), (-0.80, -0.63)]), fill=st.get('hat_band', '#222')))
        out.append(Part(line((-0.62, -1.24), (-0.71, -0.96)), ow=0.06, rim=False, color=_shade(c, 1.35), ink=False))
        out.append(Part(line((0.0, -1.27), (0.0, -1.12)), ow=0.035, rim=False))
        brim = P([(-1.32, -0.50), (-1.00, -0.64), (-0.50, -0.70), (0.0, -0.71), (0.50, -0.70), (1.00, -0.64),
                  (1.32, -0.50), (1.12, -0.44), (0.60, -0.51), (0.0, -0.53), (-0.60, -0.51), (-1.12, -0.44)], tension=0.8)
        out.append(Part(brim, fill=_shade(c, 0.92)))
    elif h == 'newsboy':
        dome = P([(-1.05, -0.45), (-1.0, -0.88), (-0.60, -1.22), (0.0, -1.30), (0.68, -1.20), (1.08, -0.88),
                  (1.12, -0.52), (0.6, -0.56), (0.0, -0.60), (-0.6, -0.56)], tension=0.85)
        out.append(Part(dome, fill=c, grad=(-1.3, -0.45, 1.12, 0.85)))
        for x in (-0.45, 0.0, 0.45):
            out.append(Part(quad((x * 0.6, -1.24), (x * 1.1, -0.95), (x * 1.2, -0.58)), ow=0.03, rim=False))
        out.append(Part(oval(0.0, -1.27, 0.07, 0.05), fill=_shade(c, 0.85), ow=0.035, rim=False))
        brim = P([(-0.70, -0.58), (0.0, -0.66), (0.70, -0.58), (0.60, -0.44), (0.0, -0.40), (-0.60, -0.44)], tension=0.8)
        out.append(Part(brim, fill=_shade(c, 0.8)))
    elif h == 'beanie':
        dome = P([(-1.04, -0.42), (-0.98, -0.86), (-0.58, -1.24), (0.0, -1.34), (0.58, -1.24), (0.98, -0.86),
                  (1.04, -0.42)], tension=0.85)
        out.append(Part(dome, fill=c, grad=(-1.34, -0.42, 1.1, 0.85)))
        for x in (-0.6, -0.3, 0.0, 0.3, 0.6):
            out.append(Part(line((x, -1.18 + abs(x) * 0.25), (x * 1.08, -0.62)), ow=0.025, rim=False, color=_shade(c, 0.75), ink=False))
        band = P([(-1.07, -0.66), (0.0, -0.74), (1.07, -0.66), (1.08, -0.38), (0.0, -0.44), (-1.08, -0.38)], tension=0.6)
        out.append(Part(band, fill=_shade(c, 0.9)))
    elif h == 'cap':
        dome = P([(-1.04, -0.42), (-0.98, -0.86), (-0.58, -1.22), (0.0, -1.32), (0.58, -1.22), (0.98, -0.86),
                  (1.04, -0.42), (0.0, -0.50)], tension=0.85)
        out.append(Part(dome, fill=c, grad=(-1.32, -0.42, 1.15, 0.85)))
        brim = P([(-0.82, -0.47), (0.0, -0.55), (0.82, -0.47), (0.70, -0.30), (0.0, -0.26), (-0.70, -0.30)], tension=0.8)
        out.append(Part(brim, fill=_shade(c, 0.8)))
    elif h:
        from .costumes import hat_extra
        out = hat_extra(h, st)
    return out


def hair_parts(st):
    h = st.get('hair')
    c = st.get('hair_color', '#2A211C')
    if h == 'slick':
        return [Part(P([(-1.03, -0.20), (-0.99, -0.64), (-0.70, -0.94), (-0.25, -1.07), (0.30, -1.05), (0.76, -0.88),
                        (1.01, -0.55), (1.04, -0.20), (0.88, -0.38), (0.55, -0.56), (0.10, -0.64), (-0.35, -0.60),
                        (-0.76, -0.46)], tension=0.85), fill=c)]
    if h == 'short':
        return [Part(P([(-1.03, -0.30), (-0.96, -0.74), (-0.60, -1.02), (0.0, -1.10), (0.60, -1.02), (0.96, -0.74),
                        (1.03, -0.30), (0.75, -0.50), (0.35, -0.62), (0.0, -0.66), (-0.35, -0.62), (-0.75, -0.50)],
                       tension=0.85), fill=c)]
    return []


# ---------------- body & clothes ----------------
SH = 0.50
ARMS = {
    'idle':   [(((-SH, 1.04), (-0.78, 1.38), (-0.86, 1.88), (-0.80, 2.22)), False),
               (((SH, 1.04), (0.78, 1.38), (0.86, 1.88), (0.80, 2.22)), False)],
    'hips':   [(((-SH, 1.04), (-1.10, 1.24), (-1.10, 1.86), (-0.70, 1.90)), False),
               (((SH, 1.04), (1.10, 1.24), (1.10, 1.86), (0.70, 1.90)), False)],
    'wave':   [(((-SH, 1.04), (-0.78, 1.38), (-0.86, 1.88), (-0.80, 2.22)), False),
               (((SH, 1.04), (0.98, 1.42), (1.30, 1.28), (1.38, 0.72)), False)],
    'point':  [(((-SH, 1.04), (-0.78, 1.38), (-0.86, 1.88), (-0.80, 2.22)), False),
               (((SH, 1.04), (0.95, 1.12), (1.30, 1.04), (1.62, 0.92)), False)],
    'chin':   [(((-SH, 1.04), (-1.04, 1.62), (-0.64, 1.78), (-0.24, 1.02)), True),
               (((SH, 1.04), (0.78, 1.38), (0.86, 1.88), (0.80, 2.22)), False)],
    'shrug':  [(((-SH, 1.04), (-0.96, 1.52), (-1.28, 1.52), (-1.40, 1.08)), False),
               (((SH, 1.04), (0.96, 1.52), (1.28, 1.52), (1.40, 1.08)), False)],
    'cheeks': [(((-SH, 1.04), (-1.16, 1.24), (-1.16, 0.72), (-0.92, 0.40)), True),
               (((SH, 1.04), (1.16, 1.24), (1.16, 0.72), (0.92, 0.40)), True)],
    'inspect': [(((-SH, 1.04), (-0.78, 1.38), (-0.86, 1.88), (-0.80, 2.22)), False),
                (((SH, 1.04), (1.06, 1.42), (1.22, 1.08), (1.00, 0.78)), True)],
}


def arms_for(pose, phase=0.0):
    if pose == 'walk':
        s = math.sin(phase)
        return [(((-SH, 1.04), (-0.74 - 0.08 * s, 1.38), (-0.74 - 0.27 * s, 1.84), (-0.66 - 0.36 * s, 2.16)), False),
                (((SH, 1.04), (0.74 - 0.08 * s, 1.38), (0.74 - 0.27 * s, 1.84), (0.66 - 0.36 * s, 2.16)), False)]
    return ARMS[pose]


def legs_for(pose, phase=0.0, hip=2.40, foot=3.10):
    if pose == 'walk':
        s = math.sin(phase)
        return [((-0.26, hip), (-0.28 + 0.26 * s, foot)), ((0.26, hip), (0.28 - 0.26 * s, foot))]
    return [((-0.27, hip), (-0.29, foot)), ((0.27, hip), (0.29, foot))]


def top_parts(st):
    t, c = st.get('top', 'tunic'), st.get('top_color', '#888888')
    out = []
    if t == 'trench':
        out.append(Part(P([(-0.30, 0.76), (-0.60, 0.88), (-0.52, 1.06), (-0.22, 0.95)], tension=0.6), fill=_shade(c, 0.95)))
        out.append(Part(P([(0.30, 0.76), (0.60, 0.88), (0.52, 1.06), (0.22, 0.95)], tension=0.6), fill=_shade(c, 0.95)))
        body = P([(-0.52, 0.90), (0.52, 0.90), (0.64, 1.28), (0.70, 1.92), (0.84, 2.64), (-0.84, 2.64), (-0.70, 1.92),
                  (-0.64, 1.28)], tension=0.45)
        out.append(Part(body, fill=c, grad=(0.9, 2.64, 1.05, 0.84)))
        out.append(Part(poly([(-0.23, 0.92), (0.23, 0.92), (0.0, 1.48)]), fill=st.get('shirt', '#EFEAE0'), ow=0.045))
        if st.get('tie'):
            out.append(Part(P([(-0.065, 1.0), (0.065, 1.0), (0.10, 1.38), (0.0, 1.50), (-0.10, 1.38)], tension=0.3),
                            fill=st['tie'], ow=0.04))
        for sx in (-1, 1):
            out.append(Part(poly([(sx * 0.23, 0.92), (sx * 0.54, 0.94), (sx * 0.46, 1.38), (sx * 0.02, 1.64)]),
                            fill=_shade(c, 1.04), ow=0.05))
        out.append(Part(poly([(-0.71, 1.80), (0.71, 1.80), (0.73, 1.97), (-0.73, 1.97)]), fill=st.get('belt', '#5A3B26'), ow=0.045))
        rr = skia.Path(); rr.addRRect(skia.RRect.MakeRectXY(skia.Rect(-0.30, 1.78, -0.08, 1.99), 0.03, 0.03))
        out.append(Part(rr, ow=0.045, rim=False, color='#C9A050', ink=False))
        out.append(Part(line((-0.19, 1.885), (-0.06, 1.885)), ow=0.035, rim=False, color='#C9A050', ink=False))
        out.append(Part(line((0.0, 1.99), (0.0, 2.62)), ow=0.04, rim=False))
        for y in (2.16, 2.40):
            for sx in (-1, 1):
                out.append(Part(oval(sx * 0.18, y, 0.037, 0.037), fill=INK, ow=0, rim=False))
        for sx in (-1, 1):
            out.append(Part(line((sx * 0.60, 2.26), (sx * 0.34, 2.21)), ow=0.035, rim=False))
    elif t in ('suit', 'windbreaker', 'vest', 'bomber'):
        hem = {'suit': 2.46, 'windbreaker': 2.42, 'vest': 2.46, 'bomber': 2.38}[t]
        body = P([(-0.50, 0.90), (0.50, 0.90), (0.60, 1.25), (0.64, hem), (-0.64, hem), (-0.60, 1.25)], tension=0.4)
        base = st.get('shirt', '#EFEAE0') if t == 'vest' else c
        out.append(Part(body, fill=base, grad=(0.9, hem, 1.05, 0.86)))
        if t == 'suit':
            out.append(Part(poly([(-0.22, 0.92), (0.22, 0.92), (0.0, 1.45)]), fill=st.get('shirt', '#EFEAE0'), ow=0.045))
            if st.get('tie'):
                out.append(Part(P([(-0.06, 1.0), (0.06, 1.0), (0.09, 1.32), (0.0, 1.42), (-0.09, 1.32)], tension=0.3),
                                fill=st['tie'], ow=0.04))
            for sx in (-1, 1):
                out.append(Part(poly([(sx * 0.22, 0.92), (sx * 0.50, 0.94), (sx * 0.40, 1.30), (sx * 0.02, 1.58)]),
                                fill=_shade(c, 1.06), ow=0.05))
            out.append(Part(line((0.0, 1.58), (0.0, hem - 0.02)), ow=0.04, rim=False))
            out.append(Part(oval(0.08, 1.80, 0.035, 0.035), fill=INK, ow=0, rim=False))
        elif t == 'windbreaker':
            out.append(Part(P([(-0.32, 0.86), (0.32, 0.86), (0.26, 1.04), (0.0, 1.10), (-0.26, 1.04)], tension=0.6),
                            fill=_shade(c, 1.12)))
            out.append(Part(line((0.0, 1.10), (0.0, hem - 0.02)), ow=0.035, rim=False, color='#B9B9B9', ink=False))
            out.append(Part(poly([(-0.64, hem - 0.14), (0.64, hem - 0.14), (0.64, hem), (-0.64, hem)]),
                            fill=_shade(c, 0.85), ow=0.04))
        elif t == 'vest':
            out.append(Part(P([(-0.16, 0.92), (0.16, 0.92), (0.0, 1.10)], tension=0.4), fill=st.get('shirt', '#EFEAE0'), ow=0.04))
            if st.get('tie'):
                out.append(Part(P([(-0.05, 1.0), (0.05, 1.0), (0.07, 1.28), (0.0, 1.36), (-0.07, 1.28)], tension=0.3),
                                fill=st['tie'], ow=0.035))
            for sx in (-1, 1):
                out.append(Part(poly([(sx * 0.14, 0.96), (sx * 0.54, 1.00), (sx * 0.62, hem), (sx * 0.06, hem),
                                      (sx * 0.06, 1.46)]), fill=st.get('vest', '#4E5A6B'), ow=0.05))
                out.append(Part(oval(sx * 0.10, 1.62 + 0.0, 0.03, 0.03), fill=INK, ow=0, rim=False))
                out.append(Part(oval(sx * 0.10, 1.88, 0.03, 0.03), fill=INK, ow=0, rim=False))
        elif t == 'bomber':
            out.append(Part(P([(-0.34, 0.86), (0.34, 0.86), (0.28, 1.06), (0.0, 1.12), (-0.28, 1.06)], tension=0.6),
                            fill='#3A2E25'))
            out.append(Part(line((0.0, 1.12), (0.0, hem - 0.02)), ow=0.035, rim=False, color='#C8C8C8', ink=False))
            out.append(Part(poly([(-0.64, hem - 0.16), (0.64, hem - 0.16), (0.64, hem), (-0.64, hem)]),
                            fill='#3A2E25', ow=0.04))
            out.append(Part(poly([(0.24, 1.30), (0.46, 1.30), (0.46, 1.42), (0.24, 1.42)]), fill=_shade(c, 0.8), ow=0.03, rim=False))
    else:
        from .costumes import top_extra
        out = top_extra(t, st)
    return out


def magnifier_parts(look=(0.0, 0.0)):
    fx, fy = look
    lc = (fx + EYE_DX + 0.03, fy - 0.03)
    out = [Part(line((lc[0] + 0.24, lc[1] + 0.27), (1.00, 0.78)), tube=0.10, fill='#5A3B2A')]
    out.append(Part(oval(lc[0], lc[1], 0.36, 0.36), fill='#3B3E45', ow=OL))
    out.append(Part(oval(lc[0], lc[1], 0.29, 0.29), fill='#F8F8F5', ow=0.035, rim=False))
    # magnified eye seen through the lens
    out.append(Part(oval(lc[0] - 0.02, lc[1] + 0.01, EYE_R * 1.9, EYE_R * 2.05), fill=INK, ow=0, rim=False))
    out.append(Part(oval(lc[0] + 0.05, lc[1] - 0.08, 0.06, 0.06), fill='#FFFFFF', ow=0, rim=False))
    out.append(Part(oval(lc[0], lc[1], 0.29, 0.29), fill='#BFE3FF', ow=0, rim=False, alpha=60))
    out.append(Part(quad((lc[0] - 0.20, lc[1] - 0.05), (lc[0] - 0.17, lc[1] - 0.19), (lc[0] - 0.04, lc[1] - 0.22)),
                    ow=0.045, rim=False, color='#FFFFFF', ink=False))
    return out


# ---------------- assemble & draw ----------------
def render_parts(canvas, order, cx, cy, R, flip=False, alpha=255, show_rim=True, rot=0.0):
    """Draw Part lists in the inked style (shared by characters and props)."""
    canvas.save()
    canvas.translate(cx, cy)
    if rot:
        canvas.rotate(rot)
    canvas.scale(-R if flip else R, R)
    if alpha < 255:
        canvas.saveLayerAlpha(None, int(alpha))
    jitter = skia.DiscretePathEffect.Make(JITTER[0], JITTER[1], 7)
    if show_rim:
        for p in order:
            if not p.rim:
                continue
            if p.tube:
                canvas.drawPath(p.path, paint(RIM_COLOR, stroke=p.tube + 2 * OL + 2 * RIM))
            else:
                if p.fill is not None:
                    canvas.drawPath(p.path, paint(RIM_COLOR))
                canvas.drawPath(p.path, paint(RIM_COLOR, stroke=max(p.ow, OL) + 2 * RIM))
    for p in order:
        if p.tube:
            ip = paint(INK, stroke=p.tube + 2 * OL)
            ip.setPathEffect(jitter)
            canvas.drawPath(p.path, ip)
            canvas.drawPath(p.path, paint(p.fill, stroke=p.tube))
            continue
        if p.fill is not None:
            if p.grad:
                y0, y1, k0, k1 = p.grad
                sh = skia.GradientShader.MakeLinear(points=[(0, y0), (0, y1)],
                                                    colors=[rgb(_shade(p.fill, k0)), rgb(_shade(p.fill, k1))])
                canvas.drawPath(p.path, paint('#FFFFFF', shader=sh, alpha=p.alpha))
            else:
                canvas.drawPath(p.path, paint(p.fill, alpha=p.alpha))
        if p.ow > 0:
            sp = paint(p.color, stroke=p.ow, cap=p.cap)
            if p.ink:
                sp.setPathEffect(jitter)
            canvas.drawPath(p.path, sp)
    if alpha < 255:
        canvas.restore()
    canvas.restore()


def draw_character(canvas, cx, cy, R, pose='idle', expr='talk', pal=HOST, flip=False, bob=(0.0, 0.0),
                   phase=0.0, alpha=255, show_rim=True, look=None, glint=False, rot=0.0):
    """Draw a round-head character with head centre (cx, cy) and head radius R (px)."""
    from .costumes import hair_extra, facial_hair, cape_parts
    st = pal
    lk = look if look is not None else st.get('look', (0.0, 0.0))
    back, mid, head, front = [], [], [], []
    top = st.get('top', 'tunic')
    hip = {'trench': 2.56, 'robe': 2.60, 'toga': 2.45}.get(top, 2.40)
    back += cape_parts(st)
    for a, b in legs_for(pose, phase, hip=hip):
        back.append(Part(line(a, b), tube=0.30, fill=st.get('pants', '#3D414C')))
    for a, b in legs_for(pose, phase, hip=hip):
        sx = -1 if b[0] < 0 else 1
        shoe = P([(b[0] - 0.17 + 0.05 * sx, b[1] + 0.12), (b[0] - 0.12 + 0.04 * sx, b[1] - 0.04),
                  (b[0] + 0.12 * sx + 0.05 * sx, b[1] - 0.03), (b[0] + 0.25 * sx + 0.04 * sx, b[1] + 0.07),
                  (b[0] + 0.20 * sx + 0.04 * sx, b[1] + 0.14)], tension=0.75)
        back.append(Part(shoe, fill=st.get('shoes', '#3A3A3A'), grad=(b[1] - 0.05, b[1] + 0.15, 1.15, 0.9)))
    sleeve = st.get('sleeve') or {'vest': st.get('shirt', '#EFEAE0'), 'athlete': HEAD_FILL}.get(top, st.get('top_color', '#888'))
    hands_mid = []
    for pts, infront in arms_for(pose, phase):
        tube = Part(cubic(*pts), tube=0.27, fill=sleeve)
        hx, hy = pts[-1]
        hand = Part(oval(hx, hy, 0.16, 0.15), fill=st.get('hands', '#F8F8F5'))
        if infront:
            front += [tube, hand]
        else:
            back.append(tube)
            hands_mid.append(hand)
    mid += top_parts(st)
    mid += hands_mid
    bx, by = bob
    h = st.get('hair')
    hb, hf = ([], hair_parts(st)) if h in ('slick', 'short', None) else hair_extra(h, st.get('hair_color', '#2A211C'))
    hp = skia.Path(); hp.addCircle(0, 0, 1.0)
    head += hb
    head.append(Part(hp, fill=HEAD_FILL))
    head += hf
    head += face_parts(expr, lk)
    if st.get('facial'):
        head += facial_hair(st['facial'], st.get('facial_color', st.get('hair_color', '#2A211C')))
    hats = hat_parts(st)
    for p in head + hats:
        p.path.offset(bx, by)
    if pose == 'inspect':
        front += magnifier_parts((lk[0] + bx, lk[1] + by))
    order = back + mid + head + hats + front
    render_parts(canvas, order, cx, cy, R, flip=flip, alpha=alpha, show_rim=show_rim, rot=rot)
    if st.get('cap_text') and not rot:
        from .text import font
        f = font(0.30 * R)
        tw = f.measureText(st['cap_text'])
        canvas.drawString(st['cap_text'], cx + (bx * R) - tw / 2, cy + (-0.82 + by) * R, f,
                          paint(st['cap_text_color'], alpha=alpha))


# framing (same scales as the format)
R_NORMAL, R_ZOOM, R_PIP = 182.0, 277.0, 87.0
NORMAL_CENTER, ZOOM_CENTER = (960.0, 430.0), (960.0, 446.0)
