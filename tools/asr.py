# Word-level ASR with sherpa-onnx Parakeet-TDT + Silero VAD. Usage: asr.py audio16k.wav out.json modeldir vad.onnx
import sys, json, time, wave, numpy as np, sherpa_onnx
wav, out, md, vadm = sys.argv[1:5]
w = wave.open(wav); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
if w.getnchannels() == 2: x = x.reshape(-1,2).mean(1)
assert sr == 16000
t0 = time.time()
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{md}/encoder.int8.onnx", decoder=f"{md}/decoder.int8.onnx",
        joiner=f"{md}/joiner.int8.onnx", tokens=f"{md}/tokens.txt", num_threads=4, sample_rate=16000, feature_dim=80,
        decoding_method="greedy_search", model_type="nemo_transducer")
cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = vadm; cfg.silero_vad.min_silence_duration = 0.2
cfg.silero_vad.min_speech_duration = 0.1; cfg.silero_vad.max_speech_duration = 25; cfg.silero_vad.threshold = 0.5; cfg.sample_rate = 16000
vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=1000)
ws = cfg.silero_vad.window_size; segs = []
for i in range(0, len(x), ws):
    vad.accept_waveform(x[i:i+ws])
    while not vad.empty(): segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
vad.flush()
while not vad.empty(): segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
print('vad segments', len(segs), flush=True)
res = {"vad": [], "segments": [], "words": []}
for st, smp in segs:
    # pad 0.15s context each side from original audio
    a = max(0, st - 2400); b = min(len(x), st + len(smp) + 2400); chunk = x[a:b]
    s = rec.create_stream(); s.accept_waveform(16000, chunk); rec.decode_stream(s); r = s.result
    off = a/16000
    res["vad"].append([st/16000, (st+len(smp))/16000])
    toks = list(r.tokens); ts = [off+t for t in r.timestamps]
    durs = list(getattr(r, 'durations', []) or [])
    words = []
    for k,(tok,t) in enumerate(zip(toks, ts)):
        d = durs[k] if k < len(durs) else 0.0
        if tok.startswith(' ') or tok.startswith('▁') or not words:
            words.append({"word": tok.replace('▁','').strip(), "start": t, "end": t + max(d, 0.04)})
        else:
            words[-1]["word"] += tok; words[-1]["end"] = t + max(d, 0.04)
    # end of each word = start of next token if no durations
    for k in range(len(words)-1):
        words[k]["end"] = min(max(words[k]["end"], words[k]["start"]+0.04), words[k+1]["start"])
    if words: words[-1]["end"] = max(words[-1]["end"], min((st+len(smp))/16000, words[-1]["start"]+0.6))
    res["segments"].append({"start": st/16000, "end": (st+len(smp))/16000, "text": r.text})
    res["words"].extend(words)
    print(f"[{st/16000:7.2f}-{(st+len(smp))/16000:7.2f}] {r.text}", flush=True)
json.dump(res, open(out, "w"), indent=1)
print("DONE", round(time.time()-t0,1), "s; words:", len(res["words"]), flush=True)
