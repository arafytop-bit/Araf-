# tools/

| Script | Purpose |
|---|---|
| `setup_env.sh` | Installs Python deps, downloads Parakeet-TDT ASR + Silero VAD (GitHub releases) and fonts (Gaegu, Comic Neue). |
| `asr.py` | Word-level transcription: `python3 asr.py audio16k.wav out.json <parakeet_dir> silero_vad.onnx` |
| `decode.py` | Decode every frame of a video into a downscaled `.npy` array. |
| `metrics.py` | Per-frame brightness/colour/difference metrics. |
| `events.py` / `classify.py` | Group frame changes into edit events; separate cuts / pops / animations / boil loops. |
| `sheets.py` / `animsheets.py` / `strips.py` | Contact sheets and per-event filmstrips for visual review. |
| `doodle.py` | Prototype procedural doodle kit (narrator rig with poses/expressions + 2-drawing boil, chalkboard, text, red X/ellipse). |
| `motion_test.py` | 30 fps render + H.264 encode test (boil, word-synced pops, hard cut, typewriter). |

See `../analysis/STYLE_SPEC.md` for the full measured style specification.
