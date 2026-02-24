#!/bin/bash
# Live tracker for Longshot Bot trades

LOG_FILE="/dev/shm/longshot_bot.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear

echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${YELLOW}🎰 POLYMARKET LONGSHOT BOT - LIVE TRACKER${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Follow the log and highlight key events
tail -f "$LOG_FILE" | while read -r line; do
    # Highlight new trades
    if echo "$line" | grep -q "PAPER TRADE:"; then
        echo -e "${GREEN}${BOLD}$line${NC}"
    
    # Highlight opportunities found
    elif echo "$line" | grep -q "Found.*outcomes under"; then
        echo -e "${YELLOW}${BOLD}$line${NC}"
    
    # Highlight portfolio updates
    elif echo "$line" | grep -q "CURRENT PORTFOLIO"; then
        echo -e "${CYAN}${BOLD}$line${NC}"
    
    # Highlight totals
    elif echo "$line" | grep -q "Total positions:\|Total invested:\|Daily spend:"; then
        echo -e "${BLUE}${BOLD}$line${NC}"
    
    # Highlight scans
    elif echo "$line" | grep -q "Scan #"; then
        echo ""
        echo -e "${CYAN}$line${NC}"
    
    # Highlight limits
    elif echo "$line" | grep -q "Daily limit reached"; then
        echo -e "${RED}${BOLD}$line${NC}"
    
    # Highlight potential/ROI
    elif echo "$line" | grep -q "Potential:\|ROI if wins:"; then
        echo -e "${YELLOW}$line${NC}"
    
    # Regular lines
    else
        echo "$line"
    fi
done
