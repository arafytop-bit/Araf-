"""v3 shot renderers. Every renderer: fn(c, b, f, ctx) where b is the compiled beat (all triggers already frames)
and ctx collects occupied rects (faces, frames) for the overlay layout engine."""
import functools
import math
import os
import sys

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(HERE))

from engine.core import W, H, rgb  # noqa: E402
from engine import roundhead as RH  # noqa: E402
from engine.premium import look as L, motion as M, typo as TY, overlays as O  # noqa: E402
from engine.premium.actors import draw_actor, draw_prop, at_time, blinked  # noqa: E402
from engine.props import draw_prop as raw_prop  # noqa: E402
from cast import HOST  # noqa: E402

L.IMG_DIR = os.path.join(os.path.dirname(HERE), 'assets', 'picked')
FPS = 30
SHOTS = {}


def shot(kind):
    def deco(fn):
        SHOTS[kind] = fn
        return fn
    return deco


def secs(b, f):
    return (f - b['f0']) / FPS


# ======================= backgrounds =======================
def bg_photo_full(c, key, b, f, focus=(0.5, 0.5), zoom=1.0, blur=0.0, gain=1.0, rate=0.006, direction=1, vignette=0.55,
                  sat=0.88, contrast=1.08):
    img = L.plate(key, W, H, tuple(focus), zoom, sat=sat, contrast=contrast, gain=gain, blur=blur)
    t = secs(b, f)
    s = M.push(t, rate, direction, start=1.0 if direction >= 0 else 1.0 + rate * (b['f1'] - b['f0']) / FPS)
    L.draw_scaled(c, img, W / 2, H / 2, s / 1.06 * 1.06, w=W, h=H)
    if vignette:
        c.drawImage(L.vignette_overlay(vignette), 0, 0)


def bg_blur(c, key, b, f, gain=0.36, rate=0.003, focus=(0.5, 0.5)):
    img = L.blur_fill(key, gain=gain, focus=tuple(focus))
    s = 1.0 + rate * secs(b, f)
    L.draw_scaled(c, img, W / 2, H / 2, s, w=W * 1.08, h=H * 1.08)


# ======================= host =======================
FRAMING = {
    'M': (960, 410, 176), 'CU': (960, 488, 292), 'ECU': (960, 590, 430), 'LOW': (960, 668, 160),
    'L': (600, 440, 166), 'R': (1320, 440, 166), 'MS': (960, 520, 236),
}


def host_head_rect(fr):
    cx, cy, R = FRAMING[fr]
    return skia.Rect(cx - 1.35 * R, cy - 1.75 * R, cx + 1.35 * R, cy + 1.1 * R)


def draw_host(c, h, f, framing=None, push=True):
    fr = framing or h.get('framing', 'M')
    cx, cy, R = FRAMING[fr]
    if h.get('dx'):
        cx += h['dx']
    e = at_time(h['exprs'], f, 'talk')
    e = blinked(e, f, seed=h['f0'] % 17)
    pose = h.get('pose', 'idle')
    # secondary motion: breathing + a 4-frame settle on every expression swap
    sy = M.breathe(f, period_s=3.4, amp=0.005, seed=h['f0'] % 7)
    last_swap = max([f0 for f0, _ in h['exprs'] if f0 <= f] or [h['f0']])
    d = f - last_swap
    if 0 <= d < 5 and last_swap != h['f0']:
        q = math.sin(math.pi * (d + 1) / 5)
        sy *= 1 - 0.018 * q
    sc = 1.0
    if push:
        sc = 1.0 + 0.0025 * (f - h['f0']) / FPS
    feet = cy + 3.2 * R
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(sc, sc)
    c.translate(-W / 2, -H / 2)
    c.translate(cx, feet)
    c.scale(1 / math.sqrt(sy), sy)
    c.translate(-cx, -feet)
    RH.draw_character(c, cx, cy, R, pose, e, HOST, bob=h.get('bob', (0.0, 0.0)), look=h.get('look', (0.0, 0.0)),
                      show_rim=True)
    c.restore()
    return host_head_rect(fr)


@shot('host')
def host(c, b, f, ctx):
    over = b.get('over')
    if over and L.exists(over):
        bg_blur(c, over, b, f, gain=0.30)
    else:
        L.stage(c)
    if b.get('pip') and L.exists(b['pip']):
        pip_panel(c, b['pip'], b, f, side=b.get('pip_side', 'R'))
    ctx['occ'].append(('face', draw_host(c, b, f)))


def pip_panel(c, key, b, f, side='R'):
    """Picture-in-picture panel next to the host (reference 3.8 %): rounded frame, soft shadow, slow push."""
    pw, ph = 0.42 * W, 0.42 * W * 0.68
    cx = 0.73 * W if side == 'R' else 0.27 * W
    cy = 0.46 * H
    df = f - b.get('pip_at', b['f0'])
    s, a = M.pop(df, 0.85, frames=5)
    if a <= 0:
        return
    rect = skia.Rect(cx - pw / 2 * s, cy - ph / 2 * s, cx + pw / 2 * s, cy + ph / 2 * s)
    L.soft_shadow(c, rect, 22, (0, 16), 0.8, 18)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(rect, 18 * s, 18 * s), True)
    img = L.plate(key, int(pw), int(ph), tuple(b.get('pip_focus', (0.5, 0.5))), b.get('pip_zoom', 1.0))
    L.draw_scaled(c, img, cx, cy, (1 + 0.006 * secs(b, f)) * s, w=pw, h=ph)
    c.restore()


# ======================= photos =======================
def frame_box(key, b, maxw=0.66 * W, maxh=0.70 * H, cy=0.52 * H, cx=W / 2):
    im = L.raw(key)
    ih, iw = im.shape[:2]
    crop_aspect = b.get('aspect') or (iw / ih)
    if b.get('zoom', 1.0) != 1.0 and not b.get('aspect'):
        crop_aspect = iw / ih
    if b.get('lowered'):
        cy, maxh = 0.615 * H, 0.60 * H
    w = min(maxw, maxh * crop_aspect)
    h = w / crop_aspect
    return skia.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), crop_aspect


@shot('photo')
def photo(c, b, f, ctx):
    key = b['img']
    mode = b.get('mode', 'frame')
    focus = tuple(b.get('focus', (0.5, 0.5)))
    if mode == 'full':
        bg_photo_full(c, key, b, f, focus, b.get('zoom', 1.0), rate=0.006, direction=b.get('push', 1),
                      vignette=b.get('vignette', 0.5))
        ctx['photo'] = True
        rect = skia.Rect(0, 0, W, H)
    else:
        bg_blur(c, key, b, f, gain=0.34, focus=focus)
        rect, aspect = frame_box(key, b, cx=b.get('cx', W / 2))
        s = M.push(secs(b, f), 0.006, b.get('push', 1), start=1.0 if b.get('push', 1) >= 0 else 1.0 + 0.006 * (b['f1'] - b['f0']) / FPS)
        cx, cy = rect.centerX(), rect.centerY()
        w, h = rect.width() * s, rect.height() * s
        r2 = skia.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        L.soft_shadow(c, r2, 26, (0, 18), 0.85, 4)
        if mode == 'doc':
            pad = 10
            wp = skia.Paint(AntiAlias=True, Color=rgb('#F4F1EA'))
            c.drawRect(skia.Rect(r2.left() - pad, r2.top() - pad, r2.right() + pad, r2.bottom() + pad), wp)
        img = L.plate(key, int(rect.width()), int(rect.height()), focus, b.get('zoom', 1.0), oversize=1.0)
        c.drawImageRect(img, r2, L.SAMPLING)
        rect = r2
    ctx['occ'].append(('frame', rect))
    for mk in b.get('marks', []):
        draw_mark(c, mk, rect, f)
    if b.get('caption'):
        df = f - b.get('cap_at', b['f0'])
        O.tag(c, b['caption'], W / 2 if mode == 'full' else rect.centerX(),
              min(H - 0.05 * H, rect.bottom() + 0.075 * H) if mode != 'full' else H - 0.07 * H, df, cap=52)
    for a in b.get('actors', []):
        r = draw_actor(c, a, f)
        if r is not None:
            ctx['occ'].append(('face', r))
    if b.get('host'):
        hh = dict(b['host'])
        hh.setdefault('f0', b['f0'])
        ctx['occ'].append(('face', draw_host(c, hh, f, framing=hh.get('framing', 'L'), push=False)))


def draw_mark(c, mk, rect, f):
    kind = mk[0]
    at = mk[-1]
    df = f - at
    if df < 0:
        return
    px = lambda u: rect.left() + u * rect.width()  # noqa: E731
    py = lambda v: rect.top() + v * rect.height()  # noqa: E731
    if kind == 'ring':
        _, u, v, ru, rv, _at = mk
        O.ring(c, px(u), py(v), ru * rect.width(), rv * rect.height(), df)
    elif kind == 'arrow':
        _, u0, v0, u1, v1, _at = mk
        O.arrow(c, px(u0), py(v0), px(u1), py(v1), df)
    elif kind == 'label':
        _, text, u, v, _at = mk
        O.tag(c, text, px(u), py(v), df, cap=50, bg='#0A0A0A')


# ======================= scenes (characters on real photos / on the stage) =======================
@shot('scene')
def scene(c, b, f, ctx):
    bgk = b.get('bg')
    if bgk and L.exists(bgk):
        bg_photo_full(c, bgk, b, f, tuple(b.get('focus', (0.5, 0.5))), b.get('zoom', 1.0), blur=b.get('blur', 1.4),
                      gain=b.get('gain', 0.86), rate=0.003, direction=b.get('push', 1), vignette=b.get('vignette', 0.5),
                      sat=b.get('sat', 0.85))
        ctx['photo'] = True
    else:
        L.stage(c)
    if b.get('fx_under'):
        for fx in b['fx_under']:
            draw_fx(c, fx, f, b)
    items = [('p', p) for p in b.get('props', [])] + [('a', a) for a in b.get('actors', [])]
    items.sort(key=lambda it: it[1].get('z', 0))
    for kind, it in items:
        if kind == 'p':
            r = draw_prop(c, it, f, shadow=it.get('shadow', False))
            if r is not None and it.get('focal'):
                ctx['occ'].append(('face', r))
        else:
            r = draw_actor(c, it, f, rim=True)
            if r is not None:
                ctx['occ'].append(('face', r))
                it['_rect'] = r
    for fx in b.get('fx', []):
        draw_fx(c, fx, f, b)
    if b.get('klines'):
        if ctx['photo']:
            c.drawImage(L.top_scrim(0.40, 0.85), 0, 0)
        draw_klines(c, b['klines'], f)
    placed = ctx.setdefault('placed', [])
    for sp in b.get('says', []):
        text, cx, bottom, at, until = sp
        if at <= f < until:
            placed.append(O.speech(c, text, cx, bottom, f - at))
    for t in sorted(b.get('tags', []), key=lambda t: t[3]):
        text, cx, bottom, at = t
        if f >= at:
            cx, bottom = anchor_tag(b, f, cx, bottom)
            bottom = avoid_boxes(ctx, cx, bottom, text)
            bottom = avoid_placed(placed, cx, bottom, text)
            r = O.tag(c, text, cx, bottom, f - at)
            placed.append(r)
            ctx['tags'].append(r)


def anchor_tag(b, f, cx, bottom):
    """Snap a tag to just above the nearest visible character's head (standing or lying), so tags never float."""
    from engine.premium.actors import actor_state, HEAD_TO_FEET
    best = None
    for a in b.get('actors', []):
        st = actor_state(a, f)
        if st is None:
            continue
        R = st['R']
        rot = st['rot']
        if abs(rot) > 45:
            sgn = -1 if rot < 0 else 1
            hx, hy = st['x'] + sgn * HEAD_TO_FEET * R, st['y'] - 0.2 * R
        else:
            hx, hy = st['x'], st['y'] - HEAD_TO_FEET * R
        d = abs(hx - cx)
        if d < 1.7 * R and (best is None or d < best[0]):
            best = (d, hx, hy - 1.62 * R - 12)
    if best is None:
        return cx, bottom
    return best[1], best[2]


def avoid_boxes(ctx, cx, bottom, text, cap=49.0):
    """Push a tag below any active callout box it would touch."""
    h = cap * 2.05
    w = TY.width(text, cap, 800) + cap * 1.3
    r = skia.Rect(cx - w / 2, bottom - h, cx + w / 2, bottom)
    for box in ctx.get('avoid', []):
        if skia.Rect.Intersects(r, box.makeOutset(0, 14)):
            bottom = box.bottom() + 14 + h
            r = skia.Rect(cx - w / 2, bottom - h, cx + w / 2, bottom)
    return bottom


def avoid_placed(placed, cx, bottom, text, cap=49.0):
    """Move a tag up (or down if it would leave the frame) until it clears every overlay already placed."""
    h = cap * 2.05
    w = TY.width(text, cap, 800) + cap * 1.3
    for _ in range(6):
        r = skia.Rect(cx - w / 2, bottom - h, cx + w / 2, bottom)
        hit = [p for p in placed if p is not None and skia.Rect.Intersects(r, p.makeOutset(8, 8))]
        if not hit:
            break
        top = min(p.top() for p in hit)
        if top - 10 - h > 0.05 * H:
            bottom = top - 10
        else:
            bottom = max(p.bottom() for p in hit) + 10 + h
    return bottom


@shot('stage')
def stage_shot(c, b, f, ctx):
    b2 = dict(b, bg=None)
    scene(c, b2, f, ctx)


def draw_fx(c, fx, f, b):
    kind = fx['kind']
    df = f - fx.get('at', b['f0'])
    if df < 0 or (fx.get('until') is not None and f >= fx['until']):
        return
    if kind == 'flash':
        a = max(0.0, 1 - df / fx.get('dur', 5))
        if a > 0:
            p = skia.Paint(Color=rgb(fx.get('color', '#FFFFFF')))
            p.setAlphaf(a * fx.get('amp', 0.8))
            c.drawRect(skia.Rect(0, 0, W, H), p)
    elif kind == 'dust':
        rng = np.random.default_rng(fx.get('seed', 1))
        x0, y0, wd = fx['x'], fx['y'], fx.get('w', 500)
        for k in range(26):
            ox, oy, r = rng.uniform(-wd / 2, wd / 2), rng.uniform(-wd * 0.12, 0), rng.uniform(wd * 0.05, wd * 0.13)
            g = min(1.0, (df + 1) / 12)
            p = skia.Paint(AntiAlias=True, Color=rgb(fx.get('color', '#C9B79A')))
            p.setAlphaf(0.55 * g)
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.35))
            c.drawCircle(x0 + ox + df * rng.uniform(-0.6, 0.6), y0 + oy - df * rng.uniform(0.0, 0.5), r * (0.6 + 0.4 * g), p)
    elif kind == 'glints':
        rng = np.random.default_rng(fx.get('seed', 2))
        for k in range(fx.get('n', 18)):
            x = fx['x'] + rng.uniform(-fx.get('w', 500) / 2, fx.get('w', 500) / 2)
            y = fx['y'] + rng.uniform(-12, 12)
            ph = rng.uniform(0, 6.28)
            a = max(0.0, math.sin(df * 0.35 + ph))
            if a > 0.2:
                p = skia.Paint(AntiAlias=True, Color=skia.ColorWHITE)
                p.setAlphaf(a)
                s = 7 + 5 * a
                c.drawLine(x - s, y, x + s, y, p)
                c.drawLine(x, y - s, x, y + s, p)
                p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
                c.drawCircle(x, y, 6 * a, p)
    elif kind == 'fire':
        raw_prop(c, 'flames', fx['x'], fx['y'], fx.get('size', 80), t=df / FPS, rim=False)
    elif kind == 'rays':
        p = skia.Paint(AntiAlias=True)
        sh = skia.GradientShader.MakeRadial((fx['x'], fx['y']), fx.get('r', 700), [rgb('#FFF4C8', 150), rgb('#FFF4C8', 0)])
        p.setShader(sh)
        c.drawRect(skia.Rect(0, 0, W, H), p)
    elif kind == 'rain_gold':
        rng = np.random.default_rng(4)
        for k in range(40):
            x = rng.uniform(fx['x'] - 300, fx['x'] + 300)
            y = (rng.uniform(-400, 0) + df * rng.uniform(14, 24)) % 900 - 100
            raw_prop(c, 'coin', x, y, 26, rot=df * 9 + k * 30, rim=False)
    elif kind == 'bossbar':
        a = min(1.0, (df + 1) / 4)
        x0, x1, y = 0.14 * W, 0.86 * W, 0.17 * H
        TY.draw(c, fx['name'], W / 2, y - 0.03 * H, 0.06 * H, style='white', weight=900, align='center', alpha=int(255 * a))
        bar = skia.Rect(x0, y, x1, y + 0.03 * H)
        bp = skia.Paint(AntiAlias=True, Color=rgb('#0B0B0B'))
        bp.setAlphaf(0.85 * a)
        c.drawRRect(skia.RRect.MakeRectXY(bar.makeOutset(5, 5), 8, 8), bp)
        k = M.ease_out_cubic((df - 3) / 16)
        fill = skia.Rect(x0, y, x0 + (x1 - x0) * k, bar.bottom())
        fp = skia.Paint(AntiAlias=True)
        fp.setShader(skia.GradientShader.MakeLinear([(0, y), (0, bar.bottom())], [rgb('#FF5A50'), rgb('#C0201A')]))
        c.drawRRect(skia.RRect.MakeRectXY(fill, 6, 6), fp)
        op = skia.Paint(AntiAlias=True, Color=rgb('#FFFFFF'), Style=skia.Paint.kStroke_Style, StrokeWidth=3)
        op.setAlphaf(0.85 * a)
        c.drawRRect(skia.RRect.MakeRectXY(bar.makeOutset(5, 5), 8, 8), op)
        if fx.get('sub'):
            TY.draw(c, fx['sub'], W / 2, bar.bottom() + 0.065 * H, 0.04 * H, style='red', weight=900, align='center',
                    alpha=int(255 * min(1.0, max(0.0, (df - 8) / 4))))
    elif kind == 'censor':
        from engine.premium.actors import actor_state, HEAD_TO_FEET
        a_ = b['actors'][fx['actor']]
        st = actor_state(a_, f)
        if st is not None:
            R = st['R']
            hx, hy = st['x'], st['y'] - HEAD_TO_FEET * R * st['sy']
            ey = hy - 0.02 * R
            k = M.ease_out_back((df + 1) / 5, 1.6)
            w_ = 0.78 * R * k
            c.save()
            c.translate(hx, ey)
            c.rotate(-4)
            c.drawRect(skia.Rect(-w_, -0.19 * R, w_, 0.19 * R), skia.Paint(AntiAlias=True, Color=rgb('#050505')))
            if k > 0.6:
                TY.draw(c, 'CENSORED', 0, 0.075 * R, 0.13 * R, style='white', weight=900, align='center', shadow=0)
            c.restore()
    elif kind == 'split':
        x, y, size = fx['x'], fx['y'], fx['size']
        t = df / FPS
        for side in (-1, 1):
            c.save()
            ang = side * min(35.0, 90 * t * t + 8 * t)
            sink = 260 * t * t
            c.translate(x + side * (14 + 60 * t), y + sink)
            c.rotate(ang)
            c.clipRect(skia.Rect(-size * 2 if side < 0 else 0, -size * 3, 0 if side < 0 else size * 2, size * 3))
            raw_prop(c, fx.get('ship', 'longship'), 0, 0, size, t=t)
            c.restore()
        rng = np.random.default_rng(3)
        for k in range(28):
            vx, vy = rng.uniform(-260, 260), rng.uniform(-520, -260)
            px, py = x + vx * t, y + size * 0.25 + vy * t + 900 * t * t
            if py < y + size * 0.6:
                sp = skia.Paint(AntiAlias=True, Color=rgb('#DCEBF2'))
                sp.setAlphaf(max(0.0, 0.9 - t))
                c.drawCircle(px, py, rng.uniform(4, 10), sp)
    elif kind == 'bodycam':
        lum = skia.Paint()
        lum.setColorFilter(skia.ColorFilters.Matrix([0.45, 0.45, 0.10, 0, 0, 0.40, 0.50, 0.10, 0, 0, 0.35, 0.45, 0.20, 0, 0, 0, 0, 0, 0.0, 0]))
        p = skia.Paint(Color=rgb('#0F1A12'))
        p.setAlphaf(0.25)
        c.drawRect(skia.Rect(0, 0, W, H), p)
        br = skia.Paint(AntiAlias=True, Color=skia.ColorWHITE, Style=skia.Paint.kStroke_Style, StrokeWidth=6)
        m, L_ = 70, 90
        for (cx_, cy_, sx, sy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
            pth = skia.Path()
            pth.moveTo(cx_, cy_ + sy * L_); pth.lineTo(cx_, cy_); pth.lineTo(cx_ + sx * L_, cy_)
            c.drawPath(pth, br)
        if (df // 15) % 2 == 0:
            c.drawCircle(m + 50, m + 62, 16, skia.Paint(AntiAlias=True, Color=rgb('#FF2A2A')))
        TY.draw(c, 'REC', m + 80, m + 80, 0.04 * H, style='white', weight=800, shadow=0.6)
        sec = 7 + df // 30
        TY.draw(c, f'SEP 25 1066  14:32:{sec:02d}', W - m - 20, H - m - 26, 0.036 * H, style='white', weight=700,
                align='right', shadow=0.6)
        TY.draw(c, 'BODYCAM 01', m + 20, H - m - 26, 0.036 * H, style='white', weight=700, shadow=0.6)
    elif kind == 'head':
        x, y = fx['x'], fx['y']
        for mv in fx.get('moves', []):
            if f >= mv[0]:
                k = M.ease_in_out_cubic((f - mv[0] + 1) / mv[3]) if len(mv) > 3 else 1.0
                x, y = x + (mv[1] - x) * k, y + (mv[2] - y) * k
        draw_head(c, fx['pal'], x, y, fx.get('R', 46), fx.get('expr', 'ko'), fx.get('rot', 0.0))
    elif kind == 'pour':
        k = min(1.0, (df + 1) / 8)
        rng = np.random.default_rng(6)
        for j in range(40):
            t = ((df * 0.9 + j * 3.7) % 20) / 20
            px, py = fx['x'] + rng.uniform(-6, 6) + t * fx.get('dx', 0), fx['y'] + t * fx.get('len', 260) * k
            gp = skia.Paint(AntiAlias=True, Color=rgb('#F2C94C'))
            gp.setAlphaf(0.9)
            c.drawCircle(px, py, 9 - 4 * t, gp)
        gl = skia.Paint(AntiAlias=True, Color=rgb('#FFD45A'))
        gl.setAlphaf(0.35)
        gl.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
        c.drawCircle(fx['x'], fx['y'] + fx.get('len', 260) * k, 46, gl)
    elif kind == 'blackout':
        dur = fx.get('dur', 60)
        k = min(1.0, (df + 1) / dur) * fx.get('amp', 0.75)
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), W * (0.9 - 0.45 * k), [rgb('#000000', 0), rgb('#000000', int(255 * k))],
                                                   [0.2, 1.0]))
        c.drawRect(skia.Rect(0, 0, W, H), p)
    elif kind == 'text':
        if df >= 0:
            s_, a_ = M.pop(df, 0.6)
            TY.draw(c, fx['t'], fx['x'], fx['y'], fx.get('cap', 0.05 * H) * s_, style=fx.get('style', 'white'), weight=900,
                    align='center', alpha=int(255 * a_), stroke=fx.get('stroke'), stroke_color='#0B0B0B')
    elif kind == 'vignette_red':
        a = min(1.0, (df + 1) / 6)
        p = skia.Paint(AntiAlias=True)
        sh = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.75, [rgb('#000000', 0), rgb('#5A0000', int(200 * a))], [0.45, 1.0])
        p.setShader(sh)
        c.drawRect(skia.Rect(0, 0, W, H), p)


# ======================= title card =======================
@shot('title')
def title(c, b, f, ctx):
    L.stage(c)
    df = f - b['f0']
    # portrait (right): settle 1.04 -> 1.0, slow push
    pw, ph = 0.29 * W, 0.29 * W * 1.25
    cx, cy = 0.705 * W, 0.50 * H
    rect = skia.Rect(cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2)
    k = M.ease_out_cubic((df + 1) / 8)
    s = (1.04 - 0.04 * k) * (1 + 0.008 * secs(b, f))
    r2 = skia.Rect(cx - pw / 2 * s, cy - ph / 2 * s, cx + pw / 2 * s, cy + ph / 2 * s)
    glow = skia.Paint(AntiAlias=True)
    glow.setShader(skia.GradientShader.MakeRadial((cx, cy), pw * 1.1, [rgb('#E0393E', 40), rgb('#E0393E', 0)]))
    c.drawRect(skia.Rect(0, 0, W, H), glow)
    L.soft_shadow(c, r2, 30, (0, 20), 0.9, 6)
    img = L.plate(b['img'], int(pw), int(ph), tuple(b.get('focus', (0.5, 0.4))), b.get('zoom', 1.0), oversize=1.0)
    c.drawImageRect(img, r2, L.SAMPLING)
    ctx['occ'].append(('frame', r2))
    # rank + name (left, x = 15 % W): tracking tightens 0.10 -> 0.02 (ease-out-expo), staggered lines
    x0 = 0.15 * W
    cap = 0.067 * H * b.get('name_scale', 1.0)
    lines = b['name']
    lh = cap * 1.42
    total = 0.05 * H * 1.6 + lh * len(lines)
    y = cy - total / 2 + 0.05 * H
    s1, a1 = M.pop(df, 0.6)
    c.save()
    c.translate(x0, y)
    c.scale(s1, s1)
    c.translate(-x0, -y)
    TY.draw(c, f'#{b["num"]}', x0, y, 0.05 * H, style='red', weight=900, alpha=int(255 * a1), shadow=0.8)
    c.restore()
    y += 0.05 * H * 0.6
    maxw = (cx - pw / 2) - x0 - 0.04 * W
    fitcap = min([cap] + [cap * maxw / TY.width(ln, cap, 800, 0.10) for ln in lines if TY.width(ln, cap, 800, 0.10) > maxw])
    for i, ln in enumerate(lines):
        d = df - 2 - 2 * i
        tr = 0.02 + 0.08 * (1 - M.ease_out_expo((d + 1) / 16))
        a = M.clamp01((d + 1) / 4)
        y += lh
        TY.draw(c, ln, x0, y, fitcap, style='silver', weight=800, tracking=tr, alpha=int(255 * a), shadow=0.9)


# ======================= kinetic title =======================
def draw_klines(c, lines, f, ghost=64):
    """Reference kinetic type: words wait as dim ghosts (~25 %) and light up white/red within 1-2 frames when spoken."""
    for line in lines:
        y, words, cap = line['y'], line['words'], line['cap']
        gap = cap * 0.55
        ws = [TY.width(w['t'], cap, 900, 0.02) for w in words]
        total = sum(ws) + gap * (len(ws) - 1)
        if total > 0.92 * W:
            k = 0.92 * W / total
            cap, gap, ws, total = cap * k, gap * k, [x * k for x in ws], total * k
        x = W / 2 - total / 2
        for w, wd in zip(words, ws):
            d = f - w['at']
            if d < 0:
                style, alpha, sc = '#FFFFFF', ghost, 1.0
            else:
                style = 'hotred' if w.get('red') else 'white'
                alpha = 255
                sc = 1 + 0.07 * max(0.0, 1 - (d + 1) / 3)
            c.save()
            c.translate(x + wd / 2, y - cap / 2)
            c.scale(sc, sc)
            c.translate(-(x + wd / 2), -(y - cap / 2))
            TY.draw(c, w['t'], x, y, cap, style=style, weight=900, alpha=alpha, shadow=0.9 if d >= 0 else 0.4, tracking=0.02)
            c.restore()
            x += wd + gap


@shot('kinetic')
def kinetic(c, b, f, ctx):
    L.stage(c)
    draw_klines(c, b['lines'], f)
    for a in b.get('actors', []):
        r = draw_actor(c, a, f)
        if r is not None:
            ctx['occ'].append(('face', r))


def _unused_kinetic(c, b, f, ctx):
    for line in b['lines']:
        y, words, cap = line['y'], line['words'], line['cap']
        gap = cap * 0.55
        ws = [TY.width(w['t'], cap, 900, 0.02) for w in words]
        total = sum(ws) + gap * (len(ws) - 1)
        x = W / 2 - total / 2
        for w, wd in zip(words, ws):
            on = w['at']
            d = f - on
            if d < 0:
                style, alpha, sc = '#FFFFFF', 64, 1.0
            else:
                style = 'hotred' if w.get('red') else 'white'
                alpha = 255
                sc = 1 + 0.07 * max(0.0, 1 - (d + 1) / 3)
            c.save()
            c.translate(x + wd / 2, y - cap / 2)
            c.scale(sc, sc)
            c.translate(-(x + wd / 2), -(y - cap / 2))
            TY.draw(c, w['t'], x, y, cap, style=style, weight=900, alpha=alpha, shadow=0.9 if d >= 0 else 0, tracking=0.02)
            c.restore()
            x += wd + gap
    for a in b.get('actors', []):
        r = draw_actor(c, a, f)
        if r is not None:
            ctx['occ'].append(('face', r))


# ======================= big statement text =======================
@shot('text')
def text_shot(c, b, f, ctx):
    if b.get('bg') and L.exists(b['bg']):
        bg_blur(c, b['bg'], b, f, gain=b.get('gain', 0.30))
        ctx['photo'] = True
    else:
        L.stage(c)
    lines = b['lines']
    cap = b.get('cap', 0.105 * H)
    caps = []
    for ln in lines:
        txt = ln[0]
        cp = ln[2] if len(ln) > 2 and ln[2] else cap
        if TY.width(txt, cp, 900) > 0.9 * W:
            cp *= 0.9 * W / TY.width(txt, cp, 900)
        caps.append(cp)
    gaps = [cp * 0.42 for cp in caps]
    total = sum(caps) + sum(gaps[:-1])
    y = H / 2 - total / 2 + b.get('dy', 0)
    df0 = f - b['f0']
    anim = b.get('anim', 'settle')
    for i, (ln, cp) in enumerate(zip(lines, caps)):
        txt, style = ln[0], ln[1]
        at = ln[3] if len(ln) > 3 and ln[3] is not None else b['f0'] + 3 * i
        d = f - at
        y += cp
        if d >= 0:
            if anim == 'slam':
                t = min(1.0, (d + 1) / 3)
                s = 1.45 - 0.45 * M.ease_out_cubic(t)
                a = min(1.0, (d + 1) / 2)
            else:
                s, a = M.settle(d, frames=5, from_scale=1.06)
            c.save()
            c.translate(W / 2, y - cp / 2)
            c.scale(s, s)
            c.translate(-W / 2, -(y - cp / 2))
            TY.draw(c, txt, W / 2, y, cp, style=style, weight=900, align='center', alpha=int(255 * a), shadow=0.95)
            if len(ln) > 4 and ln[4] and f >= ln[4]:          # strike-through draws on
                wd = TY.width(txt, cp, 900)
                pth = skia.Path()
                pth.moveTo(W / 2 - wd / 2 - 10, y - cp * 0.45)
                pth.lineTo(W / 2 + wd / 2 + 10, y - cp * 0.52)
                O.stroke_partial(c, pth, M.draw_on(f - ln[4], 6), cp * 0.16, '#E0262B')
            c.restore()
        y += cp * 0.42
    ctx['occ'].append(('frame', skia.Rect(0.05 * W, H / 2 - total / 2, 0.95 * W, H / 2 + total / 2)))


# ======================= meme band =======================
@shot('band')
def band_shot(c, b, f, ctx):
    if b.get('img'):
        bh = H * b.get('h', 0.28)
        img = L.plate(b['img'], W, int(H - bh), tuple(b.get('focus', (0.5, 0.5))), b.get('zoom', 1.0))
        s = 1 + 0.006 * secs(b, f)
        c.save()
        c.clipRect(skia.Rect(0, bh, W, H))
        L.draw_scaled(c, img, W / 2, bh + (H - bh) / 2, s, w=W, h=H - bh)
        c.restore()
        ctx['photo'] = True
    else:
        L.stage(c)
    for kind, it in sorted([('p', p) for p in b.get('props', [])] + [('a', a) for a in b.get('actors', [])],
                           key=lambda x: x[1].get('z', 0)):
        if kind == 'p':
            draw_prop(c, it, f)
        else:
            draw_actor(c, it, f)
    for item in b.get('photos', []):
        key, cx, cy, w, at = item[:5]
        if f >= at and L.exists(key):
            s, a = M.pop(f - at, 0.7)
            hh = w * 1.2
            r = skia.Rect(cx - w / 2 * s, cy - hh / 2 * s, cx + w / 2 * s, cy + hh / 2 * s)
            L.soft_shadow(c, r, 18, (0, 12), 0.8 * a, 4)
            foc = item[6] if len(item) > 6 else (0.5, 0.35)
            c.drawImageRect(L.plate(key, int(w), int(hh), foc, oversize=1.0), r, L.SAMPLING)
            if len(item) > 5 and item[5] and f >= item[5]:
                O.draw_x(c, cx, cy, min(w, hh) * 0.7, df=f - item[5])
    for txt, cx, at in b.get('photo_labels', []):
        if f >= at:
            O.tag(c, txt, cx, b.get('label_y', 0.955 * H), f - at, cap=44, bg='#E0262B', max_w=b.get('label_w', 0.25 * W))
    ctx['occ'].append(('frame', O.band(c, b['text'], f - b['f0'], b.get('h', 0.28))))


# ======================= list =======================
@shot('list')
def list_shot(c, b, f, ctx):
    if b.get('bg') and L.exists(b['bg']):
        bg_blur(c, b['bg'], b, f, gain=0.26)
    else:
        L.stage(c)
    items = b['items']
    n = len(items)
    cap = b.get('cap', 0.075 * H if n <= 4 else 0.066 * H)
    tcap = 0.085 * H
    maxw = max(TY.width(it['text'], cap, 800) for it in items)
    if maxw + cap * 1.8 > 0.86 * W:
        cap *= 0.86 * W / (maxw + cap * 1.8)
    if (tcap * 1.7 + cap * 1.75 * n) > 0.86 * H:
        cap *= 0.86 * H / (tcap * 1.7 + cap * 1.75 * n)
    lh = cap * 1.75
    widths = [TY.width(it['text'], cap, 800) for it in items]
    block_w = max(widths + [0]) + cap * 1.8
    if block_w > 0.9 * W:
        k = 0.9 * W / block_w
        cap *= k
        lh *= k
        block_w = 0.9 * W
    top = H / 2 - (tcap * 1.7 + lh * n) / 2
    if b.get('title'):
        s, a = M.settle(f - b['f0'], 5)
        TY.draw(c, b['title'], W / 2, top + tcap, tcap, style=b.get('title_style', 'red'), weight=900, align='center',
                alpha=int(255 * a))
        top += tcap * 1.75
    x0 = W / 2 - block_w / 2
    for i, it in enumerate(items):
        at = it.get('at', b['f0'] + 4 * i)
        d = f - at
        y = top + lh * i + cap
        if d < 0:
            continue
        s, a = M.pop(d, 0.7)
        slide = M.slide(d, -40, frames=7)
        mark = it.get('mark', b.get('mark'))
        mx = x0 + cap * 0.55 + slide
        if mark == 'x':
            O.draw_x(c, mx, y - cap / 2, cap * 1.05, df=d)
        elif mark == 'check':
            O.draw_check(c, mx, y - cap / 2, cap * 1.05, df=d)
        elif mark == 'dot':
            p = skia.Paint(AntiAlias=True, Color=rgb('#E0393E'))
            c.drawCircle(mx, y - cap / 2, cap * 0.22, p)
        TY.draw(c, it['text'], x0 + cap * 1.6 + slide, y, cap, style=it.get('style', 'white'), weight=800,
                alpha=int(255 * a), shadow=0.9)
        if it.get('strike') is not None and f >= it['strike']:
            wd = TY.width(it['text'], cap, 800)
            pth = skia.Path()
            pth.moveTo(x0 + cap * 1.4, y - cap * 0.45)
            pth.lineTo(x0 + cap * 1.8 + wd, y - cap * 0.55)
            O.stroke_partial(c, pth, M.draw_on(f - it['strike'], 6), cap * 0.17, '#E0262B')
    ctx['occ'].append(('frame', skia.Rect(x0, top - tcap, x0 + block_w, top + lh * n)))


# ======================= quote (karaoke) =======================
@shot('quote')
def quote_shot(c, b, f, ctx):
    if b.get('bg') and L.exists(b['bg']):
        bg_blur(c, b['bg'], b, f, gain=0.28, focus=tuple(b.get('focus', (0.5, 0.5))))
    else:
        L.stage(c)
    words = b['text'].upper().split()
    cap = b.get('cap', 0.064 * H)
    maxw = 0.78 * W
    lines, cur = [], []
    for i, w in enumerate(words):
        t = ' '.join(x for _, x in cur + [(i, w)])
        if cur and TY.width(t, cap, 800) > maxw:
            lines.append(cur)
            cur = [(i, w)]
        else:
            cur.append((i, w))
    lines.append(cur)
    lh = cap * 1.55
    total = lh * (len(lines) - 1) + cap
    top = H / 2 - total / 2 - 0.03 * H
    qc = cap * 2.2
    first_w = TY.width(' '.join(w for _, w in lines[0]), cap, 800)
    TY.draw(c, '“', W / 2 - first_w / 2 - qc * 0.95, top + qc * 0.66, qc, style='red', weight=900, shadow=0.6)
    wf = b['word_frames']
    for li, ln in enumerate(lines):
        y = top + cap + li * lh
        lw = TY.width(' '.join(w for _, w in ln), cap, 800)
        x = W / 2 - lw / 2
        for i, w in ln:
            on = wf[i] if i < len(wf) else b['f0']
            lit = f >= on
            wd = TY.width(w, cap, 800)
            TY.draw(c, w, x, y, cap, style='white' if lit else '#FFFFFF', weight=800, alpha=255 if lit else 60,
                    shadow=0.85 if lit else 0)
            x += wd + TY.width(' ', cap, 800) + cap * 0.06
    if b.get('who'):
        last = wf[-1] if wf else b['f0']
        d = f - last - 4
        if d >= 0:
            s, a = M.settle(d, 6)
            TY.draw(c, '— ' + b['who'].upper(), W / 2, top + total + 0.115 * H, 0.045 * H, style='#BDBDBD', weight=700,
                    align='center', alpha=int(255 * a), shadow=0.6)
    ctx['occ'].append(('frame', skia.Rect(0.08 * W, top, 0.92 * W, top + total + 0.13 * H)))


# ======================= versus =======================
@shot('versus')
def versus(c, b, f, ctx):
    L.stage(c)
    cols = [(0.27 * W, b['left']), (0.73 * W, b['right'])]
    for i, (cx, side) in enumerate(cols):
        at = side.get('at', b['f0'] + 6 * i)
        d = f - at
        if d < 0:
            continue
        s, a = M.pop(d, 0.7)
        cy = 0.47 * H
        if side.get('img') and L.exists(side['img']):
            pw, ph = 0.36 * W, 0.36 * W * 0.75
            r = skia.Rect(cx - pw / 2 * s, cy - ph / 2 * s - 0.06 * H, cx + pw / 2 * s, cy + ph / 2 * s - 0.06 * H)
            L.soft_shadow(c, r, 20, (0, 14), 0.8 * a, 6)
            c.drawImageRect(L.plate(side['img'], int(pw), int(ph), tuple(side.get('focus', (0.5, 0.5))), oversize=1.0), r, L.SAMPLING)
            ty = r.bottom() + 0.09 * H
        else:
            ty = cy
        for k, ln in enumerate(side['lines']):
            txt, style = ln
            cp = side.get('cap', 0.06 * H)
            if TY.width(txt, cp, 900) > 0.42 * W:
                cp *= 0.42 * W / TY.width(txt, cp, 900)
            TY.draw(c, txt, cx, ty + k * cp * 1.45, cp, style=style, weight=900, align='center', alpha=int(255 * a))
    d = f - b['f0']
    pth = skia.Path()
    pth.moveTo(W / 2, 0.16 * H)
    pth.lineTo(W / 2, 0.84 * H)
    O.stroke_partial(c, pth, M.draw_on(d, 8), 6, '#E0393E')
    ctx['occ'].append(('frame', skia.Rect(0.05 * W, 0.12 * H, 0.95 * W, 0.9 * H)))


# ======================= trio of portraits =======================
@shot('trio')
def trio(c, b, f, ctx):
    L.stage(c)
    n = len(b['people'])
    pw = 0.255 * W
    ph = pw * 1.25
    gap = 0.045 * W
    x0 = W / 2 - (n * pw + (n - 1) * gap) / 2
    cy = 0.47 * H
    for i, p in enumerate(b['people']):
        cx = x0 + pw / 2 + i * (pw + gap)
        at = p.get('at', b['f0'])
        lit = f >= p.get('lit', at)
        d = f - at
        if d < 0:
            continue
        s, a = M.pop(d, 0.8)
        r = skia.Rect(cx - pw / 2 * s, cy - ph / 2 * s, cx + pw / 2 * s, cy + ph / 2 * s)
        L.soft_shadow(c, r, 18, (0, 12), 0.8, 6)
        img = L.plate(p['img'], int(pw), int(ph), tuple(p.get('focus', (0.5, 0.4))), p.get('zoom', 1.0), oversize=1.0,
                      sat=0.88 if lit else 0.0, gain=1.0 if lit else 0.45)
        c.drawImageRect(img, r, L.SAMPLING)
        if lit and p.get('ring'):
            bp = skia.Paint(AntiAlias=True, Color=rgb('#E0393E'), Style=skia.Paint.kStroke_Style, StrokeWidth=8)
            c.drawRect(r, bp)
        for k, ln in enumerate(p['name']):
            TY.draw(c, ln, cx, r.bottom() + 0.075 * H + k * 0.062 * H, 0.043 * H, style='white' if lit else '#8A8A8A',
                    weight=800, align='center', alpha=int(255 * a))
        if p.get('sub') and f >= p.get('sub_at', 10 ** 9):
            ds = f - p['sub_at']
            s2, a2 = M.pop(ds, 0.6)
            TY.draw(c, p['sub'], cx, r.bottom() + 0.075 * H + len(p['name']) * 0.062 * H + 0.01 * H, 0.04 * H * s2, style='red',
                    weight=900, align='center', alpha=int(255 * a2))
        if p.get('crown') is not None and f >= p['crown']:
            dd = f - p['crown']
            yy = r.top() - 0.07 * H + M.drop(dd, 200, 12)
            raw_prop(c, 'crown', cx, yy, 0.045 * H)
    ctx['occ'].append(('frame', skia.Rect(x0, cy - ph / 2, W - x0, cy + ph / 2 + 0.15 * H)))


# ======================= ships (count) =======================
@shot('ships')
def ships(c, b, f, ctx):
    bgk = b.get('bg')
    if bgk and L.exists(bgk):
        bg_photo_full(c, bgk, b, f, blur=2.0, gain=0.6, rate=0.003)
    else:
        L.stage(c)
    n, n2 = b['n'], b.get('n2', b['n'])
    change = b.get('change')
    cols = int(math.ceil(math.sqrt(n * 2.4)))
    rows = int(math.ceil(n / cols))
    area_w, area_h = 0.86 * W, 0.50 * H
    cell = min(area_w / cols, area_h / rows)
    size = cell * 0.36
    x0 = W / 2 - cols * cell / 2 + cell / 2
    y0 = 0.60 * H - rows * cell / 2 + cell / 2
    rng = np.random.default_rng(7)
    keep = set(rng.choice(n, n2, replace=False).tolist()) if n2 < n else set(range(n))
    for i in range(n):
        r, k = divmod(i, cols)
        x, y = x0 + k * cell, y0 + r * cell
        at = b['f0'] + int(i * min(1.0, 14.0 / max(1, n)))
        d = f - at
        if d < 0:
            continue
        s, a = M.pop(d, 0.6)
        if change is not None and f >= change and i not in keep:
            dd = f - change - (i % 9)
            if dd >= 0:
                s, a = M.pop_out(dd, 5)
                if a <= 0:
                    continue
        raw_prop(c, b.get('ship', 'longship'), x, y + math.sin(f / 9 + i) * 2, size * s, t=f / FPS, alpha=int(255 * a))
    lab = b.get('label', ('',))
    txt = lab[0] if (change is None or f < change or len(lab) < 2) else lab[1]
    if txt:
        d = f - (b['f0'] if (change is None or f < change) else change)
        O.callout(c, txt, d, style='red' if (change is not None and f >= change) else 'white')


# ======================= map =======================
@functools.lru_cache(maxsize=1)
def _regions():
    import json
    return json.load(open(os.path.join(ROOT, 'engine', 'assets', 'maps', 'regions.json')))


@functools.lru_cache(maxsize=24)
def _region_paths(name):
    from engine.mapdraw import parse_d3_path
    reg = _regions()[name]
    return [(l['name'], parse_d3_path(l['d'])) for l in reg['land']]


@functools.lru_cache(maxsize=24)
def map_base(name, highlight=()):
    """Dark stage map: land in charcoal with a soft edge, highlighted countries in the reference green."""
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    paths = _region_paths(name)
    sh = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    sh.setAlphaf(0.7)
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
    for nm, p in paths:
        c.save(); c.translate(0, 7); c.drawPath(p, sh); c.restore()
    for nm, p in paths:
        hi = nm in highlight
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=rgb('#4D7336' if hi else '#3A3A3A'), Style=skia.Paint.kStroke_Style,
                                 StrokeWidth=7 if hi else 3, StrokeJoin=skia.Paint.kRound_Join))
    for nm, p in paths:
        hi = nm in highlight
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=rgb('#96E669' if hi else '#222222')))
        if hi:
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=rgb('#6FB34E'), Style=skia.Paint.kStroke_Style, StrokeWidth=2.5))
    return s.makeImageSnapshot()


def _ease_path(p0, p1, k, bend=0.15):
    x0, y0 = p0
    x1, y1 = p1
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    pth = skia.Path()
    pth.moveTo(x0, y0)
    pth.quadTo(mx, my, x1, y1)
    pm = skia.PathMeasure(pth, False)
    seg = skia.Path()
    pm.getSegment(0, pm.getLength() * k, seg, True)
    pos = pm.getPosTan(pm.getLength() * k)
    return seg, (pos[0].x(), pos[0].y()) if pos else (x1, y1)


@shot('map')
def map_shot(c, b, f, ctx):
    L.stage(c)
    ctx['photo'] = True
    reg = _regions()[b['region']]
    pts = reg['pts']
    tl = secs(b, f)
    zoom = b.get('zoom', 1.0)
    fx, fy = pts[b['focus']] if b.get('focus') else (W / 2, H / 2)
    s0, _ = M.settle(f - b['f0'], 6, 1.04)
    sc = s0 * (1 + 0.006 * tl) * zoom
    c.save()
    c.translate(W / 2, H / 2 + b.get('dy', 0.04 * H))
    c.scale(sc, sc)
    c.translate(-fx, -fy)
    c.drawImage(map_base(b['region'], tuple(b.get('highlight', ()))), 0, 0)
    stops = b.get('stops', [])
    head = None
    for i in range(1, len(stops)):
        fs = stops[i][2]
        if f < fs:
            break
        k = M.ease_in_out_cubic((f - fs + 1) / 20)
        seg, head = _ease_path(pts[stops[i - 1][0]], pts[stops[i][0]], k, bend=0.12 * (1 if i % 2 else -1))
        c.drawPath(seg, skia.Paint(AntiAlias=True, Color=rgb('#FFFFFF'), Style=skia.Paint.kStroke_Style, StrokeWidth=11 / sc,
                                   StrokeCap=skia.Paint.kRound_Cap))
        dp = skia.Paint(AntiAlias=True, Color=rgb('#E0393E'), Style=skia.Paint.kStroke_Style, StrokeWidth=6 / sc)
        dp.setPathEffect(skia.DashPathEffect.Make([20 / sc, 12 / sc], -(f * 2.0) / sc))
        c.drawPath(seg, dp)
    c.restore()

    def to_screen(pt):
        return (W / 2 + (pt[0] - fx) * sc, H / 2 + b.get('dy', 0.04 * H) + (pt[1] - fy) * sc)
    markers = [(n, lab, at) for (n, lab, at) in stops] + [tuple(p) for p in b.get('pins', [])]
    for n, lab, at in markers:
        if f < at:
            continue
        x, y = to_screen(pts[n])
        d = f - at
        pr = 15 * (1 + 0.5 * max(0.0, 1 - d / 8))
        ring = skia.Paint(AntiAlias=True, Color=rgb('#E0393E'), Style=skia.Paint.kStroke_Style, StrokeWidth=4)
        ring.setAlphaf(max(0.0, 1 - (d % 24) / 24))
        c.drawCircle(x, y, pr + (d % 24) * 1.6, ring)
        c.drawCircle(x, y, pr + 4, skia.Paint(AntiAlias=True, Color=rgb('#FFFFFF')))
        c.drawCircle(x, y, pr, skia.Paint(AntiAlias=True, Color=rgb('#E0393E')))
        if lab:
            cap = 0.046 * H
            wl = TY.width(lab, cap, 800)
            cands = [(x + 34, y + 18, 'left'), (x - 34, y + 18, 'right'), (x - wl / 2, y - 30, 'left'), (x - wl / 2, y + 30 + cap, 'left')]
            if x > W * 0.72:
                cands = [cands[1], cands[0]] + cands[2:]
            chosen = None
            for lx, ly, al in cands:
                x0 = lx if al == 'left' else lx - wl
                rr = skia.Rect(x0 - 8, ly - cap - 8, x0 + wl + 8, ly + 8)
                if rr.left() < 0.03 * W or rr.right() > 0.97 * W or rr.top() < 0.04 * H or rr.bottom() > 0.97 * H:
                    continue
                if not any(skia.Rect.Intersects(rr, o) for o in ctx.setdefault('maplabels', [])):
                    chosen = (lx, ly, al, rr)
                    break
            if chosen is None:
                lx, ly, al = cands[0]
                chosen = (lx, ly, al, skia.Rect(lx, ly - cap, lx + wl, ly))
            lx, ly, al, rr = chosen
            ctx['maplabels'].append(rr)
            s, a = M.pop(d, 0.6)
            TY.draw(c, lab, lx, ly, cap * s, style='#FFFFFF', weight=800, align=al,
                    alpha=int(255 * a), shadow=0.9, stroke=9, stroke_color='#0B0B0B')
    if head and b.get('icon'):
        x, y = to_screen(head) if False else (W / 2 + (head[0] - fx) * sc, H / 2 + b.get('dy', 0.04 * H) + (head[1] - fy) * sc)
        raw_prop(c, b['icon'], x, y - 34, 40, t=tl)
    for lab in b.get('labels', []):
        txt, (u, v), at = lab
        if f >= at:
            s, a = M.pop(f - at, 0.6)
            TY.draw(c, txt, u * W, v * H, 0.05 * H * s, style='#FFFFFF', weight=900, align='center', alpha=int(255 * a),
                    shadow=0.9, stroke=10, stroke_color='#0B0B0B')


# ======================= end screen =======================
@shot('end')
def end_shot(c, b, f, ctx):
    L.stage(c)
    logo_at = b['logo']
    slot_at = b.get('slot_at', logo_at)
    d = f - logo_at
    ds = f - slot_at
    # host first; when the next-video slot appears he steps right and points at it; whips out when the logo drops (reference)
    pose = 'wave' if ds < 0 else 'point'
    hh = dict(b.get('host', {}), f0=b['f0'], exprs=b.get('exprs', [(b['f0'], 'smile')]), pose=pose, look=(-0.25, 0.0) if ds >= 0 else (0, 0))
    if d < 5:
        dx = 0 if d < 0 else W * M.ease_in_cubic((d + 1) / 5)
        if ds >= 0:
            dx += (1 - M.ease_out_cubic((ds + 1) / 10)) * -0.0
        c.save()
        c.translate(dx, 0)
        if ds >= 0:
            fl = dict(hh)
            c.save()
            c.translate(0.30 * W * M.ease_out_back((ds + 1) / 10, 1.2), 0)
            c.translate(W / 2, 0)
            c.scale(-1, 1)
            c.translate(-W / 2, 0)
            draw_host(c, fl, f, framing='M')
            c.restore()
        else:
            draw_host(c, hh, f, framing='M')
        c.restore()
    if ds < 0:
        return
    # next-video slot (YouTube places the end-screen element here): glowing frame, gentle shimmer
    slot = skia.Rect(0.08 * W, 0.24 * H, 0.08 * W + 0.47 * W, 0.24 * H + 0.47 * W * 9 / 16)
    s, a = M.pop(ds, 0.8)
    if a > 0:
        c.save()
        c.translate(slot.centerX(), slot.centerY())
        c.scale(s, s)
        c.translate(-slot.centerX(), -slot.centerY())
        fill = skia.Paint(AntiAlias=True, Color=rgb('#141414'))
        fill.setAlphaf(a)
        c.drawRRect(skia.RRect.MakeRectXY(slot, 18, 18), fill)
        sh = skia.GradientShader.MakeLinear([(slot.left() - 400 + (ds * 14) % 1800, 0), (slot.left() + (ds * 14) % 1800, 0)],
                                            [rgb('#FFFFFF', 0), rgb('#FFFFFF', 22), rgb('#FFFFFF', 0)], [0, 0.5, 1])
        sp = skia.Paint(AntiAlias=True)
        sp.setShader(sh)
        c.drawRRect(skia.RRect.MakeRectXY(slot, 18, 18), sp)
        bp = skia.Paint(AntiAlias=True, Color=rgb('#E0393E'), Style=skia.Paint.kStroke_Style, StrokeWidth=6)
        bp.setAlphaf(a)
        c.drawRRect(skia.RRect.MakeRectXY(slot, 18, 18), bp)
        TY.draw(c, 'WATCH NEXT', slot.centerX(), slot.top() - 0.04 * H, 0.05 * H, style='white', weight=900, align='center',
                alpha=int(255 * a))
        c.restore()
    if d < 0:
        return
    # logo + subscribe fall in and bounce (reference end screen)
    lx, ly = 0.76 * W, 0.42 * H
    yd = M.drop(d, 700, 14)
    c.save()
    c.translate(0, yd)
    R = 120
    RH.draw_character(c, lx, ly - 0.03 * H, R * 0.7, 'idle', blinked('smile', f), HOST, show_rim=True)
    c.restore()
    d2 = d - 6
    if d2 >= 0:
        yd2 = M.drop(d2, 700, 14)
        r = skia.Rect(lx - 0.13 * W, 0.70 * H + yd2, lx + 0.13 * W, 0.70 * H + 0.10 * H + yd2)
        p = skia.Paint(AntiAlias=True, Color=rgb('#E0262B'))
        c.drawRRect(skia.RRect.MakeRectXY(r, r.height() / 2, r.height() / 2), p)
        TY.draw(c, 'SUBSCRIBE', r.centerX(), r.centerY() + 0.019 * H, 0.038 * H, style='#FFFFFF', weight=900, align='center',
                shadow=0)


# ======================= counter =======================
@shot('count')
def count_shot(c, b, f, ctx):
    if b.get('bg') and L.exists(b['bg']):
        bg_blur(c, b['bg'], b, f, gain=0.28)
    else:
        L.stage(c)
    d = f - b['f0']
    dur = b.get('dur', 26)
    k = M.ease_out_cubic((d + 1) / dur)
    v = int(round(b.get('from', 0) + (b['to'] - b.get('from', 0)) * k))
    txt = b.get('fmt', '{:,}').format(v)
    cap = b.get('cap', 0.24 * H)
    pulse = 1 + 0.05 * max(0.0, 1 - (d - dur) / 6) if d >= dur else 1.0
    c.save()
    c.translate(W / 2, 0.52 * H)
    c.scale(pulse, pulse)
    c.translate(-W / 2, -0.52 * H)
    TY.draw(c, b.get('prefix', '') + txt, W / 2, 0.52 * H + cap / 2, cap, style=b.get('style', 'white'), weight=900, align='center')
    c.restore()
    if b.get('label'):
        lc = 0.06 * H
        if TY.width(b['label'], lc, 900) > 0.9 * W:
            lc *= 0.9 * W / TY.width(b['label'], lc, 900)
        TY.draw(c, b['label'], W / 2, 0.52 * H + cap / 2 + 0.13 * H, lc, style=b.get('label_style', 'red'), weight=900,
                align='center')
    ctx['occ'].append(('frame', skia.Rect(0.1 * W, 0.2 * H, 0.9 * W, 0.85 * H)))


def draw_timer(c, o, f):
    """Speedrun timer (bottom-right pill, tabular digits so it never jitters). Visible only when it is the joke:
    for ~2.6 s after 'speedrun', then again (stopped, flashing) at the punchline."""
    stop = o.get('stop', 10 ** 9)
    if not (f < o['f0'] + 78 or f >= stop - 2):
        return None
    t = max(0.0, (min(f, stop) - o['f0']) / FPS)
    s = f'{int(t // 60):02d}:{t % 60:06.3f}'
    cap = 0.05 * H
    cell = TY.width('0', cap, 800) * 1.08
    colw = TY.width(':', cap, 800) * 1.4
    wsum = sum(colw if ch in ':.' else cell for ch in s)
    x1, y1 = W - 0.05 * W, H - 0.06 * H
    rect = skia.Rect(x1 - wsum - 60, y1 - cap - 92, x1, y1)
    a = min(1.0, (f - o['f0'] + 1) / 4) if f < stop - 2 else min(1.0, (f - stop + 3) / 3)
    if f < o['f0'] + 78:
        a *= min(1.0, (o['f0'] + 78 - f) / 4)
    O.pill(c, rect, '#0A0A0A', 0.88 * a)
    TY.draw(c, o.get('label', 'SPEEDRUN'), rect.left() + 30, rect.top() + 46, 0.026 * H, style='red', weight=800, shadow=0)
    x = rect.left() + 30
    stopped = f >= o.get('stop', 10 ** 9)
    col = '#7CFF6B' if not stopped else ('#FFFFFF' if (f // 6) % 2 else '#7CFF6B')
    for ch in s:
        wd = colw if ch in ':.' else cell
        TY.draw(c, ch, x + wd / 2, y1 - 26, cap, style=col, weight=800, align='center', shadow=0)
        x += wd
    return rect


# ======================= subscription card (Attila: "charging Rome a subscription") =======================
@shot('sub')
def sub_shot(c, b, f, ctx):
    bg_blur(c, b.get('bg', 'solidus'), b, f, gain=0.22)
    d = f - b['f0']
    s, a = M.pop(d, 0.85, frames=5)
    cw, ch = 0.56 * W, 0.66 * H
    r = skia.Rect(W / 2 - cw / 2, H / 2 - ch / 2, W / 2 + cw / 2, H / 2 + ch / 2)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    L.soft_shadow(c, r, 34, (0, 24), 0.9, 28)
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(0, r.top()), (0, r.bottom())], [rgb('#1C1C1C'), rgb('#0E0E0E')]))
    c.drawRRect(skia.RRect.MakeRectXY(r, 28, 28), p)
    bp = skia.Paint(AntiAlias=True, Color=rgb('#E0393E'), Style=skia.Paint.kStroke_Style, StrokeWidth=4)
    c.drawRRect(skia.RRect.MakeRectXY(r, 28, 28), bp)
    y = r.top() + 0.13 * H
    TY.draw(c, b.get('brand', 'HUN+'), W / 2, y, 0.09 * H, style='red', weight=900, align='center')
    y += 0.115 * H
    TY.draw(c, b.get('plan', 'PREMIUM PLAN'), W / 2, y, 0.045 * H, style='silver', weight=800, align='center', shadow=0)
    y += 0.12 * H
    TY.draw(c, b['price'], W / 2, y, 0.058 * H, style='white', weight=900, align='center')
    y += 0.075 * H
    TY.draw(c, b.get('per', 'PER YEAR · BILLED TO ROME'), W / 2, y, 0.034 * H, style='#9A9A9A', weight=700, align='center', shadow=0)
    btn = skia.Rect(W / 2 - 0.15 * W, r.bottom() - 0.165 * H, W / 2 + 0.15 * W, r.bottom() - 0.07 * H)
    lit = f >= b.get('btn_at', 10 ** 9)
    bpaint = skia.Paint(AntiAlias=True, Color=rgb('#E0393E' if not lit else '#3A3A3A'))
    c.drawRRect(skia.RRect.MakeRectXY(btn, btn.height() / 2, btn.height() / 2), bpaint)
    TY.draw(c, b.get('button', 'SUBSCRIBED'), W / 2, btn.centerY() + 0.02 * H, 0.04 * H, style='white', weight=900, align='center', shadow=0)
    c.restore()
    ctx['occ'].append(('frame', r))


# ======================= album cover gag =======================
@shot('album')
def album_shot(c, b, f, ctx):
    L.stage(c)
    d = f - b['f0']
    side = 0.62 * H
    s = (1.0 + 0.012 * d / FPS) * M.pop(d, 0.9, 5)[0]
    r = skia.Rect(W / 2 - side / 2 * s, H / 2 - side / 2 * s, W / 2 + side / 2 * s, H / 2 + side / 2 * s)
    L.soft_shadow(c, r, 30, (0, 22), 0.9, 4)
    c.save()
    c.clipRect(r)
    img = L.plate(b['img'], int(side), int(side), tuple(b.get('focus', (0.5, 0.5))), b.get('zoom', 1.0), sat=0.0, contrast=1.5,
                  gain=0.55, oversize=1.0)
    c.drawImageRect(img, r, L.SAMPLING)
    red = skia.Paint(AntiAlias=True, Color=rgb('#8E0A0A'))
    red.setBlendMode(skia.BlendMode.kMultiply)
    c.drawRect(r, red)
    c.restore()
    TY.draw(c, b['band'], r.centerX(), r.top() + side * s * 0.22, side * s * 0.16, style='white', weight=900, align='center',
            tracking=0.12, glow=('#FF2A2A', 18, 0.6))
    TY.draw(c, b['title'], r.centerX(), r.bottom() - side * s * 0.08, side * s * 0.06, style='silver', weight=800, align='center',
            tracking=0.2)
    if b.get('sticker'):
        O.stamp(c, b['sticker'], r.right() - 40, r.bottom() - 120, d - 12, cap=34, angle=10, color='#FFD23F')
    ctx['occ'].append(('frame', r))


# ======================= fleet formation (crane wing) =======================
@shot('formation')
def formation_shot(c, b, f, ctx):
    if b.get('bg') and L.exists(b['bg']):
        bg_photo_full(c, b['bg'], b, f, blur=3.0, gain=0.42, sat=0.6, rate=0.002)
    else:
        L.stage(c)
    d = f - b['f0']
    wrap_at = b.get('wrap', b['f0'] + 30)
    wipe_at = b.get('wipe', 10 ** 9)
    cx, cy = W * 0.62, H * 0.58
    # Japanese fleet: tight cluster that is lured forward (moves left), then destroyed
    rng = np.random.default_rng(2)
    lure = M.ease_in_out_cubic((d + 1) / 40) * 220
    for k in range(14):
        ox, oy = rng.uniform(-230, 230), rng.uniform(-150, 150)
        x, y = cx + ox - lure, cy + oy
        if f >= wipe_at:
            dd = f - wipe_at - k
            if dd >= 0:
                sc, al = M.pop_out(dd, 5)
                if al <= 0:
                    continue
                raw_prop(c, 'jp_ship', x, y, 62 * sc, alpha=int(255 * al), flip=True)
                continue
        raw_prop(c, 'jp_ship', x, y + math.sin(f / 8 + k) * 2, 62, flip=True)
    # Korean ships slide from a line into a U ("crane wing") around the cluster
    n = 11
    k_wrap = M.ease_in_out_cubic((f - wrap_at + 1) / 34) if f >= wrap_at else 0.0
    for i in range(n):
        u = (i / (n - 1)) * 2 - 1
        line_x, line_y = 0.18 * W, cy + u * 0.36 * H
        ang = u * 1.25
        u_x = (cx - lure) + math.cos(math.pi - ang) * 470 + 160
        u_y = cy + math.sin(ang) * 470 * 0.85
        x = line_x + (u_x - line_x) * k_wrap
        y = line_y + (u_y - line_y) * k_wrap
        raw_prop(c, 'turtle_ship', x, y + math.sin(f / 9 + i) * 2, 60)
    if f >= wrap_at:
        TY.draw(c, 'CRANE WING', 0.16 * W, 0.17 * H, 0.06 * H, style='red', weight=900, alpha=int(255 * min(1.0, (f - wrap_at + 1) / 5)))
    ctx['occ'].append(('frame', skia.Rect(0.1 * W, 0.2 * H, 0.95 * W, 0.95 * H)))


# ======================= gallery (recap: five portraits light up) =======================
@shot('gallery')
def gallery_shot(c, b, f, ctx):
    L.stage(c)
    n = len(b['people'])
    pw = 0.168 * W
    ph = pw * 1.3
    gap = 0.02 * W
    x0 = W / 2 - (n * pw + (n - 1) * gap) / 2
    cy = 0.44 * H
    for i, p in enumerate(b['people']):
        cx = x0 + pw / 2 + i * (pw + gap)
        lit = f >= p['at']
        d = f - p['at']
        r = skia.Rect(cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2)
        s = 1.0 + (0.06 * max(0.0, 1 - (d + 1) / 6) if lit and d < 6 else 0.0)
        r = skia.Rect(cx - pw / 2 * s, cy - ph / 2 * s, cx + pw / 2 * s, cy + ph / 2 * s)
        L.soft_shadow(c, r, 16, (0, 10), 0.8, 4)
        img = L.plate(p['img'], int(pw), int(ph), tuple(p.get('focus', (0.5, 0.4))), p.get('zoom', 1.0), oversize=1.0,
                      sat=0.88 if lit else 0.0, gain=1.0 if lit else 0.35)
        c.drawImageRect(img, r, L.SAMPLING)
        TY.draw(c, f'#{i + 1}', r.left() + 18, r.top() + 0.055 * H, 0.04 * H, style='red' if lit else '#555555', weight=900)
        if lit:
            lc = min([0.036 * H] + [0.036 * H * (pw * 0.94) / TY.width(ln, 0.036 * H, 800) for ln in p['label']
                                    if TY.width(ln, 0.036 * H, 800) > pw * 0.94])
            for k, ln in enumerate(p['label']):
                TY.draw(c, ln, cx, r.bottom() + 0.065 * H + k * lc * 1.5, lc, style='white', weight=800, align='center',
                        alpha=int(255 * min(1.0, (d + 1) / 4)))
    ctx['occ'].append(('frame', skia.Rect(x0, cy - ph / 2, W - x0, cy + ph / 2 + 0.15 * H)))


# ======================= comment card (mid-roll CTA) =======================
@shot('comment')
def comment_shot(c, b, f, ctx):
    L.stage(c)
    d = f - b['f0']
    s, a = M.pop(d, 0.8, frames=5)
    cw, ch = 0.62 * W, 0.30 * H
    r = skia.Rect(W / 2 - cw / 2, 0.42 * H - ch / 2, W / 2 + cw / 2, 0.42 * H + ch / 2)
    c.save()
    c.translate(W / 2, r.centerY())
    c.scale(s, s)
    c.translate(-W / 2, -r.centerY())
    L.soft_shadow(c, r, 28, (0, 18), 0.85, 36)
    c.drawRRect(skia.RRect.MakeRectXY(r, 36, 36), skia.Paint(AntiAlias=True, Color=rgb('#F4F4F4')))
    tail = skia.Path()
    tail.moveTo(r.left() + 120, r.bottom() - 2)
    tail.lineTo(r.left() + 90, r.bottom() + 60)
    tail.lineTo(r.left() + 200, r.bottom() - 2)
    tail.close()
    c.drawPath(tail, skia.Paint(AntiAlias=True, Color=rgb('#F4F4F4')))
    c.drawCircle(r.left() + 110, r.centerY(), 0.075 * H, skia.Paint(AntiAlias=True, Color=rgb('#E0393E')))
    RH.draw_character(c, r.left() + 110, r.centerY() + 6, 0.042 * H, 'idle', 'grin', HOST, show_rim=False)
    n = len(b['text'])
    k = int(min(n, max(0, (d - 6)) * 0.9)) if not b.get('instant') else n
    TY.draw(c, b['text'][:k], r.left() + 230, r.centerY() + 0.04 * H, 0.09 * H, style='#0B0B0B', weight=900, shadow=0)
    if k < n and (d // 8) % 2 == 0:
        x = r.left() + 230 + TY.width(b['text'][:k], 0.09 * H, 900) + 10
        c.drawRect(skia.Rect(x, r.centerY() - 0.05 * H, x + 8, r.centerY() + 0.04 * H), skia.Paint(Color=rgb('#0B0B0B')))
    c.restore()
    ctx['occ'].append(('frame', r))


def draw_head(c, pal, x, y, R, expr='ko', rot=0.0):
    """A character's head on its own (stage prop gags)."""
    from engine.costumes import hair_extra, facial_hair
    st = pal
    parts = []
    h = st.get('hair')
    hb, hf = ([], RH.hair_parts(st)) if h in ('slick', 'short', None) else hair_extra(h, st.get('hair_color', '#2A211C'))
    hp = skia.Path()
    hp.addCircle(0, 0, 1.0)
    parts += hb + [RH.Part(hp, fill=RH.HEAD_FILL)] + hf + RH.face_parts(expr, (0.0, 0.0))
    if st.get('facial'):
        parts += facial_hair(st['facial'], st.get('facial_color', st.get('hair_color', '#2A211C')))
    RH.render_parts(c, parts, x, y, R, rot=rot, show_rim=True)
