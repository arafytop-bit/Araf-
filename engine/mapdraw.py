"""Cartoon state/country maps (BLUEPRINT 5.6): light-green fill #96E669, thick darker
outline #4D7336, faint terrain doodles, red location dot that pulses on entry, white
caps label with black outline."""
import json
import math
import re
import functools
import numpy as np
import skia
from .core import ASSETS, paint, rgb
from .text import draw_label

FILL, OUTLINE, DOODLE = '#96E669', '#4D7336', '#7CC657'


def parse_d3_path(d):
    """Parse d3-geo SVG path output (absolute M/L/Z only)."""
    path = skia.Path()
    for cmd, args in re.findall(r'([MLZ])([^MLZ]*)', d):
        nums = [float(v) for v in re.findall(r'-?\d+\.?\d*(?:e-?\d+)?', args)]
        if cmd == 'M':
            path.moveTo(nums[0], nums[1])
            for i in range(2, len(nums), 2):
                path.lineTo(nums[i], nums[i + 1])
        elif cmd == 'L':
            for i in range(0, len(nums), 2):
                path.lineTo(nums[i], nums[i + 1])
        else:
            path.close()
    return path


@functools.lru_cache(maxsize=4)
def load_outline(name='us_outline'):
    j = json.load(open(f'{ASSETS}/maps/{name}.json'))
    return parse_d3_path(j['d']), j


@functools.lru_cache(maxsize=8)
def doodles(name, seed=3):
    """Random hand-drawn terrain squiggles/dashes inside the map's bounding box."""
    path, j = load_outline(name)
    b = path.computeTightBounds()
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(22):   # wavy ridges
        x = rng.uniform(b.left(), b.right()); y = rng.uniform(b.top(), b.bottom())
        L = rng.uniform(80, 200); ang = rng.uniform(-0.5, 0.5)
        pts = []
        for k in range(7):
            t = k / 6
            px = x + math.cos(ang) * L * t
            py = y + math.sin(ang) * L * t + math.sin(t * math.pi * 2.2 + rng.uniform(0, 1)) * 12
            pts.append((px, py))
        out.append(('ridge', pts))
    for _ in range(36):   # small dashes / blobs
        x = rng.uniform(b.left(), b.right()); y = rng.uniform(b.top(), b.bottom())
        L = rng.uniform(6, 26); ang = rng.uniform(-1.2, 1.2)
        out.append(('dash', [(x, y), (x + math.cos(ang) * L, y + math.sin(ang) * L)]))
    return out


def draw_map(canvas, name, cx, cy, scale=1.0, alpha=255, outline_w=24.0):
    """Draw the map with its bounding-box centre at (cx, cy)."""
    path, j = load_outline(name)
    b = path.computeTightBounds()
    canvas.save()
    canvas.translate(cx, cy)
    canvas.scale(scale, scale)
    canvas.translate(-(b.left() + b.right()) / 2, -(b.top() + b.bottom()) / 2)
    if alpha < 255:
        canvas.saveLayerAlpha(None, int(alpha))
    # soft dark shadow so the shape lifts off the stage
    sh = paint('#000000', alpha=150)
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    canvas.save(); canvas.translate(0, 8); canvas.drawPath(path, sh); canvas.restore()
    canvas.drawPath(path, paint(OUTLINE, stroke=outline_w * 2))
    canvas.drawPath(path, paint(FILL))
    canvas.save()
    canvas.clipPath(path, skia.ClipOp.kIntersect, True)
    for kind, pts in doodles(name):
        if kind == 'ridge':
            p = skia.Path(); p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            canvas.drawPath(p, paint(DOODLE, stroke=8, alpha=200))
        else:
            p = skia.Path(); p.moveTo(*pts[0]); p.lineTo(*pts[1])
            canvas.drawPath(p, paint(DOODLE, stroke=9, alpha=200))
    canvas.restore()
    # inner edge line (slightly darker band just inside the outline)
    canvas.drawPath(path, paint('#6FB34E', stroke=6, alpha=160))
    if alpha < 255:
        canvas.restore()
    canvas.restore()


def map_point(name, cx, cy, scale, pt):
    """Convert a map-space point (projection px) to canvas coordinates."""
    path, j = load_outline(name)
    b = path.computeTightBounds()
    return (cx + (pt[0] - (b.left() + b.right()) / 2) * scale,
            cy + (pt[1] - (b.top() + b.bottom()) / 2) * scale)


def draw_dot(canvas, x, y, r=17, visible=True):
    if not visible:
        return
    canvas.drawCircle(x, y, r + 3.5, paint('#3A0000'))
    canvas.drawCircle(x, y, r, paint('#E00000'))
    canvas.drawCircle(x - r * 0.3, y - r * 0.3, r * 0.35, paint('#FF5A4F', alpha=150))


def dot_pulse_visible(frames_since_appear):
    """Pulse on/off every 2-3 frames for ~0.5 s, then steady (measured on the source)."""
    f = frames_since_appear
    if f >= 15:
        return True
    return (f // 2) % 2 == 0
