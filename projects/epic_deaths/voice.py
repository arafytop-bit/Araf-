"""Narration for "Most Epic Deaths": voice B (Kokoro am_puck @1.25), tight pauses, word timings.

Outputs (next to this file):
  voice.wav        24 kHz mono narration
  sentences.json   per sentence: section, display text, tts text, start/end (s)
  words.json       per display word: text, sentence id, start/end (s)
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
MODEL_DIR = os.environ.get('KOKORO_DIR', '/tmp/claude-0/-home-user-Araf-/81de6a8a-0e7a-5a80-9554-3f626d2780df/scratchpad/build/tts')
VOICE, SPEED = 'am_puck', 1.25

# pronunciation respellings (voice only; on-screen text keeps the real spelling)
RESPELL = {
    'hardrada': 'Hard-rah-dah', 'kyiv': 'Keev', 'varangian': 'Vuh-ran-jee-un', 'heimskringla': 'Haymz-kring-lah',
    'snorri': 'Snorry', 'sturluson': 'Stur-loo-son', 'résumé': 'rez-oo-may', 'tycho': 'Tie-ko',
    "brahe's": "Brah-hee's", 'rasputin': 'Ras-pew-tin', 'bleda': 'Blay-dah', 'ildico': 'Ill-dee-ko',
    'jordanes': 'Jor-dah-neez', 'priscus': 'Priss-kus', 'licinius': 'Lih-sin-ee-us', 'carrhae': 'Carry',
    'bacchae': 'Back-eye', 'dio': 'Dee-oh', 'arrichion': 'Ar-rick-ee-on', "arrichion's": "Ar-rick-ee-on's",
    'phigalia': 'Fig-uh-lee-uh', 'pankration': 'pan-krat-ee-on', 'eryxias': 'Eh-rix-ee-us',
    'philostratus': 'Fil-oss-truh-tus', 'pausanias': 'Paw-say-nee-us', 'yi': 'Yee', "yi's": "Yee's",
    'sun-sin': 'Soon-sheen', 'seoul': 'Sole', 'hansan': 'Hahn-sahn', 'myeongnyang': 'Myung-nyahng',
    'noryang': 'Noh-ryahng', 'chen': 'Chun', 'chungmugong': 'Choong-moo-gong', 'mma': 'M M A', 'bc': 'B C',
    'godwinson': 'God-win-son', 'parthia': 'Par-thee-uh',
    # numbers as spoken
    '1066': 'ten sixty-six', '300': 'three hundred', '160': 'a hundred and sixty', '25th': 'twenty-fifth',
    '40': 'forty', '24': 'twenty-four', '449': 'four forty-nine', '2,100': 'twenty-one hundred',
    '453': 'four fifty-three', '500': 'five hundred', '53': 'fifty-three', '250': 'two hundred and fifty',
    '648': 'six forty-eight', '572': 'five seventy-two', '568': 'five sixty-eight', '564': 'five sixty-four',
    '25,000': 'twenty-five thousand', '1592': 'fifteen ninety-two', '150,000': 'a hundred and fifty thousand',
    '1597': 'fifteen ninety-seven', '133': 'a hundred and thirty-three', '200': 'two hundred', '31': 'thirty-one',
    '1598': 'fifteen ninety-eight', '16th': 'sixteenth', '100-won': 'hundred-won',
}
PLACEHOLDER = ('the video on your screen right now is about [YOUR END-SCREEN VIDEO].',
               'the video on your screen right now is your next stop.')


def tts_word(w):
    m = re.match(r'^([^\w\[$]*)(.*?)([^\w%]*)$', w, flags=re.UNICODE)
    pre, core, post = m.group(1), m.group(2), m.group(3)
    key = core.lower()
    if key in RESPELL:
        return pre + RESPELL[key] + post
    return w


def split_sentences(para):
    para = para.replace(PLACEHOLDER[0], PLACEHOLDER[1])
    parts = re.split(r'(?<=[.!?])["”]?\s+(?=[A-Z"“])', para)
    out = []
    for p in re.findall(r'.+?(?:[.!?]["”]?(?=\s+[A-Z"“]|$)|$)', para):
        p = p.strip()
        if p:
            out.append(p)
    return out or parts


def parse():
    sents = []
    section = 'intro'
    for raw in open(os.path.join(HERE, 'script.txt'), encoding='utf-8').read().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('@'):
            section = line[1:].strip().lower()
            continue
        if line.startswith('#'):
            section = line[1:].strip().rstrip('.')
            sents.append(dict(section=section, kind='title', text=line[1:].strip(), para_end=True))
            continue
        ss = split_sentences(line)
        for i, s in enumerate(ss):
            sents.append(dict(section=section, kind='line', text=s, para_end=(i == len(ss) - 1)))
    for i, s in enumerate(sents):
        s['id'] = i
        s['tts'] = ' '.join(tts_word(w) for w in s['text'].split())
    return sents


def tighten(s, sr, max_gap=0.11, keep=0.035):
    hop = int(0.005 * sr)
    n = len(s) // hop
    e = np.array([np.sqrt(np.mean(s[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    q = e < max(1e-4, 0.02 * np.percentile(e, 95))
    k = np.ones(len(s), bool)
    i = 0
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]:
                j += 1
            if i == 0:
                k[:max(0, j * hop - int(0.02 * sr))] = False
            elif j >= n:
                k[i * hop + int(0.04 * sr):] = False
            elif (j - i) * hop / sr > max_gap:
                k[i * hop + int(keep * sr):j * hop - int(keep * sr)] = False
            i = j
        else:
            i += 1
    return s[k]


def main():
    from kokoro_onnx import Kokoro
    from engine.align import align_chunk, norm_tokens
    k = Kokoro(os.path.join(MODEL_DIR, 'kokoro-v1.0.onnx'), os.path.join(MODEL_DIR, 'voices-v1.0.bin'))
    sents = parse()
    sr = 24000
    chunks, t = [], 0.0
    tmp = os.path.join(HERE, '_tmp16k.wav')
    words_out = []
    for idx, s in enumerate(sents):
        audio, sr = k.create(s['tts'], voice=VOICE, speed=SPEED, lang='en-us')
        audio = tighten(audio, sr)
        # leading gap
        if idx > 0:
            prev = sents[idx - 1]
            gap = 0.10
            if prev['para_end']:
                gap = 0.20
            if s['kind'] == 'title':
                gap = 0.40
            elif prev['kind'] == 'title':
                gap = 0.30
            if prev['section'] != s['section'] and s['kind'] != 'title':
                gap = 0.50
            chunks.append(np.zeros(int(gap * sr), np.float32))
            t += gap
        s['start'] = round(t, 3)
        chunks.append(audio.astype(np.float32))
        t += len(audio) / sr
        s['end'] = round(t, 3)
        # per-sentence alignment (16 kHz)
        import scipy.signal as ss
        a16 = ss.resample_poly(audio, 2, 3)
        sf.write(tmp, (np.clip(a16, -1, 1) * 32767).astype(np.int16), 16000, subtype='PCM_16')
        disp = s['text'].split()
        toks, owner = [], []
        for wi, w in enumerate(disp):
            for tk in norm_tokens(tts_word(w).replace('-', ' ')):
                toks.append(tk)
                owner.append(wi)
        _, al, err = align_chunk((idx, 0.0, len(a16) / 16000, ' '.join(toks), tmp))
        al = [a for a in al if a['w'] not in ('<s>', '</s>', '<sil>', '[NOISE]')]
        dur = len(audio) / sr
        if err or len(al) != len(toks):   # fallback: spread words by character length
            lens = np.array([max(1, len(w)) for w in disp], float)
            edges = np.concatenate([[0], np.cumsum(lens)]) / lens.sum() * dur
            for wi, w in enumerate(disp):
                words_out.append(dict(w=w, sid=idx, s=round(s['start'] + edges[wi], 3), e=round(s['start'] + edges[wi + 1], 3), est=True))
        else:
            for wi, w in enumerate(disp):
                ts = [a for a, o in zip(al, owner) if o == wi]
                if not ts:
                    continue
                words_out.append(dict(w=w, sid=idx, s=round(s['start'] + ts[0]['s'], 3), e=round(s['start'] + ts[-1]['e'], 3)))
        if idx % 25 == 0:
            print(f'{idx}/{len(sents)}  t={t:.1f}s', flush=True)
    os.remove(tmp)
    sf.write(os.path.join(HERE, 'voice.wav'), np.concatenate(chunks), sr)
    json.dump(sents, open(os.path.join(HERE, 'sentences.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(words_out, open(os.path.join(HERE, 'words.json'), 'w'), ensure_ascii=False)
    est = sum(1 for w in words_out if w.get('est'))
    print(f'done: {len(sents)} sentences, {len(words_out)} words ({est} estimated), {t / 60:.2f} min')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        for s in parse()[:12]:
            print(s['section'], '|', s['kind'], '|', s['tts'])
        print(len(parse()), 'sentences')
    else:
        main()
