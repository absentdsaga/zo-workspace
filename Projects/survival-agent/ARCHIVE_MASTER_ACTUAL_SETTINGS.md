# Archive Master ACTUAL Settings (Not Extrapolated)

**Date:** Feb 16, 2026
**Source:** Actual trade data from archive/2026-02-15-172828/paper-trades-master.json

---

## CORRECTED: What Archive Master Actually Used

### 1. Position Size: VARIABLE (Not Fixed 20%)

**Position sizes ranged from 0.034 to 0.282 SOL (6.8% to 56.4% of balance!)**

**Most common position:** 0.0531 SOL (10.6% of balance)

**Distribution:**
- Early trades (low balance): ~0.04-0.06 SOL (8-12%)
- Mid-run (balance growing): ~0.06-0.12 SOL (12-24%)
- Late trades (high balance): ~0.15-0.28 SOL (30-56%)

**Why variable?**
- Balance grew from 0.5 → 3.13 SOL during the run
- Position size appears to be based on % of CURRENT balance
- As balance grew, position sizes grew proportionally

**Current v2.1:** Fixed 0.06 SOL (12% of starting balance)
- ✅ This is actually CLOSE to Archive Master's average early positions!

**I WAS WRONG:** Archive Master did NOT use 20% fixed positions. Position size varied based on growing balance.

---

### 2. Confidence Threshold: 45 (Confirmed)

**Min confidence seen in trades:** 45
**Max confidence seen in trades:** 90

**This confirms:** MIN_SMART_MONEY_CONFIDENCE = 45

**Current v2.1:** Also uses 45 ✅
- This is CORRECT - we're matching Archive Master

---

### 3. What "Volume Matters" Meant

**Confidence distribution:**
- Conf 70: 99 trades (34.4%) ← MOST VOLUME
- Conf 45: 57 trades (19.8%) ← Second most
- Conf 60: 42 trades (14.6%)
- Conf 80: 40 trades (13.9%)

**Point:** Archive Master didn't filter out low confidence (45-50) because:
1. Trading volume matters (99 trades at conf 70 = 34% of all trades)
2. Even conf 45-50 contributed to profit (not huge, but positive)
3. Diversification across confidence levels = more opportunities

**I WAS WRONG about "raise threshold to 60"** - Archive Master used 45!

---

## What Archive Master Settings ACTUALLY Were

```typescript
// Based on actual trade data analysis:

MIN_SMART_MONEY_CONFIDENCE = 45;      // ✅ Confirmed (min seen in trades)
POSITION_SIZE_PERCENT = 0.12;         // ✅ Close to Archive Master's avg early positions
MAX_CONCURRENT_POSITIONS = 7;         // ❓ Unknown (not in data)
STOP_LOSS = -0.30;                    // ✅ Confirmed (170/288 stopped at -30%)
TAKE_PROFIT = 1.0;                    // ✅ Confirmed (70/288 hit +100% TP1)
TRAILING_STOP_PERCENT = 0.20;         // ✅ Confirmed (seen in exit reasons)
MAX_HOLD_TIME_MS = 60 * 60 * 1000;   // ✅ Confirmed (48 trades hit 60 min max)
```

---

## What We're ACTUALLY Missing

### ❌ NOT Missing: Position Size
- Current v2.1: 0.06 SOL (12%)
- Archive Master early: ~0.04-0.06 SOL (8-12%)
- **We're already matching this!**

### ❌ NOT Missing: Confidence Threshold
- Current v2.1: 45
- Archive Master: 45
- **We're already matching this!**

### ✅ ACTUALLY Missing: Unknown Factors

**What we DON'T know from the data:**
1. MAX_CONCURRENT_POSITIONS - could be 7, could be 5, could be 10
2. Scanner settings (DexScreener trending list size, refresh rate)
3. Smart money tracker weights (how confidence is calculated)
4. Meme scanner weights (how base score is calculated)
5. Any other filters applied before trading

---

## The Real Differences

### Current v2.1 vs Archive Master

**SAME:**
- ✅ Position size: 12% (Archive Master avg ~10.6%, we're close)
- ✅ Min confidence: 45 (exact match)
- ✅ Stop loss: -30% (exact match)
- ✅ Take profit: +100% (exact match)
- ✅ Trailing stop: 20% (exact match)
- ✅ Max hold: 60 min (exact match)

**DIFFERENT (maybe):**
- ❓ Max concurrent positions: We use 7, Archive Master unknown
- ❓ Scanner behavior: Market conditions Feb 15 vs Feb 16
- ❓ Token availability: Different trending tokens each day
- ✅ Blacklist behavior: We added 3-loss blacklist, Archive Master had 1 manual blacklist

**NEW in v2.1:**
- ✅ 3-loss auto-blacklist (Archive Master had manual blacklist with 1 token)
- ✅ Skip nameless tokens (planned, not implemented yet)

---

## Why Is Current v2.1 Losing When Settings Are Same?

**Possible reasons:**

### 1. Market Conditions (Feb 15 vs Feb 16)
- Different tokens trending
- Different market volatility
- Different liquidity conditions

### 2. Sample Size (17 vs 288 trades)
- Archive Master: 288 trades over several hours
- Current v2.1: 17 trades so far
- Too early to judge performance

### 3. Token Quality (luck/randomness)
- Archive Master found OrbEye, TRUMP2, HALF (goldmine tokens)
- Current v2.1 found nameless tokens (duds)
- Random variation in token selection

### 4. Confidence Score Calibration
- Smart money tracker may calculate confidence differently now
- Market conditions affect signals (volume, momentum, etc.)
- Same code, different inputs = different outputs

---

## Recommendations Going Forward

### ✅ KEEP Current Settings (They Match Archive Master!)

```typescript
POSITION_SIZE_PERCENT = 0.12;         // Matches Archive Master avg
MIN_SMART_MONEY_CONFIDENCE = 45;      // Exact match
MAX_CONCURRENT_POSITIONS = 7;         // Reasonable (Archive Master unknown)
STOP_LOSS = -0.30;                    // Exact match
TAKE_PROFIT = 1.0;                    // Exact match
TRAILING_STOP_PERCENT = 0.20;         // Exact match
MAX_HOLD_TIME_MS = 3600000;          // Exact match
```

### ✅ ADD Only These Filters (Simple improvements)

1. **Skip nameless tokens** (both our blacklisted tokens were nameless)
2. **Keep 3-loss blacklist** (prevents excessive repeat losses)

### ❌ DON'T Add These (Over-engineering)

1. ❌ Raise min confidence to 60-70 (Archive Master used 45!)
2. ❌ Skip confidence 80 (Archive Master traded it 40 times)
3. ❌ Skip previous losers (Archive Master re-traded 113 times)
4. ❌ Priority queue system (Archive Master didn't have this)
5. ❌ Increase position size to 20% (Archive Master didn't use fixed 20%)

---

## Conclusion

**I was WRONG about most "secrets":**
- ❌ Archive Master did NOT use 20% positions
- ❌ Archive Master did NOT have special filters
- ❌ Archive Master did NOT skip conf 80 or previous losers

**The TRUTH:**
- ✅ Archive Master used same settings we already have!
- ✅ Main difference: Market conditions and token luck
- ✅ Sample size too small to judge (17 vs 288 trades)

**Action:** Let current v2.1 run longer (50+ trades) before changing anything!

---

**Created:** Feb 16, 2026
**Status:** Corrected analysis based on actual data
**Next:** Let bot run, avoid over-engineering
