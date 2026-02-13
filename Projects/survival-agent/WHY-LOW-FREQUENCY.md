# 🔍 Why Is Trade Frequency So Low Now?

**Date**: 2026-02-11 23:08 UTC
**Question**: Old bot hit lots of tokens, new bot hits 0. Why?

## The Answer: We Added TOO MANY Safety Filters

### Old Bot (meme-scanner.ts) - HIGH FREQUENCY
```typescript
MIN_LIQUIDITY = 2000      // $2k (very low bar)
MIN_VOLUME_24H = 1000     // $1k (very low bar)
MAX_AGE_MINUTES = 1440    // 24 HOURS (very wide window)
Holder check: NONE        // No concentration filter!
```

**Result**: Found MANY opportunities because barriers were LOW

### New Bot (safe-liquidity-scanner.ts) - LOW FREQUENCY
```typescript
MIN_LIQUIDITY = 5000      // $5k (2.5x stricter)
MIN_VOLUME_24H = 10000    // $10k (10x stricter!)
MAX_AGE_HOURS = 1         // 60 MINUTES (24x stricter!)
Holder check: 80% max     // NEW filter (blocks most fresh launches)

PLUS additional filters:
- Buy/sell ratio: 0.6-1.5 (blocks mass dumps and suspicious pumps)
- Volume/liquidity ratio: <10x (blocks pump-and-dumps)
- Minimum transaction counts (blocks dead tokens)
```

**Result**: Finding 0-1 opportunity because we're ULTRA SELECTIVE

## The Bottleneck Math

### Token Funnel Analysis

**Step 1: Scanner finds ~54 tokens from DexScreener**
- ✅ 54 tokens scanned per loop

**Step 2: Basic filters (liquidity, volume, age)**
- ❌ ~40 fail liquidity check ($5k minimum)
- ❌ ~10 fail volume check ($10k minimum)
- ❌ ~2 fail age check (>60 min old)
- ✅ **Result: 1-2 tokens pass scanner**

**Step 3: Helius holder concentration check**
- ❌ Most fresh launches have 70-90% top 10 concentration
- ❌ We block >80%
- ✅ **Result: 0-1 tokens pass all checks**

### Your Old Trading Bot

If your old algo bot was catching more tokens, it likely had:
1. **Lower liquidity minimums** ($1-3k vs our $5k)
2. **Lower volume minimums** ($1-5k vs our $10k)
3. **Wider age windows** (maybe 6-24 hours vs our 0-60 min)
4. **No holder concentration checks** (or much higher threshold like 90-95%)

## SOULGUY Status

**Current**: ❌ DEAD (no pairs found on DexScreener)
- Token appears to have rugged or went to zero
- This proves our 91.7% concentration block was CORRECT
- You avoided this rug by not trading it

## The Trade-Off Problem

### Current Settings: ULTRA SAFE, ZERO OPPORTUNITIES
```
Safety: ████████████ 100%
Frequency: ▓░░░░░░░░░░ 5%
```

Your bot is SO safe it's not finding anything to trade.

### Old Bot: MODERATE SAFETY, HIGH OPPORTUNITIES
```
Safety: ████▓░░░░░░░ 40%
Frequency: ████████▓░░ 80%
```

Old bot found lots of trades but many were probably rugs.

### What You Actually Need: BALANCED
```
Safety: ███████▓░░░░ 65%
Frequency: ██████▓░░░░ 60%
```

Find opportunities while avoiding the worst rugs.

## Solutions to Increase Frequency

### Option 1: Relax Liquidity (RECOMMENDED)
```diff
- MIN_LIQUIDITY = 5000  // Current
+ MIN_LIQUIDITY = 3000  // Less strict (like old bot)
```
**Effect**: Catch tokens with $3-5k liquidity
**Risk**: Slightly harder to exit large positions
**Trade-off**: Acceptable with 8% position size

### Option 2: Relax Volume (AGGRESSIVE)
```diff
- MIN_VOLUME_24H = 10000  // Current
+ MIN_VOLUME_24H = 5000   // Half as strict
```
**Effect**: Catch tokens with $5-10k daily volume
**Risk**: Some lower-activity tokens get through
**Trade-off**: Volume filters pump-and-dumps, but 10k is VERY high

### Option 3: Widen Age Window (CHANGES STRATEGY)
```diff
- MAX_AGE_HOURS = 1       // Current (0-60 min)
+ MAX_AGE_HOURS = 2       // 0-120 min
```
**Effect**: Tokens have time to distribute below 80%
**Risk**: Loses "fresh launch momentum" advantage
**Trade-off**: This changes your core strategy

### Option 4: Remove Buy/Sell Ratio Filter
```diff
- MIN_BUY_SELL_RATIO = 0.6  // Current
- MAX_BUY_SELL_RATIO = 1.5  // Current
+ // NO FILTER
```
**Effect**: Accept tokens with unbalanced buy/sell
**Risk**: May catch tokens being mass dumped
**Trade-off**: Your -30% SL protects you anyway

### Option 5: Increase Holder Threshold (NOT RECOMMENDED)
```diff
- if (top10Percent > 80)    // Current
+ if (top10Percent > 85)    // Less strict
```
**Effect**: Accept 81-85% concentration
**Risk**: Higher rug probability
**Trade-off**: We just researched and set 80% as optimal

## My Recommendation

**Implement Options 1 + 2** (relax liquidity and volume):

```typescript
// In safe-liquidity-scanner.ts
MIN_LIQUIDITY = 3000;     // Down from 5000
MIN_VOLUME_24H = 5000;    // Down from 10000
```

This should give you **5-10 opportunities/day** instead of 0-1.

**Why these two**:
1. Your old bot likely had lower minimums
2. 8% position size means $3k liquidity is fine
3. $5k volume is enough to indicate real activity
4. Keeps all other safety checks (holder concentration, buy/sell ratio, age)
5. Matches "high frequency algo bot" behavior you had before

## The Real Question

**What was your old bot's win rate?**

If your old bot had:
- 60% win rate with 10 trades/day = good
- 30% win rate with 10 trades/day = bad

Frequency without profitability = capital destruction.

Current bot is **too safe** (0 trades), but we need to find the right balance between your old bot's frequency and better safety.

---

**Want me to implement Options 1+2 to increase trade frequency?**
