#!/bin/bash
# Clean paper trade monitor - shows all activity without spam

echo "🤖 Paper Trading Monitor - Live Feed"
echo "======================================"
echo ""
echo "Watching for:"
echo "  🔍 Opportunities found"
echo "  📊 Top candidates analyzed"
echo "  ✅ Trades executed"
echo "  💰 P&L updates"
echo "  ⚠️  Rejections and reasons"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

tail -f /tmp/paper-trade.log | grep -a --line-buffered -E "(^Loop|opportunities|Analyzing top|Score:|Confidence:|EXECUTING TRADE|SIMULATED|SKIPPED|Balance:|P&L:|Win rate|Sleeping)"
