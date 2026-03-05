# Sentiment Scanner Fix — 2026-03-05 03:40 UTC

## Problem
The sentiment scanner agent was running hourly but sending reports with no social cross-references against prediction markets. User kept getting emails/SMS about token and Polymarket suggestions with no social signal context.

## Root Causes Found

### 1. X/Twitter Scanner — Completely Broken
- `scan_x.py` used the `bird` CLI which requires Twitter auth cookies
- No Twitter credentials were configured (AUTH_TOKEN, CT0 env vars missing)
- Result: Every scan returned tweets with `@unknown` author and 0 engagement metrics
- The tier system, engagement scoring, and entity extraction all operated on garbage data

### 2. TikTok Scanner — Completely Broken
- `scan_tiktok.py` used `agent-browser extract` command
- The `agent-browser` symlink was broken (dangling link to deleted `/root/agent-browser/`)
- Even after reinstall, `agent-browser` v0.16.3 no longer has an `extract` command
- Result: Every TikTok scan returned 0 videos

### 3. Cross-Referencing — Too Narrow
- Only matched `$TOKEN` names (like `$SOL`) between social signals and prediction markets
- With broken social data, only generic keywords like "bullish", "pump" were extracted
- These never matched specific prediction market questions

## Fixes Applied

### scan_x.py — Rewritten
- Now uses Zo API (`/zo/ask`) to call `x_search` tool
- Async batched scanning with `aiohttp` (3 concurrent queries)
- Batches account scanning (5 accounts per query)
- Deduplicates by tweet_id
- Test: 32 signals with all known authors (was: 170 signals all @unknown)

### scan_tiktok.py — Rewritten
- Reinstalled `agent-browser` v0.16.3 (fixed broken symlink)
- Uses agent-browser's `open` + `snapshot` flow instead of deleted `extract` command
- Added web search fallback via Zo API for when browser scraping fails

### aggregate.py — Improved Cross-Referencing
- Added entity extraction from tweet text (tokens, proper nouns, known entities)
- 60+ known entity terms (crypto, politics, tech, sports) for matching
- Word boundary matching to prevent "sol" matching "console" etc
- Extensive stop-word and generic-keyword filtering
- Sample tweet text included in match output for context
- Test: 46 real matches (Bitcoin price markets matching with bitcoin social buzz)

### Scheduled Agent Updated
- Agent `8a5bd2e1-3d65-440f-853b-66fd3409ed53` instruction updated
- Runs hourly, delivery via SMS
- Uses new script flow: scan_x → scan_polymarket → scan_kalshi → scan_tiktok → aggregate

## Files Modified
- `Skills/sentiment-scanner/scripts/scan_x.py` — full rewrite
- `Skills/sentiment-scanner/scripts/scan_tiktok.py` — full rewrite
- `Skills/sentiment-scanner/scripts/aggregate.py` — improved matching
- Agent `8a5bd2e1-3d65-440f-853b-66fd3409ed53` — updated instruction
