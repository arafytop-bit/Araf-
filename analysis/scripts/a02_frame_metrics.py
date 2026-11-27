"""Per-frame visual metrics on the 30 fps grid (frame N = N/30 s).

For every frame i (compared with frame i-1):
  luma stats, saturation, near-black / near-white fractions, 3x3 luma grid,
  mean abs diff, HSV histogram distance, SSIM, edge density,
  ORB + estimateAffinePartial2D global motion (scale, rotation, tx, ty in 854x480 px),
plus a 64x36 RGB thumbnail of every frame for later fast analyses.
Output: analysis/data/frame_metrics.csv and work/thumbs64.npy
"""
import sys, os, numpy as np, cv2, csv
from multiprocessing import Pool

FR = 'work/frames/f_%05d.png'
N = len([f for f in os.listdir('work/frames') if f.endswith('.png')])
cv2.setNumThreads(1)

def load(i):
    im = cv2.imread(FR % i, cv2.IMREAD_COLOR)  # BGR uint8 854x480
    return im

def ssim(a, b):
    a = a.astype(np.float32); b = b.astype(np.float32)
    C1, C2 = (0.01*255)**2, (0.03*255)**2
    mu_a = cv2.GaussianBlur(a, (11, 11), 1.5); mu_b = cv2.GaussianBlur(b, (11, 11), 1.5)
    s_aa = cv2.GaussianBlur(a*a, (11, 11), 1.5) - mu_a**2
    s_bb = cv2.GaussianBlur(b*b, (11, 11), 1.5) - mu_b**2
    s_ab = cv2.GaussianBlur(a*b, (11, 11), 1.5) - mu_a*mu_b
    m = ((2*mu_a*mu_b + C1)*(2*s_ab + C2))/((mu_a**2 + mu_b**2 + C1)*(s_aa + s_bb + C2))
    return float(m.mean())

orb = None
def affine(g0, g1):
    global orb
    if orb is None:
        orb = cv2.ORB_create(nfeatures=1500, scaleFactor=1.2, nlevels=6, fastThreshold=10)
    k0, d0 = orb.detectAndCompute(g0, None); k1, d1 = orb.detectAndCompute(g1, None)
    if d0 is None or d1 is None or len(k0) < 8 or len(k1) < 8:
        return (np.nan,)*4 + (0, 0)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    m = bf.match(d0, d1)
    if len(m) < 8:
        return (np.nan,)*4 + (0, len(m))
    p0 = np.float32([k0[x.queryIdx].pt for x in m]); p1 = np.float32([k1[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=1.5, maxIters=3000, confidence=0.995)
    if M is None:
        return (np.nan,)*4 + (0, len(m))
    s = float(np.hypot(M[0, 0], M[1, 0])); th = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    # translation expressed about the frame centre: x' = s R (x - c) + c + t
    c = np.array([427.0, 240.0]); t = M[:, 2] + M[:, :2] @ c - c
    return (s, th, float(t[0]), float(t[1]), int(inl.sum()), len(m))

def metrics(i):
    cur = load(i)
    rgb = cur[:, :, ::-1].astype(np.float32)
    Y = 0.2126*rgb[:, :, 0] + 0.7152*rgb[:, :, 1] + 0.0722*rgb[:, :, 2]
    hsv = cv2.cvtColor(cur, cv2.COLOR_BGR2HSV)
    g = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)
    h, w = Y.shape
    grid = [float(Y[r*h//3:(r+1)*h//3, c*w//3:(c+1)*w//3].mean()) for r in range(3) for c in range(3)]
    edges = cv2.Canny(g, 60, 150)
    row = dict(frame=i, t=i/30.0, y_mean=float(Y.mean()), y_std=float(Y.std()),
               y_p02=float(np.percentile(Y, 2)), y_p98=float(np.percentile(Y, 98)),
               s_mean=float(hsv[:, :, 1].mean()), v_mean=float(hsv[:, :, 2].mean()),
               frac_black=float((Y < 16).mean()), frac_white=float((Y > 240).mean()),
               edge_density=float((edges > 0).mean()))
    for k, v in enumerate(grid):
        row[f'g{k}'] = v
    thumb = cv2.resize(cur, (64, 36), interpolation=cv2.INTER_AREA)[:, :, ::-1]
    if i == 0:
        row.update(mad=np.nan, hist_dist=np.nan, ssim=np.nan, aff_s=np.nan, aff_rot=np.nan, aff_tx=np.nan, aff_ty=np.nan, aff_inl=0, aff_matches=0)
        return row, thumb
    prev = load(i-1)
    gp = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    a = cv2.resize(gp, (427, 240), interpolation=cv2.INTER_AREA); b = cv2.resize(g, (427, 240), interpolation=cv2.INTER_AREA)
    row['mad'] = float(np.abs(a.astype(np.float32)-b.astype(np.float32)).mean())
    hp = cv2.calcHist([cv2.cvtColor(prev, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [16, 8, 8], [0, 180, 0, 256, 0, 256])
    hc = cv2.calcHist([hsv], [0, 1, 2], None, [16, 8, 8], [0, 180, 0, 256, 0, 256])
    cv2.normalize(hp, hp); cv2.normalize(hc, hc)
    row['hist_dist'] = float(cv2.compareHist(hp, hc, cv2.HISTCMP_BHATTACHARYYA))
    row['ssim'] = ssim(a, b)
    s, th, tx, ty, inl, nm = affine(gp, g)   # full res 854x480
    row.update(aff_s=s, aff_rot=th, aff_tx=tx, aff_ty=ty, aff_inl=inl, aff_matches=nm)
    return row, thumb

if __name__ == '__main__':
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rows = [None]*N; thumbs = np.zeros((N, 36, 64, 3), np.uint8)
    with Pool(nproc) as p:
        for k, (r, th) in enumerate(p.imap(metrics, range(N), chunksize=64)):
            rows[k] = r; thumbs[k] = th
            if k % 2000 == 0:
                print(k, flush=True)
    keys = list(rows[0].keys()) if 'mad' in rows[0] else list(rows[1].keys())
    with open('analysis/data/frame_metrics.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[1].keys())); wr.writeheader()
        for r in rows:
            wr.writerow(r)
    np.save('work/thumbs64.npy', thumbs)
    print('DONE', N)
