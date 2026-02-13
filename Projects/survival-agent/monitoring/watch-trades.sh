#!/bin/bash
# Clean trade monitor - only shows important events

echo "🤖 Trading Bot Monitor - Clean View"
echo "======================================"
echo ""
echo "Watching for:"
echo "  ✅ Trade executions"
echo "  💰 P&L updates"
echo "  📊 Loop summaries"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

tail -f /tmp/trading-bot.log | grep --line-buffered -E "(^Loop [0-9]+|EXECUTING TRADE|SUCCESS|FAILED|✅ TRADE|Balance:|P&L:|Win rate|🎯 HIGH CONFIDENCE)"
