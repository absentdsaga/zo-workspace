#!/bin/bash

# Survival Agent State Verification Script
# Run this BEFORE making any changes to verify current state

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SURVIVAL AGENT - STATE VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if bot is running
echo "🤖 Bot Status:"
BOT_PID=$(ps aux | grep "paper-trade-bot.ts" | grep -v grep | awk '{print $2}')
if [ -n "$BOT_PID" ]; then
    echo "   ✅ Running (PID: $BOT_PID)"
else
    echo "   ❌ Not running"
fi
echo ""

# Check for alternative bot files (should NOT exist)
echo "📁 Bot File Check:"
BOT_FILES=$(find testing -name "paper-trade*.ts" 2>/dev/null | wc -l)
if [ $BOT_FILES -eq 1 ]; then
    echo "   ✅ Only ONE bot file exists"
    find testing -name "paper-trade*.ts"
else
    echo "   ⚠️  Multiple bot files found:"
    find testing -name "paper-trade*.ts"
fi
echo ""

# Check trades file
echo "💾 Trades File:"
if [ -f "/home/workspace/Projects/survival-agent/data/paper-trades-master.json" ]; then
    OPEN_COUNT=$(jq '.trades | map(select(.status=="open")) | length' /home/workspace/Projects/survival-agent/data/paper-trades-master.json 2>/dev/null)
    TOTAL_COUNT=$(jq '.trades | length' /home/workspace/Projects/survival-agent/data/paper-trades-master.json 2>/dev/null)
    BALANCE=$(jq -r '.balance' /home/workspace/Projects/survival-agent/data/paper-trades-master.json 2>/dev/null)
    echo "   ✅ File exists"
    echo "   📊 Open: $OPEN_COUNT | Total: $TOTAL_COUNT | Balance: $BALANCE SOL"
    
    # Show open positions
    if [ "$OPEN_COUNT" -gt 0 ]; then
        echo ""
        echo "   🔓 Open Positions:"
        jq -r '.trades[] | select(.status=="open") | "      \(.tokenSymbol): \(.pnl // 0 | tonumber) SOL"' /home/workspace/Projects/survival-agent/data/paper-trades-master.json 2>/dev/null
    fi
else
    echo "   ❌ File not found at /home/workspace/Projects/survival-agent/data/paper-trades-master.json"
fi
echo ""

# Check file path consistency
echo "🔍 File Path Consistency:"
BOT_PATH=$(grep "TRADES_FILE" testing/paper-trade-bot.ts | head -1 | sed "s/.*= '//;s/'.*//")
MONITOR_PATH=$(grep "TRADES_FILE=" /tmp/paper-bot-status.sh 2>/dev/null | sed 's/.*="\(.*\)"/\1/')

echo "   Bot writes to:     $BOT_PATH"
echo "   Monitor reads from: $MONITOR_PATH"

if [ "$BOT_PATH" = "$MONITOR_PATH" ]; then
    echo "   ✅ Paths match"
else
    echo "   ❌ MISMATCH! Fix before continuing"
fi
echo ""

# Check Shocked watchlist
echo "📡 Shocked Watchlist:"
if [ -f "/tmp/shocked-watchlist.json" ]; then
    COUNT=$(jq '. | length' /tmp/shocked-watchlist.json 2>/dev/null)
    echo "   ✅ $COUNT tokens in watchlist"
    
    # Check if any are too old (>23 hours)
    NOW=$(date +%s)000
    OLD_COUNT=$(jq --argjson now "$NOW" '
        [.[] | select((($now - .[1].addedAt) / 1000 / 3600) > 23)] | length
    ' /tmp/shocked-watchlist.json 2>/dev/null)
    
    if [ "$OLD_COUNT" -gt 0 ]; then
        echo "   ⚠️  $OLD_COUNT tokens are >23 hours old (will be inactive soon)"
    fi
else
    echo "   ❌ Watchlist not found"
fi
echo ""

# Check recent backups
echo "💾 Recent Backups:"
BACKUP_COUNT=$(find testing -name "*.backup*" -mtime -1 2>/dev/null | wc -l)
if [ $BACKUP_COUNT -gt 0 ]; then
    echo "   ✅ $BACKUP_COUNT backup(s) from last 24h:"
    find testing -name "*.backup*" -mtime -1 -exec ls -lh {} \; 2>/dev/null | awk '{print "      "$9" ("$5")"}'
else
    echo "   ⚠️  No recent backups found"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ State verification complete"
echo ""
echo "⚠️  If making changes:"
echo "   1. Backup: cp testing/paper-trade-bot.ts testing/paper-trade-bot.ts.backup-\$(date +%Y%m%d-%H%M)-REASON"
echo "   2. Edit ONLY testing/paper-trade-bot.ts"
echo "   3. Test: bun run --dry-run testing/paper-trade-bot.ts"
echo "   4. Verify state preserved after restart"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
