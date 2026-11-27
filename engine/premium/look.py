"""Look: black vignette stage, photo grading, blur-fill frames, depth, final finish.

Reference numbers (style bible §2): 72.5 % near-black pixels; stage #0B0B0B centre -> #030303 edges,
corner/centre brightness 0.12; black/white/grey carry everything, red is the only accent; photos bring the colour;
blur-fill behind framed photos (same image, blurred + darkened); grain ~0.6 (clean, no film grain).
"""
import functools
import os

import cv2
import numpy as np
import skia

from ..core import W, H, vignette_image

IMG_DIR = None          # set by the project
SAMPLING = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def stage(c):
    c.drawImage(vignette_image(), 0, 0)


def _to_skia(arr_bgr):
    rgba = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2RGBA)
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.ColorType.kRGBA_8888_ColorType)


@functools.lru_cache(maxsize=96)
def raw(key):
    p = os.path.join(IMG_DIR, key + '.jpg')
    im = cv2.imread(p, cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(p)
    return im


def exists(key):
    return key and os.path.exists(os.path.join(IMG_DIR, key + '.jpg'))


def grade_arr(im, sat=0.88, contrast=1.08, gamma=1.0, gain=1.0, warm=0.0):
    """Cohesive photo grade: slightly desaturated, a touch more contrast, neutral blacks (keeps natural colour)."""
    x = im.astype(np.float32) / 255.0
    lum = (0.114 * x[..., 0] + 0.587 * x[..., 1] + 0.299 * x[..., 2])[..., None]
    x = lum + (x - lum) * sat
    x = (x - 0.5) * contrast + 0.5
    x = np.clip(x, 0, 1) ** gamma * gain
    if warm:
        x[..., 2] *= 1 + warm
        x[..., 0] *= 1 - warm
    return np.clip(x * 255 + np.random.default_rng(3).uniform(-0.5, 0.5, x.shape), 0, 255).astype(np.uint8)


def crop_arr(im, aspect, focus=(0.5, 0.5), zoom=1.0):
    """Crop to aspect (w/h) around a focus point (fractions); zoom > 1 crops tighter."""
    h, w = im.shape[:2]
    if w / h > aspect:
        ch, cw = h, h * aspect
    else:
        cw, ch = w, w / aspect
    cw, ch = cw / zoom, ch / zoom
    cx = min(max(focus[0] * w, cw / 2), w - cw / 2)
    cy = min(max(focus[1] * h, ch / 2), h - ch / 2)
    x0, y0 = int(round(cx - cw / 2)), int(round(cy - ch / 2))
    return im[y0:y0 + int(round(ch)), x0:x0 + int(round(cw))]


@functools.lru_cache(maxsize=160)
def plate(key, w, h, focus=(0.5, 0.5), zoom=1.0, sat=0.88, contrast=1.08, gain=1.0, blur=0.0, oversize=1.06):
    """Graded photo cropped to w x h (rendered `oversize` larger so push-ins never reveal edges)."""
    im = crop_arr(raw(key), w / h, focus, zoom)
    ow, oh = int(w * oversize), int(h * oversize)
    interp = cv2.INTER_AREA if im.shape[1] > ow else cv2.INTER_CUBIC
    im = cv2.resize(im, (ow, oh), interpolation=interp)
    if blur:
        im = cv2.GaussianBlur(im, (0, 0), blur)
    return _to_skia(grade_arr(im, sat=sat, contrast=contrast, gain=gain))


@functools.lru_cache(maxsize=96)
def blur_fill(key, gain=0.36, sigma=28, focus=(0.5, 0.5)):
    """Full-frame blurred + darkened copy (reference blur-fill behind framed photos), with a vignette baked in."""
    im = crop_arr(raw(key), W / H, focus, 1.0)
    small = cv2.resize(im, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / 4)
    big = cv2.resize(small, (int(W * 1.08), int(H * 1.08)), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    yy, xx = np.mgrid[0:big.shape[0], 0:big.shape[1]].astype(np.float32)
    r = np.sqrt(((xx - big.shape[1] / 2) / (big.shape[1] / 2)) ** 2 + ((yy - big.shape[0] / 2) / (big.shape[0] / 2)) ** 2)
    vig = np.clip(1.0 - 0.55 * np.clip(r - 0.35, 0, None) ** 1.3, 0.2, 1.0)[..., None]
    lum = big.mean(axis=2, keepdims=True)
    big = (lum + (big - lum) * 0.7) * gain * vig
    big += np.random.default_rng(5).uniform(-0.6, 0.6, big.shape)
    return _to_skia(np.clip(big, 0, 255).astype(np.uint8))


@functools.lru_cache(maxsize=4)
def vignette_overlay(strength=0.55, inner=0.45):
    """Black radial vignette (alpha only) for full-frame photo scenes."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = np.clip((r - inner) / (1.42 - inner), 0, 1) ** 1.6 * strength
    a = np.clip(a * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, a.shape), 0, 255).astype(np.uint8)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 3] = a
    return skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kUnpremul_AlphaType)


@functools.lru_cache(maxsize=8)
def top_scrim(h_frac=0.36, strength=0.78):
    """Dark gradient from the top edge: keeps callouts legible over photos (broadcast-style scrim)."""
    hh = int(H * h_frac)
    a = np.linspace(1, 0, hh, dtype=np.float32) ** 1.4 * strength
    a = np.clip(a[:, None] * 255 + np.random.default_rng(4).uniform(-0.5, 0.5, (hh, W)), 0, 255).astype(np.uint8)
    rgba = np.zeros((hh, W, 4), np.uint8)
    rgba[..., 3] = a
    return skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kUnpremul_AlphaType)


def draw_scaled(c, img, cx, cy, scale, alpha=1.0, w=None, h=None):
    """Draw img centred at (cx, cy) at `scale` (relative to w x h target size, default image size)."""
    iw, ih = img.width(), img.height()
    tw = (w or iw) * scale
    th = (h or ih) * scale
    p = None
    if alpha < 1:
        p = skia.Paint()
        p.setAlphaf(alpha)
    c.drawImageRect(img, skia.Rect(cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2), SAMPLING, p)


def soft_shadow(c, rect, radius=18.0, offset=(0, 14), alpha=0.75, corner=6):
    p = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    p.setAlphaf(alpha)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, radius))
    r = skia.Rect(rect.left() + offset[0], rect.top() + offset[1], rect.right() + offset[0], rect.bottom() + offset[1])
    c.drawRRect(skia.RRect.MakeRectXY(r, corner, corner), p)


def contact_shadow(c, x, y, w, alpha=0.5):
    """Soft ellipse under a character's feet: grounds cartoon figures on real photos."""
    p = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    p.setAlphaf(alpha)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, w * 0.09))
    c.drawOval(skia.Rect(x - w / 2, y - w * 0.09, x + w / 2, y + w * 0.09), p)


def luma_stats(key, rect_frac, focus=(0.5, 0.5), zoom=1.0):
    """Mean/std luma of a photo region as it appears full-frame (for text-contrast decisions)."""
    im = crop_arr(raw(key), W / H, focus, zoom)
    h, w = im.shape[:2]
    x0, y0, x1, y1 = rect_frac
    reg = cv2.cvtColor(im[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)], cv2.COLOR_BGR2GRAY).astype(np.float32)
    return float(reg.mean()), float(reg.std())
