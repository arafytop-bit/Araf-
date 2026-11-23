# Re-engineering Spec — "Doodle Finance Explainer" style

Source analysed: `The_SpaceX_IPO..._It_s_Worse_Than_You_Think_720p.mp4` (14:52).
Goal: rebuild this exact style around **your own voice-over + exact script**.

Everything below was measured, not guessed:
- **Video:** every one of the **21,410 native frames** was decoded and compared frame-to-frame.
  - The file is natively **24 fps**. Resampling to 30 fps would only duplicate every 4th frame, so the native-frame analysis already contains everything a 30 fps pass would.
  - All timings below are given in seconds, plus frame counts at both 24 and 30 fps.
- **Speech:** all 2,825 spoken words were transcribed with word-level timestamps (Parakeet-TDT ASR + Silero VAD).
- **Edits:** 640 visual edit events and 77 animation-loop swaps were detected and classified.
- **Review:** every event was reviewed visually.
- **Supporting files:**
  - `edl_visual_events.csv` (this folder) is the frame-accurate edit list.
  - Contact sheets of every state are in the session scratchpad: `…/scratchpad/sheets/`, `animsheets/`, `strips/`.

---

## 1. Technical format

| Item | Original | Recreation target |
|---|---|---|
| Resolution | 1280×720 (YouTube 720p rendition) | **1920×1080** (all px values below are given at 720p; ×1.5 for 1080p) |
| Frame rate | 24 fps CFR | **30 fps** (as requested) — all motion is time-based, converted below |
| Video codec | H.264 Main, yuv420p, ~60 kbps (mostly static frames) | H.264 High, yuv420p, CRF 18 |
| Audio | AAC-LC 44.1 kHz stereo 128 kbps | AAC 48 kHz stereo 192–320 kbps |
| Loudness | **−14.6 LUFS integrated, LRA 2.2 LU, true peak 0.0 dBFS** | −14 LUFS, LRA ≤ 3 LU, true peak −1.0 dBTP |
| Background | `#FFFFFF` (encodes as #FDFDFD) | `#FFFFFF` |

---

## 2. Script architecture (the template the original follows)

| Time | Block | What happens | Visual signature |
|---|---|---|---|
| 0:00–0:43 | **Cold-open hook** | Shocking claim → 3 escalating comparisons → "who is buying?" → twist "**the answer is you**" → promise ("NASDAQ quietly introduced a rule…") | Densest editing in the video (~1 change / 0.33–0.9 s); logos stack into bars **name-by-name** |
| 0:43–1:16 | **Setup / reframe** | "Before we get to the rule, you need to understand…" → common misconception (street-interview gag) → framing device: *The Good, the Bad and the Ugly* = 3 businesses | Comedy sketch with recurring side characters; 3 labelled boxes = structural motif |
| 1:16–3:29 | **Part 1 – "The ugly"** | Worst business first | Red handwritten section label top-left + **2.2 s music sting** (narration pauses) |
| 3:29–4:09 | **Part 2 – "The bad"** | Middle business | same label + sting |
| 4:09–7:01 | **Part 3 – "The good" (crown jewel)** | Best business, with a quoted expert clip (5:02–5:34) | same label + sting; embedded clip with "Source:" caption |
| 7:01–7:39 | **Callback / turn** | "So let's go back to the question from earlier…" → reveals the *real* story | Collage of the hook's charts (visual callback) |
| 7:39–9:17 | **Sponsor mid-roll** (≈ 92 s) | Pause line → sponsor → personal use case → demo → offer + promo code → "back to…" | **Yellow progress bar** pinned bottom-left |
| 9:17–11:35 | **Mechanism** (3 rule changes) + recap ("Here's what all this basically means") | Explained one by one, then summarised as a 3-item list | Chalkboard "teacher" shots, rules scroll, big typed text |
| 11:35–13:26 | **Widening + who pays** | "It's not just X…" → retail allocation → "you are the exit liquidity" | Bankers, CFO quote with yellow highlights |
| 13:26–14:00 | **Corrected summary + meta-joke** | "So here's the corrected version…" | Recap visuals reused |
| 14:00–14:05 | **Subscribe CTA** (inside the conclusion, not at the end) | "Hit subscribe" | "SUBSCRIBE!" big text + narrator arms up |
| 14:05–14:43 | **Closing argument** | Steel-man → twist → punchline last line | Callback to opening imagery |
| 14:43–14:52 | **End card** (≈ 8–9 s) | Outro music | "Subscribe for more <Channel>" + YouTube/social icons |

Script stats:
- **192 wpm** overall (205 wpm articulation).
- **189 sentences**, averaging 14.9 words each.
- Tone: casual, sarcastic, with asides ("Uh, sorry. I mean…"), censored swear, rhetorical questions.

---

## 3. Editing rhythm & word-sync rules (the core "algorithm")

### Measured numbers

**How often the picture changes**
- **640 visual changes in 892 s = 43 per minute.**
- Median hold between changes is **1.04 s** (mean 1.39 s, p10 0.29 s, p90 2.88 s, max 10 s).
- Hold distribution: 22% under 0.5 s, 24% 0.5–1 s, 32% 1–2 s, 18% 2–4 s, 4% over 4 s.
- About **4.4 spoken words per visual change**.
- **3.4 visual changes per sentence**; only 12 of 189 sentences have no change.

**Scenes**
- **111 scenes** separated by **hard cuts only**, with no dissolves or wipes (the single exception is one photo fading to white for "everyone left").
- Scene length: median 3.7 s, mean 8 s.
- Inside a scene, elements are *added* ("builds").

**Kinds of change**
- 414 instant pops (65%).
- 110 hard cuts (17%).
- 116 animated moves (18%): median 0.52 s, p75 1.1 s, p90 2.7 s.

**Sync to speech**
- A visual change starts **on the onset of a word, about 1 frame early**: median offset −30 ms.
- 59% land within ±2 frames, 87% within ±4 frames.

### Rules to apply to a new voice-over
1. **Beat segmentation.**
   - Every clause start is a candidate beat; 38% of changes land on the first word of a clause or sentence.
   - Every *keyword* inside a clause is a beat (the other 62%): numbers, money amounts, company or person names, list items, punch words ("combined", "ouch", "wrong").
2. **New sentence with a new idea → hard cut** to a new composition.
   - Same idea continued → **build** (add an element) or **swap** (change the narrator's pose or expression).
3. **Lists: one element per item**, popping exactly on each item's word. For example, 5 brand logos stack into one bar on "Coca-Cola, McDonald's, Disney, Nike, Starbucks".
4. **Numbers become visuals** at the number word: big text ("8 BILLION / in profit"), chart value, or a bar that grows.
5. **Contrast/negation** ("but both are wrong", "isn't even the most important") → **red X drawn over** the previous element.
6. **Asides and jokes** → tiny handwritten side-note (12–16 px at 720p) next to the subject. Examples: "ouch", "hehehe", "shh… you saw nothing", "my beloved", "ok that… was a bit dumb".
7. **Quotes or dialogue** → speech bubble (white, black outline, tail) beside a character.
8. **Rhetorical question to the viewer ("the answer is you")** → narrator **close-up pointing at the camera** (fist and index finger toward the lens).
9. **Callbacks** to an earlier topic → reuse the exact earlier visual (or a tiled collage of earlier charts).
10. **Comedic beat or pause** ("Mm.") → a **full black frame for about 1.2 s**, then a cut back.
11. **Swear word** → 1 kHz sine **bleep** over the word (0.10–0.17 s); written on screen with symbols.
12. Target density: **about 43 changes per minute, never more than ~10 s without a change**. Expect fewer during quoted clips and long animations, and 50–56 per minute in dense passages.

---

## 4. Scene/composition templates (visual vocabulary)

Approximate share of runtime, from a colour-signature tagger:
- Narrator on screen: ~24%.
- Celebrity caricature: ~11%.
- Dark screenshot/headline cards: ~17%.
- Mostly-white logo/text frames: ~16%.
- Chalkboard: ~5%.
- Real photo/video: ~3%.
- Black frames: 0.6%.

| # | Template | Layout (720p) | Typical triggers |
|---|---|---|---|
| T1 | **Narrator solo, centre** | Figure ~493 px tall (68% H), head ~199×186 px centred at x=640, y≈253; feet ≈ y 622 | Reactions, transitions, "So…", "But…" |
| T2 | **Narrator + chalkboard** ("teacher") | Narrator left (x≈150–250) with a pointer stick; board right (x≈700–1240, y≈80–500): green `#337A3C`, brown frame `#785743`, black outline. White text appears on it | Definitions, key terms, lists of reasons (lines added one by one; strike-through to negate) |
| T3 | **Narrator + object/chart** | Narrator left third, object right two-thirds | Explanations |
| T4 | **Narrator close-up pointing** | Huge head, fist toward camera, centre | "you" moments |
| T5 | **Logo hero** | Single logo centred, ~40–60% of width | Introducing a company |
| T6 | **Logo + annotation** | Logo plus a small handwritten note, or a doodle character beside it | Jokes, ownership ("mine") |
| T7 | **Headline / screenshot card** | Dark card centred top-half (~60% W); **red hand-drawn ellipse** around the key phrase; optional props below (money bags, fire) | Evidence for a claim |
| T8 | **Article excerpt with highlights** | Light card, key lines highlighted yellow `#F7E04A`, progressively | Quotes from filings or executives |
| T9 | **Data chart** (hand-drawn infographic) | Title in handwriting; bars with black outline; highlighted bar red; callout pill ("~35x") or yellow label "Largest IPO in history" | Valuations, comparisons |
| T10 | **Comparison bars with logo segments** | Reference bar (red) on top; second bar fills logo-by-logo | "Worth more than A, B, C combined" |
| T11 | **Big typed text** | Centre, handwriting font, black (or **red for the key number**) | Key phrases, dates, rules ("FAST ENTRY RULE", "3 MONTHS → 15 TRADING DAYS") |
| T12 | **Equation layout** | `[icon] + [icon]` → result text below ("8 BILLION / in profit") | Sums, cause→effect |
| T13 | **Timeline** | Horizontal row of years or calendar icons joined by red arrows, notes under each; **camera pans** along it | Chronology |
| T14 | **Dialogue sketch** | 2–3 characters, speech bubbles | Street interview, bankers, investors |
| T15 | **Desk scene** | Narrator at a desk with laptop (channel logo on lid), props around (charts, cork board, papers) | Personal/sponsor talk |
| T16 | **Split-screen A/B** | Two columns with a black divider and headers | Sponsor demo / comparisons |
| T17 | **Real photo or clip** | Inset ~45–55% W, centred, plus a handwritten caption ("+ 2 more!", "Source: …") | Quotes, people, memes |
| T18 | **Black frame** | Full black | Comedic pause |

**Recurring motifs**
- 3 grey boxes labelled "Business 1/2/3", which stack, open, and release logos.
- A "Rules" parchment scroll.
- A red carpet with the company logo walking on doodle legs.
- Money bags (pile up, catch fire).
- A green zig-zag growth arrow.
- Calendar icons.
- Briefcases (investment funds).
- An armchair with a sleepy investor (passive investing).

---

## 5. Animation library (exact timing)

**All motion is LINEAR (constant velocity), with no easing.**
- Bars grow at a constant 11.5 px/frame.
- The Earth shrinks at a constant 17.6 px/frame.
- Fly-ins move at a constant 16 px/frame.

When rebuilding, use linear keyframes.

| Effect | How it behaves | Duration / speed (measured) | @30 fps |
|---|---|---|---|
| **Hard cut** | Instant | 1 frame | 1 frame |
| **Pop-in** | Element appears at full size, no fade, no scale | 1 frame | 1 frame |
| **Staggered pops** | Several items appear one after another (crowd, money-bag pile, red X's) | 1–3 frames apart (0.04–0.125 s) | 1–4 frames apart |
| **Line boil** (characters only) | Character alternates **2 drawings A/B**, each held 8 frames; charts and logos never boil | 0.333 s per drawing (3 Hz) | 10 frames each |
| **Fire / flicker loop** | 2 drawings alternating | 7 frames each (0.29 s) | 9 frames each |
| **Typewriter text** | Characters appear one by one, in the handwriting font | ~1 char/frame ≈ 24–30 chars/s | 1 char/frame |
| **Line-by-line fade** | Each line of a paragraph fades in | ~5–8 frames per line | 6–10 frames |
| **Value-label fade** | Number label fades in after its bar finishes | 3 frames | 4 frames |
| **Bar grow** | Grows from axis, linear; then the label fades in | 0.4–1.0 s (~276 px/s @720p) | 12–30 frames |
| **Draw-on arrow** | Zig-zag growth arrow revealed along its path | ~0.7 s | ~20 frames |
| **Red ellipse / X / check** | Appears fully drawn (pop), occasionally drawn quickly | 1–3 frames | 1–4 frames |
| **Slow push-in** | Single object scales 1.0→1.6× about frame centre | 2.3 s (~26%/s) | 69 frames |
| **Scale-down entrance** | Object enters at ~2.5× and shrinks to 1.0× (Earth, Mars) | ~1.3 s | ~39 frames |
| **Fly/slide-in** | From off-screen edge to rest position (plane, yacht, papers) | ~1.1 s, ~450 px/s @720p | ~33 frames |
| **Peek-in** | Narrator's head rises from the bottom edge | slow, ~84 px/s for ~3 s | 90 frames |
| **Pan along timeline** | Whole canvas translates horizontally | 0.9–2.7 s | 27–80 frames |
| **Move-into-place** | Logo slides and shrinks to join another (acquisition) | ~0.5 s | 15 frames |
| **Pie-slice explode** | Slice translates outward, then label pops | ~0.4 s | 12 frames |
| **Tilt/rotate** | Scale beam tips; logo tilts and falls; rocket rotates and launches | 0.5–2 s | — |
| **Shatter / reassemble** | Logo split into 3–4 shards, then snaps back | cut + 4 frames | — |
| **Number ticker** | Year text swaps 2023→2024→2025 quickly | ~4 frames per step | 5 frames |
| **Fade to white** | Used once (people leaving a photo) | 1.1 s | 34 frames |
| **Clip inset** | Video plays full-frame, then shrinks to an inset beside a character | ~0.5 s shrink | 15 frames |

---

## 6. Character design sheet

### Narrator (the channel's avatar) — on screen ≈ 24% of runtime
- **Head:**
  - Slightly irregular hand-drawn oval, ~199×186 px in a solo shot.
  - Fill `#FCD4B4` (peach); outline **black, 5–6 px** at 720p.
  - **Messy black hair scribble** on the top-left of the head.
- **Face:**
  - Eyes are two small black dots (~8 px); brows only for emotions.
  - Mouths: smile arc (default) · big open smile (pink fill `#E8A0A0`) · "O" shock (pink inside) · frown · flat line · smirk · closed happy eyes "^ ^".
- **Body:**
  - Pure stick lines, **~6 px black**, round caps.
  - Neck and torso are one line.
  - Arms bend at the elbow; legs are an inverted V; no hands or feet drawn (except the fist in close-ups).
- **Proportions:** head ≈ 38% of the figure's height (big-head chibi).
- **Pose library (reused constantly):**
  1. Hands on hips (default "talking").
  2. One hand on hip.
  3. Hand-on-chin thinking (± raised eyebrow).
  4. Arms up celebrating.
  5. Shrug ("no idea").
  6. Pointing at camera (close-up, fist).
  7. Teacher with pointer stick.
  8. Holding microphone.
  9. Sitting at desk with laptop.
  10. Arm extended presenting an object.
  11. Peeking from the bottom edge.
  12. Big-head close-up with hand on chin.
- **Boil:** 2-drawing wiggle (arms and outline jitter ~2–4 px) on talking poses.

### Recurring cast (same doodle construction, varied hair, clothes and props)
- **Celebrity caricature:**
  - Cartoon (not stick) body: dark swoopy hair, black T-shirt with a logo, noodle arms that wiggle (boil), stick legs.
  - Appears small on charts and large in close-ups.
- **Street interviewer:** brown hair, microphone.
- **Interviewees:** grey-hoodie guy with sunglasses; bow-tie guy.
- **Investor / banker:** bald beige head, round glasses, green tie. Variants: heart sunglasses ("my beloved"), triplets of bankers.
- **Others:** venture capitalist (green shirt); woman with a hair bun (analyst); old lady and family (retail investors); robot (passive investing); hooded shadowy figure (insiders); runner with headband.
- **Logos with legs:** company logos get doodle legs, arms and sometimes a headband or googly eyes, and act as characters.

---

## 7. Props & drawing style

Shared style:
- Thick black outline (~3–5 px @720p) with slight wobble.
- Flat fills with a little simple shading.
- No gradients or textures.
- Doodle-icon look.

Frequent props:
- Money bag (`#6E8972` with gold `$`) and cash bills.
- Rocket (grey/white with orange flame).
- Earth (navy `#233265` / green / white), Mars (orange `#D4623B`), satellite (blue panels).
- Shipping box.
- Calendar icon (red header).
- Document / "Rules" scroll (parchment `#D6C4AA`).
- Briefcase, oil barrel, laptop and desk, chalkboard, cork board with red string.
- Newspaper "BREAKING NEWS!!!", scale of justice, armchair, buildings (bank, parliament).
- Red arrows, red X, green check, question marks, "Top Secret" docs.

Annotations:
- **Red ellipse** (rough, 4–6 px, `#C8232A`) circling the key phrase.
- **Red arrows** (`#C13725`).
- **Green check** (`#1BB935`).
- **Yellow highlighter** (`#F2DC3C`, 60% opacity) over text lines.

---

## 8. Typography

- **One handwriting family for everything.** Best match among 45 fonts tested is **Gaegu** (Google Fonts, SIL OFL, free for commercial use). It shares the wide letter spacing, serifed capital "I", hooked "f" and curved "t".
  - **Gaegu Bold** for headline words.
  - **Gaegu Regular** for notes.
  - The exact original font can't be confirmed from pixels; Gaegu is visually very close.
- Sizes @720p:
  - Hero words ("FAST ENTRY RULE", "3 MONTHS", "SUBSCRIBE!"): cap height 55–75 px.
  - Chalkboard text: ~28–40 px (white).
  - Labels and section titles ("The ugly"): ~28–32 px.
  - Side-notes: 12–16 px.
- Colours:
  - Black `#111111` default.
  - **Red `#E4141C` for the key number or word** ("COMBINED!", "15 TRADING DAYS", "5–10%", "CASUAL").
  - **Green `#1BB935`** for positive words ("FREE").
  - White on the chalkboard.
- Hierarchy trick: a small lead-in line above a big red word ("more than all / **COMBINED!**", "Usual IPO = **5–10%**").
- Chart numerals: bold rounded sans (Comic Neue Bold is a good match).

---

## 9. Colour palette (measured, k-means over all frames)

| Role | Hex |
|---|---|
| Background | `#FFFFFF` |
| Ink / outlines | `#000000`–`#111111` |
| Narrator skin | `#FCD4B4` (shading `#F6D3B5`) |
| Other skins | `#D6C4AA` (beige), `#DAAA7E` (tan), `#987F71` |
| Accent red (text) | `#E4141C` / `#EC141C` |
| Accent red (arrows/X/ellipse) | `#C13725`, chart red `#D50F12` |
| Chalkboard | `#337A3C`, frame `#785743`, dark brown `#4F3322` |
| Positive green | `#1BB935`, chart green `#61C862`, money `#6E8972` |
| Chart blue | `#3663BB`; navy `#233265` |
| Orange | `#D4623B` |
| Yellow (progress bar / labels) | `#ECD40C` / `#E4CD1B` |
| Teal (Nasdaq-like) | `#0487B4` |

---

## 10. Audio design

- **Voice:**
  - Dry, close-mic male VO, **mono** (L = R), heavily compressed and limited.
  - Integrated −14.6 LUFS, LRA 2.2 LU, peaks at 0 dBFS.
  - Noise-gated: silences between phrases fall to −80/−90 dB (digital silence).
- **Pauses are edited out:**
  - Median pause 0.08 s after a sentence and 0.0 s after a comma.
  - Median 0.29 s between speech chunks; longest 2.7 s.
  - In other words, a jump-cut VO.
- **No background music bed** under the narration (the stereo side channel is −∞ dB for 99% of the runtime).
- **No pop/whoosh SFX** on visual pops; the edit is silent apart from the voice.
- **Music stings:**
  - Three stereo stings, **2.15–2.2 s each**, placed in deliberate narration pauses at each chapter label ("The ugly / bad / good").
  - The original uses a famous film theme, which is copyrighted, so the rebuild needs a royalty-free or original sting.
- **Censor bleep:** 1000 Hz sine, 0.10–0.17 s, over the swear word.
- **Outro:** stereo music bed ~6–9 s under the end card.
- **Quoted clip:** the clip's own audio (with room tone) for its length.

---

## 11. Sponsor-segment template (if your script has one)

- **Lead-in:** "…a quick pause, because this video is sponsored by X."
- **Yellow progress bar `#ECD40C`:**
  - 26 px tall @720p (≈39 px @1080p), anchored bottom-left.
  - Fills **linearly** from 0 at the first sponsor word to 100% at the last ("…for sponsoring this video"), then disappears.
- **Visual beats:**
  - Narrator at a chalkboard with the sponsor's logo.
  - Narrator with a mic.
  - Desk-and-laptop sequence.
  - Doodles of the use case.
  - Sponsor logo walking on legs.
  - A/B split-screen demo.
  - Offer card: "<Brand> **FREE** for 1 month!" with "Promo code: **CODE**" in red.

---

## 12. End card

- 8–9 s on a white background.
- Small YouTube logo and social icons on the left, with a handwritten "only on" arrow.
- "Subscribe for more" over **<Your channel name>** (bold).
- Outro music.

---

## 13. Rebuild pipeline (what will happen when you send the audio + script)

1. **Alignment:**
   - Word timestamps for your audio come from Parakeet-TDT ASR, aligned to your exact script text, so the timing is frame-accurate.
   - Your audio is not altered unless you ask. Optional extras: pause-tightening to the original's ~0.1 s, −14 LUFS normalisation, inserted sting pauses, bleeps.
2. **Beat map:** the script is segmented into clauses and keywords (rules in §3), aiming for about 43 visual changes per minute.
3. **Storyboard:** each beat is assigned a template (§4), an animation (§5), and character pose and expression (§6). This is saved as an editable `storyboard.json` before rendering.
4. **Assets:**
   - **Procedural:** stick figures, props, charts, bubbles, arrows and ellipses are drawn as SVG, with a hand-drawn wobble and 2 boil variants each.
   - **Logos:** Iconify `logos` and Simple Icons.
   - **Extra doodle icons:** Fluent Emoji Flat (MIT), restyled with black outlines.
   - **Fonts:** Gaegu and Comic Neue (OFL).
5. **Render:**
   - Rendered at 1920×1080, 30 fps (resvg + numpy compositor), with linear motion and boil on characters.
   - Encoded H.264 + AAC, loudness-checked.
6. **Delivery:** the MP4, plus the storyboard and asset folder so individual shots can be revised.

### Prototype status (already working in this repo)

Files:
- `tools/doodle.py` draws the narrator procedurally:
  - 8 poses × 6 mouths × brows.
  - Messy-scribble hair.
  - 2 seeds per pose, giving the A/B boil.
  - Also a chalkboard, handwritten text (Gaegu), red X and red ellipse.
- `analysis/style_test_30fps.mp4` is a 4 s, 1920×1080, 30 fps test. It shows:
  - Boil every 10 frames.
  - Expression swap at 0.8 s.
  - A lead-in line at 1.2 s, then the red hero word at 1.5 s.
  - A hard cut at 2.4 s, then typewriter text on the board at 1 char/frame.
- Render speed: static frames are cached, so a 4 s test renders in under 4 s.

Layout calibration learned from the prototype (1080p):
- Hero word ≈ 33% of frame width (font ≈ 215 px for a 9-letter word); lead-in line ≈ 60 px.
- Chalkboard ≈ x 760–1820, y 110–770, frame 40 px; board text ≈ 150 px, spanning ~60% of the board.
- Narrator solo: head-top y ≈ 200–230, figure ≈ 690–740 px tall.

## 14. What I need from you
- **Audio file:** WAV/MP3/M4A of the voice-over.
- **Exact script text.**
- **Channel name** (for the laptop logo and end card) and any sponsor details (name, offer, promo code).
- **Evidence and media:**
  - Screenshots of the news articles, tweets or filings you reference, if you want real "evidence cards".
  - Any real photos or video clips you have the rights to use (quoted interviews, memes).
  - Without these, I'll use neutral text cards and doodle substitutes, and will **not** fabricate headlines under real outlets' branding.
- **Output preferences:** confirm 1920×1080 @ 30 fps, and whether you want pause-tightening, stings and an outro sting (original or royalty-free).

## 15. Rights notes
- **Fonts and icons:** Gaegu and Comic Neue are SIL OFL; Fluent Emoji is MIT.
- **Company logos:** used nominatively for commentary, the same way the original does.
- **Not reused** (all third-party copyrighted): the original's footage, memes, film-theme stings, news screenshots and the original channel's branding ("CF" laptop logo, end card).
