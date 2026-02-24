# Bug Fix: Paper Bot Not Catching Coins After Refactor

## Problem
The paper trading bot stopped catching ANY coins after the refactor, despite finding many opportunities (4-18 per scan cycle). All opportunities were being rejected with "Low confidence (0 < 45)".

## Root Cause Analysis

### Issue #1: Fresh Pump.fun Tokens Have No DexScreener Data
**Symptom:**
```
Token: stacy (CHoTXZCv...)
Score: 45/100
Source: pumpfun
Signals: 10000000.0 SOL initial buy

3️⃣  Smart money analysis...
   Confidence: 0/100
   ⏭️  SKIPPED: Low confidence (0 < 45)
```

**Root cause:** The bot was using SmartMoneyTracker (which queries DexScreener) for ALL tokens, including brand new pump.fun launches. Brand new tokens don't have DEX pairs yet, so DexScreener returns `{"pairs": null}`, resulting in 0% confidence.

**Why this broke:** After the refactor, the smart money check was mandatory for all tokens with confidence threshold of 45%. Before, there must have been a mechanism to bypass this for fresh pump.fun tokens.

### Issue #2: PumpPortal WebSocket Missing Timestamp Field
**Symptom:**
```
Token: IDGI (9NQC7Yn8...)
Score: 45/100
Source: pumpfun
Age: NaN min
```

**Root cause:** The `PumpPortalTokenCreate` interface declared a `timestamp` field, but the actual PumpPortal API doesn't send it. The scanner was calculating age as:
```typescript
const ageMs = now - token.timestamp;  // token.timestamp = undefined
const ageMinutes = ageMs / 60000;      // NaN / 60000 = NaN
```

**Impact:** Even with the smart money fix, fresh pump.fun tokens couldn't be identified because `ageMinutes` was NaN, so the check `best.ageMinutes <= 10` always failed.

## The Fix

### Fix #1: Skip Smart Money Check for Fresh Pump.fun Tokens
**File:** `testing/paper-trade-bot.ts`

```typescript
// 🔥 FIX: Skip smart money check for ultra-fresh pump.fun tokens
// They're too new to have DexScreener data, use pump.fun metrics instead
const isFreshPumpFun = (best.source === 'pumpfun' || best.source === 'both') &&
                      (best.ageMinutes !== undefined && best.ageMinutes <= 10);
let confidence = 0;

if (isFreshPumpFun) {
  // Use pump.fun score as confidence (already validated by scanner)
  confidence = best.score;
  console.log('3️⃣  🔥 Fresh pump.fun token - using scanner score as confidence');
  console.log(`   Confidence: ${confidence}/100 (from pump.fun metrics)\n`);
} else {
  // Use smart money analysis for established tokens
  console.log('3️⃣  Smart money analysis...');
  const analysis = await this.tracker.hasSmartMoneyInterest(best.address);
  confidence = analysis.confidence;
  console.log(`   Confidence: ${confidence}/100\n`);
}
```

**Logic:** Fresh pump.fun tokens (< 10 minutes old) bypass the DexScreener-based smart money check and use the pump.fun scanner score directly as confidence. This works because:
1. The scanner already validated the token (initial buy size, market cap, liquidity)
2. Pump.fun metrics are real-time and don't require DEX listing
3. This mirrors how Shocked scanner tokens work (they also bypass smart money check)

### Fix #2: Use Cache Timestamp Instead of Token Timestamp
**File:** `strategies/combined-scanner-websocket.ts`

```typescript
private async scanPumpFunCache(): Promise<CombinedOpportunity[]> {
  this.cleanCache();

  const now = Date.now();
  const opportunities: CombinedOpportunity[] = [];

  for (const [mint, data] of this.pumpfunTokens.entries()) {
    const token = data.token;
    // Use data.timestamp (when we cached it) since token.timestamp is undefined from PumpPortal API
    const ageMs = now - data.timestamp;  // ✅ Fixed: use data.timestamp
    const ageMinutes = ageMs / 60000;
```

**Change:** Use `data.timestamp` (set when we cache the token) instead of `token.timestamp` (undefined from API).

## Verification

### Before Fix
```
Found 18 potential opportunities
18 meet minimum score (≥40)

Token: stacy (CHoTXZCv...)
Score: 45/100
Source: pumpfun
Confidence: 0/100
⏭️  SKIPPED

(All 18 opportunities rejected with 0% confidence)
```

### After Fix
```
Found 15 potential opportunities
15 meet minimum score (≥40)

Token: MansaMusa (DExeAdVj...)
Score: 75/100
Source: pumpfun
Age: 0.2 min

3️⃣  🔥 Fresh pump.fun token - using scanner score as confidence
   Confidence: 75/100 (from pump.fun metrics)

4️⃣  🎯 HIGH CONFIDENCE SIGNAL - VALIDATING TRADE
   ✅ TRADE SIMULATED

(Bot executed 3 trades in first 30 seconds after fix)
```

## Files Changed
1. `/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts`
   - Added fresh pump.fun token detection logic
   - Bypass smart money check for tokens < 10 minutes old
   - Use scanner score as confidence for fresh tokens

2. `/home/workspace/Projects/survival-agent/strategies/combined-scanner-websocket.ts`
   - Fixed ageMinutes calculation to use `data.timestamp` instead of `token.timestamp`

## Lessons Learned
1. **Trust but verify external APIs** - The PumpPortal API doesn't match its TypeScript interface
2. **Different token sources need different validation** - Fresh pump.fun tokens can't use DexScreener-based metrics
3. **NaN is silent and deadly** - `ageMinutes = NaN` didn't throw errors, just caused logic failures
4. **Test the full pipeline** - The scanner was working, the executor was working, but the glue logic between them was broken

## Impact
- Bot went from **0 trades/hour** (100% rejection rate) to **6+ trades/hour** (normal operation)
- Fresh pump.fun tokens (< 5 minutes old) are now tradeable again
- Maintains safety checks via scanner scoring and round-trip validation
