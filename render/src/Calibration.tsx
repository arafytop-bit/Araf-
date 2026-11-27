// Calibration render: rebuilds frames 0-149 of the reference from analysis/blueprint.json only.
// All geometry is in reference pixels (854x480 viewBox) so the same code renders at any resolution.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import bp from './data/blueprint.json';
import {keyed, table, Key} from './lib/anim';
import {loadFonts} from './lib/fonts';

const C = (bp as any).calibration;
const T = (bp as any).templates;
const COL = (bp as any).style_tokens.colors;
const W = 854, H = 480, CX = 427, CY = 240;

const camT = (s: number, tx: number, ty: number) => `translate(${CX + tx} ${CY + ty}) scale(${s}) translate(${-CX} ${-CY})`;
const scaleAbout = (s: number, ax: number, ay: number) => `translate(${ax} ${ay}) scale(${s}) translate(${-ax} ${-ay})`;

// ---------------- placeholders (no reference pixels are used) ----------------
const SunsetLandscape: React.FC = () => (
  <g>
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#3a1d33" />
        <stop offset="0.35" stopColor="#7b3445" />
        <stop offset="0.6" stopColor="#c8603a" />
        <stop offset="0.72" stopColor="#e59a4a" />
      </linearGradient>
      <radialGradient id="sunglow" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0" stopColor="#ffe9b0" stopOpacity="0.9" />
        <stop offset="1" stopColor="#ffb060" stopOpacity="0" />
      </radialGradient>
    </defs>
    <rect x={-200} y={-200} width={1254} height={900} fill="url(#sky)" />
    <circle cx={330} cy={288} r={120} fill="url(#sunglow)" />
    <circle cx={330} cy={288} r={38} fill="#ffe2a0" />
    <polygon points="-50,330 90,250 160,230 230,300 300,330" fill="#6b2d2b" />
    <polygon points="140,240 160,230 178,246 160,250" fill="#e8c9c0" />
    <polygon points="260,330 360,285 420,310 470,330" fill="#5e2626" />
    <polygon points="600,330 715,262 800,320 900,330" fill="#6b2d2b" />
    <polygon points="700,272 715,262 730,276" fill="#e8c9c0" />
    <rect x={-200} y={325} width={1254} height={400} fill="#4f2119" />
    {[340, 365, 395, 430].map((y, i) => (
      <rect key={i} x={-200} y={y} width={1254} height={3} fill="#5c281d" />
    ))}
  </g>
);

const HeroBust: React.FC = () => (
  <g>
    <path d="M330,480 C335,380 400,330 470,315 L640,315 C710,330 770,380 790,480 Z" fill="#3b2a24" stroke="#120a08" strokeWidth={3} />
    <rect x={515} y={260} width={80} height={70} fill="#6e4430" stroke="#120a08" strokeWidth={2} />
    <ellipse cx={555} cy={205} rx={70} ry={85} fill="#7a4a32" stroke="#120a08" strokeWidth={3} />
    <path d="M490,215 Q555,330 620,215 L620,250 Q555,320 490,250 Z" fill="#4a2b1b" />
    <ellipse cx={545} cy={118} rx={165} ry={24} fill="#231915" stroke="#0a0605" strokeWidth={3} />
    <path d="M470,118 C470,60 520,52 548,60 C580,52 625,60 620,118 Z" fill="#231915" stroke="#0a0605" strokeWidth={3} />
    <text x={555} y={470} textAnchor="middle" fontFamily="Alegreya Sans" fontWeight={500} fontSize={11} fill="#cbb">placeholder hero bust</text>
  </g>
);

const WoodWall: React.FC = () => {
  const planks = [];
  for (let x = -1000; x < 1900; x += 66) planks.push(<rect key={x} x={x} y={-700} width={3} height={1900} fill="#5a2a0b" />);
  return (
    <g>
      <rect x={-1000} y={-700} width={2900} height={1900} fill={COL.wood_wall} />
      {planks}
    </g>
  );
};

const PosterBody: React.FC<{small?: boolean}> = ({small}) => (
  <g>
    <path d="M278,22 L420,26 L580,20 L584,180 L578,330 L583,462 L470,456 L420,466 L282,460 L276,300 L280,150 Z" fill={COL.poster_parchment} />
    <rect x={290} y={34} width={278} height={414} fill="none" stroke="#2b1a10" strokeWidth={1.4} />
    <circle cx={428} cy={30} r={4} fill="#3a2a20" />
    <text x={428} y={88} textAnchor="middle" fontFamily="Source Serif 4" fontWeight={900} fontSize={56.7} letterSpacing={1} fill="#2b1a10">WANTED</text>
    <line x1={312} y1={95} x2={544} y2={95} stroke="#2b1a10" strokeWidth={1.5} />
    <rect x={328} y={98} width={200} height={134} fill="#c9a874" stroke="#2b1a10" strokeWidth={2} />
    <path d="M360,232 C370,195 400,180 428,178 C456,180 486,195 496,232 Z" fill="#6d5238" />
    <ellipse cx={428} cy={150} rx={24} ry={30} fill="#6d5238" />
    <ellipse cx={428} cy={122} rx={46} ry={7} fill="#4a3826" />
    {!small && (
      <>
        <text x={428} y={262} textAnchor="middle" fontFamily="Source Serif 4" fontWeight={900} fontSize={25.4} fill="#2b1a10">ARTHUR MORGAN</text>
        <line x1={318} y1={277} x2={392} y2={277} stroke="#2b1a10" strokeWidth={1} />
        <line x1={466} y1={277} x2={540} y2={277} stroke="#2b1a10" strokeWidth={1} />
        <text x={429} y={281} textAnchor="middle" fontFamily="Alegreya Sans" fontWeight={800} fontSize={10.5} letterSpacing={2} fill="#2b1a10">WANTED FOR</text>
        {[322, 359, 396].map((y) => (
          <line key={y} x1={358} y1={y} x2={540} y2={y} stroke="#a88a5c" strokeWidth={1} strokeDasharray="2 3" />
        ))}
        <line x1={318} y1={417} x2={540} y2={417} stroke="#2b1a10" strokeWidth={1} />
        <text x={350} y={440} fontFamily="Alegreya Sans" fontWeight={800} fontSize={10} letterSpacing={3} fill="#2b1a10">REWARD</text>
      </>
    )}
  </g>
);

const Icon: React.FC<{kind: string; x: number; y: number; r: number}> = ({kind, x, y, r}) => (
  <g>
    <circle cx={x} cy={y} r={r} fill="none" stroke={COL.poster_red} strokeWidth={2.4} />
    {kind === 'train' && <rect x={x - 8} y={y - 5} width={16} height={9} fill={COL.poster_red} />}
    {kind === 'moneybag' && <circle cx={x} cy={y + 1} r={7} fill={COL.poster_red} />}
    {kind === 'map' && <rect x={x - 8} y={y - 7} width={16} height={13} fill="none" stroke={COL.poster_red} strokeWidth={2} />}
  </g>
);

// ---------------- templates ----------------
const HeroTitle: React.FC<{e: any; f: number}> = ({e, f}) => {
  const tpl = T.hero_title.anim_in;
  const fs = e.cap_px / 0.637; // Alegreya cap-height 0.637 em
  const finalTrack = 0.15 * fs;
  const lineEls = e.lines.map((txt: string, i: number) => {
    const s0 = e.start + i * tpl.line_stagger_frames;
    const t = f - s0;
    if (t < 0) return null;
    const op = Math.min(1, (t + 1) / tpl.line_opacity_frames);
    const tr = Math.min(1, Math.max(0, (t - 1) / tpl.tracking.duration_frames));
    const easeOut = 1 - Math.pow(1 - tr, 3);
    const extra = tpl.tracking.extra_px_per_gap_ref_start * (1 - easeOut);
    // keep the block's centre fixed while tracking tightens
    const gaps = txt.length - 1;
    const cxLine = e.left_px + 98.5; // measured centre of the settled line (59..255)
    return (
      <text key={i} x={cxLine} y={e.baselines_px[i]} textAnchor="middle" fontFamily="Alegreya" fontWeight={800} fontSize={fs}
        letterSpacing={finalTrack + extra} fill={COL.title_fill} stroke={COL.title_outline} strokeWidth={1.5} paintOrder="stroke"
        opacity={op} style={{filter: 'drop-shadow(0.5px 1.5px 1.5px rgba(0,0,0,0.55))'}}>
        {txt}
        <tspan dx={-(finalTrack + extra)}>{''}</tspan>
      </text>
    );
  });
  const rs = e.start + tpl.rule.start_offset;
  const rp = f >= rs ? table(tpl.rule.draw_from_centre_keyframes, f - rs) : 0;
  const rc = (e.rule_x_px[0] + e.rule_x_px[1]) / 2, rh = (e.rule_x_px[1] - e.rule_x_px[0]) / 2;
  const ss = e.start + tpl.subline.start_offset;
  const sop = f >= ss ? Math.min(1, (f - ss + 1) / tpl.subline.fade_frames) : 0;
  return (
    <g>
      {lineEls}
      {rp > 0 && <line x1={rc - rh * rp} x2={rc + rh * rp} y1={e.rule_y_px} y2={e.rule_y_px} stroke="#c9a27a" strokeWidth={1} />}
      {f >= e.start + 11 && <rect x={rc - 3} y={e.rule_y_px - 3} width={6} height={6} transform={`rotate(45 ${rc} ${e.rule_y_px})`} fill="#c9a27a" opacity={Math.min(1, (f - e.start - 10) / 3)} />}
      {sop > 0 && (
        <text x={e.subline_center_x_px} y={e.subline_baseline_px} textAnchor="middle" fontFamily="Alegreya" fontStyle="italic" fontWeight={700} fontSize={e.subline_cap_px / 0.636} fill="#c8ad8e" opacity={sop}>
          {e.subline}
        </text>
      )}
    </g>
  );
};

const ListItem: React.FC<{e: any; f: number; poster: any}> = ({e, f, poster}) => {
  const tpl = T.list_item_stamped_icon.anim_in;
  const t = f - e.start;
  if (t < 0) return null;
  const y = poster.rows_center_y_px[e.row];
  const op = table(tpl.text_opacity_keyframes, t);
  const it = t - tpl.icon_start_offset;
  const fs = poster.item_cap_px / 0.67;
  let icon = null;
  if (it >= 0) {
    const fr = tpl.icon_keyframes.frames;
    const sc = table(fr.map((x: number, i: number) => [x, tpl.icon_keyframes.scale[i]]), it);
    const io = table(fr.map((x: number, i: number) => [x, tpl.icon_keyframes.opacity[i]]), it);
    icon = (
      <g transform={`translate(${poster.icon_center_x_px} ${y}) scale(${sc}) translate(${-poster.icon_center_x_px} ${-y})`} opacity={io}>
        <Icon kind={e.icon} x={poster.icon_center_x_px} y={y} r={poster.icon_diameter_px / 2} />
      </g>
    );
  }
  return (
    <g>
      <text x={poster.item_text_left_px} y={y + poster.item_cap_px / 2} fontFamily="Source Serif 4" fontWeight={900} fontSize={fs} fill="#2b1a10" opacity={op}>{e.text}</text>
      {icon}
    </g>
  );
};

const RewardValue: React.FC<{e: any; f: number; poster: any}> = ({e, f, poster}) => {
  let txt = e.text_sequence[0][1];
  for (const [fr, s] of e.text_sequence) if (f >= fr) txt = s;
  return (
    <text x={poster.reward_value_x_px} y={poster.reward_baseline_px} fontFamily="Source Serif 4" fontWeight={900} fontSize={poster.reward_cap_px / 0.67} fill={COL.poster_red}>{txt}</text>
  );
};

const WallReveal: React.FC<{e: any; f: number}> = ({e, f}) => (
  <g>
    {e.posters.map(([x, y]: number[], i: number) => {
      const t = f - (e.start + i * e.stagger_frames);
      if (t < 0) return null;
      const op = Math.min(1, (t + 1) / e.fade_frames);
      return (
        <g key={i} opacity={op} transform={`translate(${x - 428} ${y - 240})`}>
          <PosterBody small />
        </g>
      );
    })}
  </g>
);

const Vignette: React.FC = () => (
  <g>
    <defs>
      <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75">
        <stop offset="0.45" stopColor="#000" stopOpacity="0" />
        <stop offset="1" stopColor="#000" stopOpacity="0.55" />
      </radialGradient>
    </defs>
    <rect x={0} y={0} width={W} height={H} fill="url(#vig)" />
  </g>
);

export const Calibration: React.FC = () => {
  loadFonts();
  const f = useCurrentFrame();
  const shot = C.shots.find((s: any) => f >= s.start && f <= s.end) ?? C.shots[C.shots.length - 1];
  let content = null;
  if (shot.id === 's0') {
    const bg = shot.layers[0], hero = shot.layers[1];
    content = (
      <>
        <g transform={scaleAbout(keyed(bg.keys as Key[], 's', f, 1), bg.anchor[0], bg.anchor[1])}><SunsetLandscape /></g>
        <g transform={scaleAbout(keyed(hero.keys as Key[], 's', f, 1), hero.anchor[0], hero.anchor[1])}><HeroBust /></g>
        <Vignette />
        {shot.elements.map((e: any, i: number) => (e.template === 'hero_title' ? <HeroTitle key={i} e={e} f={f} /> : null))}
      </>
    );
  } else {
    const cam = shot.camera as Key[];
    const s = keyed(cam, 's', f, 1), tx = keyed(cam, 'tx', f, 0), ty = keyed(cam, 'ty', f, 0);
    const poster = shot.poster;
    content = (
      <>
        <g transform={camT(s, tx, ty)}>
          <WoodWall />
          {shot.elements.filter((e: any) => e.template === 'poster_wall_reveal').map((e: any, i: number) => <WallReveal key={i} e={e} f={f} />)}
          <PosterBody />
          {shot.elements.map((e: any, i: number) => {
            if (e.template === 'list_item_stamped_icon') return <ListItem key={i} e={e} f={f} poster={poster} />;
            if (e.template === 'counter_suffix') return <RewardValue key={i} e={e} f={f} poster={poster} />;
            return null;
          })}
        </g>
        <Vignette />
      </>
    );
  }
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" preserveAspectRatio="none">{content}</svg>
    </AbsoluteFill>
  );
};
