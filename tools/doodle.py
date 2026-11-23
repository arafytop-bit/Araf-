"""Procedural doodle kit (prototype) reproducing the explainer style.
All coordinates are in 1920x1080 space. Every primitive takes a `seed` so a second
seed produces the A/B "line boil" variant."""
import math, random

FONT_DIR = None  # set by caller
INK = "#111111"; SKIN = "#FCD4B4"; RED = "#E4141C"; ARROW_RED = "#C13725"
BOARD = "#337A3C"; FRAME = "#785743"; GREEN = "#1BB935"; MOUTH_PINK = "#E8A0A0"
S = 1.5  # 720p -> 1080p scale for measured values

def _rng(seed): return random.Random(seed)

def _catmull(pts, closed=False):
    if len(pts) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    P = pts + pts[:3] if closed else [pts[0]] + pts + [pts[-1]]
    d = f"M{P[1][0]:.1f},{P[1][1]:.1f}" if not closed else f"M{P[0][0]:.1f},{P[0][1]:.1f}"
    rng = range(0, len(P) - 3) if closed else range(0, len(P) - 3)
    for i in rng:
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if closed and i == 0: d = f"M{p1[0]:.1f},{p1[1]:.1f}"
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + (" Z" if closed else "")

def wobble_line(pts, seed, amp=2.2, step=40):
    """Resample a polyline every `step` px and jitter perpendicular -> hand-drawn stroke."""
    r = _rng(seed); out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step))
        nx, ny = (-(y1 - y0) / (L or 1), (x1 - x0) / (L or 1))
        for k in range(n):
            t = k / n; j = r.uniform(-amp, amp) if out else 0
            out.append((x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j))
    out.append(pts[-1]); return _catmull(out)

def wobble_ellipse(cx, cy, rx, ry, seed, amp=2.5, n=28, squash=0.0):
    r = _rng(seed); pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        f = 1 + r.uniform(-amp, amp) / max(rx, ry)
        top = 1 + squash * max(0, -math.sin(a))  # slightly broader top
        pts.append((cx + rx * math.cos(a) * f * top, cy + ry * math.sin(a) * f))
    return _catmull(pts, closed=True)

def stroke(d, w, color=INK, fill="none"):
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'

def text(x, y, s, size, color=INK, weight=400, anchor="start", family="Gaegu", spacing=0.5):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size:.1f}" '
            f'fill="{color}" text-anchor="{anchor}" letter-spacing="{spacing}">{s}</text>')

# ---------------------------------------------------------------- narrator
MOUTHS = ("smile", "open", "o", "frown", "flat", "smirk")
POSES = ("hips", "hip_one", "think", "arms_up", "shrug", "present", "teacher", "mic")

def narrator(cx, top, scale=1.0, pose="hips", mouth="smile", brow=None, seed=0):
    """cx = head centre x, top = top of head (px @1080p). Scale 1.0 = solo-shot size (figure ~740 px tall)."""
    k = scale * S; g = []
    hx, hy, rx, ry = cx, top + 93 * k, 99 * k, 93 * k
    lw_head, lw_body = 5.5 * k, 6.0 * k
    sd = seed * 1000
    # body first (behind head)
    neck = (hx - 4 * k, hy + ry - 4 * k); hip = (hx - 2 * k, hy + ry + 175 * k)
    g.append(stroke(wobble_line([neck, hip], sd + 1, 1.6 * k), lw_body))
    lf = (hip[0] - 46 * k, hip[1] + 100 * k); rf = (hip[0] + 46 * k, hip[1] + 100 * k)
    g.append(stroke(wobble_line([lf, hip, rf], sd + 2, 1.6 * k), lw_body))
    sh = (hx - 3 * k, hy + ry + 45 * k)
    arms = {
        "hips":    [[sh, (sh[0] - 36 * k, sh[1] + 32 * k), (sh[0] - 4 * k, sh[1] + 62 * k)], [sh, (sh[0] + 34 * k, sh[1] + 30 * k), (sh[0] + 4 * k, sh[1] + 60 * k)]],
        "hip_one": [[sh, (sh[0] - 36 * k, sh[1] + 32 * k), (sh[0] - 4 * k, sh[1] + 62 * k)], [sh, (sh[0] + 30 * k, sh[1] + 50 * k), (sh[0] + 52 * k, sh[1] + 70 * k)]],
        "think":   [[sh, (sh[0] - 30 * k, sh[1] + 40 * k), (sh[0] + 2 * k, sh[1] + 52 * k)], [sh, (sh[0] + 44 * k, sh[1] + 24 * k), (sh[0] + 40 * k, sh[1] - 22 * k)]],
        "arms_up": [[sh, (sh[0] - 60 * k, sh[1] - 40 * k), (sh[0] - 95 * k, sh[1] - 95 * k)], [sh, (sh[0] + 60 * k, sh[1] - 40 * k), (sh[0] + 100 * k, sh[1] - 90 * k)]],
        "shrug":   [[sh, (sh[0] - 50 * k, sh[1] + 30 * k), (sh[0] - 90 * k, sh[1] + 5 * k)], [sh, (sh[0] + 50 * k, sh[1] + 30 * k), (sh[0] + 92 * k, sh[1] + 2 * k)]],
        "present": [[sh, (sh[0] - 36 * k, sh[1] + 32 * k), (sh[0] - 4 * k, sh[1] + 62 * k)], [sh, (sh[0] + 60 * k, sh[1] + 10 * k), (sh[0] + 120 * k, sh[1] - 10 * k)]],
        "teacher": [[sh, (sh[0] - 36 * k, sh[1] + 32 * k), (sh[0] - 4 * k, sh[1] + 62 * k)], [sh, (sh[0] + 46 * k, sh[1] + 26 * k), (sh[0] + 80 * k, sh[1] + 10 * k)]],
        "mic":     [[sh, (sh[0] - 36 * k, sh[1] + 32 * k), (sh[0] - 4 * k, sh[1] + 62 * k)], [sh, (sh[0] + 34 * k, sh[1] + 40 * k), (sh[0] + 50 * k, sh[1] + 4 * k)]],
    }[pose]
    for i, a in enumerate(arms): g.append(stroke(wobble_line(a, sd + 3 + i, 1.4 * k, 18 * k), lw_body))
    if pose == "teacher":  # pointer stick
        hand = arms[1][-1]
        g.append(stroke(wobble_line([(hand[0] - 30 * k, hand[1] + 18 * k), (hand[0] + 190 * k, hand[1] - 70 * k)], sd + 9, 1.0 * k), 4.5 * k, "#5A4038"))
    if pose == "mic":
        hand = arms[1][-1]
        g.append(stroke(f"M{hand[0]:.1f},{hand[1]+10*k:.1f} L{hand[0]+8*k:.1f},{hand[1]-26*k:.1f}", 7 * k))
        g.append(f'<ellipse cx="{hand[0]+10*k:.1f}" cy="{hand[1]-34*k:.1f}" rx="{10*k:.1f}" ry="{11*k:.1f}" fill="#333" stroke="{INK}" stroke-width="{3*k:.1f}"/>')
    # head
    g.append(stroke(wobble_ellipse(hx, hy, rx, ry, sd + 4, 2.0 * k, squash=0.04), lw_head, INK, SKIN))
    # hair: messy scribble patch on the top-left (irregular spikes + texture strokes), thicker on the left
    r = _rng(sd + 5); outer = []; inner = []
    a0, a1 = -172.0, -52.0; n = 22
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n); u = i / n
        thick = 0.20 - 0.12 * u            # thicker on the left side
        spike = r.uniform(0.0, 0.16) * (1.0 if i % 2 else 0.25)
        rr = 1.0 + thick * 0.55 + spike
        outer.append((hx + rx * math.cos(a) * rr + r.uniform(-3, 3) * k, hy + ry * math.sin(a) * rr + r.uniform(-3, 3) * k))
        ri = 0.86 + 0.08 * u + r.uniform(-0.02, 0.02)
        inner.append((hx + rx * math.cos(a) * ri, hy + ry * math.sin(a) * ri))
    poly = outer + inner[::-1]
    g.append(f'<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + f' Z" fill="{INK}" stroke="{INK}" stroke-width="{2.5*k:.1f}" stroke-linejoin="round"/>')
    for j in range(7):  # stray strands sticking out
        a = math.radians(r.uniform(a0 + 5, a1 - 5)); L = r.uniform(0.10, 0.22)
        b0 = (hx + rx * math.cos(a) * 1.02, hy + ry * math.sin(a) * 1.02)
        b1 = (hx + rx * math.cos(a + r.uniform(-0.25, 0.25)) * (1.02 + L), hy + ry * math.sin(a + r.uniform(-0.25, 0.25)) * (1.02 + L))
        g.append(stroke(f"M{b0[0]:.1f},{b0[1]:.1f} L{b1[0]:.1f},{b1[1]:.1f}", 3.2 * k))
    # eyes
    ex1, ex2, ey = hx - 14 * k, hx + 38 * k, hy - 18 * k
    for ex in (ex1, ex2):
        g.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{6.5*k:.1f}" ry="{7.5*k:.1f}" fill="{INK}"/>')
    if brow == "raise":
        g.append(stroke(wobble_line([(ex2 - 14 * k, ey - 22 * k), (ex2 + 12 * k, ey - 30 * k)], sd + 6, 0.8 * k), 4 * k))
        g.append(stroke(wobble_line([(ex1 - 12 * k, ey - 16 * k), (ex1 + 12 * k, ey - 14 * k)], sd + 7, 0.8 * k), 4 * k))
    elif brow == "worried":
        g.append(stroke(wobble_line([(ex1 - 12 * k, ey - 14 * k), (ex1 + 12 * k, ey - 22 * k)], sd + 6, 0.8 * k), 4 * k))
        g.append(stroke(wobble_line([(ex2 - 12 * k, ey - 22 * k), (ex2 + 12 * k, ey - 14 * k)], sd + 7, 0.8 * k), 4 * k))
    # mouth
    mx, my = hx - 8 * k, hy + 34 * k
    if mouth == "smile":
        g.append(stroke(f"M{mx-34*k:.1f},{my-6*k:.1f} Q{mx-6*k:.1f},{my+20*k:.1f} {mx+26*k:.1f},{my+2*k:.1f}", 5 * k))
    elif mouth == "open":
        g.append(f'<path d="M{mx-34*k:.1f},{my-6*k:.1f} Q{mx-4*k:.1f},{my-2*k:.1f} {mx+28*k:.1f},{my-6*k:.1f} Q{mx+16*k:.1f},{my+34*k:.1f} {mx-8*k:.1f},{my+30*k:.1f} Q{mx-30*k:.1f},{my+22*k:.1f} {mx-34*k:.1f},{my-6*k:.1f} Z" fill="{MOUTH_PINK}" stroke="{INK}" stroke-width="{4.5*k:.1f}" stroke-linejoin="round"/>')
    elif mouth == "o":
        g.append(f'<ellipse cx="{mx+2*k:.1f}" cy="{my+8*k:.1f}" rx="{17*k:.1f}" ry="{22*k:.1f}" fill="{MOUTH_PINK}" stroke="{INK}" stroke-width="{5*k:.1f}"/>')
    elif mouth == "frown":
        g.append(stroke(f"M{mx-30*k:.1f},{my+14*k:.1f} Q{mx-2*k:.1f},{my-8*k:.1f} {mx+24*k:.1f},{my+12*k:.1f}", 5 * k))
    elif mouth == "flat":
        g.append(stroke(wobble_line([(mx - 26 * k, my + 6 * k), (mx + 22 * k, my + 4 * k)], sd + 8, 1.0 * k), 5 * k))
    elif mouth == "smirk":
        g.append(stroke(f"M{mx-24*k:.1f},{my+8*k:.1f} Q{mx+4*k:.1f},{my+12*k:.1f} {mx+26*k:.1f},{my-6*k:.1f}", 5 * k))
    return "\n".join(g)

# ---------------------------------------------------------------- props
def chalkboard(x, y, w, h, lines=(), seed=0, size=58):
    sd = seed * 1000 + 50; g = []
    fr = 40
    g.append(stroke(wobble_line([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], sd, 1.6, 60), 7, INK, FRAME))
    g.append(stroke(wobble_line([(x + fr, y + fr), (x + w - fr, y + fr), (x + w - fr, y + h - fr), (x + fr, y + h - fr), (x + fr, y + fr)], sd + 1, 1.4, 60), 5, INK, BOARD))
    n = len(lines)
    for i, ln in enumerate(lines):
        yy = y + h / 2 + (i - (n - 1) / 2) * size * 1.2 + size * 0.35
        g.append(text(x + w / 2, yy, ln, size, "#F4F4F4", 400, "middle"))
    return "\n".join(g)

def red_ellipse(cx, cy, rx, ry, seed=0, w=6):
    return stroke(wobble_ellipse(cx, cy, rx, ry, seed * 1000 + 70, 6, 24), w, "#C8232A")

def red_x(cx, cy, r, seed=0, w=9):
    sd = seed * 1000 + 80
    return stroke(wobble_line([(cx - r, cy - r), (cx + r, cy + r)], sd, 3), w, ARROW_RED) + stroke(wobble_line([(cx + r, cy - r), (cx - r, cy + r)], sd + 1, 3), w, ARROW_RED)

def svg_doc(body, W=1920, H=1080, bg="#FFFFFF"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>'
