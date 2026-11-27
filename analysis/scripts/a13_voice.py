"""Final word track + voice analysis.

Words: text = Whisper (with listed corrections), timing = MMS forced alignment (primary), Whisper (secondary).
Voice: pauses (frames), sentence stats, WPM / syllables per second, pitch (pYIN on vocal stem), long-term spectrum,
crest factor / dynamics, de-essing / reverb indicators.
Outputs: analysis/data/words.json, analysis/data/sentences.json, analysis/data/voice_stats.json, plots.
"""
import json, re, numpy as np, soundfile as sf, librosa, scipy.signal as sg
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

W = json.load(open('analysis/data/words_aligned.json'))
FIX = {'teams': 'teens'}   # obvious ASR slips verified against context
words = []
for i, w in enumerate(W):
    t = w['word']
    core = re.sub(r'[^\w\']', '', t).lower()
    if core in FIX and i > 0 and W[i-1]['word'].lower().startswith('your'):
        t = t.replace(core, FIX[core]).replace(core.capitalize(), FIX[core].capitalize())
    s = w['fa_start_s']; e = w['fa_end_s']
    words.append(dict(i=i, word=t, start_s=s, end_s=e, start_f=int(np.floor(s*30 + 1e-6)), end_f=int(np.ceil(e*30 - 1e-6)),
                      whisper_start_s=w['whisper_start_s'], dis_frames=abs(w['d_start_f']), flag=abs(w['d_start_f']) > 2))
# syllables (heuristic vowel-group count)
def syl(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w: return 0
    if re.fullmatch(r'\d+', word.strip('$,.')): return 2
    g = re.findall(r'[aeiouy]+', w)
    n = len(g)
    if w.endswith('e') and not w.endswith(('le', 'ee')) and n > 1: n -= 1
    return max(1, n)
for w in words:
    w['syllables'] = syl(w['word'])
# pauses
for k in range(len(words)-1):
    words[k]['pause_after_s'] = round(max(0.0, words[k+1]['start_s'] - words[k]['end_s']), 3)
words[-1]['pause_after_s'] = None
# sentences by terminal punctuation
sents = []; cur = []
for w in words:
    cur.append(w)
    if re.search(r'[.?!]["\']?$', w['word']):
        sents.append(cur); cur = []
if cur: sents.append(cur)
S = []
for k, s in enumerate(sents):
    txt = ' '.join(w['word'] for w in s)
    S.append(dict(i=k, text=txt, start_s=s[0]['start_s'], end_s=s[-1]['end_s'], start_f=s[0]['start_f'], end_f=s[-1]['end_f'],
                  n_words=len(s), question=txt.rstrip().endswith('?'), pause_after_s=s[-1]['pause_after_s']))
json.dump(words, open('analysis/data/words.json', 'w'), indent=1)
json.dump(S, open('analysis/data/sentences.json', 'w'), indent=1)

pa = np.array([w['pause_after_s'] for w in words[:-1]])
in_sent = []; between = []
for s in sents:
    for w in s[:-1]: in_sent.append(w['pause_after_s'])
    if s[-1]['pause_after_s'] is not None: between.append(s[-1]['pause_after_s'])
in_sent = np.array(in_sent); between = np.array(between)
speech_dur = words[-1]['end_s'] - words[0]['start_s']
nw = len(words); nsyl = sum(w['syllables'] for w in words)
# articulation rate: exclude pauses > 0.25 s
talk_time = sum(w['end_s']-w['start_s'] for w in words) + float(in_sent[in_sent <= 0.25].sum())
stats = dict(n_words=nw, n_sentences=len(S), first_word_s=words[0]['start_s'], last_word_end_s=words[-1]['end_s'],
             wpm_overall=round(nw/(speech_dur/60), 1), syllables_per_s_overall=round(nsyl/speech_dur, 2),
             articulation_syll_per_s=round(nsyl/talk_time, 2),
             words_per_sentence=dict(median=float(np.median([s['n_words'] for s in S])), mean=round(float(np.mean([s['n_words'] for s in S])), 1),
                                     p10=float(np.percentile([s['n_words'] for s in S], 10)), p90=float(np.percentile([s['n_words'] for s in S], 90)),
                                     max=int(max(s['n_words'] for s in S))),
             pause_within_sentence_frames=dict(median=round(float(np.median(in_sent))*30, 1), p75=round(float(np.percentile(in_sent, 75))*30, 1),
                                               p90=round(float(np.percentile(in_sent, 90))*30, 1), share_gt_150ms=round(float((in_sent > 0.15).mean()), 3)),
             pause_between_sentences_frames=dict(median=round(float(np.median(between))*30, 1), p25=round(float(np.percentile(between, 25))*30, 1),
                                                 p75=round(float(np.percentile(between, 75))*30, 1), p90=round(float(np.percentile(between, 90))*30, 1),
                                                 max=round(float(between.max())*30, 1)),
             questions=int(sum(s['question'] for s in S)),
             flagged_words_gt2f=int(sum(w['flag'] for w in words)))
# WPM per minute
per_min = []
for m0 in range(0, int(words[-1]['end_s'])+60, 60):
    ws = [w for w in words if m0 <= w['start_s'] < m0+60]
    per_min.append(dict(minute=m0//60, words=len(ws)))
stats['words_per_minute_by_minute'] = per_min

# ---- voice acoustics on the vocal stem ----
y, sr = sf.read('work/stems/vocals.wav', dtype='float32'); y = y.mean(1)
y22 = librosa.resample(y, orig_sr=sr, target_sr=22050)
f0, vflag, vprob = librosa.pyin(y22, fmin=60, fmax=400, sr=22050, frame_length=2048, hop_length=735)
f0v = f0[vflag & (vprob > 0.5)]
st = 12*np.log2(f0v/np.median(f0v))
stats['pitch'] = dict(median_hz=round(float(np.median(f0v)), 1), p5_hz=round(float(np.percentile(f0v, 5)), 1), p95_hz=round(float(np.percentile(f0v, 95)), 1),
                      range_p5_p95_semitones=round(float(np.percentile(st, 95)-np.percentile(st, 5)), 2), std_semitones=round(float(st.std()), 2))
# per-sentence pitch contour: start vs end (declination) and question rises
f0_frames = f0  # index = video frame (hop 735 @22.05k = 1/30 s)
decl = []
for s in S:
    seg = f0_frames[s['start_f']:s['end_f']+1]
    seg = seg[~np.isnan(seg)]
    if len(seg) > 10:
        a = np.median(seg[:max(3, len(seg)//4)]); b = np.median(seg[-max(3, len(seg)//4):])
        decl.append(12*np.log2(b/a))
stats['pitch']['sentence_start_to_end_semitones_median'] = round(float(np.median(decl)), 2)
# long-term average spectrum (speech-active frames)
fr, P = sg.welch(y, fs=sr, nperseg=8192)
Pdb = 10*np.log10(P+1e-20)
bands = [(80, 150), (150, 300), (300, 600), (600, 1200), (1200, 2500), (2500, 5000), (5000, 8000), (8000, 12000), (12000, 16000), (16000, 20000)]
ref = np.mean(Pdb[(fr >= 600) & (fr < 1200)])
stats['ltas_db_rel_600_1200'] = {f'{a}-{b}': round(float(np.mean(Pdb[(fr >= a) & (fr < b)]) - ref), 1) for a, b in bands}
hp = fr[np.argmax(fr > 20)]
low = Pdb[(fr > 20) & (fr < 300)]; frl = fr[(fr > 20) & (fr < 300)]
stats['low_cut_estimate_hz'] = float(frl[np.argmax(low > low.max()-12)])   # first freq within 12 dB of low-band max
# dynamics
env = librosa.feature.rms(y=y, frame_length=4410, hop_length=1470, center=False)[0]
envdb = 20*np.log10(env+1e-9); act = envdb > np.percentile(envdb, 40)
stats['dynamics'] = dict(rms_active_dbfs_median=round(float(np.median(envdb[act])), 1), rms_active_p10_p90_spread_db=round(float(np.percentile(envdb[act], 90)-np.percentile(envdb[act], 10)), 1),
                         crest_factor_db=round(float(20*np.log10(np.abs(y).max()/np.sqrt((y**2).mean()))), 1),
                         peak_dbfs=round(float(20*np.log10(np.abs(y).max())), 2))
# sibilance: energy 5-9 kHz relative to 1-3 kHz during active speech
S_ = np.abs(librosa.stft(y, n_fft=2048, hop_length=1470))
f_ = librosa.fft_frequencies(sr=sr, n_fft=2048)
sib = 10*np.log10((S_[(f_ > 5000) & (f_ < 9000)]**2).sum(0)+1e-12); body = 10*np.log10((S_[(f_ > 1000) & (f_ < 3000)]**2).sum(0)+1e-12)
d = (sib-body)[:len(act)][act[:S_.shape[1]]] if S_.shape[1] >= len(act) else (sib-body)
stats['sibilance_5_9k_minus_1_3k_db'] = dict(median=round(float(np.median(d)), 1), p99=round(float(np.percentile(d, 99)), 1))
# reverb indicator: decay slope after phrase ends (dB per 100 ms over first 200 ms after word end, pauses >= 400 ms)
slopes = []
e5 = 20*np.log10(np.sqrt(np.convolve(y**2, np.ones(220)/220, 'same'))+1e-9)
for w in words[:-1]:
    if w['pause_after_s'] and w['pause_after_s'] >= 0.4:
        a = int(w['end_s']*sr); b = a + int(0.2*sr)
        seg = e5[a:b:220]
        if len(seg) > 10 and seg[0] > -50:
            slopes.append((seg[-1]-seg[0])/2.0)
stats['tail_decay_db_per_100ms_median'] = round(float(np.median(slopes)), 1) if slopes else None
stats['tail_decay_n'] = len(slopes)
json.dump(stats, open('analysis/data/voice_stats.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in stats.items() if k != 'words_per_minute_by_minute'}, indent=1))
# plots: LTAS + pitch histogram
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
ax[0].semilogx(fr[1:], Pdb[1:]-ref); ax[0].set_xlim(40, 20000); ax[0].set_ylim(-60, 20); ax[0].grid(alpha=.3); ax[0].set_title('Voice LTAS (dB rel. 600-1200 Hz)')
ax[1].hist(f0v, bins=80); ax[1].set_title('Voice f0 histogram (Hz)')
plt.tight_layout(); plt.savefig('analysis/plots/voice_ltas_pitch.png', dpi=80)
