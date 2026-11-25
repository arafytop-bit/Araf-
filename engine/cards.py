"""Title cards, kinetic titles and illustrated portraits (BLUEPRINT 3.1, 5.7, 5.8)."""
import functools
import numpy as np
import cv2
import skia
from .core import W, H, paint, rgb, ease_out_cubic, poly_path
from .host import draw_character
from .text import draw_text, size_for_cap, text_width, CAP


# ---------------- illustrated portrait (stand-in for a real photo) ----------------
def make_portrait(pal, expr='neutral', w=470, h=610, suit=True, aged=True, seed=5):
    s = skia.Surface(w, h)
    c = s.getCanvas()
    sh = skia.GradientShader.MakeLinear(points=[(0, 0), (0, h)], colors=[rgb('#D3D0C8'), rgb('#A9A59C')])
    c.drawRect(skia.Rect(0, 0, w, h), paint('#FFFFFF', shader=sh))
    for y in range(40, h, 46):            # mugshot height lines
        c.drawLine(0, y, w, y, paint('#8C877E', stroke=2.5, cap='butt'))
    R = 150
    hx, hy = w / 2, h * 0.43
    draw_character(c, hx, hy, R, pose='hips', expr=expr, pal=pal, show_rim=False)
    if suit:  # white collar + tie over the dark jacket
        def P(pts):
            return poly_path([(hx + x * R, hy + y * R) for x, y in pts])
        c.drawPath(P([(-0.30, 0.98), (0.0, 1.30), (0.30, 0.98), (0.16, 0.95), (0.0, 1.10), (-0.16, 0.95)]), paint('#F2F2F2'))
        c.drawPath(P([(-0.07, 1.10), (0.07, 1.10), (0.11, 1.75), (0.0, 1.88), (-0.11, 1.75)]), paint('#5A1E22'))
        c.drawPath(P([(-0.07, 1.10), (0.07, 1.10), (0.11, 1.75), (0.0, 1.88), (-0.11, 1.75)]), paint('#000000', stroke=5))
    a = s.makeImageSnapshot().toarray()[:, :, :3].astype(np.float32)  # BGR order (BGRA surface)
    if aged:
        lum = a[..., 0] * 0.114 + a[..., 1] * 0.587 + a[..., 2] * 0.299
        sep = np.dstack([lum * 0.78, lum * 0.95 + 6, lum * 1.06 + 12])   # B,G,R
        a = 0.25 * a + 0.75 * sep
        a = cv2.GaussianBlur(a, (0, 0), 0.8)
        rng = np.random.default_rng(seed)
        a += rng.normal(0, 7, a.shape[:2])[..., None]
        yy, xx = np.mgrid[0:h, 0:w]
        v = 1 - 0.28 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        a *= v[..., None]
    a = np.clip(a, 0, 255).astype(np.uint8)
    rgba = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)


def draw_photo(canvas, img, cx, cy, height, alpha=255, edge=True, shadow=True):
    sc = height / img.height()
    w = img.width() * sc
    r = skia.Rect(cx - w / 2, cy - height / 2, cx + w / 2, cy + height / 2)
    if shadow:
        sp = paint('#000000', alpha=int(200 * alpha / 255))
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
        canvas.drawRect(r.makeOffset(6, 10), sp)
    p = skia.Paint(AntiAlias=True)
    p.setAlpha(int(alpha))
    canvas.drawImageRect(img, r, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    if edge:
        canvas.drawRect(r, paint('#111111', stroke=3, alpha=alpha))


# ---------------- fugitive title card ----------------
def draw_title_card(canvas, number, lines, portrait, t_frames):
    """Rank number (red), one word per line (silver), portrait right. Hard cut, then a
    4-frame settle 106%->100% and a slow 0.6%/s push-in."""
    settle = 1.06 - 0.06 * ease_out_cubic(t_frames / 4.0)
    push = 1.0 + 0.006 * (t_frames / 30.0)
    sc = settle * push
    canvas.save()
    canvas.translate(W / 2, H / 2)
    canvas.scale(sc, sc)
    canvas.translate(-W / 2, -H / 2)
    cap_name, pitch = 70.0, 120.0
    n = len(lines)
    top = 590 - ((n - 1) * pitch + cap_name) / 2
    x0 = 281
    size_name = size_for_cap(cap_name)
    for i, ln in enumerate(lines):
        draw_text(canvas, ln, x0, top + cap_name + i * pitch, size_name, style='silver', tracking=0.03)
    cap_num = 56.0
    draw_text(canvas, str(number), x0 + 6, top - 50, size_for_cap(cap_num), style='red', tracking=0.0)
    draw_photo(canvas, portrait, 1350, 560, 610)
    canvas.restore()


# ---------------- kinetic title ----------------
class KineticTitle:
    """Words pre-placed as dim ghosts; each lights up on its spoken word (+/-2 frames).
    Layout measured on the source (lines at 18% / 37% / 59% of H)."""

    def __init__(self, lines):
        # lines: list of (baseline_y, [(word, cap_px, style, light_frame), ...], target_width)
        self.lines = lines
        self.layout = []
        for base_y, words, target_w in lines:
            gap_k = 0.95
            widths = [text_width(w, size_for_cap(cp), 0.07) for w, cp, st, lf in words]
            gaps = [gap_k * max(words[i][1], words[i + 1][1]) for i in range(len(words) - 1)]
            total = sum(widths) + sum(gaps)
            k = target_w / total if target_w else 1.0
            x = W / 2 - total * k / 2
            placed = []
            for i, (w, cp, st, lf) in enumerate(words):
                placed.append((w, x, base_y, size_for_cap(cp * k), st, lf))
                x += widths[i] * k + (gaps[i] * k if i < len(gaps) else 0)
            self.layout.append(placed)

    def draw(self, canvas, f, f_start, f_end):
        prog = (f - f_start) / max(1, (f_end - f_start))
        sc = 0.90 + 0.10 * prog          # slow push-in through the shot
        canvas.save()
        canvas.translate(W / 2, H * 0.41)
        canvas.scale(sc, sc)
        canvas.translate(-W / 2, -H * 0.41)
        for placed in self.layout:
            for w, x, y, size, st, lf in placed:
                lit = f >= lf
                ramp = min(1.0, (f - lf + 1) / 2.0) if lit else 0.0
                if ramp < 1.0:
                    draw_text(canvas, w, x, y, size, style=st, tracking=0.07, ghost=True)
                if ramp > 0:
                    draw_text(canvas, w, x, y, size, style=st, tracking=0.07, alpha=int(255 * ramp))
        canvas.restore()
