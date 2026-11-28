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
| Background shapes (mountains, mesa, props) | **4–5 px** (2 px at 480p) | `#130b01` (distant layers also outlined) | Slight wobble. Snowcaps carry their own outline |
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
  - Sun disc `#feedc5`, ring `#fedd90`.
- **Portrait: land.**
  - Mountains: lit `#823e35`, shadow `#551e11`.
  - Snow: lit `#e4bdb4`, shadow `#bc938e`.
  - Mesa: `#5e2316` / `#4c1710` with lit edge `#de8d45`.
  - Ground strata: `#7b4125 #5f2f18 #44210c`, light streak `#a56040`.
  - Grass: olive `#8a8a3a` with tips `#d8d27a`.
- **Poster and wall.**
  - Paper base `#e6c181`; stains `#deb876 #d0a865`; light patches `#f1d294`; dark worn `#7c561b`.
  - Ink `#1d0901`; red ink `#9c330a` (badges) / `#a3281c` (reward); badge interior `#efbb82`.
  - Wood `#733911 #67320e #5b2b0b #4e240a #401b06`.
- **Other scenes:** night-town and interior-wood palettes are in `style_measurements.json`.

## 6. Atmosphere

| Effect | Spec |
|---|---|
| Sun | Disc radius **82 px** (36.5 px at 480p) including a 10 px gold ring `#fedd90`. Disc `#feedc5`, flat with no texture |
| Bloom | Luma 240 at the centre → 204 at 0.9 r → 193 at 1.3 r → 172 at 2.8 r → sky level (≈130) at about 3.8 r. A two-layer halo: a tight one (1.4 r) and a wide one (4 r), screen-blended |
| God rays | **3 dominant rays** from the sun at **102°, 128°, 170°** (counter-clockwise from +x, so 90° is straight up). Each about **6° wide**, soft edges, +7…+13 luma over the sky, strongest 150–190 px (480p) from the sun. Plus 2–3 faint rays (+3–5 luma). They sway slowly (±1.5° over 3 s) |
| Haze | Each mountain layer further back is lighter and less saturated: far range +18% value / −25% saturation vs mid range. A warm haze band `#f0964e` at 25% sits along the horizon |
| Dust specks | About **30 visible per frame** in open sky (similar on walls). Core **6–7 px** (diameter, 1080p) with a soft halo 3–4× the core. Peak +50 luma over the background, warm white `#fff0d0`. Sizes vary 0.5–1.6×, opacity 0.3–1.0, blur 0–3 px. Drift: median 0.16 px/frame, 90th percentile 2.7 px/frame, mostly sideways with slight upward bias. Individual twinkle (opacity ±30%, 1–3 s period) |
| Birds | 3 thin "m" silhouettes **25–35 px** wide, stroke 3 px, `#3a1e24`. Flap at about 2.5 Hz, drift about 0.3 px/frame |
| Vignette | Strong, radial. Luma ratio to the centre at normalised radius 0.6/0.8/1.0/1.2: **0.69 / 0.55 / 0.31 / 0.23** (wall scene). Median corner/centre over the video is 0.63 |
| Warm light pool | Interiors and props: a centre ellipse +10–15% brighter, warm `#ffb060`, soft-light blend |
| Grain | Not visible (< 1.5 luma std at 480p, compression-limited). Add **≤ 1.0%** monochrome grain only to stop gradient banding, and dither every gradient |
| Chromatic aberration, VHS, light leaks | None |

## 7. Materials

- **Paper (posters, notebook, letters).**
  - Base `#e6c181`. Large soft **stains** (round blobs 90–200 px across, low contrast, low-frequency luma std ≈ 11, p5–p95 range 36) in `#deb876`/`#d0a865` with a few lighter patches `#f1d294`.
  - **Edges darken** about 10–20% within 30 px of the border, with a dark line at the very edge.
  - A **faint centre fold**: a 2 px vertical line, `#c9a56a` at 50%, plus a faint horizontal fold.
  - **Torn edges:** irregular outline, amplitude 5–11 px, period 20–60 px. A **triangular notch** (≈ 40 px wide × 30 px deep) near the bottom right.
  - **Nail** at top centre: a 20 px domed head, `#3c3f48` with a highlight ring `#8a8f9c` and a dark outline.
  - **Drop shadow** on the wall: offset (0, +13) px, blur 13 px, `#2a1205` at 55%.
- **Printed ink.**
  - Text and lines in `#1d0901`, with slightly rough edges (±0.7 px displacement) and density varying 5–10%.
  - Red ink `#a3281c` is visibly **worn**: 8–15% speckled drop-outs and lighter patches.
  - Poster portraits are **monochrome prints** of the illustrated character: sepia duotone `#2a160a` → `#d9b47a`, contrast +20%, multiplied over the paper texture.
- **Wood wall.**
  - Vertical planks **150 px** wide (66–67 px at 480p), plank-to-plank luma ±3, base `#733911`/`#67320e`/`#5b2b0b`.
  - **Gaps** 4 px dark `#2a1003` (−28 luma), with a 1 px lighter lip on one side.
  - **Grain:** sparse 2 px darker streaks, 40–180 px long, wavy.
  - **Knots:** dark ellipses about 16×27 px `#3a1a06` with a ring.
  - **Nail holes:** a row of 4 px dark dots, one per plank, at about 37% height.
  - Strong vignette plus a warm centre pool, with dust specks over the top.
- **Fabric and metal (character):** see the §3 table (pinstripes, stitching, brass buckle, concho).

## 8. Typography (verified by rendering candidates over the reference crops)

| Role | Font | Spec |
|---|---|---|
| Poster headline "WANTED" | **Bitter Black 900** (Bitter scored IoU 0.82, rank 1; 800 only matched with ink spread, 900 matches without; alt Roboto Slab 900) | Cap height **75 px** (33.5 ref px). Tracking +0.07 em. Ink `#1d0901` with print roughness |
| Poster name, list items | **Bitter Black 900** | Name cap 39 px; items cap **36 px** (16 ref px, measured); tracking 0 |
| "WANTED FOR", "REWARD" | Bitter 900 | Cap 15 px ("REWARD" 18 px), tracking +0.30 em, centred between rules. **Gap of 0.6 em on each side between text and rule**; the bottom frame lines break around the reward row |
| Reward value "$????" | Bitter 900 | Cap 44 px, worn red `#a8261a`. Each "?" is a separate glyph advance |
| Hero title | Alegreya ExtraBold 800 (alt Bitter 900, scored 0.82 alone) | See the report's §5 |
| Tags, bubbles, labels | Alegreya Sans ExtraBold 800 | See the report |
| Chapter titles | Grenze Gotisch 800 | See the report |

**Rules:**
- Every text box auto-shrinks to fit its container, with a 4% margin inside the poster frame.
- A render **fails** if any font hasn't loaded: no silent fallback.

## 9. Icons

- **Badge:** outer diameter **80 px**. Outer ring 5.5 px and inner ring 2.2 px, 6.7 px apart, in red `#9c330a`. Interior paper tinted `#efbb82`.
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
