"""Retention layer for the video: camera punches/shakes synced to the sound design, the recurring DEATH stamp,
the 1-to-5 entry tracker, host blinks/bounces/push-ins, drifting dust on the black stage, teaser flash-forwards."""
import math
import os
import random

import numpy as np
import skia

from engine.core import W, H, FPS, paint, rgb, ease_out_cubic
from engine.text import draw_text, size_for_cap, text_width
from engine.props import draw_prop

# ---------------------------------------------------------------- dust particles
_rng = np.random.default_rng(21)
_N = 46
_P = dict(x=_rng.uniform(0, W, _N), y=_rng.uniform(0, H, _N), vx=_rng.uniform(-0.25, 0.25, _N), vy=_rng.uniform(-0.55, -0.12, _N),
          r=_rng.uniform(1.0, 3.0, _N), ph=_rng.uniform(0, 6.28, _N), sp=_rng.uniform(0.02, 0.07, _N))
_dust_paint = skia.Paint(AntiAlias=True)
_dust_paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.3))
CUR_F = [0]


def dust(c, f=None):
    f = CUR_F[0] if f is None else f
    x = (_P['x'] + _P['vx'] * f + 18 * np.sin(_P['ph'] + f * 0.011)) % W
    y = (_P['y'] + _P['vy'] * f) % H
    a = 14 + 30 * (0.5 + 0.5 * np.sin(_P['ph'] + f * _P['sp']))
    for xi, yi, ri, ai in zip(x, y, _P['r'], a):
        _dust_paint.setColor(skia.Color(235, 228, 210, int(ai)))
        c.drawCircle(float(xi), float(yi), float(ri), _dust_paint)


def install_background_hook(shots_module, core_draw_background):
    def bg(c):
        core_draw_background(c)
        dust(c)
    shots_module.draw_background = bg
    return bg


# ---------------------------------------------------------------- events
CAUSES = {'Harald': ('HARALD HARDRADA', 'CAUSE: ARROW. ARMOR: AT THE SHIPS'), 'Attila': ('ATTILA THE HUN', 'CAUSE: NOSEBLEED'),
          'Crassus': ('MARCUS LICINIUS CRASSUS', 'CAUSE: "PEACE TALKS"'), 'Arrichion': ('ARRICHION', 'CAUSE: CHOKEHOLD. RESULT: WON'),
          'Yi Sun-sin': ('YI SUN-SIN', 'CAUSE: BULLET. RESULT: WON THE WAR')}
SHAKE = {'cannon': ('shake', 0.9), 'gunshot': ('shake', 1.0), 'door_crash': ('shake', 0.7), 'ship_crash': ('shake', 0.75),
         'metal_clang': ('shake', 0.4), 'stone_slam': ('shake', 0.55), 'wood_crack': ('shake', 0.45), 'bone_crack': ('punch', 0.45),
         'punch': ('punch', 0.55), 'thud': ('shake', 0.35), 'impact': ('punch', 0.5), 'arrow_hit': ('shake', 0.4),
         'text_hit': ('punch', 0.16), 'sub_drop': ('punch', 0.22), 'boxing_bell': ('punch', 0.2)}
STING_CAM = {'braam': [(0.0, 'shake', 0.65)], 'boss': [(0.33, 'punch', 0.6)], 'dun3': [(0.0, 'punch', 0.35), (0.34, 'punch', 0.35), (0.68, 'punch', 0.55)],
             'metal': [(k * 0.25, 'shake', 0.42) for k in range(9)], 'rimshot': [(0.36, 'punch', 0.3)], 'fanfare': [(0.45, 'punch', 0.3)],
             'title_hit': [(0.0, 'shake', 0.35)]}


def color_matrix(m, dim=1.0):
    """4x5 colour matrix: desaturate by m (0..1) and scale brightness by dim."""
    lum = (0.2126, 0.7152, 0.0722)
    rows = []
    for r in range(3):
        rows += [((1 - m) * (1.0 if r == c else 0.0) + m * lum[c]) * dim for c in range(3)] + [0.0, 0.0]
    return rows + [0.0, 0.0, 0.0, 1.0, 0.0]


class Retention:
    def __init__(self, timeline, calls, overlays, B):
        import sound_design as SD
        self.cam = []
        ev = SD.auto_sfx(timeline, calls, overlays) + SD.story_sfx()
        for e in ev:
            if e['name'] in SHAKE:
                kind, a = SHAKE[e['name']]
                g = 10 ** ((e.get('gain', -10) + 8) / 40)          # louder sounds hit the camera harder
                self.cam.append((int(round((e['t'] - e.get('lead', 0.0)) * FPS)) + (int(0.36 * FPS) if e['name'] == 'arrow_hit' else 0),
                                 kind, min(1.2, a * g)))
        cur = 0
        for trig, kind, style, o in SD.STINGS:
            try:
                t, i = SD.resolve(o.get('at', trig), cur)
            except KeyError:
                t, i = SD.resolve(o.get('at', trig), 0)
            for dt, k2, a in STING_CAM.get(kind, []):
                self.cam.append((int(round((t + dt) * FPS)), k2, a))
        for b in timeline:
            if b['kind'] == 'title':
                self.cam.append((b['f0'], 'shake', 0.35))
        self.deaths = []
        for n, (who, t) in enumerate(SD.death_times()):
            f0 = int(round(t * FPS))
            self.deaths.append((f0, n + 1, who))
            self.cam.append((f0 + 3, 'shake', 1.0))
        self.cam.sort()
        self._cam_f = np.array([c[0] for c in self.cam])
        # entry sections for the tracker
        titles = [b for b in timeline if b['kind'] == 'title']
        mid = [s for s in B.SENTS if s['section'] == 'midroll']
        outro = [s for s in B.SENTS if s['section'] == 'outro'][0]['start']
        mid0, mid1 = (mid[0]['start'], mid[-1]['end']) if mid else (None, None)
        self.sections = []
        for k, t in enumerate(titles):
            a = t['f1']
            z = titles[k + 1]['f0'] if k + 1 < len(titles) else int(outro * FPS)
            if mid0 is not None and t['f0'] < mid0 * FPS < z:
                z = int(mid0 * FPS)
            self.sections.append((a, z, k + 1, t['trigger'].rstrip('.').upper()))
        self.n_entries = len(titles)

    # ------------------------------------------------ camera
    def camera(self, f):
        s, dx, dy, rot = 1.0, 0.0, 0.0, 0.0
        lo = np.searchsorted(self._cam_f, f - 26)
        hi = np.searchsorted(self._cam_f, f, side='right')
        for f0, kind, a in self.cam[lo:hi]:
            k = f - f0
            if kind == 'punch':
                s += 0.055 * a * math.exp(-k / 4.5)
            else:
                r = random.Random(f0 * 131 + k)
                amp = 15 * a * math.exp(-k / 5.5)
                dx += amp * (r.random() * 2 - 1)
                dy += amp * (r.random() * 2 - 1)
                rot += 0.7 * a * math.exp(-k / 5.5) * (r.random() * 2 - 1)
                s += 0.02 * a * math.exp(-k / 6)
        return s, dx, dy, rot

    def apply_camera(self, c, surf, f):
        s, dx, dy, rot = self.camera(f)
        if abs(s - 1) < 1e-4 and abs(dx) < 0.05 and abs(dy) < 0.05 and abs(rot) < 0.005:
            return
        s = max(s, 1 + 2.2 * max(abs(dx), abs(dy)) / H + abs(rot) * 0.035)
        snap = surf.makeImageSnapshot()
        c.clear(skia.ColorBLACK)
        c.save()
        c.translate(W / 2 + dx, H / 2 + dy)
        c.rotate(rot)
        c.scale(s, s)
        c.translate(-W / 2, -H / 2)
        c.drawImage(snap, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()

    # ------------------------------------------------ death stamp
    def death_overlay(self, c, surf, f):
        for f0, n, who in self.deaths:
            k = f - f0
            if not 0 <= k < 50:
                continue
            fade_in = min(1.0, (k + 1) / 3.0)
            fade_out = min(1.0, (50 - k) / 8.0)
            amt = fade_in * fade_out
            snap = surf.makeImageSnapshot()
            cm = color_matrix(0.75 * amt, 1 - 0.38 * amt)
            p = skia.Paint(ColorFilter=skia.ColorFilters.Matrix(cm))
            c.clear(skia.ColorBLACK)
            c.drawImage(snap, 0, 0, skia.SamplingOptions(), p)
            sh = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.62, [skia.Color(0, 0, 0, 0), skia.Color(150, 0, 0, int(120 * amt))])
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
            self._stamp(c, n, who, k, fade_out)
            if k < 2:
                c.drawRect(skia.Rect(0, 0, W, H), paint('#FFFFFF', alpha=int(110 * (1 - k / 2))))

    def _stamp(self, c, n, who, k, alpha):
        name, cause = CAUSES.get(who, (who.upper(), ''))
        u = min(1.0, k / 4.0)
        sc = 1.9 - 0.9 * (u ** 2)
        if k >= 4:
            sc = 1.0 + 0.04 * math.exp(-(k - 4) / 3) * math.cos((k - 4) * 1.3)
        a = int(255 * min(1.0, (k + 1) / 3) * alpha)
        c.save()
        c.translate(W / 2, H / 2 - 10)
        c.rotate(-8)
        c.scale(sc, sc)
        red = '#E0262C'
        t1 = f'DEATH #{n}'
        s1 = size_for_cap(96)
        cap2 = 40 if len(name) < 18 else 32
        s2 = size_for_cap(cap2)
        s3 = size_for_cap(22)
        w1, w2, w3 = text_width(t1, s1, 0.04), text_width(name, s2, 0.05), text_width(cause, s3, 0.08)
        bw, bh = max(w1, w2, w3) + 130, 330
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-bw / 2, -bh / 2, bw / 2, bh / 2), 28, 28), paint('#0E0E0E', alpha=int(a * 0.6)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-bw / 2, -bh / 2, bw / 2, bh / 2), 28, 28), paint(red, stroke=14, alpha=a))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-bw / 2 + 20, -bh / 2 + 20, bw / 2 - 20, bh / 2 - 20), 18, 18),
                    paint(red, stroke=4, alpha=a))
        draw_text(c, t1, -w1 / 2, -22, s1, style=red, tracking=0.04, alpha=a, shadow=False, grunge=True)
        draw_text(c, name, -w2 / 2, 48, s2, style='#F2F2F2', tracking=0.05, alpha=a, shadow=False, grunge=False)
        draw_text(c, cause, -w3 / 2, 106, s3, style=red, tracking=0.08, alpha=a, shadow=False, grunge=False)
        c.drawCircle(-bw / 2 + 6, -bh / 2 + 6, 40, paint('#0E0E0E', alpha=a))
        c.drawCircle(-bw / 2 + 6, -bh / 2 + 6, 40, paint(red, stroke=8, alpha=a))
        draw_prop(c, 'icon', -bw / 2 + 6, -bh / 2 + 6, 46, kind='skull', alpha=a)
        c.restore()

    # ------------------------------------------------ entry tracker
    def hud(self, c, f):
        for a, z, n, name in self.sections:
            if not a <= f < z:
                continue
            fade = min(1.0, (f - a) / 8.0, (z - f) / 8.0)
            al = int(255 * fade)
            x0, y0, gap, r = 54, 54, 50, 19
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 - 32, y0 - 32, x0 + gap * (self.n_entries - 1) + 32, y0 + 44), 14, 14),
                        paint('#000000', alpha=int(140 * fade)))
            for i in range(self.n_entries):
                cx = x0 + i * gap
                if i + 1 < n:
                    c.drawCircle(cx, y0, r, paint('#5A1E20', alpha=al))
                    draw_prop(c, 'icon', cx, y0, 26, kind='skull', alpha=int(al * 0.75))
                elif i + 1 == n:
                    pulse = 1 + 0.06 * math.sin(f * 0.18)
                    c.drawCircle(cx, y0, r * 1.15 * pulse, paint('#E0262C', alpha=al))
                    draw_prop(c, 'icon', cx, y0, 30 * pulse, kind='skull', alpha=al)
                else:
                    c.drawCircle(cx, y0, r, paint('#8A8A8A', stroke=3, alpha=int(al * 0.7)))
            prog = (f - a) / max(1, z - a)
            bx0, bx1, by = x0 - 20, x0 + gap * (self.n_entries - 1) + 20, y0 + 32
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, by, bx1, by + 6), 3, 3), paint('#3A3A3A', alpha=al))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, by, bx0 + (bx1 - bx0) * prog, by + 6), 3, 3), paint('#E0262C', alpha=al))
            lab_k = (f - a) / FPS
            if lab_k < 3.5:
                la = int(al * min(1.0, (3.5 - lab_k) / 0.6))
                s = size_for_cap(22)
                draw_text(c, f'DEATH {n} OF {self.n_entries}', x0 + gap * (self.n_entries - 1) + 52, y0 + 9, s, style='silver',
                          tracking=0.08, alpha=la, shadow=False, grunge=False)

    # ------------------------------------------------ teaser chip (flash-forward)
    def teaser(self, c, surf, b, f):
        snap = surf.makeImageSnapshot()
        cm = color_matrix(0.55, 1.0)
        c.clear(skia.ColorBLACK)
        c.drawImage(snap, 0, 0, skia.SamplingOptions(), skia.Paint(ColorFilter=skia.ColorFilters.Matrix(cm)))
        sh = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.7, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 170)])
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
        k = f - b['f0']
        a = int(255 * min(1.0, (k + 1) / 4))
        s = size_for_cap(30)
        tw = text_width('COMING UP', s, 0.1)
        y0 = H - 128
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, y0, 60 + tw + 56, y0 + 64), 10, 10), paint('#E0262C', alpha=a))
        if (f // 10) % 2 == 0:
            c.drawCircle(88, y0 + 32, 9, paint('#FFFFFF', alpha=a))
        draw_text(c, 'COMING UP', 108, y0 + 46, s, style='#FFFFFF', tracking=0.1, alpha=a, shadow=False, grunge=False)


# ---------------------------------------------------------------- host life
def host_expr(h, f, e):
    """Blink schedule (3-frame blinks every 2.3-4 s), seeded per shot."""
    if e in ('sleep', 'dead') or e.endswith('_blink'):
        return e
    r = random.Random(h['f0'] * 7 + 3)
    t = h['f0'] + r.randint(18, 60)
    while t <= f:
        if f < t + 3:
            return e + '_blink'
        t += r.randint(70, 120)
    return e


def host_bounce(h, f):
    """Squash/stretch for a few frames after each expression change."""
    last = h['exprs'][0][0]
    for f0, _ in h['exprs']:
        if f0 <= f:
            last = f0
    k = f - last
    if k < 0 or k > 8 or last == h['f0']:
        return 1.0
    return 1 + 0.04 * math.sin(k / 8 * 2 * math.pi) * math.exp(-k / 4)
