"""Render every registered asset (default args) into contact sheets for visual QA."""
import sys, io, traceback
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import resvg_py, numpy as np
from PIL import Image, ImageDraw
import props, dd
out = sys.argv[1]; names = sys.argv[2].split(",") if len(sys.argv) > 2 else sorted(props.REG)
W, H = 2400, 1800
cells = []
for n in names:
    try:
        body = props.REG[n](seed=0)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><g transform="translate({W/2} {H/2})">{body}</g></svg>'
        png = resvg_py.svg_to_bytes(svg_string=svg, font_files=dd.FONT_FILES, skip_system_fonts=True)
        im = Image.open(io.BytesIO(bytes(png))).convert("RGBA")
        bb = im.getbbox() or (0, 0, 10, 10)
        bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im); c = bg.convert("RGB").crop(bb); c.thumbnail((300, 260))
        cells.append((n, c, None))
    except Exception as e:
        cells.append((n, None, str(e)[:60])); traceback.print_exc()
cols = 8; cw, ch = 310, 290
rows = (len(cells) + cols - 1) // cols
for page in range(0, rows, 6):
    sub = cells[page * cols:(page + 6) * cols]
    sheet = Image.new("RGB", (cols * cw, ((len(sub) + cols - 1) // cols) * ch), (235, 235, 235)); d = ImageDraw.Draw(sheet)
    for i, (n, c, err) in enumerate(sub):
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(Image.new("RGB", (cw - 6, ch - 6), "white"), (x + 3, y + 3))
        if c: sheet.paste(c, (x + (cw - c.width) // 2, y + 24 + (260 - c.height) // 2))
        d.text((x + 6, y + 5), n if not err else n + " ERR " + err, fill=(200, 0, 0) if err else (30, 30, 160))
    sheet.save(f"{out}/gallery_{page // 6}.png")
print("done", len(cells))
