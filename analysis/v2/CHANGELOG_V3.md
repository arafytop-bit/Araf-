# Changelog: v3 full rebuild of "Most Epic Deaths in Human History"

**Deliverable**:
- Format: 1920x1080, 30 fps, 17:54.
- Video: H.264 High, CRF 16, preset slow, yuv420p, BT.709.
- Audio: AAC 320 kbps, 48 kHz stereo.
- File: `most_epic_deaths_v3.mp4`.

Everything below was checked in the rendered file. Numbers come from `analysis/v2/measure.py`, `audit_v3.py` and `audio_measure.py`: the same tools I ran on the reference and on the last version.

## 1. Script and edit changes (story and facts unchanged)
- **Hook reordered; no words were rewritten, removed or re-recorded.** The video now opens on the two strongest lines:
  - 0:00 "One of these guys wins a fight after he's already dead." (was 0:19)
  - 0:02.5 "Another wins a battle the same way." (was 0:21.5)
  - Then the title line "These are the most epic deaths in human history" (was 0:00), as the reference's kinetic title.
- The narration track was spliced at sentence boundaries, which are digital silence in the TTS file, so there are no clicks. Every later timing shifts by +0.27 s.
- The voice is unchanged: Kokoro am_puck at 1.25x, as you chose.

## 2. Every mistake from the audit and how it was fixed
QA_TABLE_PLACEHOLDER

## 3. What changed to make it premium
**Look**
- Every character scene now sits on a real photo or painting (66 images, all credited) or on the reference's black vignette stage. The flat cartoon backdrops are gone.
- Photos are graded as one family:
  - slightly desaturated, with a little more contrast;
  - day-for-night where the story is at night;
  - framed photos sit on a blur-fill of themselves with a soft shadow;
  - a top scrim keeps red callouts readable over photos.
- Depth comes from a slight depth-of-field blur on photo backdrops, contact shadows under every character, parallax (photo at 0.6%/s, background at 0.3%/s), and vignettes.
- Palette: black, white and red, with colour coming only from the photos. Maps use the reference green on a dark stage instead of a full-frame sky-blue sea.

**Typography**
- Unbounded (Open Font License), the open twin of the reference's heavy wide caps face, with the font's real kerning.
- Readable text has a 49 px cap minimum (4.5% of frame height). Callouts use 9% of height, as the reference does.
- A glyph guard now refuses to render any character the font lacks. That rules out another missing-glyph box like the one at 8:32 in the last version.
- A layout engine handles collisions:
  - The host cuts to a lowered framing whenever a callout is on screen, as the reference does at 8:06.
  - Tags snap above the nearest head and dodge callouts and each other.
  - Map labels avoid each other.

**Animation**
- A motion grammar measured on the reference:
  - pops go 50% to 100% in 4 frames with a slight overshoot;
  - callouts settle from 105% to 100% over 5 frames;
  - photos hard-cut in, then push in at 0.6%/s.
- New character motion:
  - flipbook walk and run cycles at 5 to 7.5 drawings per second;
  - entrances: drop with squash, rise, slide;
  - exits: fly-off, pop-out;
  - falls and deaths with a settle;
  - hops, shakes, drumming.
- Characters breathe and blink; expression swaps carry a 4-frame settle.
- Camera punches and shakes only on impacts.
- No hold runs past 3.5 s without a new beat. Host shots alternate framings and never repeat one at a cut.

**Hook and retention**
- Frame 1 is mid-action: the crowned corpse on the real Olympia stadium photo, the loser already hopping and the wreath falling. The hook text lights up word by word as it is spoken.
- At 0:02.5 it cuts to the night battle on a real turtle ship, with drumming, fire and embers.
- Open loops, payoffs and the full second-by-second plan are in `RETENTION_MAP.md`. The two hook loops pay off at 11:58 (the crowned corpse) and 16:07 (the drum).
- There is a death stamp per entry (DEATH #1 to #5). The speedrun timer is shown only when it is the joke.

## 4. Sound
SOUND_PLACEHOLDER

## 5. QA passes and scores
QA_PASSES_PLACEHOLDER
