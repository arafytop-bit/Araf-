"""Align ASR word timestamps to the exact script text.

script tokens  -> normalized sub-words  (lowercase, hyphens split, numbers spelled out)
ASR words      -> normalized sub-words  (with times)
difflib alignment on sub-words, then every script word gets (start, end); unmatched
script words are interpolated between matched neighbours by character length.
"""
import re, json, difflib

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

def int_words(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + int_words(n % 100))
    for div, name in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= div:
            return int_words(n // div) + " " + name + ("" if n % div == 0 else " " + int_words(n % div))
    return str(n)

def year_words(n):
    if 2000 <= n <= 2009: return "two thousand" + ("" if n == 2000 else " " + ONES[n - 2000])
    hi, lo = divmod(n, 100)
    return int_words(hi) + " " + ("hundred" if lo == 0 else ("oh " + ONES[lo] if lo < 10 else int_words(lo)))

def num_token_words(tok):
    """'81%' -> 'eighty one percent', '$150' -> 'one hundred fifty dollars', '1983' -> year words, '1970s'."""
    m = re.fullmatch(r"\$?(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d+))?(s)?(%)?", tok)
    if not m: return tok
    ip = int(m.group(1).replace(",", "")); dec = m.group(2); plural = m.group(3); pct = m.group(4)
    if 1100 <= ip <= 2099 and dec is None and not pct and not tok.startswith("$"):
        w = year_words(ip)
        if plural:  # 1970s -> nineteen seventies
            parts = w.split(); last = parts[-1]
            parts[-1] = last[:-1] + "ies" if last.endswith("y") else last + "s"
            w = " ".join(parts)
        return w
    w = int_words(ip)
    if dec: w += " point " + " ".join(ONES[int(c)] for c in dec)
    if pct: w += " percent"
    if tok.startswith("$"): w += " dollars"
    return w

def norm_parts(tok):
    t = tok.lower().replace("’", "'").replace("‘", "'").replace("“", "").replace("”", "").replace('"', "")
    t = re.sub(r"[—–]", " ", t)
    out = []
    for piece in re.split(r"[\s\-/]+", t):
        piece = piece.strip(".,!?;:()[]…'")
        if not piece: continue
        if re.search(r"\d", piece):
            out += num_token_words(piece).split()
        else:
            p = re.sub(r"[^a-z0-9]", "", piece.replace("'", ""))
            if p: out.append(p)
    return out

def load_script(path):
    """Returns list of dicts: {i, raw, parts, section, para, punct_end, para_end, section_end}."""
    toks = []; section = None; para = 0
    lines = open(path, encoding="utf-8").read().splitlines()
    for li, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        if line.startswith("##"):
            section = line.lstrip("#").strip(); continue
        words = line.split()
        for k, w in enumerate(words):
            toks.append(dict(i=len(toks), raw=w, parts=norm_parts(w), section=section, para=para,
                             para_end=(k == len(words) - 1)))
        para += 1
    for k, t in enumerate(toks):
        t["section_end"] = (k == len(toks) - 1) or (toks[k + 1]["section"] != t["section"])
        raw = t["raw"].rstrip('"”’\')')
        t["punct"] = ("..." if raw.endswith("...") or raw.endswith("…") else
                      raw[-1] if raw and raw[-1] in ".?!:,;" else "")
    return toks

def align(script_toks, asr_words):
    """asr_words: list of {word,start,end}. Returns list (len = script tokens) of (start,end) or None + match stats."""
    S = []; S_owner = []
    for t in script_toks:
        for p in t["parts"]: S.append(p); S_owner.append(t["i"])
    A = []; A_time = []
    for w in asr_words:
        ps = norm_parts(w["word"]) or []
        n = max(1, len(ps)); dur = (w["end"] - w["start"]) / n
        for k, p in enumerate(ps):
            A.append(p); A_time.append((w["start"] + k * dur, w["start"] + (k + 1) * dur))
    sm = difflib.SequenceMatcher(a=S, b=A, autojunk=False)
    base = script_toks[0]["i"] if script_toks else 0
    times = {}
    matched = 0
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            si = S_owner[blk.a + k]; a0, a1 = A_time[blk.b + k]; matched += 1
            if si in times: times[si] = (min(times[si][0], a0), max(times[si][1], a1))
            else: times[si] = (a0, a1)
    res = [times.get(t["i"]) for t in script_toks]
    # interpolate gaps
    n = len(res); idx = [k for k in range(n) if res[k] is not None]
    for k in range(n):
        if res[k] is not None: continue
        prev = max([j for j in idx if j < k], default=None); nxt = min([j for j in idx if j > k], default=None)
        if prev is None and nxt is None: res[k] = (0.0, 0.0); continue
        if prev is None: res[k] = (res[nxt][0], res[nxt][0]); continue
        if nxt is None: res[k] = (res[prev][1], res[prev][1]); continue
        span0, span1 = res[prev][1], res[nxt][0]
        lens = [len(script_toks[j]["raw"]) for j in range(prev + 1, nxt)]; tot = sum(lens) or 1
        off = sum(len(script_toks[j]["raw"]) for j in range(prev + 1, k))
        a = span0 + (span1 - span0) * off / tot; b = span0 + (span1 - span0) * (off + len(script_toks[k]["raw"])) / tot
        res[k] = (a, b)
    return res, matched / max(1, len(S))
