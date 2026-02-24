# Complete Settings Breakdown: Git vs Current vs What's Working

## 📊 Complete Comparison Table

| Setting | Git Version | Current Working Version | Change Reason |
|---------|-------------|------------------------|---------------|
| **MIN_LIQUIDITY** | $2,000 | $10,000 | **5x INCREASE** - Filter out 78% loss rate rugs |
| **MIN_VOLUME_24H** | $1,000 | $500,000 | **500x INCREASE** - Target established tokens |
| **Age Filter** | Broken (let old tokens through) | DISABLED (no filter) | Replicate Archive Master (626% profit) |
| **Volume/Liquidity Ratio** | >1.0x | >1.0x | SAME |
| **Price Momentum Threshold** | >10% in 1h | >10% in 1h | SAME |
| **Liquidity Bonus Threshold** | >$10k | >$10k | SAME |
| **Fresh Launch Window** | <15 min | <15 min | SAME |
| **Market Cap Sweet Spot** | $20k-$1M | $20k-$1M | SAME |
| **MIN_SCORE** | 40 | 40 | SAME |
| **Paper Mode Flag** | Missing (`false`) | `true` | **CRITICAL** - Enable paper mode |
| **Shocked Processing** | Single call/cycle | Multiple calls/cycle | Fill up to max positions |
| **Executor Integration** | Fake signatures | Real executor + fees | Track actual costs |

---

## 🔍 Meme Scanner Settings - DETAILED

### Git Version (Original)
```typescript
MIN_AGE_MINUTES = 0
MAX_AGE_MINUTES = 1440        // 24 hours (not enforced - broken filter)
MIN_LIQUIDITY = 2000          // $2k minimum
MIN_VOLUME_24H = 1000         // $1k minimum volume

// Age filter (BROKEN):
if (ageMinutes < 999 && ageMinutes > 1440) {
  continue; // Only filters tokens with KNOWN age >24h
}

// Liquidity filter:
if (liquidityUSD < 2000) continue;

// Volume filter:
if (volume24h < 1000) continue;
```

**Result:** Very loose filters, let through almost everything including:
- Tokens with unknown age (999)
- Tokens 4-6 days old (if age known)
- Low liquidity ($2k)
- Low volume ($1k/day)

### Current Working Version
```typescript
MIN_AGE_MINUTES = 0
MAX_AGE_MINUTES = 1440        // 24 hours (not used)
MIN_LIQUIDITY = 10000         // $10k minimum (5x increase)
MIN_VOLUME_24H = 500000       // $500k minimum (500x increase!)

// Age filter (DISABLED):
// Filter: NO AGE FILTERING - replicate Archive Master exactly
// Archive Master (626% profit) had no age filtering and included all tokens

// Liquidity filter (MUCH STRICTER):
if (liquidityUSD < this.MIN_LIQUIDITY) continue;  // $10k

// Volume filter (EXTREMELY STRICT):
if (volume24h < this.MIN_VOLUME_24H) continue;    // $500k
```

**Result:** MUCH tighter filters:
- ✅ No age filtering (like Archive Master)
- ✅ 5x higher liquidity requirement ($10k vs $2k)
- ✅ 500x higher volume requirement ($500k vs $1k)
- ✅ Filters out 78% loss rate rug pulls
- ✅ Targets established, high-volume tokens

---

## 📈 Scoring System - IDENTICAL (Both Versions)

| Signal | Points | Threshold | Description |
|--------|--------|-----------|-------------|
| **Volume Spike** | 25 | volume/liquidity > 1.0x | High volume relative to pool |
| **Price Momentum** | 30 | +10% in 1h | Recent price pump |
| **Strong Liquidity** | 10 | >$10k | Decent pool size |
| **Fresh Launch** | 25 | <15 min old | Very recent launch |
| **MC Sweet Spot** | 10 | $20k-$1M | Not too small, not too big |
| **TOTAL** | 100 | MIN_SCORE = 40 | Need 40+ to qualify |

**Key Point:** Scoring logic is UNCHANGED between versions. The difference is:
1. **Git version:** Scores many tokens (loose filters)
2. **Current version:** Scores fewer tokens (strict filters)

### How Tokens Can Score 40+ Points

**Scenario 1: Fresh token with volume (100 points)**
```
Volume spike: 25 (high volume)
Price momentum: 30 (pumping +10%)
Liquidity: 10 (>$10k)
Fresh bonus: 25 (<15 min)
MC sweet spot: 10 ($20k-$1M)
────────────────────────
TOTAL: 100 ✅
```

**Scenario 2: Old token with momentum (75 points)**
```
Volume spike: 25 (high volume)
Price momentum: 30 (pumping +10%)
Liquidity: 10 (>$10k)
Fresh bonus: 0 (too old)
MC sweet spot: 10 ($20k-$1M)
────────────────────────
TOTAL: 75 ✅ Passes MIN_SCORE=40
```

**Scenario 3: High liquidity token (45 points)**
```
Volume spike: 25 (volume/liq > 1.0x)
Price momentum: 0 (not pumping)
Liquidity: 10 (>$10k)
Fresh bonus: 0 (old)
MC sweet spot: 10 ($20k-$1M)
────────────────────────
TOTAL: 45 ✅ Barely passes
```

**Critical Issue with Git Version:**
- Old tokens (4-6 days) could easily score 75+ points
- Fresh bonus NOT required to pass MIN_SCORE
- Scanner preferred OLD tokens with current volume over FRESH tokens

**How Current Version Helps:**
- $500k volume requirement means token must be established
- High liquidity ($10k) filters out most rugs
- Fewer false positives from stale pumps

---

## 🎯 Paper Trading Bot Settings - DETAILED

### Trading Thresholds (SAME in both versions)
```typescript
MAX_CONCURRENT_POSITIONS = 7
MAX_POSITION_SIZE = 0.12      // 12% of balance
MIN_BALANCE = 0.05
MAX_DRAWDOWN = 0.25
MIN_SCORE = 40                // Meme scanner minimum
MIN_SMART_MONEY_CONFIDENCE = 45
MIN_SHOCKED_SCORE = 30
```

### Exit Strategy (SAME in both versions)
```typescript
TAKE_PROFIT = 1.0             // 100% gain (TP1)
STOP_LOSS = -0.30             // -30% loss (before TP1)
TRAILING_STOP_PERCENT = 0.20  // 20% from peak (after TP1)
MAX_HOLD_TIME_MS = 3600000    // 60 minutes
```

### Timing (SAME in both versions)
```typescript
SCAN_INTERVAL_MS = 15000      // 15 seconds
MONITOR_INTERVAL_MS = 5000    // 5 seconds
```

### Auto-Refill (SAME in both versions)
```typescript
AUTO_REFILL_THRESHOLD = 0.03  // Trigger at 0.03 SOL
AUTO_REFILL_AMOUNT = 1.0      // Add 1 SOL per refill
```

---

## 🚨 Critical Differences (Implementation)

### 1. Paper Mode Flag
**Git Version:**
```typescript
this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey);
// Missing paper mode flag - defaults to false
```

**Current Version:**
```typescript
this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey, true);
// Explicitly enables paper mode
```

**Impact:** Git version could accidentally execute real trades!

### 2. Shocked Call Processing
**Git Version:**
```typescript
if (validShocked.length > 0) {
  const best = validShocked[0]; // Only takes FIRST call

  if (!alreadyHolding && openPositions < this.MAX_CONCURRENT_POSITIONS) {
    // Execute trade
    // Then immediately continue to next scan cycle
    continue;
  }
}
```

**Current Version:**
```typescript
for (const best of validShocked) {  // Process MULTIPLE calls
  const openPositions = this.trades.filter(t => t.status === 'open').length;

  if (openPositions >= this.MAX_CONCURRENT_POSITIONS) {
    break; // Stop when full
  }

  // Execute each shocked call
}
```

**Impact:**
- Git: Only 1 shocked call per cycle (misses opportunities)
- Current: Up to 7 shocked calls per cycle (fills all positions)

### 3. Trade Execution
**Git Version:**
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
  signature: 'PAPER_SHOCKED_' + Date.now(), // FAKE SIGNATURE
  shockedScore: best.score
  // Missing: jitoTipPaid, priorityFeePaid, totalFeesPaid
});

// No actual executor call - just logs fake trade
```

**Current Version:**
```typescript
// Execute trade through executor (paper mode)
const SOL_MINT = 'So11111111111111111111111111111111111111112';
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

console.log(`⚡ Execution time: ${tradeResult.executionTime}ms`);
console.log(`🚀 Priority fee: ${tradeResult.priorityFeeUsed} µL`);

this.trades.push({
  // ... same fields ...
  signature: tradeResult.signature!,      // REAL signature
  shockedScore: best.score,
  jitoTipPaid: tradeResult.jitoTipPaid || 0,
  priorityFeePaid: tradeResult.totalFeesSpent || 0,
  totalFeesPaid: (tradeResult.jitoTipPaid || 0) + ((tradeResult.totalFeesSpent || 0) / LAMPORTS_PER_SOL)
});
```

**Impact:**
- Git: No actual execution, fake costs, no validation
- Current: Real execution, real fees tracked, proper validation

---

## 💰 Fee Tracking Comparison

### Git Version (NO FEE TRACKING)
```typescript
interface TradeLog {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  strategy: 'meme' | 'arbitrage' | 'perp' | 'volume';
  source?: 'pumpfun' | 'dexscreener' | 'both' | 'shocked';
  amountIn: number;
  entryPrice?: number;
  currentPrice?: number;
  peakPrice?: number;
  tp1Hit?: boolean;
  signature?: string;
  pnl?: number;
  // Missing fee fields
  status: 'open' | 'closed_profit' | 'closed_loss' | 'failed';
  error?: string;
  exitTimestamp?: number;
  exitReason?: string;
  confidenceScore?: number;
  shockedScore?: number;
}
```

### Current Version (FULL FEE TRACKING)
```typescript
interface TradeLog {
  // ... same fields ...
  pnl?: number;
  pnlGross?: number;          // P&L before fees
  jitoTipPaid?: number;       // Jito tip in SOL (entry + exit)
  priorityFeePaid?: number;   // Priority fees in lamports (entry + exit)
  totalFeesPaid?: number;     // Total fees in SOL
  status: 'open' | 'closed_profit' | 'closed_loss' | 'failed';
  // ... rest of fields ...
}
```

**Impact:**
- Git version: Can't calculate true profitability (missing fee costs)
- Current version: Tracks exact costs for Jito tips + priority fees

---

## 📊 Impact Analysis

### What Changed and WHY

| Change | From | To | Reason |
|--------|------|----|---------|
| **Liquidity Filter** | $2k | $10k | 78% of <$10k liquidity tokens are rugs |
| **Volume Filter** | $1k | $500k | Targets established tokens with real trading |
| **Age Filter** | Broken | Disabled | Archive Master (626%) had no age filter |
| **Paper Mode** | Missing | Enabled | Safety - prevent real trades |
| **Shocked Processing** | 1/cycle | Multiple/cycle | Catch all valid opportunities |
| **Executor Calls** | Fake | Real | Proper validation + fee tracking |

### Expected Results

**Git Version (Loose Filters):**
- ✅ More opportunities found (low thresholds)
- ❌ Many are rugs (78% of <$10k liquidity)
- ❌ Many are stale (4-6 days old)
- ❌ Low win rate (26% observed)
- ❌ No fee tracking (inaccurate P&L)

**Current Version (Strict Filters):**
- ⚠️  Fewer opportunities found (high thresholds)
- ✅ Filter out 78% of rugs ($10k liquidity)
- ✅ Filter out low-volume scams ($500k volume)
- ✅ No age bias (like Archive Master)
- ✅ Real execution with fee tracking
- ✅ Multiple shocked calls per cycle

---

## 🎯 Archive Master Context (626% Profit)

**What Archive Master Had:**
```
MIN_LIQUIDITY: $2,000
MIN_VOLUME_24H: $1,000
Age Filter: BROKEN (let everything through)
All tokens: ageMinutes = undefined
Paper Mode: Working
Shocked Scanner: NOT USED
Executor: Real calls with fees
```

**Win Rate:** 38.9% (115W / 180L)
**Total Trades:** 295
**Return:** +626%

**Key Success Factors:**
1. ✅ Simple sources (DexScreener only)
2. ✅ Good confidence threshold (MIN_SMART_MONEY = 45)
3. ✅ No repeat losers
4. ✅ Accidental "no age filter" let all tokens through
5. ✅ Low barriers = high opportunity volume

---

## 🤔 The Strategy Dilemma

### Option A: Archive Master Replica (Loose Filters)
```typescript
MIN_LIQUIDITY = 2000          // $2k (like Archive)
MIN_VOLUME_24H = 1000         // $1k (like Archive)
Age Filter = DISABLED         // (like Archive)
```

**Pros:**
- Exactly matches 626% run
- High opportunity volume
- Proven to work

**Cons:**
- 78% of <$10k liquidity are rugs
- Includes stale tokens if age data exists
- Lower quality opportunities

### Option B: Strict Filters (Current)
```typescript
MIN_LIQUIDITY = 10000         // $10k (5x stricter)
MIN_VOLUME_24H = 500000       // $500k (500x stricter!)
Age Filter = DISABLED         // (like Archive)
```

**Pros:**
- Filters out 78% of rugs
- Targets established tokens
- Higher quality opportunities

**Cons:**
- Much lower opportunity volume
- May miss early pumps
- Unproven (not tested yet)

### Option C: Hybrid Approach
```typescript
MIN_LIQUIDITY = 5000          // $5k (middle ground)
MIN_VOLUME_24H = 50000        // $50k (middle ground)
Age Filter = DISABLED         // (like Archive)
```

**Pros:**
- Balanced filters
- More opportunities than Option B
- Better quality than Option A

**Cons:**
- Not proven (needs testing)
- Still arbitrary thresholds

---

## 🔬 Testing Strategy

### Phase 1: Current Settings (Strict)
```
MIN_LIQUIDITY = $10k
MIN_VOLUME_24H = $500k
Age Filter = OFF
```
**Run 50-100 trades and measure:**
- Opportunity volume (trades/day)
- Win rate
- Average P&L
- Fee impact

### Phase 2: Archive Replica (Loose)
```
MIN_LIQUIDITY = $2k
MIN_VOLUME_24H = $1k
Age Filter = OFF
```
**Run 50-100 trades and measure:**
- Opportunity volume (trades/day)
- Win rate
- Average P&L
- Rug rate (how many total losses)

### Phase 3: Compare & Optimize
- Which has higher win rate?
- Which has better risk-adjusted returns?
- Which has more opportunities?
- Find optimal balance

---

## 🚀 Immediate Next Steps

1. **Verify Current Settings Are Active:**
   ```bash
   grep "MIN_LIQUIDITY\|MIN_VOLUME" strategies/meme-scanner.ts
   ```

2. **Check Paper Mode Is Enabled:**
   ```bash
   grep "OptimizedExecutor" testing/paper-trade-bot.ts
   ```

3. **Run Test Session (20-30 trades):**
   ```bash
   bun run testing/paper-trade-bot.ts
   ```

4. **Monitor Results:**
   - How many opportunities found per hour?
   - What's the win rate?
   - Are trades executing properly?
   - Are fees being tracked?

5. **Compare to Archive Master:**
   - Opportunity volume: Archive had ~295 trades
   - Win rate target: 38.9%
   - If too few opportunities: Lower thresholds
   - If too many rugs: Raise thresholds

---

## ✅ Summary

### Git Version Problems:
1. ❌ Broken age filter (let 4-6 day tokens through)
2. ❌ Low liquidity threshold ($2k → 78% rug rate)
3. ❌ Low volume threshold ($1k → includes dead tokens)
4. ❌ Missing paper mode flag
5. ❌ Only 1 shocked call per cycle
6. ❌ No real executor calls
7. ❌ No fee tracking

### Current Version Improvements:
1. ✅ Age filter disabled (like Archive Master)
2. ✅ High liquidity ($10k → filters rugs)
3. ✅ High volume ($500k → established tokens)
4. ✅ Paper mode enabled
5. ✅ Multiple shocked calls per cycle
6. ✅ Real executor with validation
7. ✅ Full fee tracking (Jito + priority)

### The Big Question:
**Are the filters TOO strict now?**
- $500k volume is EXTREMELY high
- May filter out early-stage pumps
- Need to test and compare to Archive Master's loose filters

**Recommendation:** Run current settings for 50 trades, then test Archive replica, then find optimal balance.
