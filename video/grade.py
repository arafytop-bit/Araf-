"""Premium color grade (lighting, color, contrast only) for a rendered video.
  - lighting: soft lamp-on-paper falloff (multiply light map, warm towards the edges, dithered against banding)
  - color:    warm paper-white highlights, vibrance lift for accents
  - contrast: deeper ink blacks + gentle S-curve, light contrast-adaptive sharpening
usage: grade.py video  <in.mp4> <out.mp4>            (keeps the input audio)
       grade.py stills <in.mp4> <outdir> t1,t2,...   (before/after comparison sheet)"""
import os, sys, subprocess
import numpy as np
from PIL import Image

W, H = 1920, 1080
CURVES = ("curves=r='0/0 1/0.992':g='0/0 1/0.976':b='0/0 1/0.944':"
          "master='0/0 0.05/0.02 0.25/0.225 0.5/0.5 0.75/0.78 1/1'")
VIBRANCE = "vibrance=intensity=0.12"
SHARPEN = "cas=strength=0.35"

def light_map(path, strength=(0.06, 0.075, 0.105), center=(0.5, 0.46)):
    """Elliptical falloff: 1.0 in the middle, darker + warmer towards edges/corners (B falls off most -> warm)."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (x / W - center[0]) / 0.62; ny = (y / H - center[1]) / 0.58
    r = np.sqrt(nx ** 2 + ny ** 2)
    t = np.clip((r - 0.42) / (1.25 - 0.42), 0, 1); s = t * t * (3 - 2 * t)          # smoothstep
    rng = np.random.default_rng(3); dither = rng.normal(0, 0.55, (H, W)).astype(np.float32)
    img = np.stack([255 * (1 - k * s) + dither for k in strength], -1)
    Image.fromarray(np.clip(np.round(img), 0, 255).astype(np.uint8)).save(path)
    return path

def chain(map_input_index=1):
    return (f"[0:v]{CURVES},{VIBRANCE},{SHARPEN},format=gbrp[g];"
            f"[{map_input_index}:v]format=gbrp[l];[g][l]blend=all_mode=multiply:shortest=1,format=yuv420p[v]")

def grade_video(src, out, tmpdir):
    lm = light_map(os.path.join(tmpdir, "light_map.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-framerate", "30", "-i", lm,
                    "-filter_complex", chain(), "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-r", "30", "-c:a", "copy", "-movflags", "+faststart", out], check=True)

def stills(src, outdir, times):
    os.makedirs(outdir, exist_ok=True); lm = light_map(os.path.join(outdir, "light_map.png"))
    pairs = []
    for t in times:
        a = os.path.join(outdir, f"before_{t}.png"); b = os.path.join(outdir, f"after_{t}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", a], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-loop", "1", "-i", lm, "-filter_complex", chain(), "-map", "[v]",
                        "-frames:v", "1", b], check=True)
        pairs.append((a, b))
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * 2 + 10, (th + 10) * len(pairs)), (30, 30, 30))
    for i, (a, b) in enumerate(pairs):
        sheet.paste(Image.open(a).convert("RGB").resize((tw, th), Image.LANCZOS), (0, i * (th + 10)))
        sheet.paste(Image.open(b).convert("RGB").resize((tw, th), Image.LANCZOS), (tw + 10, i * (th + 10)))
    sheet.save(os.path.join(outdir, "compare.png")); return os.path.join(outdir, "compare.png")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "video":
        tmp = os.path.dirname(os.path.abspath(sys.argv[3])); grade_video(sys.argv[2], sys.argv[3], tmp)
    else:
        print(stills(sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4].split(",")]))
