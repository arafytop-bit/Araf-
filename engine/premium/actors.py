"""Actors: round-head characters and props with entrances, exits, cycles and secondary motion.

Actor dict (all frames absolute; T() triggers are resolved before rendering):
  pal, x, y (feet y px), R (head radius px), flip, z
  pose: 'idle' | [(frame, pose), ...]        expr: 'talk' | [(frame, expr), ...]
  enter: dict(kind='walk'|'run'|'pop'|'drop'|'slide'|'rise'|'cut', at=frame, dur=frames, frm=x or (x, y))
  exit:  dict(kind='walk'|'run'|'pop'|'fall'|'fly'|'cut', at=frame, dur=frames, to=x or (x, y))
  acts:  [dict(kind='fall'|'hop'|'shake'|'spin'|'bob'|'die'|'lie', at=frame, ...)]
  rot (deg, static), lie=True (lying on the ground)
Returns the head box so the layout engine knows where faces are.
"""
import math

import skia

from engine import roundhead as RH
from engine.premium import poses  # noqa: F401  (registers run/cheer/swing/drum/hold/fall)
from engine.premium import motion as M
from engine.premium import look as L

HEAD_TO_FEET = 3.22          # head centre -> sole, in R


def at_time(seq, f, default=None):
    """Value of a keyed sequence [(frame, value), ...] (or a constant) at frame f."""
    if not isinstance(seq, list):
        return seq if seq is not None else default
    v = default if default is not None else seq[0][1]
    for f0, val in seq:
        if f0 is None or f >= f0:
            v = val
    return v


def blinked(expr, f, seed=0):
    """Blink every ~3.3 s for 3 frames (keeps holds alive); never on closed/x eyes."""
    if expr.endswith('_blink') or RH.EXPR.get(expr, ('dot',))[0] in ('closed', 'x', 'none', 'happy'):
        return expr
    period = 97 + (seed * 37) % 23
    if (f + seed * 13) % period < 3 and (expr + '_blink') in RH.EXPR:
        return expr + '_blink'
    return expr


def actor_state(a, f):
    """Position/transform of an actor at frame f -> dict or None (not visible)."""
    x, y, R = a['x'], a['y'], a['R']
    pose = at_time(a.get('pose', 'idle'), f, 'idle')
    expr = at_time(a.get('expr', 'talk'), f, 'talk')
    phase = 0.0
    sx = sy = 1.0
    rot = a.get('rot', 0.0)
    alpha = 1.0
    dx = dy = 0.0
    flip = a.get('flip', False)
    en = a.get('enter')
    if en:
        df = f - en['at']
        if df < 0:
            return None
        kind = en.get('kind', 'pop')
        dur = en.get('dur', {'walk': 36, 'run': 22, 'slide': 9, 'drop': 13, 'rise': 10, 'pop': 5}.get(kind, 6))
        if kind in ('walk', 'run') and df < dur:
            x0 = en['frm'] if not isinstance(en['frm'], tuple) else en['frm'][0]
            k = M.ease_out_cubic((df + 1) / dur) if kind == 'walk' else M.ease_out_cubic((df + 1) / dur) ** 0.8
            dx = (x0 - x) * (1 - k)
            pose = kind
            phase = M.flip_phase(f, fps_draw=5.0 if kind == 'walk' else 7.5, drawings=4, offset=a.get('seed', 0) * 3)
            flip = x0 > x
            dy = -abs(math.sin(phase)) * R * (0.05 if kind == 'walk' else 0.12)
            if kind == 'run':
                rot += -7 if not flip else 7
        elif kind == 'slide' and df < dur:
            x0 = en['frm'] if not isinstance(en['frm'], tuple) else en['frm'][0]
            dx = M.slide(df, x0 - x, frames=dur)
        elif kind == 'drop':
            dy = M.drop(df, en.get('height', 700), frames=dur)
            if 0 <= df - int(dur * 0.55) < 4:              # squash on landing
                q = 1 - abs(df - int(dur * 0.55) - 1.5) / 2.5
                sy, sx = 1 - 0.10 * q, 1 + 0.08 * q
        elif kind == 'rise' and df < dur:
            dy = (1 - M.ease_out_back((df + 1) / dur, 1.3)) * R * 4.5
        elif kind == 'pop':
            s, al = M.pop(df, 0.5, frames=4)
            sx = sy = s
            alpha = al
    ex = a.get('exit')
    if ex:
        df = f - ex['at']
        if df >= 0:
            kind = ex.get('kind', 'pop')
            dur = ex.get('dur', {'walk': 30, 'run': 18, 'pop': 5, 'fall': 9, 'fly': 14}.get(kind, 6))
            if df >= dur and kind in ('walk', 'run', 'pop', 'fly'):
                return None
            if kind in ('walk', 'run'):
                x1 = ex['to'] if not isinstance(ex['to'], tuple) else ex['to'][0]
                k = M.ease_in_cubic((df + 1) / dur) if kind == 'walk' else ((df + 1) / dur) ** 1.6
                dx = (x1 - x) * k
                pose = kind
                phase = M.flip_phase(f, fps_draw=5.0 if kind == 'walk' else 7.5)
                flip = x1 > x
                dy = -abs(math.sin(phase)) * R * (0.05 if kind == 'walk' else 0.12)
                if kind == 'run':
                    rot += -7 if not flip else 7
            elif kind == 'pop':
                s, al = M.pop_out(df, frames=dur)
                sx = sy = s
                alpha = al
            elif kind == 'fly':
                k = (df + 1) / dur
                tx, ty = ex.get('to', (2400, -600))
                dx, dy = (tx - x) * k * k, (ty - y) * k * k
                rot += 720 * k * k
    lie = a.get('lie', False)
    for act in a.get('acts', []):
        df = f - act['at']
        if df < 0:
            continue
        k = act['kind']
        if k in ('fall', 'die'):
            dur = act.get('dur', 9)
            t = min(1.0, (df + 1) / dur)
            ang = 90 * M.ease_in_cubic(t) if df < dur else 90 + 6 * M.decay_osc((df - dur) / 30, 3.0, 8.0)
            rot += -ang if not act.get('back') else ang
            dy -= 0.9 * R * min(1.0, ang / 90)
            if df < dur:
                pose = 'fall'
            if k == 'die' and df >= dur // 2:
                expr = act.get('expr', 'ko')
        elif k == 'lie':
            lie = True
        elif k == 'hop':
            dur = act.get('dur', 9)
            if df < dur:
                t = (df + 1) / dur
                dy -= 4 * t * (1 - t) * R * act.get('h', 0.45)
            elif df < dur + 3:
                q = 1 - (df - dur) / 3
                sy, sx = 1 - 0.08 * q, 1 + 0.06 * q
        elif k == 'shake' and df < act.get('dur', 14):
            dx += math.sin(df * 2.9) * R * 0.05 * (1 - df / act.get('dur', 14))
        elif k == 'spin' and df < act.get('dur', 12):
            sx *= math.cos(math.pi * 2 * (df + 1) / act.get('dur', 12))
        elif k == 'bob' and df < 6:
            q = math.sin(math.pi * (df + 1) / 6)
            sy, sx = sy * (1 - 0.04 * q), sx * (1 + 0.03 * q)
        elif k == 'pose':
            pose = act['pose']
        elif k == 'expr':
            expr = act['expr']
        elif k == 'move':
            dur = act.get('dur', 12)
            t = M.ease_in_out_cubic((df + 1) / dur)
            tx, ty = act['to']
            dx += (tx - x) * t
            dy += (ty - y) * t
        elif k == 'exitcut':
            return None
    if lie:
        rot += -90
        dy -= 0.9 * R
    if pose == 'drum':
        phase = 2 * math.pi * f / 14.0
    elif pose in ('walk', 'run') and phase == 0.0:
        phase = M.flip_phase(f, fps_draw=5.0 if pose == 'walk' else 7.5, drawings=4, offset=a.get('seed', 0) * 3)
        dy -= abs(math.sin(phase)) * R * (0.05 if pose == 'walk' else 0.12)
    if pose in ('idle', 'hips', 'point', 'chin', 'shrug', 'cheeks', 'wave', 'inspect', 'hold', 'cheer', 'swing'):
        sy *= M.breathe(f, seed=a.get('seed', 0))
    expr = blinked(expr, f, a.get('seed', 0))
    return dict(x=x + dx, y=y + dy, R=R, pose=pose, expr=expr, phase=phase, sx=sx, sy=sy, rot=rot, alpha=alpha, flip=flip)


def draw_actor(c, a, f, shadow=True, rim=True):
    st = actor_state(a, f)
    if st is None or st['alpha'] <= 0.01:
        return None
    x, y, R = st['x'], st['y'], st['R']
    head_cx, head_cy = x, y - HEAD_TO_FEET * R
    if shadow and abs(st['rot']) < 30 and not a.get('no_shadow'):
        air = max(0.0, a['y'] - y)          # lifted off the ground -> lighter, smaller shadow
        k = max(0.25, 1 - air / (R * 3))
        L.contact_shadow(c, x, a['y'] + R * 0.12, R * 2.4 * k, alpha=0.45 * k * st['alpha'])
    c.save()
    c.translate(x, y)                       # pivot at the feet
    if st['rot']:
        c.rotate(st['rot'])
    c.scale(st['sx'], st['sy'])
    c.translate(-x, -y)
    RH.draw_character(c, head_cx, head_cy, R, st['pose'], st['expr'], a['pal'], flip=st['flip'], phase=st['phase'],
                      alpha=int(255 * st['alpha']), show_rim=rim, look=a.get('look'))
    c.restore()
    if abs(st['rot']) > 45:                 # lying: head is beside the feet
        ang = math.radians(st['rot'])
        hx = x + math.sin(-ang) * -HEAD_TO_FEET * R * -1
        hy = y - math.cos(ang) * HEAD_TO_FEET * R
        return skia.Rect(hx - 1.3 * R, hy - 1.3 * R, hx + 1.3 * R, hy + 1.3 * R)
    return skia.Rect(head_cx - 1.25 * R, head_cy - 1.6 * R, head_cx + 1.25 * R, y)


def prop_state(p, f):
    en = p.get('enter')
    sx = 1.0
    alpha = 1.0
    dx = dy = 0.0
    rot = p.get('rot', 0.0)
    if en:
        df = f - en['at']
        if df < 0:
            return None
        kind = en.get('kind', 'pop')
        dur = en.get('dur', 5 if kind == 'pop' else 12)
        if kind == 'pop':
            sx, alpha = M.pop(df, 0.5)
        elif kind == 'drop':
            dy = M.drop(df, en.get('height', 700), frames=dur)
        elif kind == 'fly':
            if en.get('until') is not None:
                dur = max(1, en['until'] - en['at'])
            k = (M.ease_in_out_cubic((df + 1) / dur) if en.get('until') is not None else M.ease_out_expo((df + 1) / dur)) if df < dur else 1.0
            fx, fy = en['frm']
            dx, dy = (fx - p['x']) * (1 - k), (fy - p['y']) * (1 - k)
        elif kind == 'slide':
            fx = en['frm']
            dx = M.slide(df, fx - p['x'], frames=dur)
    ex = p.get('exit')
    if ex:
        df = f - ex['at']
        if df >= 0:
            kind = ex.get('kind', 'pop')
            if kind == 'cut':
                return None
            dur = ex.get('dur', 5)
            if df >= dur:
                return None
            if kind == 'pop':
                sx, alpha = M.pop_out(df, frames=dur)
            elif kind == 'fly':
                k = ((df + 1) / dur) ** 2
                tx, ty = ex['to']
                dx, dy = (tx - p['x']) * k, (ty - p['y']) * k
    for act in p.get('acts', []):
        df = f - act['at']
        if df < 0:
            continue
        if act['kind'] == 'shake' and df < act.get('dur', 12):
            dx += math.sin(df * 3.1) * p['size'] * 0.06 * (1 - df / act.get('dur', 12))
        elif act['kind'] == 'bob':
            dy += math.sin((f - act['at']) / 30 * 2 * math.pi * act.get('hz', 0.6)) * p['size'] * act.get('amp', 0.04)
        elif act['kind'] == 'spin':
            rot += act.get('speed', 6) * df
        elif act['kind'] == 'move':
            dur = act.get('dur', 12)
            t = M.ease_in_out_cubic((df + 1) / dur)
            tx, ty = act['to']
            dx += (tx - p['x']) * t
            dy += (ty - p['y']) * t
        elif act['kind'] == 'hit' and df < 6:
            sx *= 1 + 0.12 * math.sin(math.pi * (df + 1) / 6)
    return dict(x=p['x'] + dx, y=p['y'] + dy, s=sx, alpha=alpha, rot=rot)


def draw_prop(c, p, f, shadow=False):
    from engine.props import draw_prop as dp
    st = prop_state(p, f)
    if st is None or st['alpha'] <= 0.01:
        return None
    size = p['size'] * st['s']
    if shadow:
        L.contact_shadow(c, st['x'], p.get('ground', p['y'] + p['size'] * 0.9), p['size'] * 2.0, alpha=0.4 * st['alpha'])
    kw = dict(p.get('kw', {}))
    t = (f - (p.get('enter') or {}).get('at', 0)) / 30.0
    dp(c, p['name'], st['x'], st['y'], size, t=t, rot=st['rot'], alpha=int(255 * st['alpha']), flip=p.get('flip', False),
       rim=p.get('rim', True), **kw)
    if p.get('text'):
        from engine.premium import typo as TY
        lines = p['text'] if isinstance(p['text'], list) else [p['text']]
        cap = p.get('tcap', size * 0.16)
        y0 = st['y'] + p.get('ty', 0) * size - (len(lines) - 1) * cap * 0.7
        for k, ln in enumerate(lines):
            TY.draw(c, ln, st['x'], y0 + k * cap * 1.4 + cap / 2, cap * st['s'], style=p.get('tstyle', '#3A3A3A'), weight=900,
                    align='center', alpha=int(255 * st['alpha']), shadow=0)
    return skia.Rect(st['x'] - size * 1.5, st['y'] - size * 1.5, st['x'] + size * 1.5, st['y'] + size * 1.5)
