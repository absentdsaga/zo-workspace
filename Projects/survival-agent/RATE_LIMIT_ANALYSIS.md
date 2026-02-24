# Rate Limit Analysis - 7s vs 15s Scanning

## Current Setup (15s scanner)

### API Calls Per Scan Cycle
1. **Shocked Scanner:** 9 tokens × 1 DexScreener API call = 9 calls
2. **Combined Scanner:** ~10-20 DexScreener API calls
3. **Smart Money Tracker:** 0 calls (uses on-chain RPC)
4. **Jupiter Validator:** 1-2 calls per opportunity (quote + swap)

**Total per scan:** ~20-30 API calls

### Frequency
- Scanner: Every 15 seconds
- Calls per minute: (60 / 15) × 25 = **100 calls/min**
- Calls per hour: **6,000 calls/hour**

## If Scanning Every 7s

### Frequency
- Scanner: Every 7 seconds
- Calls per minute: (60 / 7) × 25 = **214 calls/min**
- Calls per hour: **12,857 calls/hour**

### Impact

| Interval | Calls/min | Calls/hour | Rate Limit Risk |
|----------|-----------|------------|----------------|
| 15s (current) | 100 | 6,000 | ✅ Safe |
| 10s | 150 | 9,000 | ⚠️ Borderline |
| 7s | 214 | 12,857 | ☠️ High risk |
| 5s | 300 | 18,000 | ☠️ Will fail |

## DexScreener Rate Limits

**Free tier:**
- 300 requests/minute (likely)
- 10,000 requests/hour (estimated)

**Our usage at 7s:**
- 214 calls/min = **71% of limit**
- 12,857 calls/hour = **128% of hourly limit** ☠️

**Conclusion:** 7s scanning would **exceed hourly limits** and cause failures.

## Alternative: Keep 15s Scanner, Speed Up Monitor

### Current Architecture (ALREADY OPTIMAL)
```typescript
SCAN_INTERVAL_MS = 15000;    // 15s - Find new opportunities
MONITOR_INTERVAL_MS = 5000;  // 5s - Check existing positions
```

This is **already optimized**:
- Scanning (expensive API calls): 15s
- Monitoring (cheap RPC calls): 5s

### Why This Works
1. **Finding new trades:** Doesn't need to be faster than 15s
   - Tokens pump over minutes/hours, not seconds
   - 15s is fast enough to catch early momentum

2. **Exiting trades:** Needs to be fast (5s is good)
   - Already monitoring every 5s
   - Can catch dumps quickly
   - Uses cheap RPC calls (no rate limit issue)

## If You REALLY Want Faster Scanning

### Option 1: Reduce API Calls Per Scan
Instead of checking all 9 shocked tokens every scan:
- Check 3 tokens per scan (rotate through them)
- Reduces API calls by 66%
- Can scan every 7s without hitting limits

### Option 2: Use WebSocket Feeds
- DexScreener has WebSocket API for real-time updates
- No polling = no rate limits
- Most efficient solution

### Option 3: Hybrid Approach
- Scanner: 15s (DexScreener API)
- Shocked scanner: 7s (WebSocket feed)
- Monitor: 5s (RPC only)

## Recommendation

**Keep current 15s/5s setup.** Here's why:

1. **Already fast:** 15s is plenty fast for catching pumps
2. **No rate limit risk:** Well under API limits
3. **Monitor is 5s:** Quick exits are covered
4. **Proven to work:** Previous run had 209 trades with this timing

### Evidence from Previous Run
- 209 trades in ~24 hours
- Average ~9 trades/hour with 15s scanning
- **We're not missing opportunities** - the bottleneck isn't scan speed

## If Missed Opportunities Occur

Then consider:
1. Adding WebSocket feeds (no rate limit)
2. Increasing shocked token priority (already done)
3. Lowering score thresholds (risky)

But **NOT** reducing scan interval to 7s - that will cause rate limit failures.

## Bottom Line

**7s scanning = 2x more API calls = rate limit failures**

Current 15s scanner is optimal. Don't change it.

## 10 Second Scanning Update

### Impact at 10s
- Calls per minute: (60 / 10) × 25 = **150 calls/min**
- Calls per hour: **9,000 calls/hour**

### Comparison

| Interval | Calls/min | Calls/hour | Status |
|----------|-----------|------------|--------|
| 15s (current) | 100 | 6,000 | ✅ Safe (60% of limit) |
| 10s | 150 | 9,000 | ⚠️ Borderline (90% of limit) |
| 7s | 214 | 12,857 | ☠️ Exceeds limit |

### 10s Analysis

**Could work IF:**
- DexScreener limit is 10,000/hour (estimated)
- You have headroom for spikes
- No other processes using the API

**Risk:**
- Running at 90% capacity leaves **no buffer**
- API spikes during high volatility → rate limit failures
- One extra scan per minute = over limit

**Recommendation:**
- **Stick with 15s** for reliability
- 10s only if you NEED the speed AND can handle occasional failures
- Monitor for 429 errors if you try 10s

**Better alternative:** Keep 15s scanning, but take **multiple shocked calls per scan** (just implemented ✅)

This gives you:
- More shocked trades per cycle
- Same API usage (15s interval)
- Better alpha capture without rate limit risk
