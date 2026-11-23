import sys, io, subprocess
sys.path.insert(0, sys.argv[1])
import doodle as D, resvg_py
from PIL import Image
FONTS = [f"{sys.argv[2]}/Gaegu-Regular.ttf", f"{sys.argv[2]}/Gaegu-Bold.ttf"]
FPS, DUR = 30, 4.0
out = sys.argv[3]
ff = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-',
                       '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',out], stdin=subprocess.PIPE)
cache = {}
for f in range(int(FPS*DUR)):
    t = f / FPS; boil = (f // 10) % 2           # 2-drawing boil, 10 frames each @30fps (= 8 @24fps)
    if t < 2.4:
        mouth = "smile" if t < 0.8 else "open"
        body = D.narrator(560, 210, 1.0, "hips", mouth, seed=boil)
        if t >= 1.2: body += D.text(1300, 560, "more than all", 60, D.INK, 400, "middle", spacing=2)
        if t >= 1.5: body += D.text(1300, 760, "COMBINED!", 215, D.RED, 700, "middle", spacing=8)
    else:                                         # hard cut
        n = max(0, int((t - 2.6) * FPS))          # typewriter: 1 char / frame
        body = D.narrator(330, 230, 1.0, "teacher", "smile", seed=boil) + D.chalkboard(760, 110, 1060, 660, ["Must wait!"[:n]] if n else [], size=150)
    key = body
    if key not in cache:
        png = resvg_py.svg_to_bytes(svg_string=D.svg_doc(body), font_files=FONTS, skip_system_fonts=True)
        cache[key] = Image.open(io.BytesIO(bytes(png))).convert("RGB").tobytes()
    ff.stdin.write(cache[key])
ff.stdin.close(); ff.wait(); print('unique frames rendered:', len(cache))
