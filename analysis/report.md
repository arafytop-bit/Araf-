# Re-engineering report: "What If You Were Born as Arthur Morgan" (Born in Lore format)

Reference file: 480p download (854×480, 30 fps CFR, 16,731 frames, 557.7 s). Clock: frame N = N/30 s, counted from 0. Audio features use a hop of 1,470 samples at 44.1 kHz, so audio index N is video frame N; both streams start at pts 0.

Everything below was measured with tools unless marked **(inferred)**. The machine-readable version is `analysis/blueprint.json`, and every number traces to a file in `analysis/data/`.

---

## The Formula

1. **You are the hero, in the second person.** The narration is "If you were born as X…" told as a life story from birth to death. 52% of sentences contain *you/your/you'd*. It runs at about 155 wpm, with short sentences (median 7 words, 90th percentile 13).
2. **The hook is a promise plus an open loop, inside 12 s.**
   - Frame 0 shows the hero portrait, already moving.
   - The first word lands at 0.40 s (f12).
   - The name title appears at f37, 2 frames before the name is spoken.
   - The first cut is at f68 (2.3 s).
   - Three iconic deeds are listed and stamped on a wanted poster (f86/116/132).
   - Then a question, "And the thing that finally takes you down?" (f275).
   - The music drops out for 0.8 s and the payoff lands: "Not a bullet, a cough." (f340). That loop isn't closed until Chapter V, five minutes later.
3. **One sentence, one shot.** There are 226 shots. The median shot is 66 f (2.2 s), interquartile range 50–87 f, minimum 12 f. 62% of shots contain exactly one sentence start. The cut rate is 21.6 cuts/min, and 89% of shot changes are hard cuts.
4. **Cuts pre-lap the voice by 3 frames.** 95% of cuts land 0–6 f before the next word onset (median 3 f; the histogram mode is −3 relative to the sentence start). Cuts sit in the pause between sentences, whose median length is 17 f; only 17% fall inside a word. 77% of sentences open on a fresh cut.
5. **Every key noun gets an object on screen, timed to the word.**
   - Names, numbers, time jumps and verdict words all get a graphic.
   - The element's first frame is the word onset plus 0…+5 f (median +4).
   - By type: name tags +5 f, labels +3.5 f, stamps +5 f, bubbles +1 f, list items ≈0 f.
6. **The element is chosen by what the word means.**

   | The word is… | It gets… | Look |
   |---|---|---|
   | A person | Name tag | White card, NAME plus a lowercase descriptor |
   | A time jump or rating | Gold outlined label | Gold caps with a dark outline |
   | A verdict (TROUBLE, SAVED, MASSACRE, RAT) | Red rubber stamp | Red word in a double rounded border |
   | A quote | Speech bubble | White rounded box with a long tail |
   | An enumeration | List items with stamped icons, or polaroid sets | See templates |
   | A number | Counter | Number with a small caption |

7. **Pops are springy and tilted.**
   - **Tags and labels:** pop on a spring with ω₀ ≈ 0.61 rad/frame and ζ ≈ 0.54. They start at 0.35×, overshoot to 1.13× at +5 f and settle at +9 f. They rotate linearly from about −11° to −2° (+1°/f).
   - **Bubbles:** pop on a stiffer spring (ω₀ ≈ 0.72, ζ ≈ 0.57), settling at +7 f and rotating from −8° to 0°.
   - **Exits:** nothing animates out; elements disappear on the next cut.
8. **Stamps slam.** There are two ghost frames at 1.5–1.8× scale and 25–45% opacity, then one full-opacity frame at about 1.1×, then 1.0×. The tilt is −6…−8°. This is the only overlay with a guaranteed sound: a thump on the slam.
9. **The camera never rests, and it works in layers.**
   - **Idle drift:** every shot drifts, mostly a slow push-in (46% of shots push in, 25% pull out, 25% are static). Moving shots average 1.4%/s of zoom (90th percentile 4.8%/s).
   - **Parallax:** foreground characters scale 5–10× more than the background. In shot 0 the hero goes 1.00→1.105 while the sky goes 1.00→1.008.
   - **Detail punches:** when narration names a detail, the camera punches in fast: ×1.42 over 7 f with an ease-out of cubic-bezier(0.29, 0.64, 0.38, 1.04).
   - **List nudges:** a 4 f re-frame 3–4 f before each list item.
   - **Reveals:** a 21 f ease-in-out pull-out.
10. **Chapter cards: a 72-frame breath every 30–70 s.** The sequence is a scene fade-out (9–10 f), black (about 9 f), then the card visible for about 36 f (8 f in, 20–25 f hold, 9 f out), black (about 6 f), and a scene fade-in (11–12 f). The card is black with a gold revolver emblem, "CHAPTER I"…"IX" in tracked gold caps, and a cream Grenze Gotisch title. It gets a low boom plus a new music cue. There are nine cards; these are the only fades in the body of the video.
11. **Running callbacks.** The video plants three devices early and revisits each 3–7 times:
    - "Remember that hat" (f1196) runs to the HAT label, then Chapter IX "The Hat", then "an angry kid with no hat".
    - The THINGS TO REMEMBER notebook (7 appearances) gets red strikes and corrections: DOES HE? / ? / BROTHER.
    - A "PLANS THAT WORKED" tally sign appears 4 times.
12. **The look.** Flat, outlined 2D cartoon characters (big-head child versions, then semi-realistic adults) sit over painted Western backgrounds. The grade has a strong vignette (corner luma 63% of centre), rich saturation (median HSV S 130/255), deep blacks (2nd-percentile luma 8) and warm palettes: sunset orange/purple, wood brown, night navy. Dust motes, sparkles, light rays and fire flicker run in almost every shot.
13. **The type system is one superfamily.**
    - **Alegreya** ExtraBold for titles and Alegreya Bold Italic for book captions.
    - **Alegreya Sans** ExtraBold for tags, bubbles and labels.
    - **Grenze Gotisch** for chapter titles.
    - A heavy serif (**Source Serif 4 Black**, medium confidence) for the wanted poster.
    - A slab italic (**Arvo Bold Italic**, medium-low confidence) for the notebook.
    - All are free Google Fonts.
14. **The sound is voice-forward.**
    - **Voice:** −13.95 LUFS. The music and SFX bed is −28.5 LUFS, so the bed sits 14.6 LU under the voice. It ducks about 3 dB under speech (attack about 60 ms, release about 150 ms; inferred, medium confidence).
    - **Master:** −14.0 LUFS integrated, LRA 4.7 LU, −1.3 dBTP. The voice is mono and the bed is wide (L/R correlation 0.65).
    - **Music:** acoustic Western cues (plucked guitar/banjo-like, bass on the beat with a "boom-chick" feel, pads), mostly about 120 BPM. Cues change at section and mood changes (median segment 8 s by novelty), and the music drops out before punchlines.
    - **Cuts and beats are not linked:** 25% of cuts fall within ±2 f of a beat, against 27% for random frames.
15. **Silent pops, loud impacts.** Event-locked averages show no SFX on tags, labels, bubbles or arrows. Consistent SFX appear only on:
    - **Stamps:** a high-band peak of +11 dB, 2 f after the first ghost frame.
    - **Stamped icons.**
    - **Counters:** a tick on the first frame.
    - **Chapter cards:** a boom/swell from +2 f.
    - **Polaroids:** a shutter-like transient.
    - **Diegetic action:** paper, gunshots, coughs.

    There are about 30 detectable transients per minute.
16. **The ending closes the loop.** The last lines call back to the opening ("You robbed half the West…", "an angry kid with no hat"). The final question, "would you still follow Dutch?", feeds a storybook end screen that asks "Which character should be born next? Tell me in the comments", with a wax-seal subscribe button. Mid-roll CTAs come at 19% (subscribe scroll) and 40% (comment panel).

---

## Calibration result (first 5 s rebuilt from `blueprint.json` alone)

- Renderer: Remotion, `render/src/Calibration.tsx`. It reads only `blueprint.json` (style tokens, templates, and the `calibration` edit plan) and draws code-generated placeholder art.
- Audio: the reference track, used for timing only.
- Video: `analysis/calibration/calibration_side_by_side.mp4` (reference on the left, rebuild on the right, frame counters burned in).
- Keyframe sheets: `v1_keyframes_sbs.jpg` and `v3_keyframes_sbs.jpg`.
- Checks: `analysis/scripts/a20_calibrate.py` measures the rebuild with the same tools used on the reference. That means SIFT camera tracking, band contrast for text, red-pixel geometry for icons, persistent-step detection for the reward counter, and onset detection on a synthesized SFX track compared against the reference drums-stem onsets.

| Pass | Checks | Mismatches > 1 frame | What was fixed |
|---|---|---|---|
| v1 | 81 | 24 | Detector artifacts (reward jitter, background bands, "n/a in both" counted as misses). Real issues: title opacity ramp 4 f too short, pull-out vertical move using the scale easing (31 px error), SFX tick placed at 137 (reference onset 123), stamp cue at 132 (reference 130), second paper flutter masked |
| v2 | 59 | 8 | Title rule drawn at y = 432 instead of 418 px. MORGAN and "(that's you)" fades 2 f short. Checker windows overlapping the neighbouring list row |
| **v3** | **59** | **0** | All cut, motion, text, list-item, counter and SFX events within ±1 frame (38 exact, 21 at ±1) |

Residual accuracy in v3 (`analysis/calibration/v3_mismatches.csv`, `v3_camera_compare.csv`):
- Camera scale error: median 0.03%, max 0.6%.
- Camera vertical position: median 1.6 px, max 7 px at 480p.
- Hero-layer scale: max 0.24%.

Not reproduced (below the 1-frame threshold, or placeholder-only):
- The exact layout of the side posters revealed at f145–161 (approximate positions).
- Birds, light rays and dust in shot 0.
- About ±2 px of micro-jitter on holds (likely encoding).
- The character art itself.

---

## 1. Specs

| | Value |
|---|---|
| Video | H.264 Main, 854×480 (SAR 1:1, 16:9), yuv420p, BT.709 TV range, ~269 kb/s. A 480p re-encode of a ≥1080p master |
| Frame rate | 30/1 CFR; frame pts deviate ≤ 3.3×10⁻⁷ s from N/30; 228 I-frames |
| Duration | 16,731 frames = 557.7 s (audio 557.77 s) |
| Audio | AAC-LC 44.1 kHz stereo ~128 kb/s; start offset 0 for both streams |
| Loudness | −14.0 LUFS integrated, LRA 4.7 LU, true peak −1.3 dBTP, sample peak −1.28 dBFS |
| Overlays to ignore | None. No platform watermark or screen-recording UI. The end-screen disclaimer is part of the video (for a new subject it must name that IP's owners) |

The 480p source limits measurement. Fine strokes and grain are blurred. All sizes are reported in reference pixels (854 wide) and as percentages, so they scale to 1920×1080 (×2.248).

## 2. Structure and script

Transcript: `data/transcript_whisper.txt` and `data/words.json` (1,411 words). Word timing comes from MMS forced alignment, cross-checked against Whisper medium.en. On word onsets after pauses, the forced aligner had a median error of −0.4 f (53% within ±1 f), against −1.6 f for Whisper. 434 words disagree by more than 2 f between the two methods, so treat onsets as ±2 f.

Beat map (`blueprint.structure`):

| Section | Frames | s | Words | wpm | Job |
|---|---|---|---|---|---|
| Hook / cold open | 0–419 | 14.0 | 36 | 154 | Promise (iconic deeds on a wanted poster), MOST WANTED stamp, gang silhouettes, open loop "the thing that takes you down? Not a bullet, a cough." |
| Storybook + Prologue "The Wildest Kid" | 420–4422 | 133.4 | 352 | 158 | Birth, parents, the hat plant, mentors arrive (name tags), the notebook plant, first heist, love story |
| I Blackwater | 4423–6046 | 54.1 | 148 | 164 | Escalation: the job goes wrong (MASSACRE), the gang flees into snow |
| II The Debt | 6047–7434 | 46.3 | 123 | 160 | Camp life plus comment-panel pattern interrupt (f6631–6934); the debt collection that infects you |
| III One Last Job | 7435–9004 | 52.3 | 129 | 148 | The plan, the city, the robbery fails (ARRESTED) |
| IV Guarma | 9005–9622 | 20.6 | 55 | 160 | Comic detour (LONG STORY), "DOES HE?" correction |
| V The Cough | 9623–10298 | 22.5 | 55 | 146 | Twist: tuberculosis. Pays off the hook's open loop |
| VI A Good Man | 10299–11298 | 33.3 | 98 | 176 | Redemption arc: helping people, the letter |
| VII The Rat | 11299–13063 | 58.8 | 161 | 164 | Betrayal revealed (RAT stamp, Micah's plan) |
| VIII Go, John | 13064–15157 | 69.8 | 150 | 129 | Climax: the sacrifice, the death; 13.7 s wordless hold with a music swell |
| IX The Hat (epilogue) | 15158–16438 | 42.7 | 104 | 146 | Aftermath, the grave, callbacks, closing question |
| End screen / CTA loop | 16439–16730 | 9.7 | 0 | – | Storybook end screen: question + "which character next?" + subscribe |

**Hook forensics.**
- **Frame 0:** a hero bust at sunset. The foreground scales from frame 0 (easing out to +5% by f33, then +5% more at f35–46, in time with the title).
- **Sound:** 10 f of near-silence, then the voice and a music pad enter together at f10–12. The first word "If" is at f12.
- **First visual change:** title line 1 at f37 (1.23 s).
- **First cut:** f68 (2.27 s), followed by a paper-slap SFX at f70.
- **First enumerated payload:** f86–137.
- **First stamp:** MOST WANTED at f221 (on "wanted", f222).
- **First music dropout:** f318–342, just before the "a cough" payoff at f340.

**Retention devices.**
- **Pattern interrupts:**
  - nine chapter cards (2:27, 3:22, 4:08, 5:00, 5:21, 5:43, 6:17, 7:15, 8:26);
  - the subscribe scroll (1:48);
  - the comment panel (3:41);
  - the HONOR HUD (f7086, 10401, 14715);
  - counters (COUGHS TODAY 41→109, LEFT BEHIND 1→2, $730→$5,000).
- **Change rate:** visual events (cuts plus text/graphic/UI entries) run about 100/min in minute 1, 70–90/min in minutes 2–6, and 50/min in minutes 7–8 as the story slows.
- **Open loops:**
  - "the thing that takes you down?" (paid off at f9623);
  - "Remember that hat" (paid off at f15178 and in the last line);
  - the notebook items (each re-evaluated later).
- **Loop to the start:** the closing lines re-use the opening's "half the West" and "no hat" phrasing, then ask the viewer a question.

**Script mechanics.**
- **Questions:** 7, all used as hinges.
- **Contrast lines:** "Not X, Y." and "No gang, no gun, not even a hat."
- **Triads:** "trains, banks, and half the wild west"; "riding, shooting, and stealing"; "Big, tough, fast…".
- **Time-jump openers:** "Years later", "Years pass", "Two days later", "8 years later".
- **Humor beats via understatement:** "You're not even on the boat."
- **Pauses:** within sentences, median 1.8 f; between sentences, median 18 f (IQR 16–30 f); the longest is 426 f (the death scene).

## 3. Edit

Full shot list: `data/shots.csv` / `shots.json` (226 shots). It covers start/end frame, duration, camera kind and totals, luma, saturation, 6-colour palette and an agent-written content description. Cut list and soft transitions: `data/cuts.json`.

Cut detection used three methods: per-frame SSIM/MAD/histogram dips, PySceneDetect AdaptiveDetector, and the 12 review agents' logged cuts. 16 ambiguous candidates were checked on frame strips (`frames_events/ambiguous_cuts_*.jpg`). Pose swaps and lightning or impact flashes were rejected as cuts.

- **Shot length:** median 66 f, mean 74, 10th percentile 40, 25th 50, 75th 87, 90th 110, min 12, max 411.
- **Words per shot:** median 6 (90th percentile 10).
- **Source type:** 100% original 2D vector-style illustration and motion graphics.
  - Characters are rigged cut-out puppets. They move by limited-animation pose swaps on held backgrounds (e.g. f14100, 14116, 14131), plus idle bob and blinks.
  - There is no live footage, stock or 3D. The channel says "All illustrations, animation and music are original". The production method (hand-drawn vs AI-assisted then vectorised) is **(inferred)** and can't be determined from the frames.
- **Transitions:** 201 hard cuts (89%). The soft ones are:
  - nine chapter fades through black (72 f template);
  - two storybook zooms (420–427 zoom out from the scene into the book; 528–533 zoom through the picture into the scene) plus a page-flip montage (432–462);
  - flashes that hide cuts (camera flash 960–962, photo-develop 2196, gun flash 12819–12824, cream fade 2637–2646, white fade 5629–5636);
  - a thought-bubble zoom-through (8091–8092);
  - comment-panel dissolves (6630–6640, 6922–6935);
  - an end-screen dissolve (16439–16443);
  - a final fade to black (16714–16727).

  There are no whips, glitches or J/L-cut tricks beyond the 3 f pre-lap.
- **Rhythm:** cut timing follows the speech (rules 3–4), not the music.

## 4. Motion

- **Camera model:** 2.5D, with layers scaled separately. Evidence comes from SIFT tracking of separate regions (`data/tracks/`). Shot 0:
  - background: s 1.000 → 1.008;
  - hero: s 1.000 → 1.052 over f0–33, eased with cubic-bezier(0.005, −0.006, 0.378, 0.724);
  - hero, second push: 1.053 → 1.103 over f35–46, eased with cubic-bezier(0.13, 0.015, 0.219, 0.965);
  - anchor: (569, 181) px, i.e. (66.6%, 37.7%) of the frame, which is the face.
- **Shot 1 camera keys** (world = frame-75 view, frame centre c = (427, 240)):

  | Frames | Move | Easing |
  |---|---|---|
  | 68→72 | Settle 1.22 → 1.00 | cubic-bezier(0.726, −0.047, 0.701, 1.042) |
  | 82→89 | Push-in to 1.42, ty −2.5 → −123.3 | cubic-bezier(0.293, 0.639, 0.382, 1.037), which matches easeOutCubic |
  | 112→118 | Nudge ty −123 → −145 | cubic-bezier(0.25, 0.6, 0.4, 1) |
  | 127→133 | Nudge ty −145 → −163 | cubic-bezier(0.3, 0.3, 0.45, 1) |
  | 140→161 | Pull-out 1.42 → 0.50 | log-scale ease cubic-bezier(0.653, −0.066, 0.479, 0.961); ty ease cubic-bezier(0.581, 0.017, 0.326, 1.082) |

- **Whole-video statistics** (`data/shots.csv`):
  - shot mix: 25% static, 46% push-in, 25% pull-out;
  - zoom rate on moving shots: median 1.4%/s, 90th percentile 4.8%/s;
  - rotation: none (< 0.1°);
  - shake: none;
  - motion blur: none (speed lines are drawn for action).
- **Element motion:** measured per frame from white/red pixel geometry (`data/element_curves.json`). The keyframe tables are in `blueprint.templates`:
  - **Name tag:** scale 0.35, 0.70, 0.93, 1.06, 1.12, 1.13, 1.10, 1.06, 1.01, 1.00 (f+0…+9). Rotation −11.5° → −2.5° linear. Fixed centre.
  - **Bubble:** 0.53, 0.87, 1.03, 1.10, 1.10, 1.08, 1.03, 1.00. Rotation −8.3° → 0°. Anchored at the tail.
  - **Stamp:** scale 1.8, 1.5, 1.12, 1.0 with opacity 0.25, 0.45, 1, 1.
  - **Stamped icon:** scale 1.75, 1.62, 1.23, 1.0 with opacity 0.35, 1, 1, 1. It starts 1 f after its text, whose opacity runs 0.2, 0.78, 1.0.
  - **Hero title:**
    - lines stagger 3 f, each fading over 8 f;
    - letter-spacing tightens by 4.8 px per gap at the start, over 10 f with an ease-out;
    - the rule draws out from its centre over f40–49, with its diamond at f48–50;
    - the sub-line fades over f45–50.
  - **Arrows:** draw on over 10 f, starting 3–4 f after their label, with the arrowhead on the last frame.
  - **Typewriter text:** about 1 character/frame (23 characters in 30 f).
  - **Tally strokes:** 4–6 f each.
  - **Counters:** tick slowly, then accelerate to 1 step/frame.
- **Character animation** (observed by the agents; amplitude not measured): idle bob, blinks, mouth flaps on quotes, gesture pose swaps, walk-ins and walk-outs. Silhouette scenes use dissolves of 4–18 f.

## 5. Text, captions, graphics

**No narration captions.** The video carries no burned-in subtitles. All on-screen text is labels, signs and props (296 text/UI events in `blueprint.text_track`, each with first/last frame, class, exact text, position and the matched spoken word).

**Fonts.** Identified by rendering each reference string in 1,309 font files (179 Google families, all weights) and scoring glyph-mask IoU with a fitted outline and tracking (`fonts/font_match*.json`, `fonts/cmp_*.png`):

| Use | Font | Confidence |
|---|---|---|
| Hero title, poster names | Alegreya ExtraBold (800), tracking ≈ 0.15 em | High (joint IoU 0.81, rank 1) |
| Book captions, "(that's you)" | Alegreya Bold Italic (700i) | High |
| Name tags, bubbles, labels, counters | Alegreya Sans ExtraBold (800); sub-lines 500 | High for bubbles (0.83–0.85); medium for tags (tilt) and outlined labels |
| Chapter titles | Grenze Gotisch ExtraBold/Black | High (0.82) |
| "CHAPTER I" | Patua One, tracking 0.40 em (alt Alegreya SC) | Medium |
| Wanted poster | Source Serif 4 Black (alt Kameron 700, Literata 800) | Medium |
| Notebook lines | Arvo Bold Italic (alt Zilla Slab Bold Italic) | Medium-low |
| Map and letter handwriting | Not matched; closest free fonts are Caveat 600 or Kalam 700 | Low |

**Styles.** Exact values are in `blueprint.style_tokens`.

| Element | Size (cap height, % of H) | Colours | Stroke / shadow | Box |
|---|---|---|---|---|
| Hero title | 5.9% | Fill #e7d5bc | Outline #3f1f0e (0.31% H); drop shadow 0.3/0.6/0.8% H at 55% | — |
| Name tag | Main 3.4%, sub-line 1.5% | Text near-black #090300 | Card shadow | White #f8f2ea, radius 1.5% H |
| Label | 3.3% | White or gold #ead999 | Outline #140800 (0.5% H) | — |
| Bubble | 3.2% | Text #030305 | — | Radius ≈ 4% H, long tail |
| Stamp | 5.0% | Red #cb231e | — | Double border |
| Chapter card | Title 5.5%, number 2.2% | Gold #cfa65a | — | — |
| Corner tag | 1.6% | — | — | Translucent dark |

**Positions.**
- **Hero title:** a left block at 6.9% W, with baselines at 73.8% and 84.0% H.
- **Tags:** sit in the top third near the person (centres such as (31%, 13%), (30%, 19%), (51%, 14%)).
- **Stamps:** upper third (y 12–28%).
- **Labels:** beside their referent, with an arrow when they aren't adjacent.
- **HUDs:** top-left (14%, 5%) for HONOR and (9%, 9%) for counters; top-right (83%, 7%) for the game/year tag.
- **Margins:** nothing in the bottom 10% except the end-screen disclaimer, and at least about 2.6% from the frame edges. Being 16:9 long-form, there are no platform buttons inside the frame.

**Chunking.**
- **Tags:** 1–3 words in caps plus a 1–3 word lowercase descriptor ("smooth talker", "con man", "new guy").
- **Labels:** 1–3 words.
- **Bubbles:** 2–6 words, sentence case, ≤ 14 characters per line, 1–3 lines.
- **Stamps:** 1 word (2 at most).

**Timing.** See §8. Elements appear 0…+5 f after their word and almost never animate out; the next cut removes them. Corner tags and HUDs persist across cuts, with 5–6 f fades.

**Emphasis rules.** Text goes on:
- proper names (tags);
- numbers and money (counters, poster reward);
- time jumps (gold labels);
- verdicts and outcomes (red stamps);
- quoted speech (bubbles);
- enumerated lists (poster rows, polaroids, chalkboards);
- corrections (red strike plus red typed word in the notebook).

Colour carries meaning: red = verdict/correction, gold = time/rating, white = fact.

**Element inventory** (agent logs; counts are approximate): name tags 45, outlined labels 65, list lines 44, stamped/red icons 67, arrows 39, speech bubbles 24, polaroids 20, stamps 17, signs 15, handwriting 15, counters 12, circles 12, chapter cards 9, tally strokes 6, HUD meter 7, plus particles/sparkles about 60. Agent logs with exact frames: `visual_review/part_00…11.jsonl`. The consolidated log, matched to the words, is `data/visual_events.json`.

## 6. Colour, texture, layout

- **Grade (all frames):**
  - luma: median 84 (10th percentile 26, 90th percentile 130);
  - contrast: 2nd/98th-percentile luma 8/213;
  - saturation: median HSV S 130;
  - vignette: strong, with corners at a median 0.63 of centre luma (10th percentile 0.26 on night scenes);
  - no grain, chromatic aberration or VHS overlays are visible at 480p.
- **Glow:** bloom on light sources (sun, moon, candles, lanterns).
- **Palettes:** per-shot palettes (6 k-means colours) are in `shots.csv`. The recurring families are:
  - sunset (#4c2737 → #d1803c, sun #ffe2a0);
  - night (#0d173c navy with warm lamp glow);
  - interior wood (#723810 / #68330e);
  - parchment (#e5c180 / #d4c097);
  - snow (cool greys and blues);
  - flashbacks in sepia.
- **Atmosphere:** floating dust motes and twinkles, light rays from the sun or windows, fire flicker, snow and rain particles, breath vapour.
- **Layout templates:**
  - full-bleed illustrated scene (≈90%);
  - prop close-up on a desk or wall (poster, notebook, map, letter, polaroids);
  - black chapter card;
  - storybook spread (open/end);
  - UI overlays (comment panel, subscribe scroll, HUDs).

  There are no split screens or picture-in-picture.

## 7. Sound design

Stems: Demucs htdemucs (vocals/drums/bass/other), used for analysis only. Spectrograms with 1-frame gridlines: `spectrograms/spec_*.png` (56 pages of 10 s each) and `spectrograms/zoom_0000_0165_events.png`.

- **Voice** (`data/voice_stats.json`):
  - **Pitch:** male, baseline f0 ≈ 115–135 Hz, emphasis peaks at 200–235 Hz (median 152 Hz, 5th–95th percentile range 12.8 semitones, sentence declination −3.4 st).
  - **Rate:** 155 wpm, 3.2 syllables/s overall, 5.0 syllables/s articulation.
  - **Spectrum:** steep high-pass ≈ 100 Hz, broad 120–300 Hz body (+12 dB re 600–1200 Hz), gentle tilt down, presence lift at 4–6 kHz.
  - **Dynamics:** active level −16.7 dBFS (10–90% spread 12.4 dB), crest factor 16.4 dB, which suggests compression.
  - **Sibilance:** 5–9 kHz sits 11.8 dB under 1–3 kHz (smooth, likely de-essed).
  - **Room:** tail decay ≈ −10 dB/100 ms, suggesting a light room or reverb **(inferred)**.
  - **Source:** no breaths in 177 sentence gaps and a very even level point to AI TTS or heavily edited human VO **(inferred, confidence 0.6)**.
- **Music** (`data/music.json`, `data/beats.json`; the meter is often loose and the tempo confidence low):
  - **Style:** original acoustic Western score. Plucked/strummed strings, a bass note on every beat (e.g. one note per 15 f at 120 BPM around f1500–1800), sustained pads in the intro and emotional scenes, occasional shaker or percussion sections (f7800–8100), and a big swell in the wordless death scene (f14772–15173, −22.4 LUFS).
  - **Tempo and keys:** the most frequent tempo is 120 BPM (13 of 57 novelty segments), with 100–129 BPM elsewhere. Confident keys include D major, A minor, G major, G minor, B major and D minor.
  - **Structure:** cues change at section and mood changes. The music enters with the voice at f10, drops out for dramatic beats (10.6–11.4 s, 198.6–202.8 s, 300.4–302 s, 396.6–404 s, 411–435 s sparse, 471–487 s) and swells where there's no voice.
  - **Level and stereo:** the bed sits 14.6 LU under the voice, ducks about 3 dB under speech, and is wide in stereo.
  - **Beats:** cuts are not aligned to them (see Formula 14).
- **SFX** (`data/sfx_candidates.csv`, `blueprint.sfx_cues`): 278 transients at least 8 dB above the local bed (about 30/min). Each has an onset frame, peak dBFS, attack, decay to −20 dB, duration, centroid at start/peak/end, 5 band shares, flatness, pan and width, plus a category guess. Event-locked analysis (rule 15) identifies the designed ones:
  - **paper_slap:** f70, 2 f after the cut. Broadband, attack about 3 ms, about 115 ms long, −20 dBFS.
  - **stamp_thump:** on the stamp's slam or icon frame (onsets 86, 116, 130). Mid-heavy (250 Hz–2 kHz ≈ 85%), attack ≤ 10 ms, decay to −20 dB in 35–170 ms, −15…−19 dBFS.
  - **tick:** +1 f after a counter step (onset 123).
  - **paper flutters:** onsets 150 and 157. 1–7 kHz noise; the first is −30 dBFS and ~55 ms, the second −24 dBFS and ~125 ms.
  - **chapter boom:** high-band +20 dB from +2 f after the card appears.
  - **diegetic:** gunshots, horses, coughs, fire, wind.
- **Mix:** voice mono centre; bed wide; master limited to about −1 dBTP at −14 LUFS. Silence is used for drama: the death scene runs 13.7 s with no narration, just a music swell.

## 8. Sync map

Unified event table: `data/sync_map.csv`, with every word onset, sentence onset, hard cut, transition, agent-logged element (text, graphic, UI, camera, fx, character), SFX onset and beat on one frame timeline. Statistics: `data/sync_stats.json`. Plots: `plots/timeline_full.png` (whole video, 10 strips) and `plots/timeline_0000_0299.png` (first 10 s, with word labels).

- Cuts: 95% fall 0–6 f before the next word onset (median 3 f). 80.6% fall within ±3 f of the nearest word onset. 17% fall inside a word. 77.4% of sentences open with a cut at −6…+3 f (mode −3).
- Text elements relative to the matched word: median +4 f overall (IQR 0…+12.5); name tags +5, labels +3.5, stamps +5, bubbles +1, list items 0/+5/−1 (measured exactly in calibration).
- SFX: no consistent sound on tags, labels, bubbles or arrows (event-locked averages flat or negative). Stamps peak at +2 f (+11 dB, 2–8 kHz). Counters peak −3…−1 f. Chapter cards rise from +2 f.
- Music: cuts are no closer to beats than chance (25.3% vs 26.6% within ±2 f).
- Shots versus sentences: 62% one sentence start, 29% none, 9% two or more.

## 9. Transfer rules (anchor-based; full list in `blueprint.transfer_rules`)

Anchors that any new voiceover provides:
- word onsets and offsets (forced alignment);
- sentence starts and ends;
- pauses of 300 ms or more;
- emphasised words (top 20% by RMS or pitch peak within the sentence);
- proper nouns, numbers and time phrases (by meaning);
- section boundaries (life stages);
- music beats, used only for chapter-card and cue changes.

The edit plan follows from them:
1. Shot boundary = sentence start − 3 f, unless the sentence continues the same image.
2. Element first frame = keyword onset + template offset (tag +5, label +3, stamp slam +5 with ghost frames at +3 and +4, bubble +1, list item 0).
3. Arrow at label + 3 f.
4. Punch-in camera ending on the onset of an enumerated keyword (7 f before it).
5. Stamp SFX at slam − 0…1 f; counter ticks at the step + 1 f.
6. Chapter card from the pause after a section's last sentence. The scene fade-out starts at last word end + 3 f; the next narration starts 3–10 f after the fade-in begins.
7. Music cue changes at chapter cards. Dropouts of 0.5–1.5 s before a punchline sentence (detected as a short sentence after a question or a contrast "Not X, Y" pattern).
8. Callbacks: when a planted noun recurs in the script, re-show its device.

## 10. Asset recipes

| Asset | Made how (inferred) | How to recreate |
|---|---|---|
| Characters | Vector cartoon puppets: thick dark outlines, flat colour plus one shade, big heads for child scenes, semi-realistic adults; rigged in an After Effects-style tool with pose swaps | Needs art: illustrated or AI-generated, then cleaned to flat vector. Prompt template: "flat 2D vector cartoon, bold dark outlines, cel-shaded, Western outlaw [character], [pose], transparent background, children's storybook explainer style". Rig parts (head/torso/arms) for pose swaps and blinks |
| Backgrounds | Painted vector scenes (sunset desert, wood interiors, night town, snow camp, saloon, farm, swamp city), parallax layers | Needs art (same style), split into 2–4 depth layers. Simple skies and gradients can be built in code |
| Props / close-ups | Wanted poster, notebook, map, letter, polaroids, chalkboard, sign | Mostly buildable in code (parchment shapes, text, rules, icons). Portraits inside need art |
| Tags, labels, bubbles, stamps, arrows, counters, chapter cards, corner tags, HUDs, comment panel, subscribe scroll, end screen | Motion graphics | Buildable in code (Remotion templates in `blueprint.templates`; already implemented for hero title, list items, counters and camera in `render/`) |
| Particles (dust, sparkles, snow, rain, rays, fire flicker) | Particle overlays | Buildable in code |
| Music | Original Western score | Needs music (user-supplied or licensed). A fallback synthesized bed (plucked guitar arpeggios + bass on beats + pad at 120 BPM in D/G/A) is possible but noticeably lower quality |
| SFX | Library sounds | Stamps, slaps, flutters, ticks and whooshes are synthesizable from the recipes in `blueprint.calibration.sfx_recipes`. Gunshots, horses, coughs, fire and crowds need a library |
| Voice | TTS or VO (inferred) | Yours |

---

## Files

**Data**
- `blueprint.json`: style tokens, templates, camera grammar, transitions, structure, shot list, text track, SFX cues, music cues, mix, voice, transfer rules, calibration edit plan.
- `data/`:
  - `frame_metrics.csv`: per-frame luma, saturation, MAD, histogram distance, SSIM, ORB similarity, edges, 3×3 grid.
  - `audio_frames.csv`: per-frame RMS, centroid, flux and band energies for the mix and every stem.
  - `words.json` and `sentences.json`.
  - `shots.*` and `cuts.*`.
  - `visual_events.json`.
  - `sync_map.csv` and `sync_stats.json`.
  - `sfx_candidates.csv`, `music.json`, `beats.json`, `voice_stats.json`.
  - `element_curves.json`, `tracks/`, `chapter_card_timing.json`, `easing_fits_calibration.json`.

**Images**
- `contact_sheets/per_second/`: 558 sheets, 30 frames each, frame numbers burned in.
- `contact_sheets/overview_1fps/`.
- `frames_events/`.
- `fonts/`.
- `spectrograms/`.
- `plots/`.

**Agent logs**
- `visual_review/`: 12 independent per-second review logs (1,700+ events) and their summaries.

**Code**
- `scripts/`: every analysis step (a01–a20), re-runnable.
- `../render/`: the Remotion renderer (calibration composition, data-driven).

## Assumptions and limitations

- **Resolution:** the source is 480p, so 1–2 px features (outline widths, grain) are estimates. Colours sampled from antialiased thin strokes were corrected by eye.
- **Agent logs:** the per-second agent logs are perceptual, with about ±1–2 f accuracy on first frames. Every template's numbers in this report come from direct pixel measurement of representative instances; the agent logs supply semantics and counts.
- **Music:** the tempo, key and segmentation numbers for the music are low-confidence (sparse rhythm, Demucs bleed). The cue boundaries are over-segmented by the novelty detector; the real number of cues is probably 15–25.
- **SFX:** detection covers transients at least 8 dB above the local bed. Quiet designed sounds under the music may be missed, but the event-locked averages already account for that.
- **Inferred items:** TTS vs human voice, the production method of the art, and the limiter settings are all inferred.
