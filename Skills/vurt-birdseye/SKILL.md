---
name: vurt-birdseye
description: Living birds-eye-view of all VURT data. Aggregates latest metrics from GA4, NPAW, Meta (IG + FB), YouTube into a single state file. READ data/state.json at the start of EVERY VURT conversation to have full context. Run scripts/snapshot.py to refresh.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Purpose

Prevents context loss between sessions. Before making ANY claim about VURT metrics, traffic, or performance — read `data/state.json` first. This is the single source of truth for current VURT data.

## Usage

### Read state (every VURT conversation start)
```
cat Skills/vurt-birdseye/data/state.json
```

### Refresh state (on demand or scheduled)
```
cd /home/workspace/Skills/vurt-analytics/scripts && python3 /home/workspace/Skills/vurt-birdseye/scripts/snapshot.py
```

### What's in the state file
- **GA4**: Daily snapshot, weekly overview, ALL traffic sources (no truncation), ALL landing pages with bounce rates, ALL landing pages × channel crossover, geo, platforms, devices, 14-day trend
- **NPAW**: Top content, daily video overview, buffer trend, device/CDN/country breakdown
- **Meta IG**: Follower count, recent posts with engagement (likes, comments)
- **Meta FB**: Page followers, recent posts with engagement
- **YouTube**: Channel stats, recent video performance
- **Gaps**: Meta Ads Manager data NOT available (page token lacks ad account permissions — need user-level token with ads_read scope)

### Critical rules
- NEVER present GA4 data from a truncated cross-dimension query as the full picture
- For cross-dimension queries (channel × landing page), use limit=1000 to capture all rows
- Always compare your claims against the state file before presenting to user
- When the state file is stale (>24h), refresh it before making data claims
