# Fast Scan Upgrade for Profitable Positions

**Version:** v2.3.1
**Date:** Feb 16, 2026
**Bot Version:** v2.3 (with fast scan enhancement)

---

## What Changed

### Dynamic Monitoring Intervals

**Before:**
- All positions monitored every 5 seconds (fixed interval)

**After:**
- **Standard positions**: 5 seconds (unchanged)
- **Profitable positions (50%+ P&L)**: 7 seconds (faster scanning)

### Rationale

Positions at +50% or higher are in the profit zone where:
1. **Peak timing matters** - Need to catch the optimal exit before trailing stop triggers
2. **Still trending** - These tokens are actively being traded (100% scan rate in DexScreener)
3. **Momentum is strong** - Price can move quickly in either direction

By checking them every 7 seconds instead of 5 seconds, we get more frequent price updates to better time the trailing stop exits.

---

## Rate Limit Monitoring

Added tracking to detect if faster scanning causes issues:

```typescript
private rateLimitCount = 0;        // Track 429 rate limits
private lastRateLimitTime = 0;     // Last time we hit rate limit
```

**Where it's tracked:**
- Jupiter price fetches (429 errors)
- DexScreener API calls (rate limit errors)
- Logged in status updates every ~50 seconds

**What to watch for:**
- If `rateLimitCount` increases rapidly → back off to 5s for all positions
- If no rate limits observed → can potentially go faster (5s for 50%+ positions)

---

## Implementation Details

### Code Changes

**1. New constant:**
```typescript
private readonly SCAN_INTERVAL_FAST_MS = 7000; // 7 seconds for 50%+ positions
```

**2. Dynamic interval logic:**
```typescript
// Use faster interval for profitable positions
const checkInterval = pnlPercent >= 50
  ? this.SCAN_INTERVAL_FAST_MS
  : this.MONITOR_INTERVAL_MS;
```

**3. Rate limit tracking:**
```typescript
catch (error: any) {
  if (error?.message?.includes('429') || error?.message?.includes('Rate limit')) {
    this.rateLimitCount++;
    this.lastRateLimitTime = Date.now();
    console.log(`   ⚠️  Rate limited (total: ${this.rateLimitCount})`);
  }
}
```

**4. Status reporting:**
```typescript
if (this.rateLimitCount > 0) {
  const timeSinceLastLimit = (Date.now() - this.lastRateLimitTime) / 1000;
  console.log(`⚠️  Rate Limits: ${this.rateLimitCount} total (last: ${timeSinceLastLimit.toFixed(0)}s ago)`);
}
```

---

## Expected Behavior

### Normal Operation (No Rate Limits)

**Position at +35%:**
```
⏭️  Dogs: Checked 3.2s ago (normal: 5s), skipping
```

**Position at +63%:**
```
⏭️  GhostLink: Checked 4.1s ago (⚡FAST: 7s), skipping
```

### With Rate Limits

**Status update shows:**
```
⚠️  Rate Limits: 12 total (last: 45s ago)
```

**In monitoring log:**
```
⚠️  Rate limited (total: 12)
ℹ️  Using DexScreener fallback price: $0.00007944
```

---

## Decision Points

### If Rate Limits Stay Low (<5 per hour)
✅ **Keep fast scanning at 7s** - System can handle it

### If Rate Limits Increase (>20 per hour)
⚠️ **Consider adjustment:**
- Option 1: Keep 7s for 50%+, add backoff after rate limit
- Option 2: Increase to 10s for 50%+ positions
- Option 3: Revert to 5s for all positions

### If Rate Limits Spike (>50 per hour)
❌ **Revert immediately** - Too aggressive

---

## Testing Plan

1. **Monitor for 1 hour** with current bot run
2. **Check rate limit count** in status updates
3. **Watch for:**
   - Positions hitting 50%+ and getting ⚡FAST label
   - Any increase in rate limit errors
   - Whether fast scanning helps catch better exits

---

## Rollback Instructions

If rate limits become problematic:

```typescript
// Revert to fixed 5s interval for all positions
const checkInterval = this.MONITOR_INTERVAL_MS; // Remove dynamic logic
```

---

## Current Status

**Bot:** Running (PID 851)
**Positions:** 6/7 open
- GhostLink: +63% (will use 7s fast scan)
- Dogs: +35% (will use 5s standard scan)

**Rate Limits:** 0 (baseline - will track from this point)

---

**Created:** Feb 16, 2026, 7:30 PM
**Status:** ✅ Implemented, monitoring for rate limit impact
**Next Review:** After 1 hour of operation
