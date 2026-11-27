"""Direct registration of frames to a reference frame (not chained), optionally restricted to a region mask.

usage: python a10_track_region.py REF F0 F1 x0 y0 x1 y1 [label]
Region in 854x480 px. Outputs CSV rows: frame, s, rot_deg, tx, ty (similarity about frame centre; maps REF -> frame), inliers.
Uses SIFT (more precise than ORB for sub-pixel / sub-percent scale) + RANSAC similarity.
"""
import sys, numpy as np, cv2, csv, os
ref, f0, f1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
x0, y0, x1, y1 = map(int, sys.argv[4:8]); label = sys.argv[8] if len(sys.argv) > 8 else 'region'
sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02)
def load(i):
    return cv2.imread(f'work/frames/f_{i:05d}.png', cv2.IMREAD_GRAYSCALE)
mask = np.zeros((480, 854), np.uint8); mask[y0:y1, x0:x1] = 255
g0 = load(ref); k0, d0 = sift.detectAndCompute(g0, mask)
bf = cv2.BFMatcher(cv2.NORM_L2)
c = np.array([427.0, 240.0])
rows = []
for i in range(f0, f1+1):
    g = load(i); k1, d1 = sift.detectAndCompute(g, None)
    if d1 is None or len(k1) < 6:
        rows.append([i, np.nan, np.nan, np.nan, np.nan, 0]); continue
    mt = bf.knnMatch(d0, d1, k=2)
    good = [a for a, b in (x for x in mt if len(x) == 2) if a.distance < 0.75*b.distance]
    if len(good) < 6:
        rows.append([i, np.nan, np.nan, np.nan, np.nan, len(good)]); continue
    p0 = np.float32([k0[g_.queryIdx].pt for g_ in good]); p1 = np.float32([k1[g_.trainIdx].pt for g_ in good])
    M, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=1.0, maxIters=5000, confidence=0.999)
    if M is None:
        rows.append([i, np.nan, np.nan, np.nan, np.nan, 0]); continue
    # refine with inliers only (least squares)
    sel = inl.ravel() == 1
    M2, _ = cv2.estimateAffinePartial2D(p0[sel], p1[sel], method=cv2.LMEDS)
    M = M2 if M2 is not None else M
    s = float(np.hypot(M[0, 0], M[1, 0])); th = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    t = M[:, 2] + M[:, :2] @ c - c
    rows.append([i, round(s, 5), round(th, 4), round(float(t[0]), 2), round(float(t[1]), 2), int(sel.sum())])
os.makedirs('analysis/data/tracks', exist_ok=True)
out = f'analysis/data/tracks/{label}_{ref}_{f0}_{f1}.csv'
with open(out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['frame', 's', 'rot_deg', 'tx', 'ty', 'inliers']); w.writerows(rows)
print(out)
