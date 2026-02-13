#!/bin/bash
# THE ONLY BOT STARTUP SCRIPT
# v2.0 with Shocked integration

echo "🤖 Starting THE Paper Trading Bot v2.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Features:"
echo "  ✅ Shocked group call integration"
echo "  ✅ v2.0 source filter (excludes dexscreener-only)"
echo "  ✅ 12% position size"
echo "  ✅ Dual-loop architecture"
echo "  ✅ Trailing stop after +100%"
echo ""

cd /home/workspace/Projects/survival-agent
nohup bun run testing/paper-trade-bot.ts > /tmp/paper-bot.log 2>&1 &

PID=$!
echo "✅ Bot started (PID: $PID)"
echo ""
echo "Monitor with:"
echo "  watch -n 5 /tmp/paper-bot-status.sh"
echo ""
echo "Logs:"
echo "  tail -f /tmp/paper-bot.log"
echo ""
