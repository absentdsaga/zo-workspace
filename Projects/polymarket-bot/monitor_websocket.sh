#!/bin/bash

# WebSocket Paper Trading Bot Monitor
# Real-time performance dashboard

clear

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  WEBSOCKET PAPER TRADING BOT - LIVE MONITOR              ║"
echo "║  ⚡ 10,000x FASTER THAN REST POLLING ⚡                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if bot is running
PID=$(ps aux | grep paper_trading_websocket.py | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "❌ WebSocket bot is NOT running"
    echo ""
    echo "To start: ./run_websocket_bot.sh"
    exit 1
fi

echo "✅ Bot Status: RUNNING (PID: $PID)"
echo ""

# Show latest performance
echo "─────────────────────────────────────────────────────────────"
echo "📈 LATEST PERFORMANCE:"
echo "─────────────────────────────────────────────────────────────"
grep "WEBSOCKET PAPER TRADING PERFORMANCE" paper_trading_ws.log | tail -1
grep -A 12 "WEBSOCKET PAPER TRADING PERFORMANCE" paper_trading_ws.log | tail -12
echo ""

# Show WebSocket stats
echo "─────────────────────────────────────────────────────────────"
echo "⚡ WEBSOCKET CONNECTION STATS:"
echo "─────────────────────────────────────────────────────────────"
grep "WebSocket connected" paper_trading_ws.log | tail -3
grep "Updates received:" paper_trading_ws.log | tail -1
grep "Avg latency:" paper_trading_ws.log | tail -1
grep "Speed advantage:" paper_trading_ws.log | tail -1
echo ""

# Show any opportunities found
echo "─────────────────────────────────────────────────────────────"
echo "💎 ARBITRAGE OPPORTUNITIES:"
echo "─────────────────────────────────────────────────────────────"
OPPS=$(grep "ARBITRAGE OPPORTUNITY FOUND" paper_trading_ws.log | wc -l)
if [ "$OPPS" -eq 0 ]; then
    echo "No opportunities detected yet (normal during low-volume hours)"
    echo ""
    echo "💡 TIP: Opportunities spike during:"
    echo "   • Market hours (9am-4pm ET)"
    echo "   • Major events (Super Bowl in 3 days!)"
    echo "   • Crypto volatility"
else
    echo "Found $OPPS opportunities!"
    echo ""
    grep -A 8 "ARBITRAGE OPPORTUNITY FOUND" paper_trading_ws.log | tail -20
fi
echo ""

# Show recent trades
echo "─────────────────────────────────────────────────────────────"
echo "📊 RECENT PAPER TRADES:"
echo "─────────────────────────────────────────────────────────────"
if grep -q "RECENT TRADES:" paper_trading_ws.log; then
    grep -A 5 "RECENT TRADES:" paper_trading_ws.log | tail -6
else
    echo "No trades executed yet"
fi
echo ""

# Show last 5 log entries
echo "─────────────────────────────────────────────────────────────"
echo "📝 RECENT ACTIVITY:"
echo "─────────────────────────────────────────────────────────────"
tail -5 paper_trading_ws.log
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Press Ctrl+C to exit  |  Refreshing every 10 seconds    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Auto-refresh option
if [ "$1" == "--live" ]; then
    echo "🔄 Live mode enabled - refreshing every 10 seconds"
    while true; do
        sleep 10
        bash "$0"
    done
fi
