"""Core helpers for the stick-figure explainer renderer (1920x1080 @ 30 fps).

All geometry/timing constants come from analysis/BLUEPRINT.md.
"""
import math
import functools
import numpy as np
import skia

W, H, FPS = 1920, 1080, 30
ASSETS = __file__.rsplit('/', 1)[0] + '/assets'


def rgb(hexstr, a=255):
    h = hexstr.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def paint(color='#000000', stroke=None, alpha=255, cap='round', join='round', shader=None, aa=True):
    p = skia.Paint(AntiAlias=aa)
    if isinstance(color, str):
        p.setColor(rgb(color, alpha))
    else:
        p.setColor(color)
        if alpha != 255:
            p.setAlpha(alpha)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap({'round': skia.Paint.kRound_Cap, 'butt': skia.Paint.kButt_Cap,
                        'square': skia.Paint.kSquare_Cap}[cap])
        p.setStrokeJoin({'round': skia.Paint.kRound_Join, 'miter': skia.Paint.kMiter_Join,
                         'bevel': skia.Paint.kBevel_Join}[join])
    else:
        p.setStyle(skia.Paint.kFill_Style)
    if shader is not None:
        p.setShader(shader)
    return p


def catmull_rom_path(pts, closed=True, tension=1.0):
    """Smooth path through points (Catmull-Rom converted to cubic Beziers)."""
    path = skia.Path()
    n = len(pts)
    if n < 2:
        return path
    P = [tuple(map(float, p)) for p in pts]
    path.moveTo(*P[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else P[(i + 1) % n]
        t = tension / 6.0
        c1 = (p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t)
        c2 = (p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t)
        path.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        path.close()
    return path


def poly_path(pts, closed=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if closed:
        path.close()
    return path


# ---------- easing ----------
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp01(t)
    return 3 * t * t - 2 * t * t * t


def ease_out_back(t, s=1.70158):
    t = clamp01(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def damped_swing(t, freq=1.6, decay=3.0):
    """Pendulum-like settle: 1 -> 0 oscillation."""
    return math.exp(-decay * t) * math.cos(2 * math.pi * freq * t)


# ---------- background ----------
@functools.lru_cache(maxsize=1)
def vignette_array():
    """Elliptical radial vignette measured on the source: #0B0B0B flat to r=0.2,
    falling to ~#030303 at the frame edge and ~#010101 in the corners."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    prof_r = np.array([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0, 1.1, 1.2, 1.3, 1.5], np.float32)
    prof_v = np.array([11, 11, 10.7, 10.2, 9.6, 8.9, 7.7, 6.4, 5.2, 4.2, 3.0, 2.2, 1.7, 1.3, 1.0], np.float32)
    v = np.interp(r, prof_r, prof_v)
    # tiny dither to avoid banding after H.264
    v = v + np.random.default_rng(7).uniform(-0.5, 0.5, v.shape)
    v = np.clip(np.round(v), 0, 255).astype(np.uint8)
    a = np.empty((H, W, 4), np.uint8)
    a[..., 0] = v; a[..., 1] = v; a[..., 2] = v; a[..., 3] = 255
    return a


@functools.lru_cache(maxsize=1)
def vignette_image():
    return skia.Image.fromarray(vignette_array(), colorType=skia.ColorType.kRGBA_8888_ColorType)


def draw_background(canvas):
    canvas.drawImage(vignette_image(), 0, 0)


def new_surface():
    return skia.Surface(W, H)


def snapshot(surface):
    return surface.makeImageSnapshot()


def blur_dim_image(img, sigma=14.0, gain=0.42, scale=1.06):
    """Previous visual pushed behind an overlay: blurred, darkened, slightly enlarged
    (blueprint section 1 rule 8: sigma ~10-22 px @1080p, brightness 30-50%)."""
    s = new_surface()
    c = s.getCanvas()
    c.clear(skia.ColorBLACK)
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kClamp))
    g = gain
    p.setColorFilter(skia.ColorFilters.Matrix([g, 0, 0, 0, 0, 0, g, 0, 0, 0, 0, 0, g, 0, 0, 0, 0, 0, 1, 0]))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(scale, scale)
    c.translate(-W / 2, -H / 2)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()
    return s.makeImageSnapshot()


def draw_image_centered(canvas, img, cx, cy, scale=1.0, alpha=255, rot=0.0):
    p = skia.Paint(AntiAlias=True)
    p.setAlpha(int(alpha))
    canvas.save()
    canvas.translate(cx, cy)
    if rot:
        canvas.rotate(rot)
    canvas.scale(scale, scale)
    canvas.drawImage(img, -img.width() / 2, -img.height() / 2,
                     skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    canvas.restore()
