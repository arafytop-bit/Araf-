"""10-second style test: renders projects/test10/test_10s.mp4 (1920x1080, 30 fps).

Every cut is placed one frame before the onset of the word it illustrates, using the
forced-aligned word timings in voice_words.json (BLUEPRINT section 4).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))

import skia  # noqa: E402
from engine.core import W, H, FPS, new_surface, draw_background, ease_out_cubic  # noqa: E402
from engine.character import (draw_character, HOST, AGENT, subject, R_NORMAL, R_ZOOM,  # noqa: E402
                              NORMAL_CENTER, ZOOM_CENTER)
from engine.text import draw_callout, draw_label  # noqa: E402
from engine.mapdraw import draw_map, map_point, draw_dot, dot_pulse_visible, load_outline  # noqa: E402
from engine.cards import KineticTitle, draw_title_card, make_portrait  # noqa: E402
from engine import audio  # noqa: E402

TOTAL = 300                     # 10.0 s
VOICE_OFFSET = 0.07             # first word at 0.07 s, as in the source
words = json.load(open(os.path.join(HERE, 'voice_words.json')))
onset = [w['s'] + VOICE_OFFSET for w in words]


def cutf(i):
    """Frame of the cut for word index i: one frame before its onset."""
    return max(0, round(onset[i] * FPS) - 1)


# word indices: 0 every 1 person 2 on 3 the 4 fbi's 5 most 6 wanted 7 list 8 has 9 a 10 story
# 11 the 12 list 13 started 14 in 15 nineteen 16 fifty 17 in 18 washington 19 d 20 c 21 and
# 22 the 23 very 24 first 25 name 26 on 27 it 28 thomas 29 james 30 holden
C = dict(s2=cutf(8), s2_swap=cutf(10), s3=cutf(11), s3_swap=cutf(13), s4=cutf(15), s4_swap=cutf(16),
         s5=cutf(18), s6a=cutf(21), s6b=cutf(24), s6b_swap=cutf(26), s7=cutf(28))

kin = KineticTitle([
    (231, [('EVERY', 74, 'silver', cutf(0)), ('PERSON', 74, 'silver', cutf(1))], W * 0.60),
    (461, [('ON', 80, 'silver', cutf(2)), ('THE', 80, 'silver', cutf(3)), ("FBI'S", 125, 'silver', cutf(4))], W * 0.65),
    (686, [('MOST', 92, 'red', cutf(5)), ('WANTED', 92, 'red', cutf(6)), ('LIST', 108, 'silver', cutf(7))], W * 0.79),
])

portrait = make_portrait(subject(skin='#E2BC98', hair='slick', top='suit', top_color='#2E2C33'), expr='neutral')

# map sizing: height = 72% of frame (BLUEPRINT 5.6), centred
_path, _j = load_outline('us_outline')
_b = _path.computeTightBounds()
MAP_SCALE = (0.72 * H) / _b.height()
MAP_C = (960, 560)
DC = _j['dc']


def host(c, f, f0, scale, pose, exprs, bob=(0.0, 0.0), glint=False):
    """exprs: list of (start_frame, expression)."""
    e = exprs[0][1]
    k = 0
    for i, (fs, ex) in enumerate(exprs):
        if f >= fs:
            e, k = ex, i
    b = (bob[0] * (1 if k % 2 else 0), bob[1] * (1 if k % 2 else 0))
    if scale == 'zoom':
        draw_character(c, *ZOOM_CENTER, R_ZOOM, pose=pose, expr=e, pal=HOST, bob=b, glint=glint)
    else:
        draw_character(c, *NORMAL_CENTER, R_NORMAL, pose=pose, expr=e, pal=HOST, bob=b, glint=glint)


def frame(c, f):
    draw_background(c)
    if f < C['s2']:                                   # S1 kinetic title
        kin.draw(c, f, 0, C['s2'])
        e = 'talk' if f < 20 else 'o' if f < 40 else 'talk2' if f < 58 else 'smile'
        draw_character(c, 330, 905, 80, pose='hips', expr=e, pal=HOST)
        for i, xf in enumerate((1290, 1500, 1710)):  # agents walk in from the right
            if f < 30 + 4 * i:
                continue
            p = ease_out_cubic((f - 30 - 4 * i) / 36.0)
            x = xf + (2150 - xf) * (1 - p)
            walking = p < 0.999
            draw_character(c, x, 905, 58, pose='walk' if walking else 'hips', expr='o', pal=AGENT,
                           phase=f * 0.95 + i * 1.3 if walking else 0.0)
    elif f < C['s3']:                                 # S2 host normal, wave
        host(c, f, C['s2'], 'normal', 'wave', [(C['s2'], 'talk'), (C['s2_swap'], 'smile')], bob=(0.02, -0.015))
    elif f < C['s4']:                                 # S3 punch-in x1.52
        host(c, f, C['s3'], 'zoom', 'hips', [(C['s3'], 'o'), (C['s3_swap'], 'talk2')], bob=(-0.015, 0.01))
    elif f < C['s5']:                                 # S4 red callout "1950" over host
        host(c, f, C['s4'], 'normal', 'shrug', [(C['s4'], 'talk'), (C['s4_swap'], 'grin')], bob=(0.015, -0.01))
        draw_callout(c, '1950', progress=(f - C['s4'] + 1) / 5.0)
    elif f < C['s6a']:                                # S5 map + pulsing dot + label
        t = f - C['s5']
        sc = MAP_SCALE * (1.10 - 0.10 * ease_out_cubic(t / 3.0)) * (1 + 0.006 * t / FPS)
        draw_map(c, 'us_outline', *MAP_C, scale=sc)
        x, y = map_point('us_outline', *MAP_C, sc, DC)
        draw_dot(c, x, y, r=16, visible=dot_pulse_visible(t))
        draw_label(c, 'WASHINGTON, D.C.', x - 30, y + 13, 33, align='right')
    elif f < C['s6b']:                                # S6a host thinking
        host(c, f, C['s6a'], 'normal', 'nerd', [(C['s6a'], 'skeptic')], glint=True)
    elif f < C['s7']:                                 # S6b punch-in on the question
        host(c, f, C['s6b'], 'zoom', 'wave', [(C['s6b'], 'o'), (C['s6b_swap'], 'talk')], bob=(0.02, 0.0))
    else:                                             # S7 fugitive title card
        draw_title_card(c, 1, ['THOMAS', 'JAMES', 'HOLDEN'], portrait, f - C['s7'])


def render(out_path):
    tmp = out_path.replace('.mp4', '_video.mp4')
    ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo',
                           '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', tmp],
                          stdin=subprocess.PIPE)
    s = new_surface()
    for f in range(TOTAL):
        c = s.getCanvas()
        c.clear(skia.ColorBLACK)
        frame(c, f)
        ff.stdin.write(s.makeImageSnapshot().toarray().tobytes())
    ff.stdin.close()
    ff.wait()
    # audio: voice + bed (~22 dB under) + hit on the title-card cut
    mix = os.path.join(HERE, 'mix.wav')
    audio.mix(os.path.join(HERE, 'voice_tight.wav'), TOTAL / FPS, VOICE_OFFSET, hits=[C['s7'] / FPS], out_path=mix)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', tmp, '-i', mix,
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '48000',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                    out_path], check=True)
    os.remove(tmp)
    print('cuts (frame):', C)
    print('wrote', out_path)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
        s = new_surface()
        for f in [int(v) for v in sys.argv[2].split(',')]:
            c = s.getCanvas(); c.clear(skia.ColorBLACK); frame(c, f)
            import cv2
            cv2.imwrite(os.path.join(HERE, 'stills', f'f{f:03d}.png'), s.makeImageSnapshot().toarray()[:, :, :3])
        print('stills done')
    else:
        render(os.path.join(HERE, 'test_10s.mp4'))
