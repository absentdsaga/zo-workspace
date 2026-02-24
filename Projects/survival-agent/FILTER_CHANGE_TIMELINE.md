# Filter Change Timeline: When You Changed to $500k Volume

## 📅 Timeline

### **February 16, 2026 @ 12:26 PM EST (17:26 UTC)**

You changed the filters from Archive Master's loose settings to strict settings:

| Filter | Before | After | Change |
|--------|--------|-------|--------|
| **MIN_LIQUIDITY** | $2,000 | $10,000 | **5x increase** |
| **MIN_VOLUME_24H** | $1,000 | $500,000 | **500x increase** |
| **Age Filter** | Broken (let old tokens through) | Disabled (no filter) | Same as Archive Master |

**File modified:** `strategies/meme-scanner.ts`
**Time:** 12:26:07 PM EST (17:26:07 UTC)

---

## 📊 Why You Changed It

### The Data Analysis (from CRITICAL_FILTER_UPGRADE.md)

Based on 180 closed trades, you discovered:

**Liquidity Tiers:**
- **$2k-$10k liquidity:** 22% win rate (19W / 69L) ❌ **78% loss rate**
- **$10k+ liquidity:** 47% win rate (40W / 45L) ✅

**Volume Tiers:**
- **$1k-$500k volume:** 26% win rate (25W / 70L) ❌
- **$500k+ volume:** 44% win rate (37W / 48L) ✅

### The Problem

**Archive Master's loose filters ($2k/$1k) were bleeding losses:**
- 49% of trades (88/180) were in the $2k-$10k liquidity range
- Of those 88 trades, **78% were losers** (69 losses)
- This tier was responsible for MOST of the -70% loss

### The Solution

**Raise filters to where winners cluster:**
- MIN_LIQUIDITY: $2k → $10k (5x)
- MIN_VOLUME_24H: $1k → $500k (500x)

**Expected Impact:**
- Block 69 losing trades
- Keep 40 winning trades
- Win rate: 34.6% → 47% (2x improvement)
- Should flip from -70% loss to profitable

---

## 🎯 Current Status

### Your Current Settings (as of 12:26 PM today):
```typescript
// strategies/meme-scanner.ts
private readonly MIN_LIQUIDITY = 10000;   // $10k
private readonly MIN_VOLUME_24H = 500000; // $500k
```

### Bot Restarted:
- **Time:** 12:26 PM EST (same as filter change)
- **Process:** PID 13653 (per FILTERS_UPGRADED.md)
- **Status:** Running with strict filters

---

## 📈 Git History Context

### Last Git Commit: Feb 14, 2026
```
4c9cc2a - Paper Trading Bot v2.0 - Live P&L tracking + Shocked integration
```

**Settings in git (last committed):**
- MIN_LIQUIDITY: $2k
- MIN_VOLUME_24H: $1k
- Age filter: BROKEN

**Current working copy (modified today at 12:26 PM):**
- MIN_LIQUIDITY: $10k ✅
- MIN_VOLUME_24H: $500k ✅
- Age filter: DISABLED (same as Archive Master) ✅

**Status:** Changes are NOT committed to git yet

---

## 🔍 The Archive Master Mystery

### What We Discovered:

**Archive Master (626% profit) used:**
- MIN_LIQUIDITY: $2k
- MIN_VOLUME_24H: $1k
- Age filter: BROKEN (let everything through, including undefined ages)
- Result: 295 trades, 38.9% win rate, +626%

**But our analysis of 180 trades showed:**
- Same $2k/$1k filters
- 34.6% win rate (similar to Archive)
- **-70% loss** (opposite of Archive!)

### The Key Difference:

**Archive Master had additional quality controls we didn't know about:**
1. Simple sources (no shocked/subagent complexity)
2. Different market conditions
3. Some unknown filter or behavior

**Your hypothesis:** The $2k/$1k filters were too loose and needed tightening based on YOUR loss data (not Archive's).

---

## 🤔 The $500k Question

### Is $500k Volume TOO Strict?

**Consider:**
- Archive Master won +626% with **$1k volume**
- You changed to **$500k volume** (500x stricter!)
- This might filter out 99% of opportunities

**Comparison:**
| Setting | Archive Master | Your Current | Ratio |
|---------|---------------|--------------|-------|
| MIN_LIQUIDITY | $2k | $10k | 5x |
| MIN_VOLUME | $1k | $500k | **500x** |

**The liquidity change (5x) is reasonable.**
**The volume change (500x) is EXTREME.**

### Alternative Thresholds to Consider:

**Option A: Moderate Tightening**
- MIN_LIQUIDITY: $10k (keep)
- MIN_VOLUME_24H: $50k (50x vs Archive, not 500x)

**Option B: Match Winners Cluster**
- MIN_LIQUIDITY: $10k (keep)
- MIN_VOLUME_24H: $100k (100x vs Archive)

**Option C: Current (Strictest)**
- MIN_LIQUIDITY: $10k (keep)
- MIN_VOLUME_24H: $500k (current)

---

## 📉 Expected Trade Volume Impact

### Archive Master (626% profit):
- 295 trades over unknown period
- Loose filters ($2k/$1k)
- High opportunity volume

### Your Current Filters ($10k/$500k):
- **Expected:** FAR fewer trades (maybe 10-20x less)
- **Why:** $500k volume is rare for meme coins
- **Risk:** Miss early pumps (fresh tokens have low volume)

### Example:
A fresh 10-minute-old token might have:
- ✅ $15k liquidity (passes $10k threshold)
- ❌ $5k volume (fails $500k threshold)
- **Result:** Filtered out despite being fresh/quality

**$500k volume typically means:**
- Token is 6-24 hours old (established)
- Already pumped significantly
- We're entering late

---

## 🎯 Recommendations

### 1. Test Current Settings ($10k/$500k) for 24 Hours
**Monitor:**
- Opportunity volume (trades/hour)
- Win rate vs target (47%)
- Whether ANY trades execute

**If too few opportunities:**
- Lower volume to $100k or $50k
- Keep liquidity at $10k

### 2. Consider Gradual Tightening
Instead of 500x jump, try:
- Day 1: $10k liq / $50k vol (test)
- Day 2: $10k liq / $100k vol (test)
- Day 3: $10k liq / $500k vol (if needed)

### 3. Track by Tier
Log which tier each trade falls into:
- **Tier 1:** $10k+ liq, $500k+ vol
- **Tier 2:** $10k+ liq, $100k-$500k vol
- **Tier 3:** $10k+ liq, $50k-$100k vol

Compare win rates to find optimal balance.

---

## 🔬 The Real Test

**Question:** Does $10k/$500k actually improve results?

**We won't know until you run it for 50-100 trades.**

**Possible outcomes:**

1. **Best case:** 45-50% win rate, profitable, perfect balance
2. **Good case:** Fewer trades but higher quality, net positive
3. **Bad case:** TOO restrictive, miss all opportunities, no trades
4. **Worst case:** Still loses despite tighter filters (wrong hypothesis)

---

## 📝 Summary

- **When:** Today (Feb 16) at 12:26 PM EST
- **What:** Changed MIN_LIQUIDITY $2k→$10k, MIN_VOLUME $1k→$500k
- **Why:** Your data showed 78% loss rate in low-liquidity tokens
- **Status:** Running now, not yet committed to git
- **Risk:** $500k volume might be TOO strict (500x vs Archive Master)
- **Next:** Monitor for 24-48 hours, adjust if needed

**The key insight:** Archive Master's loose filters worked for them (+626%), but failed for you (-70%). You're betting that tighter filters will help. Time will tell if $500k volume is the sweet spot or overkill.
