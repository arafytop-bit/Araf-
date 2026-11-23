"""YouTube thumbnails in the video's doodle style. Renders at 1920x1080 and saves 1280x720 JPG/PNG + small-size previews.
usage: thumbnail.py outdir"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
import resvg_py
from PIL import Image
import dd
from dd import *
from props import REG
from chars import person

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)

def A(kind, x, y, s=1.0, rot=0.0, **kw):
    return G(REG[kind](**kw), x, y, s, rot)

def otext(x, y, s, size, color=INK, halo=WHITE, hw=26, anchor="middle", spacing=None, rot=0, ink_outline=0):
    """Bold handwritten text with a white halo (sticker look) and optional dark outline."""
    sp = size * 0.03 if spacing is None else spacing
    tr = f' transform="rotate({rot:.1f} {x:.1f} {y:.1f})"' if rot else ""
    base = (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Gaegu" font-weight="700" font-size="{size:.1f}" text-anchor="{anchor}" '
            f'letter-spacing="{sp:.1f}"{tr}')
    t = esc(s)
    out = f'{base} fill="{halo}" stroke="{halo}" stroke-width="{hw:.1f}" stroke-linejoin="round">{t}</text>'
    if ink_outline: out += f'{base} fill="{color}" stroke="{INK}" stroke-width="{ink_outline:.1f}" stroke-linejoin="round">{t}</text>'
    out += f'{base} fill="{color}" stroke="{color}" stroke-width="{size*0.025:.1f}" stroke-linejoin="round">{t}</text>'
    return out

def render(body, name, bg="#FFFFFF"):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><rect width="1920" height="1080" fill="{bg}"/>{body}</svg>'
    png = resvg_py.svg_to_bytes(svg_string=svg, font_files=dd.FONT_FILES, skip_system_fonts=True)
    im = Image.open(io.BytesIO(bytes(png))).convert("RGB")
    t = im.resize((1280, 720), Image.LANCZOS)
    t.save(f"{OUT}/{name}.png", optimize=True); t.save(f"{OUT}/{name}.jpg", quality=92, optimize=True, progressive=True)
    return t

# ---------------------------------------------------------------- A: YOU PAY EITHER WAY (bill + shocked narrator)
def big_bill(seed=2, w=620):
    """Thumbnail bill: two huge lines so 'AI' reads even at phone size."""
    h = w * 1.25; sd = seed * 1000 + 50
    s = rect(-w / 2, -h / 2, w, h, WHITE, sd, 7)
    s += rect(-w / 2, -h / 2, w, h * 0.2, "#2F5D8A", sd + 1, 7) + T(0, -h / 2 + h * 0.135, "ELECTRIC BILL", w * 0.1, WHITE, 700, spacing=2)
    y1, y2 = -h * 0.08, h * 0.17
    s += T(-w / 2 + 40, y1, "Power", w * 0.12, INK, 700, "start") + T(w / 2 - 40, y1, "$90", w * 0.12, INK, 700, "end", family="Comic Neue")
    s += rect(-w / 2 + 18, y2 - w * 0.13, w - 36, w * 0.17, HILITE, sd + 2, 0, None)
    s += T(-w / 2 + 40, y2, "AI", w * 0.16, INK, 700, "start") + T(w / 2 - 40, y2, "$$$$", w * 0.14, RED, 700, "end", family="Comic Neue")
    s += circle_mark(0, y2 - w * 0.045, w * 0.5, w * 0.13, sd + 3, 12)
    s += line([(-w / 2 + 30, h * 0.3), (w / 2 - 30, h * 0.3)], sd + 4, 6)
    s += T(-w / 2 + 40, h * 0.42, "TOTAL", w * 0.1, INK, 700, "start") + T(w / 2 - 40, h * 0.42, "???", w * 0.13, RED, 700, "end", family="Comic Neue")
    return s

def thumb_a():
    b = ""
    b += A("burst", 640, 600, r=520, text="", fill="#FFE8A3", seed=3)
    b += G(big_bill(), 630, 610, rot=-7)
    b += A("arrow_up", 1015, 760, h=380, seed=1)
    b += G(person(seed=4, k=1.25, pose="shrug", mouth="o", brow="worried", sweat=True, look=-0.6, hair="spiky"), 1510, 620)
    b += otext(1420, 235, "YOU PAY", 232, RED, hw=30)
    b += otext(1420, 380, "EITHER WAY", 136, INK, hw=26)
    return render(b, "thumb_A_you_pay_either_way")

# ---------------------------------------------------------------- B: TAILS YOU PAY (coin flip, winners vs you)
def thumb_b():
    b = ""
    b += A("burst", 960, 560, r=430, text="", fill="#FFE8A3", seed=2)
    b += A("coin", 960, 560, r=300, text="TAILS", sub="you pay", color="#C9C9C9", seed=1)
    for i, (dx, dy) in enumerate(((-380, -300), (-430, -200), (380, -300), (430, -200))):   # flip motion lines
        b += line([(960 + dx * 0.9, 560 + dy * 0.9), (960 + dx * 1.08, 560 + dy * 1.08)], 30 + i, 9, DGREY)
    b += G(person(seed=7, k=0.75, pose="arms_up", mouth="open", hair="none", hat="hardhat", shirt="#37474F", tie=YELLOW, skin=SKIN2), 250, 470)
    b += G(person(seed=8, k=0.75, pose="arms_up", mouth="grin", hair="swoop", shirt="#8E8E8E", glasses="sun"), 470, 470)
    b += A("money_bag", 360, 900, k=1.0, seed=9)
    b += G(person(seed=4, k=1.05, pose="hold", mouth="frown", brow="worried", sweat=True, hair="spiky"), 1610, 470)
    b += A("bill", 1620, 860, w=300, rot=8, red_total=True, seed=6)
    b += otext(360, 200, "THEY WIN", 120, DGREEN, hw=22)
    b += otext(1600, 170, "YOU PAY", 150, RED, hw=24)
    return render(b, "thumb_B_tails_you_pay")

# ---------------------------------------------------------------- C: AI IS ON YOUR BILL (data center plugged into your house)
def thumb_c():
    b = ""
    b += A("burst", 470, 560, r=420, text="", fill="#D6EBFF", seed=4)
    b += A("data_center", 470, 600, w=640, label="AI DATA CENTER", seed=1)
    b += A("chip", 470, 300, w=210, face=True, mouth="smile", seed=2)
    b += A("extension_cord", 0, 0, x0=800, y0=760, x1=1260, y1=820, sag=70, seed=3)
    b += A("house", 1430, 760, w=330, color="#E9C46A", seed=4)
    b += A("bill", 1700, 610, w=250, rot=10, red_total=True, total="$$$$", seed=5)
    b += A("arrow_up", 1850, 560, h=300, seed=6)
    b += G(person(seed=4, k=0.8, pose="shrug", mouth="o", brow="worried", sweat=True, hair="spiky"), 1180, 470)
    b += otext(1300, 190, "AI IS ON", 140, INK, hw=26)
    b += otext(1300, 345, "YOUR BILL", 170, RED, hw=28)
    return render(b, "thumb_C_ai_is_on_your_bill")

if __name__ == "__main__":
    ims = [thumb_a(), thumb_b(), thumb_c()]
    # review sheet: full size + YouTube feed size (~360x202) + small sidebar size (~168x94)
    W = 1280; sheet = Image.new("RGB", (W + 380 + 190, 3 * 730), (24, 24, 24))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 730))
        sheet.paste(im.resize((360, 202), Image.LANCZOS), (W + 10, i * 730 + 10))
        sheet.paste(im.resize((168, 94), Image.LANCZOS), (W + 380, i * 730 + 10))
    sheet.save(f"{OUT}/review_sheet.png")
    print("ok")
