"""Stick-figure character rig (narrator + cast). Origin = centre of the head.
k=1.0 is the narrator's solo-shot size (head ~297x280 px, figure ~830 px tall @1080p)."""
import math
from dd import *

U = 1.5  # base unit (720p measurements -> 1080p)
ARMS = {
    "hips":     [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (34, 30), (4, 60)]],
    "hip_one":  [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (30, 50), (50, 74)]],
    "relaxed":  [[(0, 0), (-24, 50), (-34, 102)], [(0, 0), (24, 50), (34, 102)]],
    "think":    [[(0, 0), (-30, 40), (2, 52)], [(0, 0), (44, 24), (36, -24)]],
    "arms_up":  [[(0, 0), (-60, -40), (-95, -95)], [(0, 0), (60, -40), (100, -90)]],
    "shrug":    [[(0, 0), (-50, 30), (-92, 4)], [(0, 0), (50, 30), (92, 2)]],
    "present":  [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (62, 8), (124, -12)]],
    "present_l":[[(0, 0), (-62, 8), (-124, -12)], [(0, 0), (34, 30), (4, 60)]],
    "teacher":  [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (46, 26), (80, 10)]],
    "mic":      [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (34, 40), (50, 4)]],
    "point":    [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (66, -22), (128, -56)]],
    "wave":     [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (52, -26), (64, -92)]],
    "hold":     [[(0, 0), (-46, 34), (-36, -6)], [(0, 0), (46, 34), (36, -6)]],
    "carry":    [[(0, 0), (-40, 40), (10, 60)], [(0, 0), (40, 40), (60, 50)]],
    "facepalm": [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (44, 14), (14, -76)]],
    "pull_l":   [[(0, 0), (-62, 10), (-124, 2)], [(0, 0), (-52, 30), (-112, 14)]],
    "pull_r":   [[(0, 0), (62, 10), (124, 2)], [(0, 0), (52, 30), (112, 14)]],
    "cross":    [[(0, 0), (-32, 40), (26, 34)], [(0, 0), (32, 40), (-26, 34)]],
    "run":      [[(0, 0), (-42, 26), (-24, 72)], [(0, 0), (44, -12), (78, 24)]],
    "desk":     [[(0, 0), (34, 58), (96, 66)], [(0, 0), (44, 52), (112, 58)]],
    "tug":      [[(0, 0), (-50, -40), (-70, -100)], [(0, 0), (50, -40), (70, -100)]],
    "stop":     [[(0, 0), (-36, 32), (-4, 62)], [(0, 0), (60, -10), (84, -70)]],
    "hold_up":  [[(0, 0), (-50, -110), (-40, -240)], [(0, 0), (50, -110), (40, -240)]],
}
LEGS = {"stand": [(-46, 100), (0, 0), (46, 100)], "walk": [(-62, 92), (0, 0), (34, 54), (58, 100)],
        "run": [(-72, 78), (0, 0), (42, 44), (30, 100)], "sit": [(-4, 4), (62, 8), (64, 96)],
        "lean_l": [(-80, 96), (0, 0), (20, 100)], "lean_r": [(-20, 100), (0, 0), (80, 96)], "none": None}
HAIR_COLORS = {"black": INK, "brown": "#6B4226", "blonde": "#E3C16F", "grey": "#BDBDBD", "red": "#B5502A", "dark": "#2A2A2A"}

def _hair(style, hx, hy, rx, ry, k, color, sd):
    g = []; r = rng(sd)
    if style == "spiky":   # narrator scribble patch on top-left
        outer = []; inner = []; a0, a1, n = -172.0, -52.0, 22
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n); u = i / n
            rr = 1.0 + (0.20 - 0.12 * u) * 0.55 + r.uniform(0.0, 0.16) * (1.0 if i % 2 else 0.25)
            outer.append((hx + rx * math.cos(a) * rr + r.uniform(-3, 3) * k, hy + ry * math.sin(a) * rr + r.uniform(-3, 3) * k))
            ri = 0.86 + 0.08 * u + r.uniform(-0.02, 0.02); inner.append((hx + rx * math.cos(a) * ri, hy + ry * math.sin(a) * ri))
        pts = outer + inner[::-1]
        g.append(P("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", color, color, 2.5 * k))
        for j in range(7):
            a = math.radians(r.uniform(a0 + 5, a1 - 5)); L = r.uniform(0.10, 0.22); da = r.uniform(-0.25, 0.25)
            g.append(P(f"M{hx + rx*math.cos(a)*1.02:.1f},{hy + ry*math.sin(a)*1.02:.1f} L{hx + rx*math.cos(a+da)*(1.02+L):.1f},{hy + ry*math.sin(a+da)*(1.02+L):.1f}", "none", color, 3.2 * k))
    elif style in ("side", "long", "bun", "swoop"):
        pts = []
        for i in range(19):
            a = math.radians(-190 + i * 11.1); rr = 1.06 + r.uniform(-0.01, 0.02)
            pts.append((hx + rx * math.cos(a) * rr, hy + ry * math.sin(a) * rr))
        # lower edge of the hair cap (side part swoop)
        cut = [(hx + rx * 0.98, hy - ry * 0.05), (hx + rx * 0.55, hy - ry * 0.42), (hx + rx * 0.1, hy - ry * 0.52),
               (hx - rx * 0.35, hy - ry * 0.40), (hx - rx * 0.80, hy - ry * 0.10), (hx - rx * 1.0, hy + ry * 0.15)]
        if style == "swoop":
            cut = [(hx + rx * 0.98, hy - ry * 0.15), (hx + rx * 0.4, hy - ry * 0.35), (hx - rx * 0.2, hy - ry * 0.62),
                   (hx - rx * 0.7, hy - ry * 0.45), (hx - rx * 1.02, hy + ry * 0.05)]
        g.append(P(catmull(pts + cut, closed=True), color, INK, 4 * k))
        if style == "long":
            for sx in (-1, 1):
                g.append(P(catmull([(hx + sx * rx * 0.95, hy - ry * 0.1), (hx + sx * rx * 1.12, hy + ry * 0.5), (hx + sx * rx * 1.05, hy + ry * 1.05), (hx + sx * rx * 0.78, hy + ry * 0.9), (hx + sx * rx * 0.84, hy + ry * 0.2)], closed=True), color, INK, 4 * k))
        if style == "bun":
            g.append(ell(hx + rx * 0.05, hy - ry * 1.18, rx * 0.36, ry * 0.32, color, sd + 9, 4 * k))
    elif style == "curly":
        for i in range(9):
            a = math.radians(-180 + i * 22.5)
            g.append(ell(hx + rx * math.cos(a) * 0.98, hy + ry * math.sin(a) * 0.98, rx * 0.24, ry * 0.24, color, sd + 20 + i, 4 * k))
    elif style == "bald":
        for sx in (-1, 1):
            g.append(P(catmull([(hx + sx * rx * 0.98, hy - ry * 0.05), (hx + sx * rx * 1.04, hy + ry * 0.25), (hx + sx * rx * 0.9, hy + ry * 0.35)]), color, INK, 3 * k))
    elif style == "cap" or style == "none":
        pass
    return "".join(g)

def _hat(kind, hx, hy, rx, ry, k, sd, color=None):
    if kind == "tophat":
        return (rect(hx - rx * 0.55, hy - ry * 1.95, rx * 1.1, ry * 1.05, color or INK, sd, 4 * k) +
                rect(hx - rx * 0.55, hy - ry * 1.12, rx * 1.1, ry * 0.18, RED, sd + 1, 3 * k) +
                rect(hx - rx * 0.95, hy - ry * 0.98, rx * 1.9, ry * 0.14, color or INK, sd + 2, 4 * k))
    if kind == "hardhat":
        dome = [(hx - rx * 0.92, hy - ry * 0.55)] + [(hx + rx * 0.92 * math.cos(math.radians(a)), hy - ry * 0.55 + ry * 0.75 * math.sin(math.radians(a))) for a in range(-180, 1, 20)]
        bolt = [(hx + rx * 0.05, hy - ry * 1.15), (hx - rx * 0.15, hy - ry * 0.85), (hx + rx * 0.02, hy - ry * 0.85), (hx - rx * 0.1, hy - ry * 0.62), (hx + rx * 0.2, hy - ry * 0.95), (hx + rx * 0.03, hy - ry * 0.95)]
        return (poly(dome, color or YELLOW, sd, 4.5 * k) + rect(hx - rx * 1.12, hy - ry * 0.62, rx * 2.24, ry * 0.16, color or YELLOW, sd + 1, 4.5 * k)
                + poly(bolt, ORANGE, sd + 2, 2.5 * k))
    if kind == "cap":
        dome = [(hx - rx * 0.95, hy - ry * 0.35)] + [(hx + rx * 0.95 * math.cos(math.radians(a)), hy - ry * 0.35 + ry * 0.8 * math.sin(math.radians(a))) for a in range(-180, 1, 20)]
        return poly(dome, color or RED, sd, 4.5 * k) + poly([(hx + rx * 0.5, hy - ry * 0.42), (hx + rx * 1.45, hy - ry * 0.36), (hx + rx * 1.4, hy - ry * 0.24), (hx + rx * 0.5, hy - ry * 0.26)], color or RED, sd + 1, 4 * k)
    if kind == "halo":
        return ell(hx, hy - ry * 1.25, rx * 0.6, ry * 0.12, "none", sd, 5 * k, GOLD)
    return ""

def person(seed=0, k=1.0, pose="hips", mouth="smile", brow=None, eyes="dot", look=0.0, skin=SKIN, hair="spiky",
           hair_color="black", glasses=None, tie=None, bowtie=None, shirt=None, sash=None, hat=None, hat_color=None,
           mustache=False, legs="stand", prop=None, prop_text="", sweat=False, flip=False, body=True, blush=False,
           head_scale=1.0, sign_w=260):
    sd = seed * 1000 + 7; g = []; u = U * k
    rx, ry = 99 * u * head_scale, 93 * u * head_scale; hx, hy = 0.0, 0.0
    lw_head, lw_body = 5.5 * u, 6.0 * u
    hcol = HAIR_COLORS.get(hair_color, hair_color)
    neck = (-4 * u, ry - 4 * u); hip = (-2 * u, ry + 175 * u)
    sh = (-3 * u, ry + 45 * u)
    hands = {}
    if body:
        if shirt:   # clothed torso (hoodie / suit / robe)
            tw0, tw1 = 46 * u, 56 * u; ty0, ty1 = ry - 6 * u, ry + 150 * u
            torso = [(-tw0, ty0 + 10 * u), (-tw0 * 0.55, ty0), (tw0 * 0.55, ty0), (tw0, ty0 + 10 * u), (tw1, ty1), (-tw1, ty1)]
            if legs != "none":
                for lx in (-22, 22):
                    g.append(P(wobble([(lx * u, ty1 - 4 * u), (lx * 1.3 * u, ty1 + 120 * u)], sd + 30 + lx, 1.4 * u), "none", INK, lw_body))
            g.append(poly(torso, shirt, sd + 1, 4.5 * u))
            if sash: g.append(P(f"M{-tw0*0.6:.1f},{ty0+6*u:.1f} L{tw1*0.9:.1f},{ty1-30*u:.1f}", "none", sash, 16 * u, cap="butt"))
            sh_l, sh_r = (-tw0 * 0.85, ty0 + 22 * u), (tw0 * 0.85, ty0 + 22 * u)
        else:
            g.append(P(wobble([neck, hip], sd + 1, 1.6 * u), "none", INK, lw_body))
            if legs != "none" and LEGS.get(legs):
                lp = [(hip[0] + x * u, hip[1] + y * u) for x, y in LEGS[legs]]
                g.append(P(wobble(lp, sd + 2, 1.6 * u, 22 * u), "none", INK, lw_body))
            sh_l = sh_r = sh
        arms = ARMS.get(pose, ARMS["hips"])
        for i, a in enumerate(arms):
            base = sh_l if i == 0 else sh_r
            pts = [(base[0] + x * u, base[1] + y * u) for x, y in a]
            g.append(P(wobble(pts, sd + 3 + i, 1.4 * u, 18 * u), "none", INK, lw_body))
            hands[i] = pts[-1]
        if tie and not shirt:
            tx, ty = neck[0], neck[1] + 4 * u
            g.append(poly([(tx - 9 * u, ty), (tx + 9 * u, ty), (tx + 6 * u, ty + 14 * u), (tx + 14 * u, ty + 92 * u), (tx, ty + 112 * u), (tx - 14 * u, ty + 92 * u), (tx - 6 * u, ty + 14 * u)], tie, sd + 8, 3.5 * u))
        if tie and shirt:
            tx, ty = 0, ry
            g.append(poly([(tx - 9 * u, ty), (tx + 9 * u, ty), (tx + 13 * u, ty + 80 * u), (tx, ty + 96 * u), (tx - 13 * u, ty + 80 * u)], tie, sd + 8, 3.5 * u))
        if bowtie:
            bx, by = 0, ry + 4 * u
            g.append(poly([(bx, by), (bx - 26 * u, by - 14 * u), (bx - 26 * u, by + 14 * u)], bowtie, sd + 9, 3.5 * u))
            g.append(poly([(bx, by), (bx + 26 * u, by - 14 * u), (bx + 26 * u, by + 14 * u)], bowtie, sd + 10, 3.5 * u))
    # head
    g.append(P(wellipse(hx, hy, rx, ry, sd + 4, 2.0 * u), skin, INK, lw_head))
    if hair: g.append(_hair(hair, hx, hy, rx, ry, k, hcol, sd + 5))
    if hat: g.append(_hat(hat, hx, hy, rx, ry, k, sd + 6, hat_color))
    # face
    lx = look * 22 * u
    ex1, ex2, ey = hx - 14 * u + lx, hx + 38 * u + lx, hy - 18 * u
    if eyes == "dot":
        for ex in (ex1, ex2): g.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{6.5*u:.1f}" ry="{7.5*u:.1f}" fill="{INK}"/>')
    elif eyes == "closed":
        for ex in (ex1, ex2): g.append(P(f"M{ex-10*u:.1f},{ey+3*u:.1f} Q{ex:.1f},{ey-9*u:.1f} {ex+10*u:.1f},{ey+3*u:.1f}", "none", INK, 4.5 * u))
    elif eyes == "wide":
        for ex in (ex1, ex2):
            g.append(ell(ex, ey, 14 * u, 16 * u, WHITE, sd + 11, 3.5 * u)); g.append(f'<circle cx="{ex+lx*0.2:.1f}" cy="{ey+2*u:.1f}" r="{6*u:.1f}" fill="{INK}"/>')
    elif eyes == "x":
        for ex in (ex1, ex2): g.append(xmark(ex, ey, 8 * u, sd + 12, 4 * u, INK))
    elif eyes == "money":
        for ex in (ex1, ex2): g.append(T(ex, ey + 12 * u, "$", 36 * u, DGREEN, 700))
    if glasses == "round":
        for ex in (ex1, ex2): g.append(ell(ex, ey, 19 * u, 17 * u, "none", sd + 13, 3.6 * u))
        g.append(P(f"M{ex1+19*u:.1f},{ey:.1f} L{ex2-19*u:.1f},{ey:.1f}", "none", INK, 3.6 * u))
    elif glasses == "sun":
        for ex in (ex1, ex2): g.append(rect(ex - 22 * u, ey - 13 * u, 44 * u, 26 * u, INK, sd + 14, 3 * u, r=8 * u))
        g.append(P(f"M{ex1+20*u:.1f},{ey-4*u:.1f} L{ex2-20*u:.1f},{ey-4*u:.1f}", "none", INK, 4 * u))
    if brow:
        b = {"raise": [((-12, -22), (12, -30)), ((-12, -16), (12, -14))], "worried": [((-12, -14), (12, -22)), ((-12, -22), (12, -14))],
             "angry": [((-12, -26), (12, -16)), ((-12, -16), (12, -26))], "up": [((-12, -26), (12, -28)), ((-12, -28), (12, -26))]}[brow]
        for ex, ((x0, y0), (x1, y1)) in zip((ex2, ex1) if brow == "raise" else (ex1, ex2), b):
            g.append(P(f"M{ex+x0*u:.1f},{ey+y0*u:.1f} L{ex+x1*u:.1f},{ey+y1*u:.1f}", "none", INK, 4 * u))
    mx, my = hx - 8 * u + lx * 0.6, hy + 34 * u
    m = mouth
    if m == "smile": g.append(P(f"M{mx-34*u:.1f},{my-6*u:.1f} Q{mx-6*u:.1f},{my+20*u:.1f} {mx+26*u:.1f},{my+2*u:.1f}", "none", INK, 5 * u))
    elif m in ("open", "grin"):
        g.append(P(f"M{mx-34*u:.1f},{my-6*u:.1f} Q{mx-4*u:.1f},{my-2*u:.1f} {mx+28*u:.1f},{my-6*u:.1f} Q{mx+16*u:.1f},{my+34*u:.1f} {mx-8*u:.1f},{my+30*u:.1f} Q{mx-30*u:.1f},{my+22*u:.1f} {mx-34*u:.1f},{my-6*u:.1f} Z", PINK, INK, 4.5 * u))
        if m == "grin": g.append(P(f"M{mx-28*u:.1f},{my+1*u:.1f} L{mx+22*u:.1f},{my+1*u:.1f}", "none", INK, 2.5 * u))
    elif m == "o": g.append(f'<ellipse cx="{mx+2*u:.1f}" cy="{my+8*u:.1f}" rx="{17*u:.1f}" ry="{22*u:.1f}" fill="{PINK}" stroke="{INK}" stroke-width="{5*u:.1f}"/>')
    elif m == "frown": g.append(P(f"M{mx-30*u:.1f},{my+14*u:.1f} Q{mx-2*u:.1f},{my-8*u:.1f} {mx+24*u:.1f},{my+12*u:.1f}", "none", INK, 5 * u))
    elif m == "flat": g.append(P(wobble([(mx - 26 * u, my + 6 * u), (mx + 22 * u, my + 4 * u)], sd + 8, 1.0 * u), "none", INK, 5 * u))
    elif m == "smirk": g.append(P(f"M{mx-24*u:.1f},{my+8*u:.1f} Q{mx+4*u:.1f},{my+12*u:.1f} {mx+26*u:.1f},{my-6*u:.1f}", "none", INK, 5 * u))
    elif m == "wavy": g.append(P(f"M{mx-30*u:.1f},{my+6*u:.1f} q{8*u:.1f},{-10*u:.1f} {15*u:.1f},0 t{15*u:.1f},0 t{15*u:.1f},0 t{15*u:.1f},0", "none", INK, 4.5 * u))
    elif m == "teeth":
        g.append(rect(mx - 30 * u, my - 4 * u, 56 * u, 22 * u, WHITE, sd + 15, 4 * u, r=6 * u))
        for xx in (-12, 2, 16): g.append(P(f"M{mx+xx*u:.1f},{my-4*u:.1f} L{mx+xx*u:.1f},{my+18*u:.1f}", "none", INK, 2.5 * u))
    if mustache: g.append(P(f"M{mx-30*u:.1f},{my-6*u:.1f} Q{mx-14*u:.1f},{my-22*u:.1f} {mx:.1f},{my-10*u:.1f} Q{mx+14*u:.1f},{my-22*u:.1f} {mx+30*u:.1f},{my-6*u:.1f} Q{mx:.1f},{my-2*u:.1f} {mx-30*u:.1f},{my-6*u:.1f} Z", hcol if hair_color != "black" else INK, INK, 3 * u))
    if sweat: g.append(P(f"M{hx+rx*0.92:.1f},{hy-ry*0.45:.1f} q{-14*u:.1f},{26*u:.1f} 0,{34*u:.1f} q{14*u:.1f},{-8*u:.1f} 0,{-34*u:.1f} Z", LBLUE, INK, 3 * u))
    if blush:
        for ex in (ex1 - 12 * u, ex2 + 12 * u): g.append(f'<ellipse cx="{ex:.1f}" cy="{ey+30*u:.1f}" rx="{14*u:.1f}" ry="{7*u:.1f}" fill="#F4A6A6" opacity="0.8"/>')
    # props in the right hand (index 1) unless noted
    if prop and body:
        hxp, hyp = hands.get(1, (60 * u, 200 * u))
        if prop == "mic":
            g.append(P(f"M{hxp:.1f},{hyp+10*u:.1f} L{hxp+8*u:.1f},{hyp-26*u:.1f}", "none", INK, 7 * u))
            g.append(ell(hxp + 10 * u, hyp - 34 * u, 10 * u, 11 * u, "#333333", sd + 16, 3 * u))
        elif prop == "pointer":
            g.append(P(wobble([(hxp - 30 * u, hyp + 18 * u), (hxp + 190 * u, hyp - 70 * u)], sd + 17, 1.0 * u), "none", "#5A4038", 4.5 * u))
        elif prop == "phone":
            g.append(rect(hxp - 12 * u, hyp - 40 * u, 26 * u, 44 * u, "#333333", sd + 18, 3 * u, r=4 * u))
        elif prop == "gavel":
            g.append(P(f"M{hxp:.1f},{hyp:.1f} L{hxp+30*u:.1f},{hyp-56*u:.1f}", "none", BROWN, 9 * u))
            g.append(rect(hxp + 8 * u, hyp - 82 * u, 52 * u, 30 * u, BROWN, sd + 19, 3.5 * u, r=5 * u))
        elif prop == "coffee":
            g.append(rect(hxp - 14 * u, hyp - 30 * u, 30 * u, 34 * u, WHITE, sd + 20, 3.5 * u, r=3 * u))
            g.append(P(f"M{hxp+16*u:.1f},{hyp-22*u:.1f} q{14*u:.1f},{4*u:.1f} 0,{16*u:.1f}", "none", INK, 3.5 * u))
            for s in (-6, 6): g.append(P(f"M{hxp+s*u:.1f},{hyp-40*u:.1f} q{6*u:.1f},{-10*u:.1f} 0,{-20*u:.1f}", "none", GREY, 3 * u))
        elif prop == "money":
            g.append(G(rect(-34 * u, -18 * u, 68 * u, 36 * u, "#8DC891", sd + 21, 3.5 * u) + T(0, 12 * u, "$", 34 * u, DGREEN, 700), hxp + 10 * u, hyp - 6 * u, rot=-20))
        elif prop == "bag":
            g.append(G(money_bag_svg(sd + 22, 0.55 * k), hxp + 10 * u, hyp + 20 * u))
        elif prop == "sign":
            w = sign_w * k
            g.append(P(f"M{hxp:.1f},{hyp+30*u:.1f} L{hxp:.1f},{hyp-120*u:.1f}", "none", BROWN, 7 * u))
            g.append(rect(hxp - w / 2, hyp - 240 * u, w, 120 * u, WHITE, sd + 23, 4.5 * u))
            g.append(TL(hxp, hyp - 190 * u, prop_text.split("|"), 34 * u, RED, 700, lh=1.0))
        elif prop == "paper":
            g.append(G(rect(-30 * u, -40 * u, 60 * u, 80 * u, WHITE, sd + 24, 3.5 * u) + "".join(P(f"M{-18*u:.1f},{yy*u:.1f} L{18*u:.1f},{yy*u:.1f}", "none", GREY, 3 * u) for yy in (-22, -8, 6, 20)), hxp + 6 * u, hyp - 20 * u, rot=8))
        elif prop == "whistle":
            g.append(ell(hxp + 6 * u, hyp - 6 * u, 14 * u, 10 * u, "#C0C0C0", sd + 25, 3 * u))
    out = "".join(g)
    return G(out, sx=-1, sy=1) if flip else out

def money_bag_svg(seed=0, k=1.0):
    u = k * U; sd = seed * 1000 + 300
    body = [(-40 * u, -20 * u), (-62 * u, 20 * u), (-58 * u, 62 * u), (0, 78 * u), (58 * u, 62 * u), (62 * u, 20 * u), (40 * u, -20 * u)]
    return (P(wobble(body, sd, 2 * u, 20 * u, closed=True), MONEY, INK, 5 * u) +
            poly([(-26 * u, -24 * u), (-34 * u, -56 * u), (-12 * u, -44 * u), (0, -60 * u), (12 * u, -44 * u), (34 * u, -56 * u), (26 * u, -24 * u)], MONEY, sd + 1, 4.5 * u) +
            rect(-30 * u, -30 * u, 60 * u, 12 * u, "#4E6B52", sd + 2, 4 * u, r=4 * u) +
            T(0, 50 * u, "$", 70 * u, GOLD, 700, stroke=1.5 * u))
