"""Doodle prop library. Every asset: fn(seed=0, **kw) -> SVG string drawn around the origin (px @1080p)."""
import math, json, os
from dd import *
from chars import person, money_bag_svg, U

REG = {}
def asset(fn):
    REG[fn.__name__] = fn; return fn

REG["person"] = person

# ------------------------------------------------------------------ buildings & grid
@asset
def house(seed=0, color="#E9C46A", roof=ARED, w=240, sad=False, bill=False):
    h = w * 0.62; sd = seed * 1000 + 100
    s = rect(-w / 2, -h / 2, w, h, color, sd, 5)
    s += poly([(-w / 2 - 22, -h / 2 + 4), (0, -h / 2 - w * 0.42), (w / 2 + 22, -h / 2 + 4)], roof, sd + 1, 5)
    s += rect(-w * 0.12, h / 2 - h * 0.55, w * 0.24, h * 0.55, BROWN, sd + 2, 4)
    for x in (-w * 0.36, w * 0.2):
        s += rect(x, -h * 0.25, w * 0.17, w * 0.15, LBLUE, sd + 3 + int(x), 4)
    if bill: s += G(envelope(seed, w=110, label=""), w * 0.42, h * 0.38, rot=-12)
    return s

@asset
def apartment(seed=0, color="#B9C6D3", floors=5, w=230):
    fh = 70; h = floors * fh + 30; sd = seed * 1000 + 110
    s = rect(-w / 2, -h, w, h, color, sd, 5)
    for f in range(floors):
        for c in range(3):
            s += rect(-w / 2 + 24 + c * 66, -h + 24 + f * fh, 40, 38, LBLUE, sd + 3 + f * 3 + c, 3.5)
    return G(s, 0, h / 2)

@asset
def city(seed=0, w=520):
    sd = seed * 1000 + 120; s = ""
    specs = [(-0.42, 0.55, "#AFC2D6"), (-0.2, 0.85, "#C9D3DD"), (0.02, 0.62, "#9FB4C8"), (0.22, 1.0, "#BCCADB"), (0.42, 0.5, "#AAB9C9")]
    for i, (x, hh, c) in enumerate(specs):
        bw = w * 0.2; bh = w * 0.6 * hh
        s += rect(w * x - bw / 2, -bh, bw, bh, c, sd + i, 4.5)
        for r in range(int(bh // 46)):
            for cc in range(2):
                s += rect(w * x - bw / 2 + 14 + cc * (bw / 2 - 6), -bh + 16 + r * 46, bw / 2 - 26, 24, YELLOW if (r + cc + i) % 3 == 0 else "#E8EEF4", sd + 40 + i * 20 + r * 2 + cc, 2.5)
    return G(s, 0, w * 0.3)

@asset
def data_center(seed=0, w=440, ghost=False, label="DATA CENTER", lights=True, x_over=False):
    h = w * 0.5; sd = seed * 1000 + 130
    if ghost:
        s = f'<g stroke-dasharray="18 14">{P(wrect(-w/2, -h/2, w, h, sd, 1.4), "none", GREY, 5)}{P(wrect(-w*0.42, -h/2 - 46, w*0.3, 46, sd+1, 1.2), "none", GREY, 4)}{P(wrect(w*0.1, -h/2 - 46, w*0.3, 46, sd+2, 1.2), "none", GREY, 4)}</g>'
        return s + (T(0, 16, "?", 120, GREY, 700) if True else "")
    s = rect(-w * 0.42, -h / 2 - 46, w * 0.3, 50, "#9AA5B1", sd + 1, 4.5) + rect(w * 0.1, -h / 2 - 46, w * 0.3, 50, "#9AA5B1", sd + 2, 4.5)
    for i, x in enumerate((-w * 0.37, -w * 0.25, w * 0.15, w * 0.27)):
        s += ell(x + 22, -h / 2 - 21, 16, 14, "#D7DEE5", sd + 5 + i, 3.5)
    s += rect(-w / 2, -h / 2, w, h, "#D5DCE3", sd, 5.5)
    rows = 3; cols = 6
    for r in range(rows):
        for c in range(cols):
            x = -w / 2 + 26 + c * (w - 52) / cols; y = -h / 2 + 26 + r * (h - 70) / rows
            s += rect(x, y, (w - 52) / cols - 14, (h - 70) / rows - 16, "#3A4250", sd + 10 + r * 10 + c, 3)
            if lights:
                for k in range(2): s += f'<circle cx="{x + 12 + k * 14:.1f}" cy="{y + 12:.1f}" r="4.5" fill="{GREEN if (r + c + k) % 3 else "#4FC3F7"}"/>'
    if label: s += rect(-w * 0.3, h / 2 - 38, w * 0.6, 34, WHITE, sd + 3, 3.5) + T(0, h / 2 - 12, label, 30, INK, 700, spacing=2)
    if x_over: s += xmark(0, 0, w * 0.45, sd + 9, 16)
    return s

@asset
def server_rack(seed=0, h=360, face=False, legs=False, hat=False, mouth="smile"):
    w = h * 0.5; sd = seed * 1000 + 140
    s = ""
    if legs:
        for x in (-w * 0.25, w * 0.25): s += line([(x, h / 2 - 10), (x * 1.3, h / 2 + 90)], sd + 50 + int(x), 9)
    s += rect(-w / 2, -h / 2, w, h, "#3A3F47", sd, 5.5, r=10)
    for i in range(7 if not face else 4):
        y = -h / 2 + 22 + i * (h - 40) / 7 + (h * 0.42 if face else 0)
        s += rect(-w / 2 + 16, y, w - 32, (h - 40) / 7 - 10, "#5A616B", sd + 10 + i, 2.5)
        s += f'<circle cx="{w/2 - 34:.1f}" cy="{y + 12:.1f}" r="5" fill="{GREEN}"/><circle cx="{w/2 - 52:.1f}" cy="{y + 12:.1f}" r="5" fill="#4FC3F7"/>'
    if face:
        s += f'<circle cx="{-w*0.18:.1f}" cy="{-h*0.28:.1f}" r="11" fill="{WHITE}"/><circle cx="{w*0.18:.1f}" cy="{-h*0.28:.1f}" r="11" fill="{WHITE}"/>'
        if mouth == "smile": s += P(f"M{-w*0.2:.1f},{-h*0.16:.1f} Q0,{-h*0.06:.1f} {w*0.2:.1f},{-h*0.16:.1f}", "none", WHITE, 6)
        else: s += P(f"M{-w*0.2:.1f},{-h*0.1:.1f} Q0,{-h*0.2:.1f} {w*0.2:.1f},{-h*0.1:.1f}", "none", WHITE, 6)
    if hat: s += poly([(-w * 0.28, -h / 2 + 4), (0, -h / 2 - 120), (w * 0.28, -h / 2 + 4)], "#F26CA7", sd + 3, 4.5) + ell(0, -h / 2 - 120, 16, 16, YELLOW, sd + 4, 3.5)
    return s

@asset
def warehouse(seed=0, w=620, servers=True):
    h = w * 0.42; sd = seed * 1000 + 150
    s = poly([(-w / 2, -h / 2), (-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h / 2), (0, -h / 2 - 90)], "#C7B299", sd, 5.5)
    for i, x in enumerate((-w * 0.3, 0, w * 0.3)):
        s += rect(x - w * 0.11, -h * 0.05, w * 0.22, h * 0.55, "#7C8794", sd + 1 + i, 4)
        if servers: s += G(server_rack(seed + i, 110), x, h * 0.2)
    return s

@asset
def power_plant(seed=0, kind="gas", w=360, face=False, mouth="smile", cane=False, smoke=True, money=False, eyes="dot"):
    sd = seed * 1000 + 160; s = ""
    if kind == "nuclear":
        s += cooling_tower(seed, w * 0.62)
        s = G(s, -w * 0.12, 0) + rect(w * 0.12, w * 0.05, w * 0.34, w * 0.28, "#C9C2B6", sd + 1, 5)
        fx, fy = -w * 0.12, -w * 0.05
    else:
        for i, x in enumerate((-w * 0.32, -w * 0.12)):
            s += rect(x - 18, -w * 0.62, 36, w * 0.5, "#B0A79A", sd + 2 + i, 4.5) + rect(x - 18, -w * 0.62, 36, 18, ARED, sd + 6 + i, 3.5)
            if smoke:
                for j in range(3): s += ell(x + 10 + j * 22, -w * 0.72 - j * 34, 26 + j * 8, 20 + j * 6, "#E6E6E6", sd + 10 + i * 5 + j, 4)
        s += poly([(-w / 2, -w * 0.12), (-w / 2, w * 0.32), (w / 2, w * 0.32), (w / 2, -w * 0.02), (w * 0.18, -w * 0.2), (w * 0.18, -w * 0.02), (-w * 0.12, -w * 0.2), (-w * 0.12, -w * 0.12)], "#D9CFC1" if kind != "coal" else "#A89F94", sd, 5.5)
        for i in range(4): s += rect(-w * 0.42 + i * w * 0.22, w * 0.17, w * 0.12, w * 0.1, YELLOW, sd + 20 + i, 3.5)
        fx, fy = -w * 0.02, w * 0.06
    if face:
        s += f'<circle cx="{fx - w*0.1:.1f}" cy="{fy - w*0.05:.1f}" r="{w*0.028:.1f}" fill="{INK}"/><circle cx="{fx + w*0.1:.1f}" cy="{fy - w*0.05:.1f}" r="{w*0.028:.1f}" fill="{INK}"/>' if eyes == "dot" else ""
        if eyes == "closed":
            for ex in (fx - 34, fx + 34): s += P(f"M{ex-12:.1f},{fy-26:.1f} Q{ex:.1f},{fy-40:.1f} {ex+12:.1f},{fy-26:.1f}", "none", INK, 5)
        if mouth == "smile": s += P(f"M{fx-36:.1f},{fy+4:.1f} Q{fx:.1f},{fy+30:.1f} {fx+36:.1f},{fy+4:.1f}", "none", INK, 6)
        elif mouth == "frown": s += P(f"M{fx-30:.1f},{fy+22:.1f} Q{fx:.1f},{fy-2:.1f} {fx+30:.1f},{fy+22:.1f}", "none", INK, 6)
        elif mouth == "flat": s += P(f"M{fx-30:.1f},{fy+14:.1f} L{fx+30:.1f},{fy+14:.1f}", "none", INK, 6)
        elif mouth == "open": s += P(f"M{fx-34:.1f},{fy-8:.1f} Q{fx:.1f},{fy-2:.1f} {fx+34:.1f},{fy-8:.1f} Q{fx:.1f},{fy+40:.1f} {fx-34:.1f},{fy-8:.1f} Z", PINK, INK, 5)
    if cane:
        s += P(wobble([(w * 0.56, w * 0.32), (w * 0.6, -w * 0.12)], sd + 30, 1), "none", BROWN, 9) + P(f"M{w*0.6:.1f},{-w*0.12:.1f} q{-6:.1f},{-34:.1f} {-34:.1f},{-26:.1f}", "none", BROWN, 9)
        s += line([(w * 0.5, 0), (w * 0.6, -w * 0.06)], sd + 31, 7)
    if money:
        s += G(money_bag_svg(seed + 3, 0.55), w * 0.5, w * 0.22)
    return s

@asset
def cooling_tower(seed=0, w=260, steam=True, done=1.0, state="ok"):
    """Hyperboloid cooling tower. done<1 -> built up to that height (jagged top) + dashed outline of the planned shape."""
    sd = seed * 1000 + 170; h = w * 1.15
    # outline profile: (y, half-width) from base to top
    prof = [(h / 2, w * 0.5), (h * 0.2, w * 0.36), (-h * 0.05, w * 0.27), (-h * 0.3, w * 0.29), (-h / 2, w * 0.36)]
    def hw(y):
        for (y0, a), (y1, b) in zip(prof[:-1], prof[1:]):
            if y1 <= y <= y0: return a + (b - a) * (y0 - y) / (y0 - y1)
        return prof[-1][1]
    full = [(-x, y) for y, x in prof] + [(x, y) for y, x in prof[::-1]]
    s = ""
    if done >= 1:
        if steam and state == "ok":
            for j in range(3): s += ell(-w * 0.15 + j * w * 0.15, -h / 2 - 30 - j * 26, w * 0.2, w * 0.13, "#F0F0F0", sd + 10 + j, 4)
        s += P(catmull(full, closed=True), "#CFC9BF", INK, 5.5)
        s += ell(0, -h / 2, w * 0.36, w * 0.06, "#8E877C", sd + 1, 4.5)
        s += P(f"M{-w*0.27:.1f},{-h*0.05:.1f} Q0,{h*0.02:.1f} {w*0.27:.1f},{-h*0.05:.1f}", "none", "#A39C90", 3.5)
    else:
        s += f'<g stroke-dasharray="14 12">{P(catmull(full, closed=True), "none", "#B0A89C", 4)}</g>'
        top = h / 2 - h * max(0.05, done)
        left = [(-hw(y), y) for y in [h / 2 - (h * done) * k / 8 for k in range(9)]]
        right = [(hw(y), y) for y in [top + (h * done) * k / 8 for k in range(9)]]
        r = rng(sd); n = 9; zig = []
        for k in range(n + 1):   # jagged unfinished rim
            x = hw(top) - 2 * hw(top) * k / n
            zig.append((x, top + (r.uniform(4, 16) if k % 2 else -r.uniform(0, 6))))
        s += P("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in left + zig[::-1][1:-1] + right) + " Z", "#CFC9BF", INK, 5.5)
        for i in range(3):       # scaffold around the rim
            xx = -hw(top) * 1.05 + i * hw(top) * 1.05
            s += P(f"M{xx:.1f},{top - 30:.1f} L{xx:.1f},{top + 70:.1f}", "none", BROWN, 4)
        s += P(f"M{-hw(top)*1.15:.1f},{top - 24:.1f} L{hw(top)*1.15:.1f},{top - 24:.1f}", "none", BROWN, 4)
    if state == "x": s += xmark(0, 0, w * 0.5, sd + 2, 16)
    if state == "cobweb": s += cobweb(seed, w * 0.42, -w * 0.25, -h * 0.05 if done < 1 else -h * 0.25)
    if state == "check": s += check(0, -h * 0.1, w * 0.3, sd + 3)
    return s

@asset
def tower(seed=0, h=380, wires=False):
    sd = seed * 1000 + 180; w = h * 0.45; c = "#6E7781"
    legs = [(-w * 0.45, h / 2), (-w * 0.1, -h / 2), (w * 0.1, -h / 2), (w * 0.45, h / 2)]
    s = line([legs[0], legs[1]], sd, 6, c) + line([legs[3], legs[2]], sd + 1, 6, c) + line([legs[1], legs[2]], sd + 2, 5, c)
    for i in range(5):
        y0 = h / 2 - i * h * 0.2; y1 = y0 - h * 0.2
        f0 = 0.45 - 0.35 * (i / 5); f1 = 0.45 - 0.35 * ((i + 1) / 5)
        s += line([(-w * f0, y0), (w * f1, y1)], sd + 10 + i, 3.5, c) + line([(w * f0, y0), (-w * f1, y1)], sd + 20 + i, 3.5, c)
    for j, y in enumerate((-h * 0.36, -h * 0.18)):
        s += line([(-w * 0.75, y), (w * 0.75, y)], sd + 30 + j, 6, c)
        for x in (-w * 0.7, w * 0.7): s += line([(x, y), (x, y + 30)], sd + 40 + j + int(x), 5, INK)
    return s

@asset
def wires(seed=0, x0=0, y0=0, x1=600, y1=0, sag=50, n=2, color=INK):
    s = ""
    for k in range(n):
        dy = k * 34
        pts = [(x0 + (x1 - x0) * t / 10, y0 + dy + (y1 - y0) * t / 10 + sag * 4 * (t / 10) * (1 - t / 10)) for t in range(11)]
        s += P(catmull(pts), "none", color, 4)
    return s

@asset
def substation(seed=0, w=400):
    sd = seed * 1000 + 190; h = w * 0.5; s = ""
    for i, x in enumerate((-w * 0.3, 0, w * 0.3)):
        s += rect(x - w * 0.1, -h * 0.2, w * 0.2, h * 0.45, "#9CA6B0", sd + i, 4.5)
        for f in range(3): s += P(f"M{x - w*0.07 + f * w*0.07:.1f},{-h*0.15:.1f} L{x - w*0.07 + f * w*0.07:.1f},{h*0.2:.1f}", "none", "#6B747D", 3)
        for j in (-1, 1): s += rect(x + j * w * 0.05 - 7, -h * 0.45, 14, h * 0.25, "#B6D3E8", sd + 10 + i * 2 + j, 3)
    s += line([(-w * 0.45, -h * 0.42), (w * 0.45, -h * 0.42)], sd + 20, 4)
    # fence
    s += line([(-w / 2, h * 0.32), (w / 2, h * 0.32)], sd + 21, 4, DGREY)
    for i in range(13):
        x = -w / 2 + i * w / 12; s += line([(x, h * 0.32), (x, h * 0.05)], sd + 30 + i, 3.5, DGREY)
    s += line([(-w / 2, h * 0.08), (w / 2, h * 0.08)], sd + 22, 3.5, DGREY)
    return s

@asset
def pole(seed=0, h=360):
    sd = seed * 1000 + 200
    return (rect(-10, -h / 2, 20, h, BROWN, sd, 4.5) + rect(-70, -h / 2 + 28, 140, 16, BROWN, sd + 1, 4) +
            "".join(rect(x - 6, -h / 2 + 8, 12, 22, "#B6D3E8", sd + 2 + i, 3) for i, x in enumerate((-56, 0, 56))))

@asset
def extension_cord(seed=0, x0=-500, y0=0, x1=500, y1=0, sag=60, color="#F28C28", w=16):
    sd = seed * 1000 + 210
    pts = [(x0 + (x1 - x0) * t / 12, y0 + (y1 - y0) * t / 12 + sag * 4 * (t / 12) * (1 - t / 12) + (14 * math.sin(t * 1.7) if 0 < t < 12 else 0)) for t in range(13)]
    s = P(catmull(pts), "none", INK, w + 8) + P(catmull(pts), "none", color, w)
    s += G(rect(-34, -26, 52, 52, color, sd, 5, r=8) + line([(18, -12), (40, -12)], sd + 1, 6) + line([(18, 12), (40, 12)], sd + 2, 6), x1 - 6, y1)
    s += G(rect(-30, -34, 60, 68, color, sd + 3, 5, r=8) + rect(-14, -16, 8, 14, INK, sd + 4, 2) + rect(6, -16, 8, 14, INK, sd + 5, 2), x0, y0)
    return s

# ------------------------------------------------------------------ money & paper
@asset
def money_bag(seed=0, k=1.0, fire=False, wings=False):
    s = money_bag_svg(seed, k)
    if fire:
        s += G(flame(seed + 1, 90 * k, "#F28C28"), -48 * k, -46 * k) + G(flame(seed + 2, 70 * k, "#F28C28"), 44 * k, -30 * k)
    if wings:
        for sx in (-1, 1):
            s += G(poly([(0, 0), (60, -40), (120, -20), (80, 0), (110, 20), (40, 20)], WHITE, seed * 1000 + 220 + sx, 4.5), sx * 60 * k, -10 * k, sx=sx * k, sy=k)
    return s

@asset
def cash(seed=0, n=1, w=200):
    s = ""
    for i in range(n):
        s += G(rect(-w / 2, -w * 0.23, w, w * 0.46, "#8DC891", seed * 1000 + 230 + i, 5) + ell(0, 0, w * 0.16, w * 0.16, "#C7E8C9", seed * 1000 + 240 + i, 3.5) + T(0, w * 0.1, "$", w * 0.26, DGREEN, 700), (i % 3) * 30 - 30, -i * 22, rot=(i * 7) % 13 - 6)
    return s

@asset
def coin(seed=0, r=140, text="HEADS", sub="", color=GOLD):
    sd = seed * 1000 + 250
    return ell(0, 0, r, r, color, sd, 6) + ell(0, 0, r * 0.82, r * 0.82, "none", sd + 1, 4, "#B8891A") + T(0, 14 if not sub else -4, text, r * 0.3, INK, 700) + (T(0, r * 0.32, sub, r * 0.17, INK, 700) if sub else "")

@asset
def chips(seed=0, n=4, color=RED):
    s = ""
    for i in range(n):
        s += ell(0, -i * 22, 70, 22, color if i % 2 == 0 else BLUE, seed * 1000 + 260 + i, 4.5)
    return s

@asset
def envelope(seed=0, w=300, label="ELECTRIC BILL", color=WHITE, heavy=False):
    h = w * 0.62; sd = seed * 1000 + 270
    s = rect(-w / 2, -h / 2, w, h, color, sd, 5.5)
    s += line([(-w / 2, -h / 2), (0, h * 0.08), (w / 2, -h / 2)], sd + 1, 5)
    if label:
        s += rect(-w * 0.36, h * 0.12, w * 0.72, h * 0.26, "#EEF3F8", sd + 2, 3.5) + T(0, h * 0.3, label, w * 0.085, INK, 700, spacing=1)
    s += rect(w * 0.27, -h * 0.4, w * 0.16, w * 0.16, "#F6D36B", sd + 3, 3.5) + bolt(seed, w * 0.1, w * 0.35, -h * 0.4 + w * 0.08)
    if heavy:
        for i in range(3): s += line([(-w * 0.62, -h * 0.2 + i * 30), (-w * 0.52, -h * 0.2 + i * 30)], sd + 10 + i, 5, GREY)
    return s

def bolt(seed=0, h=60, cx=0, cy=0, color=YELLOW, sw=3.5):
    k = h / 60
    pts = [(4, -30), (-14, 4), (-2, 4), (-8, 30), (14, -6), (2, -6), (8, -30)]
    return poly([(cx + x * k, cy + y * k) for x, y in pts], color, seed * 1000 + 280, sw)
REG["bolt"] = lambda seed=0, h=120, color=YELLOW: bolt(seed, h, 0, 0, color, 6)

@asset
def bill(seed=0, w=330, title="ELECTRIC BILL", items=(("Supply", "$62"), ("Delivery", "$41"), ("Capacity", "$9")), total="$112", hi=(), red_total=False, arrow_up=False, stamp_txt=None):
    h = w * 1.3; sd = seed * 1000 + 290
    s = rect(-w / 2, -h / 2, w, h, WHITE, sd, 5.5)
    s += rect(-w / 2, -h / 2, w, h * 0.17, "#2F5D8A", sd + 1, 5) + T(0, -h / 2 + h * 0.12, title, w * 0.095, WHITE, 700, spacing=1)
    y = -h / 2 + h * 0.3
    for i, (a, b) in enumerate(items):
        if i in hi: s += rect(-w / 2 + 14, y - w * 0.075, w - 28, w * 0.1, HILITE, sd + 10 + i, 0, stroke=None)
        s += T(-w / 2 + 26, y, a, w * 0.075, INK, 700, "start") + T(w / 2 - 26, y, b, w * 0.075, INK, 700, "end", family="Comic Neue")
        y += h * 0.13
    s += line([(-w / 2 + 20, y - h * 0.05), (w / 2 - 20, y - h * 0.05)], sd + 3, 4)
    s += T(-w / 2 + 26, y + h * 0.04, "TOTAL", w * 0.085, INK, 700, "start") + T(w / 2 - 26, y + h * 0.04, total, w * 0.1, RED if red_total else INK, 700, "end", family="Comic Neue")
    if arrow_up: s += arrow(w * 0.62, h * 0.32, w * 0.62, -h * 0.2, sd + 5, 12, RED, 40)
    if stamp_txt: s += stamp(seed, stamp_txt, w=w * 0.9)
    return s

@asset
def doc(seed=0, w=270, title="", lines=5, big="", big_color=RED, sub="", color=WHITE, stamp_txt=None, stamp_color=ARED, scroll=False, title_size=None, sig=False):
    h = w * 1.3; sd = seed * 1000 + 300
    if scroll:
        s = rect(-w / 2, -h / 2, w, h, PARCH, sd, 5.5)
        s += ell(0, -h / 2, w * 0.56, 22, PARCH, sd + 1, 5) + ell(0, h / 2, w * 0.56, 22, PARCH, sd + 2, 5)
    else:
        s = poly([(-w / 2, -h / 2), (w / 2 - 44, -h / 2), (w / 2, -h / 2 + 44), (w / 2, h / 2), (-w / 2, h / 2)], color, sd, 5.5)
        s += line([(w / 2 - 44, -h / 2), (w / 2 - 44, -h / 2 + 44), (w / 2, -h / 2 + 44)], sd + 3, 4)
    y = -h / 2 + (h * 0.17 if title else h * 0.12)
    if title:
        ts = title_size or min(w * 0.13, (w - 30) / max(1, len(title)) * 1.75)
        s += T(0, y, title, ts, INK, 700); y += h * 0.1
    if big:
        s += T(0, y + h * 0.17, big, w * 0.3, big_color, 700); y += h * 0.26
    if sub:
        s += TL(0, y, sub.split("|"), w * 0.085, INK, 700); y += h * 0.08 * len(sub.split("|"))
    r = rng(sd + 4)
    for i in range(lines):
        yy = y + i * h * 0.085
        if yy > h / 2 - 30: break
        x1 = w / 2 - 30 - r.uniform(0, w * 0.3)
        s += P(wobble([(-w / 2 + 30, yy), (x1, yy)], sd + 10 + i, 3, 16), "none", DGREY, 4)
    if sig: s += P(f"M{-w*0.3:.1f},{h*0.38:.1f} c20,-30 30,20 50,-6 s30,24 60,-10 s20,10 40,0", "none", BLUE, 4)
    if stamp_txt: s += stamp(seed, stamp_txt, stamp_color, w=w * 0.95)
    return s

@asset
def stamp(seed=0, text="CANCELLED", color=ARED, w=320, rot=-14, size=None):
    size = size or min(70, w * 1.6 / max(4, len(text)))
    tw = text_w(text, size, 700) + 40; h = size * 1.35
    return G(rect(-tw / 2, -h / 2, tw, h, "none", seed * 1000 + 310, 7, color, r=10) + T(0, size * 0.35, text, size, color, 700, spacing=3), rot=rot)

@asset
def calendar(seed=0, w=230, top="JUNE", big="2024", top_color=ARED, big_size=None, x_over=False):
    h = w * 1.0; sd = seed * 1000 + 320
    s = rect(-w / 2, -h / 2, w, h, WHITE, sd, 5.5) + rect(-w / 2, -h / 2, w, h * 0.27, top_color, sd + 1, 5.5)
    for x in (-w * 0.25, w * 0.25): s += rect(x - 8, -h / 2 - 22, 16, 44, LGREY, sd + 2 + int(x), 4, r=6)
    s += T(0, -h / 2 + h * 0.2, top, w * 0.14, WHITE, 700, spacing=1)
    if big: s += T(0, h * 0.27, big, big_size or min(w * 0.36, w * 1.2 / max(1, len(big))), INK, 700)
    else:
        for r in range(3):
            for c in range(4): s += rect(-w * 0.38 + c * w * 0.2, -h * 0.12 + r * h * 0.2, w * 0.13, h * 0.12, "#F3F3F3", sd + 10 + r * 4 + c, 2.5)
    if x_over: s += xmark(0, 0, w * 0.4, sd + 5, 14)
    return s

@asset
def ballot_box(seed=0, w=300, x_over=False):
    sd = seed * 1000 + 330; h = w * 0.8
    s = G(rect(-w * 0.22, -60, w * 0.44, 120, WHITE, sd + 1, 4.5) + check(0, -10, 30, sd + 2, 9, BLUE), 0, -h / 2 - 10, rot=-8)
    s += rect(-w / 2, -h / 2, w, h, "#4A6FA5", sd, 5.5) + rect(-w * 0.3, -h / 2 - 6, w * 0.6, 18, INK, sd + 3, 3)
    s += T(0, h * 0.12, "VOTE", w * 0.2, WHITE, 700, spacing=4)
    if x_over: s += xmark(0, 0, w * 0.5, sd + 4, 16)
    return s

@asset
def gavel(seed=0, w=260):
    sd = seed * 1000 + 340
    return (G(rect(-w * 0.04, -w * 0.5, w * 0.08, w * 0.62, BROWN, sd, 5) + rect(-w * 0.22, -w * 0.62, w * 0.44, w * 0.18, BROWN, sd + 1, 5, r=10), rot=-35) +
            rect(-w * 0.32, w * 0.3, w * 0.64, w * 0.12, LBROWN, sd + 2, 5, r=6))

# ------------------------------------------------------------------ boards, bubbles, cards, text
@asset
def chalkboard(seed=0, w=1060, h=660, lines=(), size=110, chars=None, strike=(), color="#F4F4F4", align="middle"):
    sd = seed * 1000 + 350; fr = 40
    s = rect(-w / 2, -h / 2, w, h, FRAME, sd, 7) + rect(-w / 2 + fr, -h / 2 + fr, w - 2 * fr, h - 2 * fr, BOARD, sd + 1, 5)
    n = len(lines); left = 10**9 if chars is None else chars
    x = 0 if align == "middle" else -w / 2 + fr + 50
    for i, ln in enumerate(lines):
        if left <= 0: break
        yy = (i - (n - 1) / 2) * size * 1.22 + size * 0.33
        sub = ln[:left]; left -= len(ln) + 1
        s += T(x, yy, sub, size, color, 400, align, spacing=2)
        if i in strike:
            tw = text_w(ln, size, 400, spacing=2); x0 = x - tw / 2 if align == "middle" else x
            s += line([(x0 - 10, yy - size * 0.3), (x0 + tw + 10, yy - size * 0.32)], sd + 10 + i, 6, color)
    return s

@asset
def bubble(seed=0, lines=("Hello!",), w=420, h=260, size=56, tail="left", color=INK, fill=WHITE, chars=None, think=False):
    sd = seed * 1000 + 360
    tails = {"left": [(-w * 0.28, h * 0.32), (-w * 0.62, h * 0.62), (-w * 0.1, h * 0.42)],
             "right": [(w * 0.28, h * 0.32), (w * 0.62, h * 0.62), (w * 0.1, h * 0.42)],
             "down": [(-w * 0.08, h * 0.44), (-w * 0.18, h * 0.8), (w * 0.1, h * 0.44)],
             "downl": [(-w * 0.2, h * 0.4), (-w * 0.42, h * 0.78), (-w * 0.02, h * 0.46)]}
    s = ""
    if think:
        for i, (dx, dy, r) in enumerate(((-w * 0.38, h * 0.62, 26), (-w * 0.5, h * 0.82, 16))): s += ell(dx, dy, r, r, fill, sd + 20 + i, 5)
    else:
        s += poly(tails[tail], fill, sd + 1, 6)
    s += ell(0, 0, w / 2, h / 2, fill, sd, 6)
    if not think: s += P(wobble(tails[tail][:1] + [tails[tail][2]], sd + 2, 0.5), "none", fill, 9)   # hide seam
    s += TL(0, -(len(lines) - 1) * size * 0.58 + size * 0.33, list(lines), size, color, 700, chars=chars)
    return s

@asset
def note(seed=0, lines=("note",), size=40, color=INK, weight=400, chars=None, anchor="middle", rot=0):
    return G(TL(0, 0, list(lines) if not isinstance(lines, str) else lines.split("|"), size, color, weight, anchor, chars=chars, spacing=1.5), rot=rot)

@asset
def hero(seed=0, text="TEXT", size=200, color=INK, lead=None, lead_size=64, lead_color=INK, chars=None, sub=None, sub_size=60, sub_color=INK, stroke=None, lh=1.05):
    lines = text.split("|"); s = ""
    y0 = 0
    if lead:
        s += T(0, -size * 0.85, lead, lead_size, lead_color, 400, spacing=2)
    s += TL(0, y0 + size * 0.35 - (len(lines) - 1) * size * lh / 2, lines, size, color, 700, lh=lh, chars=chars, spacing=size * 0.04, stroke=stroke if stroke is not None else size * 0.02)
    if sub: s += T(0, size * 0.35 + (len(lines) - 1) * size * lh / 2 + sub_size * 1.4, sub, sub_size, sub_color, 400, spacing=2)
    return s

@asset
def label(seed=0, text="The ugly", size=64, color=RED, chars=None):
    return T(0, 0, text if chars is None else text[:chars], size, color, 700, "start", spacing=2)

@asset
def card(seed=0, kicker="SURVEY", big="81%", sub="of people saw|their bill go up", source="", w=860, big_color=YELLOW, dark=True, big_size=None):
    lines = sub.split("|") if sub else []
    h = 150 + (big_size or 190) * (1 if big else 0) + 64 * len(lines) + (50 if source else 0)
    sd = seed * 1000 + 370
    bg, fg, kc = ("#1E2A44", WHITE, "#8FB8FF") if dark else (WHITE, INK, BLUE)
    s = rect(-w / 2, -h / 2, w, h, bg, sd, 6, r=24)
    y = -h / 2 + 80
    s += T(-w / 2 + 50, y, kicker, 44, kc, 700, "start", spacing=3)
    y += 30
    if big:
        bs = big_size or 190
        s += T(0, y + bs * 0.82, big, bs, big_color, 700, family="Comic Neue"); y += bs + 10
    for ln in lines:
        y += 58; s += T(0, y, ln, 54, fg, 700)
    if source: s += T(w / 2 - 40, h / 2 - 30, source, 30, "#AAB4C8" if dark else DGREY, 400, "end")
    return s

@asset
def quote_card(seed=0, lines=("Quote",), who="", role="", w=1300, chars=None, size=78):
    n = len(lines); h = 160 + n * size * 1.2 + 120; sd = seed * 1000 + 380
    s = rect(-w / 2, -h / 2, w, h, CREAM, sd, 6, r=22)
    s += T(-w / 2 + 70, -h / 2 + 150, "“", 220, "#D9C7A0", 700, family="Comic Neue")
    s += TL(0, -h / 2 + 130, list(lines), size, INK, 700, chars=chars)
    if who: s += T(w / 2 - 60, h / 2 - 90, "- " + who, 52, INK, 700, "end")
    if role: s += T(w / 2 - 60, h / 2 - 40, role, 38, DGREY, 400, "end")
    return s

@asset
def checklist(seed=0, items=("One", "Two"), checks=(), size=64, w=900, crosses=()):
    sd = seed * 1000 + 390; s = ""
    for i, it in enumerate(items):
        y = i * size * 1.6
        s += rect(-w / 2, y - size * 0.75, size * 0.9, size * 0.9, WHITE, sd + i, 5)
        if i in checks: s += check(-w / 2 + size * 0.45, y - size * 0.3, size * 0.45, sd + 20 + i, 10)
        if i in crosses: s += xmark(-w / 2 + size * 0.45, y - size * 0.3, size * 0.35, sd + 40 + i, 10)
        s += T(-w / 2 + size * 1.3, y, it, size, INK, 700, "start", spacing=1.5)
    return s

@asset
def browser(seed=0, w=1200, h=640, url="utility-commission.gov", query="large load tariff", chars=None):
    sd = seed * 1000 + 400
    s = rect(-w / 2, -h / 2, w, h, WHITE, sd, 6, r=18) + rect(-w / 2, -h / 2, w, 70, "#E4E8EE", sd + 1, 6, r=18)
    for i, c in enumerate((RED, YELLOW, GREEN)): s += ell(-w / 2 + 40 + i * 34, -h / 2 + 35, 11, 11, c, sd + 2 + i, 3)
    s += rect(-w / 2 + 160, -h / 2 + 14, w - 220, 42, WHITE, sd + 6, 3.5, r=20) + T(-w / 2 + 185, -h / 2 + 46, url, 30, DGREY, 400, "start", family="Comic Neue")
    q = query if chars is None else query[:chars]
    s += rect(-w * 0.36, -h * 0.12, w * 0.72, 90, WHITE, sd + 7, 5, r=45) + T(-w * 0.32, -h * 0.12 + 60, q + ("|" if chars is not None and chars < len(query) else ""), 52, INK, 700, "start")
    s += G(magnifier(seed, 60), w * 0.31, -h * 0.12 + 45)
    for i in range(3): s += line([(-w * 0.36, h * 0.12 + i * 60), (w * (0.2 - 0.1 * i), h * 0.12 + i * 60)], sd + 20 + i, 6, LGREY)
    return s

@asset
def magnifier(seed=0, r=60):
    sd = seed * 1000 + 410
    return line([(r * 0.6, r * 0.6), (r * 1.4, r * 1.4)], sd, 12, BROWN) + ell(0, 0, r * 0.75, r * 0.75, "#DDEFFF", sd + 1, 6)

@asset
def comment_form(seed=0, w=520, chars=None, text="Please don't make|me pay for this.", glow=False):
    h = w * 1.15; sd = seed * 1000 + 420
    s = ""
    if glow: s += ell(0, 0, w * 0.75, h * 0.66, "#FFF3B0", sd + 9, 0, None)
    s += rect(-w / 2, -h / 2, w, h, WHITE, sd, 6) + T(0, -h / 2 + 70, "PUBLIC COMMENT", w * 0.085, INK, 700, spacing=2)
    s += rect(-w / 2 + 30, -h / 2 + 110, w - 60, h * 0.5, "#F5F7FA", sd + 1, 4)
    s += TL(-w / 2 + 50, -h / 2 + 170, text.split("|"), w * 0.07, BLUE, 400, "start", chars=chars)
    s += rect(w * 0.05, h / 2 - 110, w * 0.38, 70, GREEN, sd + 2, 5, r=12) + T(w * 0.24, h / 2 - 63, "SEND", 40, WHITE, 700, spacing=2)
    return s

@asset
def subscribe_btn(seed=0, w=520, pressed=False):
    sd = seed * 1000 + 430; h = w * 0.26
    c = "#9E9E9E" if pressed else RED
    s = rect(-w / 2, -h / 2, w, h, c, sd, 6, r=h / 2) + T(-w * 0.06, h * 0.17, "SUBSCRIBED" if pressed else "SUBSCRIBE", h * 0.45, WHITE, 700, spacing=3)
    s += G(bell(seed, h * 0.55), w / 2 + h * 0.75, 0)
    return s

@asset
def bell(seed=0, h=120):
    sd = seed * 1000 + 440
    return (poly([(-h * 0.35, h * 0.25), (-h * 0.3, -h * 0.15), (0, -h * 0.42), (h * 0.3, -h * 0.15), (h * 0.35, h * 0.25)], YELLOW, sd, 5) +
            ell(0, h * 0.34, h * 0.12, h * 0.1, YELLOW, sd + 1, 4))

# ------------------------------------------------------------------ charts
@asset
def bar_chart(seed=0, title="", bars=(), vmax=600, w=1300, h=620, shown=None, p=1.0, cap=None, cap_label="PRICE CAP", ghost=None,
              ghost_label="", unit="", hi=None, val_size=46, lab_size=40, show_vals=True):
    sd = seed * 1000 + 450; s = ""
    n = len(bars); shown = n if shown is None else int(shown)
    x0, x1, y0 = -w / 2 + 40, w / 2 - 40, h / 2 - 60
    if title: s += T(0, -h / 2 - 20, title, 54, INK, 700, spacing=1.5)
    if unit: s += T(-w / 2 + 40, -h / 2 + 30, unit, 32, DGREY, 400, "start")
    bw = (x1 - x0) / max(1, n) * 0.58
    for i, b in enumerate(bars[:shown]):
        lab, val, col = b[0], b[1], b[2]; vt = b[3] if len(b) > 3 else None
        cx = x0 + (i + 0.5) * (x1 - x0) / n
        frac = (p if i == shown - 1 else 1.0)
        bh = (h - 140) * val / vmax * frac
        if bh > 2: s += rect(cx - bw / 2, y0 - bh, bw, bh, col, sd + 10 + i, 5, amp=1.2)
        if show_vals and vt and frac >= 0.999:
            s += T(cx, y0 - bh - 22, vt, val_size, RED if hi == i else INK, 700, family="Comic Neue")
        s += TL(cx, y0 + 50, lab.split("|"), lab_size, INK, 700, lh=1.0)
    if ghost is not None and shown >= ghost[0] + 1:
        i, gv = ghost; cx = x0 + (i + 0.5) * (x1 - x0) / n; bh = (h - 140) * gv / vmax
        s += f'<g stroke-dasharray="16 12">{P(wrect(cx - bw/2, y0 - bh, bw, bh, sd + 40, 1.0), "none", ARED, 5)}</g>'
        if ghost_label: s += T(cx, y0 - bh - 22, ghost_label, val_size * 0.9, ARED, 700)
    if cap is not None:
        cy = y0 - (h - 140) * cap / vmax
        s += f'<g stroke-dasharray="22 14">{P(f"M{x0:.1f},{cy:.1f} L{x1:.1f},{cy:.1f}", "none", ARED, 6)}</g>'
        s += T(x1, cy - 16, cap_label, 40, ARED, 700, "end")
    s += line([(x0 - 10, y0), (x1 + 10, y0)], sd + 1, 6)
    return s

@asset
def line_chart(seed=0, pts=((0, 0.1), (0.25, 0.25), (0.5, 0.45), (0.75, 0.7), (1.0, 0.95)), w=900, h=520, p=1.0, color=ARED, title="", xlab="", ylab="",
               pts2=None, color2=BLUE, label1="", label2="", gap=False):
    sd = seed * 1000 + 460; s = ""
    x0, y0, x1, y1 = -w / 2, h / 2, w / 2, -h / 2
    s += line([(x0, y1), (x0, y0), (x1, y0)], sd, 6)
    if title: s += T(0, -h / 2 - 30, title, 50, INK, 700)
    def path_of(pp, prog):
        q = [(x0 + px * w, y0 - py * h) for px, py in pp if px <= prog + 1e-6]
        if prog < 1 and len(q) < len(pp):
            k = len(q); a = pp[k - 1]; b = pp[k]; t = (prog - a[0]) / max(1e-6, b[0] - a[0])
            q.append((x0 + (a[0] + (b[0] - a[0]) * t) * w, y0 - (a[1] + (b[1] - a[1]) * t) * h))
        return q
    q = path_of(list(pts), p)
    if gap and pts2:
        q2 = [(x0 + px * w, y0 - py * h) for px, py in pts2]
        s += P("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in q + q2[::-1]) + " Z", "#F7C9C9", "none", 0, op=0.9)
    if len(q) >= 2: s += line(q, sd + 1, 9, color, 1.0, 40)
    if pts2:
        q2 = [(x0 + px * w, y0 - py * h) for px, py in pts2]
        s += f'<g stroke-dasharray="20 14">{P(catmull(q2), "none", color2, 8)}</g>'
    if label1 and len(q) >= 2: s += T(q[-1][0] + 20, q[-1][1] + 10, label1, 44, color, 700, "start")
    if label2 and pts2: s += T(x0 + pts2[-1][0] * w + 20, y0 - pts2[-1][1] * h + 10, label2, 44, color2, 700, "start")
    if xlab: s += T(0, h / 2 + 60, xlab, 40, DGREY, 400)
    if ylab: s += T(x0 - 20, -h / 2 + 10, ylab, 40, DGREY, 400, "end")
    return s

@asset
def stock_chart(seed=0, w=700, h=420, jump=True, color=GREEN, label=""):
    sd = seed * 1000 + 470
    r = rng(sd); pts = []; y = 0.3
    for i in range(14):
        if jump and i == 9: y += 0.38
        else: y += r.uniform(-0.04, 0.05)
        pts.append((i / 13, min(0.95, max(0.05, y))))
    s = rect(-w / 2 - 30, -h / 2 - 30, w + 60, h + 60, WHITE, sd + 1, 5, r=14)
    s += line_chart(seed, pts, w - 40, h - 40, 1.0, color)
    if label: s += T(0, -h / 2 - 50, label, 50, INK, 700)
    return s

@asset
def pie(seed=0, r=230, frac=0.12, color=ARED, base="#9BC4E2", label="", explode=0.0, label_out=True):
    sd = seed * 1000 + 480
    a0 = -math.pi / 2; a1 = a0 + 2 * math.pi * frac
    mid = (a0 + a1) / 2; ex, ey = explode * math.cos(mid), explode * math.sin(mid)
    s = ell(0, 0, r, r, base, sd, 6)
    arc = [(0, 0)] + [(r * math.cos(a0 + (a1 - a0) * t / 12), r * math.sin(a0 + (a1 - a0) * t / 12)) for t in range(13)]
    s += P(f"M{arc[0][0]:.1f},{arc[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in arc[1:]) + " Z", WHITE, "none", 0)
    s += G(P("M0,0 " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in arc[1:]) + " Z", color, INK, 6), ex, ey)
    if label:
        lx, ly = (r * 1.25 + explode) * math.cos(mid), (r * 1.25 + explode) * math.sin(mid)
        s += T(lx + (40 if label_out else 0), ly, label, 52, INK, 700, "start" if lx > 0 else "end")
    return s

@asset
def merit_order(seed=0, w=1200, h=560, demand=0.62, price_on=True, money=False):
    """Supply stack: plants sorted cheapest->priciest; demand line sets the clearing price paid to all."""
    sd = seed * 1000 + 490; s = ""
    heights = [0.12, 0.16, 0.2, 0.26, 0.34, 0.46, 0.62, 0.82]; n = len(heights)
    x0 = -w / 2; y0 = h / 2; bw = w / n
    k_last = min(n - 1, int(demand * n))
    for i, hh in enumerate(heights):
        col = "#9FC5E8" if i <= k_last else "#E3E3E3"
        s += rect(x0 + i * bw + 6, y0 - hh * h, bw - 12, hh * h, col, sd + i, 5)
        s += G(power_plant(seed + i, w=bw * 0.62, smoke=False), x0 + (i + 0.5) * bw, y0 - hh * h - bw * 0.3)
    dx = x0 + demand * w
    s += f'<g stroke-dasharray="20 14">{P(f"M{dx:.1f},{y0 + 20:.1f} L{dx:.1f},{-h/2 - 40:.1f}", "none", BLUE, 7)}</g>'
    s += T(dx, -h / 2 - 60, "FORECAST", 44, BLUE, 700)
    if price_on:
        py = y0 - heights[k_last] * h
        s += P(f"M{x0:.1f},{py:.1f} L{dx:.1f},{py:.1f}", "none", ARED, 7)
        s += T(x0 - 20, py + 14, "PRICE", 40, ARED, 700, "end")
    if money:
        for i in range(k_last + 1): s += G(money_bag_svg(seed + 30 + i, 0.32), x0 + (i + 0.5) * bw, y0 - 40)
    s += line([(x0 - 10, y0), (w / 2 + 10, y0)], sd + 30, 6)
    return s

# ------------------------------------------------------------------ maps
_US = None
def _us():
    global _US
    if _US is None: _US = json.load(open(os.path.join(os.path.dirname(__file__), "us_states.json")))
    return _US

PJM = ["Pennsylvania", "New Jersey", "Maryland", "Delaware", "Virginia", "West Virginia", "Ohio", "Kentucky", "Indiana", "Illinois", "Michigan", "North Carolina", "Tennessee", "District of Columbia"]

@asset
def us_map(seed=0, w=1500, hi=None, base="#EFEFEF", pins=(), focus=None, pad=40, sw=2.2, outline=INK, labels=(), lit=None):
    """hi: {state: colour}; focus: list of states to fit; pins: [(city, label, colour)]; lit: number of hi-states shown (in dict order)."""
    us = _us(); hi = dict(hi or {})
    if lit is not None:
        keys = list(hi.keys()); hi = {k: hi[k] for k in keys[:int(lit)]}
    if focus:
        bb = [us["states"][s]["bounds"] for s in focus]
        bx0 = min(b[0][0] for b in bb) - pad; by0 = min(b[0][1] for b in bb) - pad; bx1 = max(b[1][0] for b in bb) + pad; by1 = max(b[1][1] for b in bb) + pad
    else:
        bx0, by0, bx1, by1 = 0, 0, 975, 610
    sc = w / (bx1 - bx0); cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    body = ""
    for name, st in us["states"].items():
        if focus and name not in focus and not any(_overlap(st["bounds"], (bx0, by0, bx1, by1)) for _ in [0]): continue
        body += f'<path d="{st["d"]}" fill="{hi.get(name, base)}" stroke="{outline}" stroke-width="{sw / sc * 1.0 * 2.2:.3f}" stroke-linejoin="round"/>'
    s = f'<g transform="scale({sc:.4f}) translate({-cx:.2f} {-cy:.2f})">{body}</g>'
    for item in pins:
        city, lab = item[0], item[1]; col = item[2] if len(item) > 2 else RED
        px, py = us["cities"][city]; X = (px - cx) * sc; Y = (py - cy) * sc
        s += pin(seed, col, X, Y, 1.0) + (T(X + 34, Y - 50, lab, 46, INK, 700, "start") if lab else "")
    for (txt, sx, sy, size) in labels:
        s += T(sx, sy, txt, size, INK, 700)
    return s

def _overlap(b, box):
    return not (b[1][0] < box[0] or b[0][0] > box[2] or b[1][1] < box[1] or b[0][1] > box[3])

def pin(seed=0, color=RED, x=0, y=0, k=1.0):
    sd = seed * 1000 + 500
    return (P(f"M{x:.1f},{y:.1f} C{x-30*k:.1f},{y-40*k:.1f} {x-34*k:.1f},{y-70*k:.1f} {x:.1f},{y-80*k:.1f} C{x+34*k:.1f},{y-70*k:.1f} {x+30*k:.1f},{y-40*k:.1f} {x:.1f},{y:.1f} Z", color, INK, 4.5) +
            f'<circle cx="{x:.1f}" cy="{y-56*k:.1f}" r="{11*k:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>')
REG["pin"] = lambda seed=0, color=RED, k=1.6: pin(seed, color, 0, 40 * k, k)

@asset
def state_shape(seed=0, name="Ohio", w=520, fill="#F4D03F", text=None, text_size=70):
    st = _us()["states"][name]; (bx0, by0), (bx1, by1) = st["bounds"]
    sc = w / (bx1 - bx0); cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    s = f'<g transform="scale({sc:.4f}) translate({-cx:.2f} {-cy:.2f})"><path d="{st["d"]}" fill="{fill}" stroke="{INK}" stroke-width="{6/sc:.3f}" stroke-linejoin="round"/></g>'
    if text: s += T(0, text_size * 0.35, text, text_size, INK, 700)
    return s

# ------------------------------------------------------------------ misc props & gags
@asset
def door(seed=0, num="1", w=250, h=430, color="#5B8DBE", open_=False, inside=None):
    sd = seed * 1000 + 510
    s = rect(-w / 2 - 18, -h / 2 - 18, w + 36, h + 18, LBROWN, sd, 6)
    if open_:
        s += rect(-w / 2, -h / 2, w, h, "#2B2B2B", sd + 1, 5)
        if inside: s += inside
        s += poly([(-w / 2, -h / 2), (-w / 2 - w * 0.45, -h / 2 + 40), (-w / 2 - w * 0.45, h / 2 - 20), (-w / 2, h / 2)], color, sd + 2, 5)
    else:
        s += rect(-w / 2, -h / 2, w, h, color, sd + 1, 5)
        s += ell(w * 0.32, 20, 14, 14, GOLD, sd + 3, 4)
        s += rect(-w * 0.25, -h * 0.36, w * 0.5, w * 0.36, WHITE, sd + 4, 4, r=10) + T(0, -h * 0.36 + w * 0.29, num, w * 0.3, INK, 700, family="Comic Neue")
    return s

@asset
def table_empty(seed=0, w=520, bill=True, candle=True):
    sd = seed * 1000 + 520; s = ""
    s += G(poly([(-50, -150), (50, -150), (60, 60), (-60, 60)], "#A0522D", sd, 5), w * 0.38, -30)
    s += rect(-w / 2, -40, w * 0.8, 30, WHITE, sd + 1, 5) + line([(-w * 0.4, -10), (-w * 0.42, 150)], sd + 2, 8) + line([(w * 0.2, -10), (w * 0.22, 150)], sd + 3, 8)
    s += ell(-w * 0.12, -48, 70, 14, WHITE, sd + 4, 4)
    if candle: s += rect(-w * 0.36, -110, 22, 70, CREAM, sd + 5, 4) + G(flame(seed, 40, ORANGE), -w * 0.36 + 11, -128)
    if bill: s += G(doc(seed, 90, lines=3, big="$", big_color=DGREEN), -w * 0.12, -110, rot=-8)
    return s

@asset
def shield(seed=0, h=300, color="#5B8DBE", mark="check"):
    sd = seed * 1000 + 530; w = h * 0.8
    s = P(wobble([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, 0), (0, h / 2), (-w / 2, 0)], sd, 2, 30, closed=True), color, INK, 6)
    if mark == "check": s += check(0, -h * 0.06, h * 0.22, sd + 1, 16, WHITE)
    elif mark == "?": s += T(0, h * 0.12, "?", h * 0.5, WHITE, 700)
    elif mark == "x": s += xmark(0, -h * 0.05, h * 0.18, sd + 2, 14, WHITE)
    return s

@asset
def umbrella(seed=0, w=360, color=ARED):
    sd = seed * 1000 + 540
    top = [(-w / 2, 0)] + [(w / 2 * math.cos(math.radians(a)), w * 0.42 * math.sin(math.radians(a))) for a in range(-180, 1, 15)]
    return line([(0, 0), (0, w * 0.6), (-w * 0.1, w * 0.68)], sd, 9) + poly(top, color, sd + 1, 6)

@asset
def thermometer(seed=0, h=360, level=0.9):
    sd = seed * 1000 + 550
    return (rect(-24, -h / 2, 48, h * 0.82, WHITE, sd, 5, r=24) + rect(-12, -h / 2 + 20 + (h * 0.72) * (1 - level), 24, (h * 0.72) * level, RED, sd + 1, 0, None)
            + ell(0, h * 0.38, 48, 48, RED, sd + 2, 5) + "".join(line([(10, -h / 2 + 40 + i * 40), (24, -h / 2 + 40 + i * 40)], sd + 3 + i, 4) for i in range(5)))

@asset
def sun(seed=0, r=110, face=False):
    sd = seed * 1000 + 560; s = ""
    for i in range(10):
        a = 2 * math.pi * i / 10
        s += line([(r * 1.25 * math.cos(a), r * 1.25 * math.sin(a)), (r * 1.65 * math.cos(a), r * 1.65 * math.sin(a))], sd + i, 8, ORANGE)
    s += ell(0, 0, r, r, YELLOW, sd + 20, 6)
    if face: s += f'<circle cx="{-r*0.3:.1f}" cy="{-r*0.1:.1f}" r="8" fill="{INK}"/><circle cx="{r*0.3:.1f}" cy="{-r*0.1:.1f}" r="8" fill="{INK}"/>' + P(f"M{-r*0.35:.1f},{r*0.25:.1f} Q0,{r*0.5:.1f} {r*0.35:.1f},{r*0.25:.1f}", "none", INK, 5)
    return s

@asset
def ac_unit(seed=0, w=200, on=True):
    sd = seed * 1000 + 570; h = w * 0.7
    s = rect(-w / 2, -h / 2, w, h, "#D7DDE3", sd, 5) + ell(-w * 0.12, 0, h * 0.34, h * 0.34, "#AEB8C2", sd + 1, 4)
    for a in range(0, 360, 60):
        s += line([(-w * 0.12, 0), (-w * 0.12 + h * 0.3 * math.cos(math.radians(a)), h * 0.3 * math.sin(math.radians(a)))], sd + 2 + a, 4)
    if on:
        for i in range(3): s += P(f"M{w*0.55:.1f},{-h*0.3 + i*h*0.3:.1f} q20,-14 40,0 t40,0", "none", LBLUE, 6)
    return s

@asset
def crowd(seed=0, n=24, cols=8, w=800, h=380, colors=("#E57373", "#64B5F6", "#81C784", "#FFD54F", "#BA68C8", "#4DB6AC", "#FF8A65", "#90A4AE")):
    sd = seed * 1000 + 580; s = ""; r = rng(sd)
    rows = math.ceil(n / cols)
    for i in range(n):
        c, rw = i % cols, i // cols
        x = -w / 2 + (c + 0.5) * w / cols + r.uniform(-12, 12) + (rw % 2) * w / cols * 0.3
        y = -h / 2 + (rw + 0.5) * h / rows + r.uniform(-8, 8)
        k = 0.13
        s += G(person(seed + i, k, r.choice(["hips", "relaxed", "wave", "hip_one"]), r.choice(["smile", "flat", "smile"]), skin=r.choice([SKIN, SKIN2, SKIN3, SKIN4]),
                      hair=r.choice(["spiky", "side", "bald", "bun", "curly"]), hair_color=r.choice(["black", "brown", "blonde", "grey"]), shirt=colors[i % len(colors)]), x, y - 40)
    return s

@asset
def waiting_room(seed=0, w=1100):
    sd = seed * 1000 + 590; s = ""
    for i in range(4):
        x = -w * 0.38 + i * w * 0.2
        s += rect(x - 70, 40, 140, 24, "#5B8DBE", sd + i, 5) + rect(x - 70, -40, 24, 104, "#5B8DBE", sd + 10 + i, 5) + line([(x - 60, 64), (x - 60, 150)], sd + 20 + i, 6) + line([(x + 60, 64), (x + 60, 150)], sd + 30 + i, 6)
    s += G(clock(seed, 90), w * 0.3, -240)
    s += G(person(seed + 3, 0.42, "relaxed", "flat", eyes="closed", hair="side", hair_color="brown", shirt="#B0BEC5", legs="sit"), -w * 0.18, -120)
    s += T(-w * 0.1, -230, "z z z", 60, DGREY, 700)
    s += G(rect(-40, -10, 80, 120, "#C49A6C", sd + 40, 5) + ell(0, -60, 60, 70, DGREEN, sd + 41, 5), w * 0.44, 30)
    return s

@asset
def clock(seed=0, r=90):
    sd = seed * 1000 + 600
    return ell(0, 0, r, r, WHITE, sd, 6) + line([(0, 0), (0, -r * 0.65)], sd + 1, 7) + line([(0, 0), (r * 0.45, r * 0.15)], sd + 2, 7)

@asset
def robot(seed=0, k=1.0, relax=True):
    sd = seed * 1000 + 610; u = k
    s = ""
    if relax:   # beach chair + umbrella + drink
        s += G(umbrella(seed, 380, "#F06292"), -220 * u, -140 * u, rot=-12)
        s += line([(-120 * u, 140 * u), (40 * u, 20 * u), (140 * u, 140 * u)], sd, 9 * u, BROWN) + poly([(-110 * u, 120 * u), (60 * u, 0), (100 * u, 30 * u), (-80 * u, 150 * u)], "#4FC3F7", sd + 1, 5)
    s += rect(-60 * u, -170 * u, 120 * u, 100 * u, "#B0BEC5", sd + 2, 5, r=12) + line([(0, -170 * u), (0, -210 * u)], sd + 3, 5) + ell(0, -218 * u, 12 * u, 12 * u, RED, sd + 4, 4)
    s += rect(-36 * u, -140 * u, 26 * u, 22 * u, INK, sd + 5, 0, None) + rect(12 * u, -140 * u, 26 * u, 22 * u, INK, sd + 6, 0, None)
    s += rect(-70 * u, -60 * u, 140 * u, 130 * u, "#90A4AE", sd + 7, 5, r=12)
    s += line([(-70 * u, -30 * u), (-130 * u, 20 * u)], sd + 8, 8) + line([(70 * u, -30 * u), (140 * u, -60 * u)], sd + 9, 8)
    if relax: s += G(rect(-16, -30, 32, 50, "#FFF59D", sd + 10, 4) + line([(6, -30), (16, -60)], sd + 11, 4, RED), 150 * u, -80 * u)
    return s

@asset
def battery(seed=0, w=360, label="1 DAY", level=1.0):
    sd = seed * 1000 + 620; h = w * 0.5
    s = rect(-w / 2, -h / 2, w, h, WHITE, sd, 6, r=18) + rect(w / 2, -h * 0.18, 26, h * 0.36, INK, sd + 1, 0, None)
    s += rect(-w / 2 + 16, -h / 2 + 16, (w - 32) * level, h - 32, GREEN, sd + 2, 0, None)
    s += bolt(seed, h * 0.7, 0, 0, YELLOW, 5)
    if label: s += T(0, h / 2 + 70, label, 60, INK, 700)
    return s

@asset
def ceiling(seed=0, w=1100, bolts=True):
    sd = seed * 1000 + 630; s = rect(-w / 2, -30, w, 60, "#8D99A6", sd, 6)
    if bolts:
        for i in range(7): s += ell(-w / 2 + 60 + i * (w - 120) / 6, 0, 13, 13, "#C5CED8", sd + 1 + i, 4)
    return s

@asset
def gauge(seed=0, r=190, level=0.9):
    sd = seed * 1000 + 640
    arc = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(180, 361, 15)]
    s = poly([(-r, 0)] + arc + [(r, 0)], WHITE, sd, 6)
    for i, c in enumerate((GREEN, YELLOW, RED)):
        a0 = 180 + i * 60; a1 = a0 + 60
        pts = [(r * 0.85 * math.cos(math.radians(a)), r * 0.85 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 10)]
        s += P(catmull(pts), "none", c, 22)
    a = math.radians(180 + 180 * level)
    s += line([(0, 0), (r * 0.75 * math.cos(a), r * 0.75 * math.sin(a))], sd + 1, 10) + ell(0, 0, 18, 18, INK, sd + 2, 0, None)
    return s

@asset
def bathroom_scale(seed=0, w=360, reading="HEAVY"):
    sd = seed * 1000 + 650
    return rect(-w / 2, -w * 0.08, w, w * 0.3, "#E0E0E0", sd, 6, r=24) + rect(-w * 0.22, -w * 0.02, w * 0.44, w * 0.14, WHITE, sd + 1, 4, r=8) + T(0, w * 0.1, reading, w * 0.1, RED, 700)

@asset
def mailbox(seed=0, h=360, flag=True):
    sd = seed * 1000 + 660
    s = rect(-12, -20, 24, h * 0.6, BROWN, sd, 5)
    s += P(wobble([(-110, -20), (-110, -150), (60, -150), (110, -110), (110, -20)], sd + 1, 1.5, 30, closed=True), "#5B8DBE", INK, 6)
    if flag: s += rect(110, -170, 12, 90, RED, sd + 2, 4) + rect(110, -170, 60, 40, RED, sd + 3, 4)
    return s

@asset
def gift_card(seed=0, w=420, text="Happy B-day,|Coworker!"):
    sd = seed * 1000 + 670; h = w * 0.72
    s = rect(-w / 2, -h / 2, w, h, "#FFF3C4", sd, 6) + TL(0, -h * 0.15, text.split("|"), w * 0.11, INK, 700)
    r = rng(sd)
    for i in range(5): s += P(f"M{-w*0.35 + i*w*0.16:.1f},{h*0.3:.1f} c10,-20 20,10 34,-6", "none", r.choice([BLUE, RED, DGREEN, PURPLE]), 4)
    return s

@asset
def party_hat(seed=0, h=140):
    sd = seed * 1000 + 680
    return poly([(-h * 0.36, h / 2), (0, -h / 2), (h * 0.36, h / 2)], "#F26CA7", sd, 5) + ell(0, -h / 2, h * 0.1, h * 0.1, YELLOW, sd + 1, 4)

@asset
def dog(seed=0, k=1.0, leash=True, excited=True):
    """Golden retriever facing left, tongue out, tail wagging."""
    sd = seed * 1000 + 690; u = k; G_ = "#E0A23B"; s = ""
    s += P(f"M{150*u:.1f},{-20*u:.1f} q{70*u:.1f},{-40*u:.1f} {60*u:.1f},{-120*u:.1f}", "none", INK, 24 * u) + P(f"M{150*u:.1f},{-20*u:.1f} q{70*u:.1f},{-40*u:.1f} {60*u:.1f},{-120*u:.1f}", "none", G_, 13 * u)
    for x in (-110, -60, 70, 120): s += line([(x * u, 40 * u), (x * u, 150 * u)], sd + x, 15 * u)
    s += ell(0, 10 * u, 175 * u, 88 * u, G_, sd + 1, 6)
    s += ell(-175 * u, -100 * u, 88 * u, 80 * u, G_, sd + 2, 6)                      # head
    s += ell(-262 * u, -72 * u, 52 * u, 36 * u, "#EDB862", sd + 3, 5)                # snout
    s += ell(-302 * u, -86 * u, 16 * u, 13 * u, INK, sd + 4, 0, None)               # nose
    s += ell(-120 * u, -78 * u, 34 * u, 64 * u, "#C47F1F", sd + 5, 5)                # ear (back of head)
    s += f'<circle cx="{-205*u:.1f}" cy="{-128*u:.1f}" r="{11*u:.1f}" fill="{INK}"/>'
    if excited:
        s += P(f"M{-262*u:.1f},{-44*u:.1f} q{4*u:.1f},{60*u:.1f} {34*u:.1f},{40*u:.1f} q{6*u:.1f},{-26*u:.1f} {-6*u:.1f},{-44*u:.1f} Z", PINK, INK, 4 * u)
        for i in range(3): s += line([(200 * u + i * 26 * u, -175 * u), (232 * u + i * 26 * u, -215 * u)], sd + 10 + i, 5 * u)
    if leash: s += P(f"M{-150*u:.1f},{-30*u:.1f} q{-140*u:.1f},{70*u:.1f} {-230*u:.1f},{-40*u:.1f}", "none", RED, 7 * u)
    return s

@asset
def ai_bubble(seed=0, r=200, popped=False, text="AI"):
    sd = seed * 1000 + 700
    if popped:
        s = ""
        for i in range(12):
            a = 2 * math.pi * i / 12
            s += line([(r * 0.7 * math.cos(a), r * 0.7 * math.sin(a)), (r * 1.15 * math.cos(a), r * 1.15 * math.sin(a))], sd + i, 7, LBLUE)
        return s + T(0, 60, "POP!", 170, RED, 700, stroke=4)
    return (ell(0, 0, r, r, "#E3F2FD", sd, 6) + P(f"M{-r*0.5:.1f},{-r*0.45:.1f} q{r*0.2:.1f},{-r*0.2:.1f} {r*0.45:.1f},{-r*0.25:.1f}", "none", WHITE, 14) +
            T(0, r * 0.25, text, r * 0.7, BLUE, 700))

@asset
def tumbleweed(seed=0, r=70):
    sd = seed * 1000 + 710; s = ""; rr = rng(sd)
    for i in range(9):
        s += ell(rr.uniform(-12, 12), rr.uniform(-12, 12), r * rr.uniform(0.6, 1), r * rr.uniform(0.5, 0.9), "none", sd + i, 3.5, "#A1887F")
    return s

@asset
def baseball_field(seed=0, w=1100, subs=True):
    sd = seed * 1000 + 720; s = ""
    s += P(f"M0,{w*0.3:.1f} L{-w*0.5:.1f},{-w*0.1:.1f} Q0,{-w*0.48:.1f} {w*0.5:.1f},{-w*0.1:.1f} Z", "#7CB342", INK, 6)
    d = [(0, w * 0.22), (-w * 0.2, w * 0.02), (0, -w * 0.18), (w * 0.2, w * 0.02)]
    s += poly(d, "#D7B98E", sd, 5)
    for i in range(9): s += G(line([(0, 0), (0, -70)], sd + 30 + i, 6, "#558B2F") + ell(8, -50, 14, 28, YELLOW, sd + 40 + i, 3), -w * 0.46 + i * w * 0.115, -w * 0.3)
    if subs:
        for i, (x, y) in enumerate(d[1:]): s += G(substation(seed + i, 190), x, y - 20)
    return s

@asset
def restaurant(seed=0, w=300, name="BISTRO", color=ARED, empty=False, x_over=False):
    sd = seed * 1000 + 730; h = w * 0.8
    s = rect(-w / 2, -h / 2, w, h, "#F5E6CC", sd, 5.5)
    for i in range(6): s += poly([(-w / 2 + i * w / 6, -h / 2), (-w / 2 + (i + 1) * w / 6, -h / 2), (-w / 2 + (i + 0.5) * w / 6, -h / 2 + 46)], color if i % 2 == 0 else WHITE, sd + 1 + i, 4)
    s += rect(-w * 0.4, -h / 2 - 70, w * 0.8, 64, WHITE, sd + 10, 5) + T(0, -h / 2 - 22, name, w * 0.13, INK, 700, spacing=2)
    s += rect(-w * 0.15, h * 0.05, w * 0.3, h * 0.45, BROWN, sd + 11, 4.5) + rect(-w * 0.42, h * 0.02, w * 0.22, w * 0.2, LBLUE, sd + 12, 4) + rect(w * 0.2, h * 0.02, w * 0.22, w * 0.2, LBLUE, sd + 13, 4)
    if x_over: s += xmark(0, 0, w * 0.45, sd + 14, 14)
    return s

@asset
def balloon(seed=0, r=170, label="FORECAST", color="#EF5350"):
    sd = seed * 1000 + 740
    return (P(f"M0,{r*1.15:.1f} q{-20:.1f},{60:.1f} 10,{140:.1f}", "none", INK, 4) + ell(0, 0, r * 0.86, r, color, sd, 6) +
            poly([(-14, r * 0.98), (14, r * 0.98), (0, r * 1.15)], color, sd + 1, 4) + P(f"M{-r*0.45:.1f},{-r*0.45:.1f} q{r*0.15:.1f},{-r*0.2:.1f} {r*0.35:.1f},{-r*0.25:.1f}", "none", WHITE, 12) +
            T(0, r * 0.12, label, r * 0.24, WHITE, 700, spacing=2))

@asset
def crane(seed=0, h=520):
    sd = seed * 1000 + 750; s = ""
    s += line([(0, h / 2), (0, -h / 2)], sd, 10, "#F2B01E") + line([(-h * 0.2, -h / 2), (h * 0.62, -h / 2)], sd + 1, 10, "#F2B01E")
    for i in range(8): s += line([(-14, h / 2 - i * h / 8), (14, h / 2 - (i + 1) * h / 8)], sd + 2 + i, 4, "#B9820F")
    s += line([(h * 0.5, -h / 2), (h * 0.5, -h * 0.1)], sd + 20, 4) + rect(h * 0.5 - 40, -h * 0.1, 80, 50, DGREY, sd + 21, 4)
    return s

@asset
def brunch(seed=0, w=420, sign="RESERVED|deposit: $20"):
    sd = seed * 1000 + 760; s = ""
    s += ell(0, 40, w * 0.5, 34, WHITE, sd, 5)
    for i in range(4): s += ell(0, 20 - i * 26, w * 0.32, 26, "#E0A458", sd + 1 + i, 4.5)
    s += rect(-w * 0.1, -88, w * 0.2, 16, YELLOW, sd + 6, 3.5)
    s += G(poly([(-38, -150), (38, -150), (22, 30), (-22, 30)], "#FFCC80", sd + 7, 5), w * 0.62, -10)
    if sign:
        s += G(rect(-110, -70, 220, 120, WHITE, sd + 8, 5) + TL(0, -20, sign.split("|"), 36, INK, 700, lh=1.1), -w * 0.78, -40)
    return s

@asset
def poof(seed=0, r=180, text="POOF"):
    sd = seed * 1000 + 770; s = ""; rr = rng(sd)
    for i in range(8):
        a = 2 * math.pi * i / 8
        s += ell(r * 0.55 * math.cos(a), r * 0.45 * math.sin(a), r * 0.42, r * 0.38, "#EEEEEE", sd + i, 4.5)
    s += ell(0, 0, r * 0.55, r * 0.45, "#EEEEEE", sd + 20, 0, None)
    return s + (T(0, r * 0.15, text, r * 0.4, DGREY, 700) if text else "")

@asset
def distance(seed=0, w=900, label="100 miles", color=ARED):
    sd = seed * 1000 + 780
    return arrow(-w / 2 + 40, 0, w / 2, 0, sd, 9, color, 32) + arrow(w / 2 - 40, 0, -w / 2, 0, sd + 1, 9, color, 32) + T(0, -30, label, 70, color, 700)

@asset
def scissors(seed=0, w=300, open_=0.5):
    sd = seed * 1000 + 790; a = 0.12 * w * (0.3 + open_)
    return (line([(-w * 0.2, -w * 0.05), (w * 0.5, a)], sd, 12, "#90A4AE") + line([(-w * 0.2, w * 0.05), (w * 0.5, -a)], sd + 1, 12, "#90A4AE") +
            ell(-w * 0.3, -w * 0.1, w * 0.11, w * 0.08, RED, sd + 2, 6) + ell(-w * 0.3, w * 0.1, w * 0.11, w * 0.08, RED, sd + 3, 6) + ell(w * 0.02, 0, 7, 7, INK, sd + 4, 0, None))

@asset
def stop_sign(seed=0, r=130, text="STOP"):
    sd = seed * 1000 + 800
    pts = [(r * math.cos(math.radians(22.5 + 45 * i)), r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    return line([(0, r), (0, r * 2.4)], sd, 10, DGREY) + poly(pts, RED, sd + 1, 6) + T(0, r * 0.2, text, r * 0.5, WHITE, 700, spacing=2)

@asset
def pause_icon(seed=0, r=130):
    sd = seed * 1000 + 810
    return ell(0, 0, r, r, "#4A6FA5", sd, 6) + rect(-r * 0.35, -r * 0.45, r * 0.24, r * 0.9, WHITE, sd + 1, 0, None) + rect(r * 0.11, -r * 0.45, r * 0.24, r * 0.9, WHITE, sd + 2, 0, None)

@asset
def bond(seed=0, w=460, amount="$1,000", title="BOND", year=""):
    sd = seed * 1000 + 820; h = w * 0.62
    s = rect(-w / 2, -h / 2, w, h, "#E8F5E9", sd, 6) + rect(-w / 2 + 18, -h / 2 + 18, w - 36, h - 36, "none", sd + 1, 4, DGREEN)
    s += T(0, -h * 0.12, title, w * 0.12, DGREEN, 700, spacing=4) + T(0, h * 0.2, amount, w * 0.13, INK, 700, family="Comic Neue")
    if year: s += T(w * 0.36, h * 0.38, year, w * 0.06, DGREY, 700)
    return s

@asset
def snail(seed=0, w=300):
    sd = seed * 1000 + 830
    return (ell(0, 30, w * 0.5, w * 0.1, "#BCAAA4", sd, 5) + ell(-w * 0.05, -w * 0.08, w * 0.28, w * 0.26, "#D84315", sd + 1, 6) +
            P(f"M{-w*0.05:.1f},{-w*0.08:.1f} m-30,0 a30,30 0 1,1 60,0 a18,18 0 1,1 -36,0", "none", INK, 4) +
            line([(w * 0.38, 10), (w * 0.45, -60)], sd + 2, 5) + ell(w * 0.45, -66, 10, 10, INK, sd + 3, 0, None))

@asset
def books(seed=0, n=12, w=300):
    sd = seed * 1000 + 840; s = ""; r = rng(sd)
    cols = [ARED, BLUE, DGREEN, ORANGE, PURPLE, TEAL, "#8D6E63", "#5C6BC0"]
    for i in range(n):
        ww = w * r.uniform(0.85, 1.0); s += rect(-ww / 2 + r.uniform(-10, 10), -i * 34, ww, 32, cols[i % len(cols)], sd + i, 4)
    return G(s, 0, n * 17)

@asset
def council(seed=0, n=9, yes=6, show_votes=False, w=1100):
    sd = seed * 1000 + 850; s = ""
    for i in range(n):
        x = -w * 0.42 + i * w * 0.84 / (n - 1)
        s += G(person(seed + i, 0.24, "relaxed", "flat", skin=[SKIN, SKIN2, SKIN3][i % 3], hair=["side", "bald", "bun", "curly", "spiky"][i % 5],
                      hair_color=["brown", "grey", "black", "blonde"][i % 4], shirt=["#455A64", "#5D4037", "#37474F"][i % 3], legs="none"), x, -60)
        if show_votes:
            s += (check(x, -170, 26, sd + i, 9) if i < yes else xmark(x, -170, 22, sd + 40 + i, 9))
    s += rect(-w / 2, 10, w, 90, "#8D6E63", sd + 30, 6)
    return s

@asset
def mixer(seed=0, w=520):
    sd = seed * 1000 + 860; s = ""
    s += rect(-w / 2, -10, w * 0.95, 60, "#B0BEC5", sd, 5) + rect(w * 0.22, -110, w * 0.26, 100, "#F2B01E", sd + 1, 5) + rect(w * 0.28, -96, w * 0.14, 40, LBLUE, sd + 2, 4)
    s += G(ell(0, 0, w * 0.3, w * 0.17, "#ECEFF1", sd + 3, 6) + "".join(line([(-w * 0.25 + i * w * 0.12, -w * 0.12), (-w * 0.18 + i * w * 0.12, w * 0.12)], sd + 10 + i, 5, ORANGE) for i in range(4)), -w * 0.15, -90, rot=-14)
    for x in (-w * 0.35, -w * 0.12, w * 0.32): s += ell(x, 55, 40, 40, "#424242", sd + 20 + int(x), 5)
    return s

@asset
def progress(seed=0, w=420, frac=0.25, label="", color=GREEN):
    sd = seed * 1000 + 870
    s = rect(-w / 2, -30, w, 60, WHITE, sd, 5, r=14) + rect(-w / 2 + 8, -22, (w - 16) * frac, 44, color, sd + 1, 0, None, r=10)
    if label: s += T(0, 90, label, 54, INK, 700)
    return s

@asset
def courthouse(seed=0, w=560, label=""):
    sd = seed * 1000 + 880; h = w * 0.7; s = ""
    s += poly([(-w / 2 - 20, -h * 0.25), (0, -h * 0.58), (w / 2 + 20, -h * 0.25)], "#ECEFF1", sd, 6)
    s += rect(-w / 2, -h * 0.25, w, h * 0.08, "#CFD8DC", sd + 1, 5)
    for i in range(5): s += rect(-w * 0.42 + i * w * 0.2, -h * 0.17, w * 0.08, h * 0.55, WHITE, sd + 2 + i, 5)
    s += rect(-w / 2 - 20, h * 0.38, w + 40, h * 0.1, "#CFD8DC", sd + 10, 5)
    if label: s += T(0, -h * 0.3, label, w * 0.07, INK, 700, spacing=3)
    return s

@asset
def whitehouse(seed=0, w=640):
    sd = seed * 1000 + 890; h = w * 0.5; s = ""
    s += rect(-w / 2, -h * 0.2, w, h * 0.62, WHITE, sd, 6)
    s += poly([(-w * 0.16, -h * 0.2), (0, -h * 0.45), (w * 0.16, -h * 0.2)], WHITE, sd + 1, 5)
    for i in range(4): s += rect(-w * 0.13 + i * w * 0.08, -h * 0.18, w * 0.03, h * 0.58, "#F5F5F5", sd + 2 + i, 3.5)
    for i in range(6):
        x = -w * 0.45 + i * w * 0.07 if i < 3 else w * 0.24 + (i - 3) * w * 0.07
        s += rect(x, -h * 0.05, w * 0.04, h * 0.14, LBLUE, sd + 10 + i, 3)
    s += line([(0, -h * 0.45), (0, -h * 0.7)], sd + 20, 4) + rect(0, -h * 0.7, w * 0.08, h * 0.08, "#B71C1C", sd + 21, 3)
    return s

@asset
def trophy(seed=0, h=320, text="RECORD"):
    sd = seed * 1000 + 900
    return (P(f"M{-h*0.3:.1f},{-h*0.4:.1f} L{h*0.3:.1f},{-h*0.4:.1f} Q{h*0.3:.1f},{h*0.05:.1f} 0,{h*0.12:.1f} Q{-h*0.3:.1f},{h*0.05:.1f} {-h*0.3:.1f},{-h*0.4:.1f} Z", GOLD, INK, 6) +
            rect(-h * 0.06, h * 0.1, h * 0.12, h * 0.16, GOLD, sd, 5) + rect(-h * 0.24, h * 0.26, h * 0.48, h * 0.12, BROWN, sd + 1, 5) +
            T(0, -h * 0.17, text, h * 0.1, INK, 700))

def cobweb(seed=0, r=120, cx=0, cy=0):
    sd = seed * 1000 + 910; s = ""
    for i in range(6):
        a = math.radians(-180 + i * 18)
        s += line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))], sd + i, 2.5, DGREY)
    for k in range(1, 4):
        pts = [(cx + r * k / 4 * math.cos(math.radians(-180 + i * 18)), cy + r * k / 4 * math.sin(math.radians(-180 + i * 18))) for i in range(6)]
        s += P(catmull(pts), "none", DGREY, 2.5)
    return s
REG["cobweb"] = lambda seed=0, r=120: cobweb(seed, r)

@asset
def space_needle(seed=0, h=520):
    sd = seed * 1000 + 920
    return (line([(-h * 0.08, h / 2), (0, -h * 0.15), (h * 0.08, h / 2)], sd, 8) + line([(0, -h * 0.15), (0, -h / 2)], sd + 1, 6) +
            ell(0, -h * 0.22, h * 0.2, h * 0.05, "#CFD8DC", sd + 2, 6) + rect(-h * 0.06, -h * 0.3, h * 0.12, h * 0.08, "#ECEFF1", sd + 3, 5))

@asset
def cake(seed=0, w=360):
    sd = seed * 1000 + 930
    s = ell(0, 90, w * 0.62, 30, WHITE, sd, 5) + rect(-w / 2, -40, w, 130, "#F8BBD0", sd + 1, 6) + rect(-w * 0.36, -130, w * 0.72, 92, "#F48FB1", sd + 2, 6)
    s += P(f"M{-w/2:.1f},{-40:.1f} q{w/8:.1f},40 {w/4:.1f},0 t{w/4:.1f},0 t{w/4:.1f},0 t{w/4:.1f},0", "none", WHITE, 12)
    s += ell(0, -150, 24, 24, RED, sd + 3, 4)
    return s

@asset
def podium(seed=0, w=360, spotlight=True, mics=True, sign="PLEDGE"):
    sd = seed * 1000 + 940; s = ""
    if spotlight:
        s += P(f"M{-w*1.1:.1f},{-700:.1f} L{-w*0.2:.1f},{-700:.1f} L{w*1.2:.1f},{260:.1f} L{-w*1.2:.1f},{260:.1f} Z", "#FFF59D", "none", 0, op=0.55)
    if mics:
        for x, a in ((-60, -14), (0, 0), (60, 14)): s += G(line([(0, 0), (0, -90)], sd + x, 6) + ell(0, -100, 16, 20, "#333333", sd + x + 1, 4), x, -110, rot=a)
    s += poly([(-w / 2, -120), (w / 2, -120), (w * 0.4, 260), (-w * 0.4, 260)], "#5D4037", sd, 6)
    if sign: s += rect(-w * 0.3, -60, w * 0.6, 90, WHITE, sd + 1, 4) + T(0, 0, sign, w * 0.12, INK, 700, spacing=2)
    return s

@asset
def hook(seed=0, h=360, obj=None):
    sd = seed * 1000 + 950
    s = line([(0, -h / 2), (0, h * 0.1)], sd, 5, DGREY)
    s += P(f"M0,{h*0.1:.1f} L0,{h*0.3:.1f} a{h*0.12:.1f},{h*0.12:.1f} 0 1,1 {-h*0.24:.1f},0 l{14},{-26}", "none", "#78909C", 12)
    return s

@asset
def rope(seed=0, w=1200, y=0, tension=0.0):
    sd = seed * 1000 + 960
    pts = [(-w / 2 + w * t / 20, y + (1 - tension) * 26 * math.sin(t * 2.2)) for t in range(21)]
    return P(catmull(pts), "none", INK, 26) + P(catmull(pts), "none", "#C8A165", 16)

@asset
def price_tag(seed=0, text="18.2c", w=300, color="#FFF59D"):
    sd = seed * 1000 + 970; h = w * 0.45
    fs = min(h * 0.55, w * 0.68 / max(0.01, text_w(text, 100, 700, "Comic Neue") / 100))
    return poly([(-w / 2, 0), (-w * 0.3, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w * 0.3, h / 2)], color, sd, 6) + ell(-w * 0.28, 0, 12, 12, WHITE, sd + 1, 4) + T(w * 0.1, fs * 0.35, text, fs, INK, 700, family="Comic Neue")

@asset
def storm(seed=0, w=360):
    sd = seed * 1000 + 980
    return (ell(-w * 0.18, 0, w * 0.26, w * 0.18, "#90A4AE", sd, 5) + ell(w * 0.12, -w * 0.06, w * 0.3, w * 0.22, "#90A4AE", sd + 1, 5) + ell(w * 0.28, w * 0.04, w * 0.2, w * 0.15, "#90A4AE", sd + 2, 5) +
            bolt(seed, w * 0.4, 0, w * 0.3, YELLOW, 5) + "".join(line([(-w * 0.3 + i * w * 0.15, w * 0.2), (-w * 0.34 + i * w * 0.15, w * 0.34)], sd + 10 + i, 5, BLUE) for i in range(5)))

@asset
def flame(seed=0, h=160, color="#FF9800"):
    sd = seed * 1000 + 990
    return (P(wobble([(0, -h / 2), (h * 0.3, -h * 0.05), (h * 0.32, h * 0.25), (0, h * 0.45), (-h * 0.32, h * 0.25), (-h * 0.3, -h * 0.05)], sd, 2, 30, closed=True), color, INK, 5) +
            P(wobble([(0, -h * 0.1), (h * 0.15, h * 0.15), (0, h * 0.35), (-h * 0.15, h * 0.15)], sd + 1, 1, 20, closed=True), YELLOW, "none", 0))

@asset
def rusty(seed=0, w=300):
    sd = seed * 1000 + 1000
    s = rect(-w / 2, -w * 0.4, w, w * 0.7, "#8D9BA6", sd, 6)
    r = rng(sd)
    for i in range(7): s += ell(r.uniform(-w * 0.4, w * 0.4), r.uniform(-w * 0.3, w * 0.2), r.uniform(12, 30), r.uniform(8, 20), "#A0522D", sd + 1 + i, 0, None)
    s += line([(-w * 0.1, -w * 0.4), (0, -w * 0.2), (-w * 0.06, -w * 0.05), (w * 0.05, w * 0.1)], sd + 20, 4)
    for x in (-w * 0.3, 0, w * 0.3): s += rect(x - 10, -w * 0.55, 20, w * 0.15, "#B6D3E8", sd + 30 + int(x), 3.5)
    return s

@asset
def shovel(seed=0, h=420):
    sd = seed * 1000 + 1010
    return line([(0, -h / 2), (0, h * 0.2)], sd, 12, BROWN) + rect(-30, -h / 2 - 20, 60, 26, BROWN, sd + 1, 5, r=10) + poly([(-60, h * 0.2), (60, h * 0.2), (50, h / 2), (0, h * 0.58), (-50, h / 2)], "#B0BEC5", sd + 2, 6)

@asset
def chip(seed=0, w=260, text="AI", face=False, mouth="frown"):
    sd = seed * 1000 + 1020; s = ""
    for i in range(5):
        for sgn in (-1, 1):
            o = -w * 0.32 + i * w * 0.16
            s += line([(o, sgn * w * 0.42), (o, sgn * w * 0.58)], sd + i * 2 + (sgn > 0), 7) + line([(sgn * w * 0.42, o), (sgn * w * 0.58, o)], sd + 20 + i * 2 + (sgn > 0), 7)
    s += rect(-w * 0.45, -w * 0.45, w * 0.9, w * 0.9, "#37474F", sd, 6, r=18) + rect(-w * 0.3, -w * 0.3, w * 0.6, w * 0.6, "#455A64", sd + 40, 3.5)
    s += T(0, w * 0.13 if not face else w * 0.24, text, w * 0.3, "#80DEEA", 700, spacing=3)
    if face:
        s += f'<circle cx="{-w*0.12:.1f}" cy="{-w*0.1:.1f}" r="{w*0.035:.1f}" fill="{WHITE}"/><circle cx="{w*0.12:.1f}" cy="{-w*0.1:.1f}" r="{w*0.035:.1f}" fill="{WHITE}"/>'
        if mouth == "frown": s += P(f"M{-w*0.1:.1f},{w*0.04:.1f} Q0,{-w*0.04:.1f} {w*0.1:.1f},{w*0.04:.1f}", "none", WHITE, 5)
        else: s += P(f"M{-w*0.1:.1f},{-w*0.0:.1f} Q0,{w*0.08:.1f} {w*0.1:.1f},{0:.1f}", "none", WHITE, 5)
    return s

@asset
def pipeline(seed=0, w=1400, n=6, cut=None, labels=False):
    sd = seed * 1000 + 1030; s = ""; seg = w / n
    for i in range(n):
        x = -w / 2 + i * seg; col = "#EF9A9A" if (cut is not None and i >= n - cut) else "#90A4AE"
        s += rect(x, -40, seg - 12, 80, col, sd + i, 5, r=6) + rect(x + seg - 30, -54, 24, 108, "#78909C", sd + 20 + i, 4)
        s += G(data_center(seed + i, 150, label=""), x + seg / 2 - 10, -140)
    return s

@asset
def car(seed=0, w=420, brake=True):
    sd = seed * 1000 + 1040; s = ""
    s += poly([(-w / 2, 0), (-w / 2, -w * 0.14), (-w * 0.25, -w * 0.16), (-w * 0.12, -w * 0.32), (w * 0.2, -w * 0.32), (w * 0.32, -w * 0.16), (w / 2, -w * 0.12), (w / 2, 0)], "#E53935", sd, 6)
    s += rect(-w * 0.08, -w * 0.28, w * 0.24, w * 0.11, LBLUE, sd + 1, 4)
    for x in (-w * 0.28, w * 0.28): s += ell(x, 0, w * 0.1, w * 0.1, "#424242", sd + 2 + int(x), 6) + ell(x, 0, w * 0.04, w * 0.04, LGREY, sd + 3 + int(x), 3)
    if brake:
        for i in range(3): s += line([(-w * 0.6 - i * 30, -w * 0.08 + i * 26), (-w * 1.1 - i * 30, -w * 0.08 + i * 26)], sd + 10 + i, 6, DGREY)
        s += T(w * 0.1, -w * 0.45, "SCREECH!", w * 0.13, RED, 700, rot=-6)
    return s

@asset
def padlock(seed=0, h=260):
    sd = seed * 1000 + 1050
    return P(f"M{-h*0.24:.1f},{-h*0.05:.1f} L{-h*0.24:.1f},{-h*0.25:.1f} A{h*0.24:.1f},{h*0.24:.1f} 0 0,1 {h*0.24:.1f},{-h*0.25:.1f} L{h*0.24:.1f},{-h*0.05:.1f}", "none", "#78909C", 22) + rect(-h * 0.36, -h * 0.06, h * 0.72, h * 0.56, GOLD, sd, 6, r=14) + ell(0, h * 0.18, 16, 16, INK, sd + 1, 0, None)

@asset
def gear(seed=0, r=120, color="#90A4AE"):
    sd = seed * 1000 + 1060; pts = []
    for i in range(20):
        a = 2 * math.pi * i / 20; rr = r if (i // 1) % 2 == 0 else r * 0.8
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return poly(pts, color, sd, 6) + ell(0, 0, r * 0.3, r * 0.3, WHITE, sd + 1, 5)

@asset
def stapler(seed=0, w=380):
    sd = seed * 1000 + 1070
    return rect(-w / 2, 10, w, 36, "#455A64", sd, 5, r=10) + poly([(-w / 2, 6), (w * 0.46, -30), (w / 2, -6), (-w / 2 + 10, 20)], "#E53935", sd + 1, 6)

@asset
def paddle(seed=0, num="7", h=300):
    sd = seed * 1000 + 1080
    return rect(-12, 0, 24, h * 0.55, BROWN, sd, 5) + ell(0, -h * 0.15, h * 0.3, h * 0.27, WHITE, sd + 1, 6) + T(0, -h * 0.05, num, h * 0.3, INK, 700, family="Comic Neue")

@asset
def island(seed=0, w=700):
    sd = seed * 1000 + 1090
    s = ell(0, 70, w * 0.62, 60, "#4FC3F7", sd, 5) + ell(0, 40, w * 0.38, 46, "#E6C27A", sd + 1, 5)
    s += line([(w * 0.22, 40), (w * 0.26, -140)], sd + 2, 12, BROWN)
    for a in (-160, -110, -60, -20):
        s += P(f"M{w*0.26:.1f},-140 q{60*math.cos(math.radians(a)):.1f},{60*math.sin(math.radians(a)) - 30:.1f} {110*math.cos(math.radians(a)):.1f},{110*math.sin(math.radians(a)) + 20:.1f}", "none", "#43A047", 14)
    s += G(substation(seed, 240), -w * 0.08, -30)
    return s

@asset
def oven(seed=0, w=360):
    sd = seed * 1000 + 1100
    return rect(-w / 2, -w * 0.5, w, w, "#ECEFF1", sd, 6) + rect(-w * 0.36, -w * 0.18, w * 0.72, w * 0.5, "#FFB74D", sd + 1, 5) + "".join(ell(-w * 0.3 + i * w * 0.2, -w * 0.36, 16, 16, DGREY, sd + 2 + i, 3.5) for i in range(4))

@asset
def papers(seed=0, n=6, w=260):
    s = ""; r = rng(seed * 1000 + 1110)
    for i in range(n): s += G(doc(seed + i, w, lines=6), r.uniform(-60, 60), -i * 14, rot=r.uniform(-14, 14))
    return s

@asset
def hall_pass(seed=0, w=300):
    sd = seed * 1000 + 1120
    return rect(-w / 2, -w * 0.25, w, w * 0.5, "#FFE082", sd, 6, r=12) + T(0, w * 0.08, "HALL MONITOR", w * 0.09, INK, 700, spacing=1)

@asset
def sunrise(seed=0, w=700):
    sd = seed * 1000 + 1130; s = ""
    for i in range(7):
        a = math.radians(-180 + i * 30)
        s += line([(w * 0.2 * math.cos(a), w * 0.2 * math.sin(a)), (w * 0.3 * math.cos(a), w * 0.3 * math.sin(a))], sd + i, 8, ORANGE)
    s += P(f"M{-w*0.16:.1f},0 A{w*0.16:.1f},{w*0.16:.1f} 0 0,1 {w*0.16:.1f},0 Z", YELLOW, INK, 6) + line([(-w / 2, 0), (w / 2, 0)], sd + 20, 6)
    return s

@asset
def arrow_up(seed=0, h=300, color=RED):
    return arrow(0, h / 2, 0, -h / 2, seed, 16, color, 60)
@asset
def arrow_down(seed=0, h=300, color=GREEN):
    return arrow(0, -h / 2, 0, h / 2, seed, 16, color, 60)
@asset
def arrow_r(seed=0, w=300, color=ARED, curve=0.0, thick=10):
    return arrow(-w / 2, 0, w / 2, 0, seed, thick, color, 36, curve)
@asset
def xmark_a(seed=0, r=160, color=ARED, w=16):
    return xmark(0, 0, r, seed * 1000 + 1140, w, color)
@asset
def check_a(seed=0, r=120, color=GREEN):
    return check(0, 0, r, seed * 1000 + 1150, 18, color)
@asset
def circle_a(seed=0, rx=220, ry=80, color=ARED, w=8):
    return circle_mark(0, 0, rx, ry, seed * 1000 + 1160, w, color)
@asset
def qmarks(seed=0, n=3, size=110, color=RED):
    return "".join(T(i * size * 0.6 - (n - 1) * size * 0.3, (i % 2) * -size * 0.3, "?", size, color, 700, rot=(i - 1) * 12) for i in range(n))
@asset
def burst(seed=0, r=180, text="!", size=None, fill=YELLOW, color=INK):
    return star_burst(0, 0, r, fill, seed * 1000 + 1170) + T(0, (size or r * 0.5) * 0.35, text, size or r * 0.5, color, 700)
@asset
def pill(seed=0, text="~9x", w=240, size=70, color=INK):
    return rect(-w / 2, -size * 0.75, w, size * 1.5, WHITE, seed * 1000 + 1180, 6, r=size * 0.7) + T(0, size * 0.33, text, size, color, 700, family="Comic Neue")
@asset
def dollar(seed=0, text="$1", size=220, color=DGREEN):
    return T(0, size * 0.35, text, size, color, 700, family="Comic Neue", stroke=3)
@asset
def hline(seed=0, w=600, color=INK, thick=6):
    return line([(-w / 2, 0), (w / 2, 0)], seed * 1000 + 1190, thick, color)
@asset
def frame_box(seed=0, w=600, h=400, color=INK, fill="none", thick=6, dashed=False):
    s = P(wrect(-w / 2, -h / 2, w, h, seed * 1000 + 1200, 1.6), fill, color, thick)
    return f'<g stroke-dasharray="20 14">{s}</g>' if dashed else s
@asset
def plus(seed=0, r=60, color=INK):
    return line([(-r, 0), (r, 0)], seed * 1000 + 1210, 12, color) + line([(0, -r), (0, r)], seed * 1000 + 1211, 12, color)
@asset
def equals(seed=0, r=60, color=INK):
    return line([(-r, -18), (r, -18)], seed * 1000 + 1220, 12, color) + line([(-r, 18), (r, 18)], seed * 1000 + 1221, 12, color)
@asset
def neq(seed=0, r=60, color=ARED):
    return equals(seed, r, INK) + line([(-r * 0.5, r * 0.8), (r * 0.5, -r * 0.8)], seed * 1000 + 1222, 10, color)
@asset
def dash_line(seed=0, w=600, color=ARED, thick=6):
    return f'<g stroke-dasharray="20 14">{P(f"M{-w/2:.1f},0 L{w/2:.1f},0", "none", color, thick)}</g>'

@asset
def brand(seed=0, text="PJM", size=130, color="#1F3A68", underline=True, sub=""):
    """Organisation name as plain wordmark text (not an official logo)."""
    w = text_w(text, size, 700, "Comic Neue")
    s = T(0, size * 0.35, text, size, color, 700, family="Comic Neue", spacing=1)
    if underline: s += P(wobble([(-w / 2, size * 0.62), (w / 2, size * 0.62)], seed * 1000 + 1230, 2, 40), "none", color, size * 0.07)
    if sub: s += T(0, size * 1.25, sub, size * 0.4, DGREY, 700)
    return s

@asset
def ice_block(seed=0, w=520, h=320):
    sd = seed * 1000 + 1240
    s = rect(-w / 2, -h / 2, w, h, "#BFE6FF", sd, 6, "#3C8DBC", r=24).replace('fill="#BFE6FF"', 'fill="#BFE6FF" fill-opacity="0.72"')
    s += P(f"M{-w*0.38:.1f},{-h*0.3:.1f} L{-w*0.2:.1f},{-h*0.3:.1f}", "none", WHITE, 12) + P(f"M{-w*0.38:.1f},{-h*0.16:.1f} L{-w*0.3:.1f},{-h*0.16:.1f}", "none", WHITE, 12)
    return s + G(snowflake(seed, 90), w * 0.36, -h * 0.28)

@asset
def snowflake(seed=0, r=80, color="#3C8DBC"):
    sd = seed * 1000 + 1250; s = ""
    for i in range(6):
        a = math.pi * i / 3; ca, sa = math.cos(a), math.sin(a)
        s += line([(0, 0), (r * ca, r * sa)], sd + i, 7, color)
        for f in (0.55,):
            bx, by = r * f * ca, r * f * sa
            for da in (-0.6, 0.6):
                s += line([(bx, by), (bx + r * 0.3 * math.cos(a + da), by + r * 0.3 * math.sin(a + da))], sd + 10 + i, 6, color)
    return s

@asset
def pie_slices(seed=0, r=240, n=8, hi=None, colors=("#9BC4E2", "#F4A6A6", "#A5D6A7", "#FFE082", "#CE93D8", "#80CBC4", "#FFAB91", "#B0BEC5")):
    sd = seed * 1000 + 1260; s = ""
    for i in range(n):
        a0 = -math.pi / 2 + 2 * math.pi * i / n; a1 = a0 + 2 * math.pi / n
        pts = [(0, 0)] + [(r * math.cos(a0 + (a1 - a0) * t / 8), r * math.sin(a0 + (a1 - a0) * t / 8)) for t in range(9)]
        s += P("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", colors[i % len(colors)], INK, 5)
    return s
