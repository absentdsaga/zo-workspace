#!/bin/bash
# Monitoring dashboard for 80-90¢ paper trading bot

STATS_FILE="paper_stats_80_90.json"
POSITIONS_FILE="paper_positions_80_90.json"
LOG_FILE="paper_bot_80_90.log"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    📊 PAPER TRADING MONITOR (80-90¢ Strategy)                  "
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if files exist
if [ ! -f "$STATS_FILE" ]; then
    echo -e "${RED}❌ Bot not started yet. Run: python paper_bot_80_90.py${NC}"
    exit 1
fi

# Parse stats
STARTING=$(jq -r '.starting_bankroll' $STATS_FILE)
CURRENT=$(jq -r '.current_bankroll' $STATS_FILE)
PROFIT=$(jq -r '.total_profit' $STATS_FILE)
TOTAL_BETS=$(jq -r '.total_bets' $STATS_FILE)
WINS=$(jq -r '.wins' $STATS_FILE)
LOSSES=$(jq -r '.losses' $STATS_FILE)
WAGERED=$(jq -r '.total_wagered' $STATS_FILE)
STARTED=$(jq -r '.started_at' $STATS_FILE)

# Calculate metrics
CLOSED=$((WINS + LOSSES))
if [ $CLOSED -gt 0 ]; then
    WIN_RATE=$(echo "scale=1; $WINS * 100 / $CLOSED" | bc)
else
    WIN_RATE="0.0"
fi

PNL=$(echo "scale=2; $CURRENT - $STARTING" | bc)
PNL_PCT=$(echo "scale=1; ($CURRENT / $STARTING - 1) * 100" | bc)

# ROI
if (( $(echo "$WAGERED > 0" | bc -l) )); then
    ROI=$(echo "scale=1; $PROFIT * 100 / $WAGERED" | bc)
else
    ROI="0.0"
fi

# Expected values
EXPECTED_WIN_RATE="92.4"
EXPECTED_EDGE="7.4"

# Print bankroll
echo "💰 BANKROLL"
echo "─────────────────────────────────────────────────────────────────────────────────"
echo -e "   Starting: \$${STARTING}"
echo -e "   Current:  \$${CURRENT}"

if (( $(echo "$PNL >= 0" | bc -l) )); then
    echo -e "   P&L:      ${GREEN}\$${PNL} (+${PNL_PCT}%)${NC}"
else
    echo -e "   P&L:      ${RED}\$${PNL} (${PNL_PCT}%)${NC}"
fi
echo ""

# Print positions
OPEN_COUNT=$(jq '.open | length' $POSITIONS_FILE)
OPEN_EXPOSURE=$(jq '[.open[].cost] | add // 0' $POSITIONS_FILE)

echo "📈 POSITIONS"
echo "─────────────────────────────────────────────────────────────────────────────────"
echo "   Open: $OPEN_COUNT (exposure: \$$(printf '%.2f' $OPEN_EXPOSURE))"
echo "   Closed: $CLOSED (wins: $WINS, losses: $LOSSES)"
echo ""

# Print performance
echo "📊 PERFORMANCE"
echo "─────────────────────────────────────────────────────────────────────────────────"

# Win rate comparison
echo -n "   Win Rate:       "
if [ $CLOSED -ge 20 ]; then
    # Enough data to compare
    DIFF=$(echo "$WIN_RATE - $EXPECTED_WIN_RATE" | bc)
    if (( $(echo "$WIN_RATE >= $EXPECTED_WIN_RATE - 5" | bc -l) )); then
        echo -e "${GREEN}${WIN_RATE}%${NC} (expected: ${EXPECTED_WIN_RATE}%)"
    else
        echo -e "${RED}${WIN_RATE}%${NC} (expected: ${EXPECTED_WIN_RATE}%) ⚠️  BELOW EXPECTED"
    fi
else
    echo -e "${YELLOW}${WIN_RATE}%${NC} (expected: ${EXPECTED_WIN_RATE}%, need 20+ trades for comparison)"
fi

echo "   Total Wagered:  \$$(printf '%.2f' $WAGERED)"
echo "   Total Profit:   \$$(printf '%.2f' $PROFIT)"
echo "   ROI:            ${ROI}%"
echo ""

# Print recent activity
echo "📋 RECENT ACTIVITY (last 10 lines)"
echo "─────────────────────────────────────────────────────────────────────────────────"
if [ -f "$LOG_FILE" ]; then
    tail -n 10 $LOG_FILE
else
    echo "   No activity yet"
fi
echo ""

# Print open positions
if [ $OPEN_COUNT -gt 0 ]; then
    echo "🎯 OPEN POSITIONS"
    echo "─────────────────────────────────────────────────────────────────────────────────"
    jq -r '.open[] | "   • \(.question) - \(.outcome) @ \(.price*100|floor)¢ (cost: $\(.cost|tostring|.[0:5]))"' $POSITIONS_FILE | head -5
    if [ $OPEN_COUNT -gt 5 ]; then
        echo "   ... and $((OPEN_COUNT - 5)) more"
    fi
    echo ""
fi

# Print strategy info
echo "🎲 STRATEGY INFO"
echo "─────────────────────────────────────────────────────────────────────────────────"
echo "   Range: 80-90¢"
echo "   Expected Edge: +${EXPECTED_EDGE}%"
echo "   Expected Win Rate: ${EXPECTED_WIN_RATE}%"
echo "   Sample Size: 3,497 historical markets"
echo "   Kelly Fraction: 0.25 (quarter Kelly)"
echo "   Max Bet: 5% of bankroll"
echo ""

# Runtime
echo "⏱️  RUNTIME"
echo "─────────────────────────────────────────────────────────────────────────────────"
echo "   Started: $STARTED"
echo "   Last updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "💡 Commands:"
echo "   • View full log: tail -f $LOG_FILE"
echo "   • View stats: cat $STATS_FILE | jq"
echo "   • View positions: cat $POSITIONS_FILE | jq"
echo "   • Refresh: bash monitor_80_90.sh"
echo ""
