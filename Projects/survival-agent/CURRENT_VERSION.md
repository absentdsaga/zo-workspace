# Current Bot Version

**Version:** v2.4
**Date:** Feb 16, 2026
**Status:** Active (needs restart to activate)

---

## What's New in v2.4

### Dynamic Fast Scanning for Profitable Positions

Positions at +50% or higher P&L are now monitored every **7 seconds** (vs 5 seconds standard) to better catch peak prices for trailing stop exits.

---

## Complete Settings (v2.4)

### Trading Parameters
- **Position size:** 12% of balance (0.06 SOL starting)
- **Max positions:** 7 concurrent
- **Min confidence:** 45/100
- **Stop loss:** -30% (before TP1)
- **Take profit:** +100% (TP1 - activates trailing stop)
- **Trailing stop:** 20% drop from peak (after TP1)
- **Max hold time:** 60 minutes

### Scanner Settings
- **Min liquidity:** $10,000
- **Min volume 24h:** $1,000
- **Token age filter:** DISABLED

### Dynamic Scan Intervals (NEW)
- **Scanner:** 15 seconds (find opportunities)
- **Standard monitor:** 5 seconds (positions < 50% P&L)
- **Fast monitor:** 7 seconds ⚡ (positions ≥ 50% P&L)

### Rate Limit Monitoring (NEW)
- Tracks 429 errors from Jupiter and DexScreener
- Reports total count and time since last limit
- Displayed in status updates every ~50 seconds

---

## Version History

### v2.4 (Current)
- ✅ Dynamic fast scanning (7s for 50%+ positions)
- ✅ Rate limit tracking and monitoring
- ✅ Improved peak detection for trailing stops

### v2.3
- ✅ MIN_LIQUIDITY raised to $10k
- ✅ Age filter disabled

### v2.2
- ✅ Real executor integration
- ✅ Fee tracking (Jito + priority fees)
- ✅ Multiple shocked calls

### v2.1
- ✅ 3-loss blacklist system
- ✅ Auto-blacklist repeat losers

### v2.0
- ✅ Dual-loop architecture
- ✅ Trailing stops after TP1
- ✅ Source tracking

---

## Git Version Analysis

**Last verified:** Feb 16, 2026

The git-tracked version has:
- Position size: 12% ✅ (matches current)
- Stop loss: -30% ✅ (matches current)
- TP1: +100% ✅ (matches current)
- Trailing stop: 20% ✅ (matches current)
- Min liquidity: $2k ❌ (current: $10k)
- Age filter: ENABLED ❌ (current: DISABLED)
- Dynamic scanning: NO ❌ (current: YES - v2.4)

---

## Files Changed in v2.4

### `testing/paper-trade-bot.ts`
- Added `SCAN_INTERVAL_FAST_MS = 7000`
- Added `rateLimitCount` and `lastRateLimitTime` tracking
- Updated monitoring loop with dynamic interval logic
- Added rate limit detection in price fetches
- Updated startup messages to show fast scan feature

### `monitoring/dashboard.sh`
- Fixed regex to capture mixed-case token names
- Now shows GhostLink and other CamelCase tokens

### Documentation
- Created `BOT_V2.4_DYNAMIC_SCAN_SETTINGS.md`
- Updated `CURRENT_VERSION.md` (this file)
- Created `FAST_SCAN_UPGRADE.md`

---

## Activation Status

**Code:** ✅ Updated to v2.4
**Running:** ❌ Needs restart with environment variables
**Testing:** ⏳ Pending restart

---

**Last Updated:** Feb 16, 2026, 7:40 PM
