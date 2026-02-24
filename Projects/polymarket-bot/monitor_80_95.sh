#!/bin/bash

# Monitor for 80-95% Favorites Paper Trading Bot

POSITIONS_FILE="paper_positions_80_95.json"
STATS_FILE="paper_stats_80_95.json"
LOG_FILE="paper_bot_80_95.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

clear

echo -e "${BOLD}${CYAN}"
echo "════════════════════════════════════════════════════════════════════════"
echo "           📊 POLYMARKET BOT MONITOR - 80-95% FAVORITES"
echo "════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if bot is running
BOT_PID=$(pgrep -f "paper_bot_80_95.py")
if [ -z "$BOT_PID" ]; then
    echo -e "${RED}⚠️  BOT NOT RUNNING${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Bot Running (PID: $BOT_PID)${NC}"
fi

echo ""

# Load stats
STARTING=$(jq -r '.starting_bankroll' "$STATS_FILE")
FREE_CASH=$(jq -r '.current_bankroll' "$STATS_FILE")
TOTAL_BETS=$(jq -r '.total_bets' "$STATS_FILE")
WINS=$(jq -r '.wins' "$STATS_FILE")
LOSSES=$(jq -r '.losses' "$STATS_FILE")
WAGERED=$(jq -r '.total_wagered' "$STATS_FILE")
PROFIT=$(jq -r '.total_profit' "$STATS_FILE")

# Load positions and calculate unrealized P&L
OPEN_COUNT=$(jq '.open | length' "$POSITIONS_FILE")
CLOSED_COUNT=$(jq '.closed | length' "$POSITIONS_FILE")
TOTAL_COST=$(jq '[.open[].cost] | add // 0' "$POSITIONS_FILE")
TOTAL_VALUE=$(jq '[.open[].current_value] | add // 0' "$POSITIONS_FILE")

# If current_value not set, use cost as fallback
if (( $(echo "$TOTAL_VALUE == 0" | bc -l) )); then
    TOTAL_VALUE=$TOTAL_COST
fi

UNREALIZED_PNL=$(echo "$TOTAL_VALUE - $TOTAL_COST" | bc)

# True bankroll = free cash + position value
TRUE_BANKROLL=$(echo "$FREE_CASH + $TOTAL_VALUE" | bc)
TRUE_PNL=$(echo "$TRUE_BANKROLL - $STARTING" | bc)
TRUE_PNL_PCT=$(echo "scale=1; ($TRUE_PNL / $STARTING) * 100" | bc)

if (( $(echo "$TRUE_PNL > 0" | bc -l) )); then
    PNL_COLOR=$GREEN
else
    PNL_COLOR=$RED
fi

if (( $(echo "$UNREALIZED_PNL > 0" | bc -l) )); then
    UPNL_COLOR=$GREEN
else
    UPNL_COLOR=$RED
fi

# Win rate
if [ "$TOTAL_BETS" -gt 0 ]; then
    WIN_RATE=$(echo "scale=1; ($WINS / $TOTAL_BETS) * 100" | bc)
    if (( $(echo "$WIN_RATE >= 90" | bc -l) )); then
        WR_COLOR=$GREEN
    elif (( $(echo "$WIN_RATE >= 85" | bc -l) )); then
        WR_COLOR=$YELLOW
    else
        WR_COLOR=$RED
    fi
else
    WIN_RATE=0.0
    WR_COLOR=$YELLOW
fi

if (( $(echo "$WAGERED > 0" | bc -l) )); then
    ROI=$(echo "scale=1; ($PROFIT / $WAGERED) * 100" | bc)
else
    ROI=0.0
fi

echo -e "${BOLD}💰 BANKROLL${NC}"
echo "────────────────────────────────────────────────────────────────────────"
printf "   Starting:       \$%.2f\n" "$STARTING"
printf "   Free Cash:      \$%.2f\n" "$FREE_CASH"
printf "   Position Value: \$%.2f\n" "$TOTAL_VALUE"
echo -e "   ${BOLD}TRUE BANKROLL:  \$${TRUE_BANKROLL}${NC}"
echo -e "   ${BOLD}TRUE P&L:       ${PNL_COLOR}\$${TRUE_PNL} (${TRUE_PNL_PCT}%)${NC}"
echo ""

echo -e "${BOLD}📈 POSITIONS${NC}"
echo "────────────────────────────────────────────────────────────────────────"
printf "   Open:           %d positions\n" "$OPEN_COUNT"
printf "   Total Cost:     \$%.2f (capital deployed)\n" "$TOTAL_COST"
printf "   Current Value:  \$%.2f\n" "$TOTAL_VALUE"
echo -e "   Unrealized P&L: ${UPNL_COLOR}\$${UNREALIZED_PNL}${NC}"
printf "   Closed:         %d (wins: %d, losses: %d)\n" "$CLOSED_COUNT" "$WINS" "$LOSSES"
echo ""

echo -e "${BOLD}📊 PERFORMANCE${NC}"
echo "────────────────────────────────────────────────────────────────────────"
echo -e "   Win Rate:      ${WR_COLOR}${WIN_RATE}%${NC} (expected: 92.4%)"
printf "   Total Bets:    %d\n" "$TOTAL_BETS"
printf "   Total Wagered: \$%.2f\n" "$WAGERED"
printf "   ROI:           %.1f%% (target: +7.4%%)\n" "$ROI"
echo ""

# Show open positions with unrealized P&L
if [ "$OPEN_COUNT" -gt 0 ]; then
    echo -e "${BOLD}🎯 OPEN POSITIONS${NC}"
    echo "────────────────────────────────────────────────────────────────────────"
    jq -r '.open[] | select(.cost > 0) |
        if .unrealized_pnl then
            "   • \(.question[:55])...\n     \(.outcome) @ \(.price*100)% → \(.current_price*100)% | Cost: $\(.cost | floor * 100 / 100) | P&L: $\(.unrealized_pnl | floor * 100 / 100)\n"
        else
            "   • \(.question[:55])...\n     \(.outcome) @ \(.price*100)% | Cost: $\(.cost | floor * 100 / 100) | Checking price...\n"
        end' "$POSITIONS_FILE" | head -30
    echo ""
fi

echo -e "${BOLD}📋 RECENT ACTIVITY (last 10 lines)${NC}"
echo "────────────────────────────────────────────────────────────────────────"
tail -10 "$LOG_FILE"
echo ""

echo -e "${BOLD}🎲 STRATEGY: 80-95% Favorites | Edge: +7.4% | Target: 92% wins${NC}"
echo ""
echo "Run: watch -n 10 bash monitor_80_95.sh (auto-refresh every 10 sec)"
