"""Style-bible measurements from native 854x480 frames and the 1280x720 channel thumbnail (style study only).

Outputs analysis/lookdev/style_measurements.json. Output-size conversions: 480p -> 1080p x2.25, 720p -> 1080p x1.5.
"""
import json, numpy as np, cv2
from sklearn.cluster import KMeans
F = lambda f: cv2.imread(f'work/frames/f_{f:05d}.png')
T = cv2.imread('work/ref_hd/thumb_WKJKhnOD65o.jpg')
hexc = lambda c: '#%02x%02x%02x' % tuple(int(v) for v in c[::-1])  # BGR -> hex
out = {}

def stroke_widths(img, box, thr=45):
    x0, y0, x1, y1 = box
    g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    m = (g < thr).astype(np.uint8)
    dt = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    # ridge = local maxima of the distance transform along the stroke centre
    dil = cv2.dilate(dt, np.ones((3, 3), np.uint8))
    ridge = (dt > 0.9) & (dt >= dil - 1e-6)
    w = 2*dt[ridge]
    return dict(n=int(ridge.sum()), p25=round(float(np.percentile(w, 25)), 2), median=round(float(np.median(w)), 2), p75=round(float(np.percentile(w, 75)), 2), p90=round(float(np.percentile(w, 90)), 2), max=round(float(w.max()), 2))

# 1. outlines: character in thumbnail (face+hat+torso) and in frame 30; mountains outline in frame 30; poster frame lines f75
sw_t = stroke_widths(T, (730, 140, 1240, 720), 40)
sw_f = stroke_widths(F(30), (330, 30, 854, 480), 40)
sw_m = stroke_widths(F(30), (100, 220, 330, 330), 60)
out['outlines'] = dict(character_thumb_720p=sw_t, character_f30_480p=sw_f, mountains_f30_480p=sw_m,
                       character_at_1080p_px=dict(thin=round(sw_t['p25']*1.5, 1), typical=round(sw_t['median']*1.5, 1), heavy=round(sw_t['p90']*1.5, 1)),
                       mountains_at_1080p_px=dict(typical=round(sw_m['median']*2.25, 1), heavy=round(sw_m['p90']*2.25, 1)))
# outline colour: darkest 2 % pixels of character region
reg = T[150:720, 740:1240].reshape(-1, 3); L = reg.mean(1)
out['outline_color'] = hexc(np.median(reg[L < np.percentile(L, 2)], 0))

# 2. shading tones (k-means) per material in the thumbnail
def tones(img, box, k, mask_fn=None):
    x0, y0, x1, y1 = box; px = img[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
    lum = px.mean(1); px = px[(lum > 35)]  # drop outlines
    km = KMeans(n_clusters=k, n_init=4, random_state=0).fit(px)
    cnt = np.bincount(km.labels_, minlength=k); order = np.argsort(km.cluster_centers_.mean(1))
    return [dict(hex=hexc(km.cluster_centers_[i]), share=round(float(cnt[i]/cnt.sum()), 3)) for i in order]
out['tones'] = dict(face_skin_and_beard=tones(T, (900, 300, 1060, 470), 6), hat=tones(T, (760, 160, 1180, 280), 4),
                    vest=tones(T, (840, 560, 1000, 700), 4), shirt_sleeves=tones(T, (1180, 540, 1280, 700), 4), bandana=tones(T, (880, 470, 1030, 560), 4))
# 3. scene palettes (480p)
def pal(img, box, k=6):
    x0, y0, x1, y1 = box; px = img[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
    km = KMeans(n_clusters=k, n_init=4, random_state=0).fit(px); cnt = np.bincount(km.labels_, minlength=k); order = np.argsort(-cnt)
    return [dict(hex=hexc(km.cluster_centers_[i]), share=round(float(cnt[i]/cnt.sum()), 3)) for i in order]
f30 = F(30)
out['palette'] = dict(sky_vertical=[hexc(np.median(f30[y:y+6, 0:250].reshape(-1, 3), 0)) for y in range(0, 230, 25)],
                      sun_disc=hexc(np.median(f30[280:296, 322:340].reshape(-1, 3), 0)), sun_ring=hexc(np.median(f30[250:258, 322:340].reshape(-1, 3), 0)),
                      mountains=pal(f30, (110, 225, 260, 330), 6), mesa=pal(f30, (0, 270, 110, 330), 4), ground=pal(f30, (0, 340, 300, 480), 5),
                      paper=pal(F(75), (300, 290, 560, 410), 5), wall=pal(F(75), (0, 0, 260, 480), 5), poster_ink=pal(F(75), (315, 50, 545, 92), 3),
                      icons_badge=pal(F(143), (275, 165, 320, 300), 4), night_scene=pal(F(1660), (0, 0, 854, 480), 6), interior_wood=pal(F(600), (0, 0, 854, 480), 6))
# 4. sky gradient as HSV per row (saturation / hue progression)
hsv = cv2.cvtColor(f30, cv2.COLOR_BGR2HSV)
out['sky_rows_hsv'] = [dict(y=y, h=int(np.median(hsv[y:y+5, 0:200, 0])*2), s=int(np.median(hsv[y:y+5, 0:200, 1])), v=int(np.median(hsv[y:y+5, 0:200, 2]))) for y in range(0, 240, 20)]
# 5. bloom profile around the sun (luma vs radius), sun centre estimate
g = cv2.cvtColor(f30, cv2.COLOR_BGR2GRAY).astype(np.float32)
ys, xs = np.where(g[200:330, 250:420] > 245); cy, cx = 200+ys.mean(), 250+xs.mean()
yy, xx = np.mgrid[0:480, 0:854]; R = np.hypot(yy-cy, xx-cx)
mask = (xx < 400) & (yy < 300)  # left/upper side, avoid character
prof = [dict(r=r, luma=round(float(g[(R >= r) & (R < r+5) & mask].mean()), 1)) for r in range(0, 200, 10)]
out['sun'] = dict(centre_px_480=[round(cx, 1), round(cy, 1)], centre_pct=[round(cx/854*100, 1), round(cy/480*100, 1)], disc_radius_px_480=round(float(np.sqrt((g[200:330, 250:420] > 245).sum()/np.pi)), 1), luma_profile=prof)
# 6. dust specks: small bright blobs (top-hat) in sky over frames 0..60, tracked for drift
def specks(img):
    gg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th = cv2.morphologyEx(gg, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lab, st, cen = cv2.connectedComponentsWithStats((th > 18).astype(np.uint8))
    res = []
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        if 1 <= a <= 40 and cen[i][1] < 300 and cen[i][0] < 380:
            res.append((cen[i][0], cen[i][1], a, int(th[lab == i].max())))
    return res
counts = []; tracks = []; prev = None
for f in range(0, 61, 2):
    s = specks(F(f)); counts.append(len(s))
    if prev is not None:
        for (x, y, a, p) in s:
            d = [np.hypot(x-px, y-py) for (px, py, _, _) in prev]
            if d and min(d) < 6:
                j = int(np.argmin(d)); tracks.append(((x-prev[j][0])/2, (y-prev[j][1])/2))
    prev = s
tr = np.array(tracks) if tracks else np.zeros((1, 2))
sz = [a for f in (0, 30, 60) for (_, _, a, _) in specks(F(f))]; pk = [p for f in (0, 30, 60) for (_, _, _, p) in specks(F(f))]
out['dust_specks_sky_region'] = dict(count_per_frame_median=float(np.median(counts)), area_px_480_median=float(np.median(sz)), peak_contrast_median=float(np.median(pk)),
                                     drift_px_per_frame_480=dict(dx_median=round(float(np.median(tr[:, 0])), 3), dy_median=round(float(np.median(tr[:, 1])), 3), speed_p90=round(float(np.percentile(np.hypot(tr[:, 0], tr[:, 1]), 90)), 3)))
# 7. vignette profile (frame 30 + frame 75): mean luma by normalised radius
def vig(img):
    gg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32); r = np.hypot((yy-240)/240, (xx-427)/427)
    c = gg[r < 0.3].mean()
    return [round(float(gg[(r >= a) & (r < a+0.1)].mean()/c), 3) for a in np.arange(0, 1.4, 0.1)]
out['vignette_luma_ratio_by_radius'] = dict(f75_wall=vig(F(75)), f600_interior=vig(F(600)), f1660_night=vig(F(1660)))
# 8. grain: residual std in flat sky after 5x5 median (compression limits this)
sky = cv2.cvtColor(f30, cv2.COLOR_BGR2GRAY)[20:120, 20:200].astype(np.float32)
out['grain_residual_std_480'] = round(float((sky - cv2.medianBlur(sky.astype(np.uint8), 5)).std()), 2)
# 9. wall planks: gap positions from dark columns (f75, x<270)
w = cv2.cvtColor(F(75), cv2.COLOR_BGR2GRAY)[60:420, 0:275].astype(np.float32)
colmean = w.mean(0); smooth = cv2.GaussianBlur(colmean.reshape(1, -1), (1, 31), 0).ravel() if False else np.convolve(colmean, np.ones(25)/25, 'same')
dips = [x for x in range(3, 272) if colmean[x] < smooth[x]-8 and colmean[x] == colmean[max(0, x-3):x+4].min()]
gaps = np.diff(dips) if len(dips) > 1 else []
out['wall'] = dict(gap_x_px_480=dips, plank_width_px_480=[int(v) for v in gaps], gap_luma_drop=round(float(np.median([smooth[x]-colmean[x] for x in dips])), 1) if dips else None,
                   plank_tone_luma=[round(float(colmean[a+5:b-5].mean()), 1) for a, b in zip(dips[:-1], dips[1:])])
# 10. paper stains: low-frequency luma variation on blank paper (f75 region)
pp = cv2.cvtColor(F(75), cv2.COLOR_BGR2GRAY)[300:405, 300:560].astype(np.float32)
low = cv2.GaussianBlur(pp, (0, 0), 6)
out['paper'] = dict(stain_luma_std=round(float(low.std()), 2), stain_luma_range_p5_p95=round(float(np.percentile(low, 95)-np.percentile(low, 5)), 1),
                    base=hexc(np.median(F(75)[300:405, 300:560].reshape(-1, 3), 0)))
# edge darkening of the poster: luma profile from the left poster edge inward (row band y 150-400)
row = cv2.cvtColor(F(75), cv2.COLOR_BGR2GRAY)[150:400, 278:330].astype(np.float32).mean(0)
out['paper']['edge_profile_luma_from_left_edge'] = [round(float(v), 1) for v in row[::3]]
# 11. icon badge geometry at f143 (camera scale 1.406): red ring radii
I = F(143)[160:205, 270:320]; b, gch, r = [I[..., k].astype(int) for k in range(3)]
red = ((r-gch > 50) & (r > 110)).astype(np.uint8)
ys, xs = np.where(red)
out['icon_badge_f143'] = dict(red_hex=hexc(np.median(I[red > 0], 0)), outer_diameter_px=int(xs.max()-xs.min()+1), at_camera_scale=1.406,
                              outer_diameter_px_at_scale1=round((xs.max()-xs.min()+1)/1.406, 1))
json.dump(out, open('analysis/lookdev/style_measurements.json', 'w'), indent=1)
print(json.dumps(out, indent=0)[:6000])
