#!/bin/bash
# Clean stats monitor with token snapshots

LOG_FILE="/tmp/paper-trade.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

while true; do
    clear

    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}     📊 SOLANA BOT LIVE MONITOR${NC}"
    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "⏰ $(date '+%I:%M:%S %p')"
    echo ""

    # ═══ ACCOUNT STATUS ═══
    BALANCE_LINE=$(tail -200 "$LOG_FILE" 2>/dev/null | grep "💰 Balance:" | tail -1)
    PNL_LINE=$(tail -200 "$LOG_FILE" 2>/dev/null | grep "📈 Net P&L:" | tail -1)
    STATUS_OUTPUT=$(cd /home/workspace/Projects/survival-agent && bash testing/status.sh 2>/dev/null)

    if [[ -n "$BALANCE_LINE" ]]; then
        BAL=$(echo "$BALANCE_LINE" | grep -oP '\d+\.\d+' | head -1)
        PNL_PCT=$(echo "$PNL_LINE" | grep -oP '[-+]?\d+\.\d+(?=%)')
        PNL_SOL=$(echo "$PNL_LINE" | grep -oP '[-+]?\d+\.\d+(?= SOL)' | head -1)

        # Get starting balance (0.5 SOL)
        STARTING_BAL=0.5

        # Count open positions
        OPEN_POS=$(echo "$STATUS_OUTPUT" | grep "📈 Open Positions:" | grep -oP '\d+(?=/)')

        # Calculate deployed capital (starting - current free balance)
        DEPLOYED=$(echo "$STARTING_BAL - $BAL" | bc)

        echo -e "${BOLD}💰 Free Balance:${NC} $BAL SOL"
        echo -e "${BOLD}💵 Deployed Capital:${NC} $DEPLOYED SOL (in $OPEN_POS positions)"
        echo -e "${BOLD}🏦 Starting Capital:${NC} $STARTING_BAL SOL"

        if [[ "$PNL_PCT" =~ ^- ]]; then
            echo -e "${BOLD}📉 Overall P&L:${NC} ${RED}$PNL_SOL SOL ($PNL_PCT%)${NC}"
        else
            echo -e "${BOLD}📈 Overall P&L:${NC} ${GREEN}+$PNL_SOL SOL (+$PNL_PCT%)${NC}"
        fi
    else
        echo -e "${YELLOW}Waiting for balance data...${NC}"
    fi

    echo ""
    echo -e "${BOLD}${CYAN}═══ OPEN POSITIONS ═══${NC}"

    # Parse positions properly
    POSITIONS_FOUND=0
    while IFS= read -r line; do
        # Look for token name lines
        if [[ "$line" =~ ^[[:space:]]+([A-Z0-9]+)[[:space:]]+\[dexscreener\] ]]; then
            TOKEN="${BASH_REMATCH[1]}"
            # Read next few lines to get P&L
            while IFS= read -r pnl_line; do
                if [[ "$pnl_line" =~ P\&L:[[:space:]]*(-?[0-9]+)% ]]; then
                    PNL="${BASH_REMATCH[1]}"
                    POSITIONS_FOUND=$((POSITIONS_FOUND + 1))

                    if [[ "$PNL" =~ ^- ]]; then
                        echo -e "  ${BOLD}$TOKEN${NC} ${RED}$PNL%${NC}"
                    else
                        echo -e "  ${BOLD}$TOKEN${NC} ${GREEN}+$PNL%${NC}"
                    fi
                    break
                fi
            done
        fi
    done < <(cd /home/workspace/Projects/survival-agent && bash testing/status.sh 2>/dev/null | sed -n '/Current Positions/,/Recent Activity/p')

    if [[ $POSITIONS_FOUND -eq 0 ]]; then
        echo -e "  ${YELLOW}No active positions${NC}"
    fi

    echo ""
    echo -e "${BOLD}${CYAN}═══ SCANNER STATUS ═══${NC}"

    # Latest scan results
    SCAN_LINE=$(tail -50 "$LOG_FILE" 2>/dev/null | grep "DexScreener: Found" | tail -1)
    if [[ -n "$SCAN_LINE" ]]; then
        OPP_COUNT=$(echo "$SCAN_LINE" | grep -oP 'Found \K\d+')
        SCORES=$(echo "$SCAN_LINE" | grep -oP 'top scores: \[\K[^\]]+')
        echo -e "${BOLD}🔍 Opportunities:${NC} $OPP_COUNT found"
        echo -e "${BOLD}📊 Top scores:${NC} [$SCORES]"
    else
        echo -e "${YELLOW}Waiting for scan...${NC}"
    fi

    # Latest confidence
    CONF_LINE=$(tail -20 "$LOG_FILE" 2>/dev/null | grep "Confidence:" | tail -1)
    if [[ -n "$CONF_LINE" ]]; then
        CONF=$(echo "$CONF_LINE" | grep -oP 'Confidence: \K\d+')
        if [[ $CONF -ge 45 ]]; then
            echo -e "${BOLD}🎯 Last confidence:${NC} ${GREEN}$CONF/100 ✓${NC}"
        else
            echo -e "${BOLD}🎯 Last confidence:${NC} ${RED}$CONF/100 ✗${NC} (need 45+)"
        fi
    fi

    echo ""
    echo -e "${BOLD}${CYAN}═══ RECENT ACTIVITY ═══${NC}"

    # Recent trades
    TRADE_COUNT=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "TRADE SIMULATED")
    SKIP_COUNT=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "SKIPPED: Low confidence")
    NO_TRADE_COUNT=$(tail -50 "$LOG_FILE" 2>/dev/null | grep -c "No trades taken")

    echo -e "${BOLD}✅ Trades executed:${NC} ${GREEN}$TRADE_COUNT${NC}"
    echo -e "${BOLD}❌ Skipped (low conf):${NC} ${RED}$SKIP_COUNT${NC}"
    echo -e "${BOLD}⏭️  Scans rejected all:${NC} ${YELLOW}$NO_TRADE_COUNT${NC}"

    # Last rejection reason
    LAST_SKIP=$(tail -20 "$LOG_FILE" 2>/dev/null | grep "SKIPPED" | tail -1)
    if [[ -n "$LAST_SKIP" ]]; then
        SKIP_CONF=$(echo "$LAST_SKIP" | grep -oP '\d+(?= < 45)')
        if [[ -n "$SKIP_CONF" ]]; then
            echo -e "${BOLD}Last skip reason:${NC} Confidence ${RED}$SKIP_CONF${NC}/45"
        fi
    fi

    echo ""
    echo -e "${CYAN}────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}Refreshing every 3s... Ctrl+C to stop${NC}"

    sleep 3
done
