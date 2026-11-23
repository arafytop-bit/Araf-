"""Captions (.srt) from the exact script + aligned word times (data/words.json): sentence-based, balanced chunks <= 42 chars."""
import json, sys, math
W = json.load(open(sys.argv[1])); out = sys.argv[2]; MAXC = 42
def ts(t):
    t = max(0.0, t); ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
sents = []; cur = []
for i, w in enumerate(W):
    cur.append(w)
    if w["p"] in (".", "?", "!", "...") or i + 1 == len(W) or W[i + 1]["sec"] != w["sec"]: sents.append(cur); cur = []
cues = []
for s in sents:
    L = len(" ".join(x["w"] for x in s)); n = max(1, math.ceil(L / MAXC)); target = L / n
    chunk = []
    for k, w in enumerate(s):
        chunk.append(w); txt = " ".join(x["w"] for x in chunk)
        rest = s[k + 1:]
        if not rest: cues.append(chunk); break
        nxt_len = len(txt) + 1 + len(rest[0]["w"])
        if (len(txt) >= target - 4 and (w["p"] in (",", ";", ":") or len(txt) >= target)) or nxt_len > MAXC:
            if len(" ".join(x["w"] for x in rest)) >= 8 or nxt_len > MAXC:
                cues.append(chunk); chunk = []
with open(out, "w") as f:
    for k, c in enumerate(cues):
        a = c[0]["s"]; b = max(c[-1]["e"], a + 0.8)
        if k + 1 < len(cues): b = min(b, cues[k + 1][0]["s"] - 0.02)
        f.write(f"{k + 1}\n{ts(a)} --> {ts(b)}\n{' '.join(x['w'] for x in c)}\n\n")
print(len(cues), "cues ->", out, "| max len", max(len(" ".join(x["w"] for x in c)) for c in cues))
