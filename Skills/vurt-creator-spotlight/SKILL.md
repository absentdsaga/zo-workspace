---
name: vurt-creator-spotlight
description: Generates branded VURT Creator/Director Spotlight graphics for Instagram (4:5, 1080x1350). Takes a headshot + name/show/date, outputs a cinematic dark-gold post following VURT brand guidelines. Reusable template for every new creator.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# VURT Creator Spotlight Generator

Produces on-brand IG feed graphics for Creator/Director Spotlights. Cinematic dark layout, gold accents, Inter typography, VURT wordmark — all matching brand guidelines in VURT-master.md.

## Usage

```bash
python3 Skills/vurt-creator-spotlight/scripts/generate-spotlight.py \
  --name "Steven Alan Davis" \
  --show "The Parking Lot Series" \
  --date "April 2026" \
  --photo /path/to/headshot.jpg \
  --out Documents/VURT-Spotlight-Name.png
```

## Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | yes | Creator/director full name |
| `--show` | yes | Series or show title |
| `--date` | yes | Streaming/launch date (e.g. "April 2026") |
| `--photo` | yes | Absolute path to headshot (JPG or PNG) |
| `--out`  | yes | Output PNG path |
| `--label` | no | Override label text (default: "CREATOR SPOTLIGHT") |

## Output

- **Format**: PNG, 1080×1350 (4:5 IG feed)
- **Layout**: Full headshot fading to brand black, gold rule + label, name in ExtraBold white, show in gray, VURT wordmark bottom right
- **Fonts**: Inter (system-installed)
- **Logo source**: `/home/workspace/vurt_logo_hires.png`

## Notes

- Headshot should be portrait orientation, face visible in upper 70%
- For best results: professional headshot with clean background
- `--label` can be changed to "DIRECTOR SPOTLIGHT", "WRITER SPOTLIGHT", etc.
- Output goes to `Documents/` by convention, named `VURT-Spotlight-[Name].png`
