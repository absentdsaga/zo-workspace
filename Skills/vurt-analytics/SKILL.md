---
name: vurt-analytics
description: Pull VURT Firebase/GA4 analytics reports — DAU, engagement, retention, traffic sources, top content. Powers the daily morning report agent and on-demand analytics queries.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  property_id: "518738893"
  project: vurt-bd356
---

## Current Status (as of March 20, 2026)

**GA4:** Working (Viewer access granted). Dioni's role upgraded from None → Viewer on March 19. Need Editor access for full configuration.

**Social Media Analytics:** Live — YouTube, TikTok, X scraped automatically via agent-browser. Instagram requires Meta Graph API setup.

### What's done:
- OAuth client created (Desktop app type in vurt-bd356 project)
- Refresh token generated and stored as Zo secret
- Daily report agent scheduled (8 AM ET)
- All scripts built and tested against the API
- Social media scraper module (social_client.py) — auto-scrapes YouTube, TikTok, X
- Social media insights integrated into insights engine
- Day-over-day comparison tracking with JSON cache

### Still needed:
1. **Mark to upgrade Dioni to Editor** on GA4 property 518738893 (currently Viewer — can see reports but can't configure goals/events)
2. **Data stream needs to be created** for myvurt.com (yellow banner in GA: "Can't find any data streams")
3. **Instagram API access** — set up Meta Graph API token as Zo secret `VURT_INSTAGRAM_TOKEN` + `VURT_INSTAGRAM_USER_ID` for automated Instagram metrics

### Two GA4 properties:
- `518738893` — Production data (79 DAU as of March 18). **Target property.**
- `518543881` — Linked to `vurt-2fa0d` (test project). Empty. Ignore.

## Setup

Requires these Zo secrets (both already configured):
- `VURT_GOOGLE_OAUTH_CLIENT` — Google OAuth client JSON (Desktop app type from vurt-bd356 project)
- `VURT_ANALYTICS_REFRESH_TOKEN` — OAuth refresh token scoped to `analytics.readonly`

## Usage

### Daily Report (scheduled agent)
```bash
python3 Skills/vurt-analytics/scripts/daily-report.py
```
Outputs a formatted markdown report with WoW comparisons. Used by the daily morning agent.

### On-Demand Query
```bash
python3 Skills/vurt-analytics/scripts/query.py --metric activeUsers --days 30
python3 Skills/vurt-analytics/scripts/query.py --report engagement
python3 Skills/vurt-analytics/scripts/query.py --report traffic
python3 Skills/vurt-analytics/scripts/query.py --report content
python3 Skills/vurt-analytics/scripts/query.py --report retention
```

### Social Media Report (standalone)
```bash
python3 Skills/vurt-analytics/scripts/social_client.py
```
Scrapes YouTube, TikTok, X public profiles. Caches results for day-over-day tracking.

### Available Reports
- `daily` — Full daily digest (DAU, sessions, engagement, retention, traffic, top content, social media)
- `engagement` — Watch time, session duration, engaged sessions, sessions per user
- `traffic` — Source/medium breakdown, organic vs paid vs social vs direct
- `content` — Top pages/screens by views and engagement
- `retention` — Day 1, Day 7 cohort retention rates
- `realtime` — Current active users (last 30 min)
