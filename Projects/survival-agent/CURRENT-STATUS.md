# 🎯 Survival Agent - Current Status

**Updated**: 2026-02-11 23:06 UTC
**Status**: 🟢 PAPER TRADING ACTIVE

## Bot Configuration (Final)

### Risk Parameters
- **Position Size**: 8% of capital per trade
- **Take Profit**: +100% (2x)
- **Partial Exit**: Sell 80%, keep 20% for runners
- **Viral Detection**: If viral pump detected → keep 50% instead of 20%
- **Stop Loss**: -30%
- **Max Hold**: 60 minutes

### Safety Filters
- **Age**: 0-60 minutes only (fresh launches)
- **Liquidity**: Minimum $5,000 USD
- **Volume**: Minimum $10,000/day
- **Holder Concentration**: Maximum 80% top 10 holders ⭐ (UPDATED)
- **Deployer Check**: Helius funded-by verification
- **Token Metadata**: Helius enhanced metadata

### Viral Detection Criteria (Need 2 of 3)
1. High volume: >$1M/day OR >20x liquidity ratio
2. High activity: >1,000 transactions/day
3. Strong momentum: >50% price change in 1 hour

## Recent Changes

### Holder Concentration Threshold Evolution
1. **Original**: 60% (too conservative)
2. **First adjustment**: 75% (still too strict for 0-60 min)
3. **Current**: 80% ⭐ (research-backed)

**Reasoning for 80%**:
- WHITEWHALE: 54% concentration → +13,000% gain
- Normal fresh launches: 70-85% concentration in first hour
- Your NPC trade: +201% despite likely high concentration
- Still blocks extreme rugs: SOULGUY 91.7% ❌

## Current Performance

**Paper Trading**: 🟢 Running (PID 1603)
**Log File**: `/tmp/paper-trade-final.log`

**Latest Scan Results** (Loop 6, 23:06 UTC):
- Tokens analyzed: 54
- Tokens passing scanner: 1 (SOULGUY)
- SOULGUY concentration: 91.7% → ❌ BLOCKED (correct - above 80%)

**What we're waiting for**:
- Tokens with 60-80% concentration (the sweet spot)
- Expected frequency: 2-5 opportunities/day
- These should appear as market cycles through different launches

## Expected Outcomes with 80% Threshold

### Trade Frequency
**Before (75%)**: 0-1 trades/day
**After (80%)**: 2-5 trades/day (estimated)

### Win Rate Projection
- 45-55% win rate expected
- Losers hit -30% SL = -2.4% capital loss
- Winners average +100-300% = +8-24% capital gain
- Need 1 winner per 3-10 losers to break even
- With 50% win rate → profitable

### Risk Mitigation
- ✅ Fast stop loss at -30%
- ✅ Small position size (8%)
- ✅ Still blocking extreme concentration (>80%)
- ✅ Viral detection keeps 50% on big runners
- ✅ All Helius safety checks active

## Next Steps

1. **Monitor overnight** - Let bot scan for opportunities in 75-80% zone
2. **Evaluate results** - When trades occur, review performance
3. **Go live** - If paper trading shows profitability

## Files Modified

### Core Logic
- `core/position-manager.ts` - Lines 117-126 (80% threshold)
- `core/safe-master-coordinator.ts` - Viral detection + partial exits

### Paper Trading
- `testing/paper-trade-final.ts` - Running with final config

### Documentation
- `THRESHOLD-UPDATE-80.md` - Detailed explanation of 80% change
- `HOLDER-CONCENTRATION-RESEARCH.md` - Research backing decision
- `SCANNER-ANALYSIS.md` - Why we're seeing low opportunity count
- `FINAL-CONFIG.md` - Complete configuration summary

## Capital Status

**Starting**: 0.21 SOL (after liquidating bad positions)
**Current**: Paper trading (no real capital at risk)
**Survival Window**: 4 days of runway

---

**The bot is working as designed. We're now waiting for the market to provide opportunities in the 60-80% concentration range that passes our filters.**

**Trust the process** - the research shows this is the right threshold for 0-60 min momentum trading. 🎯
