#!/bin/bash
# Start the ADVANCED paper trading bot

cd "$(dirname "$0")"

echo "🚀 Starting ADVANCED Paper Trading Bot..."
echo ""
echo "NEW FEATURES:"
echo "⚡ Dual-loop: Scanner (15s) + Monitor (5s)"
echo "💎 Trailing stop: 20% from peak after +100% TP1"
echo "📊 Scanner source tracking (pumpfun/dexscreener/both)"
echo "🎯 Up to 10 concurrent positions"
echo "✅ Jupiter-validated prices and routes"
echo ""

# Load secrets
source ~/.zo_secrets 2>/dev/null || source ~/.bashrc 2>/dev/null

# Kill any existing paper trade process
pkill -f "paper-trade" 2>/dev/null
sleep 2

# Start the advanced version
LOG_FILE="/tmp/paper-trade-fixed.log"

nohup bun run testing/paper-trade-master-fixed.ts > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ Started with PID: $PID"
echo "📝 Logging to: $LOG_FILE"
echo ""
echo "Monitor with:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Stop with:"
echo "  pkill -f paper-trade-master-fixed"
