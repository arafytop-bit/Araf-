# Re-engineering blueprint: "The FBI's 10 Most Wanted List Explained (2024)"

**Source:** *Trust Me Bro*, YouTube `RnDmenVBwKw`, 15:03.9, about 2.7M views.
**Analysed file:** the 854×480 / 30 fps upload. All **27,117 frames** were measured individually.
**Goal:** rebuild a video in exactly this format from a new narration track plus its exact script.

All numbers below are measured unless marked *(observed)*, which means a visual judgment from frame-by-frame inspection. Pixel values are given at 480p (as analysed) and converted to the **1920×1080 production target** (×2.25).

---

## 1. The formula in 12 rules

1. **Stage.** A near-black radial-vignette background. A talking **stick-figure host** stands centre-stage and is on screen about **50% of the runtime**.
2. **Relentless visual change.** There are **508 distinct visual states in 903.9 s**: median hold **1.20 s**, mean **1.78 s** (p10 0.30 s, p90 4.24 s, max 13.3 s). That is about **34 changes per minute**, or one every **~6.5 spoken words**.
3. **Cut on the word.** Each change lands on the **first syllable of the word it illustrates**. The median offset is 0 frames and the mode is **1 frame early**; **80% fall within ±3 frames** and 90% within −5…+4 frames.
4. **The host never lip-syncs.** He holds a facial **expression for about 1 s** (0.8 face changes per second), then swaps at phrase or emphasis points. Pose and expression change at every cut. He has exactly **three scales**: normal **1.00**, punch-in **1.52**, picture-in-picture **0.47**.
5. **Wall-to-wall narration.** About **221 wpm** with pauses edited out: only 23 gaps over 0.3 s in 15 minutes.
6. **Every concrete fact gets a picture:**
   - names → title card or character
   - numbers, dates, money → **red callout text, top centre**
   - places → **green map with a red dot**
   - idioms → **literal visual gag**
   - lists → **items pop in one per spoken word**
7. **Photos and footage** sit centred at a **median 69% of frame height**, over the black stage or a blurred, darkened copy of themselves. Most get a **slow 0.6%/s push-in** (about 73% zoom in, 27% zoom out).
8. **Layering.** When something new lands on top of an image, the image underneath is **blurred (σ ≈ 10–22 px at 1080p) and dimmed to about 30–50%**.
9. **Entrances are snappy.**
   - 36.5% are 1-frame hard swaps.
   - 35.6% are **3–5-frame** pops: scale 115→100%, scale 50→100%, or a fade.
   - Cartoon animation is **flipbook at 5 fps** (6 frames per drawing).
10. **Typography is one font family.** A heavy, wide, geometric all-caps face.
    - Names are white with a silver gradient.
    - Callouts are deep red (#D00108-ish).
    - Brand accents are coral red (#F34B4B).
11. **Audio.**
    - Voice is about −21.6 dBFS RMS and near-mono.
    - The **dark, quiet music bed sits about 20–25 dB under the voice**.
    - **One recurring "hit" SFX** plays on every list-entry title card, plus SFX on gags.
    - The video ends on a **loud 6.5 s branded outro sting**.
12. **Structure.**
    - hook (kinetic title, 23 s)
    - history (46 s)
    - **10 entries using an identical template** (54–110 s each)
    - mid-roll like/comment CTA before the last entry
    - takeaways
    - "watch this next" end screen

---

## 2. Technical specs

| | Source (analysed) | Production target |
|---|---|---|
| Resolution | 854×480 (16:9), square pixels | **1920×1080** |
| Frame rate | 30/1 constant, progressive | **30 fps** |
| Duration | 903.9 s (27,117 frames) | follows your audio |
| Video | H.264 Main, ~97 kbps (very static content) | H.264 High, CRF 18, yuv420p, bt709 |
| Audio | AAC-LC 44.1 kHz stereo 128 kbps | AAC 48 kHz stereo 192–320 kbps |
| Loudness | **−19.0 LUFS integrated**, LRA 3.2 LU, true peak −1.0 dBTP | −14 to −16 LUFS, TP ≤ −1 dBTP |

Static content: 79% of frames differ from the previous frame by less than 0.1% of pixels, and 22% are bit-identical. The video is mostly *held images with instant changes*, not continuous motion.

---

## 3. Structure and timeline

| Section | Start | Dur (s) | Words | wpm | Visual states | Changes/min | Avg hold (s) | Host on screen |
|---|---|---|---|---|---|---|---|---|
| Hook + intro | 0:00.0 | 23.2 | 96 | 249 | 14 | 36 | 1.66 | 52% |
| History of the list | 0:23.2 | 46.3 | 181 | 235 | 54 | 70* | 0.86 | 31% |
| #1 | 1:09.4 | 110.1 | 405 | 221 | 61 | 33 | 1.80 | 39% |
| #2 | 2:59.5 | 69.1 | 245 | 213 | 35 | 30 | 1.98 | 40% |
| #3 | 4:08.6 | 97.8 | 334 | 205 | 64 | 39 | 1.53 | 39% |
| #4 | 5:46.4 | 54.1 | 165 | 183 | 40 | 44 | 1.35 | 18% |
| #5 | 6:40.5 | 77.5 | 275 | 213 | 39 | 30 | 1.99 | 47% |
| #6 | 7:58.0 | 64.8 | 256 | 237 | 38 | 35 | 1.71 | 58% |
| #7 | 9:02.8 | 59.9 | 234 | 234 | 32 | 32 | 1.87 | 39% |
| #8 | 10:02.8 | 74.4 | 250 | 202 | 24 | 19 | 3.10 | 52% |
| #9 | 11:17.1 | 80.1 | 301 | 226 | 35 | 26 | 2.29 | 59% |
| #10 title | 12:37.2 | 2.2 | 5 | – | 3 | – | – | – |
| **Mid-roll CTA** (like/comment for future videos) | 12:39.4 | 48.0 | 197 | 246 | 13 | 16 | 3.69 | 63% |
| #10 story | 13:27.4 | 55.6 | 198 | 214 | 44 | 48 | 1.26 | 44% |
| Outro takeaways | 14:23.0 | 17.5 | 84 | 288 | 8 | 28 | 2.18 | 71% |
| End-screen CTA + sign-off | 14:40.5 | 16.5 | 71 | 258 | 6 | 22 | 2.75 | 13% |
| Music sting | 14:57.0 | 6.9 | 0 | – | 3 | – | – | 0% |

\*Inflated by flipbook loops (0.2–0.4 s cycles). Commentary and CTA stretches deliberately slow to 3–4 s holds with the host on screen; story stretches speed up.

### 3.1 Hook (0:00–0:23)
1. **Kinetic title** (3.5 s) shows the first sentence, *"Every person currently on the FBI's most wanted list"*.
   - The words are stacked in 3 centred lines: `EVERY PERSON` / `ON THE FBI'S` / `MOST WANTED LIST`.
   - Every word is pre-placed as a **dim ghost** (about 25% brightness) and **lights up to full white (or red for "MOST WANTED") within ±2 frames of being spoken**.
   - A small host stands bottom-left, and three tiny FBI-agent chibis run in from the right.
2. Host plus a quick "relatable" setup: *"chances are you've heard…"*, a screenshot of the list, then 3 rapid punch-ins.
3. A literal gag ("I was in the same boat" puts the host in a rowboat on the ocean), then a promise of what's coming.
4. A tease ("SPOILER ALERT" in red over the blurred mugshot grid) and the hook payoff, *"these are some bad people."*

### 3.2 History (0:23–1:09)
- A big red **year slam** ("1949") over an illustrated reenactment: characters composited on a real restaurant photo, with talk loops.
- An object-as-character gag (a newspaper with legs).
- A phone-desk tip-line scene, eligibility rules, and idiom gags ("a staple", "under your belt").
- It ends on a joke beat with the host zoomed: *"captured or dying, so take your pick."*

### 3.3 The per-entry template (repeated 10×, verified on every entry)
```
[TITLE CARD + hit SFX] → H → IDENTITY FACTS → (H ↔ STORY VISUAL)×n → REWARD → H punch-in / "fled" map → next TITLE
```
1. **Title card**, 1.7 s average: a hard cut and the hit SFX, while the name is read aloud. Layout is in §5.8.
2. **Host reaction**, usually 1–3 s. It can be a picture-in-picture over a large photo (*"he definitely looks like somebody who would be on this list"*).
3. **Identity facts**: the subject's own stick-figure character with a black **name tag**.
   - Red fact labels pop in on their words: born / age, height bar, weight bar, sex/ethnicity, scars.
   - Then a **state or country map** with a red dot and label.
4. **Story**: alternates between host and illustration. B-roll runs are **1 visual** (55/89 runs), 2 (18/89) or 3 (13/89).
   - **Host stretch median 3.6 s ↔ B-roll run median 4.3 s.**
   - Illustrations used: reenactments (characters on real photos), framed photos and footage (often with a PIP host), literal gags, red date callouts, maps.
5. **Reward**: `$5 MILLION` (red callout) plus the FBI wanted or reward poster.
6. **Closer**: a host punch-in with an opinion or quip, or a map of where they fled. "Fled to Mexico" is a running theme that pays off in the outro. Then the next title card.

### 3.4 Mid-roll CTA (inside the last entry)
- **Title card #10 first**, then *"before we get into… two quick things"*.
- Offers two possible future videos, shown as visuals: a grid of historic fugitives and the US Marshals list.
- "Leave a **like**": a grey thumbs-up turns blue. "Leave a **comment**": a speech bubble reading "PLEASE MAKE THAT VID, BRODY!!"
- Then *"now let's proceed with our final entry."*

### 3.5 Outro
- Two takeaways.
- Callback gag: a "Get Out of Jail Free" card over a Mexico map.
- Call to action: *"drop a tip"*, with a red URL as a callout.
- End screen (from 14:42.7):
  - Host left, with a white rounded **"WATCH THIS NEXT"** card on the right, a red curved arrow, and a tiny agent peeking over the card.
  - At the sign-off ("…as always, trust me bro") the host **drops out with motion blur**.
  - The **channel logo and a "Subscribe" button drop in from the top with a bounce**, on the outro music sting.
  - Then 0.4 s of empty stage.

---

## 4. Pacing and timing rules

| Metric | Value |
|---|---|
| Visual states (any visible change of >2% of pixels or a motion segment) | 508 (437 holds + 71 motion segments) |
| Editorial shots (one visual idea; groups of states) | 244, about 16/min, ~13.5 words each |
| State hold: p10 / median / mean / p90 / max | 0.30 / **1.20** / 1.78 / 4.24 / 13.27 s |
| Cut offset vs. word onset (frames) | distribution −3:26 · −2:63 · **−1:90** · 0:77 · +1:61 · +2:53 · +3:33. Median 0, mode −1; 80% within ±3, 90% within −5…+4 |
| Cuts landing right after a micro-pause | the voice dips to about −40 dB 50–100 ms before hard cuts, so cut on phrase starts |
| Host face changes inside holds | **0.8/s**; median interval 0.73 s |
| Speech | 221 wpm overall (183–288 by section); 23 pauses >0.3 s, 3 >0.5 s, 1 >1 s |
| Longest host holds | 8–13 s, only during opinion or CTA monologue (still with face swaps) |

**Rules of thumb for a new script:**
- Plan **1 visual state per ~6–7 words**, and **1 new visual idea per ~13 words**.
- Never hold an unchanged frame longer than about 1.5 s. Inside long host holds, swap expression every 0.7–1.5 s.
- Return to the host after 1 (sometimes 2–3) illustrations.

---

## 5. Visual system

### 5.1 Canvas
- **Background:** an elliptical radial gradient, `#0B0B0B` flat over the inner ~20% of radius, easing to `#030303` at the frame edge and `#010101` in the corners.

  Measured profile by normalised radius:

  | Radius | 0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
  |---|---|---|---|---|---|---|
  | Brightness | 11 | 10.7 | 9.4 | 7.1 | 4.6 | 2.3 |

- Everything sits on this stage unless a full-frame photo replaces it.

### 5.2 Host character (*observed* shapes, *measured* sizes)

**Palette:**
- head `#FFFFFF`
- cap and shirt **coral red `#F34B4B`**
- outlines `#000000`
- a thin **light-grey rim stroke (~#8C8C8C, 1 px at 480p ≈ 2–3 px at 1080p) around the whole silhouette**, so the black linework reads on the black stage

**Construction:**
- **Head:** a perfect circle. The black outline is about **4.3% of head diameter** (7 px at 480p).
- **Cap:** a red dome covering the head's upper-left quadrant (about 10 o'clock to 12 o'clock), outlined. The **brim is a thick rounded black stroke** from the cap front at about 12 o'clock, pointing up-right about 10–15° above horizontal, **≈0.35 × head diameter long**.
- **Eyes** (measured): two small black ovals **≈0.06 × head diameter**, centres at **x 0.45 and 0.57, y 0.40** of the head's bounding box (12% apart, centred). Optional brows on emotional expressions.
- **Mouth:** a black filled shape that changes per expression (see below). The default open "talking" mouth is centred at **(0.48, 0.59)** of the head box and measures **0.29 × 0.19 D**.
- **Torso:** a red rectangle with a black outline, **≈0.44 D wide × 0.46 D tall**, starting at the head's bottom edge (the head overlaps it).
- **Arms and legs:** thick black rounded strokes (same weight as the head outline) with the grey rim. Legs are two short straight strokes, about 0.45 × head diameter.

**Scales and positions:**

| Scale | Head radius (480p) | Head radius (1080p) | Head centre | Usage |
|---|---|---|---|---|
| **Normal 1.00** | 81 px | 182 px (diam. ≈ 34% of frame height) | x 50%, **y 39.8%** | 124 of 205 host states; 41% of runtime |
| **Punch-in 1.52** | 123 px | 277 px (diam. ≈ 51% of height) | x 50%, y 41.3%; legs cropped | 42 states; ~10% of runtime |
| **PIP 0.47** | 38.5 px | 87 px | bottom-left (x ≈ 22–32%) or bottom-centre, y ≈ 80%, feet cropped by frame bottom | over footage, photos, end screen |
| Side position | 81 px | 182 px | x ≈ 26–32% (host left, photo right) | "compare" shots |

- Punch-ins are **hard jump-cuts** between scale levels, with no animated zoom. They are used for jokes, opinions, rhetorical asides and reactions to shocking facts.
- Each cut to the host normally changes both **pose** and **expression**.

**Pose inventory** *(observed)*:
1. Both hands on hips (default).
2. One hand on hip, other forearm raised or waving (talking).
3. Hand on chin (thinking or research).
4. **Both hands on cheeks** (shock or disgust).
5. Arms out, palms up (shrug).
6. Pointing or gesturing toward an inserted photo.

**Expression inventory** *(observed)*:
1. Talking open mouth (black bean shape).
2. Small "o".
3. Big open "D" smile.
4. Teeth grimace (outlined rectangle with teeth lines).
5. Wavy frown (concern).
6. Skeptical squiggle with one raised brow.
7. Closed smile or smirk.
8. Shocked tall "Ш/U" mouth with raised brows.

Expressions follow the sentiment of the current clause.

**Head-bob:** some expression swaps also nudge the head a few px (*observed*).

**Entrance:** the host normally cuts in. When overlaid on a previous image, he fades in over **3–4 frames** while the image behind blurs and darkens. After a title card he enters with a 2–4-frame blur-to-sharp.

### 5.3 Other characters
- **Same body template as the host**, with a **skin-tone head** and **hair, beard or moustache shapes** in black or brown.
- Coloured shirt rectangles: grey, orange `#EA994F`, navy, teal `#52A5B5`, purple, black.
- Measured skin tones: light `#BAA399`/`#C9A78F`, tan `#D2A070`, dark brown `#5D493C`.
- Accessories: caps, police caps (navy with gold badge), Santa hat, sunglasses, camo bandana mask, helmet.
- **Name tag:** small white caps text on a black rectangle centred above the head (e.g. `ALEJANDRO`).
- **Real-photo props in cartoon hands:** a desaturated photo hand holding cash, a pistol, a peace sign.
- **Real-photo head cut-outs** on stick bodies are used for public figures.
- **Extreme close-ups:** push in until the face fills the frame, for evil grins and shocked faces.
- **Object-as-character:** a newspaper with eyes and legs, a briefcase with eyes.

### 5.4 Shot catalogue: share of runtime (manual classification of all 244 editorial shots)

| Category | Shots | Time | Share | Avg shot | Description |
|---|---|---|---|---|---|
| HOST | 75 | 286.9 s | 31.7% | 3.8 s | host on stage (normal; includes quick punch-ins) |
| HOST_ZOOM | 13 | 85.2 s | 9.4% | 6.6 s | punch-in sequences |
| SCENE | 20 | 80.9 s | 8.9% | 4.0 s | characters composited on a real photo background (reenactments) |
| CHAR | 19 | 70.1 s | 7.8% | 3.7 s | characters on the black stage (actions, list build-ups, loops) |
| PHOTO | 17 | 64.4 s | 7.1% | 3.8 s | framed photos (single, side-by-side, tilted collage) |
| TEXT | 20 | 46.2 s | 5.1% | 2.3 s | red callouts or big outline numbers, usually over the host |
| DOC | 10 | 46.1 s | 5.1% | 4.6 s | wanted posters, web screenshots, mugshot grids |
| GAG | 14 | 37.8 s | 4.2% | 2.7 s | literal idiom or metaphor visuals |
| PIP | 6 | 34.8 s | 3.8% | 5.8 s | footage or photo plus small reacting host |
| CHAR_INFO | 6 | 30.9 s | 3.4% | 5.2 s | subject character plus fact labels, height/weight bars, map |
| ENDSCREEN | 2 | 20.8 s | 2.3% | 10.4 s | |
| TITLE_CARD | 10 | 17.4 s | 1.9% | 1.7 s | |
| PHOTO_FULL | 6 | 14.8 s | 1.6% | 2.5 s | |
| HOST_OVER | 4 | 13.8 s | 1.5% | 3.4 s | host over a blurred previous image |
| MAP_WORLD / MAP_STATE | 5 / 6 | 13.4 / 9.3 s | 2.5% | ~2 s | |
| HOST_PHOTO | 1 | 11.2 s | 1.2% | | host beside photos |
| FOOTAGE | 3 | 6.6 s | 0.7% | | |
| TITLE_KINETIC, LOGO, CTA, MEME, BLANK | | ~13 s | 1.4% | | |

### 5.5 Photos and footage treatment
- **Framed and centred:**
  - Median size **69% of frame height** (p10 53%, p90 95%) and 61% of width.
  - Centre (50%, 50%).
  - Over the black stage or over a **blurred, darkened, enlarged copy of itself** (a "blur fill" background).
- **Slow push-in:**
  - 96 of 113 non-host holds move.
  - The rate is roughly **constant at about 0.6% per second**, centre-anchored. Total move is about 1–3% per shot; short shots look faster because of the entry settle.
  - Direction is about 73% in and 27% out. Host shots stay static.
- **Entry:** a hard cut to about 112–115% scale, which **settles to 100% in about 3 frames** (with slight motion blur). A second image added to a layout **pops from 50%→100% in about 4 frames**, while the first slides aside (about 5 frames, ease-out) to re-centre the pair.
- **Tilted collages:** 2 photos rotated about ±5–8°, overlapping, with drop shadows. Captions in red go under them (e.g. "AUGUST, 2000").
- **PIP reaction:** footage or photo framed large; the host at 0.47 scale overlaps its bottom edge (bottom-centre or bottom-left), still swapping expressions.
- **Annotations on photos:** red circle plus green arrow, YouTube-thumbnail style.

### 5.6 Maps
- **State or country map:**
  - Flat silhouette with fill `#96E669`, a thick darker outline `#4D7336` (about 1.5% of frame height), and lighter inner "terrain" squiggles `#81C958`.
  - A **red dot** (`#E00000`) that **pulses on and off every 2–3 frames** on entry.
  - A **white caps label with a black outline** (city, county or state).
  - Size: fills about 60–75% of frame height.
  - Pops in with a slight scale settle over a blurred, dimmed photo or the black stage.
- **Cartoon world map:**
  - Ocean `#77CDF5` with lighter wave lines `#4EB6EF`; land `#95E267` / `#7BCB41` with a dark coast line `#44763F`.
  - Used for:
    - a **red route polyline with an icon travelling along it**
    - head icons placed on countries
    - cell towers
    - drug bricks over regions
    - a red "prohibited" circle over the USA
    - zoom-ins on a country with a label
- **Map gags:** the country wears "deal with it" sunglasses; a "Get Out of Jail Free" card over the map.

### 5.7 Typography

One family throughout: **a heavy, wide, geometric all-caps sans**.
- Signature letterforms: squared **M** with a short middle V, **1** with a flag and foot, wide round C/O/S, straight-legged R, generous tracking (+3–5%).
- Closest match: **LEMON MILK Bold**.
- Free fallbacks to test: **Unbounded 800/900**, **Lexend Exa 900**, Montserrat 900 with wide tracking.

| Element | Colour / effect | Size (cap height) | Position | Entrance |
|---|---|---|---|---|
| **Red callout** (`$5 MILLION`, `MAY 11TH, 2012`, `30 YEARS IN PRISON`, `600 MEMBERS`) | deep red **#D00108** (measured #B80004–#E50105), glossy gradient (brighter centre, darker edges), subtle grunge, soft dark shadow | **~8.5–9% of frame height** (≈ 95 px at 1080p) | **centred**; text top at 10–14% of height (block centre ≈ 16–19%); width up to 90% | fade/scale-settle in **~5 frames** on the first word of the phrase; host stays visible below |
| **Title-card rank number** | same red | ~5% of height (≈ 56 px) | left-aligned at x = 15%, about 20 px above the name | with the card (hard cut) |
| **Title-card name** | white→light-grey vertical gradient (silver), dark soft drop shadow, faint grunge | ~6.3% of height (≈ 68 px); line pitch ≈ 8.3% (90 px); **one word per line** | left-aligned at x = 14.6%; block vertically centred at about 53% | hard cut, then a slow settle or drift |
| **Name tag** above a character | white on a black box | ~2.5% of height | centred above the head | with the character |
| **Fact labels** around a character (`BORN IN 1998`, `NOVEMBER 26TH`, `26 YEARS OLD`, `WHITE MALE`) | red (#C90611) | ~3.5% of height | scattered left and right of the character | **each pops in on its spoken word** |
| **Height bar** | coral-red vertical line with end ticks, label beside it (`5'4`, `6' TO 6'4" FT TALL`) | spans the character's height | right of the character | pop |
| **Weight bar** | horizontal red bar with ticks above the head, label (`300 POUNDS`) | | above the character | pop |
| **Outline year** (`2021`, `2007`) | huge grey outline-only digits *behind* the host | ~35% of height | centre | cut |
| **Meme caption** | black bold caps on a white top bar (~28% of height), emoji allowed | ~11% of height | top band | hard cut |
| **Kinetic title** | white words (red for key words), ghost state at about 25% brightness | lines 5–7% of height | centred, 3 lines | per-word light-up on speech |
| **URL callout** | coral #EA4B53 | ~8.5% | top centre | fade |

### 5.8 Title card layout (1080p)
- Black vignette stage.
- Red rank number left-aligned at x ≈ 288 px, directly above the first name line (gap ≈ half a line). It moves up as the name gets more lines.
- Name block left-aligned at x = 281 px, centred about y ≈ 575 px. The text column ends before the middle (x < 965).
- **Portrait mugshot on the right**: centre x ≈ 70% (1350 px), height ≈ 56% (≈ 610 px), aspect about 3:4, centred vertically, with a thin edge and shadow.
- Duration **1.2–2.8 s** (mean 1.7 s).
- **Hit SFX exactly on the cut.**

### 5.9 Gags and visual-metaphor catalogue (the channel's signature humour)
The rule: **when the script uses an idiom, draw it literally.** Examples from this video, with the trigger words:

| Trigger | Visual |
|---|---|
| "in the same boat" | host in a rowboat on the ocean |
| "a staple" | giant staple |
| "under your belt" | leather belt |
| "a **string** of murders and kidnappings" | clothesline with swinging tags |
| "power **vacuum**" | vacuum cleaner labelled POWER |
| "kidnapping" | **KID NAPPING?** meme (sleeping kid with zzz), then **BETTER WAKE 'EM UP!!!! 😂😂😂** |
| "the case went **cold**" | briefcase frozen in an ice block |
| "Ponzi / pyramid scheme" | pyramid outline with the person on top |
| "investors all over the world" | globe with red pins |
| "paid an undisclosed amount" | green **$$$** over a blurred photo |
| "seemingly vanished" | character crossfades out |
| "killed activists" | Thanos-style pixel disintegration |
| "human trafficking" | box truck with a "WE SELL PEOPLE!" ad |
| "in true Colombian fashion" | map wearing sunglasses |
| "get out of jail free card" | Monopoly-style card |
| "captured or dying, take your pick" | giant hand holding a tiny man, plus an inset of a fall down the stairs |
| "harboring children" | "PRIVATE PROPERTY - I'M HARBORING CHILDREN" sign |
| lists ("cash, a car, a motorcycle, Christmas presents and vacations") | each item pops in on its word |

---

## 6. Motion and transition catalogue (frame counts at 30 fps)

| Transition | Share of significant changes | Spec |
|---|---|---|
| Hard cut / instant swap | **36.5%** (159) | 0 frames; the new visual lands 1–2 frames before the word |
| Cut + quick settle (pop) | **35.6%** (155) | **3–5 frames**. Full-frame images: 112–115% → 100% with motion blur, ease-out. Added elements: 50% → 100% (slight overshoot OK). Text: opacity 0→1 plus about 105→100% scale. |
| Slower fade / slide / settle | 8.0% (35) | 6–9 frames: layout re-centring slides, overlay fades, **character crossfade-out about 7 frames** ("vanished") |
| Short animation | 11.5% (50) | 10–30 frames: characters walking in or out, route drawing, pendulum swing (tag rotation oscillates about 1 s with decay), splatter, pixel disintegration (about 40 frames, squares drift up-right and fade), map dot pulse |
| Footage / long animation | 4.8% (21) | real video clips (CCTV and similar) playing at native speed |
| Background change on overlay | – | previous image blurs and darkens over **3 frames** when the host, a map or text lands on it |
| Flipbook loops | – | **6 frames per drawing** (5 fps) for talk, phone-ringing and walk cycles (2–4 drawings per loop). 0.4 s two-pose loops for "talking characters" scenes. "zzz" letters bob on 6-frame steps. |
| End whip | – | the host drops down and out with motion blur (about 5 frames) while the logo and Subscribe button fall in from the top (about 8 frames) and bounce-settle (about 6 frames) |
| Kinetic word light-up | – | ghost → full brightness in 1–2 frames on word onset |

Within shots, holds are static apart from the slow push-in on photos and posters and the host's expression swaps.

---

## 7. Audio spec

**Voice:**
- A single narrator, median F0 188 Hz (p10 150, p90 232): energetic, conversational, fast (~221 wpm).
- Near-mono (L/R correlation 0.99). Tightly edited: no breaths or pauses.
- Mix level about −21.6 dBFS RMS. Heavily levelled: loudness range only 3.2 LU.

**Music bed:**
- Present under almost the whole video, but very low: in the stereo side channel at about −40 to −60 dBFS, roughly **20–25 dB under the voice**.
- Dark and low-register (spectral centroid 440–890 Hz), with a steady pulse.
- Tonal centre changes between sections, so a **different track or mood per segment**. It is louder in suspenseful stretches (8:00–10:00 ≈ −40 dB).
- It **drops out completely before title card #10** (about −63 dBFS at 12:36.9–12:37.3).

**SFX:**
- **The same sample on every list-entry title card**: pairwise waveform similarity 0.8–0.97. Bright (centroid 4.3–5.7 kHz), sharp attack **exactly on the cut frame**, about 1 s decaying tail. It reads as a cinematic swoosh-hit.
- Gag SFX were detected at:

  | Time | Gag |
  |---|---|
  | 0:11.0 | "same boat" |
  | 0:21.1 | "SPOILER ALERT" |
  | 0:59.6 / 1:01.9 | belt / "REALLY BAD THINGS" |
  | 1:06.9 | the grab |
  | 2:07.6 | night grab |
  | 4:27.3 | string swing |
  | 7:17.9 | pyramid |
  | 13:51.9–13:54.0 | back-room door reveal, a cluster of hits |

- Normal cuts have **no** whoosh. Sound marks *moments*, not every edit.

**Outro sting:**
- Enters about 0.2 s after the last word, on the logo drop. Loud (−11 dBFS RMS, peaks −1 dBFS).
- A punchy beat at about 105–110 BPM lasting **6.5 s**, then a 0.5 s fade to silence.

---

## 8. Word → visual trigger rules (decision table for a new script)

| What is being said | Visual to cut to (on the first syllable) |
|---|---|
| Video promise or hook sentence | kinetic title (words light up as spoken) plus small host |
| New list entry or person name | **TITLE CARD** (rank number, name, portrait) + hit SFX, then host reaction |
| Physical description, birth date, age, height, weight, ethnicity | **CHAR_INFO**: the person's stick figure with name tag; red facts pop in per word; height/weight bars |
| Place (state, city, country) | green **map**, red pulsing dot, white label (over a dimmed photo if one was up) |
| Travel or route | cartoon world map with an animated red route and a moving icon |
| Year, date, money, count, sentence length | **red callout at top centre** over the host (or over the current scene), for the length of the phrase |
| Charges or list of crimes | poster or doc in the centre; red labels pop around it, one per charge as spoken |
| Concrete noun or event (a restaurant, an ATM, a wedding, a car, a bathroom) | real photo (framed or full) **with the characters composited into it acting the sentence** |
| Real footage exists (CCTV, news) | framed footage plus PIP host reacting |
| Idiom or figure of speech | **literal gag** (§5.9) + SFX |
| Joke, opinion, "to be honest", sarcasm | **host punch-in** (1.52×) with a matching expression |
| Shock ("in broad daylight", "killed", "found her body") | host hands on cheeks, or a punch-in with a shocked mouth, or an extreme close-up of a character |
| List of items | items pop in one per word in a row |
| Reward | `$X MILLION` callout plus the official poster |
| CTA (like, comment, subscribe) | thumbs-up turns blue; comment bubble; end screen |
| Anything else / connective narration | host on stage, new pose and expression |

---

## 9. Production pipeline for your audio (next step)

1. **Ingest:** your audio (WAV preferred) and the exact script.
   - Measure loudness.
   - Optionally tighten pauses to match the source's gapless delivery (only with your OK, since it changes timing).
   - Normalise to −14 to −16 LUFS.
2. **Word-level alignment** of your script to your audio.
   - Use offline pocketsphinx forced alignment (`scripts/align.py`). It was validated here against YouTube's timings: median error 0.01 s, MAD 0.05 s.
   - Anchor chunks using recognition plus dynamic-programming matching, or detected pauses.
3. **Beat planning:** segment the script into visual beats (about 6–7 words each, about 13 per idea) using the trigger table (§8). Then enforce the pacing targets:
   - median hold about 1.2 s
   - host about 50% of runtime
   - host ↔ B-roll ping-pong (host 3.6 s / B-roll 4.3 s medians)
   - expression swap every ~1 s
   - cut 1 frame before each trigger word
4. **Assets**, drawn as vectors so they stay sharp at 1080p:
   - host rig with poses and expressions; character template
   - maps from Natural-Earth TopoJSON (npm `world-atlas` / `us-atlas`) styled as in §5.6
   - callout text with the font from §5.7
   - posters and title cards
   - photos and footage: yours, or drawn replacements (§10)
5. **Render:** compose each state, then apply the motion specs (§6): pops, settles, 0.6%/s push, blur-dims, loops. Render 1920×1080 at 30 fps, then mux.
6. **Mix:**
   - voice
   - music bed about 22 dB under, with a mood per section
   - the title-card hit SFX on every entry
   - gag SFX
   - an outro sting

   Synthesised, or your royalty-free files.
7. **QA:** re-run this analysis on the render and compare cut rate, hold distribution, host share and cut-to-word offsets against the numbers above.

## 10. Inputs and limits for the build
- **Network:** image sites (Wikimedia, fbi.gov, Unsplash, YouTube thumbnails) are **blocked** from this environment, so the real-photo inserts (about 20% of runtime) need either your images or illustrated replacements. Package registries and Google Fonts are reachable.
- **Branding:** I'll use your channel name and logo on the end screen. I'll give the host your own colour or accessory so the video reads as your channel rather than an imitation of the source channel's mascot and logo.
- **Uncertain from a 480p source:** the exact font (closest match named above), the exact SFX and music tracks (characterised, not identified), and fine easing curves (approximated from 30 fps frame steps).

## 11. Files
| File | Contents |
|---|---|
| `data/edl.csv` / `edl.json` | **all 508 visual states**: frame-accurate start/end, timecode, duration, still/motion, category, description, host scale, push-in rate, **words spoken during the state**, OCR text |
| `data/edl_groups.json` | 244 editorial shots (merged states) with description and words |
| `data/sections.json` | per-section timing and pacing stats |
| `data/words_aligned.json` | 3,297 narration words with start/end times |
| `data/events.json` | every change event (>0.4% of pixels) with length and before/after difference |
| `data/host_geom.json` | host head centre, radius and shirt detection per state |
| `data/kenburns.json` | zoom/drift estimates per hold |
| `data/ocr_states.json` | OCR of white and red on-screen text per state |
| `reference/sheets/` | contact sheets of all 508 states (labelled id, time, duration) |
| `reference/strips/` | frame-by-frame strips of key animations (kinetic title, pops, slam, title card, callout fade, host-over-blur, punch-in, map pulse, string swing, pixel disintegration, crossfade, PIP, end-screen whip) |
| `reference/detail/` | magnified host, typography and expression crops |
| `scripts/` | the analysis scripts used: frame metrics, segmentation, alignment, measurements |
