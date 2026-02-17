#!/bin/bash
# Start the paper trading bot with Helius Gatekeeper

cd "$(dirname "$0")"

echo "🚀 Starting Paper Trading Bot with Helius Gatekeeper..."
echo ""
echo "⚡ 4-7x faster RPC (sub-millisecond warm connections)"
echo "🌐 Global edge network with near-zero overhead"
echo "📊 Dual-loop: Scanner (15s) + Monitor (5s)"
echo "💎 Trailing stop: 20% from peak after +100% TP1"
echo "🎯 Up to 10 concurrent positions"
echo "✅ Jupiter-validated prices and routes"
echo ""

# Load secrets
source ~/.zo_secrets 2>/dev/null || source ~/.bashrc 2>/dev/null

# Kill any existing paper trade process
pkill -f "paper-trade" 2>/dev/null
sleep 2

# Start the bot
LOG_FILE="/tmp/paper-trade.log"

nohup bun run testing/paper-trade-bot.ts > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ Started with PID: $PID"
echo "📝 Logging to: $LOG_FILE"
echo "🌐 Using Helius Gatekeeper: beta.helius-rpc.com"
echo ""
echo "Monitor with:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Stop with:"
echo "  pkill -f paper-trade-bot"
