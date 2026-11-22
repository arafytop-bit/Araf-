// Our cast as lit flat sprites in the 3D world. Each frame every character asks for a drawing (a key + a draw call);
// the pool keeps one canvas per distinct drawing, so soldiers marching in step share canvases (7 head shapes x 4
// outfits). Characters are yaw-only billboards shaded by cardShade() (scene tint, bright floor, side gradient toward
// the sun, painted crescent in the drawing); standing ones get a soft multiply contact blob. Effects are unlit cards.
// Cards, effects and blobs live on the NOINK layer so the world ink pass never outlines their quads.
import * as THREE from "three";
import { Pen, bodyFront, bodySide, soldier, fxBurst, fxSplash, fxStars, fxPuff, fxShadow, fxContact, fxDrum, Outfit, Expr, FrontOpts, SideOpts, INK } from "./toon";
import { FPS, SHOTS, V3, smooth, clamp01, SPOT, mp, PLACES, beachY, glide } from "./story";
import { SEA, GRAVE } from "./sets";
import { NOINK } from "./ink";
import { cardShade, blobMaterial, CARD_K } from "./cardshade";
import { fxFly, fxArrow, fxPam, fxEnvelope, fxReceipt, fxTickets, fxBankLetter, fxWallet, fxMoth, fxHook, fxTumble, fxTin, fxPlans, fxSparks, fxEngrave, fxTank, fxFlash, fxRipple } from "./fx";

// ---------------- canvas pool ----------------
type Entry = { cv: HTMLCanvasElement; tex: THREE.CanvasTexture; w: number; h: number };
export type Req = { key: string; w: number; h: number; k: number; draw: (p: Pen) => void; tex?: THREE.CanvasTexture };
const makeEntry = (w: number, h: number): Entry => {
  const cv = document.createElement("canvas");
  cv.width = w; cv.height = h;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { cv, tex, w, h };
};
export class Pool {
  private live = new Map<string, Entry>();
  private free: Entry[] = [];
  private reqs: Req[] = [];
  req(key: string, w: number, h: number, k: number, draw: (p: Pen) => void) {
    const r: Req = { key: `${w}x${h}|${key}`, w, h, k, draw };
    this.reqs.push(r);
    return r;
  }
  flush() {
    const want = new Map<string, Req[]>();
    for (const r of this.reqs) { const l = want.get(r.key); if (l) l.push(r); else want.set(r.key, [r]); }
    for (const [key, e] of this.live) if (!want.has(key)) { this.live.delete(key); this.free.push(e); }
    for (const [key, rs] of want) {
      let e = this.live.get(key);
      if (!e) {
        const r = rs[0], i = this.free.findIndex((x) => x.w === r.w && x.h === r.h);
        e = i >= 0 ? this.free.splice(i, 1)[0] : makeEntry(r.w, r.h);
        const g = e.cv.getContext("2d")!;
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, e.w, e.h); g.setTransform(r.k, 0, 0, r.k, 0, 0);
        r.draw(new Pen(g));
        e.tex.needsUpdate = true;
        this.live.set(key, e);
      }
      for (const r of rs) r.tex = e.tex;
    }
    this.reqs = [];
  }
}

// ---------------- sprite meshes ----------------
const blank = (() => { const c = document.createElement("canvas"); c.width = c.height = 2; return new THREE.CanvasTexture(c); })();
export const SU = 0.00216; // metres per design unit: 1000 units = 2.16 m
export const SU_SWING = 2.3 / 1830; // swing canvas: rope of 1830 units = 2.3 m
const BODY = (() => { const g = new THREE.PlaneGeometry(600 * SU, 1000 * SU); g.translate(0, (975 - 500) * SU, 0); return g; })();
const CARD = new THREE.PlaneGeometry(1, 1);
/** world roots that hold actors (to find the scene's sun when world.ts does not pass it) */
const ROOTS = new Set<THREE.Object3D>();

/** lit flat character: cardShade() material, receives shadows (dims to the bright floor only), casts its silhouette
 *  when world.ts says so (golden). Drawn after the contact blobs (renderOrder 1). */
export class Actor {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial; dmat: THREE.MeshDepthMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D, geo: THREE.BufferGeometry = BODY) {
    this.mat = cardShade(new THREE.MeshLambertMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.mat.alphaToCoverage = false; // A2C + MSAA left 1 px sky-depth seams on blurred far cards (POST)
    this.dmat = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.customDepthMaterial = this.dmat;
    // rim width is in output pixels: tell the card shader the render height (1920 = 1080 x 1920 frame)
    this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1920; };
    this.mesh.castShadow = false; this.mesh.receiveShadow = true; this.mesh.visible = false;
    this.mesh.rotation.order = "YXZ"; this.mesh.renderOrder = 1; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
    ROOTS.add(parent);
  }
  bind() { const t = this.r?.tex; if (t) { this.mat.map = t; this.dmat.map = t; } }
}
/** unlit effect card: hard cut-out (ink drawings), soft see-through (dust, mist) or a multiply ground blob */
export class Fx {
  mesh: THREE.Mesh; mat: THREE.MeshBasicMaterial; soft: THREE.MeshBasicMaterial; blob: THREE.MeshBasicMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D) {
    this.mat = new THREE.MeshBasicMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mat.alphaToCoverage = false; // A2C + MSAA left 1 px sky-depth seams on blurred far cards (POST)
    this.soft = new THREE.MeshBasicMaterial({ map: blank, transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.blob = blobMaterial(blank);
    this.mesh = new THREE.Mesh(CARD, this.mat);
    this.mesh.visible = false; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
  }
  use(soft: boolean) { this.mesh.material = soft ? this.soft : this.mat; }
  bind() {
    const t = this.r?.tex;
    if (!t) return;
    if (this.r!.key.includes("|blob|")) {
      // no mipmaps: at grazing views the mip chain averages the blob with its white surround and it fades out
      if (t.generateMipmaps) { t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.needsUpdate = true; }
      this.blob.map = t; this.mesh.material = this.blob; this.mesh.renderOrder = 0.5;
    }
    else { this.mat.map = t; this.soft.map = t; this.mesh.renderOrder = 0; }
  }
}

// ---------------- placements ----------------
export type Place = {
  key: string; draw: (p: Pen) => void; x: number; y: number; z: number;
  scale?: number; mirror?: boolean; yaw?: number; geo?: "body" | "swing"; roll?: number; size?: [number, number, number];
};
export type FxPlace = { key: string; cw: number; ch: number; draw: (p: Pen) => void; x: number; y: number; z: number; w: number; h: number; flat?: boolean; rot?: number; soft?: boolean; yaw?: number };
/** sun = world direction TOWARD the sun (optional: when absent the scene's shadow-casting light is used) */
export type CamInfo = { pos: THREE.Vector3; right: THREE.Vector3; sun?: THREE.Vector3 };

const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
const q = (v: number, n = 120) => Math.round(v * n) / n;
const vOf = (i: number) => (i * 7 + (i >> 2)) % 4;
/** head-shape seed: 7 shapes, so marching soldiers in step still share canvases */
const seedOf = (i: number) => ((i * 5 + 3) % 7) + 1;
/** drawing resolution by distance: [canvas w, h, scale from the 600 x 1000 design]; sized for the 1440 x 2560 final */
const tier = (d: number): [number, number, number] =>
  d < 3.2 ? [1800, 3000, 3.0] : d < 6.5 ? [1080, 1800, 1.8] : d < 16 ? [480, 800, 0.8] : [240, 400, 0.4];

// ---------------- light ----------------
const SUN = new THREE.Vector3(0.5, 0.75, -0.4).normalize();
const tmp = new THREE.Vector3();
let LNAME: "day" | "golden" = "day";
const sunOf = (root: THREE.Object3D) => {
  let s: THREE.DirectionalLight | null = null;
  root.traverse((o) => { if (!s && o instanceof THREE.DirectionalLight && o.castShadow) s = o; });
  return s as THREE.DirectionalLight | null;
};
/** the sun of the world that is calling: the attached root whose sun target sits on this camera's view axis */
const findSun = (cam: CamInfo, out: THREE.Vector3) => {
  if (cam.sun) return out.copy(cam.sun).normalize();
  let best: THREE.DirectionalLight | null = null, err = Infinity;
  for (const r of ROOTS) {
    if (!r.parent) continue;
    const s = sunOf(r);
    if (!s) continue;
    const d = tmp.copy(s.target.position).sub(cam.pos), e = Math.abs(d.dot(cam.right)) / (d.length() || 1);
    if (e < err) { err = e; best = s; }
  }
  return best ? out.copy(best.position).sub(best.target.position).normalize() : out;
};
/** canvas angle the sun comes FROM on an upright card facing the camera, in 45-degree steps (small texture cache) */
const light2D = (cam: CamInfo, mirror: boolean) => {
  const sx = SUN.dot(cam.right) * (mirror ? -1 : 1), sy = -SUN.y;
  return Math.round(Math.atan2(sy, sx) / (Math.PI / 4)) * (Math.PI / 4);
};

/** front / side view and mirroring for someone at (x, z) walking along (dx, dz); fs = foreshortening of the walk */
const viewOf = (cam: CamInfo, x: number, z: number, dx: number, dz: number) => {
  const tx = cam.pos.x - x, tz = cam.pos.z - z, tl = Math.hypot(tx, tz) || 1;
  const c = (tx * dx + tz * dz) / tl;
  return { side: c < 0.57, mirror: dx * cam.right.x + dz * cam.right.z < 0, fs: Math.round(Math.sqrt(Math.max(0, 1 - c * c)) * 20) / 20 };
};

// ---------------- life: blinks and reaction timing ----------------
/** reference expression and action changes land 0-3 f before the word onset */
const LEAD = 2 / FPS;
/** eyelid 0 open .. 1 shut. Reference: gaps 0.5-2.3 s, 4-frame blink half / shut / shut / half, plus a blink across
 *  every expression swap (the shut frames hide the swap) */
const LID = [0.5, 1, 1, 0.5];
const lidAt = (t: number, i: number, swaps: number[] = []) => {
  const f = Math.round(t * FPS);
  for (const ts of swaps) { const k = f - Math.round((ts - LEAD) * FPS) + 1; if (k >= 0 && k < 4) return LID[k]; }
  let s = Math.round(-60 * hh(i, 9));
  for (let n = 0; s <= f && n < 400; n++) {
    const k = f - s;
    if (k >= 0 && k < 4) return LID[k];
    s += Math.round(15 + 54 * hh(i * 31 + n, 13)); // next blink 0.5-2.3 s later
  }
  return 0;
};
const fkey = (o: object) => JSON.stringify(o, (_k, v) => (typeof v === "number" ? q(v) : v));

type Who = { i: number; o: Outfit; okey: string };
/** one character drawing in the 600 x 1000 design space, sized by distance, lit from the scene's sun */
const person = (cam: CamInfo, who: Who, x: number, y: number, z: number, view: { side: boolean; mirror: boolean }, fo: FrontOpts, so: SideOpts, scale = 1): Place & { tierKey: string } => {
  const d = cam.pos.distanceTo(tmp.set(x, y + 1.2, z)) / scale;
  const [w, h, k] = tier(d);
  const mirror = view.side && view.mirror, light = light2D(cam, mirror), seed = seedOf(who.i);
  const f2: FrontOpts = { ...fo, light, seed }, s2: SideOpts = { ...so, light, seed };
  const key = view.side ? `S|${who.okey}|${fkey(s2)}` : `F|${who.okey}|${fkey(f2)}`;
  return {
    key, x, y, z, scale, mirror, tierKey: `${w}`,
    draw: (p) => (view.side ? bodySide(p, who.o, s2) : bodyFront(p, who.o, f2)),
    size: [w, h, k],
  };
};

/** ground shadow under a standing / sitting card (review rounds 2-4), multiply, blue-violet: a TIGHT contact pool right under
 *  the feet (~.5 on screen at the core) so nobody floats, plus by day (cards cast no real shadow) a lighter soft tail
 *  stretched AWAY from the sun, length ~1.6 m / tan(sun elevation), capped. Golden: world.ts casts real card shadows. */
const CONTACT: Record<"day" | "golden", [number, number, number]> = { day: [0.2, 0.21, 0.33], golden: [0.24, 0.2, 0.33] };
const TAIL: [number, number, number] = [0.42, 0.44, 0.62];
const toSrgb = (v: number) => { const c = clamp01(v); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; };
const hexOf = (c: [number, number, number], k: number) => "#" + c.map((v) => Math.round(255 * toSrgb(1 - (1 - v) * k)).toString(16).padStart(2, "0")).join("");
const blob = (out: Stage, x: number, y: number, z: number, sc = 1, k = 1) => {
  const hl = Math.hypot(SUN.x, SUN.z) || 1, ox = -SUN.x / hl, oz = -SUN.z / hl, rot = Math.atan2(-ox, -oz);
  if (LNAME === "day") {
    const el = Math.asin(Math.min(0.99, Math.max(0.1, SUN.y)));
    const len = Math.min(2.4, Math.max(0.5, 1.6 / Math.tan(el))) * sc, h = len + 0.55 * sc, c = 0.3 * h; // feet at v = .2 of the card
    const tc = hexOf(TAIL, k);
    out.fx.push({ key: `blob|shadow|${tc}`, cw: 128, ch: 256, draw: (p) => fxShadow(p, tc), x: x + ox * c, y: y + 0.018, z: z + oz * c,
      w: 0.72 * sc, h, flat: true, rot });
  }
  const cc = hexOf(CONTACT[LNAME], k);
  out.fx.push({ key: `blob|contact|${cc}`, cw: 128, ch: 128, draw: (p) => fxContact(p, cc), x: x + ox * 0.03 * sc, y: y + 0.022, z: z + oz * 0.03 * sc,
    w: 0.52 * sc, h: 0.4 * sc, flat: true, rot });
};

// ---------------- crowd by shot ----------------
export type Stage = { places: Place[]; fx: FxPlace[] };

// ================= the Mincemeat cast =================
const PALE = "#e2e6d6";
const MARINE: Outfit = { jacket: "#7d7048", pants: "#6f6342", boots: "#3a2a20", hat: "peaked", cap: "#7a6c45", tie: "#5e4e32", buttons: "#d9c58a" };
const CORPSE: Outfit = { ...MARINE, skin: PALE };
const VEST: Outfit = { jacket: "#f2efe6", pants: "#8a8f96", boots: INK, hat: "hair", hair: "#4a3426", vest: true, skin: PALE };
const MONTAGU: Outfit = { jacket: "#26324f", pants: "#26324f", boots: INK, hat: "peaked", cap: "#1f2738", buttons: "#e8c45a", tie: "#1d1d24" };
const CHOL: Outfit = { jacket: "#5d6f8e", pants: "#5d6f8e", boots: INK, hat: "peaked", cap: "#4f5f7a", moustache: "#6a4a2a", tie: "#2a2f3a" };
const HITLER: Outfit = { jacket: "#7b7254", pants: "#2e2b28", boots: INK, hat: "hair", hair: "#2a201a", brush: true, forelock: true, buttons: "#d9c58a" };
const SPY = (v: number): Outfit => ({ jacket: ["#b69a68", "#a88c5c", "#c2a878"][v % 3], pants: "#4a4a52", boots: INK, hat: "fedora", cap: ["#5e5a50", "#4a4440", "#6b5a48"][v % 3], tie: "#7a2a2a", skin: ["#ffe2c2", "#f5c9a0", "#ecd0b6"][v % 3], ...(v % 2 ? { moustache: "#3a2a20" } : {}) });
const OFFICIAL: Outfit = { jacket: "#efe7d2", pants: "#efe7d2", boots: "#5a3b2a", hat: "hair", hair: "#2a2a2a", moustache: "#2a2a2a", tie: "#3f6fb5", skin: "#e8b98e" };
const FISHER: Outfit = { jacket: "#3f6fb5", pants: "#e9e4d6", boots: "#5a3b2a", hat: "beret", cap: "#2a2a35", skin: "#c99067", moustache: "#3a2a20" };
const CREW = (v: number): Outfit => ({ jacket: "#2b3550", pants: "#2b3550", boots: INK, hat: "cap", cap: ["#2b3550", "#f1ece0", "#2b3550"][v % 3], vest: true, skin: ["#ffe2c2", "#f5c9a0", "#ecd0b6"][v % 3] });
const GLYNDWR: Outfit = { jacket: "#6b5a44", pants: "#4d4a44", boots: "#3a2a20", hat: "cap", cap: "#6e6a60", vest: true };
const MASON: Outfit = { jacket: "#8a8f96", pants: "#5a5a60", boots: "#3a2a20", hat: "cap", cap: "#3a3d47", vest: true, skin: "#d9a57a" };
const PASSER = (v: number): Outfit => v % 2
  ? { jacket: ["#8c3b4a", "#3f6fb5", "#5d7a3a"][v % 3], pants: "#3b3f52", boots: "#4a3426", hat: "hair", hair: ["#5a3b2a", "#c9a24a", "#2a201a"][v % 3], dress: ["#8c3b4a", "#3f6fb5", "#5d7a3a"][v % 3] }
  : { jacket: ["#5a5a62", "#6b5a48", "#3f4a5a"][v % 3], pants: "#3b3f52", boots: INK, hat: "fedora", cap: ["#3a3d47", "#5e5a50", "#2e2a36"][v % 3], tie: "#8c3b4a" };
const BANDSMAN = (v: number): Outfit => soldier(v, { jacket: "#c0393f", belt: "#f1efe6", rifle: false });

const L = LEAD;
const tF = (f: number) => f / FPS;
type FigO = { i: number; o: Outfit; key: string; p: V3; fo?: FrontOpts; scale?: number; blob?: boolean; roll?: number; side?: { dx: number; dz: number; so: SideOpts } };
const fig = (cam: CamInfo, t: number, out: Stage, g: FigO) => {
  const fo: FrontOpts = { mode: "stand", ...g.fo };
  if (fo.blink === undefined) fo.blink = lidAt(t, g.i);
  const who = { i: g.i, o: g.o, okey: g.key };
  const view = g.side ? viewOf(cam, g.p[0], g.p[2], g.side.dx, g.side.dz) : { side: false, mirror: false };
  const so: SideOpts = g.side ? { ...g.side.so, blink: lidAt(t, g.i) } : {};
  const pl = person(cam, who, g.p[0], g.p[1], g.p[2], view, fo, so, g.scale ?? 1);
  if (g.roll !== undefined) pl.roll = g.roll;
  out.places.push(pl);
  if (g.blob !== false) blob(out, g.p[0], g.p[1], g.p[2], g.scale ?? 1);
};
const add3 = (a: V3, x: number, y: number, z: number): V3 => [a[0] + x, a[1] + y, a[2] + z];
const u01 = (f: number, a: number, b: number) => clamp01((f - a) / (b - a));
/** flat card lying on a surface from p0 to p1 (arrows on the map) */
const flatArrow = (out: Stage, key: string, p0: V3, p1: V3, k: number, col: string, wide = 0.11) => {
  if (k <= 0) return;
  const dx = p1[0] - p0[0], dz = p1[2] - p0[2], len = Math.hypot(dx, dz), w = (len * 512) / 460;
  const ux = dx / len, uz = dz / len, c = w / 2 - (20 / 512) * w;
  const kq = q(k, 24);
  out.fx.push({ key: `arrow|${col}|${kq}`, cw: 512, ch: 256, draw: (p) => fxArrow(p, kq, col), x: p0[0] + ux * c, y: p0[1] + 0.004, z: p0[2] + uz * c,
    w, h: wide, flat: true, rot: Math.atan2(-dz, dx) });
};
const puff = (out: Stage, f: number, f0: number, at: V3, s = 1) => {
  const u = (f - f0) / 14;
  if (u < 0 || u >= 1) return;
  const uq = q(u, 15);
  out.fx.push({ key: `puff${uq}`, cw: 300, ch: 300, draw: (p) => fxPuff(p, uq), x: at[0], y: at[1], z: at[2], w: 0.9 * s, h: 0.9 * s, soft: true });
};
/** pop-in scale for a card that appears at frame f0 (overshoot, settles in 8 f) */
const pop = (f: number, f0: number) => (f < f0 ? 0 : f - f0 >= 8 ? 1 : 1 + 0.35 * Math.sin(((f - f0) / 8) * Math.PI) * (1 - (f - f0) / 8) + ((f - f0) < 2 ? -0.4 : 0));
const tank = (out: Stage, at: V3, col: string, flip = false, s = 1) =>
  out.fx.push({ key: `tank|${col}`, cw: 512, ch: 256, draw: (p) => fxTank(p, col), x: at[0], y: at[1] + 0.035 * s, z: at[2], w: (flip ? -0.15 : 0.15) * s, h: 0.075 * s });

export const stage = (id: number, t: number, cam: CamInfo, f: number): Stage => {
  const out: Stage = { places: [], fx: [] };
  const s = SHOTS[id - 1];
  LNAME = s.light;
  findSun(cam, SUN);
  const C = SPOT;
  switch (id) {
    case 1: {
      fig(cam, t, out, { i: 1, o: CORPSE, key: "corpse", p: C.corpseHook, fo: { expr: "dead", blink: 0, prop: "briefcase", facing: 0 } });
      fig(cam, t, out, { i: 2, o: MONTAGU, key: "montagu", p: C.montaguTable, fo: { expr: f < 109 - 2 ? "smug" : "stern", look: -1 } });
      fig(cam, t, out, { i: 3, o: CHOL, key: "chol", p: add3(C.montaguTable, 1.15, 0, -0.1), fo: { expr: f < 143 - 2 ? "neutral" : "nervous", look: -1 } });
      if (f >= 172) { // a fly circles the agent's head from "no pulse"
        const a = (f - 172) * 0.32, h = add3(C.corpseHook, 0, 1.66, 0);
        out.fx.push({ key: `fly${f % 2}`, cw: 256, ch: 256, draw: (p) => fxFly(p, f % 2), x: h[0] + 0.3 * Math.cos(a), y: h[1] + 0.1 * Math.sin(a * 2), z: h[2] + 0.12 * Math.sin(a) + 0.3, w: 0.1, h: 0.1 });
      }
      break;
    }
    case 2: case 5: case 19: {
      const e: Expr = id === 2 ? (f < 247 - 2 ? "smug" : "grin") : id === 5 ? "stern" : f < 2065 ? (f < 2040 ? "neutral" : "shock") : f < 2093 ? "chomp" : "lick";
      const wave = id === 5 ? 0.15 : id === 2 && f > 250 ? 0.6 : undefined;
      fig(cam, t, out, { i: 4, o: HITLER, key: "hitler", p: C.hitler, fo: { expr: e, wave, prop: id === 19 && f < 2040 ? "paper" : null, look: id === 5 ? -1 : 0 } });
      if (id === 5) for (const [k, dl] of [[0, 0], [1, 0.5], [2, -0.4]] as const) tank(out, mp(13.5 + dl, 37.4 + 0.25 * k, 0, true), "#7b8089", k % 2 === 1);
      if (id === 19) { // the hook comes down with the letter as bait; he swallows it whole
        const bait = f < 2071;
        const down = glide(u01(f, 2026, 2058)), up = glide(u01(f, 2073, 2095));
        const yb = 1.53 + (1 - down) * 1.4 + up * 1.6; // bottom of the card (bait at the mouth line)
        if (yb < 3.4) out.fx.push({ key: `hook${bait}`, cw: 256, ch: 1024, draw: (p) => fxHook(p, bait), x: C.hitler[0] + 0.06, y: C.hitler[1] + yb + 0.65, z: C.hitler[2] + 0.3, w: 0.33, h: 1.3 });
      }
      break;
    }
    case 3: case 6: {
      const p0 = mp(10.6, 36.9), p1 = mp(13.4, 37.3);
      flatArrow(out, "sicily", p0, p1, id === 3 ? glide(u01(f, 326, 350)) : 1, "#3f6fb5");
      for (const [k, dl] of [[0, 0], [1, 0.5], [2, -0.5]] as const) tank(out, mp(9.4 + dl, 36.0 - 0.25 * k), "#6b7a3a", false, 0.9);
      tank(out, mp(14.6, 37.6), "#7b8089", true, 0.8); tank(out, mp(13.6, 37.25), "#7b8089", true, 0.8);
      if (id === 6) { // a tiny marching band crosses from Tunisia to Sicily
        const u = (f - 451) / (577 - 451), dx = p1[0] - p0[0], dz = p1[2] - p0[2];
        const phase = (t * 2) % 1;
        for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) {
          const along = u * 0.88 - r * 0.07, side = (c - 1) * 0.045;
          const len = Math.hypot(dx, dz), x = p0[0] + dx * along + (-dz / len) * side, z = p0[2] + dz * along + (dx / len) * side;
          fig(cam, t, out, { i: 20 + r * 3 + c, o: BANDSMAN(r * 3 + c), key: `band${(r * 3 + c) % 4}`, p: [x, p0[1], z], scale: 0.06, blob: false,
            side: { dx, dz, so: { mode: "march", phase: (phase + (r % 2) * 0.02) % 1, expr: r === 0 && c === 1 ? "whistle" : "grin", stride: 1 } } });
          if (r === 0 && c === 1) out.fx.push({ key: "drum", cw: 260, ch: 260, draw: fxDrum, x: x + dx / len * 0.012, y: p0[1] + 0.06 + 0.004 * Math.cos(phase * 4 * Math.PI), z: z + dz / len * 0.012 + 0.008, w: 0.045, h: 0.045 });
        }
      }
      break;
    }
    case 4:
      fig(cam, t, out, { i: 2, o: MONTAGU, key: "montagu", p: C.montaguTable, fo: { expr: "nervous", look: 0 } });
      break;
    case 7: case 12: {
      const weird = id === 7 && f >= 649 - 2;
      fig(cam, t, out, { i: 2, o: MONTAGU, key: "montagu", p: C.montaguDesk, fo: { expr: id === 12 ? "grin" : weird ? "grin" : "stern", look: weird || id === 12 ? 0 : 1, prop: id === 12 ? "photo" : null } });
      fig(cam, t, out, { i: 3, o: CHOL, key: "chol", p: C.cholDesk, fo: { expr: id === 12 ? (f < 1219 ? "smug" : "smile_closed") : weird ? "laugh" : "neutral", look: weird || id === 12 ? 0 : -1, prop: id === 12 ? "paper" : null } });
      break;
    }
    case 8: {
      const dressed = f >= 713 - 1, brief = f >= 789 - 1;
      fig(cam, t, out, { i: 1, o: dressed ? CORPSE : VEST, key: dressed ? "corpse" : "vest", p: C.corpseDress, fo: { expr: "dead", blink: 0, prop: brief ? "briefcase" : null } });
      fig(cam, t, out, { i: 2, o: MONTAGU, key: "montagu", p: C.montaguDress, fo: { expr: f < 690 ? "neutral" : "grin", look: -1, prop: f < 833 ? "paper" : null } });
      fig(cam, t, out, { i: 3, o: CHOL, key: "chol", p: C.cholDress, fo: { expr: f < 740 ? "smug" : "smile_closed", look: 1, wave: f >= 713 && f < 760 ? 0.4 : undefined } });
      puff(out, f, 713 - 1, add3(C.corpseDress, 0, 1.0, 0.15), 1.6);
      puff(out, f, 789 - 1, add3(C.corpseDress, -0.35, 0.75, 0.15), 0.8);
      if (f >= 831 && f < 858) { // the fake plans fly from Montagu's hand into the briefcase
        const u = glide(u01(f, 831, 856)), a = add3(C.montaguDress, 0.35, 1.05, 0.15), b = add3(C.corpseDress, -0.33, 0.72, 0.15);
        const sz = 0.34 - 0.24 * u;
        out.fx.push({ key: "plans", cw: 512, ch: 512, draw: fxPlans, x: a[0] + (b[0] - a[0]) * u, y: a[1] + (b[1] - a[1]) * u + 0.35 * Math.sin(u * Math.PI), z: a[2] + (b[2] - a[2]) * u, w: sz, h: sz, rot: u * 2.5 });
      }
      break;
    }
    case 10: {
      const spots: [number, number][] = [[-0.2, -161.2], [1.5, -163.6], [2.6, -160.6], [3.6, -165.2], [-1.4, -165.8], [0.6, -167.5], [-2.0, -163.0]];
      spots.forEach(([x, z], i) => {
        const zA = SEA[2] + z;
        fig(cam, t, out, { i: 30 + i, o: SPY(i), key: `spy${i % 3}${i % 2}`, p: [SEA[0] + x, beachY(zA), zA], fo: { expr: i % 3 === 0 ? "smug" : i % 3 === 1 ? "stern" : "smile", look: i % 2 ? 1 : -1, prop: i === 1 ? "camera" : i === 4 ? "paper" : null } });
      });
      break;
    }
    case 11: case 23: {
      const sick = id === 11 && f >= 1115 - 2;
      fig(cam, t, out, { i: 5, o: GLYNDWR, key: "glyndwr", p: C.bench, fo: { mode: "sit", expr: sick ? "dazed" : id === 23 ? "neutral" : "smile", look: id === 23 ? 1 : 0 } });
      if (id === 11) out.fx.push({ key: "tin", cw: 384, ch: 384, draw: fxTin, x: C.tin[0], y: C.tin[1] + 0.08, z: C.tin[2], w: 0.2, h: 0.2 });
      if (sick && f >= 1125) {
        const u = ((f - 1125) / 20) % 1, uq = q(u, 20);
        out.fx.push({ key: `stars${uq}`, cw: 420, ch: 210, draw: (p) => fxStars(p, uq), x: C.bench[0], y: C.bench[1] + 1.42, z: C.bench[2] + 0.05, w: 0.6, h: 0.3 });
      }
      // passers-by on the pavement, nobody looks at him
      const walkers: [number, number, number][] = id === 23 ? [[-7.45, -3.0, 1.35], [-7.75, 7.5, -1.25], [-7.35, -6.5, 1.3]] : [[9.2, -4, 1.3], [8.8, 6, -1.2]];
      walkers.forEach(([x, z0, v], i) => {
        const z = z0 + v * (t - tF(s.a)), ph = ((t * 1.7 + i * 0.37) % 1);
        fig(cam, t, out, { i: 40 + i, o: PASSER(i + (id === 23 ? 3 : 0)), key: `pass${i}${id}`, p: [STREETX(x), 0.12, STREETZ(z)],
          side: { dx: 0, dz: Math.sign(v), so: { mode: "march", phase: ph, expr: i % 2 ? "smile" : "neutral", stride: 0.85, stomp: 0.6 } } });
      });
      break;
    }
    case 13: {
      const d = C.deskTop;
      const items: [number, number, number, number, number, number, string, (p: Pen) => void, number, number][] = [
        // f0, x, z, w, h, rot, key, draw, cw, ch
        [1253, -0.55, 0.02, 0.34, 0.255, 0.1, "wallet", fxWallet, 512, 384],
        [1257, -0.36, -0.06, 0.2, 0.25, -0.2, "pam", fxPam, 512, 640],
        [1321, -0.12, 0.06, 0.22, 0.165, 0.25, "env1", (p) => fxEnvelope(p, true), 512, 384],
        [1328, -0.02, -0.07, 0.22, 0.165, -0.15, "env2", (p) => fxEnvelope(p, true), 512, 384],
        [1360, 0.2, 0.03, 0.12, 0.2, 0.18, "receipt", fxReceipt, 384, 640],
        [1417, 0.4, -0.04, 0.24, 0.15, -0.1, "tickets", fxTickets, 512, 320],
        [1459, 0.64, 0.02, 0.2, 0.25, 0.08, "bank", fxBankLetter, 512, 640],
      ];
      items.forEach(([f0, x, z, w, h, rot, key, draw, cw, ch], i) => {
        const k = pop(f, f0 - 1);
        if (k <= 0) return;
        out.fx.push({ key, cw, ch, draw, x: d[0] + x, y: d[1] + 0.002 + i * 0.0015, z: d[2] + z, w: w * k, h: h * k, flat: true, rot: rot + Math.PI / 2 });
      });
      break;
    }
    case 14: {
      fig(cam, t, out, { i: 1, o: CORPSE, key: "corpse", p: C.corpseHook, fo: { expr: "dead", blink: 0, prop: "briefcase" } });
      if (f >= 1562) { // a moth flutters out of his empty pocket
        const u = (f - 1562) / 40, a = add3(C.corpseHook, 0.12, 1.08, 0.18);
        out.fx.push({ key: `moth${Math.floor(f / 2) % 2}`, cw: 256, ch: 256, draw: (p) => fxMoth(p, Math.floor(f / 2) % 2), x: a[0] + 0.35 * u, y: a[1] + 0.45 * u + 0.04 * Math.sin(f * 0.6), z: a[2] + 0.25 + 0.1 * u, w: 0.15, h: 0.15 });
      }
      break;
    }
    case 15: {
      const deck = SEA[1] + 1.32;
      [[-6.2, 0.15], [-7.3, -0.35], [-4.9, -0.3]].forEach(([x, z], i) =>
        fig(cam, t, out, { i: 50 + i, o: CREW(i), key: `crew${i}`, p: [SEA[0] + x, deck, SEA[2] + z], fo: { expr: f < 1700 ? "stern" : "neutral", look: -1, wave: f >= 1706 && i === 0 ? 0.0 : undefined } }));
      // the body: lying on the deck, then slipped over the side (1679-1700), then floating
      const u = glide(u01(f, 1679, 1700));
      const bx = SEA[0] - 9.6, by = f < 1700 ? deck + 0.28 + (0.08 - deck - 0.28) * u * u : 0.08 + 0.03 * Math.sin(t * 2.2), bz = SEA[2] + 0.55 + 2.6 * u;
      fig(cam, t, out, { i: 1, o: CORPSE, key: "corpse", p: [bx, by, bz], fo: { expr: "dead", blink: 0, prop: "briefcase" }, roll: -1.5 - 0.15 * u, blob: false });
      const su = (f - 1700) / 30;
      if (su >= 0 && su < 1) { const sq = q(su, 30); out.fx.push({ key: `splash${sq}`, cw: 800, ch: 800, draw: (p) => fxSplash(p, sq), x: bx, y: 0.75, z: bz + 0.2, w: 2.4, h: 2.4 }); }
      break;
    }
    case 16: {
      const bob = 0.05 * Math.sin(t * 1.8), b = C.boat;
      fig(cam, t, out, { i: 60, o: FISHER, key: "fisher", p: [b[0] + 0.25, b[1] - 0.1 + bob, b[2]], fo: { mode: "sit", expr: f < 1763 - 2 ? "neutral" : "shock", look: f < 1755 ? 0 : -1 }, blob: false });
      const bx = b[0] - 3.7, bz = b[2] + 2.1;
      fig(cam, t, out, { i: 1, o: CORPSE, key: "corpse", p: [bx, 0.1 + 0.03 * Math.sin(t * 2.2 + 1), bz], fo: { expr: "dead", blink: 0, prop: "briefcase" }, roll: -1.62, blob: false });
      const ru = ((f - 1735) / 40) % 1, rq = q(ru, 20);
      out.fx.push({ key: `ripple${rq}`, cw: 256, ch: 256, draw: (p) => fxRipple(p, rq), x: bx - 0.2, y: 0.01, z: bz, w: 2.4, h: 2.4, flat: true });
      break;
    }
    case 17: {
      const flashA = f >= 1834 - 1 && f < 1840, flashB = f >= 1855 - 1 && f < 1861;
      fig(cam, t, out, { i: 70, o: SPY(0), key: "spy00", p: C.spy, fo: { expr: flashA || flashB ? "grin" : "smug", prop: "camera", look: -1 } });
      fig(cam, t, out, { i: 71, o: OFFICIAL, key: "official", p: C.official, fo: { expr: f < 1825 ? "smile" : "smile_closed", look: 1 } });
      const dsk = add3(C.spy, 0.35, 0.79, 0.75);
      out.fx.push({ key: "letterA", cw: 512, ch: 640, draw: fxBankLetter, x: dsk[0] - 0.25, y: dsk[1] + 0.002, z: dsk[2], w: 0.26, h: 0.32, flat: true, rot: 0.2 });
      out.fx.push({ key: "envOpen", cw: 512, ch: 384, draw: (p) => fxEnvelope(p, false), x: dsk[0] + 0.2, y: dsk[1] + 0.003, z: dsk[2] + 0.05, w: 0.3, h: 0.22, flat: true, rot: -0.15 });
      for (const [f0, on] of [[1834, flashA], [1855, flashB]] as const) if (on) {
        const u = q((f - f0 + 1) / 6, 6), hand = add3(C.spy, 0.3, 1.18, 0.3);
        out.fx.push({ key: `flash${u}`, cw: 256, ch: 256, draw: (p) => fxFlash(p, u), x: hand[0], y: hand[1], z: hand[2], w: 0.55, h: 0.55 });
      }
      break;
    }
    case 18: {
      flatArrow(out, "greece", mp(15.2, 34.4), mp(20.9, 37.7), glide(u01(f, 1910, 1934)), "#c0393f", 0.13);
      flatArrow(out, "sardinia", mp(10.3, 37.4), mp(9.4, 39.0), glide(u01(f, 1932, 1954)), "#c0393f", 0.13);
      break;
    }
    case 20: {
      const go = (k: number) => glide(u01(f, 2121 + k * 6, 2180 + k * 6));
      for (let k = 0; k < 3; k++) {
        const g = go(k), a = mp(20.2 + k * 0.6, 44.6 - k * 0.3, 0, true), b = mp(21.4 + k * 0.55, 38.9 - k * 0.35, 0, true);
        tank(out, [a[0] + (b[0] - a[0]) * g, a[1], a[2] + (b[2] - a[2]) * g], "#7b8089", false, 1.6);
        const g2 = go(k + 1), c = mp(10.4 + k * 0.4, 44.0 - k * 0.3, 0, true), e = mp(9.0 + k * 0.35, 40.6 - k * 0.45, 0, true);
        tank(out, [c[0] + (e[0] - c[0]) * g2, c[1], c[2] + (e[2] - c[2]) * g2], "#7b8089", true, 1.6);
      }
      if (f >= 2200) { // a tumbleweed rolls across empty Sicily
        const u = u01(f, 2200, 2254), a = mp(12.2, 37.9, 0, true), b = mp(15.6, 37.2, 0, true);
        out.fx.push({ key: "tumble", cw: 384, ch: 384, draw: fxTumble, x: a[0] + (b[0] - a[0]) * u, y: a[1] + 0.035 + 0.012 * Math.abs(Math.sin(f * 0.35)), z: a[2] + (b[2] - a[2]) * u, w: 0.07, h: 0.07, rot: -f * 0.25 });
      }
      break;
    }
    case 21: case 22: case 24: {
      const rows = id === 21 ? 3 : id === 24 ? 4 : 3, k = id === 22 ? u01(f, 2442, 2482) : 1;
      const st = C.stone, kq = q(k, 20), n = id === 22 && f >= 2442 ? 4 : rows;
      out.fx.push({ key: `engrave${n}|${kq}`, cw: 1024, ch: 1280, draw: (p) => fxEngrave(p, n, n === 4 ? kq : 1), x: st[0], y: st[1] + 0.72, z: st[2] + 0.104, w: 0.72, h: 0.9, yaw: 0 });
      if (id === 22) {
        const hits = [2442, 2453, 2464], last = hits.filter((h) => f >= h - 3).pop();
        const sinceHit = last !== undefined ? f - last : 99, strike = sinceHit < 0 ? 1 - (-sinceHit) / 3 : sinceHit < 6 ? 1 - sinceHit / 6 : 0;
        fig(cam, t, out, { i: 80, o: MASON, key: "mason", p: C.mason, fo: { expr: f < 2470 ? "stern" : "smile_closed", prop: ["hammer", f < 2430 ? 0 : strike], look: -1 } });
        if (sinceHit >= 0 && sinceHit < 6) {
          const u = q(sinceHit / 6, 6);
          out.fx.push({ key: `sparks${u}`, cw: 512, ch: 512, draw: (p) => fxSparks(p, u), x: st[0] - 0.22, y: st[1] + 0.42, z: st[2] + 0.16, w: 0.3, h: 0.3 });
        }
      }
      if (id === 24) fig(cam, t, out, { i: 90, o: MARINE, key: "ghost", p: C.ghost, fo: { expr: f < 2596 ? "smug" : "smile_closed", wave: f >= 2600 ? 0.1 : undefined, look: 0 } });
      break;
    }
  }
  return out;
};
const STREETX = (x: number) => STREET_O[0] + x;
const STREETZ = (z: number) => STREET_O[2] + z;
import { STREET as STREET_O } from "./sets";
