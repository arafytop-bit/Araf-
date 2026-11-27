"""Hook re-edit: open on the strongest curiosity line, keep every word of the narration.

Original intro order : 0 1 2 3 4 5 6 7 8 9 10 11 | 12 ...
New intro order      : 8 9 0 1 2 3 4 5 6 7 10 11 | 12 ...   (sentences are separated by digital silence -> clean splices)
  8  "One of these guys wins a fight after he's already dead."
  9  "Another wins a battle the same way."
  0  "These are the most epic deaths in human history."   (kinetic title, as the reference opens)
Writes v3/voice.wav, v3/words.json, v3/sentences.json (all later timings shift by the intro length change).
"""
import json
import os

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ORDER = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 10, 11]
GAP_AFTER = {8: 0.10, 9: 0.32, 0: 0.14, 7: 0.10, 10: 0.11, 11: 0.40}   # seconds of silence after each sentence
DEFAULT_GAP = 0.10


def main():
    v, sr = sf.read(os.path.join(SRC, 'voice.wav'))
    S = json.load(open(os.path.join(SRC, 'sentences.json')))
    Wd = json.load(open(os.path.join(SRC, 'words.json')))
    by_id = {s['id']: s for s in S}
    assert sorted(ORDER) == list(range(len(ORDER)))
    pieces, t, shift = [], 0.0, {}
    for k, sid in enumerate(ORDER):
        s = by_id[sid]
        a, b = s['start'], s['end']
        seg = v[int(round(a * sr)):int(round(b * sr))]
        shift[sid] = t - a
        pieces.append(seg)
        t += len(seg) / sr
        gap = GAP_AFTER.get(sid, DEFAULT_GAP)
        pieces.append(np.zeros(int(round(gap * sr)), v.dtype))
        t += gap
    rest_start = by_id[len(ORDER)]['start']
    tail_shift = t - rest_start
    pieces.append(v[int(round(rest_start * sr)):])
    out = np.concatenate(pieces)
    sf.write(os.path.join(HERE, 'voice.wav'), out, sr, subtype='PCM_16')
    S2 = []
    for s in S:
        d = shift.get(s['id'], tail_shift)
        S2.append(dict(s, start=round(s['start'] + d, 3), end=round(s['end'] + d, 3)))
    order_pos = {sid: k for k, sid in enumerate(ORDER)}
    S2.sort(key=lambda s: s['start'])
    W2 = []
    for w in Wd:
        d = shift.get(w['sid'], tail_shift)
        W2.append(dict(w, s=round(w['s'] + d, 3), e=round(w['e'] + d, 3)))
    W2.sort(key=lambda w: w['s'])
    json.dump(S2, open(os.path.join(HERE, 'sentences.json'), 'w'), indent=0)
    json.dump(W2, open(os.path.join(HERE, 'words.json'), 'w'))
    print(f'voice {len(out) / sr:.2f}s (was {len(v) / sr:.2f}s), tail shift {tail_shift:+.3f}s')
    for s in S2[:13]:
        print(f"  {s['start']:6.2f} {s['end']:6.2f}  {s['text'][:60]}")


if __name__ == '__main__':
    main()
