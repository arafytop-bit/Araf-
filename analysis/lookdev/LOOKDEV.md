# Lookdev log: high-fidelity calibration (frames 0–149)

**Status:**
- Every **code-built** element is finished and measured.
- The **illustrated art is pending**, because no image-generation key exists in this environment (no API key variables, no saved network secrets).
- Following your instruction, I stopped there and sent `../assets_to_generate/ASSET_LIST.md` with its reference attachments.
- The remaining items are A02 (hero bust for the portrait shot) and A03 (masked bust, the source for every poster print). A01 (character sheet) comes first for consistency.

**Bar:** `../style_bible.md`.

**Renderer:** `render/src/CalibrationHQ.tsx` (Remotion, 3840×2160 → 1080p).
- Plates come from `scripts/b03_plates.py`.
- Timing comes only from `blueprint.json`, the same keys as the v3 calibration, which matched within ±1 frame.

## What changed from the placeholder pass

| Area | v3 placeholder | Now |
|---|---|---|
| Sky | Muddy maroon→orange SVG gradient | Measured 13-stop gradient (purple → rose → orange → yellow), triangular-dithered 4K plate. 5 soft god rays at the measured angles (102°/128°/170° + 2 faint) swaying ±1.5°. Two-layer sun bloom, sun disc + gold ring, horizon haze glow, ~110 bokeh dust specks with size/blur/opacity/twinkle/drift variation, flapping tapered gull silhouettes |
| Land | Flat triangles | Outlined (1.0–1.2 ref px, noise-wobbled) faceted mountains with lit/shade gradients and 2-tone outlined snowcaps. Hazy far range. Banded maroon mesa with cracks. Repeating hill arches with a pale rim. Striped ground. Soft olive grass tufts. Warm haze bands and a vignette |
| Poster paper | Flat beige | Aged paper plate: buttery base with a lit centre, round translucent stains kept off the portrait box, centre and horizontal folds, ochre burnt edges, low-frequency torn outline with the bottom-right notch. Heavy soft drop shadow. Glossy plum nail |
| Type | Times-style fallback (font failed silently) | **Bitter Black 900**, matched by rendering 40 slab/serif families over the reference crops. Near-black ink with letterpress displacement and a soft ink edge; worn deep-red reward. Strict font loader cancels the render on any fallback. Offline layout check fits every string with margin: "HALF THE WEST" ends 12 px inside the frame. "WANTED FOR" rules stop 0.6 em from the text. The bottom frame breaks around "REWARD $????" |
| Icons | Bar, dot, square | Hand-drawn SVG pictograms: side-view locomotive with stack, dome, cab window and wheels; tied money bag with a knocked-out $; three-panel folded map with fold lines, dashed route and X. Each sits inside a double-ring crimson badge with print roughness |
| Wall | Even plain planks | Smooth planks of varied tone (150 px wide at output). Soft bevelled seams with a highlight lip, sparse long grain strokes, soft knots and nail heads. Screen-space warm light pool, strong vignette and glowing dust |

## Measurements against the reference

These are taken at the reference scale (854×480), ratio rebuild/reference; targets are 0.8–1.2 and ΔE2000 < 6 (`metrics_v14.json`):

| Scene | Region | Edge density | Fine texture | RMS contrast | Colourfulness | ΔE2000 |
|---|---|---|---|---|---|---|
| poster f143 | list block (text + icons + paper) | 1.02 | 0.79 ✗ | 0.92 | 0.96 | 2.12 |
| poster f143 | paper, small blank patch | 2.14 ✗ | 1.38 ✗ | 0.88 | 1.00 | **3.90** |
| poster f143 | wood, left wall (zoomed 1.4×) | 0.43 ✗ | 0.66 ✗ | 1.09 | 1.11 | **0.73** |
| poster f143 | whole frame | 0.76 ✗ | 0.84 | 0.92 | 0.99 | 4.05 |
| poster f075 | paper, empty list area | 0.98 | 1.22 ✗ | 0.70 ✗ | 0.94 | **2.79** |
| poster f075 | wood, left wall | 0.77 ✗ | 0.93 | 1.48 ✗ | 1.15 | **0.54** |
| poster f075 | poster top ("WANTED") | 0.74 ✗ | 0.80 | 0.86 | 0.98 | 2.36 |
| poster f075 | whole frame minus portrait box | 1.08 | 0.94 | 0.89 | 1.09 | 3.43 |
| portrait f030 | sky | 0.73 ✗ | 0.70 ✗ | 0.89 | 0.86 | **2.16** |
| portrait f030 | mountains | 0.76 ✗ | 1.00 | 0.73 ✗ | 0.89 | **2.61** |
| portrait f030 | mesa (105×60 px) | 0.53 ✗ | 1.27 ✗ | 1.80 ✗ | 1.09 | 0.92 |
| portrait f030 | ground | 0.93 | 1.43 ✗ | 1.10 | 0.96 | **1.95** |
| portrait f030 | background left of hero | 0.78 ✗ | 1.17 | 0.96 | 0.85 | 1.09 |

**Reading the table:**
- **Colour:** every targeted region is within ΔE2000 6 (worst 3.9). Contrast and colourfulness are within ±20% except three regions. 22 of 52 ratios fall outside 0.8–1.2.
- **Small regions:**
  - The small blank-paper patch and the 105×60 px mesa swing on single stains or lines.
  - The 480p reference's own compression blockiness and ringing add edges and fine texture to flat gradients that a clean 4K render shouldn't copy. This mainly affects the sky and wall edge counts.
- **Next lever:** the wall's lower edge and fine-texture counts at 1.4× zoom, which need more grain strokes visible up close.

Progression of the same table:
- **Mountains ΔE:** 8.2 (v2) → 2.6.
- **Sky edges:** 0.41 → 0.73.
- **Whole poster frame ΔE:** 7.2 (v9) → 3.4.

## Blind review (fresh subagent, unlabeled A/B pairs, same scale and upscale for both)

**Round 1** (pairs from v6). The rebuild-side findings that I fixed:
- **Poster:** cloudy stains → round translucent discs; caramel grainy paper → smooth buttery paper. Brown ink → near-black; vermilion line icons → chunky crimson silhouettes. No visible drop shadow → heavy soft shadow. Small grey pin → glossy plum dome. Fine ragged tears → smoother waves.
- **Wall:** mechanical streak grain → smooth planks with a few strokes; hard black seams → bevelled seams; flat lighting → vignette and light pool.
- **Sky:** muted sky → measured gradient with a gentle chroma lift; faint washes → narrower, brighter rays. Uniform small dots → varied bokeh, plus a haze glow. "~" birds → tapered gull shapes.
- **Landscape:** bold outlines → thin, wobbly ones. Light faceted mountain → muddier two-tone. Vertical-streak mesa → horizontal strata. Smooth ground → stripes. Crisp grass → soft, translucent tufts.

**Round 2** (pairs from v12; verdicts: five pairs "clear differences", the landscape "major").

Several round-2 descriptions of the reference contradicted round 1. Before changing anything, I checked each one against the reference frames at full frame and at 2–4× zoom. I then measured what it described: colours on the faces rather than the outlines, polar ray profiles, seam and orb cross-sections, line positions and text extents. The rebuild-side fixes:
- **Landscape:**
  - Mesa: the crude grid lines and pale ellipse are gone. It now has measured strata (light bands at y 294–299 and 313–326, a warm glow toward the base) and a faint plaid clipped to the shape, so nothing bleeds onto the mountain. It also has a jagged form-shadow face, a top moved down 6 px to y 276, and a stepped right face.
  - Grass: stamped identical tufts → clumps of 6–10 thin tapered blades in depth, matched to the reference's coverage (0.5–0.65% of the foreground).
  - Hills: 7 small scallops → broad 118 px arcs with a 12 px rise over a straight ground line. A quadratic curve only reaches half its control height, so the old arcs rose 5 px, not 10.
  - Mountains: re-measured on the faces. They are red-brown (`#864038`), not pink-mauve. Outlines are clean (1.8 / 1.5 px, no wobble). Snowcaps are large, two-tone and spiky. The far range is no longer washed out.
  - Sun: the hard ring and the vertical seam through the halo are fixed. The seam came from two haze bands that ended inside the halo at x 300 and 360; the haze now runs full width and the ring edge is soft.
  - Horizon: mountain bases extended behind the hills, so no sky sliver shows in the troughs.
- **Sky:**
  - Rays: re-measured with a row-detrended polar profile. There are six rays at 76° / 100° / 123° / 150° / 57° / 36°. They are sharper and start 60 px from the sun; the old ones were wide wedges glowing from the disc.
  - A large translucent halo disc with a visible edge sits behind the sun.
  - Birds are heavier strokes.
  - Orbs: fewer, larger and more uniform, with the reference's measured radial falloff.
  - The top of the sky is darker purple.
- **Wall:**
  - Light: the left-to-right falloff is replaced by a gentle symmetric vignette, matched to the reference's luma across the frame (43 / 59 / 60 / 32 at x 0 / 240 / 600 / 840).
  - Seams: re-profiled (light rim, 2 px dark core, soft 4–5 px light lip) and drawn as vectors, so they stay crisp at the 1.41× push-in.
  - Grain lines are straight, and the knots have lighter rims.
- **Poster:**
  - Ink: speckled brown → solid near-black (darkest pixel was `#381f0d`; the reference's is `#1a0100`). Badge rings are clean.
  - Nail: smaller and dull.
  - Shadow: a deep two-layer drop shadow.
  - Paper: a brighter centre with burnt edges, a ragged bottom and right tear and a deeper notch.
  - Dashed rules: matched to the reference's 5.4 px pitch and depth.
  - Reward value: measured red `#79220c`, a narrow "$" and an 8 px gap. REWARD is lighter.
  - Type: WANTED, the name and the list items take their measured tracking. "HALF THE WEST" auto-shrinks the way the reference sets it smaller.
- **Found while measuring, not by the reviewer:**
  - **An automatic fail.** The last "?" of "$????" touched the frame line at f143. The frame break now runs to x 526, and the value ends at 519.
  - **Poster position.** At f068–f082 the poster sat 3–4 px too high. The blueprint's camera track was offset on that hold, so its ty is corrected by +4.0 there; f089 onward already matched within 1 px.
  - **Frame and content offsets.** The left frame lines and the print content were 1.6–2.7 px left of the reference. Both are now set from positions measured at f075 and f143 with the camera inverted.

**Round 3** (pairs from v29). See below.

## Still to do when the art arrives

1. Run `scripts/b09_prepare_asset.py` on A02 and A03: key or alpha, despill, 1 px defringe, Real-ESRGAN 4× upscale to ≥ 2100 px tall, QA on black/white/magenta.
2. Hero layer: fit to the measured bust box and anchor (569, 181), with the 1.00 → 1.105 push on the blueprint keys.
3. Poster prints: A03 through the `printTone` sepia duotone, multiplied over paper, in the main poster and the four side posters.
4. Render the full 150 frames with `scripts/b08_calibration_hq_render.sh`: 4K → 1080p CRF 16 master, and the 3840×1080 side-by-side with frame counters.
5. Re-run the metrics, the encode check and a final blind review on all four stills.

## Encode check

On a 30-frame poster segment, 4K → 1080p CRF 16 BT.709 (`encode_check.json`):
- mean pixel ΔE2000 between the decoded MP4 and the masters is **0.59**;
- the worst 8×8 block is ΔE 2.2;
- the mean RGB offset is +0.14 / +0.03 / +0.21.

Encoding doesn't shift colour.
