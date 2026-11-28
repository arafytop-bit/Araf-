// High-fidelity calibration rebuild (frames 0-149). Timing comes only from blueprint.json; look follows analysis/style_bible.md.
// Geometry is in reference pixels (854x480 viewBox); render at 3840x2160 and downscale for 2x supersampling.
import React from 'react';
import {AbsoluteFill, random, staticFile, useCurrentFrame} from 'remotion';
import bp from './data/blueprint.json';
import layout from './data/poster_layout.json';
import {Key, keyed, table} from './lib/anim';
import {loadFontsStrict} from './lib/fontsStrict';

const C = (bp as any).calibration;
const T = (bp as any).templates;
const LY = (layout as any).items;
const W = 854, H = 480, CX = 427, CY = 240;
const INK = '#120400', RED = '#7a1a0a', BADGE = '#a22e16', OUTLINE = '#130b01';
const camT = (s: number, tx: number, ty: number) => `translate(${CX + tx} ${CY + ty}) scale(${s}) translate(${-CX} ${-CY})`;
const scaleAbout = (s: number, ax: number, ay: number) => `translate(${ax} ${ay}) scale(${s}) translate(${-ax} ${-ay})`;
const SUN = {x: 325, y: 289.5, r: 36.5, ring: 47};   // disc centre and radius re-measured on the reference at f030
// poster print content sits 1.6 ref px right of the paper's measured centre line (reference f075/f143, camera inverted)
const POSTER_DX = 1.6;

export type HQProps = {heroSrc?: string | null; posterPrintSrc?: string | null; showDebugGuides?: boolean};

// ---------- shared SVG defs ----------
const Defs: React.FC = () => (
  <defs>
    <filter id="ink" x="-3%" y="-10%" width="106%" height="120%" colorInterpolationFilters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={3} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={0.2} xChannelSelector="R" yChannelSelector="G" result="d" />
      <feTurbulence type="fractalNoise" baseFrequency="0.08" numOctaves={2} seed={4} result="dens" />
      <feColorMatrix in="dens" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.1 0 0 0 1.03" result="densA" />
      <feComposite in="d" in2="densA" operator="in" />
    </filter>
    <filter id="inkRed" x="-3%" y="-10%" width="106%" height="120%" colorInterpolationFilters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={5} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={0.24} xChannelSelector="R" yChannelSelector="G" result="d" />
      <feTurbulence type="fractalNoise" baseFrequency="0.1" numOctaves={2} seed={12} result="dens" />
      <feColorMatrix in="dens" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.14 0 0 0 1.04" result="densA" />
      <feComposite in="d" in2="densA" operator="in" />
    </filter>
    <filter id="paperShadow" x="-10%" y="-10%" width="125%" height="125%" colorInterpolationFilters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation={9} result="b1" />
      <feOffset in="b1" dx={3} dy={6} result="o1" />
      <feFlood floodColor="#140500" floodOpacity={0.3} result="c1" />
      <feComposite in="c1" in2="o1" operator="in" result="s1" />
      <feGaussianBlur in="SourceAlpha" stdDeviation={2.2} result="b2" />
      <feOffset in="b2" dx={5} dy={9} result="o2" />
      <feFlood floodColor="#120400" floodOpacity={0.8} result="c2" />
      <feComposite in="c2" in2="o2" operator="in" result="s2" />
      <feMerge><feMergeNode in="s1" /><feMergeNode in="s2" /><feMergeNode in="SourceGraphic" /></feMerge>
    </filter>
    <filter id="rayBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={5.5} /></filter>
    <filter id="soft1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={0.9} /></filter>
    <filter id="soft06" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={0.6} /></filter>
    <filter id="soft2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={2.2} /></filter>
    <filter id="printTone" colorInterpolationFilters="sRGB">
      {/* monochrome sepia print of a colour illustration: luminance -> duotone #2a160a..#d9b47a, +contrast */}
      <feColorMatrix type="matrix" values="0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0 0 0 1 0" />
      <feComponentTransfer>
        <feFuncR type="table" tableValues="0.165 0.85" />
        <feFuncG type="table" tableValues="0.086 0.706" />
        <feFuncB type="table" tableValues="0.039 0.478" />
      </feComponentTransfer>
    </filter>
    <radialGradient id="bloomTight" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#fff6d6" stopOpacity="0.95" /><stop offset="0.55" stopColor="#ffe3a0" stopOpacity="0.55" /><stop offset="1" stopColor="#ffc070" stopOpacity="0" /></radialGradient>
    <radialGradient id="bloomWide" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#ffd890" stopOpacity="0.55" /><stop offset="0.45" stopColor="#ffb868" stopOpacity="0.22" /><stop offset="1" stopColor="#ff9850" stopOpacity="0" /></radialGradient>
    <radialGradient id="rayFade" gradientUnits="userSpaceOnUse" cx={SUN.x} cy={SUN.y} r={520}>
      <stop offset="0" stopColor="#fff0c8" stopOpacity="0" /><stop offset="0.12" stopColor="#fff0c8" stopOpacity="0" /><stop offset="0.25" stopColor="#fff0c8" stopOpacity="0.5" /><stop offset="0.55" stopColor="#ffe6b8" stopOpacity="0.6" /><stop offset="1" stopColor="#ffe6b8" stopOpacity="0.3" />
    </radialGradient>
    <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#e8854a" stopOpacity="0" /><stop offset="0.55" stopColor="#e8854a" stopOpacity="0.38" /><stop offset="1" stopColor="#e8854a" stopOpacity="0" /></linearGradient>
    <radialGradient id="vigWall" gradientUnits="userSpaceOnUse" cx={427} cy={240} r={520}>
      <stop offset="0" stopColor="#000" stopOpacity="0" /><stop offset="0.45" stopColor="#000" stopOpacity="0.04" /><stop offset="0.7" stopColor="#120500" stopOpacity="0.2" /><stop offset="0.9" stopColor="#120500" stopOpacity="0.42" /><stop offset="1" stopColor="#0a0300" stopOpacity="0.6" />
    </radialGradient>
    <radialGradient id="vigSky" gradientUnits="userSpaceOnUse" cx={427} cy={250} r={600}>
      <stop offset="0" stopColor="#000" stopOpacity="0" /><stop offset="0.6" stopColor="#1a0610" stopOpacity="0.08" /><stop offset="1" stopColor="#1a0610" stopOpacity="0.42" />
    </radialGradient>
    <radialGradient id="warmPool" gradientUnits="userSpaceOnUse" cx={427} cy={230} r={360}><stop offset="0" stopColor="#ffb060" stopOpacity="0.1" /><stop offset="1" stopColor="#ffb060" stopOpacity="0" /></radialGradient>
    <radialGradient id="speck" cx="0.5" cy="0.5" r="0.5">{/* orb core; reference profile r1 0.75, r2 0.45, r3 0.15 (peak-normalised), plateau from the halo disc */}<stop offset="0" stopColor="#fffaea" stopOpacity="1" /><stop offset="0.3" stopColor="#fff6e0" stopOpacity="0.75" /><stop offset="0.57" stopColor="#fff0d0" stopOpacity="0.45" /><stop offset="0.86" stopColor="#ffe6bc" stopOpacity="0.15" /><stop offset="1" stopColor="#ffe0b0" stopOpacity="0" /></radialGradient>
    <radialGradient id="sunRing" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#ffc868" /><stop offset="0.95" stopColor="#ffc868" /><stop offset="1" stopColor="#ffc868" stopOpacity="0" /></radialGradient>
    <linearGradient id="mesaFace" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6a2a1a" /><stop offset="1" stopColor="#4c1710" /></linearGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7b4125" /><stop offset="0.5" stopColor="#5f2f18" /><stop offset="1" stopColor="#3a1a0a" /></linearGradient>
  </defs>
);

// ---------- particles ----------
const Dust: React.FC<{f: number; n: number; seed: string; box: number[]; rMin: number; rMax: number; dense?: number[]}> = ({f, n, seed, box, rMin, rMax, dense}) => (
  <g style={{mixBlendMode: 'screen'}}>
    {Array.from({length: n}).map((_, i) => {
      const r = (k: string) => random(`${seed}-${i}-${k}`);
      const bx = dense && r('d') < dense[4] ? dense : box;   // [x0, y0, x1, y1, share]: open sky left of the hero holds most orbs
      const x0 = bx[0] + r('x') * (bx[2] - bx[0]), y0 = bx[1] + r('y') * (bx[3] - bx[1]);
      const vx = (r('vx') - 0.35) * 0.18, vy = -(r('vy')) * 0.08;
      const fast = r('fast') > 0.88 ? 6 : 1;
      const x = x0 + vx * f * fast + Math.sin(f / (25 + r('p') * 40) + r('ph') * 6) * 0.8;
      const y = y0 + vy * f * fast + Math.cos(f / (30 + r('q') * 40) + r('ph2') * 6) * 0.6;
      const size = rMin + r('s') * (rMax - rMin);   // ref px radius of the halo
      const tw = 0.75 + 0.25 * Math.sin(f / (20 + r('t') * 50) * 2 + r('tp') * 6);
      const op = (0.35 + 0.65 * r('o')) * tw;
      return (
        <g key={i} opacity={op}>
          <circle cx={x} cy={y} r={size} fill="#ffe4bc" opacity={0.13} filter="url(#soft06)" />
          <circle cx={x} cy={y} r={size * 0.55} fill="url(#speck)" opacity={0.68} />   {/* peak +63..78 over the sky, as measured */}
        </g>
      );
    })}
  </g>
);

const Birds: React.FC<{f: number}> = ({f}) => {
  // [x, y, phase, scale, tilt deg, left-wing length, right-wing lift]: reference gulls are ~21 px wide at 480p, thin and uneven
  const birds = [[121, 147, 0, 1.05, -7, 0.85, 1.1], [139, 139, 1.7, 0.95, 6, 1.1, 0.9], [176, 143, 3.1, 1.12, -3, 1.0, 0.8]];
  return (
    <g fill="none" stroke="#3a1e22" strokeLinecap="round" strokeLinejoin="round">
      {birds.map(([x, y, ph, k, tilt, lw, rl], i) => {
        const fl = Math.sin(f * 2 * Math.PI * 2.5 / 30 + ph);
        const bx = x + f * 0.13, by = y + Math.sin(f / 20 + ph) * 0.6;
        const w = 9 * k, lift = (3.4 + fl * 2.4) * k;
        // each wing: a bold arched stroke, heavier at the body (reference gulls read as thick 'm' shapes)
        const wing = (dir: number) => { const ww = w * (dir < 0 ? lw : 1), ll = lift * (dir > 0 ? rl : 1); return `M${bx},${by} Q${bx + dir * ww * 0.4},${by - ll} ${bx + dir * ww},${by - ll * 0.3 + 1.2 * k}`; };
        const inner = (dir: number) => { const ww = w * (dir < 0 ? lw : 1), ll = lift * (dir > 0 ? rl : 1); return `M${bx},${by} Q${bx + dir * ww * 0.25},${by - ll * 0.7} ${bx + dir * ww * 0.5},${by - ll * 0.62}`; };
        return <g key={i} transform={`rotate(${tilt} ${bx} ${by})`}><path d={wing(-1)} strokeWidth={0.8 * k} /><path d={wing(1)} strokeWidth={0.8 * k} /><path d={inner(-1)} strokeWidth={1.2 * k} /><path d={inner(1)} strokeWidth={1.2 * k} /></g>;
      })}
    </g>
  );
};

// ---------- portrait background (code-built, original) ----------
const Tuft: React.FC<{x: number; y: number; s: number; seed: number}> = ({x, y, s, seed}) => {
  // a clump of thin tapered blades, dark olive at the root to pale yellow-green at the tips (reference grass)
  const n = 6 + Math.floor(random(`n${seed}`) * 5);
  const gid = `tuftG${seed}`;
  const blades = Array.from({length: n}).map((_, i) => {
    const u = i / (n - 1);
    const a = -0.62 + 1.24 * u + (random(`t${seed}-${i}`) - 0.5) * 0.45;
    const L = (11 + random(`l${seed}-${i}`) * 11) * s * (1 - 0.3 * Math.abs(u - 0.5));
    const bx = x + (u - 0.5) * 9 * s;
    const tx = bx + Math.sin(a) * L, ty = y - Math.cos(a) * L;
    const cx = bx + Math.sin(a) * L * 0.22, cy = y - Math.cos(a) * L * 0.68;
    const w = 0.55 * s;
    return `M${bx - w},${y} Q${cx - w * 0.45},${cy} ${tx},${ty} Q${cx + w * 0.45},${cy} ${bx + w},${y} Z`;
  });
  return (
    <g>
      <defs>
        <linearGradient id={gid} gradientUnits="userSpaceOnUse" x1={0} y1={y} x2={0} y2={y - 22 * s}>
          <stop offset="0" stopColor="#7a6e3a" /><stop offset="0.3" stopColor="#b8ac78" /><stop offset="0.7" stopColor="#d8cfa0" /><stop offset="1" stopColor="#f2ecd0" />
        </linearGradient>
      </defs>
      {blades.map((d, i) => <path key={i} d={d} fill={`url(#${gid})`} stroke="#3a3410" strokeOpacity={0.25} strokeWidth={0.3 * s} />)}
    </g>
  );
};

// grass clumps in depth: small and dim at the back, large and bright in front (reference layout + a few behind the future hero)
const TUFTS: number[][] = [
  [40, 380, 0.42], [178, 379, 0.4], [240, 390, 0.48], [350, 392, 0.45], [480, 385, 0.42], [600, 394, 0.5], [722, 382, 0.42], [800, 390, 0.45],
  [78, 400, 0.7], [150, 420, 0.9], [206, 428, 0.85], [262, 438, 1.05], [420, 422, 0.85], [690, 414, 0.8], [836, 426, 1.05],
  [8, 462, 1.35], [22, 478, 1.6], [34, 472, 1.55], [50, 482, 1.0], [66, 466, 1.3], [96, 476, 1.4], [168, 452, 1.15], [330, 446, 1.2], [418, 470, 1.5], [520, 454, 1.25], [612, 474, 1.55], [700, 450, 1.15], [762, 476, 1.45], [812, 458, 1.3],
];

const MESA_EDGE = 'M-5,277 L22,276.5 L40,275.5 L58,275 L74,275.5 L86,276.5 L100,277 L112,277 L121,278 L125,288 L123,298 L126,310 L126,322 L129,330 L134,338 L139,346 L144,354 L150,368';
const MESA = MESA_EDGE + ' L-5,368 Z';

const PortraitBackground: React.FC<{f: number}> = ({f}) => {
  // [angle deg, strength, half-width deg]: measured from the reference's polar brightness profile around the sun at f30
  const rays = [[76, 1.0, 4.0], [100, 1.0, 2.2], [123, 1.0, 2.1], [150, 0.12, 2.0], [57, 0.8, 2.6], [36, 0.6, 2.6]];
  const sway = (a: number, i: number) => a + 1.2 * (Math.sin((2 * Math.PI * (f - 30)) / 95 + i * 1.3) - Math.sin(i * 1.3));
  const ray = (a: number, w: number) => {
    const R = 900, r0 = SUN.ring;
    const p = (ang: number, rr: number) => `${SUN.x + rr * Math.cos((ang * Math.PI) / 180)},${SUN.y - rr * Math.sin((ang * Math.PI) / 180)}`;
    return `M${p(a - w * 0.3, r0)} L${p(a - w, R)} L${p(a + w, R)} L${p(a + w * 0.3, r0)} Z`;
  };
  // broad hill arcs meeting at x = 45, 163, 281, ... (troughs y 367, apexes ~355) over a straight dark ground line
  const arches = (y0: number) => {
    const step = 118; let d = `M-73,${y0}`;
    for (let x = -73; x < 900; x += step) d += ` Q${x + step / 2},${y0 - 24} ${x + step},${y0}`;   // quadratic apex = half the control offset: 12 px rise (reference)
    return d;
  };
  const bands = [[376, 5.5, '#8e4c2e', 0.58], [386, 6.5, '#4a2210', 0.54], [397, 5.5, '#94502e', 0.54], [409, 7.5, '#46200e', 0.54], [422, 6, '#8a4a2a', 0.5], [436, 8.5, '#42200c', 0.54], [452, 6.5, '#7e4224', 0.48], [468, 9.5, '#3c1c0a', 0.54]];
  return (
    <g>
      <defs>
        <linearGradient id="mtnLit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#84393a" /><stop offset="1" stopColor="#9c503c" /></linearGradient>
        <linearGradient id="mtnShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#70302e" /><stop offset="1" stopColor="#8c4836" /></linearGradient>
        <linearGradient id="farLit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#8e4844" /><stop offset="1" stopColor="#a8603e" /></linearGradient>
        <linearGradient id="farShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7c3c34" /><stop offset="1" stopColor="#985440" /></linearGradient>
        <linearGradient id="mesa2" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={78} y2={0}><stop offset="0" stopColor="#4a160e" /><stop offset="1" stopColor="#561c12" /></linearGradient>
        <linearGradient id="mesaGlow" gradientUnits="userSpaceOnUse" x1={0} y1={324} x2={0} y2={366}><stop offset="0" stopColor="#7a3a20" stopOpacity="0" /><stop offset="0.45" stopColor="#7a3a20" stopOpacity="0.55" /><stop offset="1" stopColor="#8a4424" stopOpacity="0.85" /></linearGradient>
        <linearGradient id="ground2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7e4228" /><stop offset="0.15" stopColor="#6e361e" /><stop offset="0.6" stopColor="#5c2c16" /><stop offset="1" stopColor="#4a220e" /></linearGradient>
        <linearGradient id="hills2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7a3a22" /><stop offset="1" stopColor="#70341e" /></linearGradient>
        <radialGradient id="hazeGlow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#ffb070" stopOpacity="0.5" /><stop offset="1" stopColor="#ff9a50" stopOpacity="0" /></radialGradient>
        <radialGradient id="tlDark" gradientUnits="userSpaceOnUse" cx={0} cy={0} r={330}><stop offset="0" stopColor="#14041a" stopOpacity="0.28" /><stop offset="1" stopColor="#14041a" stopOpacity="0" /></radialGradient>
        <filter id="softBand" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="1.2" /></filter>
        <filter id="softGround" x="-5%" y="-100%" width="110%" height="300%"><feGaussianBlur stdDeviation="1.6" /></filter>
        <filter id="glowBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" /></filter>
      </defs>
      {/* sky plate already contains the corner darkening, haze glow, halo disc and wide bloom (baked in float + dithered: no 8-bit rings) */}
      <image href={staticFile('hq/sky_portrait.png')} x={0} y={0} width={W} height={H} preserveAspectRatio="none" />
      <g style={{mixBlendMode: 'screen'}} filter="url(#rayBlur)">
        {rays.map(([a, op, w], i) => <path key={i} d={ray(sway(a, i), w)} fill="url(#rayFade)" opacity={op * 0.3} />)}
      </g>
      <circle cx={SUN.x} cy={SUN.y} r={SUN.ring + 3.5} fill="url(#sunRing)" />
      <circle cx={SUN.x} cy={SUN.y} r={SUN.r} fill="#feedc5" />
      <image href={staticFile('hq/sun_bloom.png')} x={0} y={0} width={W} height={H} preserveAspectRatio="none" style={{mixBlendMode: 'screen'}} />
      <Birds f={f} />
      {/* far range B and C: same burgundy family as A, big two-tone spiky snowcaps, bold clean outline */}
      <g>
        <path d="M330,372 L330,360 L352,312 L368,297 L382,280 L398,297 L414,305 L432,318 L452,330 L476,360 L476,372 Z" fill="url(#farShade)" />
        <path d="M330,372 L330,360 L352,312 L368,297 L382,280 L388,296 L381,312 L389,330 L384,360 L384,372 Z" fill="url(#farLit)" />
        <path d="M360,304.5 L368,297 L382,280 L398,297 L406,301 L397,314 L389,302 L381,316 L372,303 L364,312 Z" fill="#e6c4ba" />
        <path d="M382,280 L398,297 L406,301 L397,314 L389,302 L385,291 Z" fill="#bc9898" />
        <path d="M406,301 L397,314 L389,302 L381,316 L372,303 L364,312 L360,304.5" fill="none" stroke="#5a2a2c" strokeOpacity={0.55} strokeWidth={0.7} strokeLinejoin="round" />
        <path d="M330,360 L352,312 L368,297 L382,280 L398,297 L414,305 L432,318 L452,330 L476,360" fill="none" stroke={OUTLINE} strokeWidth={1.5} strokeLinejoin="round" />
        <path d="M640,372 L640,360 L668,316 L692,290 L717,260 L742,284 L766,306 L796,318 L830,324 L860,330 L860,360 L860,372 Z" fill="url(#farShade)" />
        <path d="M640,372 L640,360 L668,316 L692,290 L717,260 L724,280 L714,300 L726,326 L716,360 L716,372 Z" fill="url(#farLit)" />
        <path d="M686,296.5 L692,290 L717,260 L742,284 L752,293 L741,306 L731,290 L722,306 L712,291 L700,305 Z" fill="#e6c4ba" />
        <path d="M717,260 L742,284 L752,293 L741,306 L731,290 L724,276 Z" fill="#bc9898" />
        <path d="M752,293 L741,306 L731,290 L722,306 L712,291 L700,305 L686,296.5" fill="none" stroke="#5a2a2c" strokeOpacity={0.55} strokeWidth={0.7} strokeLinejoin="round" />
        <path d="M640,360 L668,316 L692,290 L717,260 L742,284 L766,306 L796,318 L830,324 L860,330" fill="none" stroke={OUTLINE} strokeWidth={1.5} strokeLinejoin="round" />
      </g>
      {/* mountain A: lit left face / shade right face, large two-tone snowcap with deep spikes */}
      <g>
        <path d="M92,372 L92,362 L104,282 L122,262 L141,238 L158,227 L162.5,221.5 L166,227 L178,239 L196,258 L216,268 L236,282 L243,300 L262,306 L283,326 L312,362 L312,372 Z" fill="url(#mtnShade)" />
        <path d="M92,372 L92,362 L104,282 L122,262 L141,238 L158,227 L162.5,221.5 L170,240 L168,256 L178,272 L170,290 L182,306 L175,324 L186,342 L180,362 L180,372 Z" fill="url(#mtnLit)" />
        <path d="M125,258 L141,238 L158,227 L162.5,221.5 L166,227 L178,239 L187,248.5 L172,275 L153,254 L136,275 Z" fill="#e6c2b8" />
        <path d="M162.5,221.5 L166,227 L178,239 L187,248.5 L172,275 L165,250 Z" fill="#bc9898" />
        <path d="M187,248.5 L172,275 L153,254 L136,275 L125,258" fill="none" stroke="#5a2a2c" strokeOpacity={0.55} strokeWidth={0.8} strokeLinejoin="round" />
        <path d="M168,256 L178,272 L170,290 L182,306 L175,324 L186,342" fill="none" stroke="#4a1c1c" strokeOpacity={0.35} strokeWidth={0.8} strokeLinejoin="round" />
        <path d="M92,362 L104,282 L122,262 L141,238 L158,227 L162.5,221.5 L166,227 L178,239 L196,258 L216,268 L236,282 L243,300 L262,306 L283,326 L312,362" fill="none" stroke={OUTLINE} strokeWidth={1.5} strokeLinejoin="round" />
      </g>
      {/* warm atmospheric haze, full width so no band ends inside the frame */}
      <rect x={-5} y={300} width={870} height={66} fill="url(#haze)" opacity={0.75} />
      <rect x={-5} y={326} width={870} height={40} fill="#ff9a50" opacity={0.16} filter="url(#glowBlur)" style={{mixBlendMode: 'screen'}} />
      {/* mesa: slightly bumpy flat top, stepped right face flaring out toward the base; soft strata and a faint plaid, clipped to the shape;
          jagged vertical form shadow on the right (reference) */}
      <g>
        <defs><clipPath id="mesaClip"><path d={MESA} /></clipPath></defs>
        <path d={MESA} fill="url(#mesa2)" />
        <g clipPath="url(#mesaClip)">
          {/* broad strata measured on the reference: light bands at y 294-299 and 313-326, dark between, warm glow toward the base */}
          <g filter="url(#softBand)">
            <rect x={-5} y={293.5} width={180} height={6.5} fill="#6c2a1a" opacity={0.65} />
            <rect x={-5} y={312.5} width={180} height={14} fill="#6c2a1a" opacity={0.65} />
            {[285, 304, 309].map((y, i) => <line key={i} x1={-5} x2={175} y1={y} y2={y} stroke="#3e120c" strokeOpacity={0.35} strokeWidth={1.6} />)}
          </g>
          <rect x={-5} y={324} width={180} height={46} fill="url(#mesaGlow)" />
          {Array.from({length: 18}).map((_, i) => { const x = 4 + i * 9 + (random(`mp${i}`) - 0.5) * 4; return <line key={'p' + i} x1={x} x2={x + (random(`mq${i}`) - 0.5) * 1.5} y1={270} y2={370} stroke="#2a0a06" strokeOpacity={0.08 + random(`mo${i}`) * 0.08} strokeWidth={0.8 + random(`mw${i}`) * 0.5} />; })}
          <path d="M78,268 L82,288 L76,302 L83,318 L79,334 L86,350 L84,372 L170,372 L170,268 Z" fill="#4c1812" opacity={0.78} />
          <path d="M78,276 L82,288 L76,302 L83,318 L79,334 L86,350 L84,368" fill="none" stroke="#1e0604" strokeOpacity={0.3} strokeWidth={0.8} />
        </g>
        <path d={MESA_EDGE} fill="none" stroke={OUTLINE} strokeWidth={1.3} strokeLinejoin="round" />
      </g>
      <ellipse cx={70} cy={352} rx={90} ry={18} fill="#f09048" opacity={0.25} filter="url(#glowBlur)" style={{mixBlendMode: 'screen'}} />
      {[[58, 343, 9], [106, 351, 7.5], [236, 347, 8.5], [560, 345, 9], [790, 350, 8]].map(([x, y, rr], i) => <ellipse key={'ob' + i} cx={x} cy={y} rx={rr * 1.9} ry={rr * 0.9} fill="#ff9a50" opacity={0.16} filter="url(#glowBlur)" style={{mixBlendMode: 'screen'}} />)}
      {/* hills and ground */}
      <path d={arches(367) + ' L900,385 L-73,385 Z'} fill="url(#hills2)" />
      <path d={arches(367)} fill="none" stroke="#e0a898" strokeWidth={1.2} strokeOpacity={0.72} />
      <rect x={-5} y={372} width={870} height={112} fill="url(#ground2)" />
      <line x1={-5} x2={860} y1={372} y2={372} stroke="#3a1408" strokeWidth={0.9} opacity={0.5} />
      <g filter="url(#softGround)">
        {bands.map(([y, h, c, o], i) => <path key={i} d={`M-5,${y} Q150,${(y as number) + 1.6} 330,${(y as number) - 0.8} T660,${(y as number) + 1.2} T880,${(y as number) - 0.6}`} stroke={c as string} strokeWidth={h as number} strokeOpacity={o as number} fill="none" />)}
      </g>
      {/* faint vertical striations across the ground bands (reference: smeared, brushy ground) */}
      <g filter="url(#soft06)">
        {Array.from({length: 90}).map((_, i) => {
          const x = random(`gs${i}`) * 864 - 5, y0 = 373 + random(`gy${i}`) * 30, dk = random(`gd${i}`) < 0.45;
          return <line key={'gs' + i} x1={x} x2={x + (random(`gx${i}`) - 0.5) * 2} y1={y0} y2={484} stroke={dk ? '#3a1808' : '#9a5a36'} strokeWidth={0.7 + random(`gw${i}`) * 0.8} strokeOpacity={0.05 + random(`go${i}`) * 0.1} />;
        })}
      </g>
      {TUFTS.map(([x, y, s], i) => <g key={i} opacity={Math.min(1, 0.65 + s * 0.35)} filter={s < 0.6 ? 'url(#soft06)' : undefined}><Tuft x={x} y={y} s={s} seed={i} /></g>)}
      <image href={staticFile('hq/vig_sky.png')} x={0} y={0} width={W} height={H} preserveAspectRatio="none" />
      <Dust f={f} n={24} seed="sky" box={[0, 0, 854, 250]} rMin={3.6} rMax={7.0} dense={[0, 30, 360, 230, 0.45]} />
      <Dust f={f} n={10} seed="land" box={[0, 270, 854, 470]} rMin={4.5} rMax={6.0} dense={[0, 272, 250, 360, 0.4]} />
    </g>
  );
};

// ---------- hero title (timing from template) ----------
const HeroTitle: React.FC<{e: any; f: number}> = ({e, f}) => {
  const tpl = T.hero_title.anim_in;
  const fs = e.cap_px / 0.637;
  const finalTrack = 0.15 * fs;
  return (
    <g>
      {e.lines.map((txt: string, i: number) => {
        const t = f - (e.start + i * tpl.line_stagger_frames);
        if (t < 0) return null;
        const op = Math.min(1, (t + 1) / tpl.line_opacity_frames);
        const tr = Math.min(1, Math.max(0, (t - 1) / tpl.tracking.duration_frames));
        const extra = tpl.tracking.extra_px_per_gap_ref_start * (1 - (1 - Math.pow(1 - tr, 3)));
        return (
          <text key={i} x={e.left_px + 98.5} y={e.baselines_px[i]} textAnchor="middle" fontFamily="Alegreya" fontWeight={800} fontSize={fs} letterSpacing={finalTrack + extra}
            fill="#ecdcc2" stroke="#3f1f0e" strokeWidth={1.4} paintOrder="stroke" opacity={op} style={{filter: 'drop-shadow(0.5px 1.4px 1.2px rgba(20,5,0,0.6))'}}>{txt}</text>
        );
      })}
      {(() => {
        const rs = e.start + tpl.rule.start_offset; const rp = f >= rs ? table(tpl.rule.draw_from_centre_keyframes, f - rs) : 0;
        const rc = (e.rule_x_px[0] + e.rule_x_px[1]) / 2, rh = (e.rule_x_px[1] - e.rule_x_px[0]) / 2;
        const ss = e.start + tpl.subline.start_offset; const sop = f >= ss ? Math.min(1, (f - ss + 1) / tpl.subline.fade_frames) : 0;
        return (
          <g>
            {rp > 0 && <line x1={rc - rh * rp} x2={rc + rh * rp} y1={e.rule_y_px} y2={e.rule_y_px} stroke="#d0ab80" strokeWidth={0.9} style={{filter: 'drop-shadow(0px 0.8px 0.6px rgba(20,5,0,0.5))'}} />}
            {f >= e.start + 11 && <rect x={rc - 2.6} y={e.rule_y_px - 2.6} width={5.2} height={5.2} transform={`rotate(45 ${rc} ${e.rule_y_px})`} fill="#e3c08f" stroke="#3f1f0e" strokeWidth={0.6} opacity={Math.min(1, (f - e.start - 10) / 3)} />}
            {sop > 0 && <text x={e.subline_center_x_px} y={e.subline_baseline_px} textAnchor="middle" fontFamily="Alegreya" fontStyle="italic" fontWeight={700} fontSize={e.subline_cap_px / 0.636} fill="#d4b896" opacity={sop} style={{filter: 'drop-shadow(0px 0.8px 0.8px rgba(20,5,0,0.6))'}}>{e.subline}</text>}
          </g>
        );
      })()}
    </g>
  );
};

// ---------- poster pieces ----------
const PText: React.FC<{k: string; y: number; fill?: string; filter?: string; dx?: number; opacity?: number}> = ({k, y, fill = INK, filter = 'url(#ink)', dx = 0, opacity = 1}) => {
  const L = LY[k];
  return (
    <text x={(L.align === 'centre' ? L.x : L.left) + dx} y={y} textAnchor={L.align === 'centre' ? 'middle' : 'start'} fontFamily="Bitter" fontWeight={900}
      fontSize={L.font_size_ref} letterSpacing={`${L.tracking_em}em`} fill={fill} filter={filter} opacity={opacity}>{L.text}</text>
  );
};

const Pictogram: React.FC<{kind: string}> = ({kind}) => {
  // drawn on a 100x100 grid, filled red silhouettes with paper-colour knock-outs (style_bible §9)
  const P = '#f2c48a';
  if (kind === 'train')
    return (
      <g>
        <path d="M6,72 L19,55 L19,74 Z" fill={BADGE} />
        <rect x={19} y={43} width={45} height={24} rx={10} fill={BADGE} />
        <path d="M24,43 L22,28 L16,20 L38,20 L32,28 L30,43 Z" fill={BADGE} />
        <circle cx={47} cy={42} r={6} fill={BADGE} />
        <rect x={62} y={30} width={24} height={37} fill={BADGE} />
        <rect x={57} y={25} width={33} height={7} rx={1.5} fill={BADGE} />
        <rect x={67} y={36} width={13} height={12} fill={P} />
        <rect x={14} y={64} width={74} height={7} fill={BADGE} />
        {[[31, 78, 10], [54, 78, 10], [77, 79, 8]].map(([x, y, r], i) => (
          <g key={i}><circle cx={x} cy={y} r={r + 1} fill={BADGE} /><circle cx={x} cy={y} r={r * 0.3} fill={P} /></g>
        ))}
      </g>
    );
  if (kind === 'moneybag')
    return (
      <g>
        <path d="M37,30 C33,24 34,15 41,14 L44,20 L50,12 L56,20 L59,14 C66,15 67,24 63,30 Z" fill={BADGE} />
        <path d="M36,34 C22,44 14,58 16,72 C18,86 32,92 50,92 C68,92 82,86 84,72 C86,58 78,44 64,34 Z" fill={BADGE} />
        <rect x={35} y={29} width={30} height={6} rx={3} fill={BADGE} />
        <path d="M36,32 L64,32" stroke={P} strokeWidth={2.2} strokeLinecap="round" />
        <text x={50} y={78} textAnchor="middle" fontFamily="Bitter" fontWeight={800} fontSize={36} fill={P}>$</text>
      </g>
    );
  return (
    <g fill="none" stroke={BADGE} strokeLinejoin="round">
      <path d="M10,26 L37,18 L63,26 L90,18 L90,78 L63,86 L37,78 L10,86 Z" fill="#f2c48a" strokeWidth={6} />
      <path d="M37,18 L37,78 M63,26 L63,86" strokeWidth={4} />
      <path d="M20,70 C30,62 34,56 44,56 C56,56 56,44 66,42 C72,40 74,36 76,34" strokeWidth={3.2} strokeDasharray="4 4" strokeLinecap="round" />
      <path d="M72,28 L82,38 M82,28 L72,38" strokeWidth={4.5} strokeLinecap="round" />
    </g>
  );
};

const Badge: React.FC<{x: number; y: number; kind: string; s: number; op: number}> = ({x, y, kind, s, op}) => (
  <g transform={scaleAbout(s, x, y)} opacity={op} filter="url(#inkRed)">
    <circle cx={x} cy={y} r={16.0} fill="#f2c890" fillOpacity={0.5} stroke={BADGE} strokeWidth={2.4} />
    <circle cx={x} cy={y} r={12.3} fill="none" stroke={BADGE} strokeWidth={1.0} />
    <g transform={`translate(${x - 10.5} ${y - 10.5}) scale(0.21)`}><Pictogram kind={kind} /></g>
  </g>
);

const MainPoster: React.FC<{f: number; shot: any; printSrc?: string | null}> = ({f, shot, printSrc}) => {
  const poster = shot.poster;
  const items = shot.elements.filter((e: any) => e.template === 'list_item_stamped_icon');
  const reward = shot.elements.find((e: any) => e.template === 'counter_suffix');
  let rv = reward.text_sequence[0][1];
  for (const [fr, s] of reward.text_sequence) if (f >= fr) rv = s;
  const tpl = T.list_item_stamped_icon.anim_in;
  const wf = LY.WANTED_FOR;
  return (
    <g>
      <image href={staticFile('hq/paper_main.png')} x={278 - 6.67} y={22 - 6.67} width={315.3} height={446.8} preserveAspectRatio="none" filter="url(#paperShadow)" />
      {/* nail */}
      <circle cx={429.4} cy={32} r={5.8} fill="#1a0a04" opacity={0.4} filter="url(#soft1)" />
      <circle cx={428} cy={30} r={6.1} fill="none" stroke="#f6e2b0" strokeWidth={1.0} opacity={0.45} />
      <circle cx={428} cy={30} r={5.0} fill="#3e3846" stroke="#141016" strokeWidth={1.4} />
      <circle cx={426.5} cy={28.5} r={1.7} fill="#c0b8c8" opacity={0.65} filter="url(#soft06)" />
      <g transform={`translate(${POSTER_DX} 0)`}>
      <g filter="url(#ink)">
        {/* frame lines at world x 296.6 / 301.8 / 558.2 / 563.5 (measured), written in content-local x */}
        <path d="M344,440 L295,440 L295,38 L561.9,38 L561.9,440 L526,440" fill="none" stroke={INK} strokeWidth={2} />
        <path d="M344,434 L300.2,434 L300.2,43 L556.6,43 L556.6,434 L526,434" fill="none" stroke={INK} strokeWidth={1} />
        <line x1={318} x2={538} y1={95.5} y2={95.5} stroke={INK} strokeWidth={1.5} />
        <rect x={328} y={98} width={200} height={134} fill="none" stroke={INK} strokeWidth={1.5} />
        <line x1={318} x2={wf.left - 0.6 * wf.font_size_ref} y1={277} y2={277} stroke={INK} strokeWidth={1} />
        <line x1={wf.right + 0.6 * wf.font_size_ref} x2={540} y1={277} y2={277} stroke={INK} strokeWidth={1} />
        <line x1={318} x2={540} y1={417} y2={417} stroke="#3a2410" strokeWidth={0.9} />
      </g>
      {[323, 360.3, 397.6].map((y) => <line key={y} x1={357} x2={539} y1={y} y2={y} stroke="#8a6838" strokeWidth={0.9} strokeDasharray="2.4 3.0" opacity={0.66} />)}
      {printSrc ? (
        <g style={{mixBlendMode: 'multiply'}}><image href={printSrc} x={329} y={99} width={198} height={132} preserveAspectRatio="xMidYMax slice" filter="url(#printTone)" /></g>
      ) : null}
      <PText k="WANTED" y={87.5} />
      <PText k="NAME" y={261.5} />
      <PText k="WANTED_FOR" y={280.3} />
      <text x={LY.REWARD.left} y={441} fontFamily="Bitter" fontWeight={800} fontSize={LY.REWARD.font_size_ref} letterSpacing={`${LY.REWARD.tracking_em}em`} fill="#2e1004" filter="url(#ink)">{LY.REWARD.text}</text>
      {items.map((e: any, i: number) => {
        const t = f - e.start;
        if (t < 0) return null;
        const y = poster.rows_center_y_px[e.row];
        const op = table(tpl.text_opacity_keyframes, t);
        const it = t - tpl.icon_start_offset;
        const fr = tpl.icon_keyframes.frames;
        const sc = it >= 0 ? table(fr.map((x: number, j: number) => [x, tpl.icon_keyframes.scale[j]]), it) : 0;
        const io = it >= 0 ? table(fr.map((x: number, j: number) => [x, tpl.icon_keyframes.opacity[j]]), it) : 0;
        return (
          <g key={i}>
            <PText k={`ITEM${e.row}`} y={y + LY[`ITEM${e.row}`].cap_ref / 2} opacity={op} />
            {it >= 0 && <Badge x={poster.icon_center_x_px - 1.1} y={y - 2.2} kind={e.icon} s={sc} op={io} />}
          </g>
        );
      })}
      {/* reference: a narrow '$', an 8 px gap, then the question marks; ends at x 519, 7 px clear of the frame break at 526 */}
      <g filter="url(#inkRed)" fill={RED}>
        <text transform={`translate(${LY.VALUE.left + 0.5} 446) scale(0.8 1)`} fontFamily="Bitter" fontWeight={900} fontSize={LY.VALUE.font_size_ref * 0.95}>$</text>
        <text x={464} y={446} fontFamily="Bitter" fontWeight={900} fontSize={LY.VALUE.font_size_ref * 0.95} letterSpacing="0.03em">{rv.slice(1)}</text>
      </g>
      </g>
    </g>
  );
};

// plank seams: crisp vectors in world px (period 66.7, phase matched to the plate's planks). Reference cross-section at f075/f143:
// ~1.5 px dark core, then a soft light lip ~4.5 px wide peaking ~+15/255; vector strokes keep that profile at any camera zoom.
const WallSeams: React.FC = () => (
  <g>
    <defs>
      <linearGradient id="seamLip" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#c47444" stopOpacity="0.05" /><stop offset="0.38" stopColor="#c47444" stopOpacity="0.36" />
        <stop offset="0.62" stopColor="#c47444" stopOpacity="0.3" /><stop offset="1" stopColor="#c47444" stopOpacity="0" />
      </linearGradient>
    </defs>
    {Array.from({length: 26}).map((_, k) => {
      const x = -421.9 + k * 66.7;
      return (
        <g key={k}>
          <rect x={x - 1.0} y={-240} width={1.2} height={960} fill="#c47444" opacity={0.22} />
          <rect x={x + 1.85} y={-240} width={5.2} height={960} fill="url(#seamLip)" />
          <rect x={x + 0.2} y={-240} width={1.7} height={960} fill="#30120a" opacity={0.68} />
        </g>
      );
    })}
  </g>
);

const SidePoster: React.FC<{cx: number; top: number; tex: number; op: number; faded?: boolean; printSrc?: string | null}> = ({cx, top, tex, op, faded, printSrc}) => (
  <g opacity={op}>
    <image href={staticFile(`hq/paper_side_${tex}.png`)} x={cx - 106.65} y={top - 6.67} width={213.3} height={293.3} preserveAspectRatio="none" filter="url(#paperShadow)" />
    <g transform={`translate(${cx} 0)`} filter="url(#ink)">
      <rect x={-92} y={top + 10} width={184} height={262} fill="none" stroke={INK} strokeWidth={1.6} />
      <text x={0} y={top + 40} textAnchor="middle" fontFamily="Bitter" fontWeight={900} fontSize={LY.SIDE_WANTED.font_size_ref} letterSpacing="0.06em" fill={INK}>WANTED</text>
      <text x={0} y={top + 51} textAnchor="middle" fontFamily="Bitter" fontWeight={800} fontSize={LY.SIDE_DOA.font_size_ref} letterSpacing="0.25em" fill={INK}>DEAD OR ALIVE</text>
      <rect x={-70} y={top + 57} width={140} height={118} fill="none" stroke={INK} strokeWidth={1.2} />
      <text x={0} y={top + 196} textAnchor="middle" fontFamily="Bitter" fontWeight={900} fontSize={LY.SIDE_NAME.font_size_ref} letterSpacing="0.01em" fill={INK}>ARTHUR MORGAN</text>
      <text x={0} y={top + 211} textAnchor="middle" fontFamily="Bitter" fontWeight={800} fontSize={LY.SIDE_REWARD.font_size_ref} letterSpacing="0.3em" fill={INK}>REWARD</text>
    </g>
    {printSrc ? <g style={{mixBlendMode: 'multiply'}}><image href={printSrc} x={cx - 69} y={top + 58} width={138} height={116} preserveAspectRatio="xMidYMax slice" filter="url(#printTone)" /></g> : null}
    <text x={cx} y={top + 232} textAnchor="middle" fontFamily="Bitter" fontWeight={900} fontSize={LY.SIDE_VALUE.font_size_ref} fill={RED} filter="url(#inkRed)">$?</text>
    {faded && <rect x={cx - 106} y={top - 6} width={212} height={292} fill="#3a1606" opacity={0.42} style={{mixBlendMode: 'multiply'}} />}
  </g>
);

export const CalibrationHQ: React.FC<HQProps> = ({heroSrc = null, posterPrintSrc = null}) => {
  loadFontsStrict();
  const f = useCurrentFrame();
  const shot = C.shots.find((s: any) => f >= s.start && f <= s.end) ?? C.shots[C.shots.length - 1];
  let content: React.ReactNode = null;
  if (shot.id === 's0') {
    const bg = shot.layers[0], hero = shot.layers[1];
    content = (
      <>
        <g transform={scaleAbout(keyed(bg.keys as Key[], 's', f, 1), bg.anchor[0], bg.anchor[1])}><PortraitBackground f={f} /></g>
        {heroSrc ? (
          <g transform={scaleAbout(keyed(hero.keys as Key[], 's', f, 1), hero.anchor[0], hero.anchor[1])}>
            <image href={heroSrc} x={hero.box[0]} y={hero.box[1]} width={hero.box[2] - hero.box[0]} height={hero.box[3] - hero.box[1]} preserveAspectRatio="xMidYMax meet" />
          </g>
        ) : null}
        {shot.elements.map((e: any, i: number) => (e.template === 'hero_title' ? <HeroTitle key={i} e={e} f={f} /> : null))}
      </>
    );
  } else {
    const cam = shot.camera as Key[];
    const s = keyed(cam, 's', f, 1), tx = keyed(cam, 'tx', f, 0), ty = keyed(cam, 'ty', f, 0);
    const wall = shot.elements.find((e: any) => e.template === 'poster_wall_reveal');
    const sideOp = (i: number) => (wall ? Math.max(0, Math.min(1, (f - (wall.start + i * wall.stagger_frames) + 1) / wall.fade_frames)) : 0);
    content = (
      <>
        <g transform={`translate(${CX + tx} ${CY + ty}) scale(${s}) translate(${-CX} ${-CY})`}>
          <image href={staticFile('hq/wall.png')} x={-427} y={-240} width={1708} height={960} preserveAspectRatio="none" />
          <WallSeams />
          <SidePoster cx={149} top={-48} tex={0} op={sideOp(0)} printSrc={posterPrintSrc} />
          <SidePoster cx={154} top={252} tex={1} op={sideOp(1)} printSrc={posterPrintSrc} />
          <SidePoster cx={708} top={-48} tex={2} op={sideOp(2)} printSrc={posterPrintSrc} />
          <SidePoster cx={708} top={238} tex={3} op={sideOp(3)} faded printSrc={posterPrintSrc} />
        </g>
        {/* screen-space wall vignette, fitted to the reference wall (elliptical, centred left of the poster); it sits under the main
            poster because the reference's poster keeps its own lit-centre/burn look (baked in float + dithered: no 8-bit bands) */}
        <image href={staticFile('hq/vig_wall.png')} x={0} y={0} width={W} height={H} preserveAspectRatio="none" />
        <g transform={`translate(${CX + tx} ${CY + ty}) scale(${s}) translate(${-CX} ${-CY})`}>
          <MainPoster f={f} shot={shot} printSrc={posterPrintSrc} />
        </g>
        <image href={staticFile('hq/warm_pool.png')} x={0} y={0} width={W} height={H} preserveAspectRatio="none" style={{mixBlendMode: 'screen'}} />
        <Dust f={f} n={34} seed="wall" box={[0, 0, 854, 480]} rMin={4.0} rMax={5.8} />
      </>
    );
  }
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" preserveAspectRatio="none">
        <Defs />
        {content}
        {/* final dither: zero-mean +-1.5-level noise under 'overlay' so no 8-bit gradient step survives as a band (style bible: grain <= 1%) */}
        <defs>
          <pattern id="ditherPat" patternUnits="userSpaceOnUse" width={1024 / 4.5} height={1024 / 4.5}>
            <image href={staticFile('hq/dither_tile.png')} width={1024 / 4.5} height={1024 / 4.5} style={{imageRendering: 'pixelated'}} />
          </pattern>
        </defs>
        <rect x={0} y={0} width={W} height={H} fill="url(#ditherPat)" style={{mixBlendMode: 'overlay'}} />
      </svg>
    </AbsoluteFill>
  );
};
