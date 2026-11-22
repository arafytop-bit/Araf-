# Word-by-word captions (ASS) from voice/words.json: 1-3 word phrases, spoken word in yellow, plum ink outline.
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, "..", "voice", "words.json")))
END = 2650 / 30
def ts(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
# group into phrases: break after punctuation, at 3 words, or at ~16 characters
phrases, cur = [], []
for i, w in enumerate(W):
    cur.append(i)
    txt = " ".join(W[j]["w"] for j in cur)
    gap = (W[i + 1]["s"] - w["e"]) if i + 1 < len(W) else 9
    if re.search(r"[.,?!]$", w["w"]) or len(cur) >= 3 or len(txt) >= 16 or gap > 0.35:
        phrases.append(cur); cur = []
if cur: phrases.append(cur)
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1440
PlayResY: 2560
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display Black,118,&H00FFFFFF,&H00FFFFFF,&H00261724,&H80261724,0,0,0,0,100,100,1,0,1,11,5,2,90,90,760,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
YEL = r"{\c&H4AD8FF&}"
WHT = r"{\c&HFFFFFF&}"
ev = []
for k, ph in enumerate(phrases):
    p_end = W[ph[-1]]["e"] + 0.25
    if k + 1 < len(phrases): p_end = min(max(p_end, W[ph[-1]]["e"]), W[phrases[k + 1][0]]["s"])
    p_end = min(p_end, END)
    words = [re.sub(r"[.,]$", "", W[j]["w"]).upper() for j in ph]
    for n, j in enumerate(ph):
        a = W[j]["s"]
        b = W[ph[n + 1]]["s"] if n + 1 < len(ph) else p_end
        if b <= a: continue
        txt = " ".join((YEL + wd + WHT) if m == n else wd for m, wd in enumerate(words))
        pop = r"{\fscx88\fscy88\t(0,90,\fscx100\fscy100)}" if n == 0 else ""
        ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{pop}{txt}")
open(os.path.join(HERE, "captions.ass"), "w").write(head + "\n".join(ev) + "\n")
print(len(phrases), "phrases,", len(ev), "events")
