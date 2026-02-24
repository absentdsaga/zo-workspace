# Archive Master Secrets Revealed - What We're NOT Copying

**Date:** Feb 16, 2026
**Finding:** Major differences between Archive Master (626% profit) and current v2.1 (losing)

---

## What We THOUGHT Archive Master Did

❌ **WRONG:** "Skip previous losers" filter
❌ **WRONG:** Priority queue for winners
❌ **WRONG:** Min confidence 70+
❌ **WRONG:** 12% position size

---

## What Archive Master ACTUALLY Did

### 1. RE-TRADED LOSERS (No "Skip Previous Losers" Filter!)

**Data:**
- Re-traded after LOSS: **113 times**
- Comeback win rate: **30.1%** (34 wins, 79 losses)
- Some tokens lost multiple times before winning

**Example sequences:**
- JUICE: W → W → L → W → W → L → W → L → L → L → L → L → L (5W/8L but +0.28 SOL!)
- OrbEye: W → W → W → W → W → L → W → L → L → L (6W/4L, +0.77 SOL!)
- Approval: L → L → W → W → L → L → L → L (2W/6L, lost money)

**Key insight:** Archive Master gave tokens MULTIPLE chances, not just one!

---

### 2. MUCH LARGER POSITION SIZE

**Archive Master:**
- Average position: **0.1025 SOL** per trade
- Effective %: **20.5%** of 0.5 SOL balance
- This means: 4-5 max concurrent positions (not 7!)

**Current v2.1:**
- Average position: **0.06 SOL** per trade
- Effective %: **12%** of balance
- Max concurrent: 7 positions

**Difference:** Archive Master used **71% LARGER positions** (0.1025 vs 0.06)!

**Impact:**
- Bigger wins when right
- Bigger losses when wrong
- Fewer concurrent positions (capital constraint)
- More selective (can't trade everything)

---

### 3. TRAILING STOPS WORKED!

**Exit breakdown:**
- **170 trades (59%):** Stop loss -30%
- **48 trades (17%):** Max hold time (60 min)
- **70 trades (24%):** Trailing stop (after hitting TP1 +100%)

**24% of trades hit TP1** and used trailing stops!

**Current v2.1:**
- Only 1 trade hit TP1 so far (out of 17 = 6%)

**Why the difference?**
- Larger positions = more capital to move price?
- Different market conditions?
- Better token selection?

---

### 4. CONFIDENCE DISTRIBUTION

**Archive Master traded EVERYTHING:**
```
Conf 90:   9 trades (  3.1%) ← Rare
Conf 80:  40 trades ( 13.9%) ← WORST performer, still traded!
Conf 70:  99 trades ( 34.4%) ← MOST trades
Conf 60:  42 trades ( 14.6%) ← BEST performer
Conf 55:   9 trades (  3.1%)
Conf 50:  31 trades ( 10.8%)
Conf 45:  57 trades ( 19.8%) ← MIN threshold
```

**Current v2.1 plan:** Min 60, skip 80
**Archive Master reality:** Min 45, traded everything including 80!

**Why did conf 80 lose money but Archive Master still traded it?**
- Because conf 70 (34% of trades) was profitable overall
- And conf 60 (15% of trades) was VERY profitable
- The losses from conf 80 were acceptable in the bigger picture

---

### 5. AVERAGE HOLD TIME: 21 MINUTES

**Archive Master:**
- Average hold: **21 minutes**
- Max hold: 62 minutes (close to 60 min limit)
- Min hold: 0 minutes (instant rug/exit)

**Current v2.1:**
- Similar max hold time (60 min)
- But fewer trades hitting trailing stops = more hitting max time?

---

### 6. SCANNER SOURCE: DexScreener Dominated

**Archive Master:**
- DexScreener: **77.1%** (222 trades)
- Both: 21.2% (61 trades)
- PumpFun: 1.7% (5 trades)

**Current v2.1:**
- Likely similar distribution
- DexScreener is primary source

---

## The Biggest Secrets We're Missing

### 🔥 SECRET #1: Much Larger Positions (20.5% vs 12%)

**Archive Master:** 0.1025 SOL per trade
**Current v2.1:** 0.06 SOL per trade
**Difference:** 71% larger!

**Why this matters:**
- Bigger wins compensate for losses
- Caps max concurrent positions naturally (4-5 instead of 7)
- More selective by necessity
- Higher risk, higher reward

**RECOMMENDATION:** Raise position size from 12% → 20%

---

### 🔥 SECRET #2: No "Skip Previous Losers" Filter

**Archive Master:** Re-traded losers 113 times
- Comeback win rate: 30.1%
- Some big winners had early losses (JUICE, OrbEye)

**Current v2.1 plan:** Skip previous losers entirely

**Why Archive Master's approach worked:**
- Tokens can pump after dumping (second wave)
- 30% comeback rate is decent
- LEO example: L → L → W (massive win on trade 3)

**RECOMMENDATION:** Don't skip previous losers - give them 2nd chance!

---

### 🔥 SECRET #3: Traded ALL Confidence Levels (45-90)

**Archive Master:** Min confidence 45
- Even traded conf 80 (worst performer) 40 times
- Took losses but overall portfolio was profitable

**Current v2.1 plan:** Min 60, skip 80

**Why Archive Master's approach worked:**
- Volume matters: Conf 70 was 34% of all trades
- Diversification: Different conf levels = different risk profiles
- Acceptable losses: Conf 80 lost -0.75 SOL but conf 60/70 made +2.6 SOL

**RECOMMENDATION:** Lower min confidence back to 50 (not 60)

---

### 🔥 SECRET #4: 24% of Trades Hit TP1 (Trailing Stops)

**Archive Master:** 70 trades hit +100% TP1
- These used trailing stops (20% from peak)
- Generated massive profits

**Current v2.1:** Only 6% hitting TP1 so far

**Why the difference?**
- Larger positions = more momentum?
- Better timing (21 min avg hold)?
- Different market conditions?
- Token selection (conf 60 goldmine)?

**Need to investigate:** Why aren't we hitting TP1 as often?

---

## Strategy Adjustments for v2.2

### Option A: Full Archive Master Clone
```typescript
// 1. LARGER POSITIONS
POSITION_SIZE_PERCENT = 0.20; // Up from 0.12 (71% increase!)

// 2. NO "SKIP PREVIOUS LOSERS" FILTER
// Remove this - give tokens 2nd/3rd chances

// 3. LOWER MIN CONFIDENCE
MIN_SMART_MONEY_CONFIDENCE = 50; // Down from 60

// 4. DON'T SKIP CONF 80
// Archive Master traded it despite losses

// 5. KEEP 3-LOSS BLACKLIST
// This prevents 4+ consecutive losses (still useful)
```

**Expected result:** Closer to Archive Master's 626% profit

**Risk:** Higher volatility (20% positions = bigger swings)

---

### Option B: Hybrid (Safer)
```typescript
// 1. MEDIUM POSITIONS
POSITION_SIZE_PERCENT = 0.15; // Up from 0.12, but not full 0.20

// 2. ALLOW 1 COMEBACK TRADE
// Skip losers only after 2 consecutive losses (not 1)

// 3. MIN CONFIDENCE 55
MIN_SMART_MONEY_CONFIDENCE = 55; // Compromise

// 4. SKIP CONF 80 (Keep our filter)
// We know it's bad, avoid it

// 5. KEEP 3-LOSS BLACKLIST
```

**Expected result:** Better than current, safer than full clone

---

### Option C: Conservative (Test Waters)
```typescript
// 1. SLIGHTLY LARGER POSITIONS
POSITION_SIZE_PERCENT = 0.12; // Keep current, OR raise to 0.15

// 2. REMOVE "SKIP PREVIOUS LOSERS" FILTER
// Match Archive Master's approach

// 3. LOWER MIN CONFIDENCE
MIN_SMART_MONEY_CONFIDENCE = 50; // Match Archive Master

// 4. KEEP SKIP CONF 80
// We have data showing it's bad

// 5. REDUCE MAX POSITIONS TO 5
MAX_CONCURRENT_POSITIONS = 5; // Forces selectivity
```

---

## The Paradox

**Archive Master:**
- Traded conf 80 (lost -0.75 SOL)
- Re-traded losers 113 times (30% comeback rate)
- Used min conf 45 (not selective)
- **Still made 626% profit!**

**How?**
1. **Volume + large positions:** 20.5% positions × 288 trades = massive exposure to winners
2. **Diversification:** Conf 60 goldmine compensated for conf 80 losses
3. **Patience with tokens:** Gave multiple chances (OrbEye, JUICE, HALF)
4. **Trailing stops:** 24% hit TP1, captured huge gains

**Current v2.1:**
- Smaller positions (12% vs 20.5%)
- Fewer trades (17 vs 288)
- More selective (plan to skip 80, skip losers)
- **Losing money**

---

## Recommendation: Start with Option A (Full Clone)

**Why:**
1. We have 288 trades of data proving it works
2. Our "improvements" are making it worse (12% positions, skip losers, min 60)
3. The paradox is real: being LESS selective worked better

**Changes to implement:**
```typescript
// v2.2 - Full Archive Master Clone

POSITION_SIZE_PERCENT = 0.20;           // 71% larger positions!
MIN_SMART_MONEY_CONFIDENCE = 45;        // Match Archive Master
MAX_CONCURRENT_POSITIONS = 5;           // Natural limit from larger positions

// REMOVE these planned filters:
// ❌ Skip confidence 80 (Archive Master traded it)
// ❌ Skip previous losers (Archive Master gave 2nd chances)
// ❌ Min confidence 60 (Archive Master used 45)

// KEEP these:
// ✅ 3-loss blacklist (prevents 4+ consecutive losses)
// ✅ Skip nameless tokens (both our blacklisted tokens were nameless)
// ✅ Trailing stops (Archive Master used them on 24% of trades)
```

**Expected impact:**
- Larger wins when right (+71% bigger)
- Larger losses when wrong (-71% bigger)
- Fewer concurrent positions (4-5 instead of 7)
- Higher total P&L (if Archive Master pattern holds)

---

**Created:** Feb 16, 2026
**Status:** Major discovery - we were over-engineering!
**Next:** Implement v2.2 as full Archive Master clone
