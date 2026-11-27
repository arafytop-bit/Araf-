"""Fit cubic-bezier easings (CSS-style) to measured normalised progress curves."""
import numpy as np
from scipy.optimize import minimize

def bezier_y_at_x(x1, y1, x2, y2, xs):
    # solve x(u)=xs for u by bisection, return y(u)
    xs = np.atleast_1d(np.asarray(xs, float))
    lo = np.zeros_like(xs); hi = np.ones_like(xs)
    for _ in range(40):
        u = (lo + hi)/2
        x = 3*(1-u)**2*u*x1 + 3*(1-u)*u**2*x2 + u**3
        lo = np.where(x < xs, u, lo); hi = np.where(x >= xs, u, hi)
    u = (lo + hi)/2
    return 3*(1-u)**2*u*y1 + 3*(1-u)*u**2*y2 + u**3

def fit_bezier(t, p, allow_overshoot=False):
    t = np.asarray(t, float); p = np.asarray(p, float)
    best = None
    for x1, y1, x2, y2 in [(0.42, 0, 0.58, 1), (0.25, 0.1, 0.25, 1), (0.33, 1, 0.68, 1), (0.55, 0, 1, 0.45), (0.0, 0.0, 0.58, 1), (0.42, 0, 1, 1)]:
        def loss(v):
            a, b, c, d = v
            if not (0 <= a <= 1 and 0 <= c <= 1): return 1e3
            if not allow_overshoot and not (-0.2 <= b <= 1.2 and -0.2 <= d <= 1.2): return 1e3
            return float(((bezier_y_at_x(a, b, c, d, t) - p)**2).mean())
        r = minimize(loss, [x1, y1, x2, y2], method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-8, maxiter=4000))
        if best is None or r.fun < best[1]:
            best = (r.x, r.fun)
    (a, b, c, d), err = best
    return dict(cubic_bezier=[round(float(a), 3), round(float(b), 3), round(float(c), 3), round(float(d), 3)], rmse=round(float(np.sqrt(err)), 4))

def segment_fit(frames, values, f0, f1):
    """normalised progress of values between f0 and f1 (inclusive) -> bezier fit"""
    frames = np.asarray(frames); values = np.asarray(values, float)
    sel = (frames >= f0) & (frames <= f1)
    fr = frames[sel]; v = values[sel]
    v0 = values[frames == f0][0]; v1 = values[frames == f1][0]
    t = (fr - f0)/(f1 - f0); p = (v - v0)/(v1 - v0 + 1e-12)
    out = fit_bezier(t, p)
    out.update(f0=int(f0), f1=int(f1), v0=round(float(v0), 4), v1=round(float(v1), 4),
               samples=[[int(a), round(float(b), 4)] for a, b in zip(fr, v)])
    return out
