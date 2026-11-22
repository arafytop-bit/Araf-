// Timeline of "The Agent With No Pulse" (Operation Mincemeat): shots timed to the voice words
// (shorts/mincemeat/voice/words.json, frame = onset x 30), camera grammar from the reference study (smootherstep
// glides 18-40 f, creeping push-ins on every hold, hard cuts on big reframes, 7-frame flip kicks on impacts).
import { ROOM, BERLIN, SPAIN, SEA, STREET, GRAVE, TABLE_C, mapPt, PLACES, V3 } from "./sets";

export const FPS = 30;
export const TOTAL = 2650;
export type { V3 };

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };

// ---------------- shots ----------------
export type Light = "day" | "golden";
export type SetName = "room" | "berlin" | "spain" | "sea" | "street" | "grave";
export type ShotDef = { id: number; a: number; b: number; light: Light; set: SetName };
const S = (id: number, a: number, b: number, set: SetName, light: Light = "day"): ShotDef => ({ id, a, b, set, light });
export const SHOTS: ShotDef[] = [
  S(1, 0, 220, "room"),        // hook: the agent with no pulse
  S(2, 220, 293, "berlin"),    // "And he still fooled Hitler."
  S(3, 293, 366, "room"),      // the Sicily plan on the map
  S(4, 366, 406, "room"),      // "Tiny issue."
  S(5, 406, 451, "berlin"),    // "Everybody knew it."
  S(6, 451, 577, "room"),      // marching band across the map
  S(7, 577, 679, "room"),      // two officers got weird
  S(8, 679, 884, "room"),      // dressing the body
  S(9, 884, 941, "sea"),       // "dump him off Spain"
  S(10, 941, 1010, "sea"),     // crawling with German spies (beach)
  S(11, 1010, 1169, "street"), // Glyndwr Michael
  S(12, 1169, 1253, "room"),   // a fake life
  S(13, 1253, 1546, "room"),   // pocket litter on the desk
  S(14, 1546, 1605, "room"),   // dead and still in debt
  S(15, 1605, 1735, "sea", "golden"), // the submarine at dawn
  S(16, 1735, 1799, "sea"),    // the fisherman
  S(17, 1799, 1882, "spain"),  // Germans copy the letters
  S(18, 1882, 2024, "room"),   // Greece, Sardinia, the decoy
  S(19, 2024, 2121, "berlin"), // would Hitler bite?
  S(20, 2121, 2254, "berlin"), // reinforcements, Sicily got none
  S(21, 2254, 2388, "grave", "golden"), // the grave in Spain
  S(22, 2388, 2492, "grave", "golden"), // 1998: his real name
  S(23, 2492, 2558, "street"), // nobody noticed him alive
  S(24, 2558, TOTAL, "grave", "golden"), // dead, he outfoxed Hitler
];
/** crossfades (frames) at place / time changes; the hook ends on a white 4-frame flash */
export const XFADE: Record<number, number> = { 9: 6, 11: 8, 15: 8, 17: 6, 21: 10, 23: 8, 24: 8 };
export const FLASH_AT = 220;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

// ---------------- staging points (shared with cast.ts) ----------------
const add = (o: V3, x: number, y: number, z: number): V3 => [o[0] + x, o[1] + y, o[2] + z];
export const TC = TABLE_C(ROOM), BTC = TABLE_C(BERLIN);
export const SPOT = {
  corpseHook: add(ROOM, -2.3, 0, 0.9),
  corpseDress: add(ROOM, -3.0, 0, -2.5),
  montaguDress: add(ROOM, -1.95, 0, -2.3),
  cholDress: add(ROOM, -4.05, 0, -2.35),
  montaguTable: add(ROOM, 0.5, 0, -2.15),
  montaguDesk: add(ROOM, 2.0, 0, -2.25),
  cholDesk: add(ROOM, 2.85, 0, -2.4),
  hitler: add(BERLIN, 0.75, 0, -2.05),
  bench: add(STREET, -8.7, 0.12, 2.3),
  tin: add(STREET, -8.0, 0.53, 2.1),
  sub: SEA,
  boat: add(SEA, -60, 0, -110),
  spy: add(SPAIN, 0.25, 0, -1.75),
  official: add(SPAIN, -1.55, 0, -2.0),
  stone: add(GRAVE, 0, 0, 2),
  mason: add(GRAVE, -0.66, 0, 2.4),
  ghost: add(GRAVE, -0.95, 0, 2.45),
  deskTop: add(ROOM, 2.4, 0.79, -3.2),
};
/** beach height on the Huelva shore (sand ramps from 0.05 m at the waterline to 0.6 m 30 m inland) */
export const beachY = (zAbs: number) => 0.05 + clamp01((SEA[2] - 140 - zAbs) / 30) * 0.55;
export const mp = (lon: number, lat: number, dy = 0, berlin = false) => mapPt(berlin ? BTC : TC, lon, lat, dy);
export { PLACES };

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
type Shot = Partial<Cam> & { pos: V3; look: V3 };
type Key = { f: number; dur?: number; cut?: boolean; s: (f: number) => Shot };
const mix = (a: Cam, b: Cam, k: number): Cam => ({
  pos: a.pos.map((v, i) => v + (b.pos[i] - v) * k) as V3, look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3,
  fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k,
});
const full = (c: Shot): Cam => ({ fov: 40, roll: 0, ...c });
const run = (keys: Key[], f: number) => {
  let cur = full(keys[0].s(f));
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (f < k.f) break;
    cur = k.cut ? full(k.s(f)) : mix(cur, full(k.s(f)), glide((f - k.f) / (k.dur ?? 24)));
  }
  return cur;
};
const T = (f: number) => f / FPS;
/** push-in factor since f0 (subject grows ~rate per frame), `punch` for the first n frames */
const pushK = (f: number, f0: number, rate: number, punch = 0, n = 30) => {
  const x = Math.max(0, f - f0);
  let s = rate * x;
  if (punch > rate) for (let i = 0; i < Math.min(x, n); i++) s += (punch - rate) * Math.max(0, Math.min(1, (i + 0.5) / 8, (n - i - 0.5) / 8));
  return Math.exp(-s);
};
const dolly = (pos: V3, look: V3, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos: [look[0] + (pos[0] - look[0]) * k, look[1] + (pos[1] - look[1]) * k, look[2] + (pos[2] - look[2]) * k], look, ...rest });
const rel = (o: V3, p: V3): V3 => [o[0] + p[0], o[1] + p[1], o[2] + p[2]];
/** a framing relative to a point: camera offset d from the subject point c (look = c + l) */
const fr = (c: V3, d: V3, l: V3 = [0, 0, 0]) => ({ pos: rel(c, d), look: rel(c, l) });
const P = (f0: number, c: V3, d: V3, l: V3, rate = 0.0025, rest: Partial<Cam> = {}, punch = 0) => (f: number): Shot => {
  const q = fr(c, d, l);
  return dolly(q.pos, q.look, pushK(f, f0, rate, punch), rest);
};

const C = SPOT;
const face = (p: V3, h = 1.45): V3 => [p[0], p[1] + h, p[2]];
const tiny = mp(PLACES.tunis[0] + 1.2, PLACES.tunis[1] + 0.2);
export const CAMS: Record<number, Key[]> = {
  1: [
    { f: 0, s: P(0, face(C.corpseHook, 1.2), [1.6, 0.35, 4.6], [0, 0, 0], 0.0022, { fov: 40 }) },
    { f: 96, dur: 30, s: P(96, face(C.corpseHook, 1.35), [0.6, 0.15, 2.5], [0, 0, 0], 0.002, { fov: 38, roll: -0.04 }) },
    { f: 180, cut: true, s: P(180, face(C.corpseHook, 1.35), [-0.4, 0.05, 1.75], [0, 0, 0], 0.0025, { fov: 36, roll: 0.04 }, 0.006) },
  ],
  2: [
    { f: 216, s: P(216, face(C.hitler, 1.3), [-0.5, 0.2, 3.2], [0, 0, 0], 0.003, { fov: 38 }) },
    { f: 244, dur: 24, s: P(244, face(C.hitler, 1.4), [-0.25, 0.05, 2.2], [0, 0, 0], 0.002, { fov: 36, roll: 0.04 }) },
  ],
  3: [
    { f: 290, s: P(290, mp(12.5, 36.2), [0.05, 1.35, 1.05], [0, 0, 0], 0.002, { fov: 40 }) },
    { f: 322, dur: 28, s: P(322, mp(12.8, 36.8), [-0.1, 0.95, 0.75], [0, 0, 0], 0.0022, { fov: 40, roll: 0.035 }) },
  ],
  4: [{ f: 366, s: P(366, face(C.montaguTable), [-0.25, 0.05, 2.0], [0, 0, 0], 0.003, { fov: 36, roll: -0.04 }, 0.006) }],
  5: [
    { f: 404, s: P(404, face(C.hitler, 1.2), [-1.6, 0.4, 3.0], [0.15, -0.15, 0.2], 0.0025, { fov: 40 }) },
  ],
  6: [
    { f: 448, s: P(448, tiny, [0.32, 0.12, 0.62], [0, 0.02, 0], 0.0015, { fov: 38 }) },
    { f: 520, dur: 32, s: P(520, mp(12.6, 37.0), [0.45, 0.16, 0.5], [0, 0.03, 0], 0.0018, { fov: 38, roll: 0.04 }) },
  ],
  7: [
    { f: 574, s: P(574, rel(C.montaguDesk, [0.42, 1.3, -0.05]), [0.1, 0.25, 4.0], [0, 0, 0], 0.0022, { fov: 40 }) },
    { f: 640, dur: 20, s: P(640, rel(C.montaguDesk, [0.42, 1.38, -0.05]), [-0.1, 0.12, 3.0], [0, 0, 0], 0.002, { fov: 38, roll: 0.045 }) },
  ],
  8: [
    { f: 676, s: P(676, face(C.corpseDress, 1.1), [0.2, 0.35, 4.6], [0, 0, 0], 0.0022, { fov: 46 }) },
    { f: 786, dur: 28, s: P(786, face(C.corpseDress, 0.95), [0.55, 0.15, 2.4], [0, 0, 0], 0.002, { fov: 38, roll: -0.035 }) },
    { f: 830, dur: 24, s: P(830, face(C.corpseDress, 1.0), [0.75, 0.1, 1.8], [-0.1, -0.1, 0], 0.0025, { fov: 36, roll: 0.03 }) },
  ],
  9: [{ f: 881, s: P(881, rel(SEA, [0, 3, -60]), [-34, 3.0, 82], [0, 0, 0], 0.0012, { fov: 42 }) }],
  10: [{ f: 938, s: P(938, [SEA[0] + 1.2, beachY(SEA[2] - 162) + 1.25, SEA[2] - 162.5], [-0.6, 0.35, 5.4], [0, 0, 0], 0.0025, { fov: 42, roll: 0.03 }) }],
  11: [
    { f: 1006, s: P(1006, face(C.bench, 0.85), [2.6, 0.45, 3.6], [0, 0, 0], 0.0022, { fov: 40 }) },
    { f: 1046, dur: 30, s: P(1046, face(C.bench, 0.95), [1.4, 0.2, 2.2], [0, 0, 0], 0.002, { fov: 38, roll: -0.04 }) },
    { f: 1113, cut: true, s: P(1113, rel(C.tin, [-0.35, 0.18, 0]), [0.9, 0.3, 1.4], [0, 0, 0], 0.003, { fov: 36, roll: 0.035 }) },
  ],
  12: [
    { f: 1169, s: P(1169, rel(C.montaguDesk, [0.42, 1.35, -0.05]), [0.25, 0.15, 3.0], [0, 0, 0], 0.0025, { fov: 38, roll: -0.03 }) },
    { f: 1210, dur: 24, s: P(1210, rel(C.montaguDesk, [0.42, 1.32, -0.05]), [-0.2, 0.05, 2.4], [0, 0, 0], 0.002, { fov: 36, roll: 0.035 }) },
  ],
  13: [ // desk-top insert, rolled a quarter turn so the desk's length runs up the portrait frame
    { f: 1253, s: P(1253, rel(C.deskTop, [-0.42, 0, 0.0]), [0.0, 0.85, 0.12], [0, 0, 0], 0.0016, { fov: 40, roll: Math.PI / 2 }) },
    { f: 1340, dur: 30, s: P(1340, rel(C.deskTop, [-0.08, 0, 0.0]), [0.0, 0.8, 0.12], [0, 0, 0], 0.0016, { fov: 40, roll: Math.PI / 2 + 0.03 }) },
    { f: 1405, dur: 30, s: P(1405, rel(C.deskTop, [0.3, 0, 0.0]), [0.0, 0.8, 0.12], [0, 0, 0], 0.0016, { fov: 40, roll: Math.PI / 2 - 0.03 }) },
    { f: 1470, dur: 26, s: P(1470, rel(C.deskTop, [0.62, 0, 0.0]), [0.0, 0.6, 0.1], [0, 0, 0], 0.0022, { fov: 38, roll: Math.PI / 2 }, 0.005) },
  ],
  14: [{ f: 1546, s: P(1546, face(C.corpseHook, 1.15), [0.4, 0.15, 1.9], [0, 0, 0], 0.0025, { fov: 36, roll: -0.04 }, 0.006) }],
  15: [
    { f: 1601, s: P(1601, rel(SEA, [-5, 2.0, 0]), [-20, 2.5, 24], [0, 0, 0], 0.0015, { fov: 42 }) },
    { f: 1648, cut: true, s: P(1648, rel(SEA, [-9.5, 1.6, 0.8]), [-4.5, 1.1, 7.8], [0, -0.3, 0.6], 0.002, { fov: 40, roll: 0.035 }) },
  ],
  16: [{ f: 1731, s: P(1731, rel(C.boat, [-1.6, 0.45, 0.9]), [3.6, 1.4, 8.2], [0, 0, 0], 0.0025, { fov: 42, roll: -0.03 }) }],
  17: [
    { f: 1796, s: P(1796, face(C.spy, 1.2), [0.9, 0.3, 3.2], [-0.4, -0.2, 0.3], 0.0022, { fov: 40 }) },
    { f: 1828, dur: 22, s: P(1828, face(C.spy, 1.25), [0.45, 0.05, 2.1], [-0.15, -0.1, 0.2], 0.002, { fov: 38, roll: 0.04 }) },
  ],
  18: [
    { f: 1882, s: P(1882, mp(14.8, 37.9), [0, 2.9, 0.8], [0, 0, 0], 0.0015, { fov: 50 }) },
    { f: 1955, dur: 30, s: P(1955, mp(PLACES.sicily[0], PLACES.sicily[1]), [0.12, 0.55, 0.62], [0, 0.03, 0], 0.002, { fov: 38, roll: 0.035 }) },
  ],
  19: [
    { f: 2024, s: P(2024, face(C.hitler, 1.35), [-0.3, 0.05, 2.4], [0, 0.12, 0], 0.0025, { fov: 38, roll: -0.03 }) },
    { f: 2062, dur: 18, s: P(2062, face(C.hitler, 1.4), [-0.15, 0.0, 1.55], [0, 0.1, 0], 0.002, { fov: 36, roll: 0.04 }, 0.006) },
  ],
  20: [
    { f: 2121, s: P(2121, mp(15.3, 40.6, 0, true), [0, 2.9, 0.8], [0, 0, 0], 0.0018, { fov: 50, roll: -0.025 }) },
    { f: 2195, cut: true, s: P(2195, mp(PLACES.sicily[0], PLACES.sicily[1], 0, true), [0.05, 0.45, 0.75], [0, 0.03, 0], 0.0022, { fov: 38 }) },
  ],
  21: [
    { f: 2249, s: P(2249, rel(C.stone, [0, 0.9, 0]), [2.6, 1.3, 10.5], [0, 0, 0], 0.0022, { fov: 40 }) },
    { f: 2326, dur: 34, s: P(2326, rel(C.stone, [0, 0.85, 0]), [1.2, 0.45, 5.2], [0, 0, 0], 0.002, { fov: 38, roll: 0.03 }) },
  ],
  22: [
    { f: 2388, s: P(2388, rel(C.stone, [0.15, 0.8, 0.1]), [0.75, 0.15, 2.2], [0, 0, 0], 0.0022, { fov: 38, roll: -0.03 }) },
    { f: 2436, dur: 22, s: P(2436, rel(C.stone, [-0.32, 0.85, 0.2]), [0.4, 0.1, 2.9], [0, 0, 0], 0.0025, { fov: 38, roll: 0.035 }, 0.005) },
  ],
  23: [{ f: 2488, s: P(2488, face(C.bench, 0.9), [3.4, 0.6, 5.4], [0, 0, 0], 0.002, { fov: 42 }) }],
  24: [
    { f: 2554, s: P(2554, rel(C.ghost, [0.45, 1.3, 0]), [0.25, 0.1, 2.6], [0, 0, 0], 0.0025, { fov: 38, roll: 0.03 }) },
    { f: 2598, dur: 40, s: (f) => { const k = glide((f - 2598) / 52); const a = fr(rel(C.ghost, [0.45, 1.3, 0]), [0.25, 0.1, 2.6]);
      return { pos: [a.pos[0] + 1.5 * k, a.pos[1] + 2.6 * k, a.pos[2] + 3.6 * k] as V3, look: [a.look[0] + 0.2 * k, a.look[1] - 0.1 * k, a.look[2] - 0.6 * k] as V3, fov: 38 + 4 * k, roll: 0 }; } },
  ],
};

// impact kicks: image offset flips sign every frame and decays over 7 f (seconds, gain)
const KICKS: [number, number][] = [[1700 / FPS, 0.9], [2093 / FPS, 1.2], [2442 / FPS, 0.4], [2453 / FPS, 0.4], [2464 / FPS, 0.5], [1996 / FPS, 0.4], [649 / FPS, 0.35]];
export const kickAt = (t: number) => {
  let a = 0;
  for (const [t0, g] of KICKS) {
    const n = Math.floor((t - t0) * FPS + 1e-6);
    if (n >= 0 && n < 7) a += g * (n % 2 ? -1 : 1) * (1 - n / 7) ** 1.5;
  }
  return a;
};
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(T(f));
  if (!a) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a;
  return { ...c, look: [c.look[0] - (d[2] / h) * m, c.look[1] + 0.6 * m, c.look[2] + (d[0] / h) * m], roll: c.roll + a * 0.004 };
};

// ---------------- lens: depth of field ----------------
/** cInf = blur disc radius (px at 1080x1920) at infinity; 0 = all sharp; focus = world point (else the look point) */
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
export const DOF: Dof[] = [
  { f: 0, cInf: 12 }, { f: 96, dur: 30, cInf: 13 }, { f: 180, cInf: 15 },
  { f: 220, cInf: 10 }, { f: 293, cInf: 8 }, { f: 366, cInf: 13 }, { f: 406, cInf: 10 },
  { f: 451, cInf: 15 }, { f: 577, cInf: 10 }, { f: 679, cInf: 10 }, { f: 786, dur: 28, cInf: 12 },
  { f: 884, cInf: 0 }, { f: 941, cInf: 7 }, { f: 1010, cInf: 10 }, { f: 1113, cInf: 14 },
  { f: 1169, cInf: 12 }, { f: 1253, cInf: 6 }, { f: 1546, cInf: 14 }, { f: 1605, cInf: 0 }, { f: 1648, cInf: 6 },
  { f: 1735, cInf: 7 }, { f: 1799, cInf: 10 }, { f: 1882, cInf: 6 }, { f: 1955, dur: 30, cInf: 12 },
  { f: 2024, cInf: 12 }, { f: 2121, cInf: 7 }, { f: 2195, cInf: 12 }, { f: 2254, cInf: 0 }, { f: 2326, dur: 34, cInf: 6 },
  { f: 2388, cInf: 12 }, { f: 2492, cInf: 7 }, { f: 2558, cInf: 10 }, { f: 2598, dur: 40, cInf: 3 },
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
