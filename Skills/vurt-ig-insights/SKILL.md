---
name: vurt-ig-insights
description: Pull VURT Instagram analytics via the Meta Graph API. Supports profile stats, daily/weekly metrics, per-post insights, audience demographics, and token refresh.
---

# vurt-ig-insights

Instagram insights for the VURT account using Meta Graph API v25.0.

## Usage

```bash
python scripts/insights.py profile
python scripts/insights.py daily --days 7
python scripts/insights.py weekly
python scripts/insights.py posts --limit 10
python scripts/insights.py demographics
python scripts/insights.py refresh-token
```

Add `--json` to any subcommand for raw JSON output.

## Environment Variables

- `VURT_META_ACCESS_TOKEN` - Meta Graph API access token
- `VURT_META_APP_SECRET` - Meta app secret (for token refresh)
- App ID: 892877370386060
- Instagram Business Account ID: 17841479978232203
- Facebook Page ID: 943789668811148
