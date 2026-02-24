# Unused Fetched Data Analysis

## Summary

**These data points are fetched from DexScreener but NEVER used in any calculations:**

### 1. ✅ `priceChange5m` - 5-minute price change
**Location:** `smart-money-tracker.ts:81`
```typescript
const priceChange5m = pair.priceChange?.m5 || 0; // ← FETCHED BUT NEVER USED
```

**Impact:** Could be used to detect "too fast" pumps (>50% in 5 min)

---

### 2. ✅ `volume24h` - 24-hour volume
**Location:** `smart-money-tracker.ts:54`
```typescript
const volume24h = pair.volume?.h24 || 0; // ← FETCHED BUT NEVER USED
```

**What IS used:** Only `volume1h` (1-hour volume)

**Why it matters:** 24h volume could show sustained interest vs flash-in-pan pumps

---

### 3. ✅ `volume1h` - 1-hour volume (in meme-scanner)
**Location:** `meme-scanner.ts:125`
```typescript
const volume1h = pair.volume?.h1 || 0; // ← FETCHED BUT NEVER USED
```

**What IS used:** Only `volume24h` in the scoring (volumeRatio calculation)

**Why it matters:** Recent volume surge could indicate fresh interest

---

### 4. ✅ `priceChange24h` - 24-hour price change
**Location:** Both scanners fetch this but only use `priceChange1h`

**Why it matters:** Tokens up 1000% in 24h but down in 1h might be dumping

---

## DexScreener API Fields We're NOT Fetching At All

Based on DexScreener API docs, these are available but not fetched:

### High-Value Unused Fields

1. **`fdv` (Fully Diluted Valuation)**
   - Could filter out tokens with unrealistic FDVs

2. **`priceChange.m5`** ← WE FETCH THIS BUT DON'T USE IT!
   - 5-minute price change
   - Perfect for "too fast pump" detection

3. **`txns.m5`, `txns.h1`**
   - Recent transaction counts
   - Could detect sudden activity spikes

4. **`volume.m5`, `volume.h6`**
   - 5-minute and 6-hour volume
   - Better granularity than just 1h/24h

5. **`makers` (number of makers)**
   - Low makers = centralized/risky
   - High makers = distributed/safer

6. **`liquidity.base`, `liquidity.quote`**
   - We only use `liquidity.usd`
   - Could check if liquidity is balanced

7. **`boosts.active`**
   - Shows if token is paying for promotion
   - Promoted tokens often dump after boost ends

8. **`pairCreatedAt`**
   - ← WE FETCH THIS for age calculation
   - But could use it for "freshness score"

## Current Usage Summary

### Smart Money Tracker - What's ACTUALLY Used:
```typescript
✅ volume1h          → confidence scoring (high volume = +25 pts)
❌ volume24h         → FETCHED, NEVER USED
✅ buys/sells        → buy pressure ratio (>60% = +20 pts)
✅ priceChange1h     → momentum scoring (>50% = +25 pts)
❌ priceChange5m     → FETCHED, NEVER USED
✅ liquidity         → strength scoring (>$100k = +20 pts)
✅ marketCap         → sweet spot bonus ($50k-$1M = +10 pts)
```

### Meme Scanner - What's ACTUALLY Used:
```typescript
✅ volume24h         → volume/liquidity ratio (>1.0x = +25 pts)
❌ volume1h          → FETCHED, NEVER USED
✅ priceChange1h     → momentum bonus (>10% = +30 pts)
❌ priceChange24h    → FETCHED but only displayed, not scored
✅ liquidity         → strength bonus (>$20k = +10 pts)
✅ ageMinutes        → fresh launch bonus (<15 min = +25 pts)
```

## Potential Improvements

### 1. Use `priceChange5m` to Filter "Too Late" Entries
```typescript
// REJECT tokens that already pumped >50% in 5 minutes
if (priceChange5m > 50) {
  reasons.push(`Already pumped +${priceChange5m.toFixed(0)}% in 5m - too late`);
  confidence -= 30; // Penalty instead of reward
}
```

### 2. Use `volume24h` for Sustained Interest Check
```typescript
// Check if recent volume is fresh (1h volume should be decent % of 24h)
const volumeFreshness = volume1h / (volume24h / 24);
if (volumeFreshness > 2.0) {
  reasons.push(`Fresh volume spike: ${volumeFreshness.toFixed(1)}x hourly average`);
  confidence += 15;
}
```

### 3. Use `txns.m5` and `txns.h1` for Activity Tracking
```typescript
const recentTxns = pair.txns?.m5?.buys + pair.txns?.m5?.sells || 0;
if (recentTxns > 20) {
  reasons.push(`Active trading: ${recentTxns} txns in 5m`);
  confidence += 10;
}
```

### 4. Use `makers` to Filter Centralized Tokens
```typescript
const makers = pair.makers || 0;
if (makers < 10) {
  reasons.push(`Too centralized: only ${makers} makers`);
  confidence -= 20; // RED FLAG
}
```

### 5. Use `boosts.active` to Avoid Promoted Dumps
```typescript
if (pair.boosts?.active) {
  reasons.push(`Promoted token - may dump after boost ends`);
  confidence -= 15; // Caution
}
```

## The Big Picture

**Current Problem:**
- Bot rewards tokens that ALREADY pumped hard (>50% in 1h = +25 confidence)
- No penalty for entering late (after big pump)
- Fetches 5m data but ignores it

**This Explains Why:**
- Entering after pumps → buying tops
- Win rate is decent but P&L is negative
- Classic "buy high, sell low" pattern

**Solution Options:**

**Option A: Anti-Late-Entry Filter**
- Use `priceChange5m` to REJECT tokens up >50% in 5 min
- Prefer tokens STARTING to move, not already parabolic

**Option B: Volume Freshness**
- Prefer tokens where recent volume (1h) is NEW, not tail of 24h pump

**Option C: Transaction Activity**
- Use `txns.m5` to find tokens with FRESH activity spike

---

**Created:** Feb 16, 2026
**Version:** v2.1 analysis
**Next Step:** Decide which unused data to incorporate in v2.2
