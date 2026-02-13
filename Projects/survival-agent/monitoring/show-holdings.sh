#!/bin/bash
# Show current paper trading holdings with live P&L

echo "📊 PAPER TRADING HOLDINGS"
echo "======================================"
echo ""

# Extract all trades from log
echo "Analyzing trade log..."
echo ""

# Count total trades
total_trades=$(grep -a "SIMULATED SUCCESSFULLY" /tmp/paper-trade-final.log 2>/dev/null | wc -l)

# Get last balance
last_balance=$(grep -a "Balance:" /tmp/paper-trade-final.log 2>/dev/null | tail -1 | grep -o "[0-9.]*" | head -1)

# Get starting balance (first occurrence)
starting_balance=$(grep -a "Starting balance:" /tmp/paper-trade-final.log 2>/dev/null | head -1 | grep -o "[0-9.]*" | head -1)

# Calculate P&L
if [ -n "$starting_balance" ] && [ -n "$last_balance" ]; then
  pnl=$(echo "$last_balance - $starting_balance" | bc)
  pnl_pct=$(echo "scale=2; ($pnl / $starting_balance) * 100" | bc)
else
  pnl="0.0000"
  pnl_pct="0.00"
fi

echo "💰 PORTFOLIO SUMMARY"
echo "------------------------------------"
echo "Starting Balance: ${starting_balance:-0.0000} SOL"
echo "Current Balance:  ${last_balance:-0.0000} SOL"
echo "Total P&L:        $pnl SOL ($pnl_pct%)"
echo "Total Trades:     $total_trades"
echo ""

echo "🎯 OPEN POSITIONS"
echo "------------------------------------"

# Extract unique tokens bought
grep -a -B10 "EXECUTING TRADE" /tmp/paper-trade-final.log 2>/dev/null | \
  grep -a "Token:" | \
  sed 's/.*Token: //' | \
  sed 's/ (.*//' | \
  sort | uniq -c | \
  while read count token; do
    echo "• $token - $count positions open"
  done

echo ""
echo "📈 LATEST ACTIVITY"
echo "------------------------------------"
tail -20 /tmp/paper-trade-final.log 2>/dev/null | cat -v | grep -a "Balance:\|P&L:\|Trades:"

echo ""
echo "======================================"
echo "Run: tail -f /tmp/paper-trade-final.log | cat -v"
echo "for live updates"
