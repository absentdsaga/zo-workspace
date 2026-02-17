#!/bin/bash

cd /home/workspace/Projects/survival-agent

echo "🚀 Starting Paper Trading Bot (Real Jito Costs)"
echo "════════════════════════════════════════════════"
echo ""
echo "Balance: 0.5 SOL"
echo "Jito tips: p75 ($0.0088/trade)"
echo "Fee tracking: ENABLED"
echo ""
echo "Monitor: watch -n 10 bash show-positions.sh"
echo ""

bun testing/paper-trade-bot.ts
