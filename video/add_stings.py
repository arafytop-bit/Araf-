"""Insert chapter stings (original synthesized motif) into narration pauses + outro music under the end card.
Reads PROD/vo_final.wav + PROD/words_raw.json; writes PROD/audio_master.wav + PROD/words.json (shifted) + PROD/stings.json"""
import sys, os, json, wave, subprocess, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from engine import Words

PROD = sys.argv[1]; SR = 48000
CHAPTERS = ["Capacity is an insurance policy", "Okay. The second way", "Now for the third way", "In the early 1970s"]
GAP = 1.35          # inserted pause (s); sting starts 0.08 s into it
ENDCARD = 8.0       # seconds of end card after the last word (+0.6 s)

def read_wav(p):
    w = wave.open(p); n = w.getnframes(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, ch) if ch > 1 else np.repeat(x[:, None], 2, 1)

def write_wav(p, x):
    y = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()

def note(freq, dur, decay=0.35, partials=((1, 1.0), (2, 0.22), (3.98, 0.12)), attack=0.004):
    t = np.arange(int(dur * SR)) / SR
    y = sum(a * np.sin(2 * np.pi * freq * h * t) * np.exp(-t * (1 + (h - 1) * 3.0) / decay) for h, a in partials)
    return y * (1 - np.exp(-t / attack))

def pan(y, p):  # p in [-1, 1]
    l, r = np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4)
    return np.stack([y * l, y * r], 1)

def place(buf, y, t):
    i = int(t * SR); j = min(len(buf), i + len(y)); buf[i:j] += y[:j - i]

def sting():
    out = np.zeros((int(1.25 * SR), 2), np.float32)
    place(out, pan(note(130.81, 0.5, 0.12, ((1, 1.0),)), 0) * 0.9, 0.0)                         # soft low thump (C3)
    for k, (f, p) in enumerate(((392.00, -0.4), (523.25, 0.3), (659.25, -0.2), (783.99, 0.35))):  # G4 C5 E5 G5
        place(out, pan(note(f, 1.1 - k * 0.09, 0.22 if k < 3 else 0.55), p) * (0.55 if k < 3 else 0.75), k * 0.085)
    place(out, pan(note(1046.5, 0.8, 0.45), 0.0) * 0.35, 0.34)                                    # sparkle C6
    return out / np.abs(out).max() * 10 ** (-7 / 20)

def outro(dur):
    out = np.zeros((int(dur * SR), 2), np.float32); beat = 0.5
    prog = [((130.81, 164.81, 196.00), (523.25, 659.25, 783.99, 659.25)), ((110.00, 130.81, 164.81), (440.00, 523.25, 659.25, 523.25)),
            ((87.31, 110.00, 130.81), (349.23, 440.00, 523.25, 440.00)), ((98.00, 123.47, 146.83), (392.00, 493.88, 587.33, 783.99))]
    t = 0.0
    while t < dur - 0.5:
        for chord, mel in prog:
            if t >= dur - 0.5: break
            for f in chord:   # warm e-piano pad
                place(out, pan(note(f * 2, 2.2, 0.9, ((1, 1.0), (2, 0.15))), 0) * 0.16, t)
            place(out, pan(note(chord[0] / 2, 2.0, 0.6, ((1, 1.0),)), 0) * 0.45, t)                # bass
            for k, f in enumerate(mel):   # marimba melody
                place(out, pan(note(f, 0.9, 0.25), (-0.3, 0.3)[k % 2]) * 0.30, t + k * beat)
            t += 4 * beat
    fo = int(2.2 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    fi = int(0.03 * SR); out[:fi] *= np.linspace(0, 1, fi)[:, None]
    return out / np.abs(out).max() * 10 ** (-6 / 20)

def main():
    raw = f"{PROD}/words_raw.json"
    if not os.path.exists(raw): os.rename(f"{PROD}/words.json", raw)
    W = json.load(open(raw)); finder = Words(raw)
    vo = read_wav(f"{PROD}/vo_final.wav")
    ins = []
    for ph in CHAPTERS:
        i = finder.find(ph); finder.cursor = i
        ins.append(((W[i - 1]["e"] + W[i]["s"]) / 2, i, ph))
    ins.sort()
    pieces = []; last = 0; st = sting(); log = []
    for k, (t, i, ph) in enumerate(ins):
        a = int(t * SR); pieces.append(vo[last:a])
        gap = np.zeros((int(GAP * SR), 2), np.float32); place(gap, st, 0.08); pieces.append(gap)
        last = a; log.append(dict(anchor=ph, t_insert=round(t + k * GAP, 3), gap=GAP))
    pieces.append(vo[last:])
    out = np.concatenate(pieces)
    # shift words
    for w in W:
        sh = sum(GAP for (t, i, ph) in ins if w["s"] >= t)
        w["s"] = round(w["s"] + sh, 3); w["e"] = round(w["e"] + sh, 3)
    json.dump(W, open(f"{PROD}/words.json", "w"), indent=0)
    # outro under end card
    t_end = W[-1]["e"] + 0.6; total = t_end + ENDCARD
    if len(out) < int(total * SR): out = np.concatenate([out, np.zeros((int(total * SR) - len(out), 2), np.float32)])
    out = out[:int(total * SR)]
    place(out, outro(ENDCARD), t_end)
    write_wav(f"{PROD}/audio_master_pre.wav", out)
    # final safety limiter (true-peak ceiling -1 dBTP), keep loudness
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{PROD}/audio_master_pre.wav", "-af", "alimiter=limit=0.89:attack=2:release=50:level=false",
                    "-ar", str(SR), "-c:a", "pcm_s16le", f"{PROD}/audio_master.wav"], check=True)
    json.dump(dict(chapters=log, endcard_start=round(t_end, 3), total=round(total, 3)), open(f"{PROD}/stings.json", "w"), indent=1)
    print(json.dumps(log, indent=1)); print("total", round(total, 2), "endcard at", round(t_end, 2))

if __name__ == "__main__":
    main()
