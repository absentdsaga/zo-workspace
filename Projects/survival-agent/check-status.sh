#!/bin/bash
# Quick status check - won't freeze terminal

echo "🤖 Trading Bot Status Check"
echo "=============================="
echo ""

# Check if bot is running
if pgrep -f "paper-trade-master" > /dev/null; then
    echo "Status: 🟢 RUNNING"
    PID=$(pgrep -f "paper-trade-master")
    echo "PID: $PID"
else
    echo "Status: 🔴 STOPPED"
fi

echo ""
echo "📊 Latest Activity (last 5 loops):"
echo "-----------------------------------"
grep "^Loop" /tmp/paper-1to1.log 2>/dev/null | tail -5

echo ""
echo "💰 Latest Balance:"
echo "------------------"
grep "Balance:" /tmp/paper-1to1.log 2>/dev/null | tail -3

echo ""
echo "🎯 Trades Executed:"
echo "-------------------"
TRADES=$(grep -c "TRADE SIMULATED" /tmp/paper-1to1.log 2>/dev/null)
echo "Total simulated: $TRADES"

echo ""
echo "📈 Recent P&L:"
echo "--------------"
grep "P&L:" /tmp/paper-1to1.log 2>/dev/null | tail -3

echo ""
echo "=============================="
echo "Log file: /tmp/paper-1to1.log"
echo ""
echo "Commands:"
echo "  Start bot: bash /home/workspace/Projects/survival-agent/start-paper-master.sh > /tmp/paper-1to1.log 2>&1 &"
echo "  Stop bot:  pkill -f paper-trade-master"
echo "  This check: bash /home/workspace/Projects/survival-agent/check-status.sh"
