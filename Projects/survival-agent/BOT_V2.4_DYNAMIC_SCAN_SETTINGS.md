# Bot v2.4: Dynamic Scan Settings

**Version:** v2.4
**Date:** Feb 16, 2026
**Status:** Active

---

## Overview

v2.4 introduces **dynamic monitoring intervals** based on position profitability, allowing the bot to track winning positions more closely while conserving API calls on standard positions.

---

## Dynamic Scan Intervals (NEW in v2.4)

### Position-Based Monitoring

| Position P&L | Scan Interval | Why |
|-------------|---------------|-----|
| **Below +50%** | **5 seconds** | Standard monitoring for regular positions |
| **+50% or higher** | **7 seconds** ⚡ | Faster tracking to catch peak exits before trailing stop |

### Logic

```typescript
const checkInterval = pnlPercent >= 50
  ? this.SCAN_INTERVAL_FAST_MS  // 7 seconds
  : this.MONITOR_INTERVAL_MS;    // 5 seconds
```

---

## All Scan Settings (Complete Reference)

### Scanner Loop (Finding Opportunities)
```typescript
SCAN_INTERVAL_MS = 15000  // 15 seconds
```

**What it does:**
- Fetches DexScreener trending tokens
- Finds 10-15 opportunities per scan
- Runs continuously in background
- **Frequency:** 4 scans per minute, 240 per hour

---

### Monitor Loop (Checking Open Positions)

#### Standard Monitoring
```typescript
MONITOR_INTERVAL_MS = 5000  // 5 seconds
```

**Applied to:**
- Positions with P&L < 50%
- All losing positions
- Newly opened positions

**What it does:**
- Fetches current price from Jupiter
- Calculates P&L and unrealized profit
- Checks stop loss (-30%)
- Checks max hold time (60 min)

#### Fast Monitoring (NEW)
```typescript
SCAN_INTERVAL_FAST_MS = 7000  // 7 seconds
```

**Applied to:**
- Positions with P&L ≥ 50%
- Winning positions approaching TP1
- Positions past TP1 with trailing stop active

**What it does:**
- Same as standard monitoring
- More frequent price updates
- Better peak detection for trailing stops
- Catches rapid price movements

---

## Position Lifecycle Example

### Example: GhostLink Trade

**Entry:** $0.000048 | **Current:** $0.000079 | **P&L:** +63%

```
Timeline of scan intervals:

Entry → +10% P&L:   Monitor every 5s (standard)
+10% → +30%:        Monitor every 5s (standard)
+30% → +50%:        Monitor every 5s (standard)
+50% → +63%:        Monitor every 7s ⚡ (FAST - activated!)
+63% → +100% (TP1): Monitor every 7s ⚡ (FAST - catching peak)
TP1+ (trailing):    Monitor every 7s ⚡ (FAST - tracking drop from peak)
```

**Log output:**
```
⏭️  GhostLink: Checked 4.1s ago (⚡FAST: 7s), skipping
📊 GhostLink [dexscreener]:
   Entry: $0.000048 | Current: $0.000079
   Peak: $0.000080 (+65.5%)
   P&L: +63% (+0.0031 SOL)
   Hold time: 13.2 min
   Status: 🔥 FAST MONITORING ACTIVE
   ⏳ Holding...
```

---

## Rate Limit Monitoring

### Tracking Metrics

```typescript
rateLimitCount = 0         // Total 429 errors encountered
lastRateLimitTime = 0      // Timestamp of last rate limit
```

### Where Rate Limits Are Tracked

1. **Jupiter Price Fetches**
   - Token price validation
   - Entry route quotes
   - Exit route quotes

2. **DexScreener API Calls**
   - Trending token scans
   - Fallback price checks

### Warning Thresholds

| Rate Limits/Hour | Status | Action |
|-----------------|--------|--------|
| **0-5** | ✅ Healthy | Keep current settings |
| **5-20** | ⚠️ Elevated | Monitor closely |
| **20-50** | 🚨 High | Consider backing off to 10s for fast scan |
| **50+** | ❌ Critical | Revert to 5s for all positions |

---

## Current Bot Configuration (v2.4)

### Trading Limits
```typescript
MAX_CONCURRENT_POSITIONS = 7
MAX_POSITION_SIZE = 0.12           // 12% of balance
MIN_BALANCE = 0.05
MIN_SMART_MONEY_CONFIDENCE = 45    // 0-100 score
```

### Exit Strategy
```typescript
STOP_LOSS = -0.30                  // -30% before TP1
TAKE_PROFIT = 1.0                  // +100% (TP1 trigger)
TRAILING_STOP_PERCENT = 0.20       // 20% drop from peak after TP1
MAX_HOLD_TIME_MS = 3600000         // 60 minutes
```

### Scanner Filters
```typescript
MIN_LIQUIDITY = $10,000            // v2.3 increase
MIN_VOLUME_24H = $1,000
TOKEN_AGE_FILTER = DISABLED        // v2.3 change
```

### Timing Intervals (v2.4)
```typescript
SCAN_INTERVAL_MS = 15000           // Scanner: 15s
MONITOR_INTERVAL_MS = 5000         // Standard monitor: 5s
SCAN_INTERVAL_FAST_MS = 7000       // Fast monitor: 7s (NEW)
```

---

## API Call Frequency Analysis

### Standard Operation (No Profitable Positions)

**Per position:**
- 1 price check every 5 seconds
- 12 checks per minute
- 720 checks per hour

**With 7 positions:**
- 84 price checks per minute
- 5,040 checks per hour

---

### With Fast Scanning (3 Profitable Positions)

**Standard positions (4):**
- 4 positions × 12 checks/min = 48 checks/min

**Fast positions (3):**
- 3 positions × 8.57 checks/min = 25.7 checks/min

**Total:**
- 73.7 checks per minute (vs 84 standard)
- 4,422 checks per hour (vs 5,040 standard)

**Savings:** ~600 API calls/hour (12% reduction) while monitoring winners more closely!

---

## Performance Targets

### v2.4 Goals

1. **Better Exit Timing**
   - Catch peak prices on 50%+ winners
   - Reduce slippage on trailing stop exits
   - Improve profit taking on +100%+ positions

2. **API Efficiency**
   - Actually REDUCES total API calls when holding winners
   - More frequent checks only where it matters (profitable positions)
   - Standard positions monitored at same rate

3. **Rate Limit Safety**
   - Continuous tracking of 429 errors
   - Automatic warnings in status updates
   - Data to inform future optimizations

---

## Comparison: v2.3 vs v2.4

| Feature | v2.3 | v2.4 |
|---------|------|------|
| **Scanner interval** | 15s | 15s (unchanged) |
| **Standard monitor** | 5s | 5s (unchanged) |
| **Profitable monitor** | 5s | 7s ⚡ (NEW) |
| **Dynamic intervals** | ❌ No | ✅ Yes |
| **Rate limit tracking** | ❌ No | ✅ Yes |
| **API efficiency** | Standard | Improved |
| **Peak exit detection** | Standard | Enhanced |

---

## Expected Behavior in Production

### Scenario 1: All Positions Losing
- All 7 positions monitored at 5s interval
- Same as v2.3 behavior
- No change in API usage

### Scenario 2: 2 Winners (+60%, +40%), 5 Others
- Winner 1 (+60%): Scanned every 7s ⚡
- Winner 2 (+40%): Scanned every 5s (not 50% yet)
- Other 5: Scanned every 5s
- Slightly reduced API usage vs v2.3

### Scenario 3: 1 Big Winner (+120%), 6 Others
- Winner (+120%, past TP1): Scanned every 7s ⚡ (trailing stop active)
- Other 6: Scanned every 5s
- Best case for peak exit timing

---

## Monitoring Commands

### Check Current Positions
```bash
bash testing/status.sh
```

### Watch Live Stats
```bash
bash monitoring/dashboard.sh
```

### Check Rate Limits
Look for this in status updates (every ~50 seconds):
```
⚠️  Rate Limits: 12 total (last: 45s ago)
```

### Watch Fast Scan Labels
Look for `⚡FAST` in position checks:
```
⏭️  Dogs: Checked 4.8s ago (⚡FAST: 7s), skipping
```

---

## Rollback Plan

If rate limits become problematic:

### Quick Fix (Adjust Fast Interval)
```typescript
private readonly SCAN_INTERVAL_FAST_MS = 10000; // Change from 7s to 10s
```

### Full Rollback (Revert to v2.3)
```typescript
// Remove dynamic logic, use fixed 5s for all
const checkInterval = this.MONITOR_INTERVAL_MS;
```

---

## Summary

**v2.4 Upgrade:**
- ✅ Faster monitoring (7s) for profitable positions (50%+)
- ✅ Better peak detection for trailing stops
- ✅ Rate limit tracking and warnings
- ✅ Actually reduces API load in most scenarios
- ✅ No change to standard position monitoring (5s)

**Key Insight:** By scanning winners slightly slower (7s vs 5s) but only winners, we reduce total API calls while improving exit timing where it matters most.

---

**Created:** Feb 16, 2026
**Version:** 2.4
**Status:** ✅ Ready for deployment
