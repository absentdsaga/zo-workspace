#!/bin/bash

# Paper Trading Bot Status Monitor

echo "=================================================="
echo "📊 PAPER TRADING BOT STATUS"
echo "=================================================="
echo ""

# Check if bot is running
if pgrep -f "paper-trade-bot.ts" > /dev/null; then
    echo "✅ Bot Status: RUNNING"
    echo "   PID: $(pgrep -f 'paper-trade-bot.ts')"
else
    echo "❌ Bot Status: STOPPED"
fi

echo ""

# Parse JSON data
DATA=$(cat /tmp/paper-trades-master.json)

# Balance info
BALANCE=$(echo "$DATA" | jq -r '.balance')
echo "💰 Balance: ${BALANCE} SOL"

# Position count
OPEN_COUNT=$(echo "$DATA" | jq '.trades | map(select(.status == "open")) | length')
echo "📈 Open Positions: ${OPEN_COUNT}/7"

echo ""
echo "Current Positions:"
echo "--------------------------------------------------"

# Show open positions
echo "$DATA" | jq -r '.trades | map(select(.status == "open")) | .[] |
  "  \(.tokenSymbol) [\(.source)]
    Entry: $\(.entryPrice | tostring)
    Current: $\(.currentPrice | tostring)
    P&L: \(((.currentPrice - .entryPrice) / .entryPrice * 100) | floor)%
    Confidence: \(.confidenceScore)
    Age: \(((now * 1000 - .timestamp) / 60000) | floor) min
"'

echo ""
echo "Recent Activity:"
echo "--------------------------------------------------"
tail -20 /tmp/paper-trade-bot.log | grep -E "SCANNER|✅ TRADE|⏭️  SKIPPED|High confidence" | tail -5

echo ""
echo "=================================================="
echo "To watch live: tail -f /tmp/paper-trade-bot.log"
echo "=================================================="
