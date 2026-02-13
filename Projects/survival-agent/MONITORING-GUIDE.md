# Paper Trading Monitor & Manual Sell Guide

## Token Monitor

Watch your paper trading positions in real-time with individual token tracking:

```bash
# One-time check
bun monitoring/token-monitor.ts

# Live watch (updates every 30 seconds)
./monitoring/watch-tokens.sh
```

### What it shows:
- ✅ Each token as a separate position
- 📊 Live P&L per token from Jupiter prices
- ⏰ Hold duration
- 🎯 Exit signals (take profit, stop loss, max hold time)
- 💰 Portfolio summary

Example output:
```
📌 Token 1/3: DOGE
────────────────────────────────────────────────────────────────────────────────
   Address: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
   Entry Time: 2/11/2026, 10:30:45 PM
   Hold Duration: 0h 25m
   Position Size: 0.0400 SOL
   Entry Price: $0.00001234
   Fetching live price...
   ✅ Current Price: $0.00001456
   💰 Current Value: 0.0472 SOL
   📈 P&L: +0.0072 SOL (+18.00%)
```

## Manual Sell Function

Sell all positions of a specific token:

```bash
# Sell by full address
bun sell-token.ts DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263

# Sell by partial address (first 8+ chars)
bun sell-token.ts DezXAZ8

# Force close rugged token (no sell route)
bun sell-token.ts DezXAZ8 --force
```

### What it does:
- ✅ Finds all open positions for that token
- 📊 Fetches current price from Jupiter
- 💰 Calculates P&L for each position
- 📝 Closes positions and saves to trades file
- 📈 Shows detailed sell summary

Example output:
```
🎯 Selling: DOGE
   Address: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
   Positions to close: 2

Fetching current price from Jupiter...
✅ Current Price: $0.00001456

Closing positions:

   ✅ Position 0.0400 SOL
      Entry: $0.00001234
      Exit:  $0.00001456
      P&L:   +0.0072 SOL (+18.00%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SELL SUMMARY
Total Positions Closed: 2
Total Invested: 0.0800 SOL
Total Returned: 0.0944 SOL
Net P&L: +0.0144 SOL (+18.00%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Quick Reference

**Monitor Commands:**
- `bun monitoring/token-monitor.ts` - One-time check
- `./monitoring/watch-tokens.sh` - Live watch

**Sell Commands:**
- `bun sell-token.ts <address>` - Sell all of a token
- `bun sell-token.ts <address> --force` - Force close rugged token

**Other Monitors:**
- `./monitoring/watch-paper-clean.sh` - Bot summary
- `./monitoring/watch-paper-verbose.sh` - Detailed logs

## Data Storage

All trades are saved to `/tmp/paper-trades.json` with this structure:

```json
[
  {
    "timestamp": 1707706245000,
    "tokenAddress": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "tokenSymbol": "DOGE",
    "amountSol": 0.04,
    "entryPrice": 0.00001234,
    "status": "open",
    "exitPrice": null,
    "exitTimestamp": null,
    "pnl": null,
    "exitReason": null
  }
]
```

The paper trader automatically:
- ✅ Loads existing trades on startup
- ✅ Saves trades after each buy
- ✅ Updates trades when positions close
- ✅ Persists across restarts
