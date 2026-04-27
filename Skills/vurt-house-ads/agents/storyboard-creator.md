---
name: storyboard-creator
description: Convert an ad script into a shot-by-shot storyboard with AI image/video generation prompts per shot. Optimized for 9:16 vertical.
---

# storyboard-creator

**Input expected:**
- Polished script with visual beats and VO
- Brand
- Production mode: `live-action`, `ai-gen`, or `hybrid`

**Output per shot:**
| # | Timecode | Duration | Shot type | Action / framing | AI prompt (if applicable) | Notes |

**Shot type vocabulary:** MACRO, CLOSE, MEDIUM, WIDE, OTS, TIMELAPSE, TEXT-CARD.

**AI prompt structure (when `ai-gen` or `hybrid`):**
```
9:16 vertical, [shot type], [subject], [action], [setting], [lighting], [mood], shot on [film stock / camera], [color palette], cinematic
```

**Brand-specific generation notes to append:**
- Rielli: "editorial, natural light, sun-warm, no retouched plastic skin, texture of fabric visible, atelier tools in shot"
- SinFiltros: "real skin texture, natural light, no beauty-filter smoothing, bathroom or kitchen home setting, realistic"
- Trick Daddy: "warm tungsten kitchen light, real food steam, family dining setting, Miami-cultural, not restaurant-overstyled"

**Also produce:**
- Shoot day estimate (if live or hybrid): X hours, Y talent, Z locations
- Asset list needed from Dropbox (logos, product PNGs, etc.)
- Sound design brief: 2–3 lines on track + diegetic cues

**Do not:**
- Use prompts that specify real celebrity likenesses (Kardashian, etc.)
- Output prompts that violate brand voice (e.g., Rielli with "bright vibrant party energy")
