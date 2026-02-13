#!/bin/bash
# Live P&L Dashboard - Updates every 5 seconds with current position status

echo "📊 LIVE P&L DASHBOARD"
echo "======================================"
echo "Updates every 5 seconds"
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

while true; do
  clear
  echo "📊 LIVE P&L DASHBOARD - $(date '+%H:%M:%S')"
  echo "======================================"
  echo ""

  # Extract latest position check from log
  latest_check=$(tail -200 /tmp/paper-trade-final.log 2>/dev/null | grep -a -A50 "Checking.*open position" | tail -50)

  if [ -z "$latest_check" ]; then
    echo "⏳ Waiting for first position check..."
  else
    # Extract each position block
    echo "$latest_check" | while IFS= read -r line; do
      # Token name
      if echo "$line" | grep -q "📊"; then
        token=$(echo "$line" | sed 's/.*📊 //' | sed 's/:.*//')
        echo ""
        echo "💎 $token"
        echo "   ────────────────────────"
      fi

      # Entry and Current price
      if echo "$line" | grep -q "Entry:"; then
        echo "   $line" | sed 's/^[[:space:]]*/   /'
      fi

      # P&L
      if echo "$line" | grep -q "P&L:"; then
        pnl_line=$(echo "$line" | sed 's/^[[:space:]]*/   /')
        # Color code P&L
        if echo "$line" | grep -q "+"; then
          echo "   ✅ $pnl_line"
        else
          echo "   ❌ $pnl_line"
        fi
      fi

      # Hold time
      if echo "$line" | grep -q "Hold time:"; then
        echo "   $line" | sed 's/^[[:space:]]*/   /'
      fi

      # Status
      if echo "$line" | grep -q "Holding\|EXITING"; then
        status=$(echo "$line" | sed 's/^[[:space:]]*//')
        if echo "$line" | grep -q "EXITING"; then
          echo "   🚪 $status"
        else
          echo "   ⏳ $status"
        fi
      fi
    done
  fi

  echo ""
  echo "======================================"

  # Overall stats
  balance=$(tail -50 /tmp/paper-trade-final.log 2>/dev/null | grep -a "Balance:" | tail -1 | grep -o "[0-9.]*" | head -1)
  total_pnl=$(tail -50 /tmp/paper-trade-final.log 2>/dev/null | grep -a "P&L:" | tail -1)

  if [ -n "$balance" ]; then
    echo "💰 Current Balance: $balance SOL"
  fi

  if [ -n "$total_pnl" ]; then
    echo "📊 Total $total_pnl" | sed 's/.*P&L:/P&L:/'
  fi

  echo ""
  echo "Next update in 5 seconds..."

  sleep 5
done
