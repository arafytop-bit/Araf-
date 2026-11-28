# What I need from you for Phase 2

## Blocking now: illustrated art for the high-fidelity calibration

This environment has no image-generation key, so these come from your phone app. Copy-ready prompts, attachments, aspect ratios and backgrounds are in `assets_to_generate/ASSET_LIST.md`.

1. `A01_character_sheet.png`: do this first. Every later asset attaches it.
2. `A02_hero_bust_sunset.png`: the hero in the portrait shot.
3. `A03_hero_bust_masked.png`: the source for every wanted-poster print.
4. Optional: A04–A06 landscape layers. These are only needed if you'd rather have painted ground than the code-built one.

**Alternative:** tell me which provider you have (OpenAI, Gemini, fal, Replicate or Recraft). I'll open a secure form for the key, so it's never pasted in chat, and generate these myself, including all of Phase 2's art.

**Phase 2's art:** it follows the same pattern. With an API key I generate everything. Without one, I send the next asset list right after your script arrives, and nothing ships with placeholder art.

## Required

1. **Your voiceover and its exact transcript.**
   - **Audio:** WAV or FLAC, 44.1 or 48 kHz, unclipped, with no music.
   - **Transcript:** plain text, exactly as spoken. Numbers should be written the way you want them on screen, e.g. "$5,000".
   - **Language:** name it if it isn't English.
   - **Pauses:** tell me whether I may trim long pauses. By default I won't cut, stretch or pitch-shift the voice. I'll only apply gain, EQ, compression and de-essing to match the reference voice, and I'll report exactly what I applied.
2. **Character and background art for Phase 2 (same choice as above).** This is the big one. The format is about 90% illustrated scenes: flat outlined 2D characters (child and adult versions of the hero, about 10–20 supporting characters, horses, crowds) over painted backgrounds in about 30–60 locations, with 2–4 parallax layers each. I can't produce that quality in code. Pick one:
   - **a. Your own illustrations.** Send PNGs with transparency, characters cut into parts (head, torso, arms) if you want pose swaps and blinks, and backgrounds split into layers.
   - **b. AI image generation.** Give me an API key for an image model you have rights to use (e.g. OpenAI Images, a Flux provider such as fal.ai or Replicate, or Stability). I'll ask for it through a secure form; please don't paste it in chat. I'll generate to the blueprint's style prompt, then key out and layer the results.
   - **c. Placeholders only.** I build everything else at final quality and leave clearly labelled placeholder frames, with a per-scene art list showing prompt, size, layers and frames.
3. **Music.** The reference uses an original acoustic Western-style score (plucked strings, bass on the beat, pads; mostly about 120 BPM; a new cue at each chapter). Pick one:
   - **a.** Tracks you own or license (ideally 6–12 cues: calm, playful, tense, sad, heroic, finale).
   - **b.** Let me synthesize a simple bed that matches the measured tempo, key and arrangement. It will work, but it will sound clearly synthetic.
4. **Your brand and channel text.** The reference's "Born in Lore" name, wax-seal "B" logo and "subscribe for the next life" line belong to that channel, so I won't copy them. I need:
   - channel name and handle;
   - logo or monogram (optional);
   - storybook running head and subscribe line;
   - end-screen question;
   - "which character should be born next?" style prompt;
   - comment-panel entries, if you want the mid-roll comment interrupt.
5. **Disclaimer text** for your subject, naming its IP owners (the reference names Rockstar Games / Take-Two Interactive).

## Decisions (defaults in brackets)

6. **Output:** resolution, frame rate and target length [1920×1080, 30 fps, length = your audio].
7. **Chapter structure:** keep chapter cards with roman numerals and 1–3 word titles [yes; I'll propose titles from your script for you to edit].
8. **Mid-roll CTAs:** subscribe scroll at about 19% and comment panel at about 40% [yes].
9. **Running callbacks:** "notebook / things to remember", "the object to remember" (the hat), and a tally sign [I'll pick equivalents from your script and show you the mapping table].
10. **Loudness target:** −14 LUFS integrated, −1 dBTP [same as the reference].

## Optional

11. **An SFX library** (gunshots, horses, coughs, crowds, fire, wind). Without one, I'll synthesize stamps, slaps, paper flutters, ticks, booms and whooshes from the measured recipes and skip the realistic diegetic sounds.
12. **Font substitutions.** All matched fonts are free Google Fonts (Alegreya, Alegreya Sans, Grenze Gotisch, Source Serif 4, Patua One, Arvo). If your script isn't in Latin script, tell me the language and I'll pick the closest families that support it.
13. **Higher-resolution reference.** If you have a 1080p copy of the reference, the outline widths, grain and colour values can be re-measured more precisely. It's optional; the current numbers are scaled from 480p.
