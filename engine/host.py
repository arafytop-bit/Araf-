"""Parametric stick-figure rig (host, agents, subject characters).

Geometry is in head-radius units (R = 1, origin = head centre, y down), measured from
the source frames (see analysis/reference/detail/host_crop3x.png and BLUEPRINT 5.2).
"""
import math
import skia
from .core import paint, catmull_rom_path, poly_path, rgb

OUT = 0.088       # head / torso outline thickness (measured 0.086R)
LIMB = 0.12       # arm stroke
LEG = 0.10        # leg stroke
RIM = 0.018       # light-grey rim around the whole silhouette (per side)
RIM_COLOR = '#9A9A9A'
LINE = '#000000'

# Our host: same construction as the source, own colour (blue) so it reads as your channel.
HOST = dict(skin='#FFFFFF', cap='#3B82F6', shirt='#3B82F6', hair=None, cap_text=None, cap_text_color=None)
AGENT = dict(skin='#FFFFFF', cap='#1E2A47', shirt='#1E2A47', hair=None, cap_text='FBI', cap_text_color='#F2C230', cap_style='front')


class Part:
    __slots__ = ('path', 'fill', 'sw', 'rim', 'color', 'cap')

    def __init__(self, path, fill=None, sw=0.0, rim=True, color=LINE, cap='round'):
        self.path, self.fill, self.sw, self.rim, self.color, self.cap = path, fill, sw, rim, color, cap


def _cubic(p0, c1, c2, p1):
    pth = skia.Path()
    pth.moveTo(*p0)
    pth.cubicTo(c1[0], c1[1], c2[0], c2[1], p1[0], p1[1])
    return pth


def _line(a, b):
    pth = skia.Path()
    pth.moveTo(*a)
    pth.lineTo(*b)
    return pth


def _oval(cx, cy, rx, ry):
    pth = skia.Path()
    pth.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    return pth


def _mirror(pts):
    return [(-x, y) for x, y in pts]


# ---------------- arms (shoulder -> elbow-ish controls -> hand) ----------------
HIP_L = ((-0.56, 1.00), (-1.05, 1.12), (-1.08, 1.82), (-0.55, 1.93))


def _arm(spec, mirror=False):
    p = [(-x, y) for x, y in spec] if mirror else spec
    return p


def arms_for(pose, phase=0.0):
    """Return list of (cubic_points, in_front_of_head, hand_radius)."""
    hip_l = HIP_L
    hip_r = _arm(HIP_L, True)
    if pose == 'hips':
        return [(hip_l, False, 0.075), (hip_r, False, 0.075)]
    if pose == 'wave':
        return [(hip_l, False, 0.075), (((0.55, 1.02), (0.98, 1.36), (1.28, 1.34), (1.42, 0.86)), False, 0.08)]
    if pose == 'wave_l':
        return [(_arm(((0.55, 1.02), (0.98, 1.36), (1.28, 1.34), (1.42, 0.86)), True), False, 0.08), (hip_r, False, 0.075)]
    if pose == 'chin':
        return [(((-0.52, 1.02), (-1.02, 1.42), (-0.78, 1.70), (-0.30, 0.95)), True, 0.10), (hip_r, False, 0.075)]
    if pose == 'cheeks':
        l = ((-0.55, 1.02), (-1.12, 1.25), (-1.08, 0.72), (-0.84, 0.40))
        return [(l, True, 0.12), (_arm(l, True), True, 0.12)]
    if pose == 'shrug':
        l = ((-0.55, 1.02), (-0.95, 1.42), (-1.22, 1.46), (-1.40, 1.04))
        return [(l, False, 0.08), (_arm(l, True), False, 0.08)]
    if pose == 'point':
        return [(hip_l, False, 0.075), (((0.55, 1.02), (0.95, 1.12), (1.25, 1.05), (1.58, 0.92)), False, 0.08)]
    if pose == 'walk':
        s = math.sin(phase)
        l = ((-0.50, 1.02), (-0.78 - 0.15 * s, 1.30), (-0.80 - 0.32 * s, 1.62), (-0.70 - 0.42 * s, 1.88))
        r = ((0.50, 1.02), (0.78 - 0.15 * s, 1.30), (0.80 - 0.32 * s, 1.62), (0.70 - 0.42 * s, 1.88))
        return [(l, False, 0.075), (r, False, 0.075)]
    raise ValueError(pose)


def legs_for(pose, phase=0.0):
    if pose == 'walk':
        s = math.sin(phase)
        return [((-0.20, 2.02), (-0.20 + 0.30 * s, 2.84)), ((0.20, 2.02), (0.20 - 0.30 * s, 2.84))]
    return [((-0.27, 2.02), (-0.27, 2.84)), ((0.27, 2.02), (0.28, 2.84))]


# ---------------- face ----------------
def face_parts(expr):
    parts = []
    black = LINE
    eye_ry = 0.065
    if expr == 'shock':
        eye_ry = 0.075
    parts.append(Part(_oval(-0.12, -0.22, 0.055, eye_ry), fill=black, rim=False))
    parts.append(Part(_oval(0.14, -0.22, 0.055, eye_ry), fill=black, rim=False))

    def brow(a, b):
        parts.append(Part(_line(a, b), sw=0.05, rim=False))

    if expr == 'talk':
        pts = [(-0.33, 0.11), (-0.21, 0.04), (-0.09, 0.08), (0.06, 0.04), (0.21, 0.07), (0.28, 0.20),
               (0.18, 0.36), (-0.02, 0.42), (-0.22, 0.37), (-0.34, 0.24)]
        parts.append(Part(catmull_rom_path(pts), fill=black, rim=False))
    elif expr == 'talk2':  # smaller open mouth, shifted (adds variety between swaps)
        pts = [(-0.22, 0.14), (-0.10, 0.09), (0.04, 0.12), (0.18, 0.10), (0.24, 0.21), (0.14, 0.33),
               (-0.04, 0.36), (-0.20, 0.31), (-0.27, 0.22)]
        parts.append(Part(catmull_rom_path(pts), fill=black, rim=False))
    elif expr == 'o':
        parts.append(Part(_oval(0.01, 0.22, 0.10, 0.12), fill=black, rim=False))
    elif expr == 'smile':  # open D smile
        pth = skia.Path()
        pth.moveTo(-0.27, 0.10)
        pth.quadTo(0.0, 0.05, 0.27, 0.10)
        pth.cubicTo(0.27, 0.44, -0.27, 0.44, -0.27, 0.10)
        pth.close()
        parts.append(Part(pth, fill=black, rim=False))
    elif expr == 'grin':
        pth = skia.Path()
        pth.moveTo(-0.24, 0.14)
        pth.quadTo(0.0, 0.42, 0.24, 0.14)
        parts.append(Part(pth, sw=0.07, rim=False))
    elif expr == 'grimace':
        rr = skia.Path()
        rr.addRRect(skia.RRect.MakeRectXY(skia.Rect(-0.29, 0.10, 0.29, 0.32), 0.10, 0.10))
        parts.append(Part(rr, fill='#FFFFFF', sw=0.055, rim=False))
        for x in (-0.10, 0.10):
            parts.append(Part(_line((x, 0.11), (x, 0.31)), sw=0.045, rim=False, cap='butt'))
        parts.append(Part(_line((-0.27, 0.21), (0.27, 0.21)), sw=0.04, rim=False, cap='butt'))
    elif expr == 'frown':
        pth = skia.Path()
        pth.moveTo(-0.22, 0.30)
        pth.cubicTo(-0.12, 0.16, -0.03, 0.36, 0.05, 0.24)
        pth.cubicTo(0.11, 0.16, 0.17, 0.20, 0.23, 0.26)
        parts.append(Part(pth, sw=0.06, rim=False))
    elif expr == 'skeptic':
        pth = skia.Path()
        pth.moveTo(-0.20, 0.30)
        pth.quadTo(-0.06, 0.18, 0.05, 0.27)
        pth.quadTo(0.14, 0.34, 0.23, 0.21)
        parts.append(Part(pth, sw=0.06, rim=False))
        brow((0.06, -0.41), (0.23, -0.47))
        brow((-0.21, -0.35), (-0.05, -0.34))
    elif expr == 'shock':
        parts.append(Part(_oval(0.0, 0.27, 0.12, 0.22), fill=black, rim=False))
        parts.append(Part(poly_path([(-0.07, 0.08), (0.07, 0.08), (0.07, 0.13), (-0.07, 0.13)]), fill='#FFFFFF', rim=False))
        brow((-0.23, -0.43), (-0.06, -0.40))
        brow((0.08, -0.40), (0.25, -0.43))
    elif expr == 'neutral':
        parts.append(Part(_line((-0.12, 0.24), (0.12, 0.24)), sw=0.06, rim=False))
    elif expr == 'evil':
        pth = skia.Path()
        pth.moveTo(-0.30, 0.12)
        pth.quadTo(0.0, 0.22, 0.30, 0.10)
        pth.quadTo(0.05, 0.48, -0.30, 0.12)
        pth.close()
        parts.append(Part(pth, fill=black, rim=False))
        brow((-0.25, -0.40), (-0.04, -0.30))
        brow((0.06, -0.30), (0.27, -0.40))
    else:
        raise ValueError(expr)
    return parts


# ---------------- head-wear / hair ----------------
CROWN = [(-1.06, -0.48), (-0.97, -0.80), (-0.76, -1.07), (-0.46, -1.25), (-0.13, -1.31), (0.13, -1.24),
         (0.10, -1.03), (-0.17, -1.02), (-0.47, -0.92), (-0.76, -0.72), (-0.97, -0.42)]
BRIM = ((0.06, -1.14), (0.74, -1.25))          # thick rounded stroke, measured tip (+0.74,-1.25)R

# forward-facing cap (agents): dome over the top of the head, brim pointing left
FCAP = [(-1.10, -0.28), (-0.95, -0.78), (-0.55, -1.12), (0.0, -1.24), (0.55, -1.12), (0.95, -0.78), (1.10, -0.28),
        (0.60, -0.36), (0.0, -0.40), (-0.60, -0.36)]
FBRIM = [(-0.60, -0.40), (-1.15, -0.44), (-1.62, -0.36), (-1.60, -0.22), (-1.12, -0.21), (-0.62, -0.27)]


def cap_parts(color, style='side'):
    if style == 'front':
        return [Part(catmull_rom_path(FBRIM, tension=0.8), fill=color, sw=OUT),
                Part(catmull_rom_path(FCAP, tension=0.8), fill=color, sw=OUT)]
    return [Part(_line(*BRIM), sw=0.10),
            Part(catmull_rom_path(CROWN, tension=0.9), fill=color, sw=OUT)]


def hair_parts(style, color='#1A1512'):
    if style == 'slick':   # 1950s slicked hair with side part
        pts = [(-1.07, -0.10), (-1.08, -0.55), (-0.85, -0.95), (-0.40, -1.16), (0.15, -1.15), (0.62, -0.98),
               (0.95, -0.66), (1.06, -0.30), (0.92, -0.42), (0.70, -0.62), (0.25, -0.74), (-0.10, -0.70),
               (-0.42, -0.62), (-0.80, -0.45), (-0.95, -0.20)]
        return [Part(catmull_rom_path(pts, tension=0.9), fill=color, sw=OUT)]
    if style == 'short':
        pts = [(-1.06, -0.25), (-1.0, -0.70), (-0.70, -1.02), (-0.25, -1.14), (0.25, -1.13), (0.70, -1.0),
               (1.0, -0.68), (1.06, -0.25), (0.86, -0.50), (0.45, -0.70), (0.0, -0.76), (-0.45, -0.70), (-0.86, -0.50)]
        return [Part(catmull_rom_path(pts, tension=0.9), fill=color, sw=OUT)]
    raise ValueError(style)


# ---------------- assemble & draw ----------------
def draw_character(canvas, cx, cy, R, pose='hips', expr='talk', pal=HOST, flip=False,
                   bob=(0.0, 0.0), phase=0.0, alpha=255, show_rim=True, crop_legs=False):
    """Draw a full stick figure with head centre (cx, cy) and head radius R (px)."""
    body, front, head = [], [], []
    # legs
    for a, b in legs_for(pose, phase):
        body.append(Part(_line(a, b), sw=LEG))
    # torso
    tor = skia.Path()
    tor.addRect(skia.Rect(-0.48, 0.95, 0.48, 2.03))
    body.append(Part(tor, fill=pal['shirt'], sw=OUT, cap='butt'))
    # arms
    for pts, infront, hr in arms_for(pose, phase):
        arm = [Part(_cubic(*pts), sw=LIMB)]
        hx, hy = pts[-1]
        arm.append(Part(_oval(hx, hy, hr, hr), fill=LINE, sw=0.0))
        (front if infront else body).extend(arm)
    # head group (can bob slightly relative to body)
    bx, by = bob
    hp = skia.Path()
    hp.addCircle(bx, by, 1.0 + OUT / 2)
    head.append(Part(hp, fill=pal['skin'], sw=OUT))
    if pal.get('hair'):
        for p in hair_parts(pal['hair']):
            p.path.offset(bx, by)
            head.append(p)
    if pal.get('cap'):
        for p in cap_parts(pal['cap'], pal.get('cap_style', 'side')):
            p.path.offset(bx, by)
            head.append(p)
    for p in face_parts(expr):
        p.path.offset(bx, by)
        head.append(p)

    order = body + head + front
    canvas.save()
    canvas.translate(cx, cy)
    canvas.scale(-R if flip else R, R)
    layer = alpha < 255
    if layer:
        canvas.saveLayerAlpha(None, int(alpha))
    if show_rim:
        for p in order:
            if not p.rim:
                continue
            if p.fill is not None:
                canvas.drawPath(p.path, paint(RIM_COLOR))
            canvas.drawPath(p.path, paint(RIM_COLOR, stroke=p.sw + 2 * RIM, cap=p.cap))
    for p in order:
        if p.fill is not None:
            canvas.drawPath(p.path, paint(p.fill))
        if p.sw > 0:
            canvas.drawPath(p.path, paint(p.color, stroke=p.sw, cap=p.cap))
    if layer:
        canvas.restore()
    canvas.restore()
    # cap lettering (drawn unmirrored)
    if pal.get('cap_text'):
        from .text import font
        f = font(0.36 * R)
        tw = f.measureText(pal['cap_text'])
        sx = -1 if flip else 1
        tx = cx + sx * (0.05 + bx) * R - tw / 2
        ty = cy + (-0.56 + by) * R
        canvas.drawString(pal['cap_text'], tx, ty, f, paint(pal['cap_text_color'], alpha=alpha))


# host scales measured on the source (head radius, 1080p)
R_NORMAL = 182.0      # 81 px @480p
R_ZOOM = 277.0        # 123 px @480p  (x1.52)
R_PIP = 87.0          # 38.5 px @480p (x0.47)
NORMAL_CENTER = (960.0, 430.0)   # head centre at x 50%, y 39.8%
ZOOM_CENTER = (960.0, 446.0)     # y 41.3%, legs cropped
