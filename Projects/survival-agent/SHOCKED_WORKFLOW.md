# Shocked Degen Chat Workflow

## The Reality
- You manually share Shocked Discord chat exports (PDFs)
- These are their "degen chat" - general discussion channel
- NOT an automated feed - manual extraction required

## When You Share a PDF
1. **Extract ALL token mentions**
   - Look for $ symbols
   - Find contract addresses
   - Note context/sentiment
   
2. **Lookup live data** (DexScreener API)
   - Price, FDV, liquidity, volume
   - Price changes (1h, 24h)
   - Check if still active
   
3. **Add to Shocked watchlist**
   ```bash
   cd /home/workspace/Projects/survival-agent
   # Create add-shocked-MMDD.ts with tokens
   bun add-shocked-MMDD.ts
   ```

4. **Bot picks them up**
   - Paper trading bot scans shocked watchlist every 15s
   - Scores each token (priority + freshness + momentum)
   - Trades if score >= MIN_SHOCKED_SCORE (30)

## Current Watchlist
Run: `bun add-shocked-call.ts --list`

## Priority Guidelines
- **HIGH**: Direct call from known profitable member
- **MEDIUM**: Strong narrative/viral potential (like BABYBOO)
- **LOW**: Chart shares, old tokens, general discussion

## Notes Template
`"[Context] - [Caller/Source], [Timestamp]"`

Example: `"TikTok viral - 250k videos, discussed 6:38 PM"`
