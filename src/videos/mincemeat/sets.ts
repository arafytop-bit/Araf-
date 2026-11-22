// The six sets of the Mincemeat short, built once as static batches (one mesh per material) far apart so fog and
// the shot cameras never see two at once:
//   ROOM    London war room (map table, desk, window, bookcase)            origin (0, 0, 0)
//   BERLIN  Hitler's map room (grey walls, red drapes, same map)           origin (300, 0, 0)
//   SPAIN   Spanish office where the letters are copied                    origin (-300, 0, 0)
//   SEA     the sea off Huelva: submarine, rowing boat, coast with town    origin (0, 0, -1500)
//   STREET  1940s London street (brick terraces, bench, lamp posts)        origin (-1500, 0, 0)
//   GRAVE   Huelva cemetery: white wall, cypresses, headstones            origin (1500, 0, 0)
import * as THREE from "three";
import { Batch, lam, boxGeo, quad, V, house, Style } from "./build";
import { ctex, rep, stoneHD, cobbleHD, grassHD, planksHD, jit } from "./paint";
import { twoTone } from "./shade";
import { NOINK } from "./ink";

export type V3 = [number, number, number];
export const ROOM: V3 = [0, 0, 0];
export const BERLIN: V3 = [300, 0, 0];
export const SPAIN: V3 = [-300, 0, 0];
export const SEA: V3 = [0, 0, -1500];
export const STREET: V3 = [-1500, 0, 0];
export const GRAVE: V3 = [1500, 0, 0];

// ---------------- the map ----------------
// equirectangular-ish: lon -8..28 E, lat 30..46 N on a 3.6 x 2.0 m table top (north = -z, away from the main cameras)
export const MAP_W = 3.6, MAP_D = 2.0, TABLE_Y = 0.95;
const LON0 = -8, LON1 = 28, LAT0 = 30, LAT1 = 46;
/** world point on a table top centred at c for (lon, lat) */
export const mapPt = (c: V3, lon: number, lat: number, dy = 0): V3 =>
  [c[0] + ((lon - LON0) / (LON1 - LON0) - 0.5) * MAP_W, c[1] + TABLE_Y + 0.012 + dy, c[2] + ((LAT1 - lat) / (LAT1 - LAT0) - 0.5) * MAP_D];
export const TABLE_C = (o: V3): V3 => [o[0], 0, o[2] - 0.5];
export const PLACES = { tunis: [10.2, 36.6], sicily: [14.1, 37.55], sardinia: [9.0, 40.0], greece: [22.1, 38.0], africa: [12.5, 33.0] } as const;

type LL = [number, number][];
const NORTH: LL = [[-1.2, 46], [-1.4, 44.6], [-1.8, 43.4], [-4, 43.5], [-8, 43.7], [-9.3, 43], [-8.8, 42], [-8.9, 40.5], [-9.5, 39], [-8.8, 38.7],
  [-8.9, 37], [-7.4, 37.2], [-6.3, 36.8], [-5.6, 36], [-4.4, 36.7], [-2.1, 36.7], [-0.6, 37.6], [0.2, 38.8], [-0.3, 39.5], [0, 40], [0.9, 41],
  [3.2, 41.9], [3.2, 42.4], [3.1, 43.1], [4.5, 43.4], [6, 43.1], [7.5, 43.8], [8.7, 44.4], [9.8, 44.1], [10.5, 43], [11.2, 42.4], [12.2, 41.7],
  [13.6, 41.2], [14.5, 40.6], [15.6, 40.1], [15.7, 39], [16.1, 38], [15.65, 37.95], [16.5, 38.5], [17.1, 39], [17.2, 39.4], [16.5, 39.7], [17, 40.5],
  [18.5, 40.1], [18.4, 40.4], [16.9, 41.2], [15.9, 41.9], [14.3, 42.5], [13.6, 43.5], [12.3, 44.5], [12.4, 45.4], [13.7, 45.6], [14.4, 45.2],
  [15, 44.5], [16, 43.5], [17.5, 43], [18.5, 42.4], [19.4, 41.9], [19.5, 40.9], [19.3, 40.4], [20, 39.6], [20.7, 38.8], [21.1, 38.3], [21.7, 37.6],
  [21.8, 36.8], [22.4, 36.4], [23.1, 36.5], [22.8, 37.4], [23.5, 37.9], [24, 38.2], [23, 38.8], [22.6, 39.4], [23.3, 39.9], [22.9, 40.5],
  [24, 40.8], [25.5, 40.9], [26.3, 40.9], [26.6, 40.3], [26.2, 39.5], [26.8, 38.7], [26.4, 38.3], [27.2, 37.4], [27.6, 36.7], [28.5, 36.7],
  [28.5, 46.5], [-1.2, 46.5]];
const SOUTH: LL = [[-8.5, 29.5], [-9.6, 30.4], [-9.8, 31.5], [-8.6, 33.3], [-6.8, 34], [-5.9, 35.8], [-5.3, 35.9], [-2, 35.1], [0, 35.9], [1.5, 36.5],
  [3, 36.8], [5, 36.8], [7.8, 36.9], [9.8, 37.3], [10.3, 37], [11, 37.1], [10.5, 36.4], [10.8, 35.6], [11.1, 35.2], [10.1, 34.3], [10.6, 33.8],
  [11.5, 33.1], [13.2, 32.9], [15.2, 32.3], [15.8, 31.5], [17.5, 30.9], [19, 30.3], [20.1, 31], [20.1, 32.2], [21.6, 32.9], [23.1, 32.6],
  [24.9, 31.9], [25.2, 31.6], [28.5, 31.1], [28.5, 29.5]];
const ISLES: LL[] = [
  [[12.4, 38.1], [13.3, 38.2], [14.2, 38.0], [15.6, 38.3], [15.1, 37.4], [15.2, 37.0], [15.1, 36.65], [14.4, 36.8], [12.6, 37.6]], // Sicily
  [[8.4, 40.9], [9.2, 41.25], [9.8, 40.9], [9.6, 40.1], [9.6, 39.1], [9.0, 39.1], [8.5, 38.9], [8.4, 39.6], [8.5, 40.4]],         // Sardinia
  [[8.6, 42.0], [9.0, 41.4], [9.4, 41.6], [9.5, 42.6], [9.4, 43.0], [8.6, 42.6]],                                                   // Corsica
  [[23.5, 35.6], [24.5, 35.4], [26.3, 35.3], [25.8, 35.0], [24.7, 35.0], [23.6, 35.2]],                                             // Crete
  [[2.4, 39.5], [3.2, 39.95], [3.4, 39.6], [2.8, 39.35]], [[3.8, 40.0], [4.3, 40.05], [4.2, 39.85]], [[1.2, 38.95], [1.6, 39.1], [1.5, 38.85]],
  [[24.8, 37.95], [25.1, 37.7], [24.7, 37.6]], [[25.3, 37.1], [25.6, 37.2], [25.5, 36.9]], [[26.0, 39.3], [26.6, 39.3], [26.4, 39.0]],
  [[23.5, 39.0], [24.0, 38.5], [24.6, 38.2], [24.1, 38.4], [23.2, 38.8]],                                                         // Euboea
];
export const mapTex = () => ctex("medMap", 2048, 1138, (g, r) => {
  const W = 2048, H = 1138, P = ([lo, la]: [number, number]) => [((lo - LON0) / (LON1 - LON0)) * W, ((LAT1 - la) / (LAT1 - LAT0)) * H] as const;
  const shape = (ll: LL) => { g.beginPath(); ll.forEach((q, i) => { const [x, y] = P(q); if (i) g.lineTo(x, y); else g.moveTo(x, y); }); g.closePath(); };
  // sea: flat blue with a lighter coastal band and faint grid
  g.fillStyle = "#6fa7cf"; g.fillRect(0, 0, W, H);
  for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(255,255,255,${0.03 + 0.03 * r()})`; g.beginPath(); g.ellipse(r() * W, r() * H, 60 + r() * 160, 20 + r() * 40, 0, 0, 7); g.fill(); }
  const lands = [NORTH, SOUTH, ...ISLES];
  g.lineJoin = "round";
  for (const ll of lands) { shape(ll); g.strokeStyle = "#a9d2ec"; g.lineWidth = 34; g.stroke(); }
  for (const ll of lands) { shape(ll); g.strokeStyle = "#8ec1e2"; g.lineWidth = 16; g.stroke(); }
  g.strokeStyle = "rgba(30,60,100,0.16)"; g.lineWidth = 2;
  for (let lo = -5; lo <= 25; lo += 5) { const [x] = P([lo, 0]); g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
  for (let la = 32; la <= 45; la += 4) { const [, y] = P([0, la]); g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
  // land: parchment with soft ochre / sage blotches, ink coast
  for (const ll of lands) { shape(ll); g.fillStyle = "#ead9ab"; g.fill(); }
  g.save(); for (const ll of lands) shape(ll); g.restore();
  for (const ll of lands) {
    g.save(); shape(ll); g.clip();
    for (let i = 0; i < 40; i++) {
      const [x, y] = P(ll[Math.floor(r() * ll.length)]);
      g.fillStyle = r() > 0.5 ? "rgba(170,180,110,0.22)" : "rgba(200,150,90,0.18)";
      g.beginPath(); g.ellipse(x + (r() - 0.5) * 300, y + (r() - 0.5) * 200, 40 + r() * 120, 30 + r() * 80, r() * 3, 0, 7); g.fill();
    }
    g.restore();
  }
  for (const ll of lands) { shape(ll); g.strokeStyle = "#3b2d2a"; g.lineWidth = 5; g.stroke(); }
  // compass rose (bottom-left, over Africa's west), border
  const cx = 230, cy = 930;
  g.fillStyle = "#c0393f"; g.beginPath(); g.moveTo(cx, cy - 110); g.lineTo(cx + 22, cy); g.lineTo(cx - 22, cy); g.closePath(); g.fill();
  g.fillStyle = "#3b2d2a"; g.beginPath(); g.moveTo(cx, cy + 110); g.lineTo(cx + 22, cy); g.lineTo(cx - 22, cy); g.closePath(); g.fill();
  g.beginPath(); g.moveTo(cx - 90, cy); g.lineTo(cx, cy - 16); g.lineTo(cx + 90, cy); g.lineTo(cx, cy + 16); g.closePath(); g.fill();
  g.strokeStyle = "#3b2d2a"; g.lineWidth = 4; g.beginPath(); g.arc(cx, cy, 60, 0, 7); g.stroke();
  g.strokeStyle = "#5a4030"; g.lineWidth = 18; g.strokeRect(9, 9, W - 18, H - 18);
});

// ---------------- painted interiors ----------------
const wallpaper = (key: string, base: string, stripe: string) => ctex("wp" + key, 512, 512, (g, r) => {
  g.fillStyle = base; g.fillRect(0, 0, 512, 512);
  for (let x = 0; x < 512; x += 64) { g.fillStyle = stripe; g.fillRect(x + 24, 0, 16, 512); }
  for (let i = 0; i < 30; i++) { g.fillStyle = `rgba(90,70,50,${0.03 + 0.03 * r()})`; g.beginPath(); g.ellipse(r() * 512, r() * 512, 30 + 60 * r(), 30 + 60 * r(), 0, 0, 7); g.fill(); }
});
const panel = (key: string, base: string) => ctex("pn" + key, 512, 512, (g, r) => {
  g.fillStyle = base; g.fillRect(0, 0, 512, 512);
  g.strokeStyle = "rgba(30,20,20,0.55)"; g.lineWidth = 6;
  for (let x = 0; x < 512; x += 256) { g.strokeRect(x + 30, 40, 196, 432); }
  g.fillStyle = "rgba(255,240,220,0.12)"; for (let x = 0; x < 512; x += 256) g.fillRect(x + 36, 46, 184, 8);
  for (let i = 0; i < 20; i++) { g.fillStyle = `rgba(60,30,20,${0.04 * r()})`; g.fillRect(r() * 512, 0, 3, 512); }
});
const tiles = () => ctex("azulejo", 512, 512, (g) => {
  for (let y = 0; y < 512; y += 64) for (let x = 0; x < 512; x += 64) {
    g.fillStyle = "#f2efe6"; g.fillRect(x, y, 64, 64);
    g.strokeStyle = "#2f5fa8"; g.lineWidth = 6; g.beginPath(); g.arc(x + 32, y + 32, 18, 0, 7); g.stroke();
    g.fillStyle = "#2f5fa8"; g.fillRect(x + 28, y + 2, 8, 10); g.fillRect(x + 28, y + 52, 8, 10); g.fillRect(x + 2, y + 28, 10, 8); g.fillRect(x + 52, y + 28, 10, 8);
    g.strokeStyle = "rgba(60,60,80,0.4)"; g.lineWidth = 2; g.strokeRect(x, y, 64, 64);
  }
});
const books = () => ctex("books", 512, 512, (g, r) => {
  g.fillStyle = "#5a3a26"; g.fillRect(0, 0, 512, 512);
  const cols = ["#8c3b4a", "#2f5f6a", "#c9a24a", "#3f6fb5", "#5d7a3a", "#7b5ac9", "#b5653f", "#e6dccd"];
  for (let s = 0; s < 4; s++) {
    const y0 = s * 128 + 14;
    let x = 10;
    while (x < 500) { const w = 14 + r() * 20, h = 80 + r() * 28; g.fillStyle = jit(r, cols[Math.floor(r() * cols.length)], 0.1); g.fillRect(x, y0 + 104 - h, w, h);
      g.fillStyle = "rgba(255,240,200,0.5)"; g.fillRect(x + 3, y0 + 120 - h, w - 6, 3); x += w + 2; }
    g.fillStyle = "#3e2618"; g.fillRect(0, y0 + 104, 512, 10);
  }
});
const windowTex = (key: string, sky: string, low: string, arch = false) => ctex("win" + key, 512, 768, (g) => {
  const gr = g.createLinearGradient(0, 0, 0, 768); gr.addColorStop(0, sky); gr.addColorStop(1, low);
  g.fillStyle = gr; g.fillRect(0, 0, 512, 768);
  g.fillStyle = "rgba(255,255,255,0.75)"; g.beginPath(); g.ellipse(150, 200, 90, 40, 0, 0, 7); g.fill(); g.beginPath(); g.ellipse(360, 320, 70, 30, 0, 0, 7); g.fill();
  g.strokeStyle = "#f1ece0"; g.lineWidth = 26; g.strokeRect(13, 13, 486, 742);
  g.beginPath(); g.moveTo(256, 0); g.lineTo(256, 768); g.moveTo(0, 384); g.lineTo(512, 384); g.stroke();
  g.strokeStyle = "rgba(40,30,40,0.9)"; g.lineWidth = 6; g.strokeRect(3, 3, 506, 762);
  if (arch) { g.fillStyle = "#f2efe6"; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 200); g.arc(256, 256, 256, Math.PI, 0); g.lineTo(512, 0); g.closePath(); g.fill(); }
});
const drape = (key: string, col: string) => ctex("dr" + key, 256, 512, (g) => {
  g.fillStyle = col; g.fillRect(0, 0, 256, 512);
  for (let x = 0; x < 256; x += 32) { const gr = g.createLinearGradient(x, 0, x + 32, 0); gr.addColorStop(0, "rgba(0,0,0,0.25)"); gr.addColorStop(0.5, "rgba(255,255,255,0.12)"); gr.addColorStop(1, "rgba(0,0,0,0.25)"); g.fillStyle = gr; g.fillRect(x, 0, 32, 512); }
});
const seaTex = () => ctex("seaTex", 1024, 1024, (g, r) => {
  g.fillStyle = "#ffffff"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 260; i++) {
    const x = r() * 1024, y = r() * 1024, w = 18 + r() * 50;
    g.strokeStyle = `rgba(${r() > 0.7 ? "40,70,120" : "255,255,255"},${0.5 + 0.4 * r()})`; g.lineWidth = 4 + r() * 3; g.lineCap = "round";
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + w / 2, y - 7, x + w, y); g.stroke();
  }
});
const sandTex = () => ctex("sandTex", 512, 512, (g, r) => {
  g.fillStyle = "#e9d3a4"; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${r() > 0.5 ? "255,250,230" : "150,110,70"},${0.15 + 0.2 * r()})`; g.fillRect(r() * 512, r() * 512, 3, 3); }
});

/** green leather desk blotter: tooled gold border, worn grain, a few ink spots */
const blotter = () => ctex("blotter", 2048, 1024, (g, r) => {
  g.fillStyle = "#3f5a3a"; g.fillRect(0, 0, 2048, 1024);
  for (let i = 0; i < 1400; i++) { g.fillStyle = `rgba(${r() > 0.5 ? "255,255,230" : "10,25,10"},${0.03 + 0.05 * r()})`; g.beginPath(); g.ellipse(r() * 2048, r() * 1024, 4 + 30 * r(), 2 + 12 * r(), r() * 3, 0, 7); g.fill(); }
  g.strokeStyle = "#b89a52"; g.lineWidth = 10; g.strokeRect(40, 40, 1968, 944); g.lineWidth = 4; g.strokeRect(62, 62, 1924, 900);
  g.strokeStyle = "rgba(20,15,10,0.6)"; g.lineWidth = 3; g.strokeRect(30, 30, 1988, 964);
  for (let i = 0; i < 5; i++) { g.fillStyle = "rgba(20,30,60,0.5)"; g.beginPath(); g.arc(200 + r() * 1600, 150 + r() * 700, 6 + r() * 10, 0, 7); g.fill(); }
});

// ---------------- geometry helpers ----------------
const UB = new THREE.BoxGeometry(1, 1, 1);
const box = (b: Batch, mat: THREE.Material, o: V3, x0: number, x1: number, y0: number, y1: number, z0: number, z1: number) =>
  b.add(UB, mat, new THREE.Matrix4().compose(V(o[0] + (x0 + x1) / 2, o[1] + (y0 + y1) / 2, o[2] + (z0 + z1) / 2), new THREE.Quaternion(), V(x1 - x0, y1 - y0, z1 - z0)));
const at = (o: V3, x: number, y: number, z: number, s: V3 = [1, 1, 1], yaw = 0) =>
  new THREE.Matrix4().compose(V(o[0] + x, o[1] + y, o[2] + z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, yaw, 0)), V(...s));
const col = (key: string, c: string) => lam("c_" + key, () => ({ color: c }));
/** wall quad facing +n (n = "+z" | "+x" | "-x") */
const wall = (b: Batch, mat: THREE.Material, o: V3, kind: "back" | "left" | "right", x0: number, x1: number, h: number, pos: number, u = 1, v = 1) => {
  const [X, Y, Z] = o;
  if (kind === "back") b.add(quad(V(X + x0, Y, Z + pos), V(X + x1, Y, Z + pos), V(X + x1, Y + h, Z + pos), V(X + x0, Y + h, Z + pos), u, v), mat);
  if (kind === "left") b.add(quad(V(X + pos, Y, Z + x1), V(X + pos, Y, Z + x0), V(X + pos, Y + h, Z + x0), V(X + pos, Y + h, Z + x1), u, v), mat);
  if (kind === "right") b.add(quad(V(X + pos, Y, Z + x0), V(X + pos, Y, Z + x1), V(X + pos, Y + h, Z + x1), V(X + pos, Y + h, Z + x0), u, v), mat);
};
const floor = (b: Batch, mat: THREE.Material, o: V3, w: number, d: number, u: number, v: number, y = 0) =>
  b.add(quad(V(o[0] - w / 2, o[1] + y, o[2] + d / 2), V(o[0] + w / 2, o[1] + y, o[2] + d / 2), V(o[0] + w / 2, o[1] + y, o[2] - d / 2), V(o[0] - w / 2, o[1] + y, o[2] - d / 2), u, v), mat);
const unlit = (key: string, map: THREE.Texture, c = new THREE.Color(1, 1, 1)) => {
  const m = new THREE.MeshBasicMaterial({ map, color: c });
  return m;
};

/** map table: four turned legs, wood frame, the painted map on top */
const mapTable = (b: Batch, c: V3, wood: string) => {
  const W = MAP_W + 0.24, D = MAP_D + 0.24, w = col("wood" + wood, wood);
  box(b, w, c, -W / 2, W / 2, TABLE_Y - 0.12, TABLE_Y, -D / 2, D / 2);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) box(b, w, c, sx * (W / 2 - 0.2) - 0.08, sx * (W / 2 - 0.2) + 0.08, 0, TABLE_Y - 0.12, sz * (D / 2 - 0.2) - 0.08, sz * (D / 2 - 0.2) + 0.08);
  const top = lam("mapTop", () => ({ map: mapTex() }));
  b.add(quad(V(c[0] - MAP_W / 2, TABLE_Y + 0.004, c[2] + MAP_D / 2), V(c[0] + MAP_W / 2, TABLE_Y + 0.004, c[2] + MAP_D / 2), V(c[0] + MAP_W / 2, TABLE_Y + 0.004, c[2] - MAP_D / 2), V(c[0] - MAP_W / 2, TABLE_Y + 0.004, c[2] - MAP_D / 2)), top);
};
const lampAt = (root: THREE.Object3D, b: Batch, o: V3, x: number, y: number, z: number) => {
  box(b, col("brass", "#b89a52"), o, x - 0.12, x + 0.12, y, y + 0.04, z - 0.12, z + 0.12);
  box(b, col("brass", "#b89a52"), o, x - 0.02, x + 0.02, y, y + 0.42, z - 0.02, z + 0.02);
  b.add(new THREE.ConeGeometry(0.2, 0.2, 18, 1, true), lam("shade_g", () => ({ color: "#2f6a43", side: THREE.DoubleSide })), at(o, x, y + 0.5, z));
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(4, 3.4, 2.2) }));
  bulb.position.set(o[0] + x, o[1] + y + 0.42, o[2] + z); bulb.layers.set(NOINK); root.add(bulb);
};
const chair = (b: Batch, o: V3, x: number, z: number, yaw: number, c: string) => {
  const m = col("chair" + c, c), M = at(o, x, 0, z, [1, 1, 1], yaw);
  for (const [x0, x1, y0, y1, z0, z1] of [[-0.25, 0.25, 0.45, 0.52, -0.25, 0.25], [-0.25, 0.25, 0.52, 1.0, -0.27, -0.21],
    [-0.24, -0.18, 0, 0.45, -0.24, -0.18], [0.18, 0.24, 0, 0.45, -0.24, -0.18], [-0.24, -0.18, 0, 0.45, 0.18, 0.24], [0.18, 0.24, 0, 0.45, 0.18, 0.24]])
    b.add(UB, m, M.clone().multiply(new THREE.Matrix4().compose(V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), new THREE.Quaternion(), V(x1 - x0, y1 - y0, z1 - z0))));
};
const desk = (b: Batch, o: V3, x: number, z: number, w: number, d: number, c: string) => {
  const m = col("desk" + c, c);
  box(b, m, o, x - w / 2, x + w / 2, 0.72, 0.78, z - d / 2, z + d / 2);
  box(b, m, o, x - w / 2, x - w / 2 + 0.45, 0, 0.72, z - d / 2 + 0.05, z + d / 2 - 0.05);
  box(b, m, o, x + w / 2 - 0.45, x + w / 2, 0, 0.72, z - d / 2 + 0.05, z + d / 2 - 0.05);
  box(b, lam("blotter", () => ({ map: blotter() })), o, x - w / 2 + 0.1, x + w / 2 - 0.1, 0.78, 0.785, z - d / 2 + 0.1, z + d / 2 - 0.1);
};

// ---------------- the sets ----------------
export type Sets = { decoy: THREE.Object3D[]; boat: THREE.Object3D; stone: THREE.Object3D };

const buildRoom = (root: THREE.Object3D, b: Batch) => {
  const o = ROOM;
  floor(b, lam("roomFloor", () => ({ map: rep(planksHD(), 3, 3) })), o, 14, 14, 3, 3);
  const wp = lam("roomWall", () => ({ map: rep(wallpaper("room", "#d9cfae", "#cdbf98"), 4, 1.5) }));
  const pn = lam("roomPanel", () => ({ map: rep(panel("room", "#6e4a30"), 6, 1) }));
  wall(b, wp, o, "back", -7, 7, 4.6, -4.2); wall(b, wp, o, "left", -7, 7, 4.6, -5.2); wall(b, wp, o, "right", -7, 7, 4.6, 5.2);
  box(b, pn, o, -7, 7, 0, 1.1, -4.2, -4.12); box(b, pn, o, -5.2, -5.12, 0, 1.1, -7, 7); box(b, pn, o, 5.12, 5.2, 0, 1.1, -7, 7);
  box(b, col("rail", "#4e3322"), o, -7, 7, 1.1, 1.16, -4.14, -4.06);
  // window on the back wall + frame, blackout curtains
  b.add(quad(V(-3.6, 1.4, -4.1), V(-1.6, 1.4, -4.1), V(-1.6, 4.0, -4.1), V(-3.6, 4.0, -4.1)), unlit("roomWin", windowTex("room", "#8fb8e6", "#d4e3ef"), new THREE.Color(1.15, 1.15, 1.15)));
  const cur = lam("roomCur", () => ({ map: drape("room", "#3c3f5c") }));
  for (const x of [-4.05, -1.15]) box(b, cur, o, x - 0.3, x + 0.3, 1.2, 4.3, -4.08, -3.98);
  // bookcase on the right wall, filing cabinets, clock-free wall map frame on the left wall
  b.add(quad(V(5.08, 0, -1.5), V(5.08, 0, 1.5), V(5.08, 2.6, 1.5), V(5.08, 2.6, -1.5)), lam("books", () => ({ map: books() })));
  box(b, col("case", "#5a3a26"), o, 4.7, 5.12, 0, 2.7, -1.6, -1.5); box(b, col("case", "#5a3a26"), o, 4.7, 5.12, 0, 2.7, 1.5, 1.6); box(b, col("case", "#5a3a26"), o, 4.7, 5.12, 2.6, 2.7, -1.6, 1.6);
  for (const z of [-3.2, -2.5]) { box(b, col("filing", "#7d8a7a"), o, 4.4, 5.1, 0, 1.4, z - 0.32, z + 0.32); for (const y of [0.3, 0.75, 1.15]) box(b, col("handle", "#c9ccd2"), o, 4.36, 4.4, y, y + 0.05, z - 0.1, z + 0.1); }
  mapTable(b, TABLE_C(o), "#7a4f33");
  desk(b, o, 2.4, -3.2, 2.0, 0.9, "#6e4a30");
  // (no desk lamp: the desk-insert camera ends where its shade stood)
  for (const [x, z, y] of [[-1.2, 1.2, 0], [1.4, 1.25, 0.2]] as const) chair(b, o, x, z + 0.4, y, "#5a3a26");
  // wall picture frames (abstract landscapes, no text)
  b.add(quad(V(0.2, 1.75, -4.1), V(2.6, 1.75, -4.1), V(2.6, 3.08, -4.1), V(0.2, 3.08, -4.1)), lam("wallMap", () => ({ map: mapTex() })));
  box(b, col("mapFrame", "#4e3322"), o, 0.12, 2.68, 1.68, 1.75, -4.12, -4.06); box(b, col("mapFrame", "#4e3322"), o, 0.12, 2.68, 3.08, 3.15, -4.12, -4.06);
  if (false) b.add(quad(V(0.6, 1.9, -4.1), V(2.0, 1.9, -4.1), V(2.0, 2.9, -4.1), V(0.6, 2.9, -4.1)), lam("pic1", () => ({ map: ctex("pic1", 256, 192, (g) => { g.fillStyle = "#9cc0d8"; g.fillRect(0, 0, 256, 192); g.fillStyle = "#6f8f4a"; g.beginPath(); g.moveTo(0, 130); g.quadraticCurveTo(120, 70, 256, 120); g.lineTo(256, 192); g.lineTo(0, 192); g.fill(); g.strokeStyle = "#7a5a2a"; g.lineWidth = 18; g.strokeRect(9, 9, 238, 174); }) })));
};

const buildBerlin = (root: THREE.Object3D, b: Batch) => {
  const o = BERLIN;
  floor(b, lam("bFloor", () => ({ map: rep(stoneHD("bFloorHD", ["#8a8580", "#938e88", "#7f7a75", "#9a958f"], "#5c5853"), 4, 4) })), o, 14, 14, 4, 4);
  const wp = lam("bWall", () => ({ map: rep(wallpaper("berlin", "#a9a49a", "#9d988e"), 4, 1.5) }));
  wall(b, wp, o, "back", -7, 7, 5.2, -4.2); wall(b, wp, o, "left", -7, 7, 5.2, -5.2); wall(b, wp, o, "right", -7, 7, 5.2, 5.2);
  box(b, col("bBase", "#4a4642"), o, -7, 7, 0, 0.4, -4.2, -4.1);
  // tall window between deep red drapes
  b.add(quad(V(o[0] - 1.0, 1.2, -4.1), V(o[0] + 1.0, 1.2, -4.1), V(o[0] + 1.0, 4.4, -4.1), V(o[0] - 1.0, 4.4, -4.1)), unlit("bWin", windowTex("berlin", "#9fb4cc", "#d9dfe6"), new THREE.Color(1.1, 1.1, 1.1)));
  const dr = lam("bDrape", () => ({ map: drape("berlin", "#8a1f24") }));
  for (const x of [-1.6, 1.6]) box(b, dr, o, x - 0.55, x + 0.55, 0, 5.0, -4.08, -3.9);
  box(b, col("bPelmet", "#5e1418"), o, -2.3, 2.3, 4.6, 5.0, -4.05, -3.85);
  for (const x of [-4.2, 4.2]) { box(b, col("bPillar", "#c2bcb0"), o, x - 0.3, x + 0.3, 0, 5.2, -4.2, -3.8); }
  mapTable(b, TABLE_C(o), "#3e2a20");
  lampAt(root, b, o, 1.55, TABLE_Y, -1.3);
};

const buildSpain = (root: THREE.Object3D, b: Batch) => {
  const o = SPAIN;
  floor(b, lam("sFloor", () => ({ map: rep(ctex("terracotta", 512, 512, (g, r) => { for (let y = 0; y < 512; y += 128) for (let x = 0; x < 512; x += 128) { g.fillStyle = jit(r, "#c4724a", 0.08); g.fillRect(x, y, 128, 128); g.strokeStyle = "rgba(80,40,30,0.5)"; g.lineWidth = 6; g.strokeRect(x, y, 128, 128); } }), 7, 7) })), o, 14, 14, 7, 7);
  const wp = lam("sWall", () => ({ color: "#f1ebdc" }));
  wall(b, wp, o, "back", -7, 7, 4.4, -3.6); wall(b, wp, o, "left", -7, 7, 4.4, -4.6); wall(b, wp, o, "right", -7, 7, 4.4, 4.6);
  const tl = lam("sTiles", () => ({ map: rep(tiles(), 14, 1.2) }));
  box(b, tl, o, -7, 7, 0, 1.2, -3.6, -3.52); box(b, tl, o, -4.6, -4.52, 0, 1.2, -7, 7);
  b.add(quad(V(o[0] - 2.6, 1.4, -3.5), V(o[0] - 0.8, 1.4, -3.5), V(o[0] - 0.8, 3.8, -3.5), V(o[0] - 2.6, 3.8, -3.5)), unlit("sWin", windowTex("spain", "#5fa2e8", "#bfe0f6", true), new THREE.Color(1.15, 1.15, 1.15)));
  for (const x of [-2.8, -0.6]) box(b, col("sShut", "#2f6a43"), o, x - 0.22, x + 0.22, 1.35, 3.85, -3.5, -3.42);
  desk(b, o, 0.6, -1.0, 2.2, 1.0, "#7a4a2c");
  lampAt(root, b, o, 1.4, 0.785, -1.25);
  chair(b, o, 0.6, -1.85, 0, "#5a3a26");
  // ceiling-less fan pole + picture
  b.add(quad(V(o[0] + 1.6, 1.9, -3.5), V(o[0] + 3.0, 1.9, -3.5), V(o[0] + 3.0, 2.9, -3.5), V(o[0] + 1.6, 2.9, -3.5)), lam("pic2", () => ({ map: ctex("pic2", 256, 192, (g) => { g.fillStyle = "#f6d28a"; g.fillRect(0, 0, 256, 192); g.fillStyle = "#e07a3c"; g.beginPath(); g.arc(128, 110, 50, 0, 7); g.fill(); g.fillStyle = "#3f7fb5"; g.fillRect(0, 140, 256, 52); g.strokeStyle = "#7a5a2a"; g.lineWidth = 18; g.strokeRect(9, 9, 238, 174); }) })));
  // potted palm
  b.add(new THREE.CylinderGeometry(0.3, 0.22, 0.55, 16), col("pot", "#b8684a"), at(o, 3.6, 0.275, -2.8));
  for (let i = 0; i < 7; i++) {
    const a = (i / 7) * Math.PI * 2, L = new THREE.SphereGeometry(1, 12, 8).scale(0.55, 0.08, 0.16).translate(0.5, 0, 0);
    b.add(L, col("palmLeaf", "#4f8f45"), new THREE.Matrix4().compose(V(o[0] + 3.6, 1.35, o[2] - 2.8), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, a, -0.5)), V(1, 1, 1)));
  }
  b.add(new THREE.CylinderGeometry(0.05, 0.06, 0.85, 8), col("palmTrunk", "#7a5a3a"), at(o, 3.6, 0.95, -2.8));
};

const palm = (b: Batch, o: V3, x: number, z: number, h: number) => {
  for (let i = 0; i < 6; i++) b.add(new THREE.CylinderGeometry(0.2 - i * 0.015, 0.22 - i * 0.015, h / 6, 10), col("trunk", "#8a6a48"), at(o, x + Math.sin(i * 0.3) * 0.15 * i, (i + 0.5) * (h / 6), z));
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    b.add(new THREE.SphereGeometry(1, 12, 8).scale(1.7, 0.12, 0.38).translate(1.5, -0.35, 0), col("frond", "#4f8f45"),
      new THREE.Matrix4().compose(V(o[0] + x + 0.6, h, o[2] + z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, a, -0.35)), V(1, 1, 1)));
  }
};
const SPAIN_STYLES: Style[] = [
  { wall: "#f4efe3", shutter: "#2f6a43", roof: "#c9775a" }, { wall: "#f0e2bf", shutter: "#3f6fb5", roof: "#b8644f" },
  { wall: "#f6f1e6", shutter: "#8c3b4a", roof: "#d27a62" }, { wall: "#ecd29a", shutter: "#2f5f6a", roof: "#c9775a" },
];

const buildSea = (root: THREE.Object3D, b: Batch): THREE.Object3D => {
  const o = SEA;
  // sea: a huge two-tone plane, painted crests, tinted blue (lighting does the rest)
  const sea = twoTone(new THREE.MeshLambertMaterial({ color: "#2f86b4", map: rep(seaTex(), 120, 120) }), 0.6);
  const sm = new THREE.Mesh(new THREE.PlaneGeometry(2600, 2600).rotateX(-Math.PI / 2), sea);
  sm.position.set(o[0], -0.02, o[2]); sm.receiveShadow = true; root.add(sm);
  // the coast: beach strip, low hills, a white town and a church tower, palms (~140-220 m from the submarine)
  const cz = o[2] - 150;
  b.add(quad(V(o[0] - 700, 0.05, cz + 10), V(o[0] + 700, 0.05, cz + 10), V(o[0] + 700, 0.6, cz - 20), V(o[0] - 700, 0.6, cz - 20), 140, 6), lam("sand", () => ({ map: sandTex() })));
  b.add(quad(V(o[0] - 700, 0.6, cz - 20), V(o[0] + 700, 0.6, cz - 20), V(o[0] + 700, 0.6, cz - 400), V(o[0] - 700, 0.6, cz - 400), 70, 20), lam("dryGrass", () => ({ map: grassHD(), color: "#e9d7a0" })));
  for (let i = 0; i < 14; i++) {
    const x = -600 + i * 95 + ((i * 37) % 40), z = cz - 120 - ((i * 53) % 90), s = 45 + ((i * 29) % 40);
    b.add(new THREE.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2).scale(s * 1.8, s * 0.38, s), col("hill" + (i % 2), i % 2 ? "#9fae6a" : "#b9b072"), at(o, x, 0.5, z - o[2]));
  }
  let x = -95;
  for (let i = 0; x < 95; i++) {
    const w = [7, 9, 6][i % 3], h = [6, 7.5, 9][i % 3];
    house(b, o[0] + x + w / 2, cz - 32 - (i % 2) * 9, 0, w, 8, h, SPAIN_STYLES[i % 4], 0.6, true);
    x += w + 1.5;
  }
  const tw = col("tower", "#f4efe3");
  box(b, tw, o, 22, 30, 0.6, 26, -150 - 52, -150 - 44); b.add(new THREE.ConeGeometry(5.6, 8, 4).rotateY(Math.PI / 4), col("towerRoof", "#c9775a"), at(o, 26, 30, -150 - 48));
  for (const px of [-60, -40, -18, 12, 44, 70]) palm(b, o, px, -150 - 8 + (px % 7), 9 + (px % 3));
  // HMS Seraph: long dark hull riding low, conning tower, periscope, deck rail
  const iron = twoTone(new THREE.MeshPhongMaterial({ color: "#4b525e", specular: "#8a8a8a", shininess: 40 }), 0.15);
  const hull = new THREE.CylinderGeometry(2.2, 2.2, 52, 28, 1).rotateZ(Math.PI / 2);
  b.add(hull, iron, at(o, 0, 0.2, 0, [1, 0.55, 0.85]));
  for (const s of [-1, 1]) b.add(new THREE.ConeGeometry(2.2, 10, 28).rotateZ(s * -Math.PI / 2), iron, at(o, s * 31, 0.2, 0, [1, 0.55, 0.85]));
  box(b, col("subDeck", "#5d6470"), o, -22, 22, 1.18, 1.32, -0.9, 0.9);
  box(b, iron, o, -3.4, 3.4, 1.3, 4.6, -1.2, 1.2);
  b.add(new THREE.CylinderGeometry(1.2, 1.2, 3.3, 20, 1, false, 0, Math.PI).rotateZ(Math.PI / 2).rotateX(Math.PI / 2), iron, at(o, 3.4, 2.95, 0, [1, 1, 1]));
  for (const [px, h] of [[-1.2, 3.2], [0.4, 2.4]] as const) b.add(new THREE.CylinderGeometry(0.1, 0.1, h, 8), iron, at(o, px, 4.6 + h / 2, 0));
  for (let k = -9; k <= 9; k++) b.add(new THREE.CylinderGeometry(0.03, 0.03, 0.7, 6), col("rail", "#3b3f46"), at(o, -16 + k * 0.9 + 9, 1.67, 0.85));
  // the rowing boat (moved per frame by world.ts)
  const boat = new THREE.Group();
  const bb = new Batch();
  const hullG = new THREE.SphereGeometry(1, 28, 14, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2).scale(2.4, 0.75, 0.95);
  bb.add(hullG, lam("boatHull", () => ({ color: "#3f6fb5", side: THREE.DoubleSide })));
  bb.add(new THREE.TorusGeometry(1, 0.06, 6, 40).rotateX(Math.PI / 2).scale(2.4, 1, 0.95), col("gunwale", "#f1ece0"));
  bb.add(new THREE.BoxGeometry(0.3, 0.06, 1.7).translate(0.3, -0.25, 0), col("thwart", "#c99669"));
  for (const s of [-1, 1]) bb.add(new THREE.CylinderGeometry(0.035, 0.035, 3.2, 6).rotateX(Math.PI / 2 - s * 0.35).rotateY(0.25 * s).translate(0.3, 0.05, s * 1.2), col("oar", "#c99669"));
  bb.build(boat);
  root.add(boat);
  return boat;
};

const buildStreet = (root: THREE.Object3D, b: Batch) => {
  const o = STREET;
  floor(b, lam("street", () => ({ map: rep(cobbleHD(), 10, 40) })), o, 14, 300, 10, 40, 0.01);
  for (const s of [-1, 1]) floor(b, lam("pave", () => ({ map: rep(stoneHD("paveHD", ["#b9b3a8", "#aea89d", "#c3bdb2", "#a69f94"], "#8a847a"), 1, 30) })), [o[0] + s * 9, 0.12, o[2]], 4, 300, 1, 30, 0);
  for (const s of [-1, 1]) box(b, col("kerb", "#9a948a"), o, s * 7 - 0.15, s * 7 + 0.15, 0, 0.14, -150, 150);
  for (const s of [-1, 1]) {
    let z = -120, i = 0;
    while (z < 60) { const w = [7, 8, 6.5][i % 3]; house(b, o[0] + s * 15, o[2] + z + w / 2, s > 0 ? -Math.PI / 2 : Math.PI / 2, w, 8, [8.4, 9.8, 7][i % 3], i % 2 ? 7 : 2 + (i % 3) * 3, 0); z += w + 0.2; i++; }
  }
  // bench (where Glyndwr sits), lamp posts, a sandbag pile and a pillar box
  const bench = col("bench", "#4f6a3a");
  box(b, bench, o, -9.6, -7.8, 0.42, 0.48, 1.55, 2.25);
  for (const y of [0.62, 0.9]) box(b, bench, o, -9.6, -7.8, y, y + 0.12, 1.42, 1.5);
  for (const x of [-9.4, -8.0]) { box(b, col("benchLeg", "#2e2a30"), o, x - 0.05, x + 0.05, 0.12, 0.45, 1.55, 1.65); box(b, col("benchLeg", "#2e2a30"), o, x - 0.05, x + 0.05, 0.12, 0.45, 2.15, 2.25); box(b, col("benchLeg", "#2e2a30"), o, x - 0.04, x + 0.04, 0.45, 1.05, 1.4, 1.48); }
  for (const z of [-30, -10, 10, 30]) { b.add(new THREE.CylinderGeometry(0.08, 0.12, 4.2, 10), col("lampPost", "#2e3a33"), at(o, -7.6, 2.1, z)); b.add(new THREE.BoxGeometry(0.45, 0.6, 0.45), col("lampHead", "#2e3a33"), at(o, -7.6, 4.4, z)); }
  for (let i = 0; i < 9; i++) b.add(new THREE.SphereGeometry(1, 14, 8).scale(0.45, 0.16, 0.28), col("sandbag", "#c9b27a"), at(o, 8.2 + (i % 3) * 0.75 - (Math.floor(i / 3) % 2) * 0.35, 0.28 + Math.floor(i / 3) * 0.3, -6));
  b.add(new THREE.CylinderGeometry(0.28, 0.28, 1.5, 16), col("pillar", "#c0393f"), at(o, -8.0, 0.87, -4.5));
  b.add(new THREE.SphereGeometry(0.29, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), col("pillar", "#c0393f"), at(o, -8.0, 1.62, -4.5));
};

const buildGrave = (root: THREE.Object3D, b: Batch): THREE.Object3D => {
  const o = GRAVE;
  floor(b, lam("gGrass", () => ({ map: rep(grassHD(), 1, 1) })), o, 600, 600, 60, 60);
  floor(b, lam("gravel", () => ({ map: rep(sandTex(), 6, 30) })), [o[0], 0.01, o[2]], 3, 80, 6, 30, 0);
  // white cemetery wall behind, with tiled cap
  const wl = col("gWall", "#f4efe3");
  box(b, wl, o, -40, 40, 0, 2.6, -14, -13.4); box(b, col("gCap", "#c9775a"), o, -40.2, 40.2, 2.6, 2.8, -14.15, -13.25);
  for (const x of [-16, -6, 6, 16, 26, -26]) { const s = 1 + ((x * 7) % 3) * 0.15; b.add(new THREE.SphereGeometry(1, 16, 12).scale(1.1 * s, 5.2 * s, 1.1 * s), col("cypress", "#2f5a35"), at(o, x, 4.6 * s, -16 - (x % 5))); }
  // rows of headstones (Portland stone, rounded tops)
  const st = lam("pStone", () => ({ color: "#ebe5d6" }));
  const stone = (x: number, z: number, s = 1) => {
    box(b, st, o, x - 0.38 * s, x + 0.38 * s, 0, 0.95 * s, z - 0.09, z + 0.09);
    b.add(new THREE.CylinderGeometry(0.38 * s, 0.38 * s, 0.18, 20, 1, false, -Math.PI / 2, Math.PI).rotateX(Math.PI / 2), st, at(o, x, 0.95 * s, z));
  };
  for (const z of [-6, -2, 6]) for (let x = -12; x <= 12; x += 2.2) if (Math.abs(x) > 1.5 || z !== -2) stone(x, z);
  for (let x = -12; x <= 12; x += 2.2) if (Math.abs(x) > 1.6) stone(x, 2);
  // Martin's stone (centre, z = 2): its own object so the engraving card can sit on its face
  const g = new THREE.Group(), gb = new Batch();
  gb.add(new THREE.BoxGeometry(0.86, 1.05, 0.2).translate(0, 0.525, 0), st);
  gb.add(new THREE.CylinderGeometry(0.43, 0.43, 0.2, 24, 1, false, -Math.PI / 2, Math.PI).rotateX(Math.PI / 2).translate(0, 1.05, 0), st);
  gb.add(new THREE.BoxGeometry(1.1, 0.12, 2.0).translate(0, 0.06, 1.05), col("kerbG", "#d9d3c5"));
  gb.build(g);
  g.position.set(o[0], 0, o[2] + 2);
  root.add(g);
  for (let i = 0; i < 6; i++) b.add(new THREE.SphereGeometry(1, 10, 8).scale(0.11, 0.08, 0.11), col("flower" + (i % 3), ["#d9475a", "#f1c45a", "#f2efe6"][i % 3]), at(o, -0.25 + (i % 3) * 0.2, 0.15, 2.3 + Math.floor(i / 3) * 0.18));
  return g;
};

/** the wooden duck decoy (on Sicily in the map rooms): body, head, beak; returned unbatched so it can pop in */
const duck = (root: THREE.Object3D, c: V3): THREE.Object3D => {
  const g = new THREE.Group(), b = new Batch();
  b.add(new THREE.SphereGeometry(1, 20, 12).scale(0.12, 0.065, 0.075).translate(0, 0.06, 0), col("duck", "#8a5a34"));
  b.add(new THREE.SphereGeometry(0.045, 16, 10).translate(0.09, 0.14, 0), col("duckHead", "#2f6a43"));
  b.add(new THREE.ConeGeometry(0.018, 0.06, 10).rotateZ(-Math.PI / 2).translate(0.15, 0.135, 0), col("beak", "#e8a23a"));
  b.add(new THREE.BoxGeometry(0.1, 0.02, 0.08).translate(-0.08, 0.1, 0), col("duckTail", "#6e4a30"));
  b.build(g);
  g.position.set(...c); g.rotation.y = 0.5; g.scale.setScalar(0.7);
  root.add(g);
  return g;
};

export const buildSets = (root: THREE.Object3D): Sets => {
  const b = new Batch();
  buildRoom(root, b);
  buildBerlin(root, b);
  buildSpain(root, b);
  const boat = buildSea(root, b);
  buildStreet(root, b);
  const stone = buildGrave(root, b);
  b.build(root);
  const decoy = [duck(root, mapPt(TABLE_C(ROOM), PLACES.sicily[0], PLACES.sicily[1])), duck(root, mapPt(TABLE_C(BERLIN), PLACES.sicily[0], PLACES.sicily[1]))];
  return { decoy, boat, stone };
};
