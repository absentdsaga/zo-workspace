# Git Version Analysis: Settings & Broken Components

## Summary
The git-tracked version of the Solana bot has **one critical bug** in the age filter logic, plus some other components that need attention. Here's the complete breakdown.

---

## Settings (Git Version)

### Trading Thresholds
```typescript
MAX_CONCURRENT_POSITIONS = 7        // Optimized for API rate limits
MAX_POSITION_SIZE = 0.12           // 12% of balance per trade
MIN_BALANCE = 0.05
MAX_DRAWDOWN = 0.25
MIN_SCORE = 40                     // Meme scanner minimum score
MIN_SMART_MONEY_CONFIDENCE = 45    // Raised from 35 based on backtest
MIN_SHOCKED_SCORE = 30             // Shocked group minimum score
```

### Exit Thresholds
```typescript
TAKE_PROFIT = 1.0                  // 100% gain (activates trailing stop)
STOP_LOSS = -0.30                  // -30% loss (before TP1)
TRAILING_STOP_PERCENT = 0.20       // 20% drop from peak (after TP1)
MAX_HOLD_TIME_MS = 60 * 60 * 1000  // 60 minutes
```

### Timing
```typescript
SCAN_INTERVAL_MS = 15000           // 15 seconds (scanner loop)
MONITOR_INTERVAL_MS = 5000         // 5 seconds (position monitor)
```

### Auto-Refill
```typescript
AUTO_REFILL_THRESHOLD = 0.03       // Refill when balance hits 0.03 SOL
AUTO_REFILL_AMOUNT = 1.0           // Add 1 SOL per refill
```

### Meme Scanner Settings
```typescript
MIN_AGE_MINUTES = 0
MAX_AGE_MINUTES = 1440             // 24 hours
MIN_LIQUIDITY = 2000               // $2k minimum
MIN_VOLUME_24H = 1000              // $1k minimum volume
```

---

## Broken Components

### 🚨 BUG #1: Age Filter Logic (CRITICAL)

**Location:** `strategies/meme-scanner.ts` line 112-116

**Broken Code:**
```typescript
// Calculate age (if pairCreatedAt exists)
let ageMinutes = 999; // Unknown age
if (pair.pairCreatedAt) {
  const ageMs = Date.now() - pair.pairCreatedAt;
  ageMinutes = ageMs / 1000 / 60;
}

// Filter: Skip very old tokens (>24h) if age is known
if (ageMinutes < 999 && ageMinutes > 1440) {
  continue;
}
```

**The Problem:**
The condition `if (ageMinutes < 999 && ageMinutes > 1440)` is **logically flawed**:

1. **Tokens with unknown age (999) pass through** ✅ (should be ❌)
   - Condition: `999 < 999` = FALSE, so the `continue` never executes
   - Unknown-age tokens are scored as valid

2. **Only filters tokens that are BOTH known AND >24h**
   - Requires BOTH conditions to be true
   - This was the intended behavior but poorly implemented

**Real-World Impact:**
- Bot traded tokens that were **4-6 DAYS old**:
  - Manchas: 6,095 minutes (4.2 days)
  - CIA: 7,518 minutes (5.2 days)
  - しずく: 8,960 minutes (6.2 days)
  - LAMB: 3,085 minutes (2.1 days)

**Why This Matters:**
- Fresh meme coins pump hardest in the **first 1-60 minutes**
- 4-6 day old tokens have already pumped and dumped
- Entry timing is terrible (late to the party)
- This explains poor win rates and losses

**The Fix (Current Working Code):**
```typescript
// Filter: NO AGE FILTERING - replicate Archive Master exactly
// Archive Master (626% profit) had no age filtering and included all tokens
// (The old broken code never filtered anything)
```

**Alternative Fix (Proper Age Filter):**
```typescript
// Skip tokens older than 24 hours (if age is known)
if (ageMinutes !== 999 && ageMinutes > 1440) {
  continue;
}
```

**Strictest Fix (Only Fresh Tokens):**
```typescript
// Only trade tokens <60 min old
if (!pair.pairCreatedAt || ageMinutes > 60) {
  continue;
}
```

---

### 🔧 ISSUE #2: OptimizedExecutor Initialization

**Location:** `testing/paper-trade-bot.ts` line 97

**Git Version (Missing Paper Mode Flag):**
```typescript
this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey);
```

**Working Version:**
```typescript
this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey, true); // Enable paper mode
```

**Impact:**
- Without the `true` flag, paper mode might not be properly enabled
- This could cause actual on-chain transactions in paper trading mode
- **CRITICAL for safety**

---

### 🔧 ISSUE #3: Shocked Calls - Single vs Multiple Processing

**Git Version:** Only processes **ONE** shocked call per cycle
```typescript
if (validShocked.length > 0) {
  const best = validShocked[0]; // Only takes first shocked call
  // ... process single call ...

  // Continues to next scan loop after shocked trade
  const elapsed = Date.now() - startTime;
  const sleepTime = Math.max(0, this.SCAN_INTERVAL_MS - elapsed);
  await new Promise(resolve => setTimeout(resolve, sleepTime));
  continue;
}
```

**Working Version:** Processes **MULTIPLE** shocked calls
```typescript
// Process multiple shocked calls (up to available position slots)
for (const best of validShocked) {
  const openPositions = this.trades.filter(t => t.status === 'open').length;

  // Stop if at max positions
  if (openPositions >= this.MAX_CONCURRENT_POSITIONS) {
    console.log(`⚠️  At max positions, skipping remaining shocked calls`);
    break;
  }

  // ... process each call ...
}
```

**Impact:**
- Git version misses multiple shocked opportunities in same cycle
- If 3 shocked calls come in, only takes 1
- Working version fills up to max positions with shocked calls

---

### 🔧 ISSUE #4: Missing Trade Execution Fees Tracking

**Git Version:** Creates trades without executor fee tracking
```typescript
this.trades.push({
  timestamp: Date.now(),
  tokenAddress: best.address,
  tokenSymbol: best.symbol,
  strategy: 'meme',
  source: 'shocked',
  amountIn: positionSize,
  entryPrice: entryPrice,
  currentPrice: entryPrice,
  peakPrice: entryPrice,
  tp1Hit: false,
  status: 'open',
  signature: 'PAPER_SHOCKED_' + Date.now(), // Fake signature!
  shockedScore: best.score
  // Missing: jitoTipPaid, priorityFeePaid, totalFeesPaid
});
```

**Working Version:** Actually executes through executor and tracks fees
```typescript
// Execute trade through executor (paper mode)
const tradeResult = await this.executor.executeTrade({
  inputMint: SOL_MINT,
  outputMint: best.address,
  amount: Math.floor(positionSize * LAMPORTS_PER_SOL),
  slippageBps: 1500,
  strategy: 'meme'
});

if (!tradeResult.success) {
  console.log(`❌ Trade execution failed: ${tradeResult.error}`);
  continue;
}

this.trades.push({
  // ... same fields ...
  signature: tradeResult.signature!,      // Real signature
  jitoTipPaid: tradeResult.jitoTipPaid || 0,
  priorityFeePaid: tradeResult.totalFeesSpent || 0,
  totalFeesPaid: (tradeResult.jitoTipPaid || 0) + ((tradeResult.totalFeesSpent || 0) / LAMPORTS_PER_SOL)
});
```

**Impact:**
- Git version doesn't track fee costs
- P&L calculations are inaccurate (missing fee deduction)
- Can't analyze true profitability vs gross profit

---

### 🔧 ISSUE #5: Missing Smart Money Confidence Variable

**Git Version:**
```typescript
console.log('3️⃣  Smart money analysis...');
const analysis = await this.tracker.hasSmartMoneyInterest(best.address);
console.log(`   Confidence: ${analysis.confidence}/100\n`);

if (analysis.confidence < this.MIN_SMART_MONEY_CONFIDENCE) {
  console.log(`   ⏭️  SKIPPED: Low confidence (${analysis.confidence} < ...)`);
  continue;
}

if (analysis.confidence >= this.MIN_SMART_MONEY_CONFIDENCE) {
  // ... execute trade ...
}
```

**Working Version:**
```typescript
const analysis = await this.tracker.hasSmartMoneyInterest(best.address);
const confidence = analysis.confidence; // Store in variable
console.log(`   Confidence: ${confidence}/100\n`);

if (confidence < this.MIN_SMART_MONEY_CONFIDENCE) {
  // ... use variable ...
}
```

**Impact:**
- Minor: Just cleaner code
- Working version stores confidence in variable for reuse

---

## Key Differences: Git vs Working

| Component | Git Version | Working Version |
|-----------|-------------|-----------------|
| **Age Filter** | Broken (`< 999 && > 1440`) | Disabled (no filter) |
| **Paper Mode** | Missing flag | `true` flag passed |
| **Shocked Processing** | Single call per cycle | Multiple calls per cycle |
| **Trade Execution** | Fake signatures | Real executor calls with fees |
| **Fee Tracking** | Missing | Full fee tracking (Jito + priority) |
| **Age Display** | Limited | Shows age in scanner output |

---

## Archive Master Context (626% Profit Run)

**Critical Discovery:** The Archive Master run that achieved **626% profit** had:

1. **ALL tokens with `ageMinutes: undefined`**
   - The broken age filter didn't actually filter anything
   - Since `undefined < 999` = false, no tokens were skipped
   - Archive Master succeeded WITHOUT age filtering

2. **Simple source strategy**
   - No shocked scanner
   - No subagent complexity
   - Just basic DexScreener + smart money confidence

3. **Key success factors were NOT age-based:**
   - Good confidence scoring (MIN_SMART_MONEY_CONFIDENCE = 45)
   - No repeat losers
   - Simple, consistent execution

**Takeaway:** The broken age filter was actually **allowing all tokens through**, and that setup won 626%. When we added proper age data, the win rate dropped because we started seeing (and trading) the actual old tokens.

---

## Recommendations

### 1. Age Filter Strategy

**Three options:**

**A) No Age Filter (Most Like Archive Master)**
```typescript
// Don't filter by age at all - replicate Archive Master
// Archive had undefined ages for all tokens
```
- **Pros:** Exactly matches 626% run
- **Cons:** Includes old tokens if age data exists

**B) 24-Hour Filter (Balanced)**
```typescript
if (ageMinutes !== 999 && ageMinutes > 1440) {
  continue; // Skip only if KNOWN age >24h
}
```
- **Pros:** Filters obvious trash, allows unknowns like Archive
- **Cons:** Still allows 24h old tokens

**C) Strict Fresh Filter (Aggressive)**
```typescript
if (!pair.pairCreatedAt || ageMinutes > 60) {
  continue; // Only <60 min with known age
}
```
- **Pros:** Only catches fresh pumps
- **Cons:** Much smaller opportunity pool

### 2. Priority Fixes

**CRITICAL (Fix Now):**
1. ✅ Add paper mode flag to executor init
2. ✅ Add real executor calls with fee tracking
3. ✅ Process multiple shocked calls per cycle

**HIGH (Test & Evaluate):**
4. Decide on age filter strategy (A, B, or C above)
5. Test with live paper trading to see results

**MEDIUM (Monitor):**
6. Track fee impact on profitability
7. Monitor shocked vs scanner win rates separately

---

## Testing Checklist

Before deploying:
- [ ] Verify paper mode is enabled (`true` flag)
- [ ] Confirm executor is actually called (not fake signatures)
- [ ] Check fee tracking is working (jitoTipPaid, priorityFeePaid)
- [ ] Test multiple shocked calls can execute in one cycle
- [ ] Validate age filter behavior matches intent
- [ ] Monitor first 20-30 trades for proper execution

---

## Conclusion

The git-tracked version has **one critical bug** (age filter) and several **missing features** (proper execution, fee tracking, multi-shocked).

The current working version has fixed these issues, but **removed age filtering entirely** to replicate the Archive Master's accidental success.

**Next decision:** Choose whether to keep no age filter (like Archive) or add back a proper filter (24h or 60min).
