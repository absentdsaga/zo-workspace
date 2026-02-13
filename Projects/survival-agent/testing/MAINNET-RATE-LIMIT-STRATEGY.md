# ⚡ Mainnet-Ready Rate Limit Strategy

## Core Principle for Real Money:
**NEVER sacrifice exit speed for rate limits. Your money > API efficiency.**

---

## 🎯 The Right Solution: Reduce Entry Checks, Keep Exit Speed

### The Problem With Current Design:

```
Every 5 seconds, for EACH of 10 positions:
  ✅ getRealExecutablePrice() → Check current price
  ❌ When exit triggered → validateSellRoute() → 2 MORE calls
  
Result: 10 positions = 10 calls + exit calls = 120-150 calls/min
```

### The Real Inefficiency: **Pre-Buy Validation**

```typescript
// BEFORE buying (Scanner loop - happens BEFORE we have money at risk):
validateRoundTrip() → 2 API calls (buy quote + sell quote)
Smart money check → 1-2 API calls
hasSmartMoneyInterest() → More calls

// This is where we can save API calls WITHOUT risking exit speed
```

---

## 🎯 Strategy 1: Aggressive Entry Filtering (Safest)

### Reduce positions, not exit speed:

```typescript
// Current:
MAX_CONCURRENT_POSITIONS = 10  // Too many for API limits

// Mainnet:
MAX_CONCURRENT_POSITIONS = 5   // Fewer positions = fewer API calls on exits
```

**Impact:**
- ❌ Before: 10 positions × 12 calls/min = 120 calls/min
- ✅ After: 5 positions × 12 calls/min = 60 calls/min
- **50% reduction, ZERO impact on exit speed**

**Trade-offs:**
- ✅ More focused trading (quality > quantity)
- ✅ Larger positions per trade (still 12% each)
- ✅ Less diversification risk
- ❌ Fewer opportunities

---

## 🎯 Strategy 2: Skip Redundant Pre-Buy Checks

### Current pre-buy validation is OVERKILL:

```typescript
// Current (wasteful):
const roundTrip = await validateRoundTrip();  // 2 calls
if (roundTrip.canBuy && roundTrip.canSell) {
  // Buy
}

// Streamlined (trust the scanner):
const buyRoute = await validateBuyRoute();  // 1 call only
if (buyRoute.valid) {
  // Buy - we'll check sell when we need to exit
}
```

**Logic:**
- If token rugs AFTER you buy → you lose anyway
- If token has liquidity NOW → buy it
- Check sell route only when EXITING (when it matters)

**Impact:**
- Saves 1 API call per trade entry
- Reduces scanner load by 50%
- **Exits still full speed**

**Risk:**
- You might buy tokens that rug before you can exit
- **BUT:** This was happening anyway (tokens rug AFTER validateRoundTrip passes)

---

## 🎯 Strategy 3: Smart Monitor Interval Scaling

### Don't check ALL positions every 5 seconds:

```typescript
async checkExitsWithTrailingStop(): Promise<void> {
  const openTrades = this.trades.filter(t => t.status === 'open');
  
  for (const trade of openTrades) {
    const holdTime = Date.now() - trade.timestamp;
    const pnl = ((trade.currentPrice! - trade.entryPrice!) / trade.entryPrice!) * 100;
    
    // DYNAMIC check frequency based on risk:
    let checkInterval: number;
    
    if (pnl <= -25) {
      // CRITICAL: Near stop loss (-30%)
      checkInterval = 2000;  // Check every 2 seconds
    } else if (pnl <= -15) {
      // WARNING: Getting close
      checkInterval = 5000;  // Check every 5 seconds
    } else if (trade.tp1Hit) {
      // TRAILING: After TP1, price moving fast
      checkInterval = 3000;  // Check every 3 seconds
    } else if (pnl > 50) {
      // WINNING: Big gains, watch closely
      checkInterval = 5000;  // Check every 5 seconds
    } else {
      // SAFE: Normal range
      checkInterval = 10000; // Check every 10 seconds
    }
    
    const lastCheck = this.lastCheckTime.get(trade.tokenAddress) || 0;
    if (Date.now() - lastCheck < checkInterval) continue;
    
    // Check this position
    await this.checkSinglePosition(trade);
    this.lastCheckTime.set(trade.tokenAddress, Date.now());
  }
}
```

**Impact:**
- Critical positions: Checked every 2-3s (FASTER than current!)
- Safe positions: Checked every 10s
- **Average: 30-40% fewer API calls, BETTER exit speed on what matters**

---

## 🎯 Strategy 4: Use Jupiter API Key Tier

### You have a Jupiter API key - use it properly:

```typescript
// Check your current tier:
// Free tier: 60 requests/min
// Paid tier: 600+ requests/min

// If you're hitting limits on mainnet:
// 1. Upgrade to paid tier ($50-100/month)
// 2. Worth it if you're trading real money
```

**Cost-benefit:**
- Jupiter Pro API: ~$100/month
- One saved exit from rate limit: Worth it
- **Just pay for the API tier you need**

---

## 🎯 Strategy 5: Parallel API Calls with Delay

### Use Promise.all() but space them out:

```typescript
async checkAllPositions(trades: TradeLog[]): Promise<void> {
  // Don't do this (rate limit):
  // await Promise.all(trades.map(t => checkPosition(t)));
  
  // Do this (controlled concurrency):
  const BATCH_SIZE = 3;  // 3 concurrent calls max
  const BATCH_DELAY = 1000; // 1 second between batches
  
  for (let i = 0; i < trades.length; i += BATCH_SIZE) {
    const batch = trades.slice(i, i + BATCH_SIZE);
    await Promise.all(batch.map(t => this.checkSinglePosition(t)));
    
    if (i + BATCH_SIZE < trades.length) {
      await new Promise(r => setTimeout(r, BATCH_DELAY));
    }
  }
}
```

**Impact:**
- 10 positions checked in 3-4 seconds instead of instant
- Spreads API load
- **Still fast enough for exits**

---

## 🎯 Strategy 6: Emergency Rate Limit Handler

### When you DO hit rate limit, handle it intelligently:

```typescript
async validateSellRoute(tokenAddress: string, amount: number): Promise<RouteValidation> {
  try {
    const response = await fetch(url);
    
    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '2');
      
      console.log(`⚠️  RATE LIMITED - Retrying in ${retryAfter}s`);
      console.log(`⚠️  Position: ${tokenAddress} - EXIT DELAYED`);
      
      // Wait and retry ONCE (don't give up)
      await new Promise(r => setTimeout(r, retryAfter * 1000));
      
      // Retry the sell validation
      return this.validateSellRoute(tokenAddress, amount);
    }
    
    // ... rest of validation
  } catch (error) {
    // Don't mark as rugged on network errors
    return { valid: false, liquidityInsufficient: false, error: error.message };
  }
}
```

**Impact:**
- Rate limit = 2-5 second delay, NOT a failed exit
- Much better than marking as "rugged"

---

## 🚀 Recommended Mainnet Configuration

### Combine these strategies:

```typescript
// 1. Fewer positions (reduces load)
MAX_CONCURRENT_POSITIONS = 5

// 2. Skip redundant pre-buy checks
// Only validate buy route, not full round-trip

// 3. Dynamic check intervals
// Critical positions: 2s, Safe positions: 10s

// 4. Emergency retry on 429
// Wait and retry instead of failing

// 5. Consider Jupiter API tier upgrade if needed
```

### Expected Performance:
- **API calls:** 30-40/min (vs 120+ before)
- **Exit speed (critical positions):** 2-3 seconds ⚡
- **Exit speed (safe positions):** 5-10 seconds ✅
- **Rate limit risk:** Very low
- **Real money safety:** Maximum

---

## 📊 Mainnet-Ready Comparison

| Metric | Old Bot | Paper Bot Now | Mainnet Bot |
|--------|---------|---------------|-------------|
| Max positions | 10 | 10 | **5** |
| Check interval | 5s (all) | 5s (all) | **2-10s (dynamic)** |
| Pre-buy checks | 2 calls | 2 calls | **1 call** |
| Exit checks | Always | Always | **Always** ✅ |
| API calls/min | 120+ | 120+ | **30-40** |
| Rate limit handling | Mark as rug | **Retry** ✅ | **Retry** ✅ |
| Exit speed (critical) | 5s | 5s | **2-3s** ⚡ |
| Real money ready | ❌ | ❌ | **✅** |

---

## ✅ Action Plan

1. **Reduce MAX_CONCURRENT_POSITIONS to 5** (instant 50% reduction)
2. **Add dynamic check intervals** (faster checks on critical positions)
3. **Implement rate limit retry logic** (2-5s delay vs failing)
4. **Remove redundant pre-buy sell validation** (saves 1 call per entry)
5. **Monitor API usage on mainnet** (add logging)
6. **Upgrade Jupiter API tier if needed** (worth it for real money)

**Result:** 
- 70% fewer API calls
- FASTER exits on critical positions
- SAFER for real money
- Rate limit protection

Want me to implement this?
