"""Storyboard -> frames -> video.  Phrase-anchored timeline, keyframed elements (linear), 2-drawing boil, camera.
Rendering: SVG per frame (cached drawer output + LRU frame cache) -> resvg -> raw RGB -> ffmpeg (parallel segments)."""
import json, math, io, os, sys, subprocess, hashlib, time
from collections import OrderedDict
import numpy as np, resvg_py
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import dd, props
from align import norm_parts

FPS = 30; W, H = 1920, 1080; LEAD = 1.0 / FPS; BOIL = 10          # boil: swap drawing every 10 frames (=8 @24fps)
BOIL_KINDS = {"person", "server_rack", "robot", "dog", "power_plant"}

def freeze(v):
    if isinstance(v, dict): return tuple(sorted((k, freeze(x)) for k, x in v.items()))
    if isinstance(v, (list, tuple)): return tuple(freeze(x) for x in v)
    if isinstance(v, float): return round(v, 3)
    return v

_draw_cache = {}
LINT_ERRORS = []
def draw(kind, seed, kw):
    key = (kind, seed, freeze(kw))
    s = _draw_cache.get(key)
    if s is None:
        if len(_draw_cache) > 6000: _draw_cache.clear()
        s = props.REG[kind](seed=seed, **kw); _draw_cache[key] = s
    return s

class Words:
    def __init__(self, path):
        self.w = json.load(open(path)); self.parts = [norm_parts(x["w"]) for x in self.w]; self.cursor = 0
    def find(self, phrase, start=None):
        tgt = []
        for tok in phrase.split(): tgt += norm_parts(tok)
        i0 = self.cursor if start is None else start
        for i in range(i0, len(self.w)):
            flat = []; j = i
            while len(flat) < len(tgt) and j < len(self.w): flat += self.parts[j]; j += 1
            if flat[:len(tgt)] == tgt: return i
        ctx = " ".join(x["w"] for x in self.w[i0:i0 + 25])
        if os.environ.get("LINT"):
            LINT_ERRORS.append(f"{phrase!r} not found after word {i0} «{ctx[:90]}»")
            return i0
        raise ValueError(f"anchor not found: {phrase!r} after word {i0}: «{ctx}»")
    def at(self, spec):
        """'phrase' -> first word; 'phrase|kw' -> word kw inside phrase. Moves cursor. Returns (time, word_index)."""
        if "|" in spec:
            ph, kw = spec.split("|", 1); i = self.find(ph); k = self.find(kw, i)
        else:
            k = i = self.find(spec)
        self.cursor = i
        t = max(0.0, self.w[k]["s"] - LEAD)
        return math.floor(t * FPS) / FPS, k
    def end_of(self, spec):
        i = self.find(spec); toks = spec.split(); j = i
        n = 0; tgt = sum(len(norm_parts(t)) for t in toks)
        while n < tgt and j < len(self.w): n += len(self.parts[j]); j += 1
        return self.w[j - 1]["e"]

class El:
    _n = 0
    def __init__(self, kind, t0, x=960, y=540, s=1.0, rot=0.0, op=1.0, boil=None, t1=None, wipe=None, wipe_box=None, seed=None, **kw):
        El._n += 1
        self.kind, self.t0, self.t1 = kind, t0, t1
        self.base = dict(x=x, y=y, s=s, rot=rot, op=op, wipe=wipe, **kw)
        self.wipe_box = wipe_box
        self.keys = []
        self.boil = (kind in BOIL_KINDS) if boil is None else boil
        self.seed = (El._n * 37) % 997 if seed is None else seed
        self.id = El._n
    def to(self, t, dur=0.0, **p):
        self.keys.append((t, dur, p)); self.keys.sort(key=lambda k: k[0]); return self
    def state(self, t):
        st = dict(self.base)
        for tk, dur, p in self.keys:
            if t < tk: break
            if dur > 0 and t < tk + dur:
                f = (t - tk) / dur
                for k, v in p.items():
                    a = st.get(k)
                    if isinstance(v, (int, float)) and isinstance(a, (int, float)) and not isinstance(v, bool): st[k] = a + (v - a) * f
                    else: st[k] = v
            else:
                st.update(p)
        return st
    def svg(self, t, frame):
        if t < self.t0 or (self.t1 is not None and t >= self.t1): return ""
        st = self.state(t)
        if st.get("op", 1) <= 0.001 or st.get("hide"): return ""
        seed = self.seed + ((frame // BOIL) % 2 if self.boil else 0)
        kw = {k: v for k, v in st.items() if k not in ("x", "y", "s", "rot", "op", "wipe", "hide", "sx", "sy")}
        for k in ("chars", "shown", "lit"):
            if k in kw and kw[k] is not None: kw[k] = int(kw[k])
        body = draw(self.kind, seed, kw)
        if st.get("wipe") is not None and st["wipe"] < 1 and self.wipe_box:
            x0, y0, w, h = self.wipe_box; cid = f"c{self.id}"
            body = f'<clipPath id="{cid}"><rect x="{x0:.1f}" y="{y0:.1f}" width="{max(0.0, w * st["wipe"]):.1f}" height="{h:.1f}"/></clipPath><g clip-path="url(#{cid})">{body}</g>'
        return dd.G(body, st["x"], st["y"], st["s"], st["rot"], st.get("op", 1.0), st.get("sx"), st.get("sy"))

class Scene:
    def __init__(self, t0, bg="#FFFFFF", name=""):
        self.t0, self.bg, self.name = t0, bg, name; self.els = []; self.cam = El("cam", t0, x=960, y=540, s=1.0)
    def add(self, el): self.els.append(el); return el
    def svg(self, t, frame):
        cs = self.cam.state(t)
        inner = "".join(e.svg(t, frame) for e in self.els)
        if abs(cs["s"] - 1) > 1e-4 or abs(cs["x"] - 960) > 0.05 or abs(cs["y"] - 540) > 0.05 or cs.get("rot", 0):
            inner = f'<g transform="translate(960 540) rotate({cs.get("rot",0):.2f}) scale({cs["s"]:.4f}) translate({-cs["x"]:.2f} {-cs["y"]:.2f})">{inner}</g>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                f'<rect width="{W}" height="{H}" fill="{self.bg}"/>{inner}</svg>')

class Board:
    def __init__(self, words_json):
        self.words = Words(words_json); self.scenes = []; self.sc = None; self.end = None; self.beats = []
    # --- anchors
    def T(self, spec):
        t, k = self.words.at(spec); return t
    # --- scenes & elements
    def cut(self, at=None, bg="#FFFFFF", name="", t=None):
        t0 = t if t is not None else (0.0 if at is None else self.T(at))
        self.sc = Scene(t0, bg, name or (at or "")); self.scenes.append(self.sc); self.beats.append(t0); return self.sc
    def add(self, kind, at=None, t=None, **kw):
        t0 = t if t is not None else (self.sc.t0 if at is None else self.T(at))
        if at is not None or t is not None: self.beats.append(t0)
        return self.sc.add(El(kind, t0, **kw))
    def at(self, spec): return self.T(spec)
    def finalize(self, end_t):
        # a cut happens when the scene's first element appears (no blank frames between a cut and its first visual)
        for sc in self.scenes:
            if sc.els:
                first = min(e.t0 for e in sc.els)
                if first > sc.t0 + 1e-6: sc.t0 = first
        self.scenes.sort(key=lambda s: s.t0); self.end = end_t
        # drop zero-length scenes
        keep = []
        for i, s in enumerate(self.scenes):
            nxt = self.scenes[i + 1].t0 if i + 1 < len(self.scenes) else end_t
            if nxt - s.t0 >= 1.0 / FPS - 1e-6: keep.append(s)
        self.scenes = keep
    def scene_at(self, t):
        lo = 0
        for i, s in enumerate(self.scenes):
            if s.t0 <= t + 1e-9: lo = i
            else: break
        return self.scenes[lo]
    def frame_svg(self, f):
        t = f / FPS; return self.scene_at(t).svg(t, f)

def rasterize(svg):
    png = resvg_py.svg_to_bytes(svg_string=svg, font_files=dd.FONT_FILES, skip_system_fonts=True)
    return Image.open(io.BytesIO(bytes(png))).convert("RGB")

def render_segment(board, f0, f1, out_path, crf=18, preset="medium", w=W, h=H, log=None):
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", "-g", "60", "-bf", "2", out_path], stdin=subprocess.PIPE)
    lru = OrderedDict(); t_start = time.time(); uniq = 0
    for f in range(f0, f1):
        svg = board.frame_svg(f); key = hashlib.md5(svg.encode()).digest()
        buf = lru.get(key)
        if buf is None:
            im = rasterize(svg)
            if (w, h) != (W, H): im = im.resize((w, h), Image.LANCZOS)
            buf = im.tobytes(); uniq += 1
            lru[key] = buf
            if len(lru) > 8: lru.popitem(last=False)
        else:
            lru.move_to_end(key)
        ff.stdin.write(buf)
        if log and (f - f0) % 900 == 0:
            print(f"[{out_path}] frame {f}/{f1} unique {uniq} elapsed {time.time()-t_start:.0f}s", flush=True)
    ff.stdin.close(); ff.wait()
    return uniq

def contact_sheet(board, times, out, cols=6, tw=384, th=216, words=None):
    from PIL import ImageDraw
    rows = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 34)), (40, 40, 40)); d = ImageDraw.Draw(sheet)
    for i, t in enumerate(times):
        f = int(round(t * FPS)); im = rasterize(board.frame_svg(f)).resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 34); sheet.paste(im, (x, y))
        cap = f"{t:7.2f}s"
        if words:
            ws = " ".join(w["w"] for w in words if t - 0.05 <= w["s"] < t + 1.6)
            cap += "  " + ws[:46]
        d.text((x + 4, y + th + 4), cap, fill=(255, 230, 120))
    sheet.save(out)
