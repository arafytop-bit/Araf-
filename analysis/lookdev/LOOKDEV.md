# Lookdev log: high-fidelity calibration (frames 0–149)

**Status:**
- Every **code-built** element is finished, measured and through three blind-review rounds; a fourth is checking the final state.
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
| Sky | Muddy maroon→orange SVG gradient | Measured 14-stop gradient (dark purple → crimson → orange → yellow) as a triangular-dithered 4K plate. The static glows are computed in float and baked in: corner darkening, haze glow, a large translucent halo disc and a wide bloom (no 8-bit SVG gradient rings). Six soft god rays at the measured angles (76°, 100°, 123°, 150° faint, 57°, 36°) that start 60 px from the sun and sway ±1.2°. Sun disc and saturated ring at the re-measured centre. Bokeh orbs (flat halo disc plus core, measured peak), denser in the open sky left of the hero. Three thin flapping gull strokes |
| Land | Flat triangles | Red-brown faceted mountains (face colours measured) with clean 1.5–1.8 px outlines, narrow tip spikes and large two-tone spiky snowcaps. The far range is the same family. Mesa with measured strata, irregular plaid and a jagged form-shadow face, clipped to its shape. Broad hill arcs with a bright pale rim. Soft striped ground with faint vertical striations. Grass clumps of thin tapered blades, in depth. Warm haze veil and out-of-focus orange blobs at the bases |
| Poster paper | Flat beige | Aged paper plate: even left-to-right light falling off toward the bottom; burn deep along the bottom and narrow at the sides; warm translucent stains matched to the reference's stain/paper ratios; centre and horizontal folds; a smooth torn outline with a notch over a compact two-layer drop shadow. Dark nail dome with a soft highlight |
| Type | Times-style fallback (font failed silently) | **Bitter Black 900**, matched by rendering 40 slab/serif families over the reference crops. Tracking is solved from the measured word widths, and "HALF THE WEST" auto-shrinks as in the reference. Solid near-black ink with a slight letterpress edge. Reward value in measured red, with a narrow "$" and the measured gap. A strict font loader cancels the render on any fallback, and `b07_poster_layout.py` fails on any overflow. The bottom frame breaks around "REWARD $????" |
| Icons | Bar, dot, square | Hand-drawn SVG pictograms: side-view locomotive, tied money bag with a knocked-out $, three-panel folded map with a dashed route and X. Each sits small inside a clean double-ring badge with a cream gap |
| Wall | Even plain planks | Rust-brown planks (150 px at output) with sparse straight grain, faint knots and nail holes. Vector seams follow the measured cross-section (light rim, 2 px core, soft lip) and stay crisp at the push-in. An elliptical vignette fitted to the reference's light map sits under the main poster. Weak warm pool, and bokeh dust |

## Measurements against the reference

These are taken at the reference scale (854×480), as the ratio rebuild/reference. Targets are 0.8–1.2 and ΔE2000 < 6 (`metrics_v37.json`; final state after three blind-review rounds).
- **Edge density:** Canny averaged over four threshold pairs. A single 60/150 pair proved unstable: a 5-level change in a wall seam flipped it from 1.01 to 0.24. The single-pair values are still in the JSON.
- **Measurement boxes:** keep off the pending character art and the reference character.

| Scene | Region | Edge density | Fine texture | RMS contrast | Colourfulness | ΔE2000 |
|---|---|---|---|---|---|---|
| poster f143 | list block (text + icons + paper) | 0.99 | 1.01 | 0.96 | 1.04 | **1.84** |
| poster f143 | paper, small blank patch (82×37 px) | 0.00 ✗ | 0.64 ✗ | 1.26 ✗ | 1.18 | **5.94** |
| poster f143 | wood, left wall (zoomed 1.4×) | 0.95 | 0.80 | 0.94 | 1.06 | **1.64** |
| poster f143 | whole frame | 0.79 ✗ | 1.00 | 1.03 | 1.04 | 1.65 |
| poster f075 | paper, empty list area | 0.89 | 0.99 | 0.94 | 1.07 | **2.24** |
| poster f075 | wood, left wall | 0.99 | 1.12 | 1.03 | 1.03 | **1.59** |
| poster f075 | poster top ("WANTED") | 0.87 | 1.06 | 1.00 | 1.08 | 2.12 |
| poster f075 | whole frame minus portrait box | 0.91 | 1.11 | 0.98 | 1.07 | 0.47 |
| portrait f030 | sky | 1.23 ✗ | 0.83 | 0.86 | 0.93 | **2.28** |
| portrait f030 | mountains | 0.86 | 1.12 | 0.88 | 0.89 | **2.43** |
| portrait f030 | mesa (105×60 px) | 0.63 ✗ | 0.97 | 1.03 | 0.93 | 2.13 |
| portrait f030 | ground | 1.02 | 1.17 | 0.94 | 0.92 | **1.78** |
| portrait f030 | background left of the hero | 0.91 | 1.20 | 0.92 | 0.92 | 1.50 |

**Reading the table:**
- **Colour:** every targeted region is within ΔE2000 6. Across whole frames, ΔE is 0.47 (f075) and 1.65 (f143). The worst region is the 82×37 px blank-paper patch at 5.94: one of my stains now lies across it, while the reference's patch is mostly clean paper.
- **Ratios:** 6 of 52 fall outside 0.8–1.2 (v14: 22 of 52).
  - **Blank-paper patch:** it is 82×37 px, and its result depends on where a random stain falls. The reference has only a stain edge inside it; mine is under a stain. The larger f075 paper region carries the paper check and passes on every ratio.
  - **Mesa:** the reference has only about 15 edge pixels in this region, so one line swings the ratio.
  - **Sky edges (1.23):** the bokeh orbs are slightly more numerous than in the reference.
  - **f143 whole frame (0.79):** just below the band.
  - **f075 list-area contrast:** now fixed, 0.66 → 0.94. The stains were re-matched to the reference's stain-to-paper ratio per channel: 0.90/0.85/0.76 in the reference, now 0.93/0.86/0.78 (was 0.93/0.90/0.86).

Progression of the same measurements:
- **Mountains ΔE:** 8.2 (v2) → 2.6 (v14) → 2.4.
- **Whole poster frame ΔE:** 7.2 (v9) → 3.4 (v14) → 0.47.
- **Ratios outside the band:** 22 (v14) → 6.

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

**Round 3** (8 pairs from v29, including two new ones: the reward line at f143 and the sun. Verdicts:
- "minor": the sun;
- "clear": the list, the poster top, the wall, the sky and the landscape;
- "major": the poster bottom and the reward line. In both, the main item is the frame break around REWARD, which is an intended difference.

As in round 2, I measured every claim before acting. Several descriptions were again reversed relative to the reference: the paper's bottom burn, the pin, the knot rims and the bottom tear. In each case the measurement decided. The rebuild-side fixes:
- **Wall:**
  - Light: the reference wall is darker at the top, bottom and right than mine was (by 10–29 luma). A 2D block fit gives an **elliptical vignette** centred left of the poster at (365, 252), radii 472 × 266, with an RMS fit error of 0.05.
  - Layering: the vignette is drawn in screen space **beneath the main poster**. The reference poster keeps its own lighting; a full-frame vignette darkened its paper by up to 27% (ΔE 13 at the top).
  - Texture: half the grain strokes and half the mottling. Subtler knot rims.
  - Orbs: about 2.5× more on the wall, each a halo disc with a core.
- **Sky:**
  - Orbs: rebuilt as bokeh (a soft flat halo disc plus a core at the measured peak, +63…+78), with a third of them in the open sky left of the hero.
  - Rays: softer (blur 5.5) and slightly narrower. The 150° band is almost gone.
  - Birds: thinner strokes.
  - Sun: re-measured as centred 3.5 px lower with radius 36, and a more saturated ring (`#fec26a`).
  - Banding: the static glows were moved out of 8-bit SVG gradients into the float, dithered sky plate (see below).
- **Landscape:**
  - A warm haze veil and out-of-focus orange blobs at the bases.
  - Faint vertical striations across the ground bands.
  - Paler grass, with the back clumps softened.
  - Mesa: an irregular vertical plaid and stronger strata.
  - Hill rim: brighter and wider.
  - Mountains: slightly darker and redder (body was `#8b463b`, reference `#823b36`), with a narrow tip spike and a 1.5 px outline.
- **Poster:**
  - Paper: the bottom edge is 6.5 px higher, matching the reference's y 452–456 at f075. The bottom tear is a smooth wave rather than ragged, over a compact, near-black shadow band (reference luma ~33 just below the edge).
  - Burn: deep along the bottom and narrow at the top and sides.
  - Lit centre: even left to right, falling off toward the bottom.
  - Pin: a darker dome, a thicker outline, a soft highlight and a light ring.
  - REWARD sits 3.5 px higher and the value 1.5 px lower, at 95% size; both measured.
  - Badges: smaller pictograms and a wider ring gap.
- **Not copied:** the light halo and dark fringe around the reference's red "$????" are 4:2:0 chroma bleed from its 480p encode, not design.

**Banding (automatic fail) found while checking round 3:**
- **The problem:** at 25× contrast, the sun glows showed 1-level contour rings. Chrome renders SVG radial gradients in 8 bits.
- **First attempt:** a ±1.5-level dither over the whole frame did not remove them. A coherent 1-level ring survives that once the 2× downscale averages the noise away.
- **The fix:** every static radial glow and vignette is now computed in float and dithered in `b03_plates.py`. In the portrait, the corner darkening, haze glow, halo disc and wide bloom are baked into the sky plate, and the tight sun bloom and sky vignette are separate overlay images. In the wall shot, the warm pool and vignette are overlay images.
- **Result:** the radial profile inside the sun disc now steps by at most 0.4 levels, and the high-pass check shows no rings. The global dither layer stays in as a safety net.

**Expected differences that remain** (round 3, after fixes):
- **Missing art:** the character and the poster prints. A01–A03 are pending.
- **Different text:** the character name and wording, once Phase 2 supplies them.
- **The broken bottom frame line around REWARD:** in the reference the line runs through the text, which your rules forbid.
- **Exact stain and particle placement:** it is random by design, not traced.
- **The reference's 480p softness and compression artefacts:** chroma bleed around red text, ringing, block noise in flat areas.

## Still to do when the art arrives

1. Run `scripts/b09_prepare_asset.py` on A02 and A03: key or alpha, despill, 1 px defringe, Real-ESRGAN 4× upscale to ≥ 2100 px tall, QA on black/white/magenta.
2. Hero layer: fit to the measured bust box and anchor (569, 181), with the 1.00 → 1.105 push on the blueprint keys.
3. Poster prints: A03 through the `printTone` sepia duotone, multiplied over paper, in the main poster and the four side posters.
4. Render the full 150 frames with `scripts/b08_calibration_hq_render.sh`: 4K → 1080p CRF 16 master, and the 3840×1080 side-by-side with frame counters.
5. Re-run the metrics, the encode check and a final blind review on all four stills.

## Full calibration render and encode check

`scripts/b08_calibration_hq_render.sh` renders frames 0–149 at 3840×2160 from the blueprint timing, with the hero and print art still pending. It then makes:
- the 1080p master: Lanczos downscale, x264 CRF 16, BT.709 TV range, with the reference audio for timing (`work/hq/final/calibration_hq_1080p.mp4`, 150 frames);
- the full-resolution side-by-side: reference 480p upscaled | rebuild, 3840×1080, with frame counters (`../calibration/calibration_hq_side_by_side.mp4`). It is reference-derived, so it is kept out of git.

Encode check, PNG masters vs the same frames decoded from the MP4 (every 5th frame, 30 frames; `encode_check_final.json`):
- mean pixel ΔE2000 **0.61**;
- worst 8×8 block ΔE **3.2**, on a thin dark rule: 4:2:0 chroma bleed. 71 of 32,400 blocks exceed 2 and the mean block ΔE is 0.33;
- mean RGB offset **+0.11 / +0.05 / +0.28**.

Encoding doesn't shift colour.
