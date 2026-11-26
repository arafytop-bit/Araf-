"""Historical costumes for the round-head rig: hats/helmets, facial hair, hair, outfits, capes.

All geometry in head-radius units (R = 1, origin head centre, y down).
"""
import math
import skia
from .roundhead import Part, P, oval, line, poly, quad, INK, OL, _shade


# ---------------- hats & helmets ----------------
def hat_extra(h, st):
    c = st.get('hat_color', '#777777')
    out = []
    if h == 'viking':     # nasal helmet (no horns: historically accurate)
        dome = P([(-1.05, -0.30), (-1.0, -0.82), (-0.62, -1.20), (0.0, -1.32), (0.62, -1.20), (1.0, -0.82),
                  (1.05, -0.30), (0.0, -0.38)], tension=0.85)
        out.append(Part(dome, fill=c, grad=(-1.32, -0.3, 1.15, 0.82)))
        out.append(Part(line((0.0, -1.30), (0.0, -0.42)), ow=0.05, rim=False))
        out.append(Part(poly([(-1.09, -0.46), (1.09, -0.46), (1.07, -0.26), (-1.07, -0.26)]), fill=_shade(c, 0.8)))
        out.append(Part(poly([(-0.045, -0.30), (0.045, -0.30), (0.045, 0.10), (-0.045, 0.10)]), fill=_shade(c, 0.8), ow=0.045))
        for x in (-0.8, -0.4, 0.4, 0.8):
            out.append(Part(oval(x, -0.36, 0.035, 0.035), fill='#E8E8E8', ow=0.02, rim=False))
    elif h == 'crown':
        pts = [(-0.80, -0.66), (-0.84, -1.24), (-0.54, -0.98), (-0.27, -1.40), (0.0, -1.02), (0.27, -1.40),
               (0.54, -0.98), (0.84, -1.24), (0.80, -0.66)]
        out.append(Part(poly(pts), fill=c or '#E8B83A', grad=(-1.4, -0.66, 1.15, 0.85)))
        out.append(Part(poly([(-0.82, -0.82), (0.82, -0.82), (0.80, -0.64), (-0.80, -0.64)]), fill=_shade(c or '#E8B83A', 0.85)))
        for x, col in ((-0.45, '#C0392B'), (0.0, '#2E86DE'), (0.45, '#C0392B')):
            out.append(Part(oval(x, -0.73, 0.07, 0.06), fill=col, ow=0.03, rim=False))
    elif h == 'laurel':   # olive wreath
        for side in (-1, 1):
            for k in range(7):
                a = math.radians(200 + k * 17) if side < 0 else math.radians(340 - k * 17)
                x, y = 1.0 * math.cos(a), 1.0 * math.sin(a) * 0.95 - 0.02
                leaf = oval(0, 0, 0.17, 0.07)
                m = skia.Matrix()
                m.setRotate(math.degrees(a) + (60 if side < 0 else -60))
                m.postTranslate(x, y)
                leaf.transform(m)
                out.append(Part(leaf, fill='#7FA650' if k % 2 else '#93B862', ow=0.03))
    elif h == 'fur':      # Hun cap: conical crown with a fur band
        out.append(Part(P([(-0.82, -0.62), (-0.70, -1.10), (-0.30, -1.48), (0.10, -1.62), (0.40, -1.40), (0.78, -1.02),
                           (0.84, -0.62)], tension=0.8), fill=c, grad=(-1.6, -0.62, 1.1, 0.85)))
        fur = []
        for k in range(11):
            x = -1.02 + k * 0.204
            fur += [(x, -0.78 - 0.10 * (k % 2)), (x + 0.10, -0.62 - 0.08 * (k % 2))]
        band = [(-1.06, -0.50)] + [(x, y) for x, y in fur] + [(1.06, -0.50), (0.9, -0.36), (0.0, -0.40), (-0.9, -0.36)]
        out.append(Part(P(band, tension=0.6), fill='#8A6A48', grad=(-0.9, -0.36, 1.15, 0.85)))
    elif h == 'roman':    # galea with red crest
        crest = P([(-0.75, -1.05), (-0.55, -1.55), (0.0, -1.78), (0.55, -1.55), (0.75, -1.05), (0.0, -1.20)], tension=0.8)
        out.append(Part(crest, fill='#B03A2E', grad=(-1.78, -1.05, 1.15, 0.8)))
        for x in (-0.45, -0.15, 0.15, 0.45):
            out.append(Part(line((x * 1.1, -1.62 + abs(x) * 0.3), (x * 1.3, -1.18)), ow=0.03, rim=False, color='#7E2A22', ink=False))
        dome = P([(-1.05, -0.32), (-1.0, -0.82), (-0.62, -1.18), (0.0, -1.28), (0.62, -1.18), (1.0, -0.82), (1.05, -0.32),
                  (0.0, -0.40)], tension=0.85)
        out.append(Part(dome, fill=c or '#C9A04A', grad=(-1.28, -0.32, 1.15, 0.82)))
        out.append(Part(poly([(-1.08, -0.44), (1.08, -0.44), (1.06, -0.28), (-1.06, -0.28)]), fill=_shade(c or '#C9A04A', 0.8)))
    elif h == 'admiral':  # Joseon general's helmet with plume
        for sx in (-1, 1):
            flap = P([(sx * 0.98, -0.30), (sx * 1.16, 0.10), (sx * 1.12, 0.62), (sx * 0.86, 0.70), (sx * 0.88, 0.10)], tension=0.7)
            out.append(Part(flap, fill='#2F3A5A', grad=(-0.3, 0.7, 1.1, 0.85)))
        out.append(Part(line((0.0, -1.30), (0.0, -1.62)), ow=0.06, rim=False))
        plume = P([(0.0, -1.58), (-0.22, -1.85), (-0.10, -2.05), (0.12, -2.02), (0.24, -1.82)], tension=0.8)
        out.append(Part(plume, fill='#C0392B'))
        dome = P([(-1.05, -0.32), (-1.0, -0.84), (-0.62, -1.22), (0.0, -1.34), (0.62, -1.22), (1.0, -0.84), (1.05, -0.32),
                  (0.0, -0.40)], tension=0.85)
        out.append(Part(dome, fill=c or '#3A3F47', grad=(-1.34, -0.32, 1.25, 0.8)))
        out.append(Part(poly([(-1.09, -0.46), (1.09, -0.46), (1.07, -0.28), (-1.07, -0.28)]), fill='#C9A050'))
        for x in (-0.6, 0.0, 0.6):
            out.append(Part(oval(x, -0.92, 0.05, 0.05), fill='#C9A050', ow=0.02, rim=False))
    elif h == 'kabuto':   # Japanese helmet with flared neck guard and crescent crest
        for sx in (-1, 1):
            out.append(Part(P([(sx * 0.95, -0.45), (sx * 1.35, -0.10), (sx * 1.30, 0.15), (sx * 0.98, 0.05)], tension=0.6),
                            fill=c or '#2E2B2B'))
        dome = P([(-1.05, -0.32), (-1.0, -0.84), (-0.62, -1.22), (0.0, -1.34), (0.62, -1.22), (1.0, -0.84), (1.05, -0.32),
                  (0.0, -0.40)], tension=0.85)
        out.append(Part(dome, fill=c or '#2E2B2B', grad=(-1.34, -0.32, 1.4, 0.9)))
        crest = skia.Path()
        crest.moveTo(-0.55, -1.55); crest.quadTo(0.0, -0.95, 0.55, -1.55); crest.quadTo(0.0, -1.15, -0.55, -1.55); crest.close()
        out.append(Part(crest, fill='#D9A93A', ow=0.04))
    elif h == 'bicorne':
        bi = P([(-1.45, -0.62), (-0.9, -1.05), (0.0, -1.22), (0.9, -1.05), (1.45, -0.62), (0.8, -0.72), (0.0, -0.78),
                (-0.8, -0.72)], tension=0.7)
        out.append(Part(bi, fill=c or '#1E2230', grad=(-1.22, -0.62, 1.3, 0.9)))
        out.append(Part(oval(0.0, -0.92, 0.12, 0.12), fill='#C9A050', ow=0.035))
    elif h == 'pirate':
        tri = P([(-1.30, -0.60), (-0.95, -1.15), (0.0, -1.32), (0.95, -1.15), (1.30, -0.60), (0.0, -0.80)], tension=0.6)
        out.append(Part(tri, fill='#1C1C1C'))
        out.append(Part(oval(0.0, -0.98, 0.13, 0.11), fill='#F2F2F2', ow=0.03, rim=False))
        for sx in (-1, 1):
            out.append(Part(line((sx * 0.20, -1.12), (-sx * 0.20, -0.84)), ow=0.04, rim=False, color='#F2F2F2', ink=False))
    elif h == 'hood':     # scribe / monk hood framing the face
        out.append(Part(P([(-1.22, 0.55), (-1.25, -0.40), (-0.85, -1.18), (0.0, -1.38), (0.85, -1.18), (1.25, -0.40),
                           (1.22, 0.55), (0.92, 0.25), (0.96, -0.40), (0.60, -0.92), (0.0, -1.04), (-0.60, -0.92),
                           (-0.96, -0.40), (-0.92, 0.25)], tension=0.8), fill=c or '#6B4F3A', grad=(-1.38, 0.55, 1.15, 0.85)))
    elif h == 'veil':
        out.append(Part(P([(-1.20, 0.80), (-1.18, -0.45), (-0.80, -1.16), (0.0, -1.30), (0.80, -1.16), (1.18, -0.45),
                           (1.20, 0.80), (0.95, 0.40), (0.98, -0.30), (0.0, -0.60), (-0.98, -0.30), (-0.95, 0.40)],
                          tension=0.8), fill='#FFFFFF', alpha=170, ow=0.035))
        out.append(Part(oval(-0.55, -0.88, 0.11, 0.11), fill='#F4B6C2', ow=0.03))
    return out


# ---------------- hair (back layer + front layer) and facial hair ----------------
def hair_extra(h, c):
    back, front = [], []
    if h == 'balding':
        for sx in (-1, 1):
            front.append(Part(P([(sx * 1.02, -0.42), (sx * 1.05, 0.05), (sx * 0.93, 0.30), (sx * 0.80, -0.02),
                                 (sx * 0.84, -0.38)], tension=0.8), fill=c))
    elif h == 'long':
        back.append(Part(P([(-1.18, -0.30), (-1.05, -0.95), (0.0, -1.25), (1.05, -0.95), (1.18, -0.30), (1.15, 0.80),
                            (0.70, 1.05), (-0.70, 1.05), (-1.15, 0.80)], tension=0.85), fill=c))
        front.append(Part(P([(-1.02, -0.30), (-0.92, -0.80), (-0.45, -1.10), (0.20, -1.12), (0.75, -0.95), (1.02, -0.45),
                             (0.70, -0.62), (0.20, -0.70), (-0.30, -0.58), (-0.75, -0.46)], tension=0.85), fill=c))
    elif h == 'viking':   # long hair falling behind the shoulders
        back.append(Part(P([(-1.15, -0.30), (-1.20, 0.50), (-1.00, 1.10), (1.00, 1.10), (1.20, 0.50), (1.15, -0.30)],
                           tension=0.8), fill=c))
    return back, front


def facial_hair(kind, c):
    out = []
    if kind == 'beard':
        out.append(Part(P([(-0.86, 0.22), (-0.70, 0.62), (-0.42, 1.00), (0.0, 1.30), (0.42, 1.00), (0.70, 0.62), (0.86, 0.22),
                           (0.50, 0.46), (0.20, 0.40), (0.0, 0.46), (-0.20, 0.40), (-0.50, 0.46)], tension=0.8),
                        fill=c, grad=(0.2, 1.3, 1.1, 0.85)))
        out.append(Part(P([(-0.36, 0.30), (0.0, 0.22), (0.36, 0.30), (0.30, 0.42), (0.0, 0.36), (-0.30, 0.42)], tension=0.7),
                        fill=_shade(c, 0.85), ow=0.035))
    elif kind == 'mustache':   # thin drooping mustache
        p = skia.Path()
        p.moveTo(-0.40, 0.66); p.quadTo(-0.36, 0.34, 0.0, 0.30); p.quadTo(0.36, 0.34, 0.40, 0.66)
        out.append(Part(p, ow=0.065, rim=False, color=c))
    elif kind == 'goatee':
        out.append(Part(P([(-0.16, 0.50), (0.16, 0.50), (0.10, 0.80), (0.0, 0.90), (-0.10, 0.80)], tension=0.7), fill=c, ow=0.035))
    return out


# ---------------- outfits ----------------
def body_shape(hem=2.30, top=0.90, w_sh=0.52, w_hip=0.66):
    return P([(-w_sh, top), (w_sh, top), (w_sh + 0.10, 1.25), (w_hip, hem), (-w_hip, hem), (-w_sh - 0.10, 1.25)], tension=0.4)


def top_extra(t, st):
    c = st.get('top_color', '#888888')
    out = []
    if t in ('tunic', 'tshirt'):
        hem = 2.30 if t == 'tunic' else 2.12
        out.append(Part(body_shape(hem), fill=c, grad=(0.9, hem, 1.06, 0.85)))
        if t == 'tunic':
            out.append(Part(line((0.0, 0.94), (0.0, 1.24)), ow=0.04, rim=False))
            out.append(Part(poly([(-0.66, 1.76), (0.66, 1.76), (0.67, 1.90), (-0.67, 1.90)]), fill=st.get('belt', '#4A3326'), ow=0.04))
            if st.get('trim'):
                out.append(Part(poly([(-0.66, hem - 0.10), (0.66, hem - 0.10), (0.66, hem), (-0.66, hem)]), fill=st['trim'], ow=0.035))
        else:
            out.append(Part(quad((-0.20, 0.92), (0.0, 1.08), (0.20, 0.92)), ow=0.04, rim=False))
    elif t == 'toga':
        out.append(Part(body_shape(2.55, w_hip=0.72), fill=c or '#F1EDE4', grad=(0.9, 2.55, 1.02, 0.86)))
        band = poly([(-0.52, 0.92), (-0.30, 0.90), (0.66, 1.95), (0.62, 2.15)])
        out.append(Part(band, fill=st.get('stripe', '#6B2E7A'), ow=0.04))
        for k in range(3):
            out.append(Part(quad((-0.50 + k * 0.12, 1.35 + k * 0.25), (-0.10 + k * 0.1, 1.55 + k * 0.25),
                                 (0.10 + k * 0.12, 1.75 + k * 0.25)), ow=0.03, rim=False))
    elif t == 'armor':
        out.append(Part(body_shape(2.32), fill=c, grad=(0.9, 2.32, 1.1, 0.8)))
        stud = st.get('stud', '#C9A050')
        for row in range(6):
            y = 1.05 + row * 0.20
            out.append(Part(quad((-0.62, y), (0.0, y + 0.07), (0.62, y)), ow=0.03, rim=False, color=_shade(c, 0.6), ink=False))
            for k in range(5):
                out.append(Part(oval(-0.44 + k * 0.22, y + 0.06, 0.028, 0.028), fill=stud, ow=0, rim=False))
        out.append(Part(poly([(-0.66, 1.80), (0.66, 1.80), (0.67, 1.94), (-0.67, 1.94)]), fill=st.get('belt', '#5A1E1E'), ow=0.04))
    elif t == 'robe':
        out.append(Part(body_shape(2.95, w_hip=0.80), fill=c, grad=(0.9, 2.95, 1.05, 0.85)))
        out.append(Part(poly([(-0.18, 0.92), (0.18, 0.92), (0.0, 1.20)]), fill=st.get('shirt', '#EFEAE0'), ow=0.04))
        out.append(Part(poly([(-0.68, 1.62), (0.68, 1.62), (0.70, 1.76), (-0.70, 1.76)]), fill=st.get('belt', '#4A3326'), ow=0.04))
    elif t == 'athlete':  # bare torso + loincloth
        skin = '#F8F8F5'
        out.append(Part(body_shape(2.15, w_hip=0.60), fill=skin))
        out.append(Part(oval(0.0, 1.70, 0.035, 0.035), fill=INK, ow=0, rim=False))
        out.append(Part(poly([(-0.62, 1.98), (0.62, 1.98), (0.50, 2.40), (0.0, 2.30), (-0.50, 2.40)]), fill=c or '#D9C9A3', ow=0.05))
    return out


def cape_parts(st):
    c = st.get('cape')
    if not c:
        return []
    return [Part(P([(-0.55, 0.92), (0.55, 0.92), (1.00, 2.20), (0.95, 2.80), (-0.95, 2.80), (-1.00, 2.20)], tension=0.5),
                 fill=c, grad=(0.9, 2.8, 1.05, 0.8))]
