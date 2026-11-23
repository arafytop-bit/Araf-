"""QA for a rendered video: stream/format checks, loudness, blank-white detection, frame contact sheets from the encoded file.
usage: qa.py video.mp4 outdir [sheet_seconds_per_tile]"""
import sys, os, json, subprocess, re
import numpy as np
from PIL import Image, ImageDraw

src, outdir = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
os.makedirs(outdir, exist_ok=True)
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", src], capture_output=True, text=True).stdout)
for s in pr["streams"]:
    print(s["codec_type"], s["codec_name"], s.get("width", ""), s.get("height", ""), s.get("r_frame_rate", ""), s.get("sample_rate", ""), s.get("channels", ""), s.get("nb_frames", ""))
dur = float(pr["format"]["duration"]); print("duration", round(dur, 2), "s  size", round(int(pr["format"]["size"]) / 1e6, 1), "MB")
lo = subprocess.run(["ffmpeg", "-nostats", "-i", src, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(" ".join(l.strip() for l in lo.splitlines()[-12:] if re.search(r"I:|LRA:|Peak:", l)))
# blank (near-white, no ink) stretches > 0.4 s, sampled at 10 fps on a small proxy
W, H = 192, 108
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=10,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
ink = []
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    a = np.frombuffer(b, np.uint8); ink.append(float((a < 200).mean()))
ink = np.array(ink); blank = ink < 0.002
runs = []; i = 0
while i < len(blank):
    if blank[i]:
        j = i
        while j < len(blank) and blank[j]: j += 1
        if (j - i) / 10 >= 0.4: runs.append((i / 10, (j - i) / 10))
        i = j
    else: i += 1
print("blank stretches >=0.4s:", runs if runs else "none")
# contact sheets every `step` seconds
times = np.arange(1.0, dur - 0.5, step); cols = 8; tw, th = 240, 135
per = cols * 8
for si in range(0, len(times), per):
    tt = times[si:si + per]
    sheet = Image.new("RGB", (cols * tw, ((len(tt) + cols - 1) // cols) * (th + 16)), (40, 40, 40)); d = ImageDraw.Draw(sheet)
    for k, t in enumerate(tt):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == tw * th * 3:
            im = Image.frombytes("RGB", (tw, th), raw); x, y = (k % cols) * tw, (k // cols) * (th + 16); sheet.paste(im, (x, y))
            d.text((x + 3, y + th + 2), f"{int(t // 60):02d}:{t % 60:05.2f}", fill=(255, 230, 120))
    sheet.save(f"{outdir}/qa_{si // per:02d}.png")
print("sheets:", (len(times) + per - 1) // per)
