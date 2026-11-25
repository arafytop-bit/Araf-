# Channel host: character spec v1

The host is an original design that replaces the source-style stick figure. It is rendered
by `engine/character.py` and shown in `design/host_character_sheet.png`.

## Concept
An internet sleuth who "did the research".
- **Yellow** echoes crime-scene tape, and stays clear of the red used for callouts.
- **Round glasses** stand for research.
- **The hoodie** keeps him relatable.

He keeps the format's mechanics (dark stage, expression swaps, three scales) but has a
silhouette of his own.

## Silhouette rules (what makes him recognisable)
1. Three-spike messy hair and a zig-zag fringe kept above the brows.
2. **Big round glasses** with thick brows above them. No other character wears them.
3. Caution-yellow hoodie with the hood bunched at the neck, two drawstrings and a kangaroo pocket.
4. Tube sleeves with round hands, slate jeans, white sneakers.
5. Egg-shaped head with blush, a small nose, and maroon open mouths with a tongue.

## Palette
| Part | Hex |
|---|---|
| Hoodie | `#FFC83D` |
| Hoodie shade (pocket, hem) | `#E9A92A` |
| Jeans | `#3A3F4B` |
| Sneakers | `#F4F4F4` |
| Skin | `#FBF6EE` |
| Hair | `#2B1F1B` |
| Outline | `#141414` |
| Blush | `#FF8A8A` (≈37% opacity) |
| Mouth / tongue | `#4A1216` / `#E66A6E` |
| Lens tint | `#DCEEFF` (≈43% opacity) |
| Rim (on dark stage) | `#8E8E8E` |

## Proportions (head half-width R = 1, origin at head centre)
- **Head:** egg shape, 2.0 wide × 2.1 tall.
- **Hair:** top at −1.52.
- **Glasses:** lenses r 0.30 at x ±0.38, y −0.12. Eyes have a white highlight.
- **Hoodie:** y 0.98 → 2.10, half-width 0.62 → 0.72. Sleeves are 0.25 wide.
- **Legs:** to 2.72, with sneakers to about 2.95. Total height is about 4.5R.

**Framing at 1080p** (same as the blueprint):

| Scale | R | Head centre |
|---|---|---|
| Normal | 182 px | (960, 430) |
| Punch-in | 277 px (×1.52) | (960, 446) |
| PIP | 87 px | bottom-left or bottom-centre |

## Expressions (swap about every 1 s at phrase points, no lip-sync)
| Expression | Use for |
|---|---|
| `talk`, `talk2` | neutral narration |
| `o` | "wait, what?" |
| `smile`, `grin` | jokes, positive beats |
| `skeptic` (one brow up) | doubt, irony |
| `frown`, `grimace` | grim facts, cringe |
| `shock` | shocking reveals |
| `evil` | describing a villain's intent |
| `neutral` | flat aside |

## Poses
| Pose | Use for |
|---|---|
| `hips` | default |
| `wave` | talking, greeting |
| `point` | at an inserted photo or map |
| `chin` | thinking |
| `shrug` | "who knows" |
| `cheeks` | horror or shock |
| **`nerd`** | **Signature move:** pushes his glasses up, with `glint=True`. Use on "I did the research", reveals, and "here's the thing". |

## Supporting cast (same construction, never the host's look)
- **FBI agents:** navy jacket, navy forward cap with yellow "FBI".
- **Subjects:** vary skin tone, hair (`short`, `slick`, `buzz`), top (`tee`, `suit`, `jacket`) and colours.
- **No glasses or yellow hoodie** on anyone but the host.
- **Portraits:** title-card portraits use the aged-photo treatment (`cards.make_portrait`).

## Don'ts
- No red sideways cap.
- No white circle head on stick limbs with a rectangle shirt. That is the source's look.

## API
```python
from engine.character import draw_character, HOST, AGENT, subject, R_NORMAL, NORMAL_CENTER
draw_character(canvas, *NORMAL_CENTER, R_NORMAL, pose='nerd', expr='skeptic', pal=HOST, glint=True)
```
