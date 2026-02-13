# 🎯 FINAL SURVIVAL BOT CONFIGURATION

## Configuration Summary

**Your Preferred Settings (Updated 2026-02-11)**

### Risk Parameters
- **Position Size**: 8% (original - allows 12.5 trades before circuit breaker)
- **Take Profit**: +100% (survival - let winners run 2x)
- **Stop Loss**: -30% (original - original risk tolerance)
- **Max Hold**: 60 minutes (original - longer time to develop)
- **Min Score**: 60 (original threshold)

### Exit Strategy - PARTIAL EXITS (20% Runners)
**At +100% Take Profit:**
- Sell 80% of position
- Hold 20% as a "runner" for potential 5x-10x gains
- Runners remain until stop loss or max hold time

**At -30% Stop Loss:**
- Sell 100% of position (cut losses fast)

**At 60 Min Max Hold:**
- Sell 100% of remaining position (don't bag-hold)

### Entry Strategy (Original - Momentum Chasing)
- **Age**: 0-60 minutes (fresh launches)
- **Momentum**: Seeking high momentum (+10%+ moves)
- **Volume**: Seeking volume spikes (FOMO indicators)
- **Liquidity**: Minimum $5k (lower threshold for early entry)
- **Strategy**: Chase the pump, exit fast with profit or loss

### Safety Checks (Enhanced with All Helius APIs)

**Before Every Buy:**
1. ✅ Duplicate prevention (don't buy same token twice)
2. ✅ Deployer verification (funded-by API - reject mixer/tornado)
3. ✅ Holder distribution (<60% top 10 concentration)
4. ✅ Token metadata (not frozen, check mint authority)
5. ✅ Sell route validation (can we exit?)

**During Position:**
6. ✅ Real-time price monitoring (every 10 seconds)
7. ✅ Automated exits (TP/SL/Max hold)
8. ✅ Partial exit logic (80/20 split on TP)

## Why This Configuration?

### Original Risk (8% position, -30% SL, 60 min hold)
- **More aggressive**: Larger positions, deeper stop losses
- **Better for momentum**: Gives trades time to develop
- **Higher reward potential**: 8% positions can make real money on 2x-3x moves

### Survival TP (+100% with 20% runners)
- **Takes profit at 2x**: Secures gains early
- **Leaves skin in the game**: 20% runner can catch 5x-10x moves
- **Best of both worlds**: Banking profits + lottery ticket upside

### Original Entry (0-60 min, momentum chasing)
- **Catches early pumps**: Fresh launches 0-60 min
- **Rides momentum**: Gets in during FOMO phase
- **Higher risk/reward**: More volatile = more profit potential

## What Changed from Survival V2?

| Parameter | Survival V2 | Your Final Config |
|-----------|-------------|-------------------|
| Position Size | 5% | **8%** (original) |
| Take Profit | +100% | **+100%** (kept) |
| Stop Loss | -20% | **-30%** (original) |
| Max Hold | 30 min | **60 min** (original) |
| Runner % | 50% | **20%** (your preference) |
| Entry Age | 2-6 hours | **0-60 min** (original) |
| Entry Style | Consolidation | **Momentum** (original) |
| Min Liquidity | $50k | **$5k** (original) |

**Result**: More aggressive, higher risk/reward, momentum-focused strategy with 20% runners for lottery ticket upside.

## Paper Trading Results (Pending)

Running 10 paper trades to validate before live deployment...

### Expected Behavior
1. Scanner finds 0-60 min old tokens with momentum
2. Helius safety checks filter out rugs/scams
3. Buys with 8% position size
4. Monitors every 10 seconds for exit conditions
5. At +100%: Sells 80%, holds 20% runner
6. At -30%: Sells 100%
7. At 60 min: Sells 100% of remaining

### What Success Looks Like
- Win rate: 40-60% (acceptable for 2:1 reward:risk)
- Average winner: +100% to +300% (2x-4x)
- Average loser: -30% (stop loss hit)
- Net P&L: Positive if winners > losers

## Files Updated

1. `core/position-manager.ts` - Updated TP to +100%
2. `core/safe-master-coordinator.ts` - Updated runner % to 20%
3. `testing/paper-trade-final.ts` - New paper trading script
4. This file - Configuration documentation

## Next Steps

1. ✅ Configuration updated
2. 📄 Paper trade 10 trades
3. 📊 Analyze results
4. 🚀 Deploy live if results are good
5. 💰 Monitor and iterate

---

**Generated**: 2026-02-11 17:10 UTC
**Status**: Ready for paper trading
**Mode**: PAPER TRADE (simulated, no real SOL)
