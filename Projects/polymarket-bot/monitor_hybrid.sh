#!/bin/bash
# Monitor for Polymarket 5-Minute HYBRID Bot
# Shows live price tracking and alerts

LOGFILE="hybrid_bot.log"
BOTSCRIPT="HYBRID_bot.py"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}🤖 Polymarket 5-Minute Bot Monitor${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if bot is running
if pgrep -f "$BOTSCRIPT" > /dev/null; then
    echo -e "${GREEN}✅ Bot Status: RUNNING${NC}"
    BOTPID=$(pgrep -f "$BOTSCRIPT")
    echo -e "   PID: $BOTPID"
    echo -e "   Runtime: $(ps -p $BOTPID -o etime= | tr -d ' ')"
else
    echo -e "${RED}❌ Bot Status: NOT RUNNING${NC}"
    echo ""
    echo "To start the bot, run:"
    echo "  ./run_bot.sh > hybrid_bot.log 2>&1 &"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}📊 LIVE OUTPUT (Ctrl+C to exit)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Tail the log with color highlighting
tail -f "$LOGFILE" 2>/dev/null | while read -r line; do
    if [[ $line == *"ARBITRAGE OPPORTUNITY"* ]]; then
        echo -e "${GREEN}${line}${NC}"
    elif [[ $line == *"PROFIT:"* ]]; then
        echo -e "${GREEN}${line}${NC}"
    elif [[ $line == *"Error"* ]] || [[ $line == *"❌"* ]]; then
        echo -e "${RED}${line}${NC}"
    elif [[ $line == *"⚠️"* ]]; then
        echo -e "${YELLOW}${line}${NC}"
    elif [[ $line == *"New market detected"* ]]; then
        echo -e "${CYAN}${line}${NC}"
    else
        echo "$line"
    fi
done
