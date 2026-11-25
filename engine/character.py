"""Original character rig for the channel (host "v1" plus supporting cast).

Design language (deliberately different from the analysed source's stick figure):
egg-shaped head, messy spiky hair, big round glasses with expressive brows, blush,
small nose, maroon open mouths with a tongue, caution-tape-yellow hoodie with hood,
drawstrings and pocket, tube sleeves with hands, slate trousers, white sneakers.

Units: head half-width R = 1, origin = head centre, y down. Same framing constants as
the format (normal / punch-in / PIP), so shot templates are unchanged.
"""
import math
import skia
from .core import paint, catmull_rom_path, poly_path

INK = '#141414'          # outline colour
OL = 0.075               # outline width
RIM = 0.02               # light rim (per side) so dark lines read on the black stage
RIM_COLOR = '#8E8E8E'

# ---------------- cast presets ----------------
HOST = dict(skin='#FBF6EE', hair='messy', hair_color='#2B1F1B', glasses=True, blush=True,
            top='hoodie', top_color='#FFC83D', top_shade='#E9A92A', pants='#3A3F4B', shoes='#F4F4F4',
            cap=None)
AGENT = dict(skin='#FBF6EE', hair=None, hair_color='#2B1F1B', glasses=False, blush=False,
             top='jacket', top_color='#1F2B4A', top_shade='#16203A', pants='#1A1E28', shoes='#2A2A2A',
             cap=dict(color='#1F2B4A', text='FBI', text_color='#F2C230'))


def subject(skin='#E7C3A1', hair='short', hair_color='#1E1612', top='tee', top_color='#8A8F99',
            top_shade=None, pants='#2E3440', shoes='#3A3A3A', glasses=False, blush=False, cap=None):
    return dict(skin=skin, hair=hair, hair_color=hair_color, glasses=glasses, blush=blush, top=top,
                top_color=top_color, top_shade=top_shade or top_color, pants=pants, shoes=shoes, cap=cap)


# ---------------- primitives ----------------
class Part:
    __slots__ = ('path', 'fill', 'ow', 'tube', 'rim', 'stroke_color', 'cap', 'alpha')

    def __init__(self, path, fill=None, ow=OL, tube=0.0, rim=True, stroke_color=INK, cap='round', alpha=255):
        # tube>0: path is a centre line drawn as an outlined tube of width `tube`
        self.path, self.fill, self.ow, self.tube = path, fill, ow, tube
        self.rim, self.stroke_color, self.cap, self.alpha = rim, stroke_color, cap, alpha


def _P(pts, closed=True, tension=0.9):
    return catmull_rom_path(pts, closed=closed, tension=tension)


def _oval(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def _line(*pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def _cubic(p0, c1, c2, p1):
    p = skia.Path()
    p.moveTo(*p0)
    p.cubicTo(c1[0], c1[1], c2[0], c2[1], p1[0], p1[1])
    return p


def _quad(p0, c, p1):
    p = skia.Path()
    p.moveTo(*p0)
    p.quadTo(c[0], c[1], p1[0], p1[1])
    return p


# ---------------- head ----------------
HEAD = [(0.0, -1.08), (0.62, -0.99), (0.95, -0.60), (1.0, -0.05), (0.92, 0.50), (0.64, 0.88), (0.0, 1.02),
        (-0.64, 0.88), (-0.92, 0.50), (-1.0, -0.05), (-0.95, -0.60), (-0.62, -0.99)]


def hair_parts(style, color):
    if style == 'messy':   # host: curved dome, three crisp spikes, zig-zag fringe kept above the brows
        p = skia.Path()
        p.moveTo(-1.03, -0.30)
        p.cubicTo(-1.05, -0.70, -0.85, -1.00, -0.52, -1.13)
        for q in [(-0.36, -1.44), (-0.18, -1.20), (0.06, -1.52), (0.24, -1.20), (0.52, -1.36), (0.60, -1.08)]:
            p.lineTo(*q)
        p.cubicTo(0.90, -0.95, 1.05, -0.68, 1.04, -0.30)
        for q in [(0.94, -0.58), (0.72, -0.72), (0.52, -0.60), (0.32, -0.78), (0.12, -0.62), (-0.08, -0.80),
                  (-0.30, -0.64), (-0.52, -0.80), (-0.74, -0.62), (-0.94, -0.58)]:
            p.lineTo(*q)
        p.close()
        return [Part(p, fill=color)]
    if style == 'short':
        pts = [(-1.03, -0.30), (-0.98, -0.75), (-0.66, -1.07), (-0.2, -1.17), (0.3, -1.15), (0.72, -1.0),
               (0.99, -0.70), (1.03, -0.30), (0.80, -0.56), (0.40, -0.70), (0.0, -0.74), (-0.42, -0.70), (-0.82, -0.56)]
        return [Part(_P(pts), fill=color)]
    if style == 'slick':   # 1950s slicked back with side part
        pts = [(-1.04, -0.15), (-1.03, -0.62), (-0.82, -0.98), (-0.40, -1.17), (0.15, -1.17), (0.62, -1.02),
               (0.95, -0.68), (1.04, -0.25), (0.90, -0.45), (0.66, -0.64), (0.22, -0.76), (-0.12, -0.73),
               (-0.44, -0.64), (-0.80, -0.46), (-0.96, -0.24)]
        return [Part(_P(pts), fill=color)]
    if style == 'buzz':
        pts = [(-1.0, -0.40), (-0.88, -0.85), (-0.45, -1.10), (0.0, -1.14), (0.45, -1.10), (0.88, -0.85),
               (1.0, -0.40), (0.6, -0.72), (0.0, -0.82), (-0.6, -0.72)]
        return [Part(_P(pts), fill=color)]
    raise ValueError(style)


def cap_parts(cap):
    """Forward-facing cap (agents), brim pointing left."""
    dome = [(-1.07, -0.34), (-0.95, -0.80), (-0.55, -1.13), (0.0, -1.25), (0.55, -1.13), (0.95, -0.80),
            (1.07, -0.34), (0.60, -0.43), (0.0, -0.47), (-0.60, -0.43)]
    brim = [(-0.55, -0.46), (-1.10, -0.50), (-1.58, -0.42), (-1.56, -0.28), (-1.08, -0.27), (-0.58, -0.33)]
    return [Part(_P(brim, tension=0.8), fill=cap['color']), Part(_P(dome, tension=0.8), fill=cap['color'])]


GL_L, GL_R, GL_RAD = (-0.38, -0.12), (0.38, -0.12), 0.30


def face_parts(expr, st, look=(0.0, 0.0), glint=False):
    parts = []
    glasses = st.get('glasses')
    lx, ly = look
    ex = 0.38 if glasses else 0.30
    ey = -0.10 if glasses else -0.18
    if glasses:   # lens tint first so it never greys out the eyes
        for c in (GL_L, GL_R):
            parts.append(Part(_oval(c[0], c[1], GL_RAD, GL_RAD), fill='#DCEEFF', ow=0.0, rim=False, alpha=110))
    # ---- eyes ----
    if expr == 'grin':      # happy closed eyes ^ ^
        for sx in (-1, 1):
            parts.append(Part(_quad((sx * ex - 0.09, ey + 0.04), (sx * ex, ey - 0.10), (sx * ex + 0.09, ey + 0.04)),
                              ow=0.055, rim=False))
    else:
        r = {'shock': 0.05, 'o': 0.075}.get(expr, 0.068)
        for sx in (-1, 1):
            parts.append(Part(_oval(sx * ex + lx, ey + ly, r, r * 1.12), fill=INK, ow=0.0, rim=False))
            if expr != 'shock':
                parts.append(Part(_oval(sx * ex + lx + r * 0.38, ey + ly - r * 0.42, r * 0.33, r * 0.33),
                                  fill='#FFFFFF', ow=0.0, rim=False))
    # ---- glasses frames ----
    if glasses:
        for c in (GL_L, GL_R):
            parts.append(Part(_oval(c[0], c[1], GL_RAD, GL_RAD), ow=0.075, rim=False))
        parts.append(Part(_quad((-0.09, -0.16), (0.0, -0.24), (0.09, -0.16)), ow=0.06, rim=False))
        parts.append(Part(_line((-0.68, -0.15), (-0.97, -0.20)), ow=0.06, rim=False))
        parts.append(Part(_line((0.68, -0.15), (0.97, -0.20)), ow=0.06, rim=False))
        if glint:
            for c in (GL_L, GL_R):
                parts.append(Part(_line((c[0] - 0.15, c[1] - 0.02), (c[0] - 0.02, c[1] - 0.17)),
                                  ow=0.06, rim=False, stroke_color='#FFFFFF'))
    # ---- brows (above glasses) ----
    by = -0.52 if glasses else -0.45
    bx0, bx1 = (0.14, 0.56) if glasses else (0.14, 0.44)
    brows = {
        'talk': ((0.0, 0.0), (0.0, 0.0)), 'talk2': ((0.02, -0.02), (0.0, 0.0)), 'neutral': ((0, 0), (0, 0)),
        'o': ((-0.06, -0.04), (-0.06, -0.04)), 'smile': ((-0.02, -0.04), (-0.02, -0.04)),
        'grin': ((-0.04, -0.04), (-0.04, -0.04)), 'grimace': ((-0.06, 0.04), (-0.06, 0.04)),
        'frown': ((-0.08, 0.05), (-0.08, 0.05)), 'skeptic': ((0.03, 0.03), (-0.12, -0.02)),
        'shock': ((-0.12, -0.10), (-0.12, -0.10)), 'evil': ((0.09, -0.05), (0.09, -0.05)),
    }[expr]
    for sx, (din, dout) in zip((-1, 1), brows):     # din: inner end dy, dout: outer end dy
        parts.append(Part(_line((sx * bx0, by + din), (sx * bx1, by + dout - 0.03)), ow=0.085, rim=False))
    # ---- nose ----
    parts.append(Part(_quad((0.03, 0.14), (-0.10, 0.30), (0.05, 0.31)), ow=0.05, rim=False))
    # ---- blush ----
    if st.get('blush'):
        for sx in (-1, 1):
            parts.append(Part(_oval(sx * 0.66, 0.40, 0.14, 0.075), fill='#FF8A8A', ow=0.0, rim=False, alpha=95))
    # ---- mouth ----
    M, T, Wt = '#4A1216', '#E66A6E', '#FFFFFF'
    if expr in ('talk', 'talk2'):
        k = 1.0 if expr == 'talk' else 0.75
        pts = [(-0.24 * k, 0.48), (0.0, 0.45), (0.24 * k, 0.48), (0.20 * k, 0.48 + 0.20 * k), (0.0, 0.48 + 0.27 * k),
               (-0.20 * k, 0.48 + 0.20 * k)]
        parts.append(Part(_P(pts), fill=M, ow=0.06, rim=False))
        parts.append(Part(_oval(0.03, 0.48 + 0.19 * k, 0.12 * k, 0.06 * k), fill=T, ow=0.0, rim=False))
    elif expr == 'o':
        parts.append(Part(_oval(0.0, 0.58, 0.10, 0.12), fill=M, ow=0.06, rim=False))
    elif expr == 'smile':
        p = skia.Path(); p.moveTo(-0.30, 0.46); p.quadTo(0.0, 0.42, 0.30, 0.46); p.cubicTo(0.28, 0.82, -0.28, 0.82, -0.30, 0.46); p.close()
        parts.append(Part(p, fill=M, ow=0.06, rim=False))
        parts.append(Part(_P([(-0.24, 0.48), (0.0, 0.46), (0.24, 0.48), (0.18, 0.55), (-0.18, 0.55)], tension=0.6),
                          fill=Wt, ow=0.0, rim=False))
        parts.append(Part(_oval(0.02, 0.69, 0.11, 0.05), fill=T, ow=0.0, rim=False))
    elif expr == 'grin':
        parts.append(Part(_quad((-0.26, 0.48), (0.0, 0.74), (0.26, 0.48)), ow=0.07, rim=False))
    elif expr == 'grimace':
        rr = skia.Path(); rr.addRRect(skia.RRect.MakeRectXY(skia.Rect(-0.30, 0.44, 0.30, 0.66), 0.09, 0.09))
        parts.append(Part(rr, fill=Wt, ow=0.06, rim=False))
        for x in (-0.10, 0.10):
            parts.append(Part(_line((x, 0.45), (x, 0.65)), ow=0.04, rim=False, cap='butt'))
        parts.append(Part(_line((-0.28, 0.55), (0.28, 0.55)), ow=0.035, rim=False, cap='butt'))
    elif expr == 'frown':
        p = skia.Path(); p.moveTo(-0.24, 0.62); p.cubicTo(-0.12, 0.46, -0.02, 0.70, 0.06, 0.56); p.cubicTo(0.12, 0.48, 0.18, 0.52, 0.24, 0.58)
        parts.append(Part(p, ow=0.065, rim=False))
    elif expr == 'skeptic':
        parts.append(Part(_quad((-0.20, 0.60), (0.06, 0.62), (0.24, 0.48)), ow=0.065, rim=False))
    elif expr == 'shock':
        parts.append(Part(_oval(0.0, 0.62, 0.15, 0.22), fill=M, ow=0.06, rim=False))
        parts.append(Part(_oval(0.0, 0.74, 0.09, 0.07), fill=T, ow=0.0, rim=False))
    elif expr == 'neutral':
        parts.append(Part(_line((-0.14, 0.56), (0.14, 0.56)), ow=0.065, rim=False))
    elif expr == 'evil':
        p = skia.Path(); p.moveTo(-0.30, 0.48); p.quadTo(0.0, 0.58, 0.30, 0.44); p.quadTo(0.04, 0.80, -0.30, 0.48); p.close()
        parts.append(Part(p, fill=M, ow=0.06, rim=False))
    else:
        raise ValueError(expr)
    return parts


# ---------------- body ----------------
SH_L, SH_R = (-0.58, 1.14), (0.58, 1.14)
ARMS = {
    'hips':   [(((-0.58, 1.14), (-1.16, 1.30), (-1.12, 1.78), (-0.70, 1.80)), False),
               (((0.58, 1.14), (1.16, 1.30), (1.12, 1.78), (0.70, 1.80)), False)],
    'wave':   [(((-0.58, 1.14), (-1.12, 1.22), (-1.14, 1.80), (-0.70, 1.86)), False),
               (((0.58, 1.14), (1.02, 1.42), (1.32, 1.30), (1.42, 0.80)), False)],
    'chin':   [(((-0.58, 1.14), (-1.10, 1.58), (-0.70, 1.80), (-0.30, 1.06)), True),
               (((0.58, 1.14), (1.12, 1.22), (1.14, 1.80), (0.70, 1.86)), False)],
    'cheeks': [(((-0.58, 1.14), (-1.18, 1.30), (-1.18, 0.80), (-0.88, 0.48)), True),
               (((0.58, 1.14), (1.18, 1.30), (1.18, 0.80), (0.88, 0.48)), True)],
    'shrug':  [(((-0.58, 1.14), (-1.00, 1.48), (-1.28, 1.46), (-1.42, 1.04)), False),
               (((0.58, 1.14), (1.00, 1.48), (1.28, 1.46), (1.42, 1.04)), False)],
    'point':  [(((-0.58, 1.14), (-1.12, 1.22), (-1.14, 1.80), (-0.70, 1.86)), False),
               (((0.58, 1.14), (1.00, 1.18), (1.32, 1.06), (1.64, 0.96)), False)],
    'nerd':   [(((-0.58, 1.14), (-1.12, 1.22), (-1.14, 1.80), (-0.70, 1.86)), False),       # push glasses up
               (((0.58, 1.14), (1.10, 1.42), (0.72, 0.86), (0.10, 0.02)), True)],
}


def arms_for(pose, phase=0.0):
    if pose == 'walk':
        s = math.sin(phase)
        return [(((-0.58, 1.14), (-0.80 - 0.10 * s, 1.40), (-0.78 - 0.30 * s, 1.66), (-0.66 - 0.40 * s, 1.92)), False),
                (((0.58, 1.14), (0.80 - 0.10 * s, 1.40), (0.78 - 0.30 * s, 1.66), (0.66 - 0.40 * s, 1.92)), False)]
    return ARMS[pose]


def legs_for(pose, phase=0.0):
    if pose == 'walk':
        s = math.sin(phase)
        return [((-0.28, 2.02), (-0.30 + 0.28 * s, 2.72)), ((0.28, 2.02), (0.30 - 0.28 * s, 2.72))]
    return [((-0.30, 2.02), (-0.33, 2.72)), ((0.30, 2.02), (0.33, 2.72))]


def torso_parts(st):
    tc, shade = st['top_color'], st['top_shade']
    parts = []
    body = _P([(-0.62, 0.98), (0.62, 0.98), (0.70, 1.40), (0.72, 2.10), (-0.72, 2.10), (-0.70, 1.40)], tension=0.35)
    parts.append(Part(body, fill=tc))
    if st['top'] == 'hoodie':
        parts.append(Part(_P([(-0.70, 2.00), (0.70, 2.00), (0.72, 2.10), (-0.72, 2.10)], tension=0.2), fill=shade, ow=0.05, rim=False))
        parts.append(Part(_P([(-0.40, 1.64), (0.40, 1.64), (0.48, 1.98), (-0.48, 1.98)], tension=0.25), fill=shade, ow=0.055, rim=False))
    elif st['top'] == 'jacket':
        parts.append(Part(_P([(-0.20, 0.98), (0.20, 0.98), (0.0, 1.42)], tension=0.2), fill='#F2F2F2', ow=0.05, rim=False))
        parts.append(Part(_line((0.0, 1.42), (0.0, 2.08)), ow=0.05, rim=False))
        parts.append(Part(_oval(0.10, 1.62, 0.035, 0.035), fill=INK, ow=0.0, rim=False))
        parts.append(Part(_oval(0.10, 1.84, 0.035, 0.035), fill=INK, ow=0.0, rim=False))
    elif st['top'] == 'suit':
        parts.append(Part(_P([(-0.30, 0.98), (0.30, 0.98), (0.0, 1.46)], tension=0.2), fill='#F2F2F2', ow=0.05, rim=False))
        parts.append(Part(_P([(-0.07, 1.10), (0.07, 1.10), (0.11, 1.75), (0.0, 1.88), (-0.11, 1.75)], tension=0.2),
                          fill='#5A1E22', ow=0.05, rim=False))
    return parts


def hood_parts(st):
    if st['top'] != 'hoodie':
        return []
    hood = _P([(-0.86, 0.80), (-0.40, 0.98), (0.40, 0.98), (0.86, 0.80), (0.70, 1.16), (0.0, 1.30), (-0.70, 1.16)], tension=0.7)
    parts = [Part(hood, fill=st['top_color'])]
    for sx in (-1, 1):
        parts.append(Part(_line((sx * 0.17, 1.12), (sx * 0.19, 1.52)), ow=0.05, rim=False))
        parts.append(Part(_oval(sx * 0.19, 1.55, 0.04, 0.05), fill='#F4F4F4', ow=0.035, rim=False))
    return parts


def draw_character(canvas, cx, cy, R, pose='hips', expr='talk', pal=HOST, flip=False, bob=(0.0, 0.0),
                   phase=0.0, alpha=255, show_rim=True, look=(0.0, 0.0), glint=False):
    """Draw a full character with head centre (cx, cy) and head half-width R (px)."""
    st = pal
    back, mid, head, front = [], [], [], []
    # legs (tubes) + shoes
    for (a, b) in legs_for(pose, phase):
        back.append(Part(_line(a, b), tube=0.26, fill=st['pants']))
    for (a, b) in legs_for(pose, phase):
        sx = -1 if b[0] < 0 else 1
        back.append(Part(_oval(b[0] + 0.08 * sx, b[1] + 0.08, 0.25, 0.13), fill=st['shoes']))
        back.append(Part(_line((b[0] - 0.13 + 0.08 * sx, b[1] + 0.155), (b[0] + 0.29 * sx * 0.9 + 0.08 * sx * 0.1, b[1] + 0.155)),
                         ow=0.05, rim=False))
    arms = arms_for(pose, phase)
    hands_mid = []
    for pts, infront in arms:
        tube = Part(_cubic(*pts), tube=0.25, fill=st['top_color'])
        hx, hy = pts[-1]
        hand = Part(_oval(hx, hy, 0.13, 0.13), fill=st['skin'], ow=0.065)
        if infront:
            front.extend([tube, hand])
        else:
            back.append(tube)
            hands_mid.append(hand)
    mid.extend(torso_parts(st))
    mid.extend(hands_mid)
    mid.extend(hood_parts(st))
    # head group
    bx, by = bob
    hp = _P(HEAD, tension=1.0)
    head.append(Part(hp, fill=st['skin']))
    if st.get('hair'):
        head.extend(hair_parts(st['hair'], st['hair_color']))
    if st.get('cap'):
        head.extend(cap_parts(st['cap']))
    head.extend(face_parts(expr, st, look, glint))
    for p in head:
        p.path.offset(bx, by)
    order = back + mid + head + front

    canvas.save()
    canvas.translate(cx, cy)
    canvas.scale(-R if flip else R, R)
    if alpha < 255:
        canvas.saveLayerAlpha(None, int(alpha))
    if show_rim:
        for p in order:
            if not p.rim:
                continue
            if p.tube:
                canvas.drawPath(p.path, paint(RIM_COLOR, stroke=p.tube + 2 * OL + 2 * RIM))
            else:
                if p.fill is not None:
                    canvas.drawPath(p.path, paint(RIM_COLOR))
                canvas.drawPath(p.path, paint(RIM_COLOR, stroke=p.ow + 2 * RIM))
    for p in order:
        if p.tube:
            canvas.drawPath(p.path, paint(INK, stroke=p.tube + 2 * OL))
            canvas.drawPath(p.path, paint(p.fill, stroke=p.tube))
            continue
        if p.fill is not None:
            canvas.drawPath(p.path, paint(p.fill, alpha=p.alpha))
        if p.ow > 0:
            canvas.drawPath(p.path, paint(p.stroke_color, stroke=p.ow, cap=p.cap))
    if alpha < 255:
        canvas.restore()
    canvas.restore()
    cap = st.get('cap')
    if cap and cap.get('text'):
        from .text import font
        f = font(0.36 * R)
        tw = f.measureText(cap['text'])
        sx = -1 if flip else 1
        canvas.drawString(cap['text'], cx + sx * (0.04 + bx) * R - tw / 2, cy + (-0.62 + by) * R, f,
                          paint(cap['text_color'], alpha=alpha))


# Framing constants (same as the format): head half-width in px at 1080p
R_NORMAL, R_ZOOM, R_PIP = 182.0, 277.0, 87.0
NORMAL_CENTER, ZOOM_CENTER = (960.0, 430.0), (960.0, 446.0)
