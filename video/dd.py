"""Doodle drawing primitives (SVG strings). All coordinates in px @1920x1080.
Every primitive takes `seed`; two seeds of the same drawing = the A/B "line boil" pair."""
import math, random, os
from PIL import ImageFont

INK = "#111111"; WHITE = "#FFFFFF"; SKIN = "#FCD4B4"; SKIN2 = "#E9C9A6"; SKIN3 = "#C99872"; SKIN4 = "#8D5B3E"
RED = "#E4141C"; ARED = "#C8232A"; GREEN = "#1BB935"; DGREEN = "#2E8B3E"; BOARD = "#337A3C"; FRAME = "#785743"
YELLOW = "#F2D21B"; HILITE = "#F7E04A"; BLUE = "#3663BB"; LBLUE = "#7AB3DD"; NAVY = "#233265"; ORANGE = "#E8743B"
GREY = "#9A9A9A"; LGREY = "#D9D9D9"; DGREY = "#555555"; PARCH = "#E8D9B5"; MONEY = "#6E8F72"; GOLD = "#E8B923"
PINK = "#E8A0A0"; BROWN = "#8B5A3C"; LBROWN = "#C49A6C"; PURPLE = "#7D5BA6"; TEAL = "#1F8A9E"; CREAM = "#FFF6E0"
OUT = 6.0  # default outline width

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONT_FILES = [os.path.join(FONT_DIR, f) for f in ("Gaegu-Regular-Latin.ttf", "Gaegu-Bold-Latin.ttf", "ComicNeue-Bold.ttf", "ComicNeue-Regular.ttf")]
_pil_fonts = {}

def text_w(s, size, weight=700, family="Gaegu", spacing=0.0):
    key = (family, weight, int(size))
    if key not in _pil_fonts:
        fn = {("Gaegu", 400): "Gaegu-Regular-Latin.ttf", ("Gaegu", 700): "Gaegu-Bold-Latin.ttf",
              ("Comic Neue", 700): "ComicNeue-Bold.ttf", ("Comic Neue", 400): "ComicNeue-Regular.ttf"}[(family, 400 if weight < 600 else 700)]
        _pil_fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, fn), int(size))
    return _pil_fonts[key].getlength(s) + spacing * max(0, len(s) - 1)

def rng(seed): return random.Random(seed)

def _f(v): return f"{v:.1f}"

def catmull(pts, closed=False):
    if len(pts) < 2: return ""
    if len(pts) == 2:
        return f"M{_f(pts[0][0])},{_f(pts[0][1])} L{_f(pts[1][0])},{_f(pts[1][1])}"
    P = (pts[-1:] + pts + pts[:2]) if closed else ([pts[0]] + pts + [pts[-1]])
    n = len(pts) if closed else len(pts) - 1
    d = f"M{_f(P[1][0])},{_f(P[1][1])}"
    for i in range(n):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{_f(c1[0])},{_f(c1[1])} {_f(c2[0])},{_f(c2[1])} {_f(p2[0])},{_f(p2[1])}"
    return d + (" Z" if closed else "")

def resample(pts, step, closed=False):
    pp = pts + [pts[0]] if closed else pts
    out = []
    for (x0, y0), (x1, y1) in zip(pp[:-1], pp[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step))
        for k in range(n): out.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, (x1 - x0) / (L or 1), (y1 - y0) / (L or 1)))
    if not closed: out.append((pp[-1][0], pp[-1][1], 0, 0))
    return out

def wobble(pts, seed, amp=1.8, step=34, closed=False, corners=True):
    """Hand-drawn polyline/polygon path: resample + perpendicular jitter (corners kept sharp-ish)."""
    r = rng(seed); out = []
    for i, (x, y, dx, dy) in enumerate(resample(pts, step, closed)):
        j = r.uniform(-amp, amp)
        if not closed and (i == 0): j = 0
        out.append((x - dy * j, y + dx * j))
    if corners and not closed:
        return catmull(out)
    return catmull(out, closed)

def wpoly(pts, seed, amp=1.8, step=40):
    """Closed polygon with straight-ish edges & slightly wobbly lines (keeps corners)."""
    r = rng(seed); out = []
    pp = pts + [pts[0]]
    for (x0, y0), (x1, y1) in zip(pp[:-1], pp[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step))
        nx, ny = -(y1 - y0) / (L or 1), (x1 - x0) / (L or 1)
        out.append((x0 + r.uniform(-amp, amp) * 0.4, y0 + r.uniform(-amp, amp) * 0.4))
        for k in range(1, n):
            j = r.uniform(-amp, amp); t = k / n
            out.append((x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j))
    d = f"M{_f(out[0][0])},{_f(out[0][1])}"
    # quadratic smoothing between mid-edge points but keep vertices
    for p in out[1:]: d += f" L{_f(p[0])},{_f(p[1])}"
    return d + " Z"

def wrect(x, y, w, h, seed, amp=1.8, r=0):
    if r <= 0: return wpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], seed, amp)
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(5):
            a = math.radians(a0 + k * 22.5); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return wobble(pts, seed, amp, 60, closed=True)

def wellipse(cx, cy, rx, ry, seed, amp=2.0, n=None):
    r = rng(seed); n = n or max(12, int((rx + ry) / 9)); pts = []
    for k in range(n):
        a = 2 * math.pi * k / n; f = 1 + r.uniform(-amp, amp) / max(rx, ry, 1)
        pts.append((cx + rx * math.cos(a) * f, cy + ry * math.sin(a) * f))
    return catmull(pts, closed=True)

def P(d, fill="none", stroke=INK, w=OUT, op=1.0, cap="round", extra=""):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    s = f' stroke="{stroke}" stroke-width="{w:.1f}" stroke-linecap="{cap}" stroke-linejoin="round"' if stroke and w > 0 else ' stroke="none"'
    return f'<path d="{d}" fill="{fill}"{s}{o}{extra}/>'

def line(pts, seed=0, w=OUT, color=INK, amp=1.4, step=30):
    return P(wobble(pts, seed, amp, step), "none", color, w)

def rect(x, y, w, h, fill=WHITE, seed=0, sw=OUT, stroke=INK, r=0, amp=1.6):
    return P(wrect(x, y, w, h, seed, amp, r), fill, stroke, sw)

def ell(cx, cy, rx, ry, fill=WHITE, seed=0, sw=OUT, stroke=INK, amp=1.6):
    return P(wellipse(cx, cy, rx, ry, seed, amp), fill, stroke, sw)

def poly(pts, fill=WHITE, seed=0, sw=OUT, stroke=INK, amp=1.6):
    return P(wpoly(pts, seed, amp), fill, stroke, sw)

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def T(x, y, s, size=60, color=INK, weight=700, anchor="middle", family="Gaegu", spacing=1.0, op=1.0, stroke=0.0, rot=0):
    """Text; y = baseline. stroke>0 adds faux-bold outline in the same colour."""
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    st = f' stroke="{color}" stroke-width="{stroke:.1f}" stroke-linejoin="round"' if stroke > 0 else ""
    tr = f' transform="rotate({rot:.1f} {x:.1f} {y:.1f})"' if rot else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size:.1f}" fill="{color}"'
            f' text-anchor="{anchor}" letter-spacing="{spacing:.1f}"{st}{o}{tr}>{esc(s)}</text>')

def TL(x, y, lines, size=60, color=INK, weight=700, anchor="middle", lh=1.15, chars=None, **kw):
    """Multi-line text block, y = baseline of first line; `chars` = typewriter count across lines."""
    out = []; left = 10**9 if chars is None else chars
    for i, ln in enumerate(lines):
        if left <= 0: break
        s = ln[:left]; left -= len(ln) + 1
        out.append(T(x, y + i * size * lh, s, size, color, weight, anchor, **kw))
    return "".join(out)

def G(content, tx=0.0, ty=0.0, s=1.0, rot=0.0, op=1.0, sx=None, sy=None):
    tr = []
    if tx or ty: tr.append(f"translate({tx:.1f} {ty:.1f})")
    if rot: tr.append(f"rotate({rot:.2f})")
    if sx is not None or sy is not None: tr.append(f"scale({(sx if sx is not None else s):.4f} {(sy if sy is not None else s):.4f})")
    elif s != 1: tr.append(f"scale({s:.4f})")
    t = f' transform="{" ".join(tr)}"' if tr else ""
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f"<g{t}{o}>{content}</g>"

def arrow(x0, y0, x1, y1, seed=0, w=9, color=ARED, head=34, curve=0.0):
    """Hand-drawn arrow (optionally curved) with open V head."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / L * curve, my + ny / L * curve
    pts = [(x0 + (cx - x0) * t * 2, y0 + (cy - y0) * t * 2) if t <= 0.5 else (cx + (x1 - cx) * (t - 0.5) * 2, cy + (y1 - cy) * (t - 0.5) * 2) for t in [k / 8 for k in range(9)]]
    shaft = P(wobble(pts, seed, 1.2, 40), "none", color, w)
    ang = math.atan2(y1 - pts[-3][1], x1 - pts[-3][0])
    a1 = ang + math.radians(152); a2 = ang - math.radians(152)
    hd = P(f"M{_f(x1 + head * math.cos(a1))},{_f(y1 + head * math.sin(a1))} L{_f(x1)},{_f(y1)} L{_f(x1 + head * math.cos(a2))},{_f(y1 + head * math.sin(a2))}", "none", color, w)
    return shaft + hd

def xmark(cx, cy, r, seed=0, w=14, color=ARED):
    return P(wobble([(cx - r, cy - r), (cx + r, cy + r)], seed, 3, 40), "none", color, w) + P(wobble([(cx + r, cy - r), (cx - r, cy + r)], seed + 1, 3, 40), "none", color, w)

def check(cx, cy, r, seed=0, w=16, color=GREEN):
    return P(wobble([(cx - r, cy), (cx - r * 0.3, cy + r * 0.7), (cx + r, cy - r * 0.8)], seed, 2, 30), "none", color, w)

def circle_mark(cx, cy, rx, ry, seed=0, w=7, color=ARED):
    """Rough red ellipse that overshoots (hand-drawn emphasis circle)."""
    r = rng(seed); pts = []
    n = 26
    for k in range(n + 3):
        a = 2 * math.pi * k / n - 0.4; f = 1 + r.uniform(-0.05, 0.05) + 0.04 * k / n
        pts.append((cx + rx * math.cos(a) * f, cy + ry * math.sin(a) * f))
    return P(catmull(pts), "none", color, w)

def underline(x0, x1, y, seed=0, w=7, color=ARED):
    return P(wobble([(x0, y), (x1, y + 3)], seed, 2.5, 40), "none", color, w)

def star_burst(cx, cy, r, fill=YELLOW, seed=0, n=12):
    pts = []
    for k in range(2 * n):
        a = math.pi * k / n; rr = r if k % 2 == 0 else r * 0.72
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return poly(pts, fill, seed, 5)
