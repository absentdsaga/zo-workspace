#!/bin/bash
# Real-time monitor for paper trading bot

cd /home/workspace/Projects/polymarket-bot

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           POLYMARKET PAPER TRADING - LIVE MONITOR                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Monitoring: paper_trading.log"
echo "🔄 Updates every 5 seconds"
echo "🛑 Press Ctrl+C to exit"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# Check if bot is running
if [ ! -f "paper_trading.log" ]; then
    echo "⚠️  No paper_trading.log found"
    echo ""
    echo "Is the bot running? Start it with:"
    echo "    ./run_paper_trading.sh"
    echo ""
    exit 1
fi

# Function to display dashboard
show_dashboard() {
    clear
    
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║           POLYMARKET PAPER TRADING - LIVE MONITOR                    ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Get latest stats from log
    if [ -f "paper_trading.log" ]; then
        # Show last performance update
        echo "📊 LATEST PERFORMANCE:"
        echo "══════════════════════════════════════════════════════════════════════"
        grep -A 10 "PAPER TRADING PERFORMANCE" paper_trading.log | tail -15
        echo ""
        
        # Show recent trades
        echo "💎 RECENT OPPORTUNITIES:"
        echo "══════════════════════════════════════════════════════════════════════"
        grep "ARBITRAGE OPPORTUNITY FOUND" paper_trading.log | tail -3
        echo ""
        
        # Show latest activity
        echo "📝 LATEST ACTIVITY:"
        echo "══════════════════════════════════════════════════════════════════════"
        tail -10 paper_trading.log
        echo ""
    fi
    
    echo "══════════════════════════════════════════════════════════════════════"
    echo "🔄 Auto-refresh in 5 seconds... (Ctrl+C to exit)"
    echo "══════════════════════════════════════════════════════════════════════"
}

# Main loop
while true; do
    show_dashboard
    sleep 5
done
