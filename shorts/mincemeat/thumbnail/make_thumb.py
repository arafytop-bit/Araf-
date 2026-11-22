# Thumbnails from the film's own frames: vertical 1080x1920 (Shorts) and 1280x720 (search/browse).
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os
F = "/home/user/Araf-/out/final/"
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
INK, YEL, WHITE, RED = (36, 23, 38), (255, 216, 74), (255, 255, 255), (214, 51, 61)
corpse = Image.open(F + "th_6.6.png").convert("RGB")   # dead agent, fly on his cap
hitler = Image.open(F + "th_69.6.png").convert("RGB")  # chomping the hook

def text(d, xy, s, size, fill, anchor="mm", stroke=None):
    f = ImageFont.truetype(FONT, size)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke or max(6, size // 9), stroke_fill=INK)

def cover(img, w, h, cx=0.5, cy=0.5, zoom=1.0):
    s = max(w / img.width, h / img.height) * zoom
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = min(max(0, round(im.width * cx - w / 2)), im.width - w); y = min(max(0, round(im.height * cy - h / 2)), im.height - h)
    return im.crop((x, y, x + w, y + h))

def badge(img, size, border=16):
    im = cover(img, size, size, 0.5, 0.5, 1.05)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size + 2 * border, size + 2 * border), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, out.width - 1, out.height - 1), fill=YEL + (255,))
    ImageDraw.Draw(out).ellipse((border // 2, border // 2, out.width - 1 - border // 2, out.height - 1 - border // 2), outline=INK + (255,), width=6)
    out.paste(im, (border, border), m)
    return out

def vignette(im, k=0.55):
    w, h = im.size
    v = Image.new("L", (w, h), 0); ImageDraw.Draw(v).ellipse((-w * 0.2, -h * 0.1, w * 1.2, h * 1.1), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(min(w, h) // 6))
    dark = Image.new("RGB", (w, h), (20, 12, 24))
    return Image.composite(im, Image.blend(im, dark, k), v)

# ---- vertical 1080x1920 ----
V = vignette(cover(corpse, 1080, 1920, 0.5, 0.3, 1.12))
d = ImageDraw.Draw(V)
text(d, (540, 250), "BRITAIN'S TOP SPY", 92, WHITE)
text(d, (540, 430), "WAS DEAD", 190, YEL)
b = badge(hitler, 430)
V.paste(b, (1080 - b.width - 40, 1180), b)
text(d, (330, 1330), "...AND HE", 92, WHITE)
text(d, (330, 1450), "FOOLED", 118, WHITE)
text(d, (330, 1580), "HITLER", 140, RED)
V.save("thumb_vertical_1080x1920.jpg", quality=93)

# ---- horizontal 1280x720 ----
H = Image.new("RGB", (1280, 720))
H.paste(vignette(cover(corpse, 700, 720, 0.5, 0.3, 0.9), 0.35), (0, 0))
H.paste(vignette(cover(hitler, 580, 720, 0.5, 0.5, 0.95), 0.35), (700, 0))
d = ImageDraw.Draw(H)
d.polygon([(690, 0), (730, 0), (690, 720), (650, 720)], fill=YEL)
d.line([(690, 0), (650, 720)], fill=INK, width=8); d.line([(730, 0), (690, 720)], fill=INK, width=8)
text(d, (330, 640), "DEAD MAN", 120, YEL)
text(d, (990, 75), "FOOLED", 92, WHITE)
text(d, (990, 175), "HITLER", 112, RED)
H.save("thumb_horizontal_1280x720.jpg", quality=93)
print("ok")
