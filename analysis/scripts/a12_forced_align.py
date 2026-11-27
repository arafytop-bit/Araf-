"""Second timing method: torchaudio MMS_FA (wav2vec2 CTC) forced alignment of the Whisper words, per Whisper segment.

For each Whisper segment, the segment's words (normalised: lowercase, digits spelled out) are force-aligned inside
[seg.start-0.4 s, seg.end+0.4 s] of the vocal stem. Word start/end -> frames (round(t*30)).
Output: analysis/data/words_aligned.json with both methods + disagreement in frames.
"""
import json, re, torch, torchaudio, numpy as np, soundfile as sf
from num2words import num2words
torch.set_num_threads(2)
bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=False); model.eval()
DICT = bundle.get_dict(star=None)
tok = bundle.get_tokenizer(); aligner = bundle.get_aligner()
wav, sr = sf.read('work/stems/vocals_16k.wav', dtype='float32'); assert sr == 16000
raw = json.load(open('analysis/data/whisper_raw.json'))

def norm(w):
    w = w.lower().replace('’', "'")
    w = w.replace('$', '')
    parts = []
    for p in re.split(r'[-\s]+', w):
        p2 = re.sub(r"[^a-z0-9']", '', p)
        if not p2:
            continue
        if re.fullmatch(r'\d[\d,]*', p2):
            n = int(p2.replace(',', ''))
            if 1800 <= n <= 1999 and len(p2) == 4:
                s = num2words(n, to='year')
            else:
                s = num2words(n)
            parts += re.sub(r"[^a-z' ]", ' ', s.replace('-', ' ')).split()
        else:
            p3 = ''.join(ch for ch in p2 if ch in DICT)
            if p3:
                parts.append(p3)
    return parts

out = []
for seg in raw['segments']:
    words = seg.get('words', [])
    if not words:
        continue
    t0 = max(0.0, seg['start'] - 0.4); t1 = min(len(wav)/sr, seg['end'] + 0.4)
    x = torch.from_numpy(wav[int(t0*sr):int(t1*sr)])[None]
    with torch.inference_mode():
        em, _ = model(x)
    em = torch.log_softmax(em, -1)
    toks = []; owner = []
    for wi, w in enumerate(words):
        for p in norm(w['word']):
            toks.append(p); owner.append(wi)
    if not toks:
        continue
    try:
        spans = aligner(em[0], tok(toks))
    except Exception as e:
        print('align fail seg', seg['id'], e); continue
    ratio = x.shape[1] / em.shape[1] / sr   # seconds per emission frame
    wstart = {}; wend = {}
    for p_i, sp in enumerate(spans):
        wi = owner[p_i]
        s = t0 + sp[0].start*ratio; e = t0 + sp[-1].end*ratio
        wstart[wi] = min(wstart.get(wi, 1e9), s); wend[wi] = max(wend.get(wi, -1), e)
    for wi, w in enumerate(words):
        if wi not in wstart:
            continue
        out.append(dict(word=w['word'].strip(), seg=seg['id'],
                        whisper_start_s=round(w['start'], 3), whisper_end_s=round(w['end'], 3),
                        fa_start_s=round(wstart[wi], 3), fa_end_s=round(wend[wi], 3),
                        whisper_start_f=int(round(w['start']*30)), fa_start_f=int(round(wstart[wi]*30)),
                        whisper_end_f=int(round(w['end']*30)), fa_end_f=int(round(wend[wi]*30)),
                        prob=round(w.get('probability', 0), 3)))
for o in out:
    o['d_start_f'] = o['fa_start_f'] - o['whisper_start_f']; o['d_end_f'] = o['fa_end_f'] - o['whisper_end_f']
json.dump(out, open('analysis/data/words_aligned.json', 'w'), indent=1)
d = np.array([o['d_start_f'] for o in out]); de = np.array([o['d_end_f'] for o in out])
print('aligned words', len(out), 'start diff frames: median', np.median(d), 'mean abs', np.abs(d).mean().round(2),
      '|d|<=1:', (np.abs(d) <= 1).mean().round(3), '|d|<=2:', (np.abs(d) <= 2).mean().round(3), 'n>2:', int((np.abs(d) > 2).sum()))
print('end diff frames: median', np.median(de), 'mean abs', np.abs(de).mean().round(2), '|d|<=2:', (np.abs(de) <= 2).mean().round(3))
