---
name: vurt-npaw-analytics
description: |
  Pull NPAW/Youbora analytics from myvurt.com — buffer ratios, plays, sessions, 
  concurrent viewers, by device/CDN/geo. Run this to diagnose video quality issues.
  Usage: python3 scripts/npaw_query.py
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
allowed-tools: Bash, Read
---
# VURT NPAW Analytics

## Setup
NPAW credentials must be set as secrets:
- `NPAW_SYSTEM_CODE` = "vurt"
- `NPAW_API_SECRET` = [from Enveu/NPAW dashboard]

Set them at: [Settings > Advanced](/?t=settings&s=advanced)

## Usage
```bash
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --help
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --quality --days 7
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --sessions --hours 6
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --geo --days 3
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --cdn --days 7
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --concurrent --days 1
python3 Skills/vurt-npaw-analytics/scripts/npaw_query.py --hourly --days 1
```
