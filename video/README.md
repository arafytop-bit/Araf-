# Doodle-explainer video pipeline

This folder rebuilds the style measured in `../analysis/STYLE_SPEC.md` around a new voice-over:
- white background
- stick-figure narrator with a 2-drawing line boil
- hand-drawn props and charts
- hard cuts, with pop-ins and builds synced to the spoken words
- linear motion
- dry voice at −14 LUFS
- short chapter stings and an outro

Production: *Your Electric Bill Is Holding a Bet on AI* (16:41, 1920×1080, 30 fps).

## Files

| File | What it does |
|---|---|
| `script.txt` | Exact narration script, with `##` section headers. It is the single source of truth for word timing. |
| `build_audio.py` | Orders the 8 voice clips by section and caps pauses by punctuation (sentence 0.32 s, comma 0.22 s, `...` 0.8 s, paragraph 0.42 s). Cuts use 6 ms crossfades. Then applies a high-pass filter, gentle compression and two-pass loudnorm to −14 LUFS. |
| `align.py` | Normalises script and speech-recognition words (spells out numbers and years, splits hyphens) and sequence-aligns them, so every script word gets a start and end time. |
| `make_words.py` | Writes `words.json`, which maps each script word index to its time. |
| `add_stings.py` | Inserts 1.35 s pauses with an original synthesized sting at the 4 chapter labels, and shifts word times to match. Adds an original outro under the end card. |
| `dd.py` | Hand-drawn primitives: wobbly paths, outlines, text, arrows, X marks, ellipses. |
| `chars.py` | Character rig: 23 poses, 10 mouths, brows, eyes, hair, hats, clothes, props. Two seeds give the A/B boil. |
| `props.py` | About 130 doodle assets: grid, buildings, money, documents, charts, maps (US states from `us_states.json`), and gags. |
| `engine.py` | Timeline engine. Each element is pinned to a phrase of the script; keyframes are linear. The scene cut happens when its first element appears. Renders through resvg → raw RGB → ffmpeg, rendering each unique frame only once. |
| `story.py` | The storyboard: 223 scenes and about 680 word-anchored visual events. Commands: `info` (with `LINT=1` it checks every anchor), `preview out.png t0 t1` (contact sheet), `render out.mp4 [t0 t1]`. |
| `sound_design.py` | Sound design. About 1,000 synthesized effects placed from the storyboard's events (pops, cut swishes, pencil/chalk/key ticks, stamps, impacts, marker swipes, dings, cha-chings, rising tones and more), panned by on-screen position. Adds an original lo-fi music bed with section moods: tense in the escalation, a muffled "tape" sound in the flashback, brighter at the end. The bed is ducked 8 dB under the voice and muted under the stings. Mixes to −14 LUFS and remuxes the video without re-rendering (`--no-bed` gives effects only). |
| `gallery.py` | Renders every asset to contact sheets for visual QA. |
| `fonts/` | Gaegu (subset to Latin) and Comic Neue, both under the SIL Open Font License (licence texts included). |
| `data/` | `words.json`, `words_raw.json`, `stings.json` and `audio_report.json` for this production. |

## Rebuild from scratch
```bash
bash ../tools/setup_env.sh .work                      # deps + Parakeet ASR + Silero VAD + fonts
export PROD=/path/to/workdir                          # needs audio_in/<id>.48k.wav, <id>.16k.wav per clip
for id in ...; do python3 ../tools/asr.py $PROD/audio_in/$id.16k.wav $PROD/asr/$id.json <parakeet_dir> <silero_vad.onnx>; done
python3 build_audio.py $PROD script.txt               # -> vo_final.wav (clip order is set in ORDER)
ffmpeg -i $PROD/vo_final.wav -ac 1 -ar 16000 $PROD/vo_final.16k.wav
python3 ../tools/asr.py $PROD/vo_final.16k.wav $PROD/asr_final.json <parakeet_dir> <silero_vad.onnx>
python3 make_words.py $PROD script.txt                # -> words.json
python3 add_stings.py $PROD                           # -> audio_master.wav + shifted words.json
ffmpeg -i $PROD/audio_master.wav -af volume=0.6dB $PROD/a.wav && mv $PROD/a.wav $PROD/audio_master.wav   # → −14.0 LUFS
LINT=1 python3 story.py info                          # all anchors must resolve
WORKERS=4 python3 story.py render $PROD/final.mp4     # about 10 minutes on 4 CPUs
PROD=$PROD python3 sound_design.py $PROD/final.mp4 $PROD/final_sd.mp4   # adds sound effects + music bed (about 4 minutes)
```

## Editing a shot
Every visual is one line in `story.py`, pinned to the words it appears on. For example:
```python
hero("eighty-one percent", "81%", 520, 470, 320, RED)   # pops in 1 frame before "eighty-one"
```
To change a shot:
1. Change the anchor phrase, the asset or its position.
2. Run `LINT=1 python3 story.py info` to check the anchors.
3. Run `python3 story.py preview sheet.png t0 t1` to see the result.
4. Re-render only the affected range, or the whole video.
