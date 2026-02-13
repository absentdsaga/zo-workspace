#!/bin/bash
# Verbose paper trade monitor - shows everything important

echo "🤖 Paper Trading Monitor - Verbose Mode"
echo "======================================"
echo ""
echo "Shows:"
echo "  🔍 All scans and opportunities"
echo "  ✅ Passed checks"
echo "  ❌ Failed checks with reasons"
echo "  📊 Score analysis"
echo "  💰 Trade executions"
echo "  📈 System health"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

# Use -a flag to treat as text, not binary
tail -f /tmp/paper-trade-final.log | cat -v | grep -a --line-buffered -v "^$"
