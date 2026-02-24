#!/bin/bash
# Simple log viewer for paper trading

cd /home/workspace/Projects/polymarket-bot

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              PAPER TRADING - LOG VIEWER                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose option:"
echo ""
echo "  1) Live tail (follow log in real-time)"
echo "  2) View last 50 lines"
echo "  3) View all opportunities found"
echo "  4) View performance summaries"
echo "  5) Check if bot is running"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📊 Following log in real-time (Ctrl+C to exit)..."
        echo ""
        tail -f paper_trading.log
        ;;
    2)
        echo ""
        echo "📊 Last 50 lines:"
        echo "══════════════════════════════════════════════════════════════════════"
        tail -50 paper_trading.log
        ;;
    3)
        echo ""
        echo "💎 Opportunities Found:"
        echo "══════════════════════════════════════════════════════════════════════"
        grep -A 8 "ARBITRAGE OPPORTUNITY FOUND" paper_trading.log
        ;;
    4)
        echo ""
        echo "📈 Performance Summaries:"
        echo "══════════════════════════════════════════════════════════════════════"
        grep -A 10 "PAPER TRADING PERFORMANCE" paper_trading.log
        ;;
    5)
        echo ""
        if pgrep -f "paper_trading_bot.py" > /dev/null; then
            echo "✅ Paper trading bot IS running"
            echo ""
            ps aux | grep paper_trading_bot.py | grep -v grep
        else
            echo "❌ Paper trading bot is NOT running"
            echo ""
            echo "Start it with: ./run_paper_trading.sh"
        fi
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
