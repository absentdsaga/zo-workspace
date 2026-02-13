#!/bin/bash
# Paper trade summary - key metrics only

echo "🤖 Paper Trading Summary Monitor"
echo "======================================"
echo ""
echo "Shows key events:"
echo "  📊 Loop number & opportunities found"
echo "  🎯 Top candidate analysis"
echo "  ✅ Trade executions"
echo "  💰 Balance & P&L"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

# -a = treat as text, --line-buffered = real-time output
tail -f /tmp/paper-trade-final.log | cat -v | grep -a --line-buffered -E "(^Loop [0-9]+|opportunities$|meet minimum|Analyzing top|Token:|Score:|Confidence:|EXECUTING|SIMULATED|Balance:|P&L:|Win rate)"
