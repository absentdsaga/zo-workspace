# Confidence Score Strategy - The U-Shape Discovery

**Date:** Feb 16, 2026
**Discovery:** Confidence scores have a U-shape pattern, NOT linear

---

## Archive Master Performance by Confidence

| Rank | Conf | Trades | Win Rate | Avg P&L | Total P&L | Verdict |
|------|------|--------|----------|---------|-----------|---------|
| 🏆 #1 | 90 | 9 | 66.7% | +0.0902 SOL | +0.8116 SOL | **BEST** |
| 🏆 #2 | 60 | 42 | 61.9% | +0.0368 SOL | +1.5475 SOL | **2ND BEST** |
| 📊 #3 | 70 | 99 | 33.3% | +0.0110 SOL | +1.0866 SOL | Okay |
| 📊 #4 | 45 | 57 | 36.8% | +0.0079 SOL | +0.4484 SOL | Okay |
| 📊 #5 | 50 | 31 | 38.7% | +0.0028 SOL | +0.0867 SOL | Meh |
| 💀 #6 | 55 | 9 | 22.2% | -0.0132 SOL | -0.1189 SOL | Bad |
| 💀 #7 | 80 | 40 | 27.5% | -0.0187 SOL | -0.7465 SOL | **WORST** |

---

## The U-Shape Pattern

```
Avg P&L by Confidence Level:

+0.09 SOL |              90 ← PEAK
          |
+0.04 SOL |                       60 ← PEAK
          |
+0.01 SOL |                    70
  0 SOL   |                 45 50
          |              55 ← VALLEY
-0.02 SOL |           80 ← VALLEY (WORST!)
```

**Pattern:** High (90) and Mid (60) are great, but 80 and 55 are valleys!

---

## Why "Ranking by Top Confidence" DOESN'T Work

**If we only traded highest confidence first:**

1. **Conf 90:** Only 9 opportunities total (too rare, would barely trade)
2. **Conf 80:** Next in line, 40 trades, **LOSES -0.7465 SOL total!**
3. **Conf 70:** 99 trades, barely profitable (+1.0866 SOL)

**Problem:** The 2nd highest level (80) is the WORST performer!

**We'd miss:** Conf 60's goldmine (42 trades, +1.5475 SOL, 61.9% WR)

---

## Why Does Conf 80 Lose Money?

**Possible explanations:**

### 1. "Too Obvious" Theory
- Conf 80 tokens may be already pumping hard
- Everyone sees them → worse entry prices
- Late to the party = buy high, sell low

### 2. "False Signal" Theory
- Whatever combination creates score 80 may include misleading signals
- Example: High volume + momentum might signal "already pumped"

### 3. "Market Competition" Theory
- Conf 80 tokens get more bot attention
- More competition = worse fills, slippage

### 4. "Sweet Spot" Theory
- Conf 60 tokens are "Goldilocks zone" - not too hot, not too cold
- Conf 90 tokens are rare gems (only 9 in 288 trades!)
- Conf 80 tokens are just "mediocre hype"

---

## Recommended Strategy for v2.2

### Option A: Accept 60-70 + 90, Skip 80 (Targeted)
```typescript
if (confidence >= 90) {
  // Accept - consistently excellent (66.7% WR)
} else if (confidence >= 60 && confidence <= 70) {
  // Accept - Archive Master's goldmine (60: 61.9% WR, 70: 33.3% WR)
} else if (confidence === 80) {
  console.log('   ⏭️  SKIPPED: Conf 80 (proven underperformer)');
  continue;
} else if (confidence < 60) {
  // Skip - too low
  continue;
}
```

**Pros:**
- Captures the two peaks (90 and 60-70)
- Explicitly avoids the valley (80)
- Backed by 288 trades of data

**Cons:**
- More complex logic
- May confuse users ("why skip 80 but accept 70?")

---

### Option B: Accept 60+ but Skip 80 (Simple)
```typescript
if (confidence === 80) {
  console.log('   ⏭️  SKIPPED: Conf 80 (proven underperformer)');
  continue;
}

if (confidence < 60) {
  console.log('   ⏭️  SKIPPED: Low confidence (< 60)');
  continue;
}

// Accept 60-79, 81-100
```

**Pros:**
- Simple rule: "60+ except 80"
- Easy to explain
- Captures most of the good range

**Cons:**
- Still accepts conf 70 (only 33.3% WR)
- But conf 70 was +1.0866 SOL total (2nd most profit!)

---

### Option C: Only Accept 60 and 90 (Aggressive)
```typescript
if (confidence === 60 || confidence >= 90) {
  // Accept - proven winners
} else {
  console.log(`   ⏭️  SKIPPED: Conf ${confidence} (only trading 60 or 90+)`);
  continue;
}
```

**Pros:**
- Only trades the two best levels
- 66.7% WR (conf 90) and 61.9% WR (conf 60)

**Cons:**
- **Way too restrictive**
- Would skip conf 70 (33.3% WR, +1.0866 SOL total = 35% of Archive Master's profit!)
- Would skip conf 45-50 (36-38% WR, still profitable)

---

## My Recommendation: Option B

**Rule:** Accept confidence 60+ but explicitly skip 80

**Why:**
1. **Captures the goldmine:** Conf 60 (61.9% WR, +1.5475 SOL)
2. **Keeps the volume:** Conf 70 was 99 trades (+1.0866 SOL = 35% of profit!)
3. **Avoids the trap:** Conf 80 (27.5% WR, -0.7465 SOL)
4. **Simple to understand:** "Trade 60+, but skip 80"

**Expected impact:**
- Conf 60: 42 trades → keep all (+1.5475 SOL) ✅
- Conf 70: 99 trades → keep all (+1.0866 SOL) ✅
- Conf 80: 40 trades → skip all (avoid -0.7465 SOL!) ✅
- Conf 90: 9 trades → keep all (+0.8116 SOL) ✅

**Total saved:** +0.7465 SOL just by skipping conf 80!

---

## Implementation

```typescript
// In paper-trade-bot.ts, after getting confidence score from smart money tracker

// Skip confidence 80 (proven loser)
if (confidence === 80) {
  console.log(`   ⏭️  SKIPPED: ${opp.symbol} (Conf 80 - historical underperformer)`);
  continue;
}

// Skip low confidence
if (confidence < 60) {
  console.log(`   ⏭️  SKIPPED: ${opp.symbol} (Conf ${confidence} < 60 threshold)`);
  continue;
}

// Accept 60-79, 81-100
console.log(`   ✅ QUALIFIED: ${opp.symbol} (Conf ${confidence})`);
```

---

## Summary

**Your question:** "Would ranking by top conf score be more profitable?"

**Answer:** **NO!** Because:
1. Conf 90 is too rare (only 9 trades)
2. Conf 80 is 2nd highest but WORST performer (-0.7465 SOL)
3. Conf 60 (lower) is actually 2nd BEST performer (+1.5475 SOL)

**Better strategy:**
- Accept 60+ (captures goldmine)
- Explicitly skip 80 (avoid trap)
- Keep 70 (33.3% WR but high volume = significant profit)
- Prioritize 90 when available (66.7% WR, rare)

---

**Created:** Feb 16, 2026
**Status:** Data-driven strategy based on 288 trades
**Next:** Implement in v2.2
