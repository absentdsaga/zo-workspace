---
name: token-guardian
description: Manages VURT API token lifecycle -- health checks, expiry tracking, and auto-refresh for Meta and other expiring tokens.
---

# Token Guardian

Centralized management of all VURT API tokens that expire or need periodic refresh.

## Token Inventory

### Tokens That Expire (managed by this skill)

| Token | Lifetime | Refresh Method | Status |
|-------|----------|----------------|--------|
| `VURT_META_ACCESS_TOKEN` | ~60 days | Graph API exchange (`/oauth/access_token`) | **Auto-refresh via scheduled agent** |
| Frame.io `access_token` | 1 hour | Adobe IMS refresh (handled by `frameio_client.py`) | **Self-managing** -- no action needed |

### Tokens That Do NOT Expire

| Token | Notes |
|-------|-------|
| `VURT_YOUTUBE_REFRESH_TOKEN` | Auto-refreshes per request via OAuth flow |
| `VURT_YOUTUBE_API_KEY` | Permanent API key |
| `VURT_GOOGLE_OAUTH_CLIENT` | Permanent client credentials |
| `VURT_NOTION_API_KEY` | Permanent integration token |
| `NPAW_API_SECRET` | Permanent API secret |
| `VURT_FRAMEIO_CLIENT_ID` | Permanent client ID |
| `FRAMEIO_CLIENT_SECRET` | Permanent client secret |

## Scripts

### `scripts/refresh-all.py`

Health check and status report for all tokens.

```bash
# Check status of all tokens (read-only)
python3 scripts/refresh-all.py --check

# Check + refresh Meta token if needed
python3 scripts/refresh-all.py --refresh
```

Outputs JSON with status of each token, days until expiry where knowable, and any warnings.

### `scripts/auto-refresh-meta.py`

Standalone Meta token refresh script. Calls the Graph API to exchange the current long-lived token for a new one.

```bash
python3 scripts/auto-refresh-meta.py
```

Outputs JSON:
```json
{
  "status": "success",
  "new_token": "EAAMr...",
  "expires_in_seconds": 5184000,
  "expires_in_days": 60,
  "refreshed_at": "2026-04-14T12:00:00Z"
}
```

## Scheduled Agent Setup

The Meta token must be refreshed every 50 days. The scheduled agent should:

1. Run `python3 /home/workspace/Skills/token-guardian/scripts/auto-refresh-meta.py`
2. Parse the JSON output
3. If `status` is `"success"`, update the Zo secret:
   - Use `update_user_settings` to set `VURT_META_ACCESS_TOKEN` to the `new_token` value
4. If `status` is `"error"`, alert Dioni via email

**Agent prompt template:**

> Run the Meta token refresh script: `python3 /home/workspace/Skills/token-guardian/scripts/auto-refresh-meta.py`
> Parse the JSON output. If status is "success", use update_user_settings to update the secret VURT_META_ACCESS_TOKEN with the new_token value from the output. If status is "error", send an email to dioni@myvurt.com with subject "ALERT: Meta Token Refresh Failed" and the error details.

## Required Environment Variables

- `VURT_META_ACCESS_TOKEN` -- Current Meta long-lived access token
- `VURT_META_APP_SECRET` -- Meta app secret for token exchange
- `VURT_FRAMEIO_CLIENT_ID` -- Frame.io OAuth client ID (for health check)
- `FRAMEIO_CLIENT_SECRET` -- Frame.io OAuth client secret (for health check)
- `VURT_YOUTUBE_API_KEY` -- YouTube Data API key (for health check)

## Meta API Details

- App ID: `892877370386060`
- API Base: `https://graph.facebook.com/v25.0`
- Exchange endpoint: `/oauth/access_token?grant_type=fb_exchange_token`
