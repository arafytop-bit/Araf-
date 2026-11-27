"""Word-timed timeline for v3: triggers -> frames, lazy sub-event triggers, beat compilation."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
VOICE_OFFSET = 0.10
W, H = 1920, 1080

WORDS = json.load(open(os.path.join(HERE, 'words.json')))
SENTS = json.load(open(os.path.join(HERE, 'sentences.json')))
for _w in WORDS:
    _w['s'] = round(_w['s'] + VOICE_OFFSET, 3)
    _w['e'] = round(_w['e'] + VOICE_OFFSET, 3)
for _s in SENTS:
    _s['start'] = round(_s['start'] + VOICE_OFFSET, 3)
    _s['end'] = round(_s['end'] + VOICE_OFFSET, 3)
LAST_WORD_END = SENTS[-1]['end']
OUTRO_S = 7.2                          # outro sting: enters 0.2 s after the last word, 6.5 s + fade (reference)
TOTAL_S = LAST_WORD_END + OUTRO_S
TOTAL_F = int(round(TOTAL_S * FPS))


def norm(t):
    t = t.lower().replace('’', "'").replace('‘', "'")
    return re.sub(r"[^a-z0-9']", '', t).strip("'")


NW = [norm(w['w']) for w in WORDS]


def fr(t):
    return int(round(t * FPS))


def find(phrase, start=0):
    """Index of the first word of `phrase` at/after word `start`. 'a b | c d' matches the whole phrase and returns
    the index of the word right after the bar (lets a short trigger be made unique by its context)."""
    pre = 0
    if '|' in phrase:
        left, right = phrase.split('|', 1)
        pre = len([x for x in left.split() if norm(x)])
        phrase = left + ' ' + right
    toks = [norm(x) for x in phrase.split() if norm(x)]
    n = len(toks)
    for i in range(start, len(NW) - n + 1):
        if NW[i:i + n] == toks:
            return i + pre
    raise KeyError(f'trigger not found after word {start} ({WORDS[start]["w"] if start < len(WORDS) else "END"}): {phrase!r}')


def cut_frame(i):
    """Cuts land one frame before the word onset (measured on the reference)."""
    return max(0, fr(WORDS[i]['s']) - 1)


def word_on(i):
    return fr(WORDS[i]['s'])


def word_off(i):
    return fr(WORDS[i]['e'])


class T:
    """Lazy trigger inside a beat: T('phrase') -> frame of the word onset (cut frame + 1 by default).
    T('phrase', end=True) -> frame the phrase's last word ends. off= adds frames."""
    __slots__ = ('phrase', 'end', 'off', 'cut')

    def __init__(self, phrase, end=False, off=0, cut=False):
        self.phrase, self.end, self.off, self.cut = phrase, end, off, cut

    def resolve(self, start_word):
        i = find(self.phrase, start_word)
        if self.end:
            n = len([x for x in self.phrase.split('|')[-1].split() if norm(x)])
            return word_off(i + n - 1) + self.off
        return (cut_frame(i) if self.cut else word_on(i)) + self.off

    def __repr__(self):
        return f'T({self.phrase!r})'


def resolve_all(obj, start_word):
    """Replace every T inside nested dicts/lists/tuples with a frame number."""
    if isinstance(obj, T):
        return obj.resolve(start_word)
    if isinstance(obj, dict):
        return {k: resolve_all(v, start_word) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_all(v, start_word) for v in obj]
    if isinstance(obj, tuple):
        return tuple(resolve_all(v, start_word) for v in obj)
    return obj


def sentence_of_frame(f):
    for s in SENTS:
        if fr(s['start']) <= f < fr(s['end']) + 3:
            return s
    return None


def words_between(f0, f1):
    return [k for k, w in enumerate(WORDS) if f0 <= fr(w['s']) < f1]


def tc(f):
    t = f / FPS
    return f'{int(t // 60)}:{t % 60:05.2f}'
