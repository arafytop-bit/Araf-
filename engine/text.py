"""Typography: one heavy, wide geometric caps family (Archivo Expanded Black as the
closest free match to the source font), silver-white names, glossy deep-red callouts."""
import functools
import numpy as np
import skia
from .core import ASSETS, W, H, paint, rgb

FONT_PATH = ASSETS + '/fonts/ArchivoExp-900.ttf'
CAP = 0.686  # cap height / font size for this face


@functools.lru_cache(maxsize=None)
def typeface():
    return skia.Typeface.MakeFromFile(FONT_PATH)


@functools.lru_cache(maxsize=256)
def font(size):
    f = skia.Font(typeface(), float(size))
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def size_for_cap(cap_px):
    return cap_px / CAP


def glyph_layout(s, size, tracking=0.04):
    """x offsets per character with extra tracking (fraction of font size)."""
    f = font(size)
    xs, x = [], 0.0
    for ch in s:
        xs.append(x)
        x += f.measureText(ch) + (tracking * size if ch != ' ' else 0.0)
    total = x - (tracking * size if s and s[-1] != ' ' else 0.0)
    return xs, total


def text_width(s, size, tracking=0.04):
    return glyph_layout(s, size, tracking)[1]


@functools.lru_cache(maxsize=1)
def grunge_image():
    """Subtle distressed texture (opaque greys ~0.78-1.0), applied with kModulate."""
    rng = np.random.default_rng(11)
    small = rng.uniform(0.0, 1.0, (H // 6, W // 6)).astype(np.float32)
    import cv2
    big = cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), 2.0)
    fine = rng.uniform(0, 1, (H, W)).astype(np.float32)
    v = 0.90 + 0.10 * big - 0.10 * (fine > 0.985)
    # a few scratch lines
    for _ in range(140):
        x0, y0 = rng.integers(0, W), rng.integers(0, H)
        ln = rng.integers(10, 60)
        ang = rng.uniform(-0.6, 0.6)
        x1, y1 = int(x0 + ln * np.cos(ang)), int(y0 + ln * np.sin(ang))
        cv2.line(v, (int(x0), int(y0)), (x1, y1), 0.80, 1)
    v = np.clip(v, 0.72, 1.0)
    g = (v * 255).astype(np.uint8)
    a = np.dstack([g, g, g, np.full_like(g, 255)])
    return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)


def _draw_chars(canvas, s, x, y, size, p, tracking):
    f = font(size)
    xs, _ = glyph_layout(s, size, tracking)
    for ch, dx in zip(s, xs):
        if ch != ' ':
            canvas.drawString(ch, x + dx, y, f, p)


SILVER = ('#FFFFFF', '#F4F4F4', '#C9C9C9')
RED = ('#FF3B30', '#E3060E', '#A10008')
CORAL = ('#FF6A6F', '#F0484E', '#C8343A')


def draw_text(canvas, s, x, y, size, style='silver', tracking=0.04, alpha=255, shadow=True,
              grunge=True, outline=None, outline_color='#000000', ghost=False):
    """Draw caps text with its baseline at y and left edge at x."""
    cap = size * CAP
    if style in ('silver', 'red', 'coral'):
        cols = {'silver': SILVER, 'red': RED, 'coral': CORAL}[style]
        shader = skia.GradientShader.MakeLinear(
            points=[(0, y - cap), (0, y)], colors=[rgb(c) for c in cols], positions=[0.0, 0.45, 1.0])
        fill = paint('#FFFFFF', alpha=255, shader=shader)
    else:
        fill = paint(style)
    canvas.saveLayerAlpha(None, int(alpha))
    if shadow:
        sp = paint('#000000', alpha=210)
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1.0, size * 0.035)))
        _draw_chars(canvas, s, x + size * 0.02, y + size * 0.045, size, sp, tracking)
    if outline:
        op = paint(outline_color, stroke=outline)
        _draw_chars(canvas, s, x, y, size, op, tracking)
    canvas.saveLayer(None, None)
    _draw_chars(canvas, s, x, y, size, fill, tracking)
    if style == 'red':  # darker rim on the glyph edges
        ep = paint('#6E0006', stroke=max(1.0, size * 0.012), alpha=180)
        _draw_chars(canvas, s, x, y, size, ep, tracking)
    if grunge:
        gp = skia.Paint()
        gp.setBlendMode(skia.BlendMode.kModulate)
        canvas.drawImage(grunge_image(), 0, 0, skia.SamplingOptions(), gp)
    if ghost:
        gp = skia.Paint()
        gp.setColor(skia.Color(0, 0, 0, 255))
        gp.setBlendMode(skia.BlendMode.kSrcATop)
        gp.setAlpha(int(255 * 0.74))
        canvas.drawRect(skia.Rect(0, 0, W, H), gp)
    canvas.restore()
    canvas.restore()


def draw_callout(canvas, s, progress=1.0, cap_px=94.0, top_y=None, center_x=W / 2, tracking=0.035, style='red'):
    """Red callout, top centre (blueprint 5.7): fades + settles 105%->100% over ~5 frames."""
    size = size_for_cap(cap_px)
    tw = text_width(s, size, tracking)
    max_w = W * 0.90
    if tw > max_w:
        size *= max_w / tw
        tw = max_w
        cap_px = size * CAP
    if top_y is None:
        top_y = H * 0.125
    from .core import ease_out_cubic
    e = ease_out_cubic(progress)
    sc = 1.05 - 0.05 * e
    canvas.save()
    cy = top_y + cap_px / 2
    canvas.translate(center_x, cy)
    canvas.scale(sc, sc)
    canvas.translate(-center_x, -cy)
    draw_text(canvas, s, center_x - tw / 2, top_y + cap_px, size, style=style, tracking=tracking,
              alpha=int(255 * e))
    canvas.restore()


def draw_label(canvas, s, x, y, cap_px, align='left', alpha=255):
    """Map label: white caps with a black outline (baseline y)."""
    size = size_for_cap(cap_px)
    tw = text_width(s, size, 0.03)
    if align == 'center':
        x -= tw / 2
    elif align == 'right':
        x -= tw
    draw_text(canvas, s, x, y, size, style='#FFFFFF', tracking=0.03, alpha=alpha, shadow=False,
              grunge=False, outline=size * 0.16)
    return tw


# ---------------- speech captions (reference cartoon style) ----------------
SPEECH_FONT = ASSETS + '/fonts/Nunito-900.ttf'


@functools.lru_cache(maxsize=None)
def speech_typeface():
    return skia.Typeface.MakeFromFile(SPEECH_FONT)


def draw_speech(canvas, s, x, y, cap_px=40.0, tail=None, rot=0.0, alpha=255):
    """White rounded caption with a thick black outline and soft shadow, plus an optional
    short white tail line (tail = ((x0, y0), (x1, y1))) pointing at the speaker."""
    size = cap_px / 0.705
    f = skia.Font(speech_typeface(), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    canvas.save()
    canvas.translate(x, y)
    if rot:
        canvas.rotate(rot)
    canvas.saveLayerAlpha(None, int(alpha))
    sh = paint('#000000', alpha=150)
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.06))
    canvas.drawString(s, size * 0.03, size * 0.07, f, sh)
    canvas.drawString(s, 0, 0, f, paint('#111111', stroke=size * 0.16))
    canvas.drawString(s, 0, 0, f, paint('#FFFFFF'))
    canvas.restore()
    canvas.restore()
    if tail:
        (x0, y0), (x1, y1) = tail
        canvas.drawLine(x0, y0, x1, y1, paint('#111111', stroke=cap_px * 0.36))
        canvas.drawLine(x0, y0, x1, y1, paint('#FFFFFF', stroke=cap_px * 0.16))
