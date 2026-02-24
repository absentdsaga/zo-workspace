#!/bin/bash
# Real-time stats dashboard for Longshot Bot

LOG_FILE="/dev/shm/longshot_bot.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

while true; do
    clear
    
    echo -e "${BOLD}${CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║${NC}  ${BOLD}${YELLOW}🎰 POLYMARKET LONGSHOT BOT - LIVE DASHBOARD${NC}                                  ${BOLD}${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Get latest stats from log
    TOTAL_SCANS=$(grep -c "Scan #" "$LOG_FILE" 2>/dev/null || echo "0")
    TOTAL_TRADES=$(grep -c "PAPER TRADE:" "$LOG_FILE" 2>/dev/null || echo "0")
    TOTAL_OPPS=$(grep "Found.*outcomes under" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\d+(?= outcomes)' || echo "0")
    
    # Portfolio stats
    POSITIONS=$(grep "Total positions:" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\d+' || echo "0")
    INVESTED=$(grep "Total invested:" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\$[\d.]+' || echo "\$0.00")
    DAILY_SPEND=$(grep "Daily spend:" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\$[\d.]+' | head -1 || echo "\$0.00")
    
    # Calculate potential
    POTENTIAL=$(echo "$POSITIONS * 10000" | bc 2>/dev/null || echo "0")
    
    # Last scan time
    LAST_SCAN=$(grep "Scan #" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP '\d{2}:\d{2}:\d{2}' || echo "Never")
    
    # Session stats
    echo -e "${BOLD}${BLUE}📊 SESSION STATS${NC}"
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────────────────────────┐${NC}"
    printf "${CYAN}│${NC} Total Scans:          ${YELLOW}%-50s${CYAN}│${NC}\n" "$TOTAL_SCANS"
    printf "${CYAN}│${NC} Last Scan:            ${YELLOW}%-50s${CYAN}│${NC}\n" "$LAST_SCAN"
    printf "${CYAN}│${NC} Opportunities Found:  ${YELLOW}%-50s${CYAN}│${NC}\n" "$TOTAL_OPPS"
    printf "${CYAN}│${NC} Trades Executed:      ${GREEN}%-50s${CYAN}│${NC}\n" "$TOTAL_TRADES"
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    # Portfolio
    echo -e "${BOLD}${BLUE}💼 PORTFOLIO${NC}"
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────────────────────────┐${NC}"
    printf "${CYAN}│${NC} Active Positions:     ${GREEN}%-50s${CYAN}│${NC}\n" "$POSITIONS longshots"
    printf "${CYAN}│${NC} Total Invested:       ${YELLOW}%-50s${CYAN}│${NC}\n" "$INVESTED"
    printf "${CYAN}│${NC} Daily Spend:          ${YELLOW}%-50s${CYAN}│${NC}\n" "$DAILY_SPEND / \$50.00"
    printf "${CYAN}│${NC} Max Potential Payout: ${MAGENTA}%-50s${CYAN}│${NC}\n" "\$$POTENTIAL (if any hit)"
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    # Recent trades (last 5)
    echo -e "${BOLD}${BLUE}🎯 RECENT TRADES (Last 5)${NC}"
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────────────────────────┐${NC}"
    
    grep -A 4 "PAPER TRADE:" "$LOG_FILE" 2>/dev/null | tail -25 | while read -r line; do
        if echo "$line" | grep -q "PAPER TRADE:"; then
            SHARES=$(echo "$line" | grep -oP '\d+\.\d+(?= shares)')
            OUTCOME=$(echo "$line" | grep -oP "shares of '\K[^']+")
            printf "${CYAN}│${NC} ${GREEN}✓${NC} Bought ${YELLOW}%-65s${CYAN}│${NC}\n" "$SHARES shares of '$OUTCOME'"
        elif echo "$line" | grep -q "Market:"; then
            MARKET=$(echo "$line" | grep -oP 'Market: \K.*' | cut -c1-67)
            printf "${CYAN}│${NC}   ${MARKET}%-10s${CYAN}│${NC}\n" ""
        elif echo "$line" | grep -q "Price:"; then
            PRICE=$(echo "$line" | grep -oP 'Price: \K.*')
            printf "${CYAN}│${NC}   ${BLUE}Price: %-67s${CYAN}│${NC}\n" "$PRICE"
        elif echo "$line" | grep -q "Potential:"; then
            POT=$(echo "$line" | grep -oP 'Potential: \K.*')
            printf "${CYAN}│${NC}   ${MAGENTA}${POT}%-68s${CYAN}│${NC}\n" ""
            echo -e "${CYAN}├─────────────────────────────────────────────────────────────────────────────┤${NC}"
        fi
    done 2>/dev/null | head -25
    
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    # Status
    if [ "$DAILY_SPEND" = "\$50.00" ]; then
        echo -e "${RED}${BOLD}⚠️  DAILY LIMIT REACHED - Waiting for next scan to find new opportunities${NC}"
    else
        echo -e "${GREEN}${BOLD}✓ Bot running - Scanning every 5 minutes for sub-5¢ outcomes${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}Press Ctrl+C to exit | Refreshing every 3 seconds${NC}"
    
    sleep 3
done
