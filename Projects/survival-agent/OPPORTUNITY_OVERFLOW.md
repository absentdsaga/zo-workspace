# Opportunity Overflow Problem

**Date:** Feb 16, 2026
**Issue:** Bot constantly finds 13 opportunities but can only trade 7

---

## The Situation

**Every scan (every 15 seconds):**
- DexScreener finds: **13 opportunities**
- All 13 meet minimum score (≥40)
- Top scores: [75, 75, 75, 75, 75]
- Bot capacity: **7 concurrent positions**
- **Result:** Always at max capacity, 6 opportunities skipped each scan

---

## Why This Happens

### 1. Low Minimum Score (40)
```typescript
private readonly MIN_SCORE = 40;
```

**Current behavior:**
- Score 40+ qualifies
- 13 tokens consistently qualify
- Bot takes first 7, skips remaining 6

### 2. Fast Scanning (15 seconds)
```typescript
private readonly SCAN_INTERVAL_MS = 15000; // 15 seconds
```

**Math:**
- Scan: 15s
- Avg trade duration: 15-60 min
- Slots refill faster than they empty
- **Result:** Always maxed out

### 3. All Scores Are 75
**Top 5 scores:** [75, 75, 75, 75, 75]

**This means:**
- Multiple tokens tied at same score
- No clear "best" opportunity
- Bot just picks first 7 alphabetically/chronologically
- Quality differentiation is poor

---

## Archive Master Comparison

### Archive Master (626% profit)
**Unknown:**
- How many opportunities per scan?
- What was the minimum score?
- Were they always maxed out?

**Hypothesis:**
- Either found fewer opportunities (higher threshold)
- Or had better score differentiation (scores varied more)
- Or had lower max concurrent (more selective)

### Current v2.1
**Known:**
- 13 opportunities per scan
- All qualify (score ≥40)
- Always maxed at 7/7
- Top scores all identical (75)

---

## The "Always Full" Problem

**Your observation:** "Why is it always full?"

**Answer:** You're seeing the same pattern every time because:

1. **Supply > Demand**
   - 13 opportunities found
   - Only 7 positions available
   - Surplus: 6 tokens

2. **Continuous Refilling**
   - Scan every 15s
   - Position closes (avg 30 min)
   - New scan immediately fills slot
   - Back to 7/7 within seconds

3. **No Scarcity**
   - Bot never "runs out" of opportunities
   - Always has 13 to choose from
   - Always picks 7
   - Remaining 6 ignored

---

## Why Score 75 Keeps Appearing

**Scoring breakdown (from meme-scanner.ts):**

Possible signals:
- Volume spike: 25 points
- Price momentum: 30 points
- Strong liquidity: 10 points
- Fresh launch (<15 min): 25 points

**Score 75 = 25 + 30 + 10 + 10 (partial)**

This suggests most tokens have:
- ✅ Volume spike
- ✅ Price momentum
- ✅ Some liquidity
- ⚠️ NOT fresh launches (missing 25 pt bonus)

**Problem:** Score doesn't differentiate well at the top end.

---

## Solutions

### Option A: Raise Minimum Score
```typescript
// Current
private readonly MIN_SCORE = 40;

// Proposed
private readonly MIN_SCORE = 60;
```

**Expected impact:**
- Fewer qualifying tokens (maybe 5-8 instead of 13)
- More selective
- Less likely to hit max capacity

---

### Option B: Reduce Max Concurrent Positions
```typescript
// Current
private readonly MAX_CONCURRENT_POSITIONS = 7;

// Proposed
private readonly MAX_CONCURRENT_POSITIONS = 3-5;
```

**Benefits:**
- More selective (only best opportunities)
- Lower capital at risk
- Better risk management
- Not always maxed out

**Trade-offs:**
- Fewer total trades
- May miss some opportunities

---

### Option C: Better Score Differentiation

**Problem:** Scores cluster around 75

**Solution:** Make scoring more granular
```typescript
// Instead of fixed points (25, 30, 10)
// Use sliding scales

// Example: Volume spike (0-40 points based on ratio)
const volumeScore = Math.min(40, volumeRatio * 10);

// Example: Price momentum (0-50 points based on %)
const momentumScore = Math.min(50, priceChange1h * 1.5);
```

**Result:** Scores spread from 40-100 instead of clustering at 75

---

### Option D: Use Smart Money Confidence as Filter

**Current flow:**
1. Meme scanner finds 13 tokens (score 75)
2. Bot picks first 7
3. **THEN** checks smart money confidence
4. If confidence < 45, skip and try next

**Better flow:**
1. Meme scanner finds 13 tokens
2. Check smart money confidence on ALL 13
3. **THEN** pick top 7 by confidence
4. Trade only those

**Benefit:** Better pre-filtering using confidence scores

---

## The "Same Tokens" Problem

**Your observation:** "Why same tokens showing up?"

**Answer:** Two separate issues:

### Issue 1: Limited Token Pool
- DexScreener trending list is finite
- Same ~20-30 tokens stay trending for hours
- Bot sees same tokens repeatedly
- Combined with no "skip previous losers" filter = repeats

### Issue 2: Nameless Tokens
- Tokens with empty symbols show as "‎"
- Hard to visually distinguish
- Appear to be "the same" but are different addresses
- Creates confusion

---

## Data-Driven Recommendation

**Based on current run:**

**Confidence score analysis shows:**
- Conf 90: 1 trade, 100% WR (1W/0L)
- Conf 80: 3 trades, 33% WR (1W/2L)
- Conf 70: 5 trades, 40% WR (2W/3L)
- Conf 60: 4 trades, 0% WR (0W/4L)
- Conf 50: 2 trades, 0% WR (0W/2L)
- Conf 45: 2 trades, 50% WR (1W/1L)

**Best approach:** Use confidence as primary filter

### Recommendation: v2.2 Implementation

**1. Raise min confidence to 70**
```typescript
private readonly MIN_SMART_MONEY_CONFIDENCE = 70; // Up from 45
```

**2. Skip confidence 80** (proven loser in Archive Master)
```typescript
if (confidence === 80) {
  console.log('   ⏭️  SKIPPED: Confidence 80 (historical underperformer)');
  continue;
}
```

**3. Reduce max positions to 5**
```typescript
private readonly MAX_CONCURRENT_POSITIONS = 5; // Down from 7
```

**4. Add "skip previous losers" filter**
```typescript
const previouslyLost = this.trades.some(t =>
  t.tokenAddress === opp.address &&
  t.status === 'closed_loss'
);
if (previouslyLost) {
  continue;
}
```

**Expected impact:**
- Fewer qualifying opportunities (5-8 instead of 13)
- Better quality (conf 70-90 only, skip 80)
- Not always maxed out (5 max instead of 7)
- No repeat losers (skip previous losers)

---

## Summary

**Current state:**
- 13 opportunities per scan
- All score 75
- Always use 7/7 positions
- 6 opportunities ignored
- Same tokens repeat

**Root cause:**
- Min score too low (40)
- Poor score differentiation (all 75)
- Too many positions (7)
- No repeat filter

**Solution:**
- Raise confidence threshold
- Skip proven bad levels (80)
- Reduce max positions
- Add previous loser filter

---

**Created:** Feb 16, 2026
**Status:** Explains why bot is always maxed out
**Next:** Implement filters in v2.2
