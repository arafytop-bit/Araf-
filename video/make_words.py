"""Align final VO ASR to script -> words.json (script word index, raw text, start, end, section, punct)."""
import sys, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import align as AL
prod, script = sys.argv[1], sys.argv[2]
toks = AL.load_script(script)
asr = json.load(open(f"{prod}/asr_final.json"))["words"]
times, frac = AL.align(toks, asr)
out = []
for t, tm in zip(toks, times):
    out.append(dict(i=t["i"], w=t["raw"], s=round(tm[0], 3), e=round(tm[1], 3), sec=t["section"], p=t["punct"], pe=t["para_end"]))
# enforce monotonic starts
for k in range(1, len(out)):
    if out[k]["s"] < out[k-1]["s"]: out[k]["s"] = out[k-1]["s"]
json.dump(out, open(f"{prod}/words.json", "w"), indent=0)
print("script words", len(out), "match", round(frac, 4))
secs = {}
for w in out: secs.setdefault(w["sec"], w["s"])
for k, v in secs.items(): print(f"{int(v//60):02d}:{v%60:05.2f}  {k}")
print("last word end", out[-1]["e"])
