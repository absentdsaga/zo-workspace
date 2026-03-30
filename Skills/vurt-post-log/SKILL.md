---
name: vurt-post-log
description: Syncs post URLs and performance metrics from Instagram (Meta Graph API) and YouTube into the Notion Post Log database. Run after posting to populate URLs, or after 72 hours to pull metrics.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Usage

### Sync post URLs and metrics into Notion Post Log

```bash
python3 Skills/vurt-post-log/scripts/sync.py --urls       # Pull URLs from IG + YT, match to Post Log entries
python3 Skills/vurt-post-log/scripts/sync.py --metrics     # Pull metrics (views, likes, shares, saves, comments) for all entries
python3 Skills/vurt-post-log/scripts/sync.py --all         # Both URLs and metrics
python3 Skills/vurt-post-log/scripts/sync.py --dry-run     # Preview what would be updated without writing to Notion
```

### How matching works

- **Instagram**: Pulls recent posts via Meta Graph API with `permalink`. Matches Post Log entries by platform=Instagram + date overlap.
- **YouTube**: Pulls recent videos via YouTube Data API with `videoId`. Constructs URL as `https://youtube.com/shorts/{videoId}`. Matches by platform=YT Shorts + date overlap.
- **Facebook**: Permalink not available via API yet. Enter manually in Notion.
- **TikTok**: No API access. Enter manually in Notion.

### Required secrets (Settings > Advanced)

- `VURT_NOTION_API_KEY` — Notion internal integration token
- `VURT_META_ACCESS_TOKEN` — Meta Graph API token (already configured)
- `VURT_GOOGLE_OAUTH_CLIENT` — Google OAuth client JSON (already configured)
- `VURT_YOUTUBE_REFRESH_TOKEN` — YouTube refresh token (already configured)

### Constants

- Post Log database ID: `c592ce58-b453-436f-b8e0-4510b2dcb412`
- IG Account ID: `17841479978232203`
- YT Channel ID: `UCB7B5ifo5Pgfc-j_uJGQG1g`
