"""Sync map: unify all events on one frame timeline and derive statistical rules.

Inputs: words.json, sentences.json, cuts.json, shots.json, visual_review/part_*.jsonl, sfx_candidates.csv, beats.json, music.json
Outputs: analysis/data/visual_events.json (consolidated agent log, text matched to words)
         analysis/data/sync_map.csv (every event, one row each, sorted by frame)
         analysis/data/sync_stats.json (rules with numbers)
"""
import json, glob, re, numpy as np, pandas as pd
from difflib import SequenceMatcher

words = json.load(open('analysis/data/words.json')); sents = json.load(open('analysis/data/sentences.json'))
cuts = json.load(open('analysis/data/cuts.json')); shots = json.load(open('analysis/data/shots.json'))
sfx = pd.read_csv('analysis/data/sfx_candidates.csv'); beats = json.load(open('analysis/data/beats.json'))
music = json.load(open('analysis/data/music.json'))
W_on = np.array([w['start_f'] for w in words]); W_off = np.array([w['end_f'] for w in words])
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', s.lower().replace('-', ' ').replace('$', ' ')).split()
wtok = [norm(w['word']) for w in words]

# ---------- 1. consolidate agent events ----------
ev = []
for f in sorted(glob.glob('analysis/visual_review/part_*.jsonl')):
    part = int(re.search(r'part_(\d+)', f).group(1))
    for line in open(f):
        line = line.strip()
        if not line: continue
        try: r = json.loads(line)
        except Exception: continue
        try: f0 = int(r.get('f0'))
        except Exception: continue
        f1 = r.get('f1'); f1 = int(f1) if isinstance(f1, (int, float)) else None
        ev.append(dict(part=part, f0=f0, f1=f1, type=str(r.get('type', '')).lower(), cls=str(r.get('cls', '')).lower(),
                       text=str(r.get('text', '') or ''), where=str(r.get('where', '') or ''), anim=str(r.get('anim', '') or ''), note=str(r.get('note', '') or '')))
# dedupe: same type & cls & text within 3 frames
ev.sort(key=lambda e: (e['f0'], e['type']))
ded = []
for e in ev:
    if any(d['type'] == e['type'] and d['cls'] == e['cls'] and d['text'].lower() == e['text'].lower() and abs(d['f0']-e['f0']) <= 3 for d in ded[-30:]):
        continue
    ded.append(e)
ev = ded

# ---------- 2. match on-screen text to narration ----------
def match_text(e, win=120):
    toks = norm(e['text'])
    toks = [t for t in toks if t not in ('the', 'a', 'of', 'and', 'to')] or norm(e['text'])
    if not toks: return None
    lo = np.searchsorted(W_on, e['f0']-win); hi = np.searchsorted(W_on, e['f0']+win)
    best = None
    for i in range(lo, hi):
        for L in range(1, min(6, len(toks)+2)):
            span = [t for k in range(i, min(len(words), i+L)) for t in wtok[k]]
            if not span: continue
            sc = SequenceMatcher(None, ' '.join(toks), ' '.join(span)).ratio()
            if sc > 0.72 and (best is None or sc > best[0] + 0.02 or (abs(sc - best[0]) <= 0.02 and abs(words[i]['start_f']-e['f0']) < abs(words[best[1]]['start_f']-e['f0']))):
                best = (sc, i, L)
    if best is None: return None
    sc, i, L = best
    return dict(match_score=round(sc, 2), word_i=i, words=' '.join(words[k]['word'] for k in range(i, min(len(words), i+L))),
                word_onset_f=words[i]['start_f'], offset_f=e['f0']-words[i]['start_f'])
for e in ev:
    if e['type'] in ('text', 'ui') and e['text']:
        m = match_text(e)
        if m: e.update(m)
json.dump(ev, open('analysis/data/visual_events.json', 'w'), indent=1)

# ---------- 3. sync map rows ----------
rows = []
for w in words:
    rows.append(dict(frame=w['start_f'], kind='word_on', detail=w['word'], end=w['end_f']))
for s in sents:
    rows.append(dict(frame=s['start_f'], kind='sentence_on', detail=s['text'][:60], end=s['end_f']))
for c in cuts['hard_cuts']:
    rows.append(dict(frame=c, kind='cut', detail='hard', end=c))
for t in cuts['transitions']:
    rows.append(dict(frame=t['start'], kind='transition', detail=t['kind'], end=t['end']))
for e in ev:
    if e['type'] in ('text', 'graphic', 'ui', 'camera', 'fx', 'character'):
        rows.append(dict(frame=e['f0'], kind=f"{e['type']}:{e['cls']}", detail=e['text'][:40] or e['note'][:40], end=e['f1'] if e['f1'] is not None else e['f0']))
for _, s in sfx.iterrows():
    rows.append(dict(frame=int(s.frame), kind='sfx', detail=s.category_guess, end=int(s.frame + s.dur_ms/1000*30)))
for b in beats:
    rows.append(dict(frame=b['frame'], kind='beat', detail='', end=b['frame']))
sm = pd.DataFrame(rows).sort_values(['frame', 'kind']).reset_index(drop=True)
sm.to_csv('analysis/data/sync_map.csv', index=False)

# ---------- 4. statistics ----------
stats = {}
def nearest(arr, x):
    arr = np.asarray(arr); i = np.searchsorted(arr, x)
    c = [arr[j] for j in (i-1, i) if 0 <= j < len(arr)]
    return min(c, key=lambda v: abs(v-x)) if c else None
def pct(a, f):
    a = np.asarray(a); return round(float(f(a).mean()), 3) if len(a) else None

C = np.array(cuts['hard_cuts'])
# cuts vs word onsets
d_cut_word = np.array([c - nearest(W_on, c) for c in C])
# is cut inside a word (between onset and offset) or in a gap?
inside = np.array([any((W_on <= c) & (W_off > c)) for c in C])
# cuts vs sentence starts
S_on = np.array([s['start_f'] for s in sents])
d_cut_sent = np.array([c - nearest(S_on, c) for c in C])
# relation to the word that follows: cut leads the next word onset by k frames
nxt = []
for c in C:
    i = np.searchsorted(W_on, c)
    if i < len(W_on): nxt.append(W_on[i]-c)
nxt = np.array(nxt)
stats['cuts'] = dict(n=int(len(C)), per_minute=round(len(C)/(16731/30/60), 2),
    nearest_word_onset_offset_f=dict(median=float(np.median(d_cut_word)), within_pm1=pct(d_cut_word, lambda a: np.abs(a) <= 1), within_pm2=pct(d_cut_word, lambda a: np.abs(a) <= 2), within_pm3=pct(d_cut_word, lambda a: np.abs(a) <= 3)),
    share_cut_inside_a_word=pct(inside, lambda a: a),
    frames_until_next_word_onset=dict(median=float(np.median(nxt)), p25=float(np.percentile(nxt, 25)), p75=float(np.percentile(nxt, 75)), share_0_to_6=pct(nxt, lambda a: (a >= 0) & (a <= 6))),
    nearest_sentence_onset_offset_f=dict(median=float(np.median(d_cut_sent)), within_pm3=pct(d_cut_sent, lambda a: np.abs(a) <= 3), within_pm6=pct(d_cut_sent, lambda a: np.abs(a) <= 6)))
# share of sentences that get a cut at their start (within -6..+3 frames)
sent_has_cut = np.array([np.any((C - s >= -6) & (C - s <= 3)) for s in S_on])
stats['cuts']['share_sentences_with_cut_at_start'] = round(float(sent_has_cut.mean()), 3)
# cut offset relative to sentence onset for those within window
rel = np.array([c - nearest(S_on, c) for c in C if abs(c - nearest(S_on, c)) <= 8])
stats['cuts']['offset_to_sentence_onset_when_aligned_f'] = dict(n=int(len(rel)), median=float(np.median(rel)) if len(rel) else None, hist={int(k): int(v) for k, v in zip(*np.unique(rel, return_counts=True))})
# cuts in pauses: gap length when cut lands in a pause
gaps = []
for c in C:
    i = np.searchsorted(W_on, c)
    if 0 < i < len(W_on) and not any((W_on <= c) & (W_off > c)):
        gaps.append(W_on[i] - W_off[i-1])
stats['cuts']['pause_len_containing_cut_f'] = dict(median=float(np.median(gaps)), p25=float(np.percentile(gaps, 25)))
# shot length
L = np.array([s['frames'] for s in shots])
stats['shots'] = dict(n=int(len(L)), median_f=float(np.median(L)), mean_f=round(float(L.mean()), 1), p10_f=float(np.percentile(L, 10)), p25_f=float(np.percentile(L, 25)),
                      p75_f=float(np.percentile(L, 75)), p90_f=float(np.percentile(L, 90)), min_f=int(L.min()), max_f=int(L.max()))
# words per shot / sentences per shot
wps = []; sps = []
for s in shots:
    wps.append(int(((W_on >= s['start']) & (W_on <= s['end'])).sum())); sps.append(int(((S_on >= s['start']) & (S_on <= s['end'])).sum()))
stats['shots']['words_per_shot'] = dict(median=float(np.median(wps)), p90=float(np.percentile(wps, 90)))
stats['shots']['sentences_starting_per_shot'] = dict(median=float(np.median(sps)), share_1=pct(np.array(sps), lambda a: a == 1), share_0=pct(np.array(sps), lambda a: a == 0), share_ge2=pct(np.array(sps), lambda a: a >= 2))
# visual change rate (events per minute by minute): cuts + text + graphic
vis = sm[sm.kind.str.startswith(('cut', 'text', 'graphic', 'ui', 'transition'))]
vpm = vis.groupby(vis.frame // 1800).size()
stats['visual_events_per_minute'] = {int(k): int(v) for k, v in vpm.items()}
# text/ui elements vs their spoken words
te = [e for e in ev if 'offset_f' in e]
by = {}
for e in te:
    by.setdefault(e['cls'], []).append(e['offset_f'])
stats['text_vs_word_onset'] = {k: dict(n=len(v), median_f=float(np.median(v)), p25=float(np.percentile(v, 25)), p75=float(np.percentile(v, 75)),
                                         within_pm3=pct(np.array(v), lambda a: np.abs(a) <= 3), within_pm6=pct(np.array(v), lambda a: np.abs(a) <= 6))
                               for k, v in by.items() if len(v) >= 3}
allo = np.array([e['offset_f'] for e in te])
stats['text_vs_word_onset']['ALL'] = dict(n=int(len(allo)), median_f=float(np.median(allo)), p25=float(np.percentile(allo, 25)), p75=float(np.percentile(allo, 75)), within_pm3=pct(allo, lambda a: np.abs(a) <= 3), within_pm6=pct(allo, lambda a: np.abs(a) <= 6))
cls_counts = pd.Series([f"{e['type']}:{e['cls']}" for e in ev]).value_counts()
stats['element_counts'] = {k: int(v) for k, v in cls_counts.items() if v >= 3}
# SFX vs visual events
vis_f = np.array(sorted(set([int(x) for x in C] + [e['f0'] for e in ev if e['type'] in ('text', 'graphic', 'ui')] + [t['start'] for t in cuts['transitions']])))
sfx_off = np.array([int(f) - nearest(vis_f, int(f)) for f in sfx.frame])
sfx_cut = np.array([int(f) - nearest(C, int(f)) for f in sfx.frame])
stats['sfx'] = dict(n_candidates=int(len(sfx)), per_minute=round(len(sfx)/(16731/1800), 1),
    offset_to_nearest_visual_event_f=dict(median=float(np.median(sfx_off)), within_pm2=pct(sfx_off, lambda a: np.abs(a) <= 2), within_pm4=pct(sfx_off, lambda a: np.abs(a) <= 4)),
    offset_to_nearest_cut_f=dict(within_pm3=pct(sfx_cut, lambda a: np.abs(a) <= 3)))
# share of cuts with an SFX onset within [-6, +3]
cut_sfx = np.array([np.any((sfx.frame.values - c >= -6) & (sfx.frame.values - c <= 3)) for c in C])
stats['sfx']['share_cuts_with_sfx_m6_p3'] = round(float(cut_sfx.mean()), 3)
offs = [int(f) - c for c in C for f in sfx.frame.values if -6 <= int(f) - c <= 3]
stats['sfx']['cut_sfx_offset_hist'] = {int(k): int(v) for k, v in zip(*np.unique(offs, return_counts=True))} if offs else {}
# text elements with an SFX within [-3,+3] of first frame
txt_f = [e['f0'] for e in ev if e['type'] == 'text']
txt_sfx = np.array([np.any(np.abs(sfx.frame.values - f) <= 3) for f in txt_f])
stats['sfx']['share_text_elements_with_sfx_pm3'] = round(float(txt_sfx.mean()), 3)
for cl in ['stamp', 'name_tag', 'label', 'bubble', 'counter', 'list_line', 'chapter_card']:
    fs = [e['f0'] for e in ev if e['type'] in ('text', 'ui') and e['cls'] == cl]
    if fs:
        hit = [int(sfx.frame.values[np.argmin(np.abs(sfx.frame.values - f))]) - f for f in fs]
        hit = np.array(hit)
        stats['sfx'][f'{cl}_nearest_sfx_offset'] = dict(n=len(fs), median=float(np.median(hit)), within_pm3=pct(hit, lambda a: np.abs(a) <= 3))
# beats vs cuts (only segments with tempo_conf >= 0.15)
good = [s for s in music['segments'] if s.get('tempo_conf', 0) >= 0.15]
bfr = np.array(sorted(b['frame'] for b in beats if any(s['start_f'] <= b['frame'] <= s['end_f'] for s in good)))
cb = []
for c in C:
    if any(s['start_f'] <= c <= s['end_f'] for s in good):
        cb.append(c - nearest(bfr, c))
cb = np.array(cb)
# null model: random frames in same segments
rng = np.random.default_rng(0); null = []
seg_frames = np.concatenate([np.arange(s['start_f'], s['end_f']) for s in good])
for _ in range(2000):
    f = int(rng.choice(seg_frames)); null.append(f - nearest(bfr, f))
null = np.array(null)
stats['beats_vs_cuts'] = dict(n_cuts_in_confident_tempo_segments=int(len(cb)), within_pm2=pct(cb, lambda a: np.abs(a) <= 2), null_within_pm2=pct(null, lambda a: np.abs(a) <= 2))
json.dump(stats, open('analysis/data/sync_stats.json', 'w'), indent=1)
print(json.dumps(stats, indent=1)[:6000])
