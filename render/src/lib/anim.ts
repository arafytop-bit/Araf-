// Generic keyframe / easing helpers driven by blueprint data.
import {Easing} from 'remotion';

export type Ease = 'linear' | [number, number, number, number] | undefined;
export type Key = {f: number; ease?: Ease; log_scale?: boolean; [prop: string]: any};

export const easeFn = (e: Ease) => {
  if (!e || e === 'linear') return (t: number) => t;
  return Easing.bezier(e[0], e[1], e[2], e[3]);
};

// Value of `prop` at frame f from a key list. Each key carries the easing of the segment that ENDS at it.
export const keyed = (keys: Key[], prop: string, f: number, fallback = 0): number => {
  const ks = keys.filter((k) => k[prop] !== undefined);
  if (ks.length === 0) return fallback;
  if (f <= ks[0].f) return ks[0][prop];
  for (let i = 1; i < ks.length; i++) {
    const a = ks[i - 1], b = ks[i];
    if (f <= b.f) {
      // per-property easing override: key.ease_<prop> (e.g. ease_ty) beats key.ease
      const t = easeFn(b['ease_' + prop] ?? b.ease)((f - a.f) / (b.f - a.f));
      if (prop === 's' && (b.log_scale || a.log_scale)) {
        return Math.exp(Math.log(a[prop]) + (Math.log(b[prop]) - Math.log(a[prop])) * t);
      }
      return a[prop] + (b[prop] - a[prop]) * t;
    }
  }
  return ks[ks.length - 1][prop];
};

// Piecewise-linear lookup in [[offset, value], ...] tables (measured keyframes).
export const table = (pairs: number[][], x: number): number => {
  if (x <= pairs[0][0]) return pairs[0][1];
  for (let i = 1; i < pairs.length; i++) {
    if (x <= pairs[i][0]) {
      const [x0, y0] = pairs[i - 1];
      const [x1, y1] = pairs[i];
      return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0);
    }
  }
  return pairs[pairs.length - 1][1];
};

// world -> screen similarity used by the analysis: p_s = s*(p_w - c) + c + t
export const camTransform = (s: number, tx: number, ty: number, k: number, cx = 427, cy = 240) =>
  `translate(${(cx + tx) * k}px, ${(cy + ty) * k}px) scale(${s}) translate(${-cx * k}px, ${-cy * k}px)`;

// underdamped spring (frames) used for tag / bubble pops
export const springVal = (t: number, w0: number, z: number) => {
  if (t <= 0) return 0;
  const wd = w0 * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + ((z * w0) / wd) * Math.sin(wd * t));
};
