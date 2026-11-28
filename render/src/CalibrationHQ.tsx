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
const INK = '#140600', RED = '#8e2216', BADGE = '#9a2a14', OUTLINE = '#130b01';
const camT = (s: number, tx: number, ty: number) => `translate(${CX + tx} ${CY + ty}) scale(${s}) translate(${-CX} ${-CY})`;
const scaleAbout = (s: number, ax: number, ay: number) => `translate(${ax} ${ay}) scale(${s}) translate(${-ax} ${-ay})`;
const SUN = {x: 325, y: 286, r: 37, ring: 47};

export type HQProps = {heroSrc?: string | null; posterPrintSrc?: string | null; showDebugGuides?: boolean};

// ---------- shared SVG defs ----------
const Defs: React.FC = () => (
  <defs>
    <filter id="ink" x="-3%" y="-10%" width="106%" height="120%" colorInterpolationFilters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={3} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={0.22} xChannelSelector="R" yChannelSelector="G" result="d" />
      <feTurbulence type="fractalNoise" baseFrequency="1.7" numOctaves={1} seed={9} result="w" />
      <feColorMatrix in="w" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -14 0 0 0 11.2" result="wa" />
      <feComposite in="d" in2="wa" operator="in" result="k" />
      <feTurbulence type="fractalNoise" baseFrequency="0.08" numOctaves={2} seed={4} result="dens" />
      <feColorMatrix in="dens" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.08 0 0 0 1.06" result="densA" />
      <feComposite in="k" in2="densA" operator="in" result="k2" />
      <feGaussianBlur in="k2" stdDeviation="0.35" result="kb" />
      <feMerge><feMergeNode in="kb" /><feMergeNode in="k2" /></feMerge>
    </filter>
    <filter id="inkRed" x="-3%" y="-10%" width="106%" height="120%" colorInterpolationFilters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={5} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={0.28} xChannelSelector="R" yChannelSelector="G" result="d" />
      <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves={2} seed={11} result="w" />
      <feColorMatrix in="w" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -14 0 0 0 10.6" result="wa" />
      <feComposite in="d" in2="wa" operator="in" result="r1" />
      <feGaussianBlur in="r1" stdDeviation="0.3" />
    </filter>
    <filter id="paperShadow" x="-10%" y="-10%" width="120%" height="125%" colorInterpolationFilters="sRGB">
      <feDropShadow dx={4} dy={7} stdDeviation={4.5} floodColor="#1a0802" floodOpacity={0.85} />
    </filter>
    <filter id="rayBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={5} /></filter>
    <filter id="soft1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={0.9} /></filter>
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
      <stop offset="0" stopColor="#fff0c8" stopOpacity="0" /><stop offset="0.16" stopColor="#fff0c8" stopOpacity="0.55" /><stop offset="0.38" stopColor="#ffe6b8" stopOpacity="0.5" /><stop offset="1" stopColor="#ffe6b8" stopOpacity="0" />
    </radialGradient>
    <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#f6a655" stopOpacity="0" /><stop offset="0.55" stopColor="#f39d50" stopOpacity="0.38" /><stop offset="1" stopColor="#f39d50" stopOpacity="0" /></linearGradient>
    <radialGradient id="vigWall" gradientUnits="userSpaceOnUse" cx={450} cy={228} r={520}>
      <stop offset="0" stopColor="#000" stopOpacity="0" /><stop offset="0.38" stopColor="#000" stopOpacity="0.04" /><stop offset="0.6" stopColor="#120500" stopOpacity="0.25" /><stop offset="0.85" stopColor="#120500" stopOpacity="0.58" /><stop offset="1" stopColor="#0a0300" stopOpacity="0.8" />
    </radialGradient>
    <radialGradient id="vigSky" gradientUnits="userSpaceOnUse" cx={427} cy={250} r={600}>
      <stop offset="0" stopColor="#000" stopOpacity="0" /><stop offset="0.6" stopColor="#1a0610" stopOpacity="0.08" /><stop offset="1" stopColor="#1a0610" stopOpacity="0.42" />
    </radialGradient>
    <radialGradient id="warmPool" gradientUnits="userSpaceOnUse" cx={470} cy={220} r={340}><stop offset="0" stopColor="#ffb060" stopOpacity="0.26" /><stop offset="1" stopColor="#ffb060" stopOpacity="0" /></radialGradient>
    <radialGradient id="speck" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#fffaea" stopOpacity="1" /><stop offset="0.18" stopColor="#fff3d8" stopOpacity="0.95" /><stop offset="0.42" stopColor="#ffe6bc" stopOpacity="0.32" /><stop offset="1" stopColor="#ffd8a0" stopOpacity="0" /></radialGradient>
    <linearGradient id="mesaFace" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6a2a1a" /><stop offset="1" stopColor="#4c1710" /></linearGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7b4125" /><stop offset="0.5" stopColor="#5f2f18" /><stop offset="1" stopColor="#3a1a0a" /></linearGradient>
  </defs>
);

// ---------- particles ----------
const Dust: React.FC<{f: number; n: number; seed: string; box: number[]; scale?: number}> = ({f, n, seed, box, scale = 1}) => (
  <g style={{mixBlendMode: 'screen'}}>
    {Array.from({length: n}).map((_, i) => {
      const r = (k: string) => random(`${seed}-${i}-${k}`);
      const x0 = box[0] + r('x') * (box[2] - box[0]), y0 = box[1] + r('y') * (box[3] - box[1]);
      const vx = (r('vx') - 0.35) * 0.18, vy = -(r('vy')) * 0.08;
      const fast = r('fast') > 0.88 ? 6 : 1;
      const x = x0 + vx * f * fast + Math.sin(f / (25 + r('p') * 40) + r('ph') * 6) * 0.8;
      const y = y0 + vy * f * fast + Math.cos(f / (30 + r('q') * 40) + r('ph2') * 6) * 0.6;
      const size = (0.7 + Math.pow(r('s'), 2.2) * 2.6) * scale;   // ref px radius of the halo; skewed so a few are large
      const tw = 0.55 + 0.45 * Math.sin(f / (20 + r('t') * 50) * 2 + r('tp') * 6);
      const op = (0.35 + 0.65 * r('o')) * tw;
      return <circle key={i} cx={x} cy={y} r={size} fill="url(#speck)" opacity={op} filter={r('b') > 0.6 ? 'url(#soft1)' : undefined} />;
    })}
  </g>
);

const Birds: React.FC<{f: number}> = ({f}) => {
  const birds = [[121, 147, 0, 1.35], [139, 139, 1.7, 1.2], [176, 143, 3.1, 1.45]];
  return (
    <g fill="#3a1e24">
      {birds.map(([x, y, ph, k], i) => {
        const fl = Math.sin(f * 2 * Math.PI * 2.5 / 30 + ph);
        const bx = x + f * 0.13, by = y + Math.sin(f / 20 + ph) * 0.6;
        const w = 9 * k, lift = (3.4 + fl * 2.4) * k;
        // each wing: a tapered crescent (thick at the body, thin at the tip)
        const wing = (dir: number) => `M${bx},${by} Q${bx + dir * w * 0.45},${by - lift} ${bx + dir * w},${by - lift * 0.35 + 1.2 * k} Q${bx + dir * w * 0.5},${by - lift * 0.55} ${bx},${by + 1.3 * k} Z`;
        return <g key={i}><path d={wing(-1)} /><path d={wing(1)} /></g>;
      })}
    </g>
  );
};

// ---------- portrait background (code-built, original) ----------
const Mountain: React.FC<{d: string; lit: string; ridge: string; snowLit: string; snowShade: string; fillLit: string; fillShade: string; sw?: number}> = (p) => (
  <g>
    <path d={p.d} fill={p.fillShade} />
    <path d={p.lit} fill={p.fillLit} />
    <path d={p.snowShade} fill="#bc938e" />
    <path d={p.snowLit} fill="#e4bdb4" />
    <path d={p.ridge} fill="none" stroke="#3c1410" strokeOpacity={0.55} strokeWidth={0.9} strokeLinecap="round" />
    <path d={p.snowShade} fill="none" stroke={OUTLINE} strokeWidth={1.1} strokeLinejoin="round" />
    <path d={p.d} fill="none" stroke={OUTLINE} strokeWidth={p.sw ?? 2} strokeLinejoin="round" />
  </g>
);

const Tuft: React.FC<{x: number; y: number; s: number; seed: number}> = ({x, y, s, seed}) => {
  const blades = Array.from({length: 7}).map((_, i) => {
    const a = (-0.9 + 1.8 * (i / 6)) + (random(`t${seed}${i}`) - 0.5) * 0.25;
    const L = (9 + random(`l${seed}${i}`) * 8) * s;
    const tx = x + Math.sin(a) * L, ty = y - Math.cos(a) * L;
    const cx = x + Math.sin(a) * L * 0.35, cy = y - Math.cos(a) * L * 0.6;
    return `M${x + (i - 3) * 0.8 * s},${y} Q${cx},${cy} ${tx},${ty}`;
  });
  return (
    <g strokeLinecap="round" fill="none">
      {blades.map((d, i) => <path key={'o' + i} d={d} stroke="#4a3a14" strokeOpacity={0.25} strokeWidth={1.5 * s} />)}
      {blades.map((d, i) => <path key={'f' + i} d={d} stroke={i % 2 ? '#a8a24e' : '#bcb45c'} strokeWidth={1.0 * s} />)}
      {blades.map((d, i) => <path key={'h' + i} d={d} stroke="#e8e090" strokeWidth={0.55 * s} strokeDasharray={`0 ${10 * s} ${5 * s}`} />)}
    </g>
  );
};

const PortraitBackground: React.FC<{f: number}> = ({f}) => {
  const rays = [[102, 1.0, 3.6], [128, 1.0, 3.4], [170, 0.85, 3.2], [114, 0.35, 2.4], [150, 0.3, 2.6]];
  const sway = (a: number, i: number) => a + 1.5 * Math.sin((2 * Math.PI * f) / 95 + i * 1.3);
  const ray = (a: number, w: number) => {
    const R = 900, r0 = SUN.ring;
    const p = (ang: number, rr: number) => `${SUN.x + rr * Math.cos((ang * Math.PI) / 180)},${SUN.y - rr * Math.sin((ang * Math.PI) / 180)}`;
    return `M${p(a - w * 0.3, r0)} L${p(a - w, R)} L${p(a + w, R)} L${p(a + w * 0.3, r0)} Z`;
  };
  const arches = (y0: number) => {
    let d = `M-5,${y0}`; const step = 46;
    for (let x = -5; x < 870; x += step) d += ` Q${x + step / 2},${y0 - 9} ${x + step},${y0}`;
    return d;
  };
  return (
    <g>
      <defs>
        <linearGradient id="mtnLit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#9a5658" /><stop offset="1" stopColor="#b26c5e" /></linearGradient>
        <linearGradient id="mtnShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6e3a44" /><stop offset="1" stopColor="#8e5250" /></linearGradient>
        <linearGradient id="farLit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#a06266" /><stop offset="1" stopColor="#c07a6a" /></linearGradient>
        <linearGradient id="farShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7c4450" /><stop offset="1" stopColor="#a86a64" /></linearGradient>
        <linearGradient id="mesa2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#5c1e18" /><stop offset="1" stopColor="#481410" /></linearGradient>
        <linearGradient id="ground2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#8a4a2e" /><stop offset="0.15" stopColor="#74391f" /><stop offset="0.6" stopColor="#5e2c16" /><stop offset="1" stopColor="#46200c" /></linearGradient>
        <linearGradient id="hills2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7e3c2c" /><stop offset="1" stopColor="#6e3222" /></linearGradient>
        <radialGradient id="hazeGlow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#ffb070" stopOpacity="0.5" /><stop offset="1" stopColor="#ff9a50" stopOpacity="0" /></radialGradient>
        <radialGradient id="tlDark" gradientUnits="userSpaceOnUse" cx={0} cy={0} r={330}><stop offset="0" stopColor="#14041a" stopOpacity="0.28" /><stop offset="1" stopColor="#14041a" stopOpacity="0" /></radialGradient>
        <filter id="softBand" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="1.2" /></filter>
        <filter id="wobble" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves={2} seed={21} result="n" /><feDisplacementMap in="SourceGraphic" in2="n" scale={1.1} xChannelSelector="R" yChannelSelector="G" /></filter>
        <filter id="glowBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" /></filter>
      </defs>
      <image href={staticFile('hq/sky_portrait.png')} x={0} y={0} width={W} height={H} preserveAspectRatio="none" />
      <rect x={0} y={0} width={W} height={H} fill="url(#tlDark)" />
      <g style={{mixBlendMode: 'screen'}} filter="url(#rayBlur)">
        {rays.map(([a, op, w], i) => <path key={i} d={ray(sway(a, i), w)} fill="url(#rayFade)" opacity={op * 0.3} />)}
      </g>
      <circle cx={360} cy={300} r={230} fill="url(#hazeGlow)" style={{mixBlendMode: 'screen'}} opacity={0.8} />
      <circle cx={SUN.x} cy={SUN.y} r={130} fill="url(#bloomWide)" style={{mixBlendMode: 'screen'}} />
      <circle cx={SUN.x} cy={SUN.y} r={SUN.ring} fill="#fedd90" />
      <circle cx={SUN.x} cy={SUN.y} r={SUN.r} fill="#feedc5" />
      <circle cx={SUN.x} cy={SUN.y} r={58} fill="url(#bloomTight)" style={{mixBlendMode: 'screen'}} opacity={0.5} />
      <Birds f={f} />
      <g filter="url(#wobble)">
        <path d="M330,360 L352,312 L368,297 L382,280 L398,297 L414,305 L432,318 L452,330 L476,360 Z" fill="url(#farShade)" />
        <path d="M330,360 L352,312 L368,297 L382,280 L388,296 L381,312 L389,330 L384,360 Z" fill="url(#farLit)" />
        <path d="M368,297 L382,280 L398,297 L389,293 L382,300 L375,293 Z" fill="#ead2c8" />
        <path d="M330,360 L352,312 L368,297 L382,280 L398,297 L414,305 L432,318 L452,330 L476,360" fill="none" stroke={OUTLINE} strokeWidth={1.0} strokeLinejoin="round" />
        <path d="M640,360 L668,316 L692,290 L717,260 L742,284 L766,306 L796,318 L830,324 L860,330 L860,360 Z" fill="url(#farShade)" />
        <path d="M640,360 L668,316 L692,290 L717,260 L724,280 L714,300 L726,326 L716,360 Z" fill="url(#farLit)" />
        <path d="M697,284 L717,260 L742,284 L730,280 L722,290 L714,280 L705,289 Z" fill="#ead2c8" />
        <path d="M640,360 L668,316 L692,290 L717,260 L742,284 L766,306 L796,318 L830,324 L860,330" fill="none" stroke={OUTLINE} strokeWidth={1.0} strokeLinejoin="round" />
      </g>
      <rect x={300} y={290} width={560} height={76} fill="url(#haze)" opacity={0.8} />
      <g filter="url(#wobble)">
        <path d="M92,362 L104,282 L122,262 L141,238 L162,224 L178,239 L196,258 L216,268 L236,282 L243,300 L262,306 L283,326 L312,362 Z" fill="url(#mtnShade)" />
        <path d="M92,362 L104,282 L122,262 L141,238 L162,224 L170,240 L163,252 L172,268 L161,286 L174,304 L165,322 L177,340 L170,362 Z" fill="url(#mtnLit)" />
        <path d="M139,241 L162,224 L181,241 L172,239 L166,250 L159,240 L151,252 L145,243 Z" fill="#e8d0c8" />
        <path d="M162,224 L181,241 L172,239 L166,250 L163,236 Z" fill="#c4a0a2" />
        <path d="M92,362 L104,282 L122,262 L141,238 L162,224 L178,239 L196,258 L216,268 L236,282 L243,300 L262,306 L283,326 L312,362" fill="none" stroke={OUTLINE} strokeWidth={1.2} strokeLinejoin="round" />
      </g>
      <rect x={70} y={296} width={290} height={70} fill="url(#haze)" opacity={0.85} />
      <rect x={-5} y={322} width={870} height={44} fill="#ffb070" opacity={0.42} filter="url(#glowBlur)" style={{mixBlendMode: 'screen'}} />
      {/* mesa: dark maroon, horizontal strata bands and smudges, thin top outline */}
      <g>
        <path d="M-5,272 L40,270 L86,272 L113,276 L117,292 L114,318 L121,364 L-5,364 Z" fill="url(#mesa2)" />
        <g filter="url(#softBand)">
          {[282, 291, 299, 309, 320, 333, 347].map((y, i) => <path key={i} d={`M-5,${y} Q50,${y + (i % 2 ? 2 : -1)} 118,${y + 1}`} stroke={i % 2 ? '#6e2a1e' : '#44140c'} strokeOpacity={0.4} strokeWidth={i % 2 ? 2.4 : 3.2} fill="none" />)}
        </g>
        {[[30, 300, 18, 6], [80, 326, 22, 7]].map(([x, y, rx, ry], i) => <ellipse key={i} cx={x} cy={y} rx={rx} ry={ry} fill="#7a3424" opacity={0.35} filter="url(#soft2)" />)}
        {[287, 304, 326].map((y, i) => <path key={'c' + i} d={`M-5,${y} Q40,${y + 1.5} 80,${y - 0.5} T118,${y + 1}`} stroke="#220804" strokeOpacity={0.5} strokeWidth={0.7} fill="none" />)}
        {[24, 58, 97].map((x, i) => <path key={'v' + i} d={`M${x},${280 + i * 3} L${x - 1},${300 + i * 5} L${x + 1},${322}`} stroke="#220804" strokeOpacity={0.45} strokeWidth={0.7} fill="none" />)}
        <path d="M-5,272 L40,270 L86,272 L113,276 L117,292 L114,318" fill="none" stroke={OUTLINE} strokeWidth={1.1} strokeLinejoin="round" filter="url(#wobble)" />
      </g>
      <ellipse cx={70} cy={350} rx={90} ry={22} fill="#f09048" opacity={0.35} filter="url(#glowBlur)" style={{mixBlendMode: 'screen'}} />
      <ellipse cx={55} cy={333} rx={34} ry={9} fill="#f6a050" opacity={0.22} filter="url(#soft2)" style={{mixBlendMode: 'screen'}} />
      <g style={{mixBlendMode: 'screen'}}>{[[71, 312, 1.4]].map(([x, y, r], i) => <circle key={i} cx={x} cy={y} r={r * 1.8} fill="url(#speck)" opacity={0.55} />)}</g>
      {/* repeating hill arches with a pale pink rim */}
      <path d={arches(360) + ' L870,380 L-5,380 Z'} fill="url(#hills2)" />
      <path d={arches(360)} fill="none" stroke="#e8b4a4" strokeWidth={1.2} strokeOpacity={0.8} />
      {/* ground: firm horizontal stripes */}
      <rect x={-5} y={368} width={870} height={116} fill="url(#ground2)" />
      <g filter="url(#soft1)">
        {[374, 384, 395, 407, 420, 434, 449, 465].map((y, i) => <rect key={i} x={-5} y={y} width={870} height={i % 2 ? 4 : 5} fill={i % 2 ? '#9c5634' : '#4a2210'} opacity={i % 2 ? 0.5 : 0.45} />)}
      </g>
      {[[22, 446, 1.2], [64, 470, 1.3], [104, 462, 1.1], [150, 436, 0.9], [182, 456, 1.0], [228, 420, 0.7], [14, 414, 0.8], [130, 476, 1.2], [835, 424, 1.0], [812, 456, 1.1], [52, 404, 0.6], [92, 428, 0.65], [200, 474, 0.9], [262, 446, 0.75]].map(([x, y, s], i) => (
        <g key={i} opacity={0.62 + 0.3 * random(`go${i}`)}><Tuft x={x} y={y} s={s} seed={i} /></g>
      ))}
      <rect x={0} y={0} width={W} height={H} fill="url(#vigSky)" />
      <Dust f={f} n={100} seed="sky" box={[0, 0, 854, 350]} scale={2.0} />
      <Dust f={f} n={14} seed="land" box={[0, 270, 854, 470]} scale={2.0} />
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
    <circle cx={x} cy={y} r={16.4} fill="#f0c088" fillOpacity={0.55} stroke={BADGE} strokeWidth={3.1} />
    <circle cx={x} cy={y} r={13.0} fill="none" stroke={BADGE} strokeWidth={1.3} />
    <g transform={`translate(${x - 12.4} ${y - 12.4}) scale(0.248)`}><Pictogram kind={kind} /></g>
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
      <image href={staticFile('hq/paper_main.png')} x={278 - 6.67} y={22 - 6.67} width={315.3} height={453.3} preserveAspectRatio="none" filter="url(#paperShadow)" />
      {/* nail */}
      <circle cx={429} cy={32} r={6.4} fill="#1a0a04" opacity={0.5} filter="url(#soft1)" />
      <circle cx={428} cy={30} r={6.2} fill="#4a3848" stroke="#241a24" strokeWidth={1.1} />
      <circle cx={427.2} cy={29.2} r={4.0} fill="none" stroke="#7a6a7a" strokeWidth={1.0} />
      <circle cx={426.2} cy={28.0} r={1.5} fill="#f0e6f0" />
      <g filter="url(#ink)">
        <path d="M344,440 L294,440 L294,38 L563,38 L563,440 L512,440" fill="none" stroke={INK} strokeWidth={2} />
        <path d="M344,434 L299,434 L299,43 L558,43 L558,434 L512,434" fill="none" stroke={INK} strokeWidth={1} />
        <line x1={318} x2={538} y1={95.5} y2={95.5} stroke={INK} strokeWidth={1.5} />
        <rect x={328} y={98} width={200} height={134} fill="none" stroke={INK} strokeWidth={1.5} />
        <line x1={318} x2={wf.left - 0.6 * wf.font_size_ref} y1={277} y2={277} stroke={INK} strokeWidth={1} />
        <line x1={wf.right + 0.6 * wf.font_size_ref} x2={540} y1={277} y2={277} stroke={INK} strokeWidth={1} />
        <line x1={318} x2={540} y1={417} y2={417} stroke={INK} strokeWidth={1.2} />
      </g>
      {[322, 359, 396].map((y) => <line key={y} x1={357} x2={539} y1={y} y2={y} stroke="#86602f" strokeWidth={1.0} strokeDasharray="3.6 2.4" opacity={0.9} />)}
      {printSrc ? (
        <g style={{mixBlendMode: 'multiply'}}><image href={printSrc} x={329} y={99} width={198} height={132} preserveAspectRatio="xMidYMax slice" filter="url(#printTone)" /></g>
      ) : null}
      <PText k="WANTED" y={87.5} />
      <PText k="NAME" y={261.5} />
      <PText k="WANTED_FOR" y={280.3} />
      <PText k="REWARD" y={441.5} />
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
            {it >= 0 && <Badge x={poster.icon_center_x_px} y={y} kind={e.icon} s={sc} op={io} />}
          </g>
        );
      })}
      <text x={LY.VALUE.left} y={444.5} fontFamily="Bitter" fontWeight={900} fontSize={LY.VALUE.font_size_ref} letterSpacing={`${LY.VALUE.tracking_em}em`} fill={RED} filter="url(#inkRed)">{rv}</text>
    </g>
  );
};

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
          <SidePoster cx={149} top={-48} tex={0} op={sideOp(0)} printSrc={posterPrintSrc} />
          <SidePoster cx={154} top={252} tex={1} op={sideOp(1)} printSrc={posterPrintSrc} />
          <SidePoster cx={708} top={-48} tex={2} op={sideOp(2)} printSrc={posterPrintSrc} />
          <SidePoster cx={708} top={238} tex={3} op={sideOp(3)} faded printSrc={posterPrintSrc} />
          <MainPoster f={f} shot={shot} printSrc={posterPrintSrc} />
        </g>
        <rect x={0} y={0} width={W} height={H} fill="url(#warmPool)" style={{mixBlendMode: 'screen'}} />
        <rect x={0} y={0} width={W} height={H} fill="url(#vigWall)" />
        <Dust f={f} n={60} seed="wall" box={[0, 0, 854, 480]} scale={2.4} />
      </>
    );
  }
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" preserveAspectRatio="none">
        <Defs />
        {content}
      </svg>
    </AbsoluteFill>
  );
};
