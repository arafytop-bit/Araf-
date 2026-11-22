// Flat 2D effect / insert drawings for the Mincemeat short (our own drawings, ink #241726, no text anywhere).
// Every drawer paints into the canvas size given in its comment; cast.ts places them as unlit cards.
import { Pen, INK, shade } from "./toon";

type P2 = [number, number];
const rr = (x0: number, y0: number, x1: number, y1: number, r: number): P2[] => {
  const pts: P2[] = [];
  const c = [[x1 - r, y0 + r, -90], [x1 - r, y1 - r, 0], [x0 + r, y1 - r, 90], [x0 + r, y0 + r, 180]] as const;
  for (const [cx, cy, a0] of c) for (let i = 0; i <= 6; i++) { const a = ((a0 + i * 15) * Math.PI) / 180; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); }
  return pts;
};
const lines = (p: Pen, x0: number, y0: number, w: number, n: number, gap: number, col = "#8a93ad", lw = 5, seed = 1) => {
  for (let i = 0; i < n; i++) {
    const k = 0.55 + 0.45 * Math.abs(Math.sin(seed * 3.1 + i * 1.7));
    p.stroke([[x0, y0 + i * gap], [x0 + w * k, y0 + i * gap + 1]], lw, col);
  }
};

/** 256 x 256: a house fly, wings up/down by beat */
export const fxFly = (p: Pen, beat: number) => {
  const up = beat % 2 === 0;
  for (const s of [-1, 1]) p.ell(128 + s * 34, up ? 92 : 116, 34, 20, "#e8f2ff", 6, 0, 360, s * (up ? -35 : -10));
  p.ell(128, 136, 30, 38, "#2a2733", 8);
  p.ell(128, 98, 22, 20, "#2a2733", 7);
  p.dot(118, 94, 6, "#c0393f"); p.dot(138, 94, 6, "#c0393f");
};

/** 512 x 256: fat map arrow pointing right, grown to fraction k (0..1) */
export const fxArrow = (p: Pen, k: number, col: string) => {
  const L = 40 + 420 * k;
  p.poly([[20, 100], [L - 70, 100], [L - 70, 50], [L, 128], [L - 70, 206], [L - 70, 156], [20, 156]], col, 12);
  p.stroke([[34, 112], [L - 84, 112]], 8, shade(col, 1.25));
};

/** 256 x 384: little map pin flag (Union-ish colours kept abstract: blue field, red + white cross) */
export const fxPin = (p: Pen, col: string) => {
  p.stroke([[60, 60], [60, 370]], 10, INK);
  p.poly([[60, 40], [220, 70], [60, 160]], col, 8);
  p.dot(60, 372, 14, "#c9ccd2");
};

/** 512 x 640: photo of "Pam" (a smiling woman in a bathing costume, the real snapshot was a beach photo) */
export const fxPam = (p: Pen) => {
  p.poly(rr(20, 20, 492, 620, 10), "#f7f2e4", 10);
  const photo = rr(52, 52, 460, 520, 4);
  p.poly(photo, "#9ec3dc", 6);
  p.clip(photo, () => {
    p.poly([[52, 420], [460, 380], [460, 520], [52, 520]], "#ecd9a8", 0);
    p.ell(256, 300, 150, 150, "#8a4b2c", 0);               // long hair behind the head
    p.poly([[110, 300], [402, 300], [420, 470], [92, 470]], "#8a4b2c", 0);
    p.ell(256, 560, 130, 150, "#d9475a", 8);               // bathing costume
    p.ell(256, 250, 92, 100, "#f5d2b0", 9);
    p.poly([[162, 236], [178, 150], [256, 124], [334, 150], [350, 236], [320, 176], [256, 160], [192, 176]], "#8a4b2c", 8);
    p.ell(222, 248, 9, 12, "#241726", 0); p.ell(290, 248, 9, 12, "#241726", 0);
    for (const s of [-1, 1]) { p.stroke([[256 + s * 34, 236], [256 + s * 48, 226]], 4); }
    p.ell(256, 296, 22, 12, "#c8323a", 5);                  // lipstick smile
    p.dot(160, 290, 9, "#e8c45a"); p.dot(352, 290, 9, "#e8c45a"); // earrings
  });
  p.poly(photo, null, 6);
};

/** 512 x 384: envelope, `heart` seals it */
export const fxEnvelope = (p: Pen, heart: boolean) => {
  p.poly(rr(24, 40, 488, 344, 12), "#f4ecd8", 10);
  p.poly([[24, 52], [256, 220], [488, 52]], null, 8);
  if (heart) {
    const hx = 256, hy = 214;
    p.poly([[hx, hy + 48], [hx - 52, hy - 2], [hx - 44, hy - 34], [hx - 18, hy - 40], [hx, hy - 18], [hx + 18, hy - 40], [hx + 44, hy - 34], [hx + 52, hy - 2]], "#d6334a", 7);
  }
  lines(p, 70, 280, 150, 2, 22, "#9aa0b6", 6, 3);
};

/** 384 x 640: receipt with a drawn ring */
export const fxReceipt = (p: Pen) => {
  const z: P2[] = [[30, 20], [354, 20]];
  for (let i = 0; i <= 12; i++) z.push([354 - i * 27, 620 - (i % 2) * 16]);
  p.poly(z, "#fbf8ee", 8);
  p.ell(192, 160, 62, 62, null, 16); p.ell(192, 160, 62, 62, null, 0);
  p.arc(192, 160, 62, 62, 0, 360, 14, "#e8c45a");
  p.poly([[192, 70], [222, 96], [192, 118], [162, 96]], "#bfe6ff", 6);
  lines(p, 60, 280, 260, 7, 40, "#9aa0b6", 6, 7);
  p.stroke([[60, 560], [320, 560]], 8, INK);
};

/** 512 x 320: two torn theatre ticket stubs */
export const fxTickets = (p: Pen) => {
  const stub = (x: number, y: number, a: number, col: string) => {
    const pts: P2[] = [[x, y], [x + 200, y], [x + 200, y + 40], [x + 188, y + 60], [x + 200, y + 80], [x + 200, y + 120], [x, y + 120]];
    p.rot = [a, x + 100, y + 60];
    p.poly(pts, col, 8);
    p.ell(x + 60, y + 60, 30, 30, null, 6);
    p.dot(x + 60, y + 60, 9, INK);
    p.stroke([[x + 110, y + 40], [x + 170, y + 40]], 6, "#7d5a3a"); p.stroke([[x + 110, y + 80], [x + 160, y + 80]], 6, "#7d5a3a");
    p.rot = null;
  };
  stub(40, 60, -0.12, "#f1c45a"); stub(250, 130, 0.1, "#e98a6b");
};

/** 512 x 640: the grumpy bank letter: letterhead bar, a frowning seal, an underlined total */
export const fxBankLetter = (p: Pen) => {
  p.poly(rr(30, 20, 482, 620, 8), "#fbf9f2", 9);
  p.poly(rr(30, 20, 482, 110, 8), "#3a5a8c", 9);
  p.ell(400, 200, 54, 54, "#c0393f", 8);
  p.arc(400, 222, 24, 12, 200, 340, 8, "#fbf9f2");
  p.stroke([[380, 186], [392, 192]], 7, "#fbf9f2"); p.stroke([[420, 186], [408, 192]], 7, "#fbf9f2");
  lines(p, 70, 180, 240, 3, 36, "#8a93ad", 7, 2);
  lines(p, 70, 320, 330, 5, 36, "#8a93ad", 7, 5);
  p.stroke([[300, 540], [440, 540]], 10, "#c0393f"); p.stroke([[300, 560], [440, 560]], 10, "#c0393f");
  p.stroke([[310, 518], [430, 518]], 9, INK);
};

/** 512 x 384: open leather wallet */
export const fxWallet = (p: Pen) => {
  p.poly(rr(30, 60, 482, 340, 26), "#7a4a2c", 10);
  p.stroke([[256, 64], [256, 336]], 8, "#4a2c18");
  p.poly(rr(60, 110, 236, 300, 12), "#8e5a38", 6);
  p.poly(rr(276, 110, 452, 300, 12), "#8e5a38", 6);
};

/** 256 x 256: a moth, wings flapping by beat */
export const fxMoth = (p: Pen, beat: number) => {
  const k = beat % 2 ? 0.55 : 1;
  for (const s of [-1, 1]) {
    p.ell(128 + s * 50 * k, 110, 52 * k, 40, "#d7c8a6", 6);
    p.ell(128 + s * 36 * k, 160, 34 * k, 26, "#c4b28c", 6);
  }
  p.ell(128, 136, 14, 46, "#8a7454", 6);
  p.stroke([[122, 92], [104, 64]], 4); p.stroke([[134, 92], [152, 64]], 4);
};

/** 256 x 1024: fishing line from the top with a hook and the letter as bait at the bottom */
export const fxHook = (p: Pen, bait = true) => {
  p.stroke([[128, 0], [128, 760]], 5, "#e8eef4");
  p.stroke([[128, 0], [128, 760]], 2, "#9aa6b4");
  p.arc(128, 820, 46, 50, -90, 200, 13, "#9aa6b4");
  p.arc(128, 820, 46, 50, -90, 200, 3, INK);
  p.poly([[78, 790], [70, 744], [96, 780]], "#9aa6b4", 4);
  if (!bait) return;
  p.rot = [0.25, 150, 900];
  p.poly(rr(70, 840, 230, 990, 6), "#fbf8ee", 8);
  lines(p, 90, 880, 110, 3, 28, "#7d8aa6", 6, 9);
  p.rot = null;
};

/** 384 x 384: a tumbleweed (rotation by rot) */
export const fxTumble = (p: Pen) => {
  p.ell(192, 192, 150, 140, null, 10);
  for (let i = 0; i < 14; i++) {
    const a = i * 0.9, b = a + 2.2;
    p.arc(192 + 30 * Math.cos(a), 192 + 30 * Math.sin(a), 120, 100, (a * 180) / Math.PI, (b * 180) / Math.PI, 6, "#b08a52");
  }
  p.ell(192, 192, 150, 140, null, 7);
};

/** 384 x 384: rat-poison tin: a squat tin with a rat silhouette and a cross on the label */
export const fxTin = (p: Pen) => {
  p.poly([[60, 110], [324, 110], [324, 330], [60, 330]], "#c8b23a", 10);
  p.ell(192, 110, 132, 30, "#d9c64e", 9);
  p.ell(192, 330, 132, 30, null, 9, 0, 180);
  p.poly(rr(90, 160, 294, 300, 12), "#f3eddc", 7);
  p.ell(170, 240, 46, 26, "#5a5560", 6); p.ell(124, 226, 18, 16, "#5a5560", 6);
  p.dot(116, 220, 4, "#f3eddc");
  p.stroke([[216, 246], [270, 270]], 6, "#5a5560");
  p.stroke([[234, 186], [270, 222]], 10, "#c0393f"); p.stroke([[270, 186], [234, 222]], 10, "#c0393f");
};

/** 512 x 512: plans sheet: map scribble with a big arrow */
export const fxPlans = (p: Pen) => {
  p.poly(rr(20, 20, 492, 492, 8), "#f1ead2", 10);
  p.poly([[60, 300], [150, 220], [250, 250], [320, 180], [440, 220], [440, 440], [60, 440]], "#d8c79a", 6);
  p.ell(300, 330, 40, 26, "#d8c79a", 6);
  p.line([[120, 410], [240, 330], [360, 150]], "#c0393f", 14, false);
  p.poly([[360, 120], [392, 176], [334, 168]], "#c0393f", 0);
  lines(p, 70, 80, 300, 2, 34, "#7d8aa6", 7, 4);
};

/** 512 x 512: chisel sparks, t 0..1 */
export const fxSparks = (p: Pen, t: number) => {
  for (let i = 0; i < 9; i++) {
    const a = -Math.PI / 2 + (i - 4) * 0.33, r0 = 40 + 160 * t, r1 = r0 + 60 * (1 - t);
    p.stroke([[256 + r0 * Math.cos(a), 300 + r0 * Math.sin(a)], [256 + r1 * Math.cos(a), 300 + r1 * Math.sin(a)]], 10 * (1 - t) + 3, "#ffd36a");
  }
};

/** 1024 x 1280: headstone face lettering as engraved strokes (no readable text): `lines` rows visible, the last row
 *  revealed to fraction k */
export const fxEngrave = (p: Pen, rows: number, k: number) => {
  const g = p.g;
  g.clearRect(0, 0, 1024, 1280);
  // cross at the top
  const cut = "#5f5a63", hi = "#f6f1e6";
  const groove = (pts: P2[], w: number) => { p.stroke(pts.map(([x, y]) => [x + 3, y + 3]) as P2[], w, hi); p.stroke(pts, w, cut); };
  groove([[512, 120], [512, 330]], 26); groove([[430, 190], [594, 190]], 26);
  const widths = [520, 700, 420, 640, 560, 600, 380];
  // rows of engraved grooves (word-length dashes), never letter shapes: no readable text in the film
  for (let r = 0; r < rows; r++) {
    const full = widths[r % widths.length] * 0.8, w = full * (r === rows - 1 ? k : 1), y = 470 + r * 120;
    const x0 = 512 - full / 2;
    let x = x0, n = 0;
    while (x < x0 + w - 20) {
      const len = Math.min(x0 + w - x, 60 + 110 * Math.abs(Math.sin(n * 12.9898 + r * 78.233)));
      groove([[x, y], [x + len, y]], 22);
      x += len + 34; n++;
    }
  }
};

/** 512 x 256: a grey toy tank seen from the side (a reinforcement token on the map) */
export const fxTank = (p: Pen, body = "#7b8089") => {
  p.poly(rr(40, 130, 472, 220, 40), shade(body, 0.76), 9);
  for (let i = 0; i < 5; i++) p.ell(100 + i * 78, 176, 26, 26, "#3b3e44", 6);
  p.poly([[110, 70], [330, 70], [370, 130], [80, 130]], body, 9);
  p.poly([[300, 88], [480, 88], [480, 108], [300, 108]], shade(body, 0.86), 7);
};

/** 256 x 256: small white flash star for the spy camera */
export const fxFlash = (p: Pen, t: number) => {
  const r = 40 + 80 * t;
  const pts: P2[] = [];
  for (let i = 0; i < 16; i++) { const a = (i * Math.PI) / 8, rr2 = i % 2 ? r * 0.35 : r; pts.push([128 + rr2 * Math.cos(a), 128 + rr2 * Math.sin(a)]); }
  p.poly(pts, "#fffbe8", 0);
};

/** 256 x 256: water ring ripple, t 0..1 */
export const fxRipple = (p: Pen, t: number) => {
  p.ell(128, 128, 40 + 80 * t, 16 + 32 * t, null, 10 * (1 - t) + 2);
  p.g.globalCompositeOperation = "source-in"; p.g.fillStyle = "#eaf6ff"; p.g.fillRect(0, 0, 256, 256); p.g.globalCompositeOperation = "source-over";
};
