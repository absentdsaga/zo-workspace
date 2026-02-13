# 🎯 Holder Concentration Threshold Update

**Updated**: 2026-02-11 22:38 UTC
**Change**: Relaxed from 60% → 75% top 10 holder concentration

## What Changed

### Before
```typescript
// RED FLAG: Top 10 holders own >60% (too centralized)
if (top10Percent > 60) {
  return { safe: false, ... };
}
```

### After
```typescript
// RED FLAG: Top 10 holders own >75% (too centralized for fresh launches)
// Relaxed from 60% to 75% for 0-60 min momentum trading
if (top10Percent > 75) {
  return { safe: false, ... };
}
```

## Rationale

Following the **Crypto Trader** expert advice:
- Fresh 0-60 min launches ARE concentrated (that's normal)
- The real alpha is in the first hour
- Accepting 60-75% concentration opens up more early opportunities
- Your -30% stop loss protects against rugs
- The winners (that don't rug) will 5x-20x and pay for the losers

## Risk Profile

**Old threshold (60%)**:
- Very conservative
- Missed most fresh launches (too strict for 0-60 min)
- Found almost no opportunities

**New threshold (75%)**:
- More aggressive for early-stage trading
- Accepts that fresh launches have concentration
- Still blocks EXTREME concentration (like Hosico's 97.2%)
- Higher rug risk, but higher reward potential

## What This Means

**Will PASS (60-75% concentration)**:
- Early launches with moderate concentration
- Tokens starting to distribute but still fresh
- Potential for big gains if they're legit

**Will BLOCK (>75% concentration)**:
- Extreme concentration (like Hosico 97.2%)
- Likely rug pull setups
- Dev + insider wallets dominating

## Current Status

**Paper Trading Live** (PID 1214)
- Threshold: >75% blocks
- Still finding Hosico (97.2%) and correctly blocking it
- Waiting for tokens in the 60-75% range to appear

**Expected Behavior**:
- More opportunities than before (60% threshold)
- Still selective (blocks worst offenders >75%)
- Trade frequency: TBD (monitoring)

## Files Modified

1. `/home/workspace/Projects/survival-agent/core/position-manager.ts`
   - Line 117-143: Updated holder distribution check
   - Changed threshold from 60% → 75%
   - Updated reason messages

## Next Steps

1. ✅ Updated threshold to 75%
2. ✅ Restarted paper trading
3. 📊 Monitor for 1-2 hours to see trade frequency
4. 📈 Evaluate if we're finding opportunities now
5. 🎯 Adjust again if needed

---

**Trade-off accepted**: Higher risk of rugs, higher potential for early alpha gains.
**Protection**: -30% stop loss cuts losses fast on rugs.
**Goal**: Find the sweet spot between safety and opportunity.
