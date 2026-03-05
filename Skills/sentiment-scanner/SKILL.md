---
name: sentiment-scanner
description: Multi-platform social media sentiment scanner for crypto, memecoins, and prediction markets. Scans X/Twitter, Instagram, and TikTok for fresh signals, then cross-references with Polymarket and Kalshi to find underpriced bets. Designed for continuous automated scanning.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: "1.0.0"
  created: "2026-03-04"
---

# Sentiment Scanner

Multi-platform social sentiment engine for alpha generation.

## Architecture

```
X/Twitter (bird CLI) ─┐
Instagram (browser)  ──┼── Sentiment Engine ── Signal Scorer ── Dashboard + SMS Alerts
TikTok (agent-browser)─┘         │
                                 ├── Polymarket API (free, no auth)
                                 └── Kalshi API (free, no auth)
```

## Scripts

### Core Scanner
```bash
python3 Skills/sentiment-scanner/scripts/scan_x.py          # X/Twitter sentiment
python3 Skills/sentiment-scanner/scripts/scan_polymarket.py  # Polymarket underpriced bets
python3 Skills/sentiment-scanner/scripts/scan_kalshi.py      # Kalshi underpriced bets
python3 Skills/sentiment-scanner/scripts/scan_tiktok.py      # TikTok trending crypto
```

### Signal Aggregator
```bash
python3 Skills/sentiment-scanner/scripts/aggregate.py        # Cross-platform signals
```

## Data Flow

1. **Scan** — Each platform module produces raw signals (trending topics, sentiment scores, engagement velocity)
2. **Score** — AI scores each signal for: freshness, cross-platform presence, momentum direction, and deviation from prediction market odds
3. **Alert** — High-conviction signals get sent via SMS + dashboard update

## Key Concepts

- **Freshness**: Only signals < 24h old. No stale meta.
- **Cross-platform amplification**: Something trending on X AND TikTok AND IG = 3x signal weight
- **Sentiment-odds divergence**: When social sentiment is strongly bullish/bearish but prediction market odds haven't moved = edge opportunity
- **Engagement velocity**: Rate of change matters more than absolute numbers

## Accounts to Monitor (X/Twitter)

### Tier 1 — Memecoin Callers (watch closely)
- @MustStopMurad, @RookieXBT, @cometcalls, @thisisdjen, @free_electron0
- @flooksta, @levigem, @gammichan, @Palgrani2, @_Shadow36

### Tier 2 — On-chain / Wallet Trackers
- @W0LF0FCRYPT0, @nofxlines, @sro_cto, @zinceth, @badattrading_

### Tier 3 — Culture / Meme Arbitrage
- @Chubbicorn230, @Ga__ke, @BRADLEYBANNED, @frankdegods, @Agnesrium

### TikTok — Hashtags to Track
#memecoin #solana #crypto #cryptotok #defi #altcoin #web3 #pumpdotfun #degen

### Instagram — Scanner Account
@loveofflinedating (burner, follow CT/meme accounts via this account)

## Prediction Markets

### Polymarket (no auth needed)
- API: `https://clob.polymarket.com`
- Gamma API: `https://gamma-api.polymarket.com`
- Focus: Politics, crypto, geopolitics, culture markets
- Target: Markets with < 30% odds where social sentiment suggests higher probability

### Kalshi (no auth needed for reading)
- API: `https://api.elections.kalshi.com/trade-api/v2`
- Focus: All categories
- Target: Same divergence strategy

## Output Format

Each signal includes:
- Topic/token/market
- Sentiment score (-100 to +100)
- Freshness (hours since first detection)
- Platform sources (X, IG, TT)
- Cross-platform presence score
- Related prediction market (if any)
- Current odds vs sentiment-implied odds
- Confidence level (low/medium/high)
