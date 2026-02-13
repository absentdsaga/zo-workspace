# ⚡ Rate Limit Optimization Strategy

## The Problem

Jupiter API rate limits caused 12 false "rugs" (-0.330 SOL). We need to:
1. ✅ Stay under rate limits
2. ✅ Still exit positions fast when needed
3. ✅ Maximize API efficiency

---

## Current API Usage Pattern

### Per Trade Cycle (every 5-15 seconds):
```
Scanner Loop (15s):
- validateRoundTrip() = 2 calls (buy quote + sell quote)
- Smart money analysis = 0-2 calls
- TOTAL: 2-4 calls per opportunity

Monitor Loop (5s, per position):
- getRealExecutablePrice() = 1 call per position
- validateSellRoute() when exiting = 2 calls (buy quote + sell quote)
- TOTAL: 1-3 calls per position
```

### The Rate Limit Killers:
1. **10 concurrent positions × monitor every 5s** = 10 API calls every 5s = **120 calls/min**
2. **Rapid re-buys after failures** = Doubles the API load
3. **No caching** = Same token checked multiple times

---

## 🎯 Solution 1: Smart Caching (Fastest, Easiest)

### Cache price checks for 3-5 seconds:

```typescript
private priceCache = new Map<string, { price: number; timestamp: number }>();
private readonly PRICE_CACHE_TTL = 3000; // 3 seconds

async getRealExecutablePriceCached(
  tokenAddress: string,
  direction: 'buy' | 'sell',
  amount: number
): Promise<number | null> {
  const cacheKey = `${tokenAddress}_${direction}_${amount}`;
  const cached = this.priceCache.get(cacheKey);
  
  // Use cache if < 3 seconds old
  if (cached && (Date.now() - cached.timestamp) < this.PRICE_CACHE_TTL) {
    return cached.price;
  }
  
  // Fetch fresh price
  const price = await this.validator.getRealExecutablePrice(tokenAddress, direction, amount);
  
  if (price !== null) {
    this.priceCache.set(cacheKey, { price, timestamp: Date.now() });
  }
  
  return price;
}
```

**Impact:**
- ❌ Before: 10 positions × 12 checks/min = **120 API calls/min**
- ✅ After: 10 positions × 4 checks/min = **40 API calls/min**
- **67% reduction**, still checks every 3-5 seconds

---

## 🎯 Solution 2: Stagger Position Checks

Instead of checking ALL positions every 5s, stagger them:

```typescript
private lastCheckTime = new Map<string, number>();

async checkExitsWithTrailingStop(): Promise<void> {
  const openTrades = this.trades.filter(t => t.status === 'open');
  const now = Date.now();
  
  for (const trade of openTrades) {
    const lastCheck = this.lastCheckTime.get(trade.tokenAddress) || 0;
    const timeSinceCheck = now - lastCheck;
    
    // Stagger: Check each position every 10-15s instead of all at 5s
    const checkInterval = 10000; // 10 seconds per position
    
    if (timeSinceCheck < checkInterval) {
      console.log(`   ⏭️  ${trade.tokenSymbol}: Checked ${(timeSinceCheck/1000).toFixed(1)}s ago, skipping`);
      continue;
    }
    
    // Do the check
    await this.checkSinglePosition(trade);
    this.lastCheckTime.set(trade.tokenAddress, now);
  }
}
```

**Impact:**
- Spreads 10 positions over 50 seconds instead of all in 5 seconds
- **Still fast** - each position checked every 10s
- **90% rate limit reduction**

---

## 🎯 Solution 3: Priority-Based Checking

Check positions based on urgency:

```typescript
async checkExitsWithTrailingStop(): Promise<void> {
  const openTrades = this.trades.filter(t => t.status === 'open');
  
  // Sort by urgency
  const sorted = openTrades.sort((a, b) => {
    // Priority 1: Positions near stop loss (need fast checks)
    const aPnl = ((a.currentPrice! - a.entryPrice!) / a.entryPrice!) * 100;
    const bPnl = ((b.currentPrice! - b.entryPrice!) / b.entryPrice!) * 100;
    
    const aUrgent = aPnl < -20; // Near -30% stop loss
    const bUrgent = bPnl < -20;
    
    if (aUrgent && !bUrgent) return -1; // Check 'a' first
    if (!aUrgent && bUrgent) return 1;  // Check 'b' first
    
    // Priority 2: TP1 hit (trailing stop active)
    if (a.tp1Hit && !b.tp1Hit) return -1;
    if (!a.tp1Hit && b.tp1Hit) return 1;
    
    // Priority 3: Oldest positions
    return a.timestamp - b.timestamp;
  });
  
  // Check urgent positions every cycle, others less frequently
  for (let i = 0; i < sorted.length; i++) {
    const trade = sorted[i];
    const pnl = ((trade.currentPrice! - trade.entryPrice!) / trade.entryPrice!) * 100;
    const urgent = pnl < -20 || trade.tp1Hit;
    
    if (urgent) {
      // Check every cycle (5s)
      await this.checkSinglePosition(trade);
    } else if (i % 2 === 0) {
      // Check every other cycle (10s)
      await this.checkSinglePosition(trade);
    }
  }
}
```

**Impact:**
- Losing positions: Checked every 5s ✅
- Winning positions: Checked every 10s ✅
- **50% rate limit reduction** while staying fast on important exits

---

## 🎯 Solution 4: Batch API Calls

Use Jupiter's quote API with multiple tokens:

```typescript
// Instead of 10 separate calls:
for (const trade of trades) {
  const price = await getPrice(trade.tokenAddress); // 1 call each
}

// Do 1 batch call:
const prices = await getBatchPrices(trades.map(t => t.tokenAddress)); // 1 call total
```

**Jupiter doesn't officially support batch quotes**, but you can:
- Use Promise.all() with delay between calls
- Implement request queuing

---

## 🎯 Solution 5: Rate Limit Headers + Backoff

Monitor Jupiter's rate limit headers:

```typescript
async function fetchWithRateLimitAwareness(url: string) {
  const response = await fetch(url);
  
  // Check rate limit headers
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');
  
  if (remaining && parseInt(remaining) < 10) {
    console.log(`⚠️  Only ${remaining} API calls remaining, slowing down...`);
    // Increase cache TTL temporarily
    this.PRICE_CACHE_TTL = 10000; // 10 seconds
  }
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After') || '60';
    console.log(`🛑 Rate limited! Waiting ${retryAfter}s...`);
    await new Promise(r => setTimeout(r, parseInt(retryAfter) * 1000));
    return fetchWithRateLimitAwareness(url); // Retry
  }
  
  return response;
}
```

---

## 🎯 Recommended Implementation

### Combine Solutions 1 + 3 (Best Balance):

```typescript
// Add to class:
private priceCache = new Map<string, { price: number; timestamp: number }>();
private readonly PRICE_CACHE_TTL = 4000; // 4 seconds

// 1. Cache price checks (67% reduction)
async getRealExecutablePriceCached(...) { /* Solution 1 */ }

// 2. Priority-based checking (50% additional reduction)
async checkExitsWithTrailingStop() { /* Solution 3 */ }

// Combined effect: 85% rate limit reduction
```

### Expected Results:
- **Before:** 120 API calls/min → Rate limit at ~10 positions
- **After:** 18-20 API calls/min → Can handle 20+ positions
- **Exit speed:** 
  - Urgent positions: 4-5 second detection (cached price updates every 4s)
  - Safe positions: 8-10 second detection
  - Still WAY faster than manual trading

---

## 📊 Comparison Table

| Strategy | API Calls/Min | Exit Speed | Complexity |
|----------|---------------|------------|------------|
| Current (No optimization) | 120+ | 5s | Low |
| **Solution 1: Caching** | 40 | 4s | **Low** ⭐ |
| Solution 2: Staggering | 12 | 10s | Medium |
| **Solution 3: Priority** | 60 | 5s (urgent) | **Medium** ⭐ |
| Solution 1 + 3 Combined | 20 | 4-8s | Medium ⭐⭐⭐ |

---

## 🚀 Quick Win: Implement Solution 1 Now

**Easiest to implement, biggest impact:**

1. Add price caching (4-5 second TTL)
2. Reduces API calls by 67%
3. Still checks positions every 4-5 seconds
4. 5 minutes to implement

**Want me to implement this?** I can add it to your bot right now.
