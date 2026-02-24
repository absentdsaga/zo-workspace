#!/bin/bash
# Start the 80-90¢ paper trading bot

echo "════════════════════════════════════════════════════════════════════════════════"
echo "        🤖 Starting Paper Trading Bot (80-90¢ Strategy)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Strategy Details:"
echo "   • Target Range: 80-90¢"
echo "   • Expected Edge: +7.4%"
echo "   • Expected Win Rate: 92.4%"
echo "   • Starting Bankroll: \$1,000"
echo "   • Kelly Fraction: 0.25 (quarter Kelly)"
echo "   • Max Bet: 5% of bankroll"
echo ""
echo "✅ Validation:"
echo "   • Monte Carlo simulations: 10,000 runs"
echo "   • Expected return: +44.9% per 100 bets"
echo "   • Profit probability: 99.3%"
echo "   • Sharpe ratio: 2.31 (excellent)"
echo ""
echo "📋 Files:"
echo "   • Bot: paper_bot_80_90.py"
echo "   • Stats: paper_stats_80_90.json"
echo "   • Positions: paper_positions_80_90.json"
echo "   • Log: paper_bot_80_90.log"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Starting bot in 3 seconds..."
echo "Press Ctrl+C to stop"
echo ""

sleep 3

# Run the bot
python paper_bot_80_90.py
