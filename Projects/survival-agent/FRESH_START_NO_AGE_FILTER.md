# Fresh Start - No Age Filter (Archive Master Replication)

**Reset Time:** 2026-02-16 04:30:09 AM UTC
**Bot PID:** 18779

---

## Changes Applied

### 1. Age Filter REMOVED ✅

**Changed in:** `strategies/meme-scanner.ts` line 115-117

**BEFORE (24h filter):**
```typescript
// Filter: Skip very old tokens (>24h) if age is known
if (ageMinutes !== 999 && ageMinutes > 1440) {
  continue;
}
```

**AFTER (NO filter - Archive Master replication):**
```typescript
// Filter: NO AGE FILTERING - replicate Archive Master exactly
// Archive Master (626% profit) had no age filtering and included all tokens
// (The old broken code never filtered anything)
```

**Reasoning:**
- Archive Master (626%) had broken age filter that NEVER filtered anything
- The condition `(age < 999 && age > 1440)` is mathematically impossible
- Archive Master included ALL tokens: 0 min, 60 min, 24h, 4-6 days, everything
- We're now exactly replicating that behavior

---

### 2. Complete Stats Reset ✅

**Backed up old data to:**
- `/tmp/paper-trades-backup-before-reset-20260216_043009.json`
- `/tmp/paper-trades-state-backup-before-reset-20260216_043009.json`

**Reset to:**
```json
{
  "startingBalance": 0.5,
  "currentBalance": 0.5,
  "totalRefills": 0,
  "trades": []
}
```

**Previous run stats (before reset):**
- Balance: 0.2418 SOL (depleted)
- P&L: -0.2582 SOL (-51.6%)
- Trades: 53
- Win Rate: 28.3%

---

## Current Bot Configuration

**Matching Archive Master settings:**

```typescript
MAX_POSITION_SIZE = 0.12;              // 12% (will change to 10%)
STOP_LOSS = -0.30;                     // -30%
TAKE_PROFIT = 1.0;                     // 100%
TRAILING_STOP_PERCENT = 0.20;          // 20% from peak
MAX_HOLD_TIME_MS = 60*60*1000;         // 60 minutes

JITO_TIP = 0.0002;                     // 0.0002 SOL
PRIORITY_FEE = 111000;                 // lamports

AGE_FILTER = NONE;                     // ✅ NO FILTERING (like Archive Master)
```

**Still needs:**
- ❌ Position size: 12% → 10%
- ❌ Remove subagent/shocked sources (if present)
- ❌ Add TRUMP2 blacklist

---

## What This Means

### Archive Master Behavior (626% profit):
The old broken code looked like this:
```typescript
if (ageMinutes < 999 && ageMinutes > 1440) {
  continue; // Skip token
}
```

**This NEVER filtered anything because:**
- A number can't be both <999 AND >1440 (impossible condition)
- Result: ALL tokens were included

**Archive Master included:**
- ✅ Tokens with no creation date (age = 999)
- ✅ Fresh tokens (0-60 min)
- ✅ Older tokens (60-1440 min / 0-24h)
- ✅ Stale tokens (>1440 min / >24h)
- ✅ Even 4-6 day old tokens

**And it still made 626% profit.**

---

## Our Current Approach

**We're now doing EXACTLY what Archive Master did:**
- No age filtering at all
- Include ALL tokens from scanner
- Let confidence scoring and other filters do the work

**Differences from Archive Master:**
- We still have subagent/shocked sources (need to remove)
- We have 12% position sizing (need to change to 10%)
- We have better stop loss execution (-13 mSOL vs -29 mSOL)

---

## Expected Behavior

**With no age filter, scanner will find:**
- Very fresh tokens (0-60 min) ✅
- Somewhat fresh tokens (1-24h) ✅
- Older tokens (>24h) ✅
- Unknown age tokens ✅

**Quality control will come from:**
1. Confidence scoring (min 60 score)
2. Liquidity requirements ($2k min)
3. Volume requirements ($1k/day min)
4. Smart money validation (if enabled)

**NOT from age filtering.**

---

## Monitoring

**Bot Status:**
```bash
ps aux | grep paper-trade-bot.ts | grep -v grep
```

**Live Log:**
```bash
tail -f /tmp/paper-trade.log
```

**Current Positions:**
```bash
cat /tmp/paper-trades-master.json | jq '.trades[] | select(.status=="open")'
```

---

## What We're Testing

**Hypothesis:**
Archive Master's 626% profit came from:
1. ✅ Simple sources (3 only: DexScreener, both, PumpFun)
2. ✅ No age filtering (included everything)
3. ✅ Good confidence scoring
4. ✅ 38.9% win rate from quality tokens

**NOT from:**
- ❌ Age filtering (it was broken/non-existent)
- ❌ Multiple sources (Refactored added subagent/shocked and LOST money)

**We're now testing:** Can we replicate 626% by matching Archive Master exactly (no age filter)?

---

## Next Steps

1. **Monitor for 24-48 hours** - See if win rate improves
2. **Remove subagent/shocked sources** - If they're present
3. **Add TRUMP2 blacklist** - Prevent repeat losing
4. **Change position 12% → 10%** - Match Archive Master
5. **Track win rate** - Target: 38%+

---

## Success Criteria

**If this works (matches Archive Master):**
- Win rate: 38%+ (from current 28%)
- Win/Loss ratio: 2.5x+ (from current 1.6x)
- Per-trade profit: +10 mSOL+ (from current -1.7 mSOL)
- Total P&L: Profitable over 100+ trades

**If this doesn't work:**
- Win rate stays <30%
- Ratio stays <2x
- Too many stale/bad tokens getting through

**Then we'll know:** Age filtering DOES matter (contrary to Archive Master data)

---

## Files Modified

1. `/home/workspace/Projects/survival-agent/strategies/meme-scanner.ts` - Age filter removed
2. `/tmp/paper-trades-master.json` - Reset to 0.5 SOL starting
3. `/tmp/paper-trades-state.json` - Reset to fresh state

---

**Status:** 🟢 Bot running with NO age filter (Archive Master replication)
**Starting Balance:** 0.5 SOL
**Bot PID:** 18779
