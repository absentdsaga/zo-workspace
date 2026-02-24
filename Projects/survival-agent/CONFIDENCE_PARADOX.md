# The Confidence Score Paradox

**Date:** Feb 16, 2026
**Discovery:** Confidence score correlation with success REVERSED between runs

## The Shocking Finding

### Current v2.1 Run
✅ **High confidence WORKS as expected:**
- High conf (≥70): 50.0% WR, +0.0104 SOL avg
- Low conf (<70): 0.0% WR, -0.0207 SOL avg
- **Difference: +50.0% WR, +0.0310 SOL advantage for high confidence**

### Archive Master (626% profit run)
❌ **High confidence UNDERPERFORMED:**
- High conf (≥70): 33.8% WR, +0.0078 SOL avg
- Low conf (<70): 44.3% WR, +0.0141 SOL avg
- **Difference: -10.5% WR, -0.0063 SOL advantage for LOW confidence**

### Archive Refactored (lost money)
⚠️ **Mixed signals:**
- High conf (≥70): 32.7% WR, +0.0001 SOL avg
- Low conf (<70): 40.3% WR, -0.0012 SOL avg
- **Higher WR for low conf, but slightly better avg P&L for high conf**

---

## Deep Dive: Archive Master's Best Confidence Levels

### The Winners (Best Avg P&L):

**1. Confidence 90: BEST**
- Trades: 9
- Win Rate: 66.7%
- Avg P&L: **+0.0902 SOL** (!!!)
- Total: +0.8116 SOL

**2. Confidence 60: GOLD MINE**
- Trades: 42
- Win Rate: 61.9%
- Avg P&L: **+0.0368 SOL**
- Total: +1.5475 SOL (MOST profit!)

**3. Confidence 65:**
- Trades: 1
- Win Rate: 100%
- Avg P&L: +0.0135 SOL

**4. Confidence 70:**
- Trades: 99
- Win Rate: 33.3%
- Avg P&L: +0.0110 SOL
- Total: +1.0866 SOL (2nd most profit)

### The Losers:

**1. Confidence 80: WORST**
- Trades: 40
- Win Rate: 27.5%
- Avg P&L: **-0.0187 SOL**
- Total: -0.7465 SOL (biggest loss!)

**2. Confidence 55:**
- Trades: 9
- Win Rate: 22.2%
- Avg P&L: -0.0132 SOL

**3. Confidence 45:**
- Trades: 57
- Win Rate: 36.8%
- Avg P&L: +0.0079 SOL (barely positive)

---

## The Confidence 60 Mystery

### Archive Master: Confidence 60 = GOLDMINE
- 42 trades
- 61.9% win rate (BEST!)
- +1.5475 SOL total (MOST profit!)
- +0.0368 SOL avg (2nd best after 90)

### Current v2.1: Confidence 60 = DEATH ZONE
- 3 trades
- 0% win rate
- -0.0722 SOL total
- -0.0241 SOL avg

**What changed?!**

---

## Confidence 80: The Consistent Loser

### Archive Master:
- 40 trades, 27.5% WR, -0.7465 SOL

### Archive Refactored:
- 42 trades, 26.2% WR, -1.1879 SOL

### Current v2.1:
- Only 2 open positions so far (Mochi +0.0206, MOG -0.0055)

**Confidence 80 has been bad across MULTIPLE runs!**

---

## Why the Paradox?

### Hypothesis 1: Different Market Conditions
- Archive Master ran on Feb 15 (different tokens available)
- Current v2.1 running Feb 16 (different market)
- Token quality may vary day-to-day

### Hypothesis 2: Score Calibration Changed
- Did confidence scoring logic change between runs?
- Are the same signals producing different scores?

### Hypothesis 3: Sample Size
- Current v2.1: Only 6 closed trades (tiny sample)
- Archive Master: 288 closed trades (large sample)
- Current data may be noise, not signal

### Hypothesis 4: The Sweet Spot Moved
- Archive Master's best: Conf 60 (61.9% WR)
- Current v2.1's best: Conf 70 (50% WR with 2 trades)
- Optimal confidence range may shift over time

---

## Key Insights

### 1. Confidence 90 is Consistently Good
- Archive Master: 66.7% WR, +0.0902 avg
- Archive Refactored: 66.7% WR, +0.0902 avg
- **Same performance across runs!**

### 2. Confidence 80 is Consistently Bad
- Archive Master: 27.5% WR, -0.0187 avg
- Archive Refactored: 26.2% WR, -0.0283 avg
- **Avoid this level!**

### 3. Confidence 60 Volatility
- Archive Master: 61.9% WR (BEST)
- Current v2.1: 0% WR (WORST)
- **Most unpredictable level**

### 4. The U-Shape Pattern (Archive Master)
```
Conf 90: 66.7% WR ← PEAK
Conf 80: 27.5% WR ← VALLEY
Conf 70: 33.3% WR
Conf 60: 61.9% WR ← PEAK
Conf 55: 22.2% WR ← VALLEY
Conf 50: 38.7% WR
Conf 45: 36.8% WR
```

**Pattern:** High and mid-range confidence good, conf 80 and 55 are valleys!

---

## Recommendations

### Based on Archive Master (Large Sample):

**GOOD confidence levels:**
- ✅ 90 (66.7% WR, +0.0902 avg) - **BEST**
- ✅ 60 (61.9% WR, +0.0368 avg) - **2ND BEST**
- ✅ 70 (33.3% WR, +0.0110 avg) - Decent
- ✅ 50 (38.7% WR, +0.0028 avg) - Okay
- ✅ 45 (36.8% WR, +0.0079 avg) - Okay

**BAD confidence levels:**
- ❌ 80 (27.5% WR, -0.0187 avg) - **WORST**
- ❌ 55 (22.2% WR, -0.0132 avg) - Bad

### Proposed Filter (v2.2):

**Option A: Accept 60-70 + 90**
```typescript
if (confidence >= 60 && confidence <= 70) {
  // Accept - Archive Master's best range
} else if (confidence >= 90) {
  // Accept - consistently excellent
} else {
  // Skip
}
```

**Option B: Skip the valleys (80, 55)**
```typescript
if (confidence === 80 || confidence === 55) {
  // Skip - these levels consistently lose
  continue;
}
if (confidence < 45) {
  // Skip - too low
  continue;
}
// Accept all others
```

**Option C: Simple threshold at 60**
```typescript
if (confidence < 60) {
  continue; // Skip
}
// But be aware: conf 80 still loses even though it's >60!
```

---

## The Bigger Question

**Why does confidence 80 lose money?**

Possible reasons:
1. **Overfitting**: Score 80 tokens may be "too obvious" - already pumped
2. **Competition**: Everyone trades conf 80+ tokens = worse entry prices
3. **False signals**: Some scoring factors may be misleading at this level
4. **Sample bias**: Conf 80 tokens may be in a specific category that dumps

**Need to investigate:** What makes conf 80 different from conf 60/70?

---

## Action Items for v2.2

1. **Implement confidence filter that skips 80** (proven loser)
2. **Keep minimum at 60** (Archive Master's goldmine)
3. **Prioritize 90 when available** (consistently best)
4. **After 20+ trades: Re-analyze** (current sample too small)

---

**Created:** Feb 16, 2026
**Status:** Discovery phase
**Next:** Implement smart confidence filtering based on historical data
