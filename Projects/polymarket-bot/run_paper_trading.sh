#!/bin/bash
# Guaranteed launcher for paper trading bot

cd /home/workspace/Projects/polymarket-bot

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              POLYMARKET PAPER TRADING BOT LAUNCHER                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  PAPER TRADING MODE - ZERO RISK"
echo ""
echo "Checking Python environment..."

# Use absolute path to python
PYTHON=/usr/local/bin/python3

# Verify aiohttp is available
if ! $PYTHON -c "import aiohttp" 2>/dev/null; then
    echo "❌ aiohttp not found. Installing..."
    $PYTHON -m pip install aiohttp
fi

echo "✅ Python environment ready"
echo ""
echo "This will:"
echo "  ✅ Find REAL arbitrage opportunities"
echo "  ✅ Simulate trades (NO real money spent)"
echo "  ✅ Prove profitability BEFORE you risk capital"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""

read -p "Simulated balance (default 100): " BALANCE
BALANCE=${BALANCE:-100}

echo ""
echo "🚀 Starting paper trading with \$$BALANCE simulated capital..."
echo ""
echo "📊 Logs: paper_trading.log"
echo "📊 Results: paper_trading_results.json"
echo ""
echo "⏱️  Let this run for 24-48 hours for best results"
echo "🛑 Press Ctrl+C to stop and see final results"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# Run with absolute python path
echo "$BALANCE" | $PYTHON paper_trading_bot.py 2>&1 | tee paper_trading.log
