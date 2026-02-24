# Paper Trading Fidelity Audit - Mainnet Simulation Accuracy

**Date:** Feb 15, 2026
**Purpose:** Identify data fidelity issues that could cause paper trading results to diverge from mainnet reality

---

## 🚨 CRITICAL ISSUES (High Impact on Results)

### 1. **HARDCODED SOL PRICE: $119**
**File:** `core/jupiter-validator.ts:79`
```typescript
private solPriceUsd: number = 119;
```

**Impact:** 🔴 **HIGH - Price calculations are wrong if SOL moves**
- Entry prices calculated in USD are off if SOL != $119
- P&L calculations in USD are inaccurate
- If SOL drops to $100, we're overstating USD value by 19%
- If SOL rises to $140, we're understating USD value by 15%

**Real SOL Price (Feb 15 2026):** Need to verify current price

**Fix Required:**
```typescript
// Fetch live SOL price from Jupiter or DexScreener
private async updateSolPrice(): Promise<void> {
  const response = await fetch('https://price.jup.ag/v6/price?ids=SOL');
  const data = await response.json();
  this.solPriceUsd = data.data.SOL.price;
}
```

**Mainnet Impact:** On mainnet, this won't matter because we're trading in SOL terms, not USD. But for paper trading metrics and comparisons, this is misleading.

---

### 2. **HARDCODED TOKEN DECIMALS: 6**
**File:** `core/jupiter-validator.ts:144`
```typescript
const decimals = 6;  // Assume 6 decimals (most tokens)
```

**Impact:** 🟡 **MEDIUM - Price calculations wrong for non-6-decimal tokens**
- Most SPL tokens use 6 or 9 decimals
- Pump.fun tokens typically use 6 decimals ✅
- But established tokens can use 9 (SOL), 8 (USDC), or other values
- Wrong decimals = wrong price by 1000x+ (if assuming 6 for a 9-decimal token)

**Example:**
- Token with 9 decimals, we get 1,000,000,000 units
- We calculate price assuming 6 decimals: 1,000,000 units
- Price is off by 1000x!

**Fix Required:**
```typescript
// Fetch token metadata from SPL Token Registry or on-chain
const decimals = await this.getTokenDecimals(tokenAddress);
```

**Mainnet Impact:** On mainnet, Jupiter handles decimals correctly in routing. But our PRICE DISPLAY and P&L TRACKING will be wrong for non-6-decimal tokens in paper trading.

---

### 3. **SLIPPAGE MISMATCH: Validation vs Execution**
**Files:**
- Validation: `jupiter-validator.ts` uses `slippageBps=300` (3%)
- Execution: `paper-trade-bot.ts` uses `slippageBps=1500` (15%)

**Impact:** 🟡 **MEDIUM - We're not validating what we execute**

**The Problem:**
1. Round-trip validation checks with 3% slippage
2. Actual trade execution uses 15% slippage
3. This means we might execute trades that would fail our validation!

**Example:**
- Token has 10% actual slippage
- Validation with 3% slippage: ❌ REJECTED (would fail)
- But we don't actually use that validation result
- Execution with 15% slippage: ✅ ACCEPTS the trade
- Result: We trade tokens we "validated" as too high slippage

**Current Code:**
```typescript
// Validation (not used for entry decision)
const roundTrip = await this.validator.validateRoundTrip(best.address, positionSize);

// Then we execute with DIFFERENT slippage
const tradeResult = await this.executor.executeTrade({
  ...
  slippageBps: 1500  // 15% - different from validation!
});
```

**Fix Required:** Use the SAME slippage for validation and execution, or don't validate at all if we're going to ignore it.

**Mainnet Impact:** On mainnet, this could cause:
- Trades that fail due to slippage (we accepted 15% but got 20%)
- Or trades that succeed but with terrible fills (accepted 15%, got 12%)

---

## 🟠 MODERATE ISSUES (Medium Impact)

### 4. **PRICE STALENESS: DexScreener Fallback**
**File:** `testing/paper-trade-bot.ts:524-536`

**The Flow:**
1. Try to get Jupiter price (real executable quote)
2. If that fails (429 rate limit, network error), fall back to DexScreener
3. DexScreener prices can be stale (5-60 seconds old)

**Impact:** 🟡 **MEDIUM - Using stale prices for exit decisions**

**The Problem:**
- Jupiter prices are REAL (what you'd actually get if you sold now)
- DexScreener prices are CACHED (what someone got 5-60 seconds ago)
- For volatile meme coins, 5 seconds = 10%+ price movement
- We might hold or sell based on outdated data

**Example:**
```
10:00:00 - Token at $0.00005 (current)
10:00:05 - Price dumps to $0.00003 (Jupiter shows this)
10:00:05 - But we hit 429 rate limit, use DexScreener
10:00:05 - DexScreener still shows $0.00005 (cached from 10:00:00)
10:00:05 - Bot thinks we're still profitable, doesn't sell
10:00:10 - Price at $0.00002, we finally get fresh data, big loss
```

**Mainnet Impact:** On mainnet, this delay means:
- Missed exit opportunities (thought price was higher than reality)
- False exits (thought price was lower than reality)
- Either way, we're trading on stale information

**Frequency:** Happens when we hit Jupiter rate limits (429 errors) - which is happening in the logs!

---

### 5. **DYNAMIC CHECK INTERVALS: Inconsistent Monitoring**
**File:** `testing/paper-trade-bot.ts:480-502`

**The Logic:**
```typescript
if (pnlPercent <= -25) checkInterval = 2000;      // Check every 2s near stop loss
else if (pnlPercent <= -15) checkInterval = 3000; // Check every 3s
else if (trade.tp1Hit) checkInterval = 3000;      // Check every 3s if trailing
else if (pnlPercent > 50) checkInterval = 5000;   // Check every 5s if big gain
else checkInterval = 10000;                       // Check every 10s otherwise
```

**Impact:** 🟡 **MEDIUM - Position monitoring frequency varies**

**The Problem:**
- A position at -10% gets checked every 10 seconds
- In 10 seconds, it could dump to -40% and we'd miss the -30% stop loss
- By the time we check again, we're at -50% instead of -30%

**Example Timeline:**
```
10:00:00 - Position at -10%, set checkInterval=10000 (10s)
10:00:02 - Price dumps hard, now at -35% (we don't know yet)
10:00:10 - We finally check, see -35%, trigger stop loss
10:00:10 - But we should have exited at -30% (8 seconds ago)
```

**Mainnet Impact:** On mainnet:
- We'd be monitoring constantly via WebSocket price feeds
- Or checking every 1-5 seconds regardless of P&L
- This dynamic interval creates ARTIFICIAL delays that wouldn't exist in reality

**Fix:** Use consistent monitoring interval (5s max) or WebSocket price feeds

---

### 6. **PAPER MODE LATENCY: Optimistic Simulation**
**File:** `core/optimized-executor.ts:366-372`

```typescript
// Simulate network latency (200-500ms for direct, 150-300ms for Jito)
const latency = this.useJito ? 150 + Math.random() * 150 : 200 + Math.random() * 300;
await new Promise(resolve => setTimeout(resolve, latency));
```

**Impact:** 🟡 **MEDIUM - Simulated latency is optimistic**

**Real Mainnet Latency:**
- Jito bundles: 200-800ms (not 150-300ms)
- Direct transactions: 300-1500ms (not 200-500ms)
- During network congestion: 2000-5000ms
- Failed transactions: Need retry, adding 5-15 seconds

**Current simulation assumes:**
- Best case network conditions
- No congestion
- No failed transactions
- Instant confirmation

**Mainnet Impact:**
- Real trades take 2-5x longer than paper trades
- Price can move significantly during real execution
- We might enter at a different price than paper trading simulated

---

## 🟢 MINOR ISSUES (Low Impact)

### 7. **JITO TIP PERCENTILE: Hardcoded p75**
**File:** `core/optimized-executor.ts:78`
```typescript
private jitoTipLevel: 'p25' | 'p50' | 'p75' | 'p95' | 'p99' = 'p75';
```

**Impact:** 🟢 **LOW - Tip level is reasonable but static**

**Current:** Using p75 ($0.0088/trade)
**Real world:** Should be dynamic based on competition

**Mainnet Impact:** Minor - p75 is competitive enough for most trades. Might lose on ultra-competitive opportunities that need p95/p99.

---

### 8. **RATE LIMITING: Not Simulated in Paper Mode**
**File:** `core/jupiter-validator.ts:45-59`

**Impact:** 🟢 **LOW - Paper trading doesn't experience rate limits**

**The Issue:**
- Paper trading makes the same API calls as real trading
- But we don't simulate the COST of those calls (API credits)
- We also don't simulate rate limit RECOVERY time

**Mainnet Impact:** On mainnet, we'll hit rate limits and need to:
- Back off more aggressively
- Use cached quotes when possible
- Pay for higher rate limits

**Current handling:** We retry 429s with exponential backoff ✅ This is good!

---

## 📊 ACCURACY ASSESSMENT

### What We're Getting RIGHT ✅
1. **Jupiter quotes for entry/exit** - Using real routing engine
2. **Round-trip validation** - Checking both buy and sell routes
3. **Fee tracking** - Jito tips + priority fees included
4. **Rate limit handling** - Retries with backoff
5. **Slippage awareness** - Checking round-trip slippage
6. **Paper mode transactions** - Not actually sending txs

### What's INACCURATE ❌
1. **SOL price hardcoded** - $119 assumption
2. **Token decimals hardcoded** - 6 decimals assumption
3. **Slippage mismatch** - Validate at 3%, execute at 15%
4. **Stale DexScreener fallback** - 5-60 second delay
5. **Optimistic latency** - 2-5x faster than reality
6. **Dynamic monitoring** - Inconsistent price checks

---

## 🎯 RECOMMENDED FIXES (Priority Order)

### Priority 1: CRITICAL (Fix Before Mainnet)
1. **Fetch live SOL price** - Update every 60 seconds
   ```typescript
   setInterval(() => this.updateSolPrice(), 60000);
   ```

2. **Fetch token decimals** - Query SPL metadata
   ```typescript
   const mintInfo = await connection.getParsedAccountInfo(new PublicKey(tokenMint));
   const decimals = mintInfo.value.data.parsed.info.decimals;
   ```

3. **Fix slippage consistency** - Use same slippage for validation and execution
   ```typescript
   const SLIPPAGE_BPS = 1500; // Use everywhere
   ```

### Priority 2: HIGH (Impacts P&L Accuracy)
4. **Consistent monitoring interval** - Check positions every 5s regardless of P&L
   ```typescript
   const CHECK_INTERVAL = 5000; // Fixed 5 seconds
   ```

5. **Realistic latency simulation** - Use pessimistic estimates
   ```typescript
   const latency = this.useJito ? 300 + Math.random() * 500 : 500 + Math.random() * 1000;
   ```

### Priority 3: MEDIUM (Nice to Have)
6. **WebSocket price feeds** - Real-time prices instead of polling
7. **Retry simulation** - Simulate failed transactions and retries
8. **Dynamic Jito tips** - Adjust based on competition

---

## 🔬 TESTING RECOMMENDATIONS

### Before Mainnet:
1. **Run paper trading for 24 hours**
2. **Compare paper results to ACTUAL Jupiter quotes at entry/exit**
3. **Log the difference:**
   - Paper entry price vs real quote at that moment
   - Paper exit price vs real quote at that moment
   - Calculate "paper profit" vs "would-be real profit"

### Validation Script:
```typescript
// At each trade:
const paperEntryPrice = roundTrip.buyPrice;
const realQuote = await jupiter.getQuote(/* same params */);
const realEntryPrice = calculatePriceFromQuote(realQuote);
const priceDiff = (paperEntryPrice - realEntryPrice) / realEntryPrice * 100;

console.log(`Price diff: ${priceDiff}%`);
// Log to CSV for analysis
```

---

## 🎓 CONCLUSION

**Overall Fidelity:** ~70-80%

**Biggest Risks:**
1. SOL price drift (if SOL moves from $119)
2. Slippage mismatch (validating different params than executing)
3. Stale prices (DexScreener fallback)

**Mainnet Reality Check:**
- Paper trading will likely show BETTER results than mainnet because:
  - Faster execution (optimistic latency)
  - No failed transactions
  - Perfect price data (when Jupiter works)
  - No MEV/sandwich attacks

**Recommendation:**
- Fix Priority 1 issues BEFORE trusting paper trading P&L
- Add 20-30% safety margin to paper trading results
- Run small mainnet test (0.1 SOL) to validate assumptions
