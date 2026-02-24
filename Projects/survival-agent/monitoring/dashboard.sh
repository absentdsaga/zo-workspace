#!/bin/bash
# Comprehensive trading dashboard
# Usage: bash dashboard.sh           (paper mode)
#        bash dashboard.sh mainnet   (mainnet mode)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load config based on mode argument
if [[ "$1" == "mainnet" ]]; then
    source "$SCRIPT_DIR/mainnet-dashboard-config.sh"
else
    source "$SCRIPT_DIR/dashboard-config.sh"
fi

print_header() {
    local mode_display="${MODE_LABEL:-PAPER}"
    if [[ "$mode_display" == "MAINNET" ]]; then
        echo -e "${BOLD}${RED}╔════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${RED}║${NC}${WHITE}              🔴 SOLANA TRADING BOT DASHBOARD [MAINNET]              ${RED}║${NC}"
        echo -e "${BOLD}${RED}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    else
        echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${CYAN}║${NC}${WHITE}              📊 SOLANA TRADING BOT DASHBOARD [PAPER]                ${CYAN}║${NC}"
        echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    fi
}

print_section() {
    echo -e "\n${BOLD}${BLUE}━━━ $1 ━━━${NC}"
}

while true; do
    clear
    print_header
    echo -e "${DIM}$(date '+%A, %B %d, %Y - %I:%M:%S %p')${NC}"

    # Detect correct bot process per mode
    if [[ "${MODE_LABEL:-PAPER}" == "MAINNET" ]]; then
        BOT_PID=$(pgrep -f "mainnet-trade-bot" | head -1)
    else
        BOT_PID=$(pgrep -f "paper-trade-bot" | grep -v mainnet | head -1)
    fi
    if [[ -n "$BOT_PID" ]]; then BOT_STATUS="RUNNING"; else BOT_STATUS="STOPPED"; fi
    BALANCE=""
    # Read position counts from JSON (source of truth)
    OPEN_POS=$(jq -r '[.trades[] | select(.status == "open")] | length' "$STATS_FILE" 2>/dev/null || echo "0")
    MAX_POS=${MAX_POSITIONS:-7}

    # Get P&L from closed trades in JSON (source of truth)
    CLOSED_COUNT=$(jq -r '[.trades[] | select(.status | startswith("closed"))] | length' "$STATS_FILE" 2>/dev/null || echo "0")
    GROSS_PNL=$(jq -r '[.trades[] | select(.status | startswith("closed")) | .pnlGross // 0] | add // 0' "$STATS_FILE" 2>/dev/null || echo "0")
    PNL_SOL=$(jq -r '[.trades[] | select(.status | startswith("closed")) | .pnl // 0] | add // 0' "$STATS_FILE" 2>/dev/null || echo "0")
    # Calculate P&L % vs starting balance
    if [[ -n "$PNL_SOL" && "$PNL_SOL" != "0" ]]; then
        PNL_PCT=$(awk "BEGIN {printf \"%.1f\", ($PNL_SOL / ${STARTING_BALANCE:-0.5}) * 100}" 2>/dev/null || echo "0")
    else
        PNL_PCT="0"
    fi

    # Get actual deployed capital and P&L from JSON (source of truth)
    STARTING_BAL=${STARTING_BALANCE:-0.5}
    DEPLOYED=$(jq -r '.trades | map(select(.status == "open")) | map(.amountIn) | add // 0' "$STATS_FILE" 2>/dev/null || echo "0")
    TOTAL_PNL_SOL=$(jq -r '.totalPnl // 0' "$STATS_FILE" 2>/dev/null || echo "0")
    # Free balance from JSON (not the log — log can mix paper/mainnet)
    BALANCE=$(jq -r '.balance // 0' "$STATS_FILE" 2>/dev/null || echo "$BALANCE")

    # Total Capital = free balance + deployed capital (what you actually have right now)
    # This correctly reflects unrealized losses/gains on open positions
    if [[ -n "$BALANCE" && -n "$DEPLOYED" ]]; then
        TOTAL_CAPITAL=$(printf "%.6f" $(echo "$BALANCE + $DEPLOYED" | bc))
        # Gain vs starting capital
        TOTAL_GAIN_SOL=$(echo "$TOTAL_CAPITAL - $STARTING_BAL" | bc)
        TOTAL_GAIN_PCT=$(awk "BEGIN {printf \"%.1f\", ($TOTAL_GAIN_SOL / $STARTING_BAL) * 100}" 2>/dev/null || echo "0")
    else
        TOTAL_CAPITAL="$BALANCE"
        TOTAL_GAIN_PCT="0"
    fi

    # ══════════════════════════════════════════════════════════
    # ACCOUNT OVERVIEW
    # ══════════════════════════════════════════════════════════
    print_section "ACCOUNT OVERVIEW"

    if [[ "$BOT_STATUS" == "RUNNING" ]]; then
        echo -e "${BOLD}Status:${NC} ${GREEN}● RUNNING${NC} ${DIM}(PID: $BOT_PID)${NC}"
    else
        echo -e "${BOLD}Status:${NC} ${RED}● STOPPED${NC}"
    fi

    echo ""
    echo -e "${BOLD}┌─ Capital Allocation ─────────────────────────────────────┐${NC}"
    printf "  %-25s ${WHITE}%10s${NC} SOL\n" "Starting Capital:" "$STARTING_BAL"
    printf "  %-25s ${CYAN}%10s${NC} SOL\n" "Free Balance:" "${BALANCE:-0.0000}"
    printf "  %-25s ${YELLOW}%10s${NC} SOL ${DIM}(%s/%s positions)${NC}\n" "Deployed Capital:" "${DEPLOYED:-0.0000}" "${OPEN_POS:-0}" "${MAX_POS:-7}"
    if [[ $(echo "${TOTAL_GAIN_PCT:-0} >= 0" | bc) -eq 1 ]]; then
        printf "  %-25s ${BOLD}%10s${NC} SOL ${GREEN}(+%s%%)${NC}\n" "Total Capital:" "${TOTAL_CAPITAL:-0.0000}" "${TOTAL_GAIN_PCT:-0}"
    else
        printf "  %-25s ${BOLD}%10s${NC} SOL ${RED}(%s%%)${NC}\n" "Total Capital:" "${TOTAL_CAPITAL:-0.0000}" "${TOTAL_GAIN_PCT:-0}"
    fi
    echo -e "${BOLD}└──────────────────────────────────────────────────────────┘${NC}"

    echo ""
    echo -e "${BOLD}┌─ Performance ────────────────────────────────────────────┐${NC}"
    if [[ -n "$PNL_SOL" ]]; then
        if [[ "$PNL_PCT" =~ ^- ]]; then
            printf "  %-25s ${RED}%10s${NC} SOL ${RED}(%s%%)${NC}\n" "Net P&L:" "$PNL_SOL" "$PNL_PCT"
        else
            printf "  %-25s ${GREEN}%10s${NC} SOL ${GREEN}(+%s%%)${NC}\n" "Net P&L:" "$PNL_SOL" "$PNL_PCT"
        fi
        printf "  %-25s ${DIM}%10s${NC} SOL\n" "Gross P&L:" "${GROSS_PNL:-N/A}"

        # Calculate fees
        if [[ -n "$GROSS_PNL" && -n "$PNL_SOL" ]]; then
            FEES=$(echo "$GROSS_PNL - $PNL_SOL" | bc 2>/dev/null || echo "0")
            printf "  %-25s ${RED}%10s${NC} SOL\n" "Fees Paid:" "$FEES"
        fi
    else
        echo -e "  ${YELLOW}No P&L data yet${NC}"
    fi
    echo -e "${BOLD}└──────────────────────────────────────────────────────────┘${NC}"

    # ══════════════════════════════════════════════════════════
    # OPEN POSITIONS
    # ══════════════════════════════════════════════════════════
    print_section "OPEN POSITIONS (${OPEN_POS:-0}/${MAX_POS:-7})"

    echo -e "${BOLD}┌──────────┬─────────┬────────┬───────┬──────────┬──────────┐${NC}"
    echo -e "${BOLD}│ TOKEN    │   P&L % │    AGE │  CONF │   TP1    │  STATUS  │${NC}"
    echo -e "${BOLD}├──────────┼─────────┼────────┼───────┼──────────┼──────────┤${NC}"

    POSITIONS_FOUND=0
    NOW_MS=$(date +%s%3N)

    # Read positions directly from JSON (always current, works for both paper and mainnet)
    while IFS=$'\t' read -r TOKEN PNL_RAW CONF TP1HIT AGE_MIN; do
        [[ -z "$TOKEN" ]] && continue
        POSITIONS_FOUND=$((POSITIONS_FOUND + 1))

        CURRENT_PNL=$(printf "%.0f" "$PNL_RAW" 2>/dev/null || echo "0")

        # TP1 from JSON field (sticky, written by bot)
        if [[ "$TP1HIT" == "true" ]]; then
            TP1_STATUS="${GREEN}✓ ACTIVE  ${NC}"
        else
            TP1_STATUS="${DIM}pending   ${NC}"
        fi

        # Status emoji
        if [[ $CURRENT_PNL -gt 50 ]]; then
            STATUS="🚀 MOON"
        elif [[ $CURRENT_PNL -gt 20 ]]; then
            STATUS="📈 UP  "
        elif [[ $CURRENT_PNL -gt 0 ]]; then
            STATUS="➚ GAIN"
        elif [[ $CURRENT_PNL -eq 0 ]]; then
            STATUS="━ FLAT"
        elif [[ $CURRENT_PNL -gt -10 ]]; then
            STATUS="➘ DOWN"
        elif [[ $CURRENT_PNL -gt -20 ]]; then
            STATUS="📉 LOSS"
        else
            STATUS="💀 RUG "
        fi

        echo -n "│ "
        printf "%-8s" "$TOKEN"
        echo -n " │ "
        if [[ $CURRENT_PNL -ge 0 ]]; then
            echo -ne "${GREEN}"; printf "%6s%%" "+${CURRENT_PNL}"; echo -ne "${NC}"
        else
            echo -ne "${RED}"; printf "%6s%%" "${CURRENT_PNL}"; echo -ne "${NC}"
        fi
        echo -n " │ "
        printf "%5s m" "$AGE_MIN"
        echo -n " │ "
        printf "%5s" "$CONF"
        echo -n " │ "
        echo -ne "$TP1_STATUS"
        echo -n "│ "
        printf "%-8s" "$STATUS"
        echo " │"

    done < <(jq -r --argjson now "$NOW_MS" '
        .trades[]
        | select(.status == "open")
        | [
            .tokenSymbol,
            ((.currentPrice - .entryPrice) / .entryPrice * 100),
            (.confidenceScore | tostring),
            (.tp1Hit | tostring),
            (($now - .timestamp) / 60000 | floor | tostring)
          ]
        | @tsv
    ' "$STATS_FILE" 2>/dev/null)

    if [[ $POSITIONS_FOUND -eq 0 ]]; then
        echo -e "│ ${YELLOW}No open positions${NC}                                                │"
    fi

    echo -e "${BOLD}└──────────┴─────────┴────────┴───────┴──────────┴──────────┘${NC}"
    echo -e "${DIM}TP1 = Trailing stop active after +100% gain${NC}"

    # ══════════════════════════════════════════════════════════
    # SCANNER STATUS
    # ══════════════════════════════════════════════════════════
    print_section "SCANNER STATUS"

    # Latest scan
    LATEST_SCAN=$(tail -50 "$LOG_FILE" 2>/dev/null | grep "DexScreener: Found" | tail -1)
    OPP_COUNT=$(echo "$LATEST_SCAN" | grep -oP 'Found \K\d+')
    TOP_SCORES=$(echo "$LATEST_SCAN" | grep -oP 'top scores: \[\K[^\]]+')

    # Latest confidence check
    LAST_CONF=$(tail -30 "$LOG_FILE" 2>/dev/null | grep "Confidence:" | tail -1 | grep -oP 'Confidence: \K\d+')
    LAST_SCORE=$(tail -30 "$LOG_FILE" 2>/dev/null | grep "Score:" | tail -1 | grep -oP 'Score: \K\d+')

    echo -e "${BOLD}┌─ Latest Scan ────────────────────────────────────────────┐${NC}"
    printf "  %-25s ${CYAN}%10s${NC}\n" "Opportunities Found:" "${OPP_COUNT:-0}"
    printf "  %-25s ${DIM}[%s]${NC}\n" "Top Scores:" "${TOP_SCORES:-N/A}"
    echo -e "${BOLD}└──────────────────────────────────────────────────────────┘${NC}"

    echo ""
    echo -e "${BOLD}┌─ Last Token Analyzed ────────────────────────────────────┐${NC}"
    printf "  %-25s ${YELLOW}%10s${NC}/100\n" "Scanner Score:" "${LAST_SCORE:-N/A}"
    printf "  %-25s " "Confidence Score:"

    if [[ -n "$LAST_CONF" ]]; then
        if [[ $LAST_CONF -ge 45 ]]; then
            echo -e "${GREEN}${LAST_CONF}${NC}/100 ${GREEN}✓ PASS${NC}"
        else
            echo -e "${RED}${LAST_CONF}${NC}/100 ${RED}✗ FAIL${NC} ${DIM}(need 45+)${NC}"
        fi
    else
        echo "N/A"
    fi
    echo -e "${BOLD}└──────────────────────────────────────────────────────────┘${NC}"

    # ══════════════════════════════════════════════════════════
    # ACTIVITY STATS
    # ══════════════════════════════════════════════════════════
    print_section "RECENT ACTIVITY (Last 100 Events)"

    TRADES=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "TRADE SIMULATED")
    SKIPS=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "SKIPPED: Low confidence")
    NO_TRADES=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "No trades taken")
    SCANS=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "Scanning for opportunities")

    echo -e "${BOLD}┌─────────────────────────┬──────────┐${NC}"
    echo -e "${BOLD}│ Event                   │    Count │${NC}"
    echo -e "${BOLD}├─────────────────────────┼──────────┤${NC}"
    printf "│ ${GREEN}✅ Trades Executed${NC}      │ ${GREEN}%8s${NC} │\n" "$TRADES"
    printf "│ ${RED}❌ Tokens Skipped${NC}       │ ${RED}%8s${NC} │\n" "$SKIPS"
    printf "│ ${YELLOW}⏭️  All Rejected${NC}         │ ${YELLOW}%8s${NC} │\n" "$NO_TRADES"
    printf "│ ${CYAN}🔍 Scans Completed${NC}      │ ${CYAN}%8s${NC} │\n" "$SCANS"
    echo -e "${BOLD}└─────────────────────────┴──────────┘${NC}"

    # Skip rate
    if [[ $SCANS -gt 0 ]]; then
        SKIP_RATE=$(echo "scale=1; ($SKIPS / $SCANS) * 100" | bc 2>/dev/null || echo "0")
        echo -e "\n${DIM}Skip Rate: ${RED}${SKIP_RATE}%${NC} ${DIM}of tokens fail confidence check${NC}"
    fi

    # ══════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${DIM}Refreshing every 3 seconds... Press Ctrl+C to exit${NC}"

    sleep ${REFRESH_INTERVAL:-3}
done
