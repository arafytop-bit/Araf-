"""Typography: Unbounded (OFL), the open-licence near-twin of the reference's heavy wide caps face.

- real kerning from the font's GPOS 'kern' pairs (extracted once with fontTools, cached as JSON)
- glyph guard: any character missing from the font raises (no tofu boxes can ever reach a frame)
- sizes are given as CAP HEIGHT in px (cap = 0.75 em for this face)
"""
import functools
import json
import os

import skia

from ..core import ASSETS, W, H, rgb

FONT = {w: os.path.join(ASSETS, 'fonts', f'Unbounded-{w}.ttf') for w in (700, 800, 900)}
CAP = 0.75
KERN_CACHE = os.path.join(ASSETS, 'fonts', 'unbounded_kern.json')


@functools.lru_cache(maxsize=None)
def typeface(weight=800):
    return skia.Typeface.MakeFromFile(FONT[weight])


@functools.lru_cache(maxsize=None)
def _tables(weight=800):
    """(cmap set, kern dict 'AB' -> units/1000) for a weight."""
    cache = {}
    if os.path.exists(KERN_CACHE):
        cache = json.load(open(KERN_CACHE))
    key = str(weight)
    if key not in cache:
        from fontTools.ttLib import TTFont
        f = TTFont(FONT[weight])
        cmap = f.getBestCmap()
        g2c = {}
        for cp, g in cmap.items():
            g2c.setdefault(g, []).append(chr(cp))
        gpos = f['GPOS'].table
        lookups = set()
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == 'kern':
                lookups.update(fr.Feature.LookupListIndex)
        pairs = {}
        order = [g for g in f.getGlyphOrder() if g in g2c]
        for li in sorted(lookups):
            lk = gpos.LookupList.Lookup[li]
            for st in lk.SubTable:
                if lk.LookupType == 9:
                    st = st.ExtSubTable
                if st.Format == 1:
                    for gi, ps in zip(st.Coverage.glyphs, st.PairSet):
                        for pvr in ps.PairValueRecord:
                            xa = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                            if xa and (gi, pvr.SecondGlyph) not in pairs:
                                pairs[(gi, pvr.SecondGlyph)] = xa
                elif st.Format == 2:
                    cd1, cd2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                    for g1 in st.Coverage.glyphs:
                        if g1 not in g2c:
                            continue
                        rec = st.Class1Record[cd1.get(g1, 0)]
                        for g2 in order:
                            v = rec.Class2Record[cd2.get(g2, 0)].Value1
                            xa = getattr(v, 'XAdvance', 0) if v else 0
                            if xa and (g1, g2) not in pairs:
                                pairs[(g1, g2)] = xa
        kern = {}
        for (a, b), v in pairs.items():
            for ca in g2c.get(a, []):
                for cb in g2c.get(b, []):
                    kern[ca + cb] = v
        cache[key] = dict(cmap=sorted(cmap), kern=kern)
        json.dump(cache, open(KERN_CACHE, 'w'))
    t = cache[key]
    return frozenset(t['cmap']), t['kern']


def check(s, weight=800):
    cm, _ = _tables(weight)
    bad = sorted({c for c in s if ord(c) not in cm and c not in '\n'})
    if bad:
        raise ValueError(f'glyphs missing from Unbounded-{weight}: {bad!r} in {s!r}')


@functools.lru_cache(maxsize=1024)
def font(size, weight=800):
    f = skia.Font(typeface(weight), float(size))
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    f.setHinting(skia.FontHinting.kNone)
    f.setLinearMetrics(True)
    return f


def size_for(cap_px):
    return cap_px / CAP


@functools.lru_cache(maxsize=8192)
def layout(s, size, weight=800, tracking=0.02):
    """Glyph ids and x positions with kerning + tracking (fraction of em). Returns (glyphs, xs, width)."""
    check(s, weight)
    f = font(size, weight)
    _, kern = _tables(weight)
    glyphs = f.textToGlyphs(s)
    widths = f.getWidths(glyphs)
    xs, x = [], 0.0
    for i, ch in enumerate(s):
        xs.append(x)
        x += widths[i]
        if i + 1 < len(s):
            x += kern.get(ch + s[i + 1], 0) * size / 1000.0
            if ch != ' ' and s[i + 1] != ' ':
                x += tracking * size
    return tuple(glyphs), tuple(xs), x


def width(s, cap, weight=800, tracking=0.02):
    return layout(s, size_for(cap), weight, tracking)[2]


def blob(s, x, y, size, weight=800, tracking=0.02):
    glyphs, xs, w = layout(s, size, weight, tracking)
    b = skia.TextBlobBuilder()
    b.allocRunPosH(font(size, weight), list(glyphs), [x + v for v in xs], y)
    return b.make(), w


def fill_paint(style, y_top, y_base, alpha=255):
    """style: hex colour, or a named gradient."""
    p = skia.Paint(AntiAlias=True)
    grads = {
        'red': ('#F0544E', '#E0403A', '#B9302B'),       # reference callout red #D8423C-#EB484B
        'hotred': ('#FF2A2F', '#EB050C', '#B80309'),    # kinetic-title red #EB050C
        'silver': ('#FFFFFF', '#F4F4F4', '#BDBDBD'),    # title-card silver-white
        'white': ('#FFFFFF', '#F7F7F7', '#E6E6E6'),
        'gold': ('#FFE9A6', '#F2C94C', '#B8860B'),
    }
    if style in grads:
        c0, c1, c2 = grads[style]
        p.setShader(skia.GradientShader.MakeLinear(points=[(0, y_top), (0, y_base)], colors=[rgb(c0), rgb(c1), rgb(c2)],
                                                   positions=[0.0, 0.5, 1.0]))
        p.setAlphaf(alpha / 255.0)
    else:
        p.setColor(rgb(style, alpha))
    return p


TEXT_LOG = None          # list -> every visible draw is recorded as (text, cap_px_on_canvas, alpha) for QA


def draw(c, s, x, y, cap, style='white', weight=800, tracking=0.02, align='left', alpha=255,
         shadow=0.9, stroke=None, stroke_color='#000000', glow=None):
    """Draw one line of caps; (x, y) = anchor at the BASELINE. Returns the drawn width.
    shadow: opacity of a soft drop shadow (0 = none). stroke: outline width in px (drawn under the fill)."""
    if alpha <= 0 or not s:
        return 0.0
    if TEXT_LOG is not None:
        m = c.getTotalMatrix()
        TEXT_LOG.append((s, cap * abs(m.getScaleY()), alpha))
    size = size_for(cap)
    _, _, w = layout(s, size, weight, tracking)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    tb, _ = blob(s, x, y, size, weight, tracking)
    a = alpha / 255.0
    if glow:
        gc, gr, ga = glow
        gp = skia.Paint(AntiAlias=True, Color=rgb(gc))
        gp.setAlphaf(ga * a)
        gp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, gr))
        c.drawTextBlob(tb, 0, 0, gp)
    if shadow:
        sp = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
        sp.setAlphaf(min(1.0, shadow * a))
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1.5, cap * 0.075)))
        c.drawTextBlob(tb, cap * 0.03, cap * 0.07, sp)
    if stroke:
        op = skia.Paint(AntiAlias=True, Color=rgb(stroke_color))
        op.setAlphaf(a)
        op.setStyle(skia.Paint.kStroke_Style)
        op.setStrokeWidth(stroke)
        op.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawTextBlob(tb, 0, 0, op)
    c.drawTextBlob(tb, 0, 0, fill_paint(style, y - cap, y, alpha))
    return w


def wrap(text, cap, max_w, weight=800, tracking=0.02, max_lines=3):
    """Greedy word wrap into at most max_lines lines; returns (lines, cap) shrinking cap if needed."""
    words = text.split()
    while True:
        lines, cur = [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if cur and width(t, cap, weight, tracking) > max_w:
                lines.append(cur)
                cur = wd
            else:
                cur = t
        lines.append(cur)
        if len(lines) <= max_lines and all(width(ln, cap, weight, tracking) <= max_w for ln in lines):
            return lines, cap
        cap *= 0.95


def balance(text, cap, max_w, weight=800, tracking=0.02, max_lines=2):
    """Split into up to max_lines lines with the most even widths (premium layouts avoid one-word widows)."""
    words = text.split()
    if len(words) == 1 or width(text, cap, weight, tracking) <= max_w:
        if width(text, cap, weight, tracking) <= max_w:
            return [text], cap
    best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        m = max(width(a, cap, weight, tracking), width(b, cap, weight, tracking))
        if best is None or m < best[0]:
            best = (m, [a, b])
    m, lines = best
    if m > max_w:
        cap *= max_w / m
    return lines, cap
