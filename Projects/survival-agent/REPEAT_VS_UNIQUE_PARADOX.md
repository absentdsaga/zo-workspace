# The Repeat vs Unique Token Paradox

**Date:** Feb 16, 2026
**Discovery:** Profit source COMPLETELY REVERSED between Archive Master and current run

---

## The Shocking Finding

### Archive Master (626% profit)
✅ **REPEAT tokens were the goldmine:**
- Repeat tokens: **+3.3154 SOL (106% of profit!)**
- Unique tokens: -0.1865 SOL (lost money)
- **Difference: +3.50 SOL advantage for repeats**

**Top repeat winners:**
1. **OrbEye**: 10x trades (6W/4L) +0.7749 SOL
2. **HALF**: 10x trades (6W/4L) +0.4777 SOL
3. **LEO**: 3x trades (1W/2L) +0.4772 SOL
4. **TRUMP2**: 5x trades (5W/0L) +0.2714 SOL (!!!)

### Current v2.1 (losing money)
❌ **REPEAT tokens are destroying P&L:**
- Repeat tokens: **-0.0572 SOL (113.7% of losses!)**
- Unique tokens: +0.0069 SOL (slight profit)
- **Difference: +0.0641 SOL advantage for unique**

**Repeat losers:**
1. **‎ (nameless)**: 3x trades (0W/3L) -0.0722 SOL ← BLACKLISTED
2. **‎ (CvVncV...)**: 5x trades (1W/4L) -0.0078 SOL ← NOW BLACKLISTED
3. **Mochi**: 2x trades (1W/1L) +0.0196 SOL (okay)
4. **MOG**: 2x trades (1W/1L) +0.0032 SOL (okay)

---

## Deep Dive: Archive Master's Repeat Token Magic

### The Pattern: Find a Winner, Milk It

**OrbEye (10 trades, +0.7749 SOL):**
- Win Rate: 60%
- 6 wins, 4 losses
- Avg P&L: +0.0775 SOL per trade
- **Strategy:** Kept trading it because it was profitable

**HALF (10 trades, +0.4777 SOL):**
- Win Rate: 60%
- 6 wins, 4 losses
- Avg P&L: +0.0478 SOL per trade
- **Same pattern as OrbEye**

**TRUMP2 (5 trades, +0.2714 SOL):**
- Win Rate: **100%** (5W/0L!)
- Avg P&L: +0.0543 SOL per trade
- **Perfect record on repeat trades**

**LEO (3 trades, +0.4772 SOL):**
- Win Rate: 33.3% (1W/2L)
- **Still profitable despite only 1 win!**
- That 1 win was MASSIVE

### The Stats

**Archive Master - Repeat Tokens:**
- 59 tokens traded 2+ times
- 260 total trades from repeats
- 40.4% win rate
- **+3.3154 SOL profit**
- **106% of total profit came from repeats!**

**Archive Master - Unique Tokens:**
- 28 tokens traded once
- 28 total trades
- 25.0% win rate
- **-0.1865 SOL loss**

---

## Why Are Current Repeats Losing?

### Current v2.1 - Repeat Token Breakdown

**The Nameless Token (3vgJGbBD...):**
- 3 trades, 0 wins, 3 losses
- -0.0722 SOL
- All confidence 60
- **NOW BLACKLISTED** ✅

**The Other Nameless Token (CvVncV...):**
- 5 trades, 1 win, 4 losses
- -0.0078 SOL
- Mixed confidence (50, 70, 70, 70, 70)
- **NOW BLACKLISTED** ✅

**Why these failed:**
1. **No symbol visibility** - Can't track/recognize them easily
2. **Low quality tokens** - Confidence 50-70 (Archive Master's goldmine was 60)
3. **Bad luck** - Small sample size (5 trades vs 10+ in Archive Master)

**Why Mochi/MOG succeeded on repeats:**
- Both went 1W/1L (break even territory)
- Higher confidence (80)
- Real symbols (trackable)

---

## The Key Difference

### Archive Master's Strategy (Implicit)
1. Trade token
2. If it wins → **trade it again** (and again, and again)
3. If it loses → still might trade again
4. Keep trading until **10+ trades** on best performers
5. **Milk the winners**

**Result:** +3.3154 SOL from repeats (106% of profit)

### Current v2.1's Problem
1. Trade token
2. If it loses → **trade it again anyway** (no filter!)
3. Lose again → **trade AGAIN** (still no filter!)
4. Lose a 3rd time → **FINALLY blacklist**
5. **Can't find winners to milk**

**Result:** -0.0572 SOL from repeats (113.7% of losses)

---

## What Changed?

### Theory 1: Token Quality
- **Archive Master:** Found good tokens worth repeating (OrbEye, HALF, TRUMP2)
- **Current v2.1:** Finding bad tokens (nameless junk)

### Theory 2: Repeat Filter Missing
- **Archive Master:** May have had implicit "skip recent losers" logic?
- **Current v2.1:** No filter until 3 losses (lets bad tokens drain capital)

### Theory 3: Market Conditions
- **Archive Master:** Feb 15 had better tokens/conditions
- **Current v2.1:** Feb 16 is a different market

### Theory 4: Sample Size
- **Archive Master:** 260 repeat trades (large sample)
- **Current v2.1:** 12 repeat trades (tiny sample, could be noise)

---

## The Paradox Explained

**Archive Master's secret sauce:**
1. **Find winners** (OrbEye, HALF, LEO, TRUMP2, etc.)
2. **Trade them repeatedly** (10x, 5x, 3x)
3. **High win rate on repeats** (40.4% overall, 60% on best tokens)
4. **Result:** Massive profit from repeating good tokens

**Current v2.1's problem:**
1. **Find losers** (nameless tokens)
2. **Trade them repeatedly** (3-5x before blacklist)
3. **Low win rate on repeats** (25% overall)
4. **Result:** Massive loss from repeating bad tokens

---

## Key Insight: It's Not About Repeats, It's About Quality

**The real difference:**
- Archive Master repeated **GOOD** tokens (OrbEye 60% WR, TRUMP2 100% WR)
- Current v2.1 repeats **BAD** tokens (CvVncV 20% WR, 3vgJGbBD 0% WR)

**Repeating is GOOD if:**
- ✅ Token has proven itself (1st trade won or broke even)
- ✅ Token has real symbol/name (trackable)
- ✅ Confidence stays high on repeat scans

**Repeating is BAD if:**
- ❌ Token lost on 1st trade
- ❌ Token is nameless/sketchy
- ❌ Confidence was low on entry

---

## Solutions

### Option A: "Skip Previous Losers" Filter (Conservative)
```typescript
// Don't trade tokens that previously lost
const previouslyLost = this.trades.some(t =>
  t.tokenAddress === opp.address &&
  t.status === 'closed_loss'
);

if (previouslyLost) {
  continue; // Skip - already lost once
}
```

**Pros:**
- Prevents repeat losses
- Saved ~0.06 SOL in current run

**Cons:**
- Would have prevented Archive Master's LEO (3x, 1W/2L, +0.4772 SOL!)
- Blocks comeback opportunities

---

### Option B: "Skip Consecutive Losers" Filter (Current: 3-Loss Blacklist)
```typescript
// Already implemented - blacklist after 3 consecutive losses
```

**Pros:**
- Working as intended (blacklisted bad tokens)
- Allows tokens to prove themselves (3 chances)

**Cons:**
- Still wastes 2 trades on proven losers (trades 2 and 3)

---

### Option C: "Prioritize Previous Winners" (Archive Master's Secret?)
```typescript
// Boost confidence for tokens that won before
const previouslyWon = this.trades.some(t =>
  t.tokenAddress === opp.address &&
  t.status === 'closed_profit'
);

if (previouslyWon) {
  confidence += 20; // Boost confidence for known winners
}
```

**Pros:**
- Encourages repeat trades on winners (like Archive Master)
- Mimics "milk the winners" strategy

**Cons:**
- May over-trade cooling tokens

---

### Option D: "Track Token Success Rate"
```typescript
// Calculate historical win rate for this token
const tokenTrades = this.trades.filter(t => t.tokenAddress === opp.address);
const tokenWins = tokenTrades.filter(t => t.status === 'closed_profit').length;
const tokenWR = tokenWins / tokenTrades.length;

if (tokenWR < 0.3) {
  continue; // Skip tokens with <30% historical win rate
}
```

**Pros:**
- Data-driven decision
- Would have blocked CvVncV (20% WR) after trade 2

**Cons:**
- Small sample size issues (1 loss = 0% WR)

---

## Recommendations for v2.2

**Implement Option A: Skip Previous Losers**

Why:
1. **Current run:** Unique tokens are profitable (+0.0069), repeats are not (-0.0572)
2. **Archive Master:** Had larger sample size, current run is too small to trust repeat pattern
3. **3-loss blacklist already working** - but preventing 1st repeat loss is better
4. **LEO exception:** That was 1 outlier in 288 trades, not worth optimizing for

**Expected impact:**
- Would have prevented: CvVncV trades 2-5 (-0.0402 SOL saved)
- Would have prevented: 3vgJGbBD trades 2-3 (-0.0464 SOL saved)
- **Total saved: ~0.09 SOL** on this run alone

---

**Created:** Feb 16, 2026
**Status:** Critical discovery - repeat strategy works ONLY if you find winners
**Next:** Implement "skip previous losers" filter in v2.2
