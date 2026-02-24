#!/bin/bash

# Continuous Paper Trading Bot Monitor
# Refreshes every 5 seconds

while true; do
  clear
  echo "=================================================="
  echo "📊 PAPER TRADING BOT - LIVE MONITOR"
  echo "   $(date '+%Y-%m-%d %H:%M:%S')"
  echo "=================================================="
  echo ""

  # Check if bot is running
  if pgrep -f "paper-trade-bot.ts" > /dev/null; then
    PID=$(pgrep -f 'paper-trade-bot.ts')
    UPTIME=$(ps -p $PID -o etime= | tr -d ' ')
    echo "✅ Bot Status: RUNNING (PID: $PID, Uptime: $UPTIME)"
  else
    echo "❌ Bot Status: STOPPED"
    echo ""
    echo "To start: cd /home/workspace/Projects/survival-agent && source /root/.zo_secrets && nohup bun testing/paper-trade-bot.ts > /tmp/paper-trade-bot.log 2>&1 &"
    sleep 5
    continue
  fi

  echo ""

  # Parse JSON data
  DATA=$(cat /tmp/paper-trades-master.json)

  # Balance info
  BALANCE=$(echo "$DATA" | jq -r '.balance')
  STARTING=$(echo "$DATA" | jq -r '.startingBalance // 0.5')
  PNL=$(echo "$BALANCE - $STARTING" | bc -l)
  PNL_PCT=$(echo "scale=2; ($PNL / $STARTING) * 100" | bc -l)

  echo "💰 Balance: ${BALANCE} SOL"
  echo "📊 P&L: ${PNL} SOL (${PNL_PCT}%)"

  # Position count
  OPEN_COUNT=$(echo "$DATA" | jq '.trades | map(select(.status == "open")) | length')
  TOTAL_TRADES=$(echo "$DATA" | jq '.trades | length')
  
  echo "📈 Positions: ${OPEN_COUNT}/7 open | ${TOTAL_TRADES} total trades"

  # Win/Loss stats
  WINS=$(echo "$DATA" | jq '[.trades[] | select(.status == "closed_profit")] | length')
  LOSSES=$(echo "$DATA" | jq '[.trades[] | select(.status == "closed_loss")] | length')
  if [ $((WINS + LOSSES)) -gt 0 ]; then
    WIN_RATE=$(echo "scale=1; ($WINS / ($WINS + $LOSSES)) * 100" | bc -l)
    echo "🎯 Win Rate: ${WIN_RATE}% (${WINS}W / ${LOSSES}L)"
  fi

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "OPEN POSITIONS (RUNNERS)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # Show open positions
  echo "$DATA" | jq -r '.trades | map(select(.status == "open")) | sort_by(.timestamp) | reverse | .[] |
    "\(.tokenSymbol) [\(.source)] - Conf:\(.confidenceScore)%
    💵 Entry: $\(.entryPrice) → Current: $\(.currentPrice)
    📊 P&L: \(((.currentPrice - .entryPrice) / .entryPrice * 100) | floor)% | Peak: \(((.peakPrice - .entryPrice) / .entryPrice * 100) | floor)%
    \(if .tp1Hit then "🎯 TP1 HIT - Trailing stop active (20% from peak)" else "⏳ Pre-TP1 (Stop: -30%)" end)
    Age: \(((now * 1000 - .timestamp) / 60000) | floor) min
    ────────────────────────────────────────────────"'

  if [ "$OPEN_COUNT" -eq 0 ]; then
    echo "No open positions"
    echo "────────────────────────────────────────────────"
  fi

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "RECENT EXITS (Last 3)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  echo "$DATA" | jq -r '.trades | map(select(.status | startswith("closed"))) | sort_by(.exitTimestamp) | reverse | .[0:3] | .[] |
    "\(.tokenSymbol) - \(if .status == "closed_profit" then "✅ PROFIT" else "❌ LOSS" end)
    P&L: \(((.pnl / .amountIn) * 100) | floor)% (\(.pnl) SOL)
    \(if .tp1Hit then "🎯 Hit TP1, exited on trailing stop" else "" end)
    Exit: \(.exitReason)
    ────────────────────────────────────────────────"'

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "RECENT SCANNER ACTIVITY (Last 10 lines)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  tail -30 /tmp/paper-trade-bot.log | grep -E "SCANNER|Pump.fun:|DexScreener:|✅ TRADE|SKIPPED.*Low confidence" | tail -10

  echo ""
  echo "=================================================="
  echo "Refreshing in 5s... (Ctrl+C to exit)"
  echo "=================================================="

  sleep 5
done
