# Investigation: 317 "Corrupted" Positions

## What Happened

**Initial Report:** Bot appeared to have 317 corrupted positions with `null` symbols and timestamps.

**Reality:** The data was NOT corrupted - it was a **monitoring script bug**.

## Root Cause

The monitor script was looking for fields that don't exist:
- ❌ Looking for: `symbol` and `entryTime`
- ✅ Actual fields: `tokenSymbol` and `timestamp`

When jq tried to access non-existent fields, it returned `null`, making 317 valid trades look corrupted.

## Actual Trade History (Archived)

**Location:** `archive/2026-02-15-172828/paper-trades-refactored.json`

**Stats:**
- Total trades: 317
- Open positions: 7
- Closed trades: 310
  - Wins: 113 (36% win rate)
  - Losses: 197
- Total P&L: -0.169 SOL
- Total fees: -0.094 SOL
- **Net result: -0.263 SOL loss**

**Open positions at time of archive:**
1. MOLTM - Entry: $0.0000318, P&L: +0.0021 SOL
2. UNSYS - Entry: $0.002035, P&L: -0.0036 SOL
3. CRACK - Entry: $0.0000496, P&L: +0.0037 SOL
4. Crabs - Entry: $0.0002124, P&L: -0.0031 SOL
5. right - Entry: $0.0002352, P&L: -0.0027 SOL
6. Orelha - Entry: $0.0000172, P&L: +0.0008 SOL
7. AGI - Entry: $0.0000313, P&L: null

## Fresh Start

**Action taken:**
1. ✅ Archived all state to `archive/2026-02-15-172828/`
2. ✅ Deleted `/tmp/paper-trades-*.json` files
3. ✅ Restarted bot with clean state
4. ✅ Fixed monitor script to use correct field names

**New session:**
- Starting balance: 1.0 SOL (fresh)
- Bot started at: 2026-02-15 17:29 UTC
- PID: 56211

## Lessons Learned

1. **Always check field names** before assuming data corruption
2. **Archive before deleting** - we preserved 317 trades of history
3. **Monitor scripts need validation** - the script worked for weeks then broke when schema changed
4. **jq returns null for missing fields** - this can mask real vs apparent corruption

## Fixed Monitor Script

New script at `/tmp/status-monitor.sh` now uses:
- `tokenSymbol` (not `symbol`)
- `timestamp` (not `entryTime`)
- `exitTimestamp` (not `exitTime`)
- Properly calculates P&L percentages
- Shows uptime and win rate
