# The Agent With No Pulse — production notes

- Output: `out/final/mincemeat_final_2k.mp4` (1440x2560, 30 fps, 2650 frames, 88.33 s, H.264 CRF 16 + AAC 320k 48 kHz;
  −15.2 LUFS integrated, −1.5 dB peak). Not committed (gitignored, 128 MB).
- Rendered at 1080x1920 (2x MSAA, lighter lens blur) and Lanczos-upscaled to 1440x2560: this cloud box has no GPU, and
  SwiftShader WebGL ran ~25 s/frame at native 2K vs ~3.2 s/frame at 1080 with two workers (2.4 h total).
- Code: `src/videos/mincemeat/` (story.ts shots/cameras/DOF, sets.ts six sets + painted map, cast.ts staging, fx.ts
  effect drawings, toon.ts new hats/props/faces). Sound: `shorts/mincemeat/audio/build.py` (score, SFX, mix, cues.md).
- Render: `scripts/render_chunks.sh` (WORKERS=2 WORKER=0/1), then join + upscale + mux (see scripts/finalize.sh), QA with
  `scripts/short_qa.py` (no black/white frames, no silences; flagged pops are all planned beats).
- Opus verifier round 1 fixes applied: corpse pallor + slack mouth, war-room wall map, Pam photo, desk blotter,
  Hitler hairline, ending framing. Headstone lettering replaced by grooves (no readable text).
- QA fix: desk lamp removed (the desk-insert camera ended inside its shade → 55 green frames).
- Known limits: verifier still wanted richer textures, lower 3/4 cameras and a clearer submarine/boat; not redone.
