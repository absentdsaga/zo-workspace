---
name: vurt-analytics
description: Pull VURT Firebase/GA4 + NPAW video analytics. Generates and sends the daily HTML report email. Powers the daily morning report agent and on-demand analytics queries.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  property_id: "518738893"
  project: vurt-bd356
---

## EMAIL SENDING — STRICT REQUIREMENTS (read every time before sending)

**NEVER manually type or abbreviate HTML inline.** Always use the script.

### Correct send procedure (follow exactly, every time):

```
Step 1: cd /home/workspace/Skills/vurt-analytics/scripts
        python3 send-report.py generate
        → Note the html_path from REPORT_METADATA output

Step 2: Run gmail-send.py to send the full report:
        python3 gmail-send.py <html_path> "<subject>" dioni@myvurt.com
        → Uses /zo/tools/use_app_gmail/run API directly — handles large files

Step 2 (manual fallback): If gmail-send.py fails, use mcp__zo__use_app_gmail with:
        - tool_name: gmail-send-email
        - to: dioni@myvurt.com   ← ONLY this address unless explicitly told otherwise
        - subject: from metadata (e.g. "VURT Daily Analytics Report — March 26, 2026")
        - bodyType: html          ← CRITICAL: must be "bodyType", NOT "content_type"
        - body: the FULL file contents (do NOT truncate)
        - email: dioniproduces@gmail.com
```

### Why gmail-send.py uses /zo/tools/use_app_gmail/run (not /zo/ask):
- `/zo/ask` spawns a child agent — requires credits, often returns 402
- `/zo/tools/{name}/run` calls the tool directly — always works, handles large payloads
- The HTML report is ~35-80KB; passing it via mcp__zo__read_file truncates it

### What goes wrong when you skip these steps:
- **Manually typing HTML** → report is truncated/abbreviated, missing most sections
- **Using `content_type` instead of `bodyType`** → renders as raw HTML source code
- **Not reading the file** → old data or wrong sections

### Report recipients (as of March 2026):
- **Daily send:** dioni@myvurt.com only
- **Full team send:** Only when Dioni explicitly says "send to the team"

### Data freshness note:
GA4 data for "yesterday" may not be finalized until mid-morning. The freshness detection
in daily-report.py automatically falls back to 2daysAgo when needed — this is correct behavior,
not a bug. The report header always states which date's data is shown.

## NPAW Video Analytics (added March 26, 2026)

**Credentials:** `NPAW_API_SECRET` + `NPAW_SYSTEM_CODE=vurt` (stored as Zo secrets)
**Client:** `scripts/npaw_client.py`
**Endpoint:** `https://api.youbora.com/vurt/data`
**Working metrics:** `views` (plays), `completionRate`, `effectiveTime`
**Grouped queries:** use `group_by="title"` — title comes from `block["name"]`, values sum across daily data points
**Ranking:** Engagement Score = `completionRate * log10(plays + 1)` — surfaces quality AND volume

The daily report pulls:
1. Yesterday's video overview (sessions, plays, errors, error rate)
2. Top 20 titles → ranked two ways: Engagement Score (top 5) + Raw Plays (top 5)

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
