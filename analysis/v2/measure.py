"""Measure a video the same way for the reference and for our renders.

  python3 measure.py VIDEO OUTDIR [--fps4] [--sheets]

Produces in OUTDIR:
  diffs.npy        per-frame mean abs luma difference (30 fps, 192x108 analysis size)
  cuts.json        cut frames (hard cuts), shot lengths
  changes.json     every visual change event (cuts + in-shot pops/reveals)
  stats.json       pacing, palette, contrast, saturation, grain, vignette, motion
  f4/              frames at 4 fps (480 px tall) for viewing + contact sheets (sheet_###.jpg, 8x6 grid = 12 s each)
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

AW, AH = 192, 108


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                          '-show_entries', 'format=duration', '-of', 'json', path], capture_output=True, text=True).stdout
    j = json.loads(out)
    st = j['streams'][0]
    num, den = st['r_frame_rate'].split('/')
    return st['width'], st['height'], float(num) / float(den), float(j['format']['duration'])


def read_small(path, fps):
    """Stream frames at AWxAH: gray uint8 stack, colour-histogram distances, colour subsample (memory-light)."""
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={fps},scale={AW}:{AH}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10 ** 8)
    grays, hds, sub = [], [], []
    n = AW * AH * 3
    prev_h = None
    i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        f = np.frombuffer(b, np.uint8).reshape(AH, AW, 3)
        grays.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
        h = cv2.calcHist([f], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3).ravel()
        h = h / (h.sum() + 1e-9)
        hds.append(0.0 if prev_h is None else float(0.5 * np.abs(h - prev_h).sum()))
        prev_h = h
        if i % 15 == 0:
            sub.append(f.copy())
        i += 1
    p.wait()
    return np.stack(grays), np.array(hds, np.float32), np.stack(sub)


def detect(grays, hd, fps):
    from numpy.lib.stride_tricks import sliding_window_view
    d = np.zeros(len(grays), np.float32)
    for i in range(1, len(grays)):
        d[i] = np.abs(grays[i].astype(np.int16) - grays[i - 1].astype(np.int16)).mean()
    k = int(fps)
    pad = np.pad(d, k, mode='edge')
    base = np.median(sliding_window_view(pad, 2 * k + 1), axis=1)[:len(d)]
    cuts = [i for i in range(1, len(d)) if (d[i] > max(8.0, 5.0 * base[i]) and hd[i] > 0.15) or hd[i] > 0.55 or d[i] > 30]
    merged = []
    for c in cuts:
        if not merged or c - merged[-1] > 2:
            merged.append(c)
    changes = [i for i in range(1, len(d)) if d[i] > max(3.0, 3.0 * base[i])]
    ch = []
    for c in changes:
        if not ch or c - ch[-1] > 3:
            ch.append(c)
    return d, hd, merged, ch


def palette(frames, k=8):
    sample = frames[::max(1, len(frames) // 600)].reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(0)
    sample = sample[rng.choice(len(sample), min(60000, len(sample)), replace=False)]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, labels, centers = cv2.kmeans(sample, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    share = np.bincount(labels.ravel(), minlength=k) / len(labels)
    order = np.argsort(-share)
    return [dict(hex='#%02X%02X%02X' % tuple(int(v) for v in centers[i][::-1]), share=round(float(share[i]), 3)) for i in order]


def look_stats(frames):
    f = frames[::max(1, len(frames) // 900)]
    hsv = np.stack([cv2.cvtColor(x, cv2.COLOR_BGR2HSV) for x in f])
    luma = np.stack([cv2.cvtColor(x, cv2.COLOR_BGR2GRAY) for x in f]).astype(np.float32)
    lum_mean = float(luma.mean())
    lum_std = float(luma.std(axis=(1, 2)).mean())
    p5, p95 = [float(np.percentile(luma, q)) for q in (5, 95)]
    sat = float(hsv[..., 1].mean() / 2.55)
    black = float((luma < 25).mean() * 100)
    white = float((luma > 235).mean() * 100)
    # vignette: corner vs centre brightness
    h, w = luma.shape[1:]
    corner = np.concatenate([luma[:, :h // 5, :w // 6].ravel(), luma[:, :h // 5, -w // 6:].ravel(),
                             luma[:, -h // 5:, :w // 6].ravel(), luma[:, -h // 5:, -w // 6:].ravel()]).mean()
    centre = luma[:, h // 3:2 * h // 3, w // 3:2 * w // 3].mean()
    return dict(luma_mean=round(lum_mean, 1), contrast_std=round(lum_std, 1), luma_p5=p5, luma_p95=p95, saturation_pct=round(sat, 1),
                near_black_pct=round(black, 1), near_white_pct=round(white, 1), corner_to_centre=round(float(corner / (centre + 1e-6)), 3))


def grain(path, dur, n=40):
    """High-frequency noise in flat regions, measured on full-res frames (std of a 3x3 high-pass in low-gradient areas)."""
    vals = []
    for t in np.linspace(5, dur - 5, n):
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', path, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                           capture_output=True)
        im = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), 0)
        if im is None:
            continue
        im = cv2.resize(im, (854, 480), interpolation=cv2.INTER_AREA).astype(np.float32)
        hp = im - cv2.blur(im, (3, 3))
        gx = cv2.Sobel(cv2.GaussianBlur(im, (0, 0), 2), cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(cv2.GaussianBlur(im, (0, 0), 2), cv2.CV_32F, 0, 1)
        flat = np.hypot(gx, gy) < 4
        if flat.mean() > 0.05:
            vals.append(float(hp[flat].std()))
    return round(float(np.median(vals)), 3) if vals else None


def motion_stats(d, cuts, fps):
    cutset = set(cuts)
    inshot = np.array([d[i] for i in range(1, len(d)) if i not in cutset and (i - 1) not in cutset and (i + 1) not in cutset])
    return dict(static_frame_pct=round(float((inshot < 0.15).mean() * 100), 1), moving_frame_pct=round(float((inshot >= 0.15).mean() * 100), 1),
                median_inshot_diff=round(float(np.median(inshot)), 3))


def contact_sheets(path, outdir, dur, cols=8, rows=6, tile_h=135):
    os.makedirs(os.path.join(outdir, 'f4'), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vf', 'fps=4,scale=-2:480', '-q:v', '4',
                    os.path.join(outdir, 'f4', 'f_%05d.jpg')], check=True)
    files = sorted(f for f in os.listdir(os.path.join(outdir, 'f4')) if f.startswith('f_'))
    per = cols * rows
    for s in range(0, len(files), per):
        tiles = []
        for k, fn in enumerate(files[s:s + per]):
            im = cv2.imread(os.path.join(outdir, 'f4', fn))
            tw = int(im.shape[1] * tile_h / im.shape[0])
            im = cv2.resize(im, (tw, tile_h), interpolation=cv2.INTER_AREA)
            t = (s + k) / 4.0
            cv2.putText(im, f'{int(t // 60)}:{t % 60:05.2f}', (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1)
            tiles.append(im)
        while len(tiles) < per:
            tiles.append(np.zeros_like(tiles[0]))
        sheet = np.vstack([np.hstack(tiles[r * cols:(r + 1) * cols]) for r in range(rows)])
        cv2.imwrite(os.path.join(outdir, f'sheet_{s // per:03d}.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 80])


def main(path, outdir, sheets=False):
    os.makedirs(outdir, exist_ok=True)
    w, h, fps, dur = probe(path)
    grays, hdist, sub = read_small(path, fps)
    d, hd, cuts, changes = detect(grays, hdist, fps)
    nframes = len(grays)
    np.save(os.path.join(outdir, 'diffs.npy'), np.stack([d, hd]))
    shots = np.diff([0] + cuts + [nframes]) / fps
    n5 = int(np.ceil(nframes / fps / 5))
    cuts5 = np.bincount((np.array(cuts) / fps // 5).astype(int), minlength=n5)[:n5]
    ch5 = np.bincount((np.array(changes) / fps // 5).astype(int), minlength=n5)[:n5]
    stats = dict(
        file=os.path.basename(path), width=w, height=h, fps=fps, duration_s=round(dur, 2), frames=nframes,
        cuts=len(cuts), shots=len(shots), asl_s=round(float(shots.mean()), 3), median_shot_s=round(float(np.median(shots)), 3),
        shot_p10_s=round(float(np.percentile(shots, 10)), 3), shot_p90_s=round(float(np.percentile(shots, 90)), 3),
        longest_shot_s=round(float(shots.max()), 2), cuts_per_5s_mean=round(float(cuts5.mean()), 2),
        visual_changes_per_5s_mean=round(float(ch5.mean()), 2), visual_changes_per_5s_p10=float(np.percentile(ch5, 10)),
        windows_5s_without_any_change=int((ch5 == 0).sum()), first_cut_s=round(cuts[0] / fps, 3) if cuts else None,
        cuts_first_30s=int(sum(1 for c in cuts if c / fps < 30)), changes_first_30s=int(sum(1 for c in changes if c / fps < 30)),
        palette=palette(sub), look=look_stats(sub), grain_hp_std=grain(path, dur), motion=motion_stats(d, cuts, fps))
    json.dump(stats, open(os.path.join(outdir, 'stats.json'), 'w'), indent=1)
    json.dump(dict(cuts=[int(c) for c in cuts], shot_s=[round(float(x), 3) for x in shots]), open(os.path.join(outdir, 'cuts.json'), 'w'))
    json.dump(dict(changes=[int(c) for c in changes], per5=[int(x) for x in ch5]), open(os.path.join(outdir, 'changes.json'), 'w'))
    if sheets:
        contact_sheets(path, outdir, dur)
    print(json.dumps({k: v for k, v in stats.items() if k not in ('palette',)}, indent=1))
    print('palette', stats['palette'])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--sheets' in sys.argv)
