# Channel host: character spec v2 (round-head cartoon style)

The host is drawn in the round-head cartoon style from the user's reference screenshots.

- **What we match:** the art style.
- **What we don't copy:** any specific character from those screenshots. Our host is an original detective.

Renderer: `engine/roundhead.py`. Model sheet: `design/host_character_sheet.png`.

## Style rules (measured from the references, 1080p)
- **Head:** a big white circle (`#F8F8F5`) with an inked black outline of about **0.06 R**, plus a tiny wobble (fixed seed, so lines don't boil). The head is **42–49% of total height**.
- **Eyes:** two small black shapes (r ≈ 0.125 R), **close together** (centres ±0.155 R), shifted toward where the character looks (`look=(dx, dy)`).
  - Moods come from the eye shape: dot, lidded, smug, angry, sad, wide with a highlight, happy arcs.
  - Thin brows are added only when needed.
- **Mouth:** absent by default. A small open mouth, an "o", a smile, a grimace or a smirk only when the line needs it.
- **Hands:** big white mitten blobs.
- **Limbs:** chunky tubes (sleeves 0.27 R, legs 0.30 R).
- **Identity:** carried by **hat + outfit**, in muted earthy colours with soft vertical gradients.
- **On the black stage:** a faint grey rim (0.02 R) keeps dark clothes readable. Drop the rim on illustrated backgrounds.

## The host: "The Detective"
- Brown fedora with a dark band.
- Tan trench coat with lapels, belt and gold buckle, double buttons and pocket flaps.
- White shirt and red tie.
- Slate trousers and brown shoes.
- **Signature pose:** `inspect`, a magnifying glass held over one eye that enlarges it. Use it for reveals, "the first name on it…", "I did the research".

| Part | Hex |
|---|---|
| Fedora / band | `#6A4A38` / `#2A221E` |
| Trench / belt | `#C9A26B` / `#7D5B3A` |
| Tie / shirt | `#B23A32` / `#EFEAE0` |
| Trousers / shoes | `#3D414C` / `#4A3329` |
| Head & hands / ink | `#F8F8F5` / `#151515` |

**Alternate outfits on the same rig** (one-line swap):

| Preset | Outfit |
|---|---|
| `REPORTER` | newsboy cap and vest |
| `SLEUTH` | beanie and bomber jacket |

## Expressions
`neutral`, `talk`, `talk2`, `smile`, `grin`, `smug`, `deadpan`, `skeptic`, `angry`, `evil`, `sad`, `cry` (tears),
`nervous` (sweat drop), `grimace`, `shock`.

Swap about every second at phrase points. There is no lip-sync.

## Poses
`idle`, `hips`, `wave`, `point`, `chin`, `inspect`, `shrug`, `cheeks`, `walk`

## Framing (unchanged from the blueprint)
| Scale | Head radius | Head centre |
|---|---|---|
| Normal | 182 px | (960, 430) |
| Punch-in | 277 px | (960, 446) |
| PIP | 87 px | bottom-left |

## Supporting cast
Same construction for everyone.
- **FBI agents:** navy cap with yellow "FBI", and a navy windbreaker.
- **Subjects:** `subject(hair=..., top=..., ...)`.
- **Portraits:** `cards.make_portrait`, with the aged-photo look.
- The fedora and trench coat belong to the host only.

## Speech captions
These follow the reference style:
- white rounded heavy text (Nunito Black) with a thick black outline and soft shadow
- a short white tail line pointing at the speaker
- usually a slight tilt

Call `text.draw_speech(canvas, text, x, y, cap_px, tail=((x0, y0), (x1, y1)), rot)`.

## API
```python
from engine.roundhead import draw_character, HOST, AGENT, subject, R_NORMAL, NORMAL_CENTER
draw_character(canvas, *NORMAL_CENTER, R_NORMAL, pose='inspect', expr='neutral', pal=HOST)
```
