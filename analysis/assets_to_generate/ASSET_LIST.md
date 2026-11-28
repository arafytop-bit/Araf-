# Art to generate in your phone app (no image API is available here)

**Use:** ChatGPT (image generation) or Gemini, whichever you prefer.

**Order:** do **A01 first**. Every later asset attaches the A01 result, so the character stays the same person.

**Attachments:** the `REF*.png` files are in `analysis/assets_to_generate/attach/` (sent to you with this list).
- They are **style references only**: line weight, shading and colour.
- The prompts tell the model **not** to copy the reference character's face, outfit or identity.
- The rebuild uses an **original** outlaw, because this tests the look, not the likeness.

**After you upload, I do the rest:** cut-outs (keying, defringing), cleanup, 2× upscaling (Real-ESRGAN anime model), colour-matching to the style bible palette, and layering. If an app can't give a transparent background, ask for flat pure green `#00FF00` instead; I key that out cleanly.

**Never let the app add text.** Every prompt ends with "no text, no letters, no watermark". If a result contains text, regenerate it.

---

## A01 · `A01_character_sheet.png` (required, do first)
- **Attach:** `REF1_style_hero_bust.png`, `REF2_style_face_detail.png`
- **Aspect:** 3:2 landscape (e.g. 1536×1024)
- **Background:** flat pure green #00FF00

**Prompt (copy all):**
> Character model sheet of ONE original character, three panels side by side on a flat pure green (#00FF00) background: (1) front view head-and-shoulders, (2) three-quarter view head-and-shoulders, (3) front view head-and-shoulders with a dark bandana pulled up over his nose and mouth. The character: a rugged frontier outlaw in his late 30s, weathered sun-tanned face, deep-set tired eyes with heavy lids and pale steel-blue irises, a short scruffy dark-brown beard, shoulder-length wavy light-brown hair in pointed locks, a battered dark wide-brim cowboy hat with a braided leather hat band and a small round silver concho, an oxblood-red wool scarf knotted at the throat, a blue-grey work shirt with thin vertical pinstripes, a dark brown leather vest with light dashed stitching along its edges, and a diagonal leather strap across the chest with a brass buckle. STYLE (match the attached images' style exactly, but do NOT copy that character's face, hair, outfit or identity): flat 2D cartoon illustration for an animated explainer; bold warm near-black outlines (#130b01) that taper at the tips, thick on the outer silhouette (about 1% of image height) and thinner on interior lines; cel shading with exactly three tones per material (skin #734a37 / #9a684a / #c48962); a hard cast shadow band from the hat brim across the eyes; small hard-edged highlights on nose bridge and cheekbones; thin tapered wrinkle hatching strokes in groups of 2–4 on the forehead, crow's feet and cheeks; the beard drawn as a dark base with many short light hair strokes; brows made of hair strokes; one white specular dot per eye; fabric detail (pinstripes following the folds, dashed stitching, braided hat band, buckle with outline). Same proportions, same design and same colours in all three panels. Even, neutral studio light. No text, no letters, no labels, no watermark, no frame.

## A02 · `A02_hero_bust_sunset.png` (required: the hero in the portrait shot)
- **Attach:** your `A01_character_sheet.png`, `REF3_portrait_composition.png`, `REF1_style_hero_bust.png`
- **Aspect:** 4:5 portrait (e.g. 1024×1280; as large as the app allows)
- **Background:** transparent (or flat pure green #00FF00)

**Prompt:**
> The same character as in the attached character sheet (identical face, hair, hat, scarf, shirt, vest and strap), drawn front-facing as a head-and-shoulders portrait, looking straight at the viewer with a calm, tired, determined expression, shoulders and upper chest visible and cropped at the bottom edge, hat fully inside the frame. Warm golden late-sunset light coming from the left and slightly behind him: warm front fill on the face, a hard hat-brim shadow band across the eyes, a thin warm rim of light on his left shoulder and hat edge. STYLE: match the attached style references exactly — flat 2D cartoon illustration, bold tapered near-black (#130b01) outlines thick on the silhouette and thinner inside, three-tone cel shading per material, wrinkle hatching strokes, beard hair strokes, pinstripes and dashed stitching, small hard highlights. Character only on a fully transparent background (if transparency is not possible: flat pure green #00FF00 with no shadow on the background). Clean crisp edges, no glow, no background scenery. No text, no letters, no watermark.

## A03 · `A03_hero_bust_masked.png` (required: the source for the wanted-poster print)
- **Attach:** your `A01_character_sheet.png`, `REF4_poster_print_style.png`, `REF1_style_hero_bust.png`
- **Aspect:** 4:5 portrait
- **Background:** transparent (or flat pure green #00FF00)

**Prompt:**
> The same character as in the attached character sheet, front-facing head-and-chest portrait, hat on, the oxblood scarf pulled up over his nose and mouth like an outlaw mask, eyes looking straight ahead, shoulders squared, arms out of frame. Same flat 2D cartoon style as the references: bold tapered near-black outlines, three-tone cel shading, hatching strokes, fabric detail. Drawn in full colour with neutral even lighting (I will convert it to a monochrome print myself). Character only on a fully transparent background (or flat pure green #00FF00). No text, no letters, no watermark.

## A04–A06 (optional: only if my code-built landscape doesn't pass the blind review)

These are the same style as `REF5_landscape_style.png`. Each goes on flat pure green #00FF00 with a 16:9 aspect.

- **A04 `A04_far_mountains.png`:**
  > A wide row of distant jagged mountains with snow caps, flat 2D cartoon style, each mountain with a lit left face and a darker right face (mauve-red #823e35 / #551e11), snow caps lit #e4bdb4 and shaded #bc938e, every shape outlined in tapered near-black, mountains filling only the bottom third, the sky area flat pure green #00FF00. No sun, no text, no watermark.
- **A05 `A05_mesa_and_hills.png`:**
  > A red desert mesa (flat top, vertical cliff strata lines, lit top edge) on the left third and low rolling hills with a thin lit rim along their tops across the rest, flat 2D cartoon style with tapered near-black outlines and three-tone shading (#5e2316 / #4c1710 / lit edge #de8d45), occupying the bottom 40%, everything above flat pure green #00FF00. No text, no watermark.
- **A06 `A06_foreground_ground.png`:**
  > A foreground strip of dusty red-brown desert ground in horizontal strata bands (#7b4125, #5f2f18, #44210c) with scattered olive grass tufts with pale tips (#8a8a3a / #d8d27a), flat 2D cartoon style with tapered dark outlines on the tufts, occupying the bottom 35%, everything above flat pure green #00FF00. No text, no watermark.

---

### What each asset becomes
| Asset | Used for |
|---|---|
| A02 | Portrait shot hero layer (f0–67, 1.00 → 1.105 push about the face) |
| A03 | Main wanted-poster print, plus every side poster revealed at f145–161 (the reference also repeats one face across the wall) |
| A01 | The consistency reference for every future pose (Phase 2 uses the same sheet → pose prompts) |
