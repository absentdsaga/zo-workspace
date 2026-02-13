# Survival Agent - Project State Tracker

**Last Updated:** 2026-02-12 23:43 UTC

## 🎯 SINGLE SOURCE OF TRUTH

### Active Files (DO NOT CREATE ALTERNATIVES)
- **Main Bot**: `testing/paper-trade-bot.ts` (THE ONLY BOT)
  - Never create: paper-trade-master.ts, paper-trade-v2.ts, etc.
  - Any changes go HERE
  
- **Trades File**: `/tmp/paper-trades-master.json`
  - Bot writes here
  - Status monitor reads from here
  - Never use: /tmp/paper-trades.json

- **Shocked Watchlist**: `/tmp/shocked-watchlist.json`
  - Format: Map-compatible array with [address, ShockedCall object]
  - Timestamps must be current (Date.now() in milliseconds)

- **Status Monitor**: `/tmp/paper-bot-status.sh`
  - Must read from TRADES_FILE path in bot

### Start Script
```bash
cd /home/workspace/Projects/survival-agent
source ~/.zo_secrets
nohup bun run testing/paper-trade-bot.ts > /tmp/paper-trade.log 2>&1 &
```

### Stop Script
```bash
pkill -f "paper-trade-bot.ts"
```

### Monitor Commands
```bash
# Live dashboard
watch -n 2 /tmp/paper-bot-status.sh

# Token details
bun monitoring/token-monitor.ts

# Live logs
tail -f /tmp/paper-trade.log
```

## 📋 BEFORE MAKING CHANGES CHECKLIST

### 1. Check Current State
```bash
# Is bot running?
ps aux | grep paper-trade-bot.ts | grep -v grep

# What trades are open?
cat /tmp/paper-trades-master.json | jq '.trades[] | select(.status=="open") | {symbol, pnl}'

# Backup current config
cp testing/paper-trade-bot.ts testing/paper-trade-bot.ts.backup-YYYY-MM-DD-REASON
```

### 2. Make Changes
- Edit ONLY `testing/paper-trade-bot.ts`
- Test compilation: `bun run --dry-run testing/paper-trade-bot.ts`

### 3. Restart Safely
```bash
# Stop bot
pkill -f "paper-trade-bot.ts"

# Verify trades file exists and has open positions
cat /tmp/paper-trades-master.json

# Start bot (it will load existing trades)
cd /home/workspace/Projects/survival-agent
source ~/.zo_secrets
nohup bun run testing/paper-trade-bot.ts > /tmp/paper-trade.log 2>&1 &

# Verify it loaded trades
sleep 3 && tail -20 /tmp/paper-trade.log | grep "Loaded.*trades"
```

## 🚨 CRITICAL RULES

### Never:
1. Create alternative bot files (v2, master, fixed, etc.)
2. Overwrite trades file with empty state
3. Restart without checking open positions
4. Use relative paths in scripts
5. Make multiple changes at once without testing

### Always:
1. Backup before changes
2. Check what's currently running/open
3. Verify file paths match between bot and monitors
4. Test compilation before restart
5. Verify trades loaded after restart

## 📊 Current Configuration (v2.0)

### Position Sizing
- Max position: 12% of balance
- Max concurrent: 10 positions

### Exit Rules
- TP1 threshold: +100% (activates trailing stop)
- Trailing stop: 20% from peak (after TP1)
- Stop loss: -30% (before TP1)
- Max hold: 60 minutes

### Entry Filters
- Min score: 40
- Min shocked score: 30
- Min smart money confidence: 45
- **EXCLUDED**: dexscreener-only signals

### Sources
1. Pump.fun (new launches)
2. DexScreener (smart money)
3. Shocked watchlist (Discord calls)

## 🔍 Debug Commands

### Check Scanner Health
```bash
tail -100 /tmp/paper-trade.log | grep -E "Shocked scanner|qualified after filters|EXECUTING"
```

### Check File Consistency
```bash
# Bot's file path
grep "TRADES_FILE" testing/paper-trade-bot.ts

# Monitor's file path
grep "TRADES_FILE" /tmp/paper-bot-status.sh

# They MUST match!
```

### Verify Shocked Watchlist Format
```bash
cat /tmp/shocked-watchlist.json | jq '.[0]'
# Should show: [address, {object with addedAt, priority, etc}]
```

## 📝 Change Log

### 2026-02-12 v2.0
- Increased position size: 10% → 12%
- Excluded dexscreener-only signals
- Added trailing stop after +100%
- Reset stats to track v2.0 performance

### Issues Fixed Tonight
- saveTrades() now writes complete state (balance, totalPnl, trades)
- Status monitor points to correct file
- Shocked watchlist timestamps refreshed
- Debug logging added for scanner

## 🎯 Recovery Procedures

### If Trades Lost
1. Check `/tmp/paper-trades-master.json` timestamp
2. Look for backups: `ls -lht testing/*.backup*`
3. Reconstruct from logs: `grep "EXECUTING\|Position closed" /tmp/paper-trade.log`

### If Bot Not Trading
1. Check Shocked scanner: "📡 Shocked scanner: X opportunities found"
2. Check validity: "✅ Valid shocked: X"
3. If 0 valid, check timestamps in watchlist (must be < 24h old)

### If Monitor Shows Wrong Data
1. Check file path: `grep TRADES_FILE /tmp/paper-bot-status.sh`
2. Compare to bot: `grep TRADES_FILE testing/paper-trade-bot.ts`
3. Update monitor if different

## 🧹 Cleanup Log

### 2026-02-12 23:44 - Removed Alternative Bot Files
**Problem:** Multiple bot files existed causing confusion
**Action:** Moved to archive:
- `paper-trade-master.ts` → `archive/`
- `paper-trade-master-fixed.ts` → `archive/`
- `paper-trade-simple.ts` → `archive/`

**Result:** Only `testing/paper-trade-bot.ts` remains active

### Verification Command
```bash
./scripts/verify-state.sh
```
Run this BEFORE making any changes to check current state.
