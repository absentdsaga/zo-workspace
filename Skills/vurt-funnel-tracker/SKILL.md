---
name: vurt-funnel-tracker
description: Monitors the VURT conversion funnel daily via GA4 Data API. Tracks bounce rates, engagement rates, and conversion events broken down by traffic source and campaign. Compares today vs yesterday vs 7-day rolling average and flags regressions with severity levels.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  ga4_property: "518738893"
---

# VURT Funnel Tracker

Automated daily monitoring of the VURT conversion funnel via GA4. Detects regressions in bounce rate, engagement, and conversion events across traffic sources and campaigns.

## Scripts

### Full Funnel Report
```bash
python3 scripts/funnel-check.py
```

Pulls GA4 data and outputs a full terminal report with:
- Bounce rate, engagement rate, sessions, engaged sessions by traffic source (Paid Social, Direct, Organic Search, etc.)
- Same metrics by campaign name
- Conversion events: play_content, sign_up, app_cta_click, share_content
- Today vs yesterday vs 7-day rolling average comparisons
- Regression flags with severity: WARNING (15-30% worse) and CRITICAL (>30% worse)
- JSON log saved to `/home/workspace/Logs/live/`

#### Options
```bash
python3 scripts/funnel-check.py --hours 6            # Last 6 hours instead of full day
python3 scripts/funnel-check.py --json                # Machine-readable JSON output only
python3 scripts/funnel-check.py --alert-threshold 25  # Custom regression sensitivity (default 15%)
```

### Alert Check (Lightweight)
```bash
python3 scripts/alert-check.py
```

Lighter script for scheduled/cron runs. Only checks for regressions and outputs alerts -- no full report. Exit code 1 if any alerts found, exit code 0 if clean.

```bash
python3 scripts/alert-check.py --alert-threshold 20
python3 scripts/alert-check.py --json
```

## Environment Variables
- `VURT_GOOGLE_OAUTH_CLIENT` -- Google OAuth client JSON (installed app)
- `VURT_ANALYTICS_REFRESH_TOKEN` -- OAuth refresh token for GA4

## Regression Detection
- Compares today's metrics against the 7-day rolling average
- WARNING: metric regressed 15-30% from 7-day average
- CRITICAL: metric regressed >30% from 7-day average
- For "inverted" metrics (bounce rate), an increase is the regression direction
- Threshold is configurable via `--alert-threshold`

## Data Flow
1. Authenticate via OAuth2 refresh token
2. Pull GA4 runReport for today, yesterday, and 7-day window
3. Aggregate by sessionDefaultChannelGroup and sessionCampaignName
4. Compute deltas and flag regressions
5. Output terminal report + save JSON to Logs/live/

## Zero Dependencies
All scripts use Python stdlib only (json, urllib, datetime, argparse).
