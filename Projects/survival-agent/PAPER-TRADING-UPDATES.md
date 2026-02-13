# Paper Trading Bot Updates

## Changes Made (2026-02-11)

### 1. Increased Concurrent Token Positions
**Previous behavior:** Bot would only trade 3 tokens at a time (implicitly limited by the logic that skipped when all qualified tokens were already held)

**New behavior:** Bot can now trade up to **10 tokens concurrently**

**Technical changes:**
- Added `MAX_CONCURRENT_POSITIONS = 10` constant
- Replaced logic that checked "all qualified tokens already held" with a check for max concurrent positions
- Bot will now continue finding new opportunities as long as `openPositions < MAX_CONCURRENT_POSITIONS`
- Updated initialization logs to show max concurrent positions

### 2. Added Scanner Source Tracking
**New feature:** The bot now tracks and displays which scanner each token came from

**Scanner sources:**
- `pumpfun` - Found via PumpPortal WebSocket feed (ultra-early catches)
- `dexscreener` - Found via DexScreener API (established tokens)
- `both` - Found in BOTH sources (gets +20 score boost!)

**Where it's displayed:**
1. When analyzing opportunities: Shows source alongside score
2. When monitoring positions: Shows source in brackets next to token symbol
3. Stored in trade logs for future analysis

**Technical changes:**
- Added `source` field to `TradeLog` interface
- Capture source when creating trades: `source: best.source`
- Display format: `📊 SYMBOL [source]:`

## Example Output

### Before:
```
2️⃣  Analyzing top opportunity:
   Token: PEPE (8ZxYq2x...)
   Score: 75/100
   Signals: Ultra fresh (<5 min), 5.2 SOL initial buy
```

### After:
```
2️⃣  Analyzing top opportunity:
   Token: PEPE (8ZxYq2x...)
   Score: 75/100
   Source: both
   Signals: Ultra fresh (<5 min), 5.2 SOL initial buy, ⭐ Found in both sources
```

### Position Monitoring Before:
```
📊 PEPE:
   Entry: $0.00000123 | Current: $0.00000156
```

### Position Monitoring After:
```
📊 PEPE [both]:
   Entry: $0.00000123 | Current: $0.00000156
```

## Benefits

1. **More diversification**: 10 positions means better risk distribution
2. **Better opportunities**: Won't miss good tokens just because 3 positions are filled
3. **Scanner insights**: See which scanner is finding the best performing tokens
4. **Data for analysis**: Can later analyze which source produces better returns

## File Modified
- `/home/workspace/Projects/survival-agent/testing/paper-trade-master-fixed.ts`

## Testing
Run with: `bash /home/workspace/Projects/survival-agent/start-paper-master-fixed.sh`
