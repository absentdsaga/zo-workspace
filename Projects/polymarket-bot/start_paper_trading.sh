#!/bin/bash
# Quick launcher for paper trading bot

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              POLYMARKET PAPER TRADING BOT LAUNCHER                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  PAPER TRADING MODE - ZERO RISK"
echo ""
echo "This will:"
echo "  ✅ Find REAL arbitrage opportunities"
echo "  ✅ Simulate trades (NO real money spent)"
echo "  ✅ Prove profitability BEFORE you risk capital"
echo ""
echo "Requirements: NONE (no wallet, no money, no setup)"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""

read -p "Simulated balance (default 100): " BALANCE
BALANCE=${BALANCE:-100}

echo ""
echo "🚀 Starting paper trading with \$$BALANCE simulated capital..."
echo ""
echo "📊 Logs will be saved to: paper_trading.log"
echo "📊 Results will be saved to: paper_trading_results.json"
echo ""
echo "⏱️  Let this run for 24-48 hours for best results"
echo "🛑 Press Ctrl+C to stop and see final results"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# Run the bot
echo "$BALANCE" | python3 paper_trading_bot.py 2>&1 | tee paper_trading.log
