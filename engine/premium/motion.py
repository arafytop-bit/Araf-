"""Motion grammar (frame-based, 30 fps). Nothing moves linearly.

Measured on the reference (style bible §4):
- elements pop 50% -> 100% in ~4 frames with a slight overshoot
- callouts settle 105% -> 100% with a fade over ~5 frames
- photos hard-cut in at scale 1.000, then push in at 0.60 %/s (73 % in, 27 % out)
- characters run/walk in as flipbook cycles at 5 drawings/s (6 frames per drawing)
"""
import math

FPS = 30.0


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a, b, t):
    return a + (b - a) * t


# ---------- easing curves ----------
def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_cubic(t):
    t = clamp01(t)
    return t ** 3


def ease_in_out_cubic(t):
    t = clamp01(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_expo(t):
    t = clamp01(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def ease_in_back(t, s=1.70158):
    t = clamp01(t)
    return (s + 1) * t ** 3 - s * t ** 2


def ease_out_back(t, s=1.70158):
    t = clamp01(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def spring(t_s, zeta=0.67, peak_s=4 / FPS):
    """Under-damped step response 0 -> 1 (value overshoots once ~6 % at zeta 0.67), t in seconds."""
    if t_s <= 0:
        return 0.0
    wd = math.pi / peak_s
    w = wd / math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * w * t_s) * (math.cos(wd * t_s) + zeta * w / wd * math.sin(wd * t_s))


def decay_osc(t_s, freq=7.0, decay=9.0):
    """1 -> 0 decaying oscillation (shake, wobble, follow-through)."""
    if t_s < 0:
        return 0.0
    return math.exp(-decay * t_s) * math.cos(2 * math.pi * freq * t_s)


# ---------- entrances (df = frames since the element's start) ----------
def pop(df, from_scale=0.5, frames=4):
    """(scale, alpha): reference pop 50 % -> 100 % in ~4 frames, slight overshoot."""
    if df < 0:
        return 0.0, 0.0
    s = spring(df / FPS, zeta=0.62, peak_s=frames / FPS)
    return from_scale + (1 - from_scale) * s, clamp01((df + 1) / 2.0)


def settle(df, frames=5, from_scale=1.05):
    """(scale, alpha): callout fade + 105 % -> 100 % settle."""
    if df < 0:
        return from_scale, 0.0
    e = ease_out_cubic((df + 1) / frames)
    return from_scale + (1 - from_scale) * e, e


def slide(df, dist, frames=8, overshoot=1.2):
    """Remaining offset (px) for a slide-in with ease-out-back."""
    if df < 0:
        return dist
    return dist * (1 - ease_out_back((df + 1) / frames, overshoot))


def drop(df, height, frames=12):
    """Remaining y offset for something dropping in and bouncing (gravity + 2 damped bounces)."""
    t = (df + 1) / frames
    if df < 0:
        return -height
    if t < 0.55:
        return -height * (1 - (t / 0.55) ** 2)
    u = (t - 0.55) / 0.45
    return -height * 0.12 * abs(math.sin(math.pi * 2 * min(u, 1.0))) * (1 - min(u, 1.0))


def pop_out(df, frames=4):
    """(scale, alpha) for an exit: anticipation squash then shrink to 0."""
    if df < 0:
        return 1.0, 1.0
    t = clamp01((df + 1) / frames)
    return max(0.0, 1 - ease_in_back(t, 2.2)), 1 - t ** 3


def draw_on(df, frames=8):
    """0 -> 1 path trim for strokes (arrows, circles, routes)."""
    return ease_in_out_cubic((df + 1) / frames)


# ---------- holds ----------
def push(t_s, rate=0.006, direction=1, start=1.0):
    """Photo push-in (0.6 %/s measured). direction -1 = slow push-out from start."""
    if direction >= 0:
        return start + rate * t_s
    return start - rate * t_s


def breathe(f, period_s=3.2, amp=0.006, seed=0):
    """Idle breathing scale (y) for characters: barely visible, keeps holds alive."""
    return 1 + amp * math.sin(2 * math.pi * (f / FPS) / period_s + seed)


def flip_phase(f, fps_draw=5.0, drawings=4, offset=0):
    """Flipbook cycle: phase stepped at 5 drawings/s (6 frames each), as measured on the reference."""
    k = int((f + offset) / (FPS / fps_draw)) % drawings
    return 2 * math.pi * k / drawings


def shake(df, amp=10.0, frames=10, seed=0):
    """(dx, dy) camera shake that decays to 0 over `frames`."""
    if df < 0 or df > frames:
        return 0.0, 0.0
    t = df / FPS
    k = 1 - df / frames
    return (amp * k * math.sin(2 * math.pi * 13 * t + seed), amp * 0.7 * k * math.sin(2 * math.pi * 17 * t + 1.7 + seed))


def punch(df, amount=0.035, frames=9):
    """Camera punch-in on impact: snaps to 1+amount and springs back to 1."""
    if df < 0 or df > frames * 2:
        return 1.0
    return 1 + amount * math.exp(-df / (frames / 2.5)) * math.cos(df / frames * math.pi * 0.5)
