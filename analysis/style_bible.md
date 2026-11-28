# Style bible: "Born in Lore" look

This file is the bar every asset and render is checked against.

**Sources:**
- native 854×480 frames of the reference (100–300% crops in `lookdev/ref_crops/`);
- the channel's own 1280×720 thumbnail for this video (same hero art at about 1.5× the video's detail; `work/ref_hd/`, used for style study only, never copied);
- measurements in `lookdev/style_measurements.json` and `lookdev/sun_measure.json`.

**Units:** all pixel sizes are at the **1920×1080 output** unless marked. Conversions: 480p × 2.25, 720p × 1.5. Render at 3840×2160 (2×) and downscale with Lanczos. Colours are sRGB hex.

**Limitation:** no full-resolution copy of the video is obtainable here. YouTube blocks downloads from this machine with a bot check and HTTP 429. Values marked † come from the 1280×720 thumbnail; everything else comes from 480p frames, so 1–2 px features carry about ±1 px of uncertainty at output size.

---

## 1. Overall look in one paragraph

Flat 2D cartoon illustration with **bold, warm near-black outlines**, cel shading in **3 tones per material**, sparse **hatching and texture strokes** (wrinkles, beard stubble, wood grain, paper stains), **painterly light** (gradient skies, god rays, large soft bloom, warm light pools, strong darkened corners) and **constant floating dust specks**. Shapes are clean vectors, but every surface carries a texture layer, so nothing reads as a flat fill. Text looks printed or painted, never like a clean UI font.

## 2. Line work

| Item | Width (1080p) | Colour | Notes |
|---|---|---|---|
| Character outer contour † | **8–9 px** (thumbnail median 6.4 px × 1.5; 480p frames 3.5–4 px × 2.25) | `#130b01` | Tapers to 40–60% at the tips of hair strands, fingers, collar points and brim ends. Never uniform like a vector stroke |
| Character interior lines † (nose, brows, lips, ears, fabric folds) | **3–5 px** | `#130b01` | Often broken into 2–3 strokes. Lines end in a taper, not a round cap |
| Hatching and wrinkles † | **2–3 px**, 10–45 px long | `#3c2717` to `#130b01` at 60–80% opacity | Groups of 2–4 parallel strokes on the forehead, crow's feet and cheek. Strokes taper at both ends |
| Beard and stubble † | 2 px hair strokes, 8–20 px long, ±20° from vertical | Lighter strokes `#9a684a`/`#c48962` over the beard base | About 60 strokes per 100×100 px of beard |
| Background shapes (mountains, mesa, props) | **4 px** for the near mountain (1.8 ref px), 3.4 px for the far range (1.5 ref px), mesa 3 px | `#130b01` (distant layers also outlined) | **Clean**, no wobble (round 2: the wobbled outline read as amateur). Snowcap bottoms carry a thin `#5a2a2c` line at 55% instead of a full outline |
| Poster frame lines | Outer **4.5 px**, inner **2.2 px**, gap 6.7 px | Ink `#1d0901` | Inset 25 px from the paper edge |
| Highlight rim lines (hill tops, brim) | 2–3 px | Lighter than the fill by about +40 L | A thin lit edge on the light-facing silhouette |

## 3. Shading and colour by material (cel shading, 3 tones + accents)

| Material | Shadow | Mid | Light | Accents |
|---|---|---|---|---|
| Skin † | `#734a37` | `#9a684a` | `#c48962` | Hat-brim cast shadow band across the eyes, multiplied `#4f3523` at ~70%. Nose-bridge and cheekbone highlights are the light tone. No blush |
| Beard and brows † | `#3c2717` | `#4f3523` | Hair strokes `#9a684a` | Brows are hair strokes, not a flat shape |
| Hair † | Dark strand lines `#3c2717` | `#8a6438` | `#c8a060` | Separate locks with pointed tips, each outlined |
| Eyes † | Upper-lid line 4 px `#130b01` | Iris `#7a96a8` | Sclera `#cbd5db` | One white specular dot (3–4 px) per eye. Squinting heavy lids |
| Hat † | `#1e1a17` | `#302a25` | Brim-top rim `#5a4a3e` | Band `#68513f` with braided texture strokes; small metal concho |
| Leather vest † | `#352a2c` | `#4e3a2c` | `#755538` | Dashed stitching `#c4a778`, 2.5 px dashes, 6 px period, 8 px inside the edge |
| Shirt (pinstripe) † | `#495461` | `#5a6b7a` | `#7d8e9c` | Pinstripes 1.5 px `#495461` every 9 px, following the fold direction |
| Bandana † | `#2a2e3a` | `#3b4150` | `#5a6978` | Knot with 2–3 fold lines, tapered tails |
| Satchel strap, buckle † | `#3a2416` | `#5a3a22` | `#8a5a32` | Brass buckle `#c49a48` with dark outline, dashed stitching |

**Shadows are warm.** Shadow tones shift toward red-brown (+5–10° hue toward red, −30% value), never grey. **Highlights** are small hard-edged shapes, not gradients.

## 4. Light

- **Portrait scene:** the key light is the low sun at frame-left behind the hero (sun centre **38.5% x, 55.7% y**). The hero is front-filled with warm light. The hat casts a hard shadow band across the eyes. Rim light is mostly absent; the dark outlines separate figure from ground.
- **Interiors and props:** a warm overhead pool at the frame centre, falling off to very dark corners.
- **Night:** cool navy ambient (`#0d173c`) with warm lamp pools and bloom.

## 5. Palettes per scene (measured)

- **Portrait: sky.** Vertical gradient top → horizon (every 25 px at 480p): `#412334 #522634 #6a3036 #833c38 #9c473a #b5533c #c76340 #d96f40 #e47b44 #e78844`. Near the sun: `#f0964e` → `#fbb15c`. Hue runs 322° (purple) through magenta and 0° to 24° (orange); saturation 135 → 183/255; value 54 → 220/255.
  - Sky top `#3d1d2e` (darker than the earlier stop). Near the sun the sky stays **vivid orange** (`#f9a959` at (250, 230)), never beige: sun glows are saturated orange, screen-blended. Sun disc `#feecc3`, centre **(324.6, 288.9)**, radius **36** at 480p; ring `#fec26a` (re-measured in round 3, more saturated than the bloom-washed `#fedd90`), extending to r ≈ 50 with a soft outer falloff.
- **Portrait: land.**
  - Mountains (measured at f30 on the faces, not the outline): lit face `#864038` → `#a0563d` toward the base, shade face `#7b392f` → `#9c5338`; whole-body median `#823b36` (hue 6°). Each peak ends in a narrow spike. Red-brown burgundy, **not** pink-mauve; the far range is the same family, only slightly lighter, and is **not** washed out by haze.
  - Snow: lit `#e5beb4`, shade `#bc9898`. **Large two-tone caps** covering the top quarter to third of each peak, with 2–3 deep spikes (≈ 20 px at 480p) on the bottom edge.
  - Mesa: flat top at y 276 (480p), right face nearly vertical at x ≈ 125, then flaring to x ≈ 150 at the base. Dark bands `#4b170e`–`#551a12`, light strata `#5b2113`–`#632618` at y 294–299 and 313–326, warm glow `#6c321c` toward the base. Face right of x ≈ 78 is a uniform form-shadow `#501913` with a jagged boundary. A faint plaid of vertical lines every 9 px.
  - Hills: broad arcs ≈ 118 px wide, rising ≈ 12 px (troughs y 367, apexes ≈ 355 at 480p), pale rim `#d8a090`, over a straight dark ground line.
  - Ground strata: `#7b4125 #5f2f18 #44210c`, light streak `#a56040`; soft irregular stripes 5–9 px tall.
  - Grass: clumps of 6–10 thin tapered blades, dark olive root → `#b8a854` → pale tips `#f8f0c4`. Front clumps 15–22 px tall at 480p, back clumps 5–8 px and dimmer; about 0.65% of the foreground area.
- **Poster and wall.**
  - Paper base `#e6c181`; stains `#deb876 #d0a865`; light patches `#f1d294`; dark worn `#7c561b`.
  - Ink `#1d0901`; red ink `#9c330a` (badges) / `#a3281c` (reward); badge interior `#efbb82`.
  - Wood `#733911 #67320e #5b2b0b #4e240a #401b06`.
- **Other scenes:** night-town and interior-wood palettes are in `style_measurements.json`.

## 6. Atmosphere

| Effect | Spec |
|---|---|
| Sun | Disc radius **82 px** (36.5 px at 480p) including a 10 px gold ring `#ffd47c` with a soft outer edge. Disc `#feedc5`, flat with no texture. Behind it, a **large translucent halo disc** (r ≈ 108 px at 480p) with a visible soft edge |
| Bloom | Luma 240 at the centre → 204 at 0.9 r → 193 at 1.3 r → 172 at 2.8 r → sky level (≈130) at about 3.8 r. A two-layer halo: a tight one (1.4 r) and a wide one (4 r), screen-blended |
| God rays | Re-measured with a polar brightness profile around the sun at f30 (row-detrended): rays at **76°** (wide, ≈ 12° FWHM), **100°** and **123°** (narrow, ≈ 5–6°), a faint one at 150°, and two more at **≈ 57° and 36°** that show above the hero's hat. Peaks +10…+12 luma. They start ≈ 60 px from the sun and stay strong to the top edge (they are not wedges glowing from the disc). Slow sway ±1.2° over 3 s |
| Haze | Each mountain layer further back is lighter and less saturated: far range +18% value / −25% saturation vs mid range. A warm haze band `#f0964e` at 25% sits along the horizon |
| Dust specks | **Bokeh orbs**: a bright core plus a soft, flat halo disc (r ≈ 5–7 px at 480p, visible rim). About **20 orbs** (> +12 luma) in the open sky, most of them left of the hero; fairly uniform in size. Radial profile at 480p, peak-normalised: r1 0.75, r2 0.45, r3 0.2, then a plateau ≈ 0.1 to r6 (the disc); peak +63…+78 luma over the local background, warm white `#fff0d0`. Walls: about 10 orbs per 250 × 480 px of open wall, same construction, smaller. Drift: median 0.16 px/frame, 90th percentile 2.7 px/frame, mostly sideways with slight upward bias. Gentle twinkle (opacity ±25%, 1–3 s period) |
| Birds | 3 thin, **uneven** "m" strokes about **21 px wide at 480p** (≈ 47 px at 1080p; measured), each tilted a few degrees with unequal wings; stroke 0.8–1.2 ref px, `#3a1e22`. Flap at about 2.5 Hz, drift about 0.3 px/frame |
| Vignette | Wall scene, fitted to the reference's 2D luma map at f075 (blocks outside the poster, RMS error 0.05): **elliptical**, centre (365, 252), radii 472 × 266 (480p), darkening factor 1 − 0.435·min(t, 1.6)^1.77. It darkens the wall and side posters but **not the main poster**, which keeps its own lit-centre/burn look. Portrait: radial, centre (427, 250), 0.08 at 0.6 r → 0.42 at r = 600. Median corner/centre over the video is 0.63 |
| Warm light pool | Interiors and props: a centre ellipse +10–15% brighter, warm `#ffb060`, soft-light blend |
| Grain | Not visible (< 1.5 luma std at 480p, compression-limited). Add **≤ 1.0%** monochrome grain only to stop gradient banding, and dither every gradient. **Never build a large glow or vignette from an 8-bit SVG radial gradient**: compute it in float and dither it into an image (8-bit SVG glows left 1-level contour rings) |
| Chromatic aberration, VHS, light leaks | None |

## 7. Materials

- **Paper (posters, notebook, letters).**
  - Base `#e6c181`. Large soft **stains** (round blobs 90–200 px across, low contrast, low-frequency luma std ≈ 11, p5–p95 range 36) in `#deb876`/`#d0a865` with a few lighter patches `#f1d294`.
  - **Lit centre:** a broad light centred left of the poster's centre, at about world (400, 290). Measured as the 85th-percentile luma field at f075, which ignores stains and text: top-right corner −16%, bottom corners −12%, centre-left +8% relative to an evenly lit sheet. It is partly screen-space; the same paper point is ~4% darker at f143. Robust fit in `lookdev/paper_light_fit.json`.
  - **Burn** to a yellow ochre `#a8742e`: deep along the bottom (≈ 45 ref px), narrow along the top and sides (≈ 12 ref px; the mid-height left edge measures flat in the reference), with a light lip at the torn edge.
  - **Stains:** translucent ellipses with fairly crisp edges (≈ 1.5 px soft). Stain/paper ratio per channel in the reference: 0.90 / 0.85 / 0.76 (they darken blue most, so they read warmer, not grey).
  - A **faint centre fold**: a 2 px vertical line, `#c9a56a` at 50%, plus a faint horizontal fold.
  - **Torn edges:** gently wavy, with larger low-frequency waves along the top and a more torn right edge. The bottom is not ragged: it is a wave with a light lip, over a compact dark shadow band (luma ≈ 25–33 for ≈ 10 px below the edge, then the planks show). A **triangular notch** (≈ 40 ref px wide × 18 deep) near the bottom right. The bottom edge sits at y ≈ 452–456 at f075 (≈ 14 px below the outer frame line).
  - **Nail** at top centre: a dark grey-violet dome `#3e3846`, r ≈ 5 ref px, with a thick dark outline (1.4 px), a soft top-left highlight and a faint light ring on the paper around it.
  - **Drop shadow** on the wall: a tight deep one offset (+5, +8) ref px, blur 2.6, `#120400` at 90%, plus a wide ambient one (+3, +6), blur 9, 45%. The right and bottom edges show a clear dark band.
- **Printed ink.**
  - Text and lines are **solid near-black** (darkest pixel at 480p `#1a0100`/`#120000`), with only slight edge roughness (±0.2 px) and a few % density variation. **No speckled drop-outs** (round 2: they read as brown, speckled ink).
  - Red ink: reward value `#79220c` (measured), solid with slight edge roughness; badges `#9a2a14`, clean rings.
  - Poster portraits are **monochrome prints** of the illustrated character: sepia duotone `#2a160a` → `#d9b47a`, contrast +20%, multiplied over the paper texture.
- **Wood wall.**
  - Vertical planks **150 px** wide (66.7 px at 480p), plank-to-plank luma within ±1.5%, **amber**-brown base `#84431a`/`#804118`/`#86441a` (hue 24°; measured), with soft horizontal banding inside the planks.
  - **Seams** (cross-section at f075, 480p): a faint +4 light rim, a **≈ 2 px dark core** (min ≈ 30 on a ≈ 60 plank), then a **soft light lip ≈ 4–5 px wide peaking +12…+17**. Draw them as vector strokes so they stay crisp at every camera zoom (baked into a texture they go soft at the 1.41× push-in).
  - **Grain:** thin, nearly straight darker lines, ≈ 4 per plank per 960 px of height, 120–300 px long; very low mottling (≈ 1.5%).
  - **Knots:** ellipses about 10×17 ref px with a **deep-maroon interior** `#4c1e12` and a **darker thin outline** `#2a0e06` (zoomed reference).
  - **Nail holes:** a row of 4 px dark dots, one per plank, at about 37% height.
  - **Even, symmetric light:** luma across the f075 wall at x = 0 / 240 / 600 / 840 is 43 / 59 / 60 / 32. A gentle radial vignette centred on the frame; a very weak warm pool (10%).
- **Fabric and metal (character):** see the §3 table (pinstripes, stitching, brass buckle, concho).

## 8. Typography (verified by rendering candidates over the reference crops)

| Role | Font | Spec |
|---|---|---|
| Poster headline "WANTED" | **Bitter Black 900** (Bitter scored IoU 0.82, rank 1; 800 only matched with ink spread, 900 matches without; alt Roboto Slab 900) | Cap height **78 px** (34.5 ref px). Tracking **+0.097 em**, solved for the measured 233 ref px width. Solid near-black ink |
| Poster name, list items | **Bitter Black 900** | Name cap 39 px, tracking +0.017 em (220 ref px wide); items cap **36 px** (16 ref px), tracking **+0.04 em** ("TRAINS"/"BANKS" are 5% wider than untracked Bitter). **"HALF THE WEST" is set smaller in the reference** (row height 19 vs 22 px): it auto-shrinks to the list's right limit (cap 14.2 ref px) |
| "WANTED FOR", "REWARD" | Bitter 900 | Cap 15 px ("REWARD" 18 px), tracking +0.30 em, centred between rules. **Gap of 0.6 em on each side between text and rule**; the bottom frame lines break around the reward row |
| Reward value "$????" | Bitter 900 | 95% of the 19.5 ref px cap, red `#7a1a0a` (glyph body measured `#882f0d`). A **narrow "$"** (80% width), then an **8 ref px gap**, then the "?"s (tracking +0.03 em); baseline y 446, ending well inside the frame break at 526. "REWARD" baseline y 441: in the reference the thick outer frame line runs along its baseline and the thin one crosses its upper half. The light halo and dark fringe seen around the reference's red glyphs are 4:2:0 chroma bleed in its 480p encode; don't copy them |
| Hero title | Alegreya ExtraBold 800 (alt Bitter 900, scored 0.82 alone) | See the report's §5 |
| Tags, bubbles, labels | Alegreya Sans ExtraBold 800 | See the report |
| Chapter titles | Grenze Gotisch 800 | See the report |

**Poster geometry (measured at f075 and f143, camera inverted):** frame lines at world x 296.6 / 301.8 (left) and 558.2 / 563.5 (right); the print content sits 1.6 ref px right of the paper's centre line; dashed rules at y 323 / 360.3 / 397.6 with a 5.4 px pitch (2.4 dash, 3.0 gap), `#8a6838` at 66%. The reward line `#3a2410`, 0.9 px.

**Rules:**
- Every text box auto-shrinks to fit its container, with a 4% margin inside the poster frame (`scripts/b07_poster_layout.py` fails loudly on any overflow).
- A render **fails** if any font hasn't loaded: no silent fallback.

## 9. Icons

- **Badge:** centred 2.2 ref px above the text row's centre line (measured at f143). Outer radius 16 ref px. Outer ring 2.4 ref px and inner ring 1 ref px at r 12.3 (a clear cream gap between them), clean (no speckle), in red `#a22e16`. Interior paper tinted `#f2c890` at 50%. The pictogram is small (about 2/3 of the inner ring's diameter).
- **Pictogram:** a **filled red silhouette** with knocked-out paper-colour details at 2–3 px.
  - Locomotive: side view with chimney, cab, boiler bands, 3 wheels and a cow-catcher.
  - Money bag: a tied sack with a knocked-out "$".
  - Map: a folded three-panel map with fold lines, a dotted route and an "X".
- **Print treatment:** the same roughness and wear as the red ink. No geometric primitives (bars, dots, squares) may stand in for a pictogram.

## 10. Level of detail (acceptance)

- **Hero bust:** at least 40 distinct outlined shapes. At least 3 tones per material. Hatching in at least 3 places. Textured beard and hair strokes. Fabric detail (pinstripes, stitching, buckle, knot).
- **Background plates:** at least 3 depth layers with haze between them. Outlines on every silhouette. A texture or stroke layer on every large area (strata, grain, stains).
- **Measured targets against the reference:**
  - each scene within ±20% on edge density, fine texture, RMS contrast and colourfulness;
  - ΔE2000 < 6 on the sky, mountain, paper and wood regions.

## 11. Automatic fails

- A placeholder look of any kind: flat primitive shapes, faceless characters, untextured large fills.
- Any font fallback.
- Text crossing a border or rule.
- Visible gradient banding.
- Halos or fringes around cutouts.
- Jagged or blurry edges at output size.
- Image-model-drawn text.

## 12. Verified render and encode chain

- **Rendering:** compositions render at 3840×2160. They're downscaled to 1920×1080 with ffmpeg Lanczos (`accurate_rnd+full_chroma_int`), converting to BT.709 TV-range YUV 4:2:0, and encoded x264 `-preset slow -crf 16` with BT.709 tags.
- **Measured on a 30-frame poster segment** (`lookdev/encode_check.json`): mean pixel ΔE2000 **0.59** between the decoded MP4 and the PNG masters scaled with the same filter, and mean RGB offset **+0.14 / +0.03 / +0.21**, so encoding shifts no colour. The worst 8×8 block is ΔE 2.2, on saturated red edges (4:2:0 chroma).
- **Decode accurately when checking:** use `scale=in_color_matrix=bt709:in_range=tv:flags=accurate_rnd+full_chroma_int`. ffmpeg's default decoder path alone adds a −1.5 green bias that isn't in the file.
