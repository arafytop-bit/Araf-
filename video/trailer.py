"""Channel trailer: evergreen cut of the cold open + "who really pays?" promise card + the subscribe ask + branded end card.
usage: PROD=<workdir> python3 trailer.py <full_video_with_sound.mp4> <out.mp4> ["Channel Name"]"""
import os, sys, json, math, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import engine, props, story
from engine import Scene, El, FPS
from dd import *
import sound_design as SD
from add_stings import sting

PROD = os.environ.get("PROD", story.PROD); SR = 48000
SRC, OUT = sys.argv[1], sys.argv[2]
NAME = sys.argv[3] if len(sys.argv) > 3 else "Sketchy Economics"
TMP = os.path.join(os.path.dirname(OUT) or ".", "_trailer_tmp"); os.makedirs(TMP, exist_ok=True)

# ---------------------------------------------------------------- cut points = existing scene cuts
B = story.build(); words = B.words
def scene_t(phrase):
    i = words.find(phrase, 0); s = words.w[i]["s"]
    c = [sc.t0 for sc in B.scenes if s - 0.12 <= sc.t0 <= s + 0.01]
    return round(min(c, key=lambda x: abs(x - s)) * FPS) / FPS
def fr(t): return int(round(t * FPS))
def word_t(phrase, pad=0.06):
    i = words.find(phrase, 0); return math.floor((words.w[i]["s"] - pad) * FPS) / FPS
a1 = (scene_t("the AI boom lost an election"), word_t("Last month, Consumer Reports"))   # end mid-scene, just before "Last month"
a2 = (scene_t("So the fix sounds obvious"), scene_t("The answer starts with"))
bb = (scene_t("Making this one meant"), scene_t("So here's where it lands"))
P_DUR, C_DUR = 2.0, 8.0
print("cuts:", a1, a2, bb)

def cut(t0, t1, name):
    out = f"{TMP}/{name}.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.4f}", "-i", SRC, "-frames:v", str(fr(t1) - fr(t0)), "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out], check=True)
    return out

# ---------------------------------------------------------------- cards (rendered with the video's engine)
props.REG["dash_circle"] = lambda seed=0, r=110, color=INK: f'<g stroke-dasharray="16 12">{P(wellipse(0, 0, r, r, seed * 1000 + 7, 1.5), "none", color, 6)}</g>'

class Mini:
    def __init__(self, scenes): self.scenes = scenes
    def frame_svg(self, f):
        t = f / FPS; sc = [s for s in self.scenes if s.t0 <= t + 1e-9][-1]; return sc.svg(t, f)

def card_promise():
    sc = Scene(0.0)
    sc.add(El("note", 0.0, x=960, y=390, lines="Every video asks one question:", size=70, color=INK, weight=700))
    sc.add(El("hero", 0.4, x=960, y=620, text="WHO REALLY PAYS?", size=175, color=RED))
    return Mini([sc]), [(0.4, "impact", 0.0)]

def card_end():
    sc = Scene(0.0); sfx = []
    sc.add(El("person", 0.15, x=330, y=320, k=0.8, pose="present", mouth="open", hair="spiky")); sfx.append((0.15, "pop_char", -0.6))
    sc.add(El("hero", 0.0, x=1180, y=190, text=NAME, size=128, color=INK)); sfx.append((0.0, "pop", 0.2))
    nw = text_w(NAME, 128, 700, spacing=128 * 0.03)
    sc.add(El("hline", 0.0, x=1180, y=255, w=nw, color=RED, thick=12))
    sc.add(El("note", 0.35, x=1180, y=345, lines="Who really pays? Economics, explained in doodles.", size=50, color="#333333", weight=700)); sfx.append((0.35, "pop_small", 0.2))
    # guides for YouTube end-screen elements: video box (right) + subscribe circle (under the narrator)
    sc.add(El("note", 0.8, x=1330, y=478, lines="Watch the full story", size=56, color=INK, weight=700))
    sc.add(El("frame_box", 0.8, x=1330, y=745, w=820, h=460, dashed=True)); sfx.append((0.8, "pop", 0.4))
    sc.add(El("arrow_r", 1.05, x=700, y=600, w=300, rot=18)); sfx.append((1.05, "zip_side", 0.0))
    sc.add(El("dash_circle", 1.3, x=330, y=935, r=100)); sfx.append((1.3, "pop", -0.6))
    sc.add(El("note", 1.3, x=455, y=955, lines="Subscribe!", size=64, color=RED, weight=700, anchor="start"))
    return Mini([sc]), sfx

def render_card(mini, dur, name):
    out = f"{TMP}/{name}.mkv"; engine.render_segment(mini, 0, int(round(dur * FPS)), out, 18, "medium"); return out

# ---------------------------------------------------------------- audio
mix = SD.read(f"{PROD}/mix.wav"); master = SD.read(f"{PROD}/audio_master.wav"); stj = json.load(open(f"{PROD}/stings.json"))
def seg(x, t0, t1, fi=0.015, fo=0.03):
    y = x[int(round(t0 * SR)):int(round(t1 * SR))].copy()
    n = int(fi * SR); y[:n] *= np.linspace(0, 1, n)[:, None]; n = int(fo * SR); y[-n:] *= np.linspace(1, 0, n)[:, None]; return y
def sfx_bed(dur, events):
    buf = np.zeros((int(round(dur * SR)), 2), np.float32)
    for t, kind, pan in events:
        y = SD.SFX[kind]() if not kind.startswith("pop") else SD.SFX[kind](1.0)
        SD.place_stereo(buf, SD.fadeout(SD.peak(y, SD.LEVEL[kind]), 0.006), t, pan)
    return buf

if __name__ == "__main__":
    vids = [cut(*a1, "a1"), cut(*a2, "a2")]
    mp, p_sfx = card_promise(); vids.append(render_card(mp, P_DUR, "promise"))
    vids.append(cut(*bb, "ask"))
    me, c_sfx = card_end(); vids.append(render_card(me, C_DUR, "endcard"))
    # audio pieces
    pa = sfx_bed(P_DUR, p_sfx); SD.place_stereo(pa, np.zeros(1), 0, 0)
    st = sting(); pa[int(0.05 * SR):int(0.05 * SR) + len(st)] += st[:len(pa) - int(0.05 * SR)]
    ec = stj["endcard_start"]
    ca = seg(master, ec, ec + C_DUR, 0.01, 0.4) + sfx_bed(C_DUR, c_sfx)[:int(round(C_DUR * SR))]
    audio = np.concatenate([seg(mix, *a1), seg(mix, *a2), pa, seg(mix, *bb, 0.015, 0.12), ca])
    SD.write(f"{TMP}/audio_pre.wav", audio * 0.9)
    I, _ = SD.lufs(f"{TMP}/audio_pre.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{TMP}/audio_pre.wav", "-af", f"volume={-14.0 - I:.2f}dB,alimiter=limit=0.85:attack=1:release=60:level=false",
                    "-ar", str(SR), "-c:a", "pcm_s16le", f"{TMP}/audio.wav"], check=True)
    # concat video (re-encode once) + mux
    ins = sum([["-i", v] for v in vids], [])
    fc = "".join(f"[{i}:v]" for i in range(len(vids))) + f"concat=n={len(vids)}:v=1:a=0[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", f"{TMP}/audio.wav", "-filter_complex", fc, "-map", "[v]", "-map", f"{len(vids)}:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k",
                    "-movflags", "+faststart", "-shortest", OUT], check=True)
    vd = sum(fr(b) - fr(a) for a, b in (a1, a2, bb)) / FPS + P_DUR + C_DUR
    print(f"trailer: video {vd:.2f}s, audio {len(audio) / SR:.2f}s -> {OUT}")
