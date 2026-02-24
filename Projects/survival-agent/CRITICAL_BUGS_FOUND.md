# 🚨 CRITICAL BUGS FOUND

## Bug #1: Age Filter Broken - Trading Old/Unknown Tokens

### Location
`strategies/meme-scanner.ts` line 116

### The Bug
```typescript
// CURRENT (BROKEN):
if (ageMinutes < 999 && ageMinutes > 1440) {
  continue; // Skip tokens older than 24 hours
}
```

**This logic is BACKWARDS!**

### What It Does (Wrong)
- Only skips tokens if age is KNOWN (`< 999`) AND OLDER than 24h (`> 1440`)
- If age is UNKNOWN (`= 999`), it passes through ✅ (should be rejected ❌)
- Tokens with unknown age get scored as if they're valid

### Evidence
Recent scanner output shows tokens being analyzed that are:
- Manchas: **6,095 minutes old** (4.2 days) ❌
- CIA: **7,518 minutes old** (5.2 days) ❌
- しずく: **8,960 minutes old** (6.2 days) ❌
- LAMB: **3,085 minutes old** (2.1 days) ❌

These are FAR beyond the 24-hour (1,440 min) threshold!

### Why This Happens
1. DexScreener API sometimes returns tokens without `pairCreatedAt`
2. Code sets `ageMinutes = 999` for unknown age
3. Broken filter logic: `999 < 999` = FALSE, so condition fails
4. Token passes through with age = 999
5. Token scores 75+ points and gets traded

### Impact
**HIGH - Trading stale tokens instead of fresh opportunities**
- Fresh tokens (<60 min) are the target
- Actually trading tokens that are 2-6 days old
- Old tokens have already pumped and dumped
- This explains poor entry timing and losses

### The Fix
```typescript
// CORRECT:
if (ageMinutes > 1440) {
  continue; // Skip tokens older than 24 hours OR unknown age
}

// Alternative (stricter):
if (ageMinutes >= 999 || ageMinutes > 1440) {
  continue; // Explicitly reject unknown age AND old tokens
}
```

---

## Bug #2: Scoring Rewards Old Tokens

### Location
`strategies/meme-scanner.ts` lines 172-226

### The Bug
Tokens can score 75+ points WITHOUT the fresh launch bonus!

**Scoring breakdown:**
- Volume spike: 25 points (if volume/liquidity > 1.0x)
- Price momentum: 30 points (if +10% in 1h)
- Strong liquidity: 10 points (if >$10k)
- **Fresh launch: 25 points** (only if <15 min) ← OLD TOKENS DON'T GET THIS
- MC sweet spot: 10 points (if $20k-$1M)

**Total possible without fresh bonus: 75 points**

### The Problem
- MIN_SCORE = 40
- Old tokens can easily hit 75 points from volume/momentum/liquidity alone
- Fresh launch bonus (+25 points) is NOT required to pass
- Scanner prefers OLD tokens with volume over FRESH tokens

### Example
4-day-old token scores 75:
```
Volume spike: +25 (high volume)
Price momentum: +30 (pumping)
Liquidity: +10 ($15k)
Fresh bonus: +0 (too old) ← IGNORED!
MC sweet spot: +10 ($50k)
───────────────────────
TOTAL: 75 ✅ Passes!
```

### Impact
**HIGH - Wrong token selection priority**
- Prefers old tokens with current momentum
- Ignores fresh tokens that lack volume history
- Entry timing is terrible (late to the party)

### The Fix Options

**Option 1: Make fresh bonus REQUIRED**
```typescript
// Reject if not fresh
if (ageMinutes >= 60) {
  return; // Don't even score old tokens
}
```

**Option 2: Age penalty for old tokens**
```typescript
// Penalize old tokens heavily
if (ageMinutes > 60) {
  score -= 50; // Massive penalty
} else if (ageMinutes > 15) {
  score -= 25; // Moderate penalty
}
```

**Option 3: Require minimum age score**
```typescript
// Fresh bonus is mandatory, not optional
if (ageMinutes >= 15) {
  continue; // Skip in scanner, don't add to results
}
```

---

## Bug #3: Unknown Age Tokens Bypass All Checks

### Location
`strategies/meme-scanner.ts` line 109

### The Bug
```typescript
let ageMinutes = 999; // Unknown age
```

Setting unknown age to 999 means:
1. ✅ Passes age filter (Bug #1)
2. ✅ Scores high without fresh bonus (Bug #2)
3. ✅ No warning to user that age is unknown

### The Fix
```typescript
// REJECT tokens with unknown age
if (!pair.pairCreatedAt) {
  continue; // Skip tokens without creation timestamp
}
```

**Rationale:** If DexScreener doesn't have the creation time, the token is likely:
- Too old (pre-dates DexScreener tracking)
- Suspicious/incomplete data
- Not worth trading

---

## Summary of Impact

### Current Behavior (BROKEN)
1. Scanner finds 10 "opportunities"
2. Most are 2-6 DAYS old
3. All score 75+ (high volume, momentum, liquidity)
4. Bot tries to enter these stale pumps
5. Smart money filter rejects them (confidence 10-30)
6. Bot cycles through 5 stale tokens, finds nothing
7. No trades executed OR enters at terrible timing

### Expected Behavior (FIXED)
1. Scanner filters for <60 minute old tokens
2. Rejects tokens with unknown age
3. Fresh tokens score high (with fresh bonus)
4. Bot enters early in the pump
5. Better timing = better exits = profitability

---

## Recommended Fix Priority

### CRITICAL (Fix Immediately)
1. **Fix age filter** - Line 116 in meme-scanner.ts
2. **Reject unknown age** - Skip tokens without pairCreatedAt

### HIGH (Fix Soon)
3. **Require fresh bonus** - Make age <60 min mandatory

### MEDIUM (Test & Tune)
4. **Adjust scoring weights** - Test if fresh tokens score high enough

---

## Code Changes Needed

### File: `strategies/meme-scanner.ts`

**Change 1 (Line 109-118):**
```typescript
// BEFORE:
let ageMinutes = 999; // Unknown age
if (pair.pairCreatedAt) {
  const ageMs = Date.now() - pair.pairCreatedAt;
  ageMinutes = ageMs / 1000 / 60;
}

if (ageMinutes < 999 && ageMinutes > 1440) {
  continue;
}

// AFTER:
if (!pair.pairCreatedAt) {
  continue; // Skip tokens without creation timestamp
}

const ageMs = Date.now() - pair.pairCreatedAt;
const ageMinutes = ageMs / 1000 / 60;

if (ageMinutes > 1440) {
  continue; // Skip tokens older than 24 hours
}
```

**Change 2 (Line 115 - add fresh requirement):**
```typescript
// Add after age calculation:
if (ageMinutes > 60) {
  continue; // Only trade tokens <60 min old
}
```

This will ensure ONLY fresh tokens (<60 min) with known age are considered.
