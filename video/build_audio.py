"""Assemble the voice-over: order clips, tighten pauses by script punctuation, loudness-normalise.
usage: build_audio.py <prod_dir> <script.txt>
Reads  prod/audio_in/<id>.48k.wav, prod/asr/<id>.json
Writes prod/vo_raw.wav (tightened, 48k mono), prod/vo_final.wav (48k stereo, -14 LUFS), prod/audio_report.json
"""
import sys, json, wave, subprocess, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import align as AL

PROD, SCRIPT = sys.argv[1], sys.argv[2]
ORDER = [("80c7029e", "1 · Cold open"), ("6fc39342", "2 · Stakes and setup"), ("776c3134", "2 · Stakes and setup"),
         ("293f3761", "3 · The engine"), ("de677599", "3 · The engine"), ("fc8ffbbd", "5 · The history parallel"),
         ("9ec82919", "6 · The escalation"), ("b2f908f3", "7 · The payoff|8 · The ask|9 · The last line")]
SR = 48000
PAUSE = {"...": 0.80, ".": 0.32, "?": 0.34, "!": 0.32, ":": 0.30, ",": 0.22, ";": 0.22, "": 0.20}
PARA_END = 0.42
JOIN = {"section": 0.60, "para": 0.42}
PAD_PRE, PAD_POST, XF = 0.05, 0.09, 0.006

toks = AL.load_script(SCRIPT)

def read48(path):
    w = wave.open(path); n = w.getnframes(); sw = w.getsampwidth(); raw = w.readframes(n)
    if sw == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        x = np.where(x >= 1 << 23, x - (1 << 24), x).astype(np.float32) / (1 << 23)
    else:
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return x

def write_wav(path, x, ch=1):
    y = np.clip(x, -1, 1); y = (y * 32767).astype(np.int16)
    if ch == 2: y = np.repeat(y[:, None], 2, axis=1).reshape(-1)
    w = wave.open(path, "wb"); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()

def asr_to_script_map(words, sec_names):
    sub = [t for t in toks if t["section"] in sec_names]
    S = []; S_owner = []
    for t in sub:
        for p in t["parts"]: S.append(p); S_owner.append(t["i"])
    A = []; A_owner = []
    for wi, w in enumerate(words):
        for p in AL.norm_parts(w["word"]): A.append(p); A_owner.append(wi)
    import difflib
    sm = difflib.SequenceMatcher(a=S, b=A, autojunk=False); m = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): m[A_owner[blk.b + k]] = S_owner[blk.a + k]
    return m, sum(b.size for b in sm.get_matching_blocks()) / max(1, len(A))

pieces = []; report = []; prev_last_tok = None
for ci, (cid, secs) in enumerate(ORDER):
    x = read48(f"{PROD}/audio_in/{cid}.48k.wav")
    r = json.load(open(f"{PROD}/asr/{cid}.json")); words = r["words"]; vad = r["vad"]
    wmap, frac = asr_to_script_map(words, set(secs.split("|")))
    # speech regions (VAD, padded, merged)
    segs = []
    for a, b in vad:
        a = max(0.0, a - PAD_PRE); b = min(len(x) / SR, b + PAD_POST)
        if segs and a <= segs[-1][1]: segs[-1][1] = max(segs[-1][1], b)
        else: segs.append([a, b])
    cuts = []  # intervals (s) to remove
    for k in range(len(segs) - 1):
        g0, g1 = segs[k][1], segs[k + 1][0]
        total = (g1 + PAD_PRE) - (g0 - PAD_POST)          # speech-to-speech silence
        # last word before the gap -> script punctuation
        wl = [wi for wi, w in enumerate(words) if w["end"] <= g0 + 0.05]
        tk = toks[wmap[wl[-1]]] if wl and wl[-1] in wmap else None
        punct = tk["punct"] if tk else ""
        target = PAUSE.get(punct, 0.2)
        if tk and tk["para_end"] and punct != "...": target = max(target, PARA_END)
        if total > target:
            rem = min(total - target, g1 - g0 - 0.002)
            if rem > 0.01:
                mid = (g0 + g1) / 2; cuts.append((mid - rem / 2, mid + rem / 2))
    keep = []; t0 = 0.0
    for a, b in cuts: keep.append((t0, a)); t0 = b
    keep.append((t0, len(x) / SR))
    y = []
    for a, b in keep:
        seg = x[int(a * SR):int(b * SR)].copy(); f = int(XF * SR)
        if len(seg) > 2 * f:
            seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        y.append(seg)
    y = np.concatenate(y)
    # trim leading/trailing silence beyond 40 ms
    nz = np.where(np.abs(y) > 0.003)[0]
    if len(nz): y = y[max(0, nz[0] - int(0.04 * SR)): nz[-1] + int(0.12 * SR)]
    if ci > 0:
        new_sec = ORDER[ci][1].split("|")[0] != ORDER[ci - 1][1].split("|")[-1]
        pieces.append(np.zeros(int(JOIN["section" if new_sec else "para"] * SR), np.float32))
    pieces.append(y)
    report.append(dict(clip=cid, sections=secs, in_s=round(len(x) / SR, 2), out_s=round(len(y) / SR, 2),
                       removed_s=round(sum(b - a for a, b in cuts), 2), n_cuts=len(cuts), script_match=round(frac, 3)))
vo = np.concatenate(pieces)
write_wav(f"{PROD}/vo_raw.wav", vo, 1)
# loudness: HPF + gentle compression, then two-pass loudnorm to -14 LUFS / -1 dBTP
pre = "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=90:makeup=2"
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{PROD}/vo_raw.wav", "-af", pre + ",loudnorm=I=-14:TP=-1.0:LRA=5:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
js = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.0:LRA=5:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{PROD}/vo_raw.wav", "-af", pre + "," + ln + ",aresample=48000",
                "-ac", "2", "-c:a", "pcm_s16le", f"{PROD}/vo_final.wav"], check=True)
json.dump(dict(clips=report, total_s=round(len(vo) / SR, 2), loudnorm_first_pass=js), open(f"{PROD}/audio_report.json", "w"), indent=1)
for r in report: print(r)
print("total", round(len(vo) / SR, 2), "s")
