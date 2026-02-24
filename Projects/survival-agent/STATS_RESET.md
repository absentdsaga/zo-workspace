# Paper Trading Stats Reset ✅

**Date:** Feb 14, 2026 20:05 UTC

## What Was Reset

### Previous Stats (Before Reset)
- **Balance:** 8.96 SOL
- **Total P&L:** +16.10 SOL (+3,220%)
- **Trades:** 209
- **Starting balance:** 0.5 SOL

### New Stats (After Reset)
- **Balance:** 0.5 SOL
- **Total P&L:** 0 SOL
- **Trades:** 0
- **Starting balance:** 0.5 SOL

## What Was Preserved

**Blacklist:** All rugged tokens are still blacklisted (kept from previous run)

## Backup Location

All previous data backed up to:
```
/tmp/paper-backups/20260214_200537/
├── paper-trades-master.json (138 KB - 209 trades)
└── paper-trades-state.json
```

You can review the old data anytime from the backup.

## Why Reset?

To observe the impact of **real Jito costs** on P&L from a clean slate:

### Previous Run (Made-Up Costs)
- Used hardcoded tips: 0.0005 SOL ($0.044/trade)
- Did NOT subtract fees from P&L
- Result: +16.10 SOL gross (unrealistic)

### New Run (Real Costs)
- Using real tips: 0.0001 SOL ($0.0088/trade at p75)
- **Subtracts all fees from P&L** (entry + exit)
- Shows: Gross P&L → Fees → Net P&L
- Result: Will show realistic mainnet profitability

## What You'll See Now

When the bot runs, status updates will look like:

```
📈 Net P&L: +6.14 SOL (+1,228%)
   ├─ Gross P&L: +6.20 SOL
   └─ Total fees: -0.058 SOL (Jito p75: $0.0088/trade)
```

**Net P&L = actual profit after all costs**

## Cost Breakdown (Per Trade)

| Cost Type | Amount (SOL) | Amount (USD) |
|-----------|--------------|--------------|
| Entry Jito tip (p75) | 0.0001 | $0.0088 |
| Entry priority fee | ~0.000006 | ~$0.0005 |
| Exit Jito tip (p75) | 0.0001 | $0.0088 |
| Exit priority fee | ~0.000006 | ~$0.0005 |
| **Total per trade** | **~0.000212** | **~$0.0186** |

**Monthly (5,500 trades):** ~$102 in fees

## Expected Results

If paper bot maintains similar win rate:

```
Previous: +16.10 SOL gross over 209 trades
Expected now: +~15.96 SOL net (after -0.14 SOL fees)

Fees = ~0.9% of gross profit
```

The strategy should remain **highly profitable** even with real costs.

## Next Steps

1. ✅ Stats reset to 0.5 SOL
2. ✅ Real Jito costs implemented (p75)
3. ✅ Fee tracking enabled
4. 🚀 **Run paper bot** - observe realistic P&L
5. 📊 Compare to previous run (backup available)

Start the bot with:
```bash
bun testing/paper-trade-bot.ts
```
