# Momentum Scoring Fix - Changelog

## Date: 2026-02-13

## Changes Made: Approach B (Hard Filter + Tiered Rewards)

### Backup Location
- **Original file:** `strategies/smart-money-tracker.ts.backup-before-momentum-fix`
- **Modified file:** `strategies/smart-money-tracker.ts`

### What Changed

#### BEFORE (Old Momentum Scoring):
```typescript
// Signal 3: Price momentum (25 points)
const priceChange1h = pair.priceChange?.h1 || 0;

if (priceChange1h > 50) {
  reasons.push(`Explosive momentum: +${priceChange1h.toFixed(0)}% in 1h`);
  confidence += 25;
} else if (priceChange1h > 20) {
  reasons.push(`Good momentum: +${priceChange1h.toFixed(0)}% in 1h`);
  confidence += 15;
}
```

**Problems:**
- Rewards tokens that already pumped 50%+ with +25 points
- Pushes confidence to 90-100 range (24.3% win rate)
- Buy-the-top behavior

#### AFTER (New Tiered Momentum):
```typescript
// Signal 3: Price momentum - EARLY ENTRY FILTER + TIERED REWARDS
const priceChange1h = pair.priceChange?.h1 || 0;

// HARD FILTER: Reject if already pumped 30%+
if (priceChange1h > 30) {
  return {
    interested: false,
    confidence: 0,
    reasons: [`Already pumped ${priceChange1h.toFixed(0)}% in 1h - too late to enter`]
  };
}

// TIERED REWARDS: Sweet spot is 10-20%
if (priceChange1h >= 10 && priceChange1h <= 20) {
  reasons.push(`Ideal early momentum: +${priceChange1h.toFixed(0)}% in 1h`);
  confidence += 15;
} else if (priceChange1h >= 5 && priceChange1h < 10) {
  reasons.push(`Building momentum: +${priceChange1h.toFixed(0)}% in 1h`);
  confidence += 8;
} else if (priceChange1h > 0 && priceChange1h < 5) {
  reasons.push(`Very early entry: +${priceChange1h.toFixed(0)}% in 1h`);
  confidence += 3;
}
// Note: 0% or negative momentum gets 0 points (unchanged)
```

**Benefits:**
- Blocks 30%+ pumps entirely (prevents buy-the-top)
- Rewards 10-20% sweet spot (proven best range)
- Differentiates early stages (3% vs 8% vs 15%)

### Expected Performance Impact

| Metric | Before | Expected After | Change |
|--------|--------|----------------|--------|
| Total Trades | 389 | ~352 | -37 (-9.5%) |
| Win Rate | 32.1% | 40-45% | +8-13% |
| Total P&L | +11.92 SOL | +13.73+ SOL | +15%+ |
| Avg Confidence | 66.4 | 64-68 | More stable |

### How to Revert

If performance is worse after testing:

```bash
cd /home/workspace/Projects/survival-agent/strategies
cp smart-money-tracker.ts.backup-before-momentum-fix smart-money-tracker.ts
```

Then restart the paper trading bot.

### Testing Plan

1. **Run paper bot for 50+ trades** with new momentum logic
2. **Track metrics:**
   - Win rate (target: >35%)
   - Average P&L per trade (target: >0.04 SOL)
   - Confidence score distribution (should see more 60-75 range)
   - Number of 30%+ pumps rejected
3. **Compare to baseline:**
   - If WR improves by 3%+: Deploy to mainnet
   - If WR drops or neutral: Revert and try Hybrid approach
4. **Timeline:** 2-3 days of paper trading

### Rollback Criteria

Revert if ANY of these occur:
- Win rate drops below 30% (worse than baseline)
- Average P&L per trade becomes negative
- Bot rejects >20% of all opportunities (over-filtering)
- Confidence scores cluster below 50 (under-scoring)

### Notes

- Backup includes full original logic for safe rollback
- This is Approach B from MOMENTUM_SCORING_ANALYSIS.md
- Hard filter at 30% based on backtest showing 75.7% loss rate for 30%+ pumps
- Tiered rewards based on 60-69 confidence range performing best (35.7% WR)
