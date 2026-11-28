"""Deliverable stills: rebuild-only 1080p frames plus reference | rebuild side-by-sides.

usage: python analysis/scripts/b10_deliver_stills.py <tag>    (reads work/hq/<tag>_f030/f050/f143.png, 3840x2160 renders)
writes analysis/lookdev/deliver/<n>_<name>.png (side-by-side, reference-derived: kept out of git)
   and analysis/lookdev/deliver/<n>_<name>_rebuild_only.png (original work only: committed)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

TAG = sys.argv[1] if len(sys.argv) > 1 else 'v1'
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)


def pair(fr, box, name, note):
    ours = Image.open(f'work/hq/{TAG}_f{fr:03d}.png').convert('RGB').resize((1920, 1080), Image.LANCZOS)
    ref = Image.open(f'work/frames/f_{fr:05d}.png').convert('RGB').resize((1920, 1080), Image.LANCZOS)
    a, b = ref.crop(box), ours.crop(box); w, h = a.size
    c = Image.new('RGB', (w * 2 + 20, h + 60), (30, 30, 30)); c.paste(a, (0, 60)); c.paste(b, (w + 20, 60)); d = ImageDraw.Draw(c)
    d.text((10, 14), f'REFERENCE f{fr} (480p source, upscaled)', font=F, fill='yellow')
    d.text((w + 30, 14), f'REBUILD f{fr} - {note}', font=F, fill='cyan')
    c.save(f'analysis/lookdev/deliver/{name}.png'); b.save(f'analysis/lookdev/deliver/{name}_rebuild_only.png')


pair(30, (0, 0, 1920, 1080), '1_portrait_f030', 'code-built plate; hero art pending (A02)')
pair(50, (0, 0, 1920, 1080), '2_title_card_f050', 'title + plate; hero art pending (A02)')
pair(143, (0, 0, 1920, 1080), '3_poster_all_items_f143', 'poster print pending (A03)')
pair(143, (560, 330, 1380, 720), '4_poster_close_f143', 'complete (no illustrated art in this crop)')
print('deliverable stills written from', TAG)
