# Bot Restart - New Age Filter Settings

**Restart Time:** 2026-02-16 04:21:25 AM UTC

---

## Changes Applied

### Age Filter Updated (meme-scanner.ts line 115-118)

**BEFORE (60 minutes - too restrictive):**
```typescript
// Filter: Skip old tokens (>60 min for fresh launches)
if (ageMinutes > 60) {
  continue; // Only analyze tokens less than 60 minutes old
}
```

**AFTER (1440 minutes / 24 hours - matching Archive Master logic):**
```typescript
// Filter: Skip very old tokens (>24h) if age is known
if (ageMinutes !== 999 && ageMinutes > 1440) {
  continue; // Skip tokens older than 24 hours (allows unknown age like Archive Master)
}
```

---

## What This Changes

### ✅ Now Allows:
1. **Unknown age (999)** - Archive Master had all undefined ages and made +626%
2. **0-24h tokens** - Fresh enough to catch pumps, more opportunities
3. **Larger pool of tokens** - More trades with good quality

### ❌ Now Filters:
1. **>24h old tokens** - Blocks 4-6 day old garbage that was getting through
2. **Obvious stale tokens** - Past their pump phase

---

## Bot State at Restart

**Balance:** 0.2418 SOL (from 0.5 starting)
**Open Positions:** 7 positions
**Previous performance:** -54% return (losing run)

**Bot PID:** 13356
**Status:** 🟢 Running

---

## Expected Impact

### Compared to 60-minute filter:
- **More trades** - Larger opportunity pool (0-24h vs 0-60min)
- **Better win rate** - Archive Master had no age filter and achieved 38.9% win rate
- **Still filters trash** - Blocks the 4-6 day old tokens that destroyed current run

### Key Insight:
Archive Master (626% return) had **NO age filtering** (all ages undefined).

The 60-minute filter was **TOO RESTRICTIVE** compared to what actually worked.

The 1440-minute (24h) filter is a **middle ground**:
- Less restrictive than 60 min (more opportunities)
- More restrictive than none (blocks stale tokens)
- Matches the original broken code's INTENT

---

## Next Steps to Match Archive Master Performance

### ✅ COMPLETED:
1. Age filter fixed (60 min → 1440 min)

### 🔄 REMAINING:
1. **Remove subagent/shocked sources** (if present)
   - Archive Master: 3 sources → +626%
   - Archive Refactored: 5 sources (added subagent/shocked) → -17%
   - Subagent had 6.7% win rate and cost -1.59 SOL!

2. **Blacklist TRUMP2 and repeat losers**
   - TRUMP2: 6 losses, -0.115 SOL
   - FIREHORSE: 2 losses, -0.023 SOL
   - Without TRUMP2: Win rate would be 41.7% vs current 26.1%

3. **Revert position size 12% → 10%**
   - Archive Master used 10%
   - Current 12% is too aggressive

4. **Reset to 0.5 SOL starting balance** (optional)
   - Current: 0.242 SOL (depleted)
   - Archive: 0.5 SOL starting
   - Larger positions = larger wins

5. **KEEP current stop loss execution**
   - Your avg loss: -13 mSOL (55% better than Archive's -29 mSOL!)

---

## Expected Results After All Fixes

### If win rate returns to Archive Master level:
```
Win rate: 38.9% (fix scanner quality)
Avg win: +74 mSOL (with 0.5 SOL reset)
Avg loss: -13 mSOL (KEEP your execution - it's better!)
Ratio: 5.69x (74 / 13)

Per-trade EV: +20.06 mSOL
Over 288 trades: +5.78 SOL (+1,156% return!)
```

**Potential to DOUBLE Archive Master's 626% return with your better stop execution.**

---

## Monitoring

**Check bot status:**
```bash
ps aux | grep paper-trade-bot.ts | grep -v grep
```

**View live log:**
```bash
tail -f /tmp/paper-trade.log
```

**Check positions:**
```bash
cat /tmp/paper-trades-master.json | jq '.trades[] | select(.status=="open") | {symbol, pnl}'
```

---

## Files Modified

1. `/home/workspace/Projects/survival-agent/strategies/meme-scanner.ts` - Age filter updated

---

**Status:** Bot restarted with 24h age filter ✅

**Next priority:** Remove subagent/shocked sources and blacklist TRUMP2
