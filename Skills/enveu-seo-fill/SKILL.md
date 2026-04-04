---
name: enveu-seo-fill
description: Automates filling SEO fields (title, description, tags, heading) in the Enveu CMS via their API. Parses VURT content titles, generates SEO metadata by content type, and batch-updates items.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  project: vurt
  cms: enveu
---

## Overview

VURT has ~3,818 content items in Enveu CMS with mostly empty SEO fields. This skill parses content titles (e.g. `KARMA_IN_HEELS_EP18`), generates appropriate SEO metadata based on content type, and pushes updates via the Enveu API.

## Environment Variables Required

- `ENVEU_AUTH_TOKEN` -- Value for the `A_t` header
- `ENVEU_PROJECT_ID` -- Value for the `P_i` header
- `ENVEU_TENANT_ID` -- Value for the `T_i` header

## Usage

```bash
cd /home/workspace/Skills/enveu-seo-fill/scripts

# Audit: scan all content items and report SEO field coverage
python3 enveu-seo.py audit

# Preview SEO changes for one show (dry run, no API writes)
python3 enveu-seo.py preview --show "Karma In Heels"

# Preview all changes
python3 enveu-seo.py preview --all

# Fill SEO fields for one show
python3 enveu-seo.py fill --show "Karma In Heels"

# Fill one specific item by ID
python3 enveu-seo.py fill --id 90

# Fill all content (requires --confirm flag)
python3 enveu-seo.py fill --all --confirm
```

## SEO Templates by Content Type

| Type | Title Template | Description Template |
|------|---------------|---------------------|
| MICRO_EPISODES | {Show} Ep {N} \| VURT - Watch Free | Watch {Show} Episode {N} free on VURT. Vertical micro-drama for your phone. |
| MICRO_SEASON | {Show} Season {N} \| VURT | Stream {Show} Season {N} free on VURT. |
| Series / MICRO_DRAMA_SERIES | {Show} \| VURT - Free Vertical Drama | Watch {Show} free on VURT. Original vertical micro-series. |
| Movies | {Title} \| VURT - Watch Free | Watch {Title} free on VURT. |
| Trailers | {Show} Trailer \| VURT | Watch the {Show} trailer on VURT. |

## Title Parsing

Handles patterns like:
- `KARMA_IN_HEELS_EP18` -- "Karma In Heels", Episode 18
- `VURT_Marry Me For Christmas_9x16_EP01` -- "Marry Me For Christmas", Episode 1
- `VURT_MARDIGRAS_EP10` -- "Mardi Gras", Episode 10
- `VURT_MyFirstLove_Ep01_9x16-v2` -- "My First Love", Episode 1
- `Something_Like_Business_v1_EP20` -- "Something Like Business", Episode 20
- `The Parking Lot` -- "The Parking Lot" (movie, no episode)

## Rate Limiting

0.5s delay between API calls. Full batch of ~3,818 items takes ~30 minutes for audit, longer for fill (requires GET + PATCH per item).

## Logs

All changes are logged to `scripts/seo-changes-{timestamp}.json`.
Audit results are saved to `scripts/seo-audit-{timestamp}.csv`.
