"""Shot renderers for long-form videos in the format (photos, maps, scenes, cards, ships, titles).

Every renderer has the signature render(canvas, beat, f) where f is the global frame and
beat carries f0/f1 plus resolved trigger frames (beat['ev'][name] = frame).
"""
import functools
import json
import math
import os
import re

import numpy as np
import skia

from .core import W, H, FPS, ASSETS, paint, rgb, ease_out_cubic, ease_out_back, draw_background, blur_dim_image
from .roundhead import draw_character, R_PIP, DETECTIVE
from .text import draw_text, draw_callout, draw_label, draw_speech, text_width, size_for_cap, font
from .props import draw_prop
from .mapdraw import parse_d3_path, draw_dot, dot_pulse_visible
from .cards import draw_title_card

IMG_DIR = None          # set by the project build (folder with <key>.jpg)
HOST_PAL = DETECTIVE


# ---------------- images ----------------
@functools.lru_cache(maxsize=64)
def load_img(key):
    import cv2
    p = os.path.join(IMG_DIR, key + '.jpg')
    a = cv2.imread(p)
    if a is None:
        return None
    a = cv2.cvtColor(a, cv2.COLOR_BGR2RGBA)
    return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)


@functools.lru_cache(maxsize=32)
def blur_bg(key):
    img = load_img(key)
    s = skia.Surface(W, H)
    c = s.getCanvas()
    _cover(c, img, 1.15)
    return blur_dim_image(s.makeImageSnapshot(), sigma=22, gain=0.40, scale=1.0)


def _cover(c, img, scale=1.0, cx=0.5, cy=0.5):
    iw, ih = img.width(), img.height()
    k = max(W / iw, H / ih) * scale
    w, h = iw * k, ih * k
    x = W / 2 - w * cx * 2 + w / 2 - w / 2 * 0 - (w - W) * 0 if False else W / 2 - w / 2
    y = H / 2 - h / 2
    c.drawImageRect(img, skia.Rect(x, y, x + w, y + h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))


def _framed(c, img, cx, cy, max_h, max_w, scale=1.0, rot=0.0, alpha=255, border=True):
    iw, ih = img.width(), img.height()
    k = min(max_h / ih, max_w / iw) * scale
    w, h = iw * k, ih * k
    c.save()
    c.translate(cx, cy)
    if rot:
        c.rotate(rot)
    r = skia.Rect(-w / 2, -h / 2, w / 2, h / 2)
    sp = paint('#000000', alpha=int(170 * alpha / 255))
    sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16))
    c.drawRect(r.makeOffset(8, 12), sp)
    p = skia.Paint(AntiAlias=True)
    p.setAlpha(int(alpha))
    c.drawImageRect(img, r, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    if border:
        c.drawRect(r, paint('#F4F1EA', stroke=5, alpha=alpha))
        c.drawRect(r.makeInset(-2.5, -2.5), paint('#111111', stroke=2, alpha=alpha))
    c.restore()
    return w, h


def pop(f, f0, n=3, frm=1.12):
    return frm - (frm - 1.0) * ease_out_cubic((f - f0) / float(n))


def appear(f, f0, n=4):
    """0..1 pop-in factor for an element that appears at frame f0."""
    if f0 is None or f < f0:
        return 0.0
    return ease_out_back(min(1.0, (f - f0 + 1) / float(n)), 2.2)


def ev(beat, key, default=None):
    return beat.get('ev', {}).get(key, default)


# ---------------- pip host ----------------
def pip_host(c, f, beat, x=300, y=905, R=R_PIP * 0.95):
    exprs = ['talk', 'talk2', 'shock', 'talk', 'smug']
    e = exprs[((f - beat['f0']) // 34) % len(exprs)]
    draw_character(c, x, y, R, 'idle', e, HOST_PAL, look=(0.28, -0.05))


# ---------------- photo ----------------
def render_photo(c, b, f):
    img = load_img(b['img'])
    if img is None:
        draw_background(c); return
    tl = (f - b['f0']) / FPS
    zoom = b.get('zoom', 'in')
    drift = (1 + 0.006 * tl) if zoom == 'in' else (1.03 - 0.006 * tl)
    s = pop(f, b['f0']) * drift
    if b.get('mode') == 'full':
        c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
        _cover(c, img)
        c.restore()
    else:
        c.drawImage(blur_bg(b['img']), 0, 0)
        _framed(c, img, W / 2, H / 2 - (30 if b.get('pip') else 0), H * 0.72, W * 0.80, scale=s)
    if b.get('caption'):
        draw_label(c, b['caption'], W / 2, H - 70, 34, align='center')
    if b.get('bodycam'):
        c.drawRect(skia.Rect(40, 40, W - 40, H - 40), paint('#FFFFFF', stroke=3, alpha=180))
        if (f // 15) % 2 == 0:
            c.drawCircle(110, 110, 18, paint('#E0393E'))
        _txt(c, 'REC', 145, 124, 34, color='#FFFFFF')
        _txt(c, '1066-09-25  14:03:%02d' % ((f // 30) % 60), W - 90, 124, 30, color='#FFFFFF', align='right')
        _txt(c, 'BODYCAM · UNIT 03', W - 90, H - 80, 26, color='#FFFFFF', align='right')
    if b.get('pip'):
        pip_host(c, f, b)


def render_collage(c, b, f):
    keys = b['imgs']
    c.drawImage(blur_bg(keys[0]), 0, 0)
    tl = (f - b['f0']) / FPS
    for i, k in enumerate(keys):
        img = load_img(k)
        if img is None:
            continue
        fa = ev(b, f'img{i}', b['f0'])
        a = appear(f, fa)
        if a <= 0:
            continue
        x = W * (0.34 if i == 0 else 0.66)
        y = H * (0.45 if i == 0 else 0.55)
        _framed(c, img, x, y, H * 0.55, W * 0.42, scale=(0.6 + 0.4 * a) * (1 + 0.005 * tl), rot=(-5 if i == 0 else 6))


# ---------------- title card with a real portrait ----------------
@functools.lru_cache(maxsize=16)
def portrait(key, w=470, h=610):
    img = load_img(key)
    if img is None:
        return None
    s = skia.Surface(w, h)
    c = s.getCanvas()
    iw, ih = img.width(), img.height()
    k = max(w / iw, h / ih)
    dw, dh = iw * k, ih * k
    c.drawImageRect(img, skia.Rect((w - dw) / 2, (h - dh) * 0.2, (w - dw) / 2 + dw, (h - dh) * 0.2 + dh),
                    skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    return s.makeImageSnapshot()


def render_title(c, b, f):
    draw_background(c)
    img = portrait(b['img'])
    if img is None:
        from .cards import make_portrait
        img = make_portrait(b['pal'])
    draw_title_card(c, b['num'], b['name'], img, f - b['f0'])


# ---------------- maps ----------------
@functools.lru_cache(maxsize=1)
def _regions():
    return json.load(open(os.path.join(ASSETS, 'maps', 'regions.json')))


@functools.lru_cache(maxsize=16)
def region_base(name, highlight=()):
    reg = _regions()[name]
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(rgb('#77CDF5'))
    rng = np.random.default_rng(5)
    for _ in range(70):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        p = skia.Path(); p.moveTo(x, y); p.quadTo(x + 30, y - 10, x + 60, y); p.quadTo(x + 90, y + 10, x + 120, y)
        c.drawPath(p, paint('#5FBDEB', stroke=5, alpha=180))
    paths = [(l['name'], parse_d3_path(l['d'])) for l in reg['land']]
    for nm, p in paths:
        c.drawPath(p, paint('#44763F', stroke=10))
    for nm, p in paths:
        c.drawPath(p, paint('#F2D26B' if nm in highlight else '#95E267'))
        c.drawPath(p, paint('#6FB34E', stroke=2.5, alpha=200))
    return s.makeImageSnapshot()


def render_map(c, b, f):
    reg = _regions()[b['region']]
    tl = (f - b['f0']) / FPS
    s = pop(f, b['f0'], 3, 1.06) * (1 + 0.006 * tl)
    fx, fy = (W / 2, H / 2)
    if b.get('focus'):
        fx, fy = reg['pts'][b['focus']]
    zoom = b.get('zoom', 1.0)
    c.save()
    c.translate(W / 2, H / 2); c.scale(s * zoom, s * zoom); c.translate(-fx, -fy)
    c.drawImage(region_base(b['region'], tuple(b.get('highlight', ()))), 0, 0)
    # route
    stops = b.get('stops', [])
    pts = [reg['pts'][n] for n, _, _ in stops]
    head = None
    for i in range(1, len(stops)):
        fs = ev(b, f'stop{i}')
        if fs is None or f < fs:
            break
        k = min(1.0, (f - fs) / 18.0)
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]
        xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        c.drawLine(x0, y0, xe, ye, paint('#FFFFFF', stroke=14 / zoom))
        p = paint('#E0393E', stroke=8 / zoom)
        p.setPathEffect(skia.DashPathEffect.Make([22 / zoom, 12 / zoom], 0))
        c.drawLine(x0, y0, xe, ye, p)
        head = (xe, ye)
    for i, (n, label, _) in enumerate(stops):
        fs = ev(b, f'stop{i}') if i else ev(b, 'stop0', b['f0'])
        if fs is None or f < fs:
            continue
        x, y = reg['pts'][n]
        draw_dot(c, x, y, r=15 / zoom, visible=dot_pulse_visible(f - fs))
        if label:
            draw_label(c, label, x + 24 / zoom, y - 18 / zoom, 30 / zoom)
    for n, label, trig in b.get('pins', []):
        fs = ev(b, 'pin_' + n, b['f0'])
        if f < fs:
            continue
        x, y = reg['pts'][n]
        draw_dot(c, x, y, r=15 / zoom, visible=dot_pulse_visible(f - fs))
        if label:
            draw_label(c, label, x + 24 / zoom, y - 18 / zoom, 30 / zoom)
    if head and b.get('icon'):
        draw_prop(c, b['icon'], head[0], head[1] - 30 / zoom, 34 / zoom, t=tl)
    for txt, xy in b.get('labels', []):
        draw_label(c, txt, xy[0], xy[1], 40 / zoom, align='center')
    c.restore()


# ---------------- scenes ----------------
def backdrop(c, kind, f=0):
    if kind == 'black' or kind is None:
        draw_background(c); return
    if kind.startswith('img:'):
        img = load_img(kind[4:])
        if img is not None:
            _cover(c, img, 1.0 + 0.004 * f / FPS)
            c.drawRect(skia.Rect(0, 0, W, H), paint('#000000', alpha=60))
            return
        draw_background(c); return
    pal = {
        'field': ('#8FCBF2', '#DDF0FB', '#7FB65A', '#5E9442', 770),
        'sea': ('#8FCBF2', '#DDF0FB', '#3E93CF', '#2A6FA8', 640),
        'night': ('#141B33', '#2B3760', '#25331F', '#1A2416', 790),
        'arena': ('#9AD2F3', '#E2F2FB', '#D9C08A', '#C4A66C', 760),
        'hall': ('#B6A285', '#9C8668', '#7A5434', '#5E3F26', 800),
        'forest': ('#8FCBF2', '#DDF0FB', '#6FA64C', '#4F8236', 780),
    }[kind]
    top, bot, g0, g1, hz = pal
    sh = skia.GradientShader.MakeLinear(points=[(0, 0), (0, hz)], colors=[rgb(top), rgb(bot)])
    c.drawRect(skia.Rect(0, 0, W, hz), paint('#FFFFFF', shader=sh))
    sh2 = skia.GradientShader.MakeLinear(points=[(0, hz), (0, H)], colors=[rgb(g0), rgb(g1)])
    c.drawRect(skia.Rect(0, hz, W, H), paint('#FFFFFF', shader=sh2))
    c.drawLine(0, hz, W, hz, paint('#151515', stroke=5))
    if kind == 'hall':
        for row in range(9):
            y = row * 90
            c.drawLine(0, y, W, y, paint('#8A775C', stroke=3))
            for k in range(12):
                x = k * 180 + (90 if row % 2 else 0)
                c.drawLine(x, y, x, y + 90, paint('#8A775C', stroke=3))
        for k in range(14):
            c.drawLine(k * 150, hz, k * 150 - 60, H, paint('#4A3020', stroke=3))
    elif kind == 'sea':
        rng = np.random.default_rng(3)
        for _ in range(40):
            x, y = rng.uniform(0, W), rng.uniform(hz + 20, H)
            xo = (f * 1.5) % 80
            p = skia.Path(); p.moveTo(x + xo, y); p.quadTo(x + xo + 25, y - 10, x + xo + 50, y)
            c.drawPath(p, paint('#BFE3F7', stroke=4, alpha=170))
    elif kind in ('field', 'forest', 'arena'):
        for i, (x, r) in enumerate([(300, 380), (1100, 520), (1750, 420)]):
            p = skia.Path(); p.addOval(skia.Rect(x - r, hz - r * 0.35, x + r, hz + r * 0.35))
            c.save(); c.clipRect(skia.Rect(0, 0, W, hz)); c.drawPath(p, paint('#A9D88A' if kind != 'arena' else '#B9B2A2')); c.restore()
        c.drawLine(0, hz, W, hz, paint('#151515', stroke=5))
    elif kind == 'night':
        c.drawCircle(1600, 180, 70, paint('#F4F1DC'))
        rng = np.random.default_rng(9)
        for _ in range(60):
            c.drawCircle(rng.uniform(0, W), rng.uniform(0, hz - 50), rng.uniform(1.5, 3.5), paint('#FFFFFF', alpha=200))


def name_tag(c, text, x, y, cap=26):
    size = size_for_cap(cap)
    tw = text_width(text, size, 0.05)
    c.drawRect(skia.Rect(x - tw / 2 - 14, y - cap - 12, x + tw / 2 + 14, y + 10), paint('#111111', alpha=235))
    draw_text(c, text, x - tw / 2, y, size, style='#FFFFFF', tracking=0.05, shadow=False, grunge=False)


def _expr_at(spec, f, beat):
    e = spec.get('expr', 'neutral')
    if isinstance(e, list):
        cur = e[0][1]
        for trig, ex in e:
            fr = beat['ev'].get('x:' + trig, beat['f0']) if trig else beat['f0']
            if f >= fr:
                cur = ex
        return cur
    return e


def render_scene(c, b, f):
    tl = (f - b['f0']) / FPS
    s = pop(f, b['f0'], 3, 1.05) * (1 + 0.004 * tl)
    c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
    backdrop(c, b.get('bg', 'black'), f - b['f0'])
    floor = b.get('floor', 975)
    items = []
    for i, p in enumerate(b.get('props', [])):
        items.append(('p', i, p))
    for i, ch in enumerate(b.get('chars', [])):
        items.append(('c', i, ch))
    items.sort(key=lambda it: it[2].get('z', 0))
    for kind, i, spec in items:
        fa = ev(b, f'{kind}{i}', b['f0'])
        a = appear(f, fa) if spec.get('at') else 1.0
        if a <= 0:
            continue
        fx = ev(b, f'{kind}{i}_exit')
        alpha = 255
        if fx is not None and f >= fx:
            alpha = int(255 * max(0.0, 1 - (f - fx) / 7.0))
            if alpha <= 0:
                continue
        if kind == 'p':
            x, y = spec['x'], spec['y']
            dx, dy = spec.get('move', (0, 0))
            if 'move' in spec:
                k = ease_out_cubic(min(1.0, (f - fa) / float(spec.get('move_frames', 24))))
                x, y = x + dx * k, y + dy * k
            draw_prop(c, spec['name'], x, y, spec.get('size', 100) * (0.4 + 0.6 * a), t=tl, rot=spec.get('rot', 0),
                      alpha=alpha, flip=spec.get('flip', False), **spec.get('kw', {}))
            if spec.get('text'):
                draw_label(c, spec['text'], x + spec.get('tx', 0), y + spec.get('ty', 0), spec.get('tcap', 30), align='center')
        else:
            R = spec.get('R', 115)
            x = spec['x']
            y = spec.get('y', floor - 3.12 * R)
            e = _expr_at(spec, f, b)
            if spec.get('alpha_dim'):
                alpha = min(alpha, 120)
            draw_character(c, x, y, R * (0.5 + 0.5 * a), spec.get('pose', 'idle'), e, spec['pal'],
                           flip=spec.get('flip', False), look=spec.get('look'), alpha=alpha, rot=spec.get('rot', 0.0),
                           phase=tl * 7 if spec.get('pose') == 'walk' else 0.0)
            if not spec.get('tag') and b.get('tag_all') and spec['pal'].get('hat') != 'crown':
                name_tag(c, b['tag_all'], x, y - R * 1.55)
            if spec.get('tag'):
                name_tag(c, spec['tag'], x, y - R * 1.55 - (0.35 * R if spec['pal'].get('hat') in ('admiral', 'roman', 'crown') else 0))
            if spec.get('say'):
                fs = ev(b, f'say{i}', fa)
                if f >= fs:
                    sx = spec.get('say_x', x + R * 0.9)
                    sy = spec.get('say_y', y - R * 1.6)
                    draw_speech(c, spec['say'], sx, sy, cap_px=spec.get('say_cap', 34),
                                tail=((sx + 10, sy + 16), (sx - 18, sy + 50)), rot=-2.5)
    for li, (txt, lx, ly, trig) in enumerate(b.get('labels', [])):
        fl = ev(b, f'label{li}', b['f0'])
        if f >= fl:
            k = appear(f, fl)
            draw_label(c, txt, lx, ly, 34 * max(0.3, k), align='center')
    if b.get('drum'):
        beat_f = (f - b['f0']) % 12
        if beat_f < 3:
            draw_prop(c, 'icon', 1320, 520, 30, kind='bang')
    if b.get('boss'):
        k = min(1.0, (f - b['f0']) / 12.0)
        c.drawRect(skia.Rect(360, 110, 1560, 150), paint('#2A0B0B'))
        c.drawRect(skia.Rect(360, 110, 360 + 1200 * k, 150), paint('#C0392B'))
        c.drawRect(skia.Rect(360, 110, 1560, 150), paint('#F2C94C', stroke=4))
        _txt(c, b['boss'], W / 2, 92, 34, color='#FFFFFF', align='center')
        if b.get('boss_sub'):
            _txt(c, b['boss_sub'], W / 2, 196, 24, color='#F2C94C', align='center')
    if b.get('censor'):
        x, y, w, h = b['censor']
        c.drawRect(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), paint('#111111'))
        draw_text(c, 'CENSORED', x - text_width('CENSORED', 30, 0.05) / 2, y + 10, 30, style='#FFFFFF', shadow=False, grunge=False)
    c.restore()
    if b.get('pip'):
        pip_host(c, f, b)


# ---------------- cards ----------------
def _panel(c, x0, y0, x1, y1, fill='#1E1F24', r=26, edge='#3A3C44'):
    rr = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r)
    sp = paint('#000000', alpha=170)
    sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 8, y0 + 14, x1 + 8, y1 + 14), r, r), sp)
    c.drawRRect(rr, paint(fill))
    c.drawRRect(rr, paint(edge, stroke=3))


def _txt(c, s, x, y, cap, color='#FFFFFF', align='left', style=None, font_name='archivo', tracking=0.03):
    if font_name == 'nunito':
        from .text import speech_typeface
        size = cap / 0.705
        fnt = skia.Font(speech_typeface(), size)
        tw = fnt.measureText(s)
        if align == 'center':
            x -= tw / 2
        elif align == 'right':
            x -= tw
        c.drawString(s, x, y, fnt, paint(color))
        return tw
    size = size_for_cap(cap)
    tw = text_width(s, size, tracking)
    if align == 'center':
        x -= tw / 2
    elif align == 'right':
        x -= tw
    draw_text(c, s, x, y, size, style=style or color, tracking=tracking, shadow=False, grunge=False)
    return tw


def _wrap(s, maxw, cap, font_name='nunito'):
    from .text import speech_typeface
    size = cap / 0.705
    fnt = skia.Font(speech_typeface(), size)
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if fnt.measureText(t) > maxw and cur:
            out.append(cur); cur = w
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def render_card(c, b, f):
    draw_background(c)
    tl = (f - b['f0']) / FPS
    s = pop(f, b['f0'], 3, 1.08) * (1 + 0.004 * tl)
    c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
    t = b['type']
    if t in ('list', 'playlist'):
        items = b['items']
        n = len(items)
        rowh = min(165 if t == 'playlist' else 118, 760 / max(1, n))
        top = H / 2 - (n * rowh + 120) / 2
        _panel(c, 200, top, W - 200, top + n * rowh + 140)
        _txt(c, b['title'], 260, top + 80, 44, color=b.get('title_color', '#F2C94C'))
        for i, it in enumerate(items):
            fa = ev(b, f'item{i}', b['f0'])
            a = appear(f, fa)
            if a <= 0:
                continue
            y = top + 110 + i * rowh
            c.save(); c.translate(280, y + rowh / 2); c.scale(a, a); c.translate(-280, -(y + rowh / 2))
            label, img = it.get('text'), it.get('img')
            x = 280
            if t == 'playlist' and img and load_img(img) is not None:
                th = rowh - 22
                tw_ = th * 16 / 9
                pi = load_img(img)
                k = max(tw_ / pi.width(), th / pi.height())
                c.save(); c.clipRect(skia.Rect(x, y + 6, x + tw_, y + 6 + th))
                c.drawImageRect(pi, skia.Rect(x + tw_ / 2 - pi.width() * k / 2, y + 6 + th / 2 - pi.height() * k / 2,
                                              x + tw_ / 2 + pi.width() * k / 2, y + 6 + th / 2 + pi.height() * k / 2),
                                skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
                c.restore()
                c.drawRect(skia.Rect(x, y + 6, x + tw_, y + 6 + th), paint('#000000', stroke=2))
                x += tw_ + 30
                _txt(c, label, x, y + rowh * 0.45, 42, color='#FFFFFF', font_name='nunito')
                _txt(c, it.get('meta', ''), x, y + rowh * 0.45 + 52, 26, color='#9A9CA3', font_name='nunito')
            else:
                mark = it.get('mark', b.get('mark'))
                if mark:
                    draw_prop(c, 'icon', x + 30, y + rowh / 2, 28, kind=mark)
                    x += 84
                col = it.get('color', b.get('item_color', '#FFFFFF'))
                _txt(c, label, x, y + rowh / 2 + 18, max(46, b.get('cap', 34) + 14), color=col, font_name='nunito')
                if it.get('strike'):
                    fs = ev(b, f'strike{i}')
                    if fs is not None and f >= fs:
                        tw_ = text_width(label, size_for_cap(b.get('cap', 34)), 0.0) * 0.8
                        c.drawLine(x - 10, y + rowh / 2, x + tw_ + 10, y + rowh / 2, paint('#E0393E', stroke=9))
            c.restore()
        if b.get('overlay_icon'):
            fo = ev(b, 'overlay', None)
            if fo is not None and f >= fo:
                draw_prop(c, 'icon', W - 380, H / 2, 170 * appear(f, fo), kind=b['overlay_icon'])
    elif t == 'quote':
        lines = _wrap(b['text'], 1280, 70)
        n = len(lines)
        y0 = H / 2 - (n * 100) / 2 + 40
        _txt(c, '“', 250, y0 - 40, 200, color='#E0393E', font_name='nunito')
        widx = 0
        words_ev = b.get('word_frames', [])
        for li, ln in enumerate(lines):
            x = 330
            for w in ln.split():
                lit = widx < len(words_ev) and f >= words_ev[widx] or not words_ev
                col = '#FFFFFF' if lit else '#4A4A4A'
                tw_ = _txt(c, w, x, y0 + li * 100, 70, color=col, font_name='nunito')
                x += tw_ + 26
                widx += 1
        if b.get('who'):
            _txt(c, '— ' + b['who'], 340, y0 + n * 100 + 40, 34, color='#F2C94C')
    elif t == 'dict':
        _panel(c, 360, 250, W - 360, 830, fill='#F4EFE4', edge='#C9BFA8')
        _txt(c, b['word'], 430, 400, 84, color='#1A1A1A', font_name='nunito')
        _txt(c, b.get('pos', ''), 430, 470, 32, color='#7A7365', font_name='nunito')
        for i, d in enumerate(b.get('defs', [])):
            fa = ev(b, f'item{i}', b['f0'])
            if f >= fa:
                _txt(c, d, 450, 570 + i * 80, 44, color='#2B2B2B', font_name='nunito')
    elif t == 'bio':
        _panel(c, 460, 220, W - 460, 860, fill='#FFFFFF', edge='#DADCE0')
        c.drawRect(skia.Rect(460, 220, W - 460, 380), paint('#3E6BB5'))
        c.drawCircle(620, 400, 92, paint('#FFFFFF'))
        c.save(); pth = skia.Path(); pth.addCircle(620, 400, 84); c.clipPath(pth, skia.ClipOp.kIntersect, True)
        c.drawCircle(620, 400, 84, paint('#D9E6F2'))
        draw_character(c, 620, 430, 62, 'idle', 'deadpan', b['pal'], show_rim=False)
        c.restore()
        _txt(c, b['name'], 740, 470, 40, color='#111111', font_name='nunito')
        _txt(c, b.get('handle', ''), 740, 520, 26, color='#6B6F76', font_name='nunito')
        for i, ln in enumerate(b.get('lines', [])):
            ln = ln['text'] if isinstance(ln, dict) else ln
            fa = ev(b, f'item{i}', b['f0'])
            if f >= fa:
                _txt(c, ln, 540, 660 + i * 62, 34, color='#E0393E' if i == len(b['lines']) - 1 else '#222222', font_name='nunito')
    elif t == 'sub':
        _panel(c, 520, 170, W - 520, 910, fill='#141821', edge='#2E3445')
        _txt(c, b['title'], W / 2, 290, 56, color='#F2C94C', align='center')
        _txt(c, b['price'], W / 2, 400, 40, color='#FFFFFF', align='center', font_name='nunito')
        for i, ln in enumerate(b.get('lines', [])):
            draw_prop(c, 'icon', 650, 490 + i * 70, 16, kind='check')
            _txt(c, ln, 690, 502 + i * 70, 30, color='#D6D9E0', font_name='nunito')
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(700, 760, W - 700, 840), 40, 40), paint('#E0393E'))
        _txt(c, b.get('button', 'SUBSCRIBE'), W / 2, 813, 30, color='#FFFFFF', align='center')
        if b.get('note'):
            _txt(c, b['note'], W / 2, 885, 20, color='#7A7F8C', align='center', font_name='nunito')
    elif t == 'inventory':
        _panel(c, 330, 200, W - 330, 880, fill='#2A2219', edge='#8A6A3A')
        _txt(c, b['title'], 390, 280, 34, color='#F2C94C')
        for i, it in enumerate(b['items']):
            name, rarity = (it['name'], it.get('rarity', '')) if isinstance(it, dict) else it
            fa = ev(b, f'item{i}', b['f0'])
            if f < fa:
                continue
            y = 360 + i * 120
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(390, y, W - 390, y + 96), 12, 12), paint('#3A2F23'))
            col = {'COMMON': '#B8B8B8', 'LEGENDARY': '#F2A93C', 'CURSED': '#B05FE0'}.get(rarity, '#E0393E')
            _txt(c, name, 430, y + 62, 36, color='#FFFFFF', font_name='nunito')
            _txt(c, rarity, W - 430, y + 62, 24, color=col, align='right')
            if b.get('strike') == i:
                fs = ev(b, 'strike')
                if fs is not None and f >= fs:
                    c.drawLine(410, y + 48, W - 410, y + 48, paint('#E0393E', stroke=10))
    elif t == 'album':
        c.drawRect(skia.Rect(560, 140, 1360, 940), paint('#0B0B0B'))
        c.drawRect(skia.Rect(560, 140, 1360, 940), paint('#3A3A3A', stroke=6))
        draw_prop(c, 'icon', W / 2, 520, 180, kind='skull')
        draw_prop(c, 'coffin', 760, 600, 90, c='#E8B83A')
        draw_prop(c, 'coffin', 1160, 600, 90, c='#C9CED3')
        _txt(c, b.get('band', 'ATTILA'), W / 2, 290, 96, color='#B3001B', align='center')
        _txt(c, b.get('title', ''), W / 2, 850, 46, color='#E8E8E8', align='center')
        c.drawRect(skia.Rect(1170, 870, 1340, 925), paint('#FFFFFF'))
        _txt(c, 'EPIC HISTORY', 1255, 907, 14, color='#000000', align='center')
    elif t == 'comment':
        _panel(c, 360, 380, W - 360, 700, fill='#FFFFFF', edge='#DADCE0')
        c.drawCircle(470, 470, 52, paint('#7E57C2'))
        _txt(c, 'V', 470, 488, 40, color='#FFFFFF', align='center')
        _txt(c, '@history_viewer  ·  just now', 560, 455, 26, color='#606060', font_name='nunito')
        n = len(b['text'])
        k = int(min(n, max(0, (f - b['f0']) / 2)))
        _txt(c, b['text'][:k] + ('|' if (f // 8) % 2 else ''), 560, 540, 52, color='#111111', font_name='nunito')
        draw_prop(c, 'icon', 590, 640, 22, kind='heart')
        _txt(c, '25K', 630, 652, 26, color='#606060', font_name='nunito')
    elif t == 'likes':
        target = b['target']
        k = min(1.0, (f - b['f0']) / 45.0)
        val = int(target * ease_out_cubic(k))
        draw_prop(c, 'icon', W / 2 - 330, H / 2, 120, kind='heart')
        _txt(c, f'{val:,}', W / 2 - 150, H / 2 + 60, 150, color='#FFFFFF')
        _txt(c, 'LIKES = PART TWO', W / 2, H / 2 + 230, 44, color='#F2C94C', align='center')
    elif t == 'versus':
        for i, (txt, col) in enumerate([(b['left'], '#3E6BB5'), (b['right'], '#B23A32')]):
            x0 = 160 + i * 820
            fa = ev(b, f'item{i}', b['f0'])
            if f < fa:
                continue
            _panel(c, x0, 300, x0 + 780, 780, fill=col, edge='#151515')
            for li, ln in enumerate(_wrap(txt, 680, 64)):
                _txt(c, ln, x0 + 390, 520 + li * 90, 64, color='#FFFFFF', align='center', font_name='nunito')
        _txt(c, 'VS', W / 2, 580, 90, color='#F2C94C', align='center')
    elif t == 'calendar':
        _panel(c, 660, 200, 1260, 880, fill='#FFFFFF', edge='#C8C8C8')
        c.drawRect(skia.Rect(660, 200, 1260, 360), paint('#E0393E'))
        _txt(c, b.get('month', 'WEDDING DAY'), 960, 300, 44, color='#FFFFFF', align='center')
        _txt(c, b['text'], 960, 600, 90, color='#111111', align='center', font_name='nunito')
        _txt(c, b.get('sub', ''), 960, 760, 34, color='#7A7A7A', align='center', font_name='nunito')
    elif t == 'split':
        k = ease_out_cubic(min(1.0, (f - b['f0']) / 20.0))
        for i, (txt, col) in enumerate([('PART 1', '#3E6BB5'), ('PART 2', '#B23A32')]):
            dx = (-1 if i == 0 else 1) * 60 * k
            x0 = 360 + i * 600 + dx
            _panel(c, x0, 320, x0 + 600, 760, fill=col, edge='#151515', r=10)
            _txt(c, txt, x0 + 300, 580, 80, color='#FFFFFF', align='center')
    elif t == 'ammo':
        draw_prop(c, 'arrow', 520, H / 2 - 10, 150)
        _txt(c, 'ARROWS:', 760, H / 2 + 36, 70, color='#FFFFFF')
        _txt(c, '∞', 1560, H / 2 + 75, 170, color='#F2C94C', font_name='nunito')
        _txt(c, 'CAMEL RESUPPLY: ON', W / 2, H / 2 + 220, 40, color='#7FD16A', align='center')
    elif t == 'text':
        for li, ln in enumerate(b['lines']):
            _txt(c, ln, W / 2, H / 2 + (li - (len(b['lines']) - 1) / 2) * 130 + 40, b.get('cap', 90),
                 color=b.get('color', '#FFFFFF'), align='center', style=b.get('style'))
    elif t == 'formation':
        backdrop(c, 'sea', f - b['f0'])
        k = ease_out_cubic(min(1.0, (f - b['f0']) / 40.0))
        for i in range(9):
            a = math.pi * (0.15 + 0.7 * i / 8)
            x = W / 2 + math.cos(a) * 560 * (1.4 - 0.4 * k)
            y = 760 - math.sin(a) * 420 * (0.6 + 0.4 * k)
            draw_prop(c, 'turtle_ship', x, y, 55, t=tl)
        for i in range(5):
            draw_prop(c, 'jp_ship', W / 2 - 200 + i * 100, 640 + (i % 2) * 50, 45, t=tl)
        _txt(c, 'CRANE WING FORMATION', W / 2, 150, 60, color='#FFFFFF', align='center')
    c.restore()


def render_ships(c, b, f):
    backdrop(c, b.get('bg', 'sea'), f - b['f0'])
    n0, n1 = b['n'], b.get('n2', b['n'])
    fc = ev(b, 'change')
    if n0 <= 15:
        cols, size = min(n0, 5), 78
    elif n0 <= 60:
        cols, size = 12, 58
    else:
        cols, size = 20, 36
    rows = math.ceil(n0 / cols)
    gx, gy = (size * 3.4, size * 1.7) if n0 <= 15 else (size * 2.25, size * 1.5)
    x0 = W / 2 - (min(cols, n0) - 1) * gx / 2
    y0 = max(560, 690 - (rows - 1) * gy / 2)
    tl = (f - b['f0']) / FPS
    for i in range(n0):
        r, col = divmod(i, cols)
        x, y = x0 + col * gx + (gx / 4 if r % 2 else 0), y0 + r * gy
        a = 255
        if fc is not None and f >= fc and i >= n1:
            a = int(255 * max(0.0, 1 - (f - fc) / 10.0))
            if a <= 0:
                continue
        bob = math.sin(tl * 3 + i * 0.7) * size * 0.06
        draw_prop(c, b.get('ship', 'longship'), x, y + bob, size, t=tl, alpha=a, rim=False)
    lab = b.get('label')
    if lab:
        txt = lab[1] if (fc is not None and f >= fc and len(lab) > 1) else lab[0]
        draw_callout(c, txt, progress=1.0, style='red')


def render_kinetic(c, b, f):
    draw_background(c)
    b['kin'].draw(c, f, b['f0'], b['f1'])
    draw_character(c, 330, 905, 80, 'idle', ['talk', 'talk2', 'smile'][((f - b['f0']) // 25) % 3], HOST_PAL)


def render_end(c, b, f):
    draw_background(c)
    fx = ev(b, 'logo', b['f1'] - 150)
    if not b.get('channel'):
        draw_character(c, 420, 380, 140, 'point', ['smile', 'talk', 'grin'][((f - b['f0']) // 30) % 3], HOST_PAL)
        if f >= fx:     # SUBSCRIBE drops in with the outro sting
            k = ease_out_back(min(1.0, (f - fx) / 9.0), 2.2)
            c.save(); c.translate(420, 945); c.scale(max(0.01, k), max(0.01, k)); c.translate(-420, -945)
            bw = text_width('SUBSCRIBE', size_for_cap(34), 0.03) / 2 + 44
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(420 - bw, 900, 420 + bw, 990), 20, 20), paint('#E0393E'))
            _txt(c, 'SUBSCRIBE', 420, 962, 34, color='#FFFFFF', align='center')
            c.restore()
    elif f < fx:
        draw_character(c, 420, 400, 150, 'point', ['smile', 'talk', 'grin'][((f - b['f0']) // 30) % 3], HOST_PAL)
    else:
        k = ease_out_back(min(1.0, (f - fx) / 10.0), 2.0)
        _txt(c, b.get('channel', 'YOUR CHANNEL'), 420, 330 - (1 - k) * 300, 64, color='#FFFFFF', align='center', font_name='nunito')
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(250, 420 - (1 - k) * 300, 590, 510 - (1 - k) * 300), 20, 20), paint('#E0393E'))
        _txt(c, 'SUBSCRIBE', 420, 482 - (1 - k) * 300, 34, color='#FFFFFF', align='center')
    rr = skia.RRect.MakeRectXY(skia.Rect(900, 300, 1650, 720), 24, 24)
    c.drawRRect(rr, paint('#FFFFFF'))
    lw = text_width('WATCH THIS NEXT', size_for_cap(26), 0.03) / 2 + 34
    c.drawRect(skia.Rect(1275 - lw, 262, 1275 + lw, 330), paint('#E0393E'))
    _txt(c, 'WATCH THIS NEXT', 1275, 309, 26, color='#FFFFFF', align='center')
    p = skia.Path(); p.moveTo(1690, 330); p.quadTo(1830, 520, 1680, 700)
    c.drawPath(p, paint('#E0393E', stroke=34))
    p2 = skia.Path(); p2.moveTo(1640, 660); p2.lineTo(1700, 740); p2.lineTo(1740, 650); p2.close()
    c.drawPath(p2, paint('#E0393E'))


RENDERERS = dict(photo=render_photo, collage=render_collage, title=render_title, map=render_map, scene=render_scene,
                 card=render_card, ships=render_ships, kinetic=render_kinetic, end=render_end)
