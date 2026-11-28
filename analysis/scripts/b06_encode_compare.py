"""Encoding colour-shift check: decoded MP4 frames vs. the PNG masters scaled to the same size with the same filter.
Reports per-frame mean dE2000 (pixel-wise, 20k random pixels), mean signed RGB offset, and 99th-percentile channel error.
"""
import subprocess, glob, os, json, sys, numpy as np, cv2
sys.path.insert(0, 'analysis/scripts')
from b04_lookdev_metrics import srgb_to_lab
OUT = 'work/hq/enc'; mp4 = f'{OUT}/segment_1080p_crf16.mp4'
os.makedirs(f'{OUT}/dec', exist_ok=True); os.makedirs(f'{OUT}/ref1080', exist_ok=True)
subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-y', '-i', mp4, '-vf', 'scale=in_color_matrix=bt709:in_range=tv:flags=accurate_rnd+full_chroma_int,format=rgb24', f'{OUT}/dec/d_%03d.png'], check=True, capture_output=True)
pngs = sorted(glob.glob(f'{OUT}/png/element-*.png'))
for p in pngs:
    o = f"{OUT}/ref1080/{os.path.basename(p)}"
    if not os.path.exists(o):
        subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-y', '-i', p, '-vf', 'scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int,format=rgb24', o], check=True, capture_output=True)
decs = sorted(glob.glob(f'{OUT}/dec/d_*.png'))
def de76fast(l1, l2):
    return np.sqrt(((l1-l2)**2).sum(-1))
rng = np.random.default_rng(0); res = []
from b04_lookdev_metrics import de2000
for p, d in zip(sorted(glob.glob(f'{OUT}/ref1080/*.png')), decs):
    A = cv2.imread(p)[:, :, ::-1].astype(np.float32); B = cv2.imread(d)[:, :, ::-1].astype(np.float32)
    idx = rng.integers(0, A.shape[0]*A.shape[1], 20000)
    a = A.reshape(-1, 3)[idx]; b = B.reshape(-1, 3)[idx]
    la, lb = srgb_to_lab(a), srgb_to_lab(b)
    de = np.array([de2000(la[i], lb[i]) for i in range(0, 20000, 10)])
    # region means (8x8 blocks) to see systematic shifts
    ma = cv2.resize(A, (240, 135), interpolation=cv2.INTER_AREA).reshape(-1, 3); mb = cv2.resize(B, (240, 135), interpolation=cv2.INTER_AREA).reshape(-1, 3)
    dm = np.array([de2000(srgb_to_lab(ma[i]), srgb_to_lab(mb[i])) for i in range(0, len(ma), 37)])
    res.append(dict(frame=os.path.basename(p), pixel_dE00_mean=round(float(de.mean()), 3), pixel_dE00_p99=round(float(np.percentile(de, 99)), 3),
                    block_mean_dE00_mean=round(float(dm.mean()), 3), block_mean_dE00_max=round(float(dm.max()), 3),
                    mean_rgb_offset=[round(float(v), 2) for v in (B-A).reshape(-1, 3).mean(0)], abs_err_p99=round(float(np.percentile(np.abs(B-A), 99)), 1)))
summary = dict(frames=len(res), pixel_dE00_mean=round(float(np.mean([r['pixel_dE00_mean'] for r in res])), 3), block_dE00_max=round(float(np.max([r['block_mean_dE00_max'] for r in res])), 3),
               mean_rgb_offset=[round(float(np.mean([r['mean_rgb_offset'][k] for r in res])), 2) for k in range(3)])
json.dump(dict(summary=summary, frames=res), open('analysis/lookdev/encode_check.json', 'w'), indent=1)
print(json.dumps(summary))
