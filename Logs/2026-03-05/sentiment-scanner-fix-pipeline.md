# Sentiment Scanner Pipeline Fix - March 5 2026

## Problem
- X scanner used Zo API (`/zo/ask`) to call `x_search` — burned credits, hit daily limit
- TikTok scanner used Zo API for `web_search` — same credit burn issue
- Agent-browser had been broken/reinstalled but TikTok scraping still returned 0
- Cross-referencing was producing 0 matches because social data sources were empty/broken

## Root Cause
Both `scan_x.py` and `scan_tiktok.py` were calling the Zo API to invoke tools that the scheduled agent can call directly as MCP tools. Every hourly scan burned significant credits.

## Fix
1. **Rewrote agent instructions** — agent now calls `x_search` and `web_search` MCP tools directly (no Zo API intermediary), then writes Python scripts to parse results into scan format
2. **Fixed aggregator (`aggregate.py`):**
   - Removed overly generic terms from `known_entities` (btc, eth, sol, ai, etc.)
   - Added `NOISE_SIGNAL_TOPICS` filter to prevent base-layer names from appearing as top signals while keeping them for market matching
   - Added war, ban, nfl, nba, etc. to `GENERIC_CRYPTO_KEYWORDS` stop list
   - Kept "bitcoin", "ethereum", "elon musk" etc. for cross-referencing with prediction markets
3. **Delivery changed from SMS to email** for richer formatting

## Test Results
- 20 X signals (all with known authors)
- 7 TikTok signals (all crypto relevant)
- 96 Polymarket + 33 Kalshi opportunities
- **20 real prediction market matches** with social cross-references
- Clean matches: Bitcoin price markets ↔ BTC social discussion, Elon Musk tweet markets ↔ DOGE/Musk social buzz, Ethereum price ↔ ETH mentions

## Files Modified
- `Skills/sentiment-scanner/scripts/aggregate.py` — entity extraction, noise filtering, stop words
- Agent `8a5bd2e1-3d65-440f-853b-66fd3409ed53` — full instruction rewrite
