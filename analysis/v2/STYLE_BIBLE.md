# Style bible: "The FBI's 10 Most Wanted List Explained" (Trust Me Bro)

**What was measured.** The source is 854x480 at 30 fps, 15:04 long, H.264. Everything below comes from `analysis/v2/measure.py` and `audio_measure.py`, plus 4 fps contact sheets (76 sheets) and frame-level checks:

- ECC scale tracking.
- Pixel-colour sampling.
- Mid/side audio analysis.

The "EDL" in this document is the hand-checked shot list from the original analysis (243 editorial cuts, 508 visual states). It is used to cross-check the automatic detector.

## 1. Pacing

| Metric | Value |
|---|---|
| Editorial cuts (EDL, hand-checked) | 243 → average shot **3.70 s**, median **2.73 s**, p10 1.08 s, p90 7.10 s |
| Hard cuts (automatic detector) | 214 → average 4.20 s, median 2.57 s |
| Visual state changes (anything new on screen) | every **1.78 s** on average (median 1.20 s) → **2.8 changes per 5 s** (p10 = 1) |
| 5-second windows with no change | 17 of 181 (9%) |
| First cut | **3.5 s** (after the kinetic title) |
| First 30 s | 9 cuts and 23 visual changes |
| Static frames (no in-shot motion) | **69.6%**. Host shots are static, apart from expression swaps about every 1 s. Photos push in slowly. |

## 2. Look

- **Stage**: a black vignette stage, #0B0B0B centre falling to #030303 at the corners (corner-to-centre brightness ratio **0.12**).
  - **72.5% of all pixels are near-black.**
  - Mean brightness 39.6/255; contrast (standard deviation) 57.3.
- **Palette** (k-means share of pixels): #060406 black 73% · #39302D warm dark grey 9% · #F8F6F7 white 6% · #6E6861 / #B1A7A4 greys 9% · **#D8423C red 1.7% (the only accent)** · #68BAEC sky blue 1.1% · #93DD64 green 0.7%.
- **Restraint**: black, white and grey carry everything. Red is reserved for callouts, the cap and the shirt. Colour only arrives with real photos.
- **Characters**: flat white heads with thick black outlines (about 3% of head diameter), no shading in the video, black stick limbs, and a red cap and shirt.
- **Scenes**: about 30% of the runtime uses real imagery:
  - Characters composited onto **real photos**: 8.9% of runtime.
  - Framed photos: 7.1%.
  - Documents and screenshots: 5.1%.
  - Picture-in-picture: 3.8%.
  - Full-frame photos: 1.6%.
  - Host over a blurred photo: 1.5%.
- **Grain**: about 0.6 high-pass standard deviation (low). There is no film grain or bloom. It is clean and crisp.
- **Depth**: blur-fill backgrounds behind framed photos (the same image blurred and darkened); the host is composited over blurred photos. No parallax.

## 3. Typography (measured on frames)

- **Typeface**: one family, a heavy, wide, geometric all-caps sans. The closest match is LEMON MILK Bold; Unbounded 800 is an open-licence near-twin.
- **Kinetic title**: lines at **7.7% of frame height**, 54–59% of the width, centred.
  - Words start as dim ghosts at about 25% and light up white (#F4F4F4) or pure red (#EB050C) on the spoken word.
  - Light-up takes 1–2 frames.
- **Callouts**: red #D8423C–#EB484B with a soft dark shadow.
  - Size: cap **8.5–9.6% of height**, up to 91% of the width; two-line alerts up to 14.2%.
  - Position: centred, with the top at 10–14% of the height.
  - Entrance: about a 5-frame fade/scale settle.
- **Title cards**: rank number in red (about 5% of height); name in silver-white, cap **6.7%**, one word per line, left-aligned at x = 15%; a real portrait on the right.
- **Meme captions**: black caps on a full-width white top band covering 26–33% of the height; emoji allowed.
- **Small labels**: name tags about 2.5% of height on black boxes; fact labels about 3.5% in red.

## 4. Motion (frame counts at 30 fps)

- Changes: **hard cuts 36.5%**, cut + 3–5-frame settle 35.6%, 6–9-frame slides/fades 8%, 10–30-frame animations 11.5%, footage 4.8%.
- **Photos**: hard cut in (scale 1.000 at the cut, measured), then a **0.60%/s push-in** (73% in, 27% out).
- **Host**: static (scale drift under 0.2%); expression swap about every 1 s; no lip-sync; punch-in cuts to a zoomed framing.
- **Elements**: pop 50%→100% in about 4 frames with a slight overshoot. Characters run or walk in using flipbook cycles at 5 fps (6 frames per drawing).
- **Transitions**: there are no wipes or whips mid-video. The only whip is at the end (the host drops out in about 5 frames while the logo and Subscribe fall in and bounce).

## 5. Audio

| Metric | Reference |
|---|---|
| Integrated loudness | **−19.0 LUFS**, LRA 3.2 LU, true peak −1.0 dBTP |
| Voice | one energetic human narrator, about 221 wpm, near-mono (stereo correlation 0.99), mid RMS −20.6 dB in speech |
| Narration tightness | 25.5 pauses of 120–600 ms per minute, median pause **0.18 s** |
| Music bed | dark, low-register pulse at **about 100 BPM** (hip-hop/trap-style library beds), **23.7 dB under the voice** (side vs mid); a different track per entry |
| SFX | **7.2 per minute** overall; the intro is dense (about 32 per minute in the first 70 s; every kinetic word gets a hit); one bright hit on **every title card, on the cut frame**; gag SFX on jokes; **normal cuts are silent** (only 5% of SFX land on cuts) |
| Silence | 43 silences of 150 ms or more (8.6 s total); the music drops out completely before the final entry |
| Outro | a punchy beat at about 105–110 BPM for 6.5 s, entering 0.2 s after the last word |

## 6. Structure

- **0:00–0:03.5 (the hook)**: frame 1 is already the kinetic title. The words light up on the spoken hook ("Every person currently on the FBI's most wanted list"). Small chibi agents **run in** from the right while the host stands with a magnifying glass. There is motion from frame 1 and no logo or fade.
- **0:03.5–0:23**: host, screenshot, three rapid punch-ins (about 1 s each), a gag on a real photo ("same boat"), the host over the blurred photo, a mugshot grid, then "SPOILER ALERT" in big red over the blurred grid.
- **Body**: 10 entries using the same template. A title card (about 1.7 s, with a hit SFX), then the backstory with characters on real photos, fact labels and maps, then the crime, the arrest or reward, and the host's joke.
- **Ending**: a recap, then the end screen. The host whips out, the logo and Subscribe fall in and bounce, and the outro sting plays for 6.5 s with a 0.5 s fade.

## 7. Why it reads as "expensive" despite simple drawings

1. **Restraint**: one typeface; black/white/red; consistent line weight; every layout centred and aligned.
2. **Real-world imagery**: about 30% of the runtime puts characters on or next to real photos.
3. **Big, readable text**: callouts at about 9% of height, never small UI text.
4. **Snappy, consistent motion**: hard cuts on the word, 3–5-frame settles, flipbook cycles.
5. **A human narrator** with energy, plus library music and real recorded SFX.
6. **Constant humour beats**: a gag about every 30 s (memes, literal idioms, gag props).
