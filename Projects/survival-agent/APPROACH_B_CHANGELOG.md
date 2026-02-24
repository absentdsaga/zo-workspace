2026-02-13 22:54:01

# Approach B: Prevent Late Entries with Momentum Filter

## Current Settings (Backup saved)
- File: smart-money-tracker.ts.backup-before-approach-b
- Momentum scoring: Tiered (0-5%: 3pts, 5-10%: 8pts, 10-20%: 15pts)
- Hard filter: Reject if >30% pump in 1h

## Changes in Approach B
- Lower hard filter from 30% to 20% (reject earlier)
- Remove all momentum points - only use as entry gate
- Focus scoring on: volume (25pts), buy pressure (20pts), liquidity (20pts), market cap (10pts)
- Total possible: 75 points (down from 90)
- MIN_SMART_MONEY_CONFIDENCE stays at 45

## Rationale
Backtest showed 0% win rate on tokens with >20% 1h momentum. By filtering these out and not rewarding momentum with points, we should catch tokens earlier in their cycle.


## Implementation Complete

### What Changed
1. **Hard filter lowered**: 30% → 20% (rejects tokens earlier)
2. **Momentum scoring removed**: 0-15 points → 0 points
3. **New max score**: 75 points (was 90)
   - Volume: 25 points max
   - Buy pressure: 20 points max
   - Liquidity: 20 points max
   - Market cap: 10 points max

### Scoring Examples
**Before (with momentum points):**
- Token at +15% 1h pump → 15 momentum points → could hit 90/100 total
- High chance of late entry

**After (no momentum points):**
- Token at +15% 1h pump → 0 momentum points → max 75/100 total
- Only passes if fundamentals are strong (volume, liquidity, buy pressure)
- Momentum is just a gate: >20% = instant reject, ≤20% = allowed but no bonus

### Expected Behavior
- Should enter tokens EARLIER in their cycle
- Fewer trades (stricter filter + no momentum boost)
- Better quality entries (based on fundamentals, not hype)

### How to Revert
```bash
cp /home/workspace/Projects/survival-agent/strategies/smart-money-tracker.ts.backup-before-approach-b \
   /home/workspace/Projects/survival-agent/strategies/smart-money-tracker.ts
```

### Next Steps
1. Run paper bot for 2-4 hours
2. Compare win rate vs previous session
3. If worse: revert using command above
4. If better: keep and monitor for another session
