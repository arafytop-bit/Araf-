"""YouTube channel branding in the video's doodle style: profile picture, banner, watermark + review previews.
usage: branding.py outdir ["Channel Name"] ["tagline"]"""
import sys, os, io, math
sys.path.insert(0, os.path.dirname(__file__))
import resvg_py
from PIL import Image, ImageDraw
import dd
from dd import *
from props import REG
from chars import person

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
NAME = sys.argv[2] if len(sys.argv) > 2 else "Sketchy Economics"
TAG = sys.argv[3] if len(sys.argv) > 3 else "Who really pays? Economics, explained in doodles."
BRAND_YELLOW = "#FFCF3F"
os.makedirs(OUT, exist_ok=True)

def A(kind, x, y, s=1.0, rot=0.0, op=1.0, **kw): return G(REG[kind](**kw), x, y, s, rot, op)

def raster(body, W, H, bg=None):
    rect_ = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{rect_}{body}</svg>'
    png = resvg_py.svg_to_bytes(svg_string=svg, font_files=dd.FONT_FILES, skip_system_fonts=True)
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")

def otext(x, y, s, size, color=INK, halo=WHITE, hw=0, anchor="middle", spacing=None):
    sp = size * 0.03 if spacing is None else spacing
    base = f'<text x="{x:.1f}" y="{y:.1f}" font-family="Gaegu" font-weight="700" font-size="{size:.1f}" text-anchor="{anchor}" letter-spacing="{sp:.1f}"'
    out = f'{base} fill="{halo}" stroke="{halo}" stroke-width="{hw:.1f}" stroke-linejoin="round">{esc(s)}</text>' if hw else ""
    return out + f'{base} fill="{color}" stroke="{color}" stroke-width="{size*0.025:.1f}" stroke-linejoin="round">{esc(s)}</text>'

# ---------------------------------------------------------------- profile picture (800x800, shown as a circle)
def avatar():
    W = 800
    b = f'<circle cx="400" cy="400" r="400" fill="{BRAND_YELLOW}"/>'
    b += G(person(seed=3, k=1.72, pose="hips", mouth="smirk", brow="raise", look=0.35, hair="spiky", body=False), 395, 430)
    im = raster(b, W, W, BRAND_YELLOW)
    im.convert("RGB").save(f"{OUT}/profile_picture_800x800.png", optimize=True)
    return im

# ---------------------------------------------------------------- watermark (150x150, transparent)
def watermark():
    b = '<circle cx="75" cy="75" r="71" fill="#FFFFFF" stroke="#111111" stroke-width="5"/>'
    b += G(person(seed=3, k=0.29, pose="hips", mouth="smile", hair="spiky", body=False), 74, 80)
    im = raster(b, 150, 150, None)
    im.save(f"{OUT}/watermark_150x150.png", optimize=True)
    return im

# ---------------------------------------------------------------- banner (2560x1440; text-safe area 1546x423 centred)
def banner():
    W, H = 2560, 1440; sx0, sy0, sx1, sy1 = 507, 508, 2053, 931
    b = ""
    # faint doodle wallpaper outside the desktop strip (visible on TV only)
    icons = [("bill", dict(w=150)), ("money_bag", dict(k=0.55)), ("bolt", dict(h=110)), ("data_center", dict(w=210, label="")),
             ("coin", dict(r=70, text="$")), ("tower", dict(h=200)), ("calendar", dict(w=120, top="", big="")), ("chip", dict(w=120)),
             ("house", dict(w=170)), ("arrow_up", dict(h=150)), ("pie", dict(r=80, frac=0.3)), ("envelope", dict(w=170, label=""))]
    k = 0
    for row, y in enumerate((130, 330, 1110, 1310)):
        for col in range(9):
            x = 140 + col * 285 + (row % 2) * 140
            kind, kw = icons[k % len(icons)]; k += 1
            b += A(kind, x, y, rot=((k * 37) % 30) - 15, op=0.13, seed=k, **kw)
    # desktop-only strip edges (outside mobile safe area)
    b += A("data_center", 250, 735, seed=5, w=330, label="")
    b += A("bolt", 400, 560, seed=6, h=120)
    b += A("bill", 2290, 720, seed=7, w=230, rot=8, red_total=True)
    b += A("arrow_up", 2470, 690, seed=8, h=230)
    b += A("money_bag", 2160, 860, seed=9, k=0.6)
    # safe area: narrator + name + tagline
    b += G(person(seed=3, k=0.56, pose="present", mouth="open", brow="raise", hair="spiky"), 740, 607)
    size = 190
    while text_w(NAME, size, 700, spacing=size * 0.03) > 1080 and size > 90: size -= 4
    nx = 1460
    b += otext(nx, 705, NAME, size, INK)
    nw = text_w(NAME, size, 700, spacing=size * 0.03)
    b += line([(nx - nw / 2, 742), (nx + nw / 2, 748)], 11, 12, RED, 3, 50)
    tsize = 58
    while text_w(TAG, tsize, 700) > 1060 and tsize > 30: tsize -= 2
    b += otext(nx, 845, TAG, tsize, "#333333")
    im = raster(b, W, H, WHITE)
    im.convert("RGB").save(f"{OUT}/banner_2560x1440.png", optimize=True)
    im.convert("RGB").save(f"{OUT}/banner_2560x1440.jpg", quality=92, optimize=True)
    return im, (sx0, sy0, sx1, sy1)

if __name__ == "__main__":
    av = avatar(); wm = watermark(); bn, safe = banner()
    # review sheet: banner with safe areas + avatar at YouTube display sizes + watermark
    rv = bn.convert("RGB").copy(); d = ImageDraw.Draw(rv)
    d.rectangle([0, 508, 2559, 931], outline=(30, 120, 255), width=6)          # desktop strip
    d.rectangle(list(safe), outline=(255, 0, 140), width=6)                   # mobile / text-safe
    rv = rv.resize((1280, 720), Image.LANCZOS)
    sheet = Image.new("RGB", (1280 + 420, 720), (40, 40, 40)); sheet.paste(rv, (0, 0))
    mask_big = Image.new("L", (800, 800), 0); ImageDraw.Draw(mask_big).ellipse([0, 0, 799, 799], fill=255)
    circ = Image.new("RGBA", (800, 800), (0, 0, 0, 0)); circ.paste(av, (0, 0), mask_big)
    y = 20
    for sz in (176, 98, 48, 36):
        sheet.paste(circ.resize((sz, sz), Image.LANCZOS), (1300 + (176 - sz) // 2, y), circ.resize((sz, sz), Image.LANCZOS)); y += sz + 24
    sheet.paste(wm.resize((120, 120), Image.LANCZOS), (1520, 40), wm.resize((120, 120), Image.LANCZOS))
    sheet.save(f"{OUT}/review_branding.png")
    print("ok")
