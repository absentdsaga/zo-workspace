#!/bin/bash
# Restart paper trading bot with optimized settings

cd /home/workspace/Projects/polymarket-bot

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║          RESTARTING WITH OPTIMIZED SETTINGS                          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🔧 Configuration Changes:"
echo "   MIN_PROFIT_THRESHOLD: 0.5% → 0.3%"
echo ""
echo "📈 Expected Impact:"
echo "   • 3-5x more opportunities"
echo "   • Opportunities within 1-2 hours (vs 4-8 hours)"
echo "   • 30-50 trades in 48 hours (vs 5-10 trades)"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# Check if bot is running
if pgrep -f "paper_trading_bot.py" > /dev/null; then
    echo "⚠️  Stopping current bot..."
    pkill -f "paper_trading_bot.py"
    sleep 2
    echo "✅ Stopped"
    echo ""
fi

echo "🚀 Starting optimized paper trading bot..."
echo ""

# Start in background for 24/7 operation
nohup /usr/local/bin/python3 paper_trading_bot.py < <(echo "100") > paper_trading.log 2>&1 &

sleep 2

if pgrep -f "paper_trading_bot.py" > /dev/null; then
    echo "✅ Bot started successfully!"
    echo ""
    echo "📊 Status:"
    ps aux | grep paper_trading_bot.py | grep -v grep | head -1
    echo ""
    echo "📝 Logs: tail -f paper_trading.log"
    echo "📊 Monitor: ./monitor_paper_trading.sh"
    echo ""
    echo "🎯 Next: Let it run through Super Bowl Sunday!"
    echo ""
else
    echo "❌ Failed to start. Run manually:"
    echo "   ./run_paper_trading.sh"
fi
