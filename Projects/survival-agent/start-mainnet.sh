#!/bin/bash
# Start the MAINNET trading bot
# Runs the same code as paper-trade-bot.ts but with mainnet.config.ts

set -e
cd "$(dirname "$0")"

echo "🔴 MAINNET TRADING BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  REAL MONEY - LIVE TRANSACTIONS ON SOLANA MAINNET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Settings:"
echo "  Max positions:  3  (paper: 7)"
echo "  Position size:  5%  (paper: 12%)"
echo "  Stop loss:      -20%  (paper: -30%)"
echo "  Starting bal:   0.1 SOL"
echo "  Log:            /tmp/mainnet-trade.log"
echo ""

# Load secrets
source ~/.zo_secrets 2>/dev/null || source ~/.bashrc 2>/dev/null

# Check required env vars
if [ -z "$JUP_TOKEN" ] || [ -z "$HELIUS_API_KEY" ]; then
  echo "❌ Missing env vars. Need: JUP_TOKEN, HELIUS_API_KEY"
  echo "   Also need: MAINNET_PRIVATE_KEY (or SOLANA_PRIVATE_KEY)"
  exit 1
fi

WALLET_KEY="${MAINNET_PRIVATE_KEY:-$SOLANA_PRIVATE_KEY}"
if [ -z "$WALLET_KEY" ]; then
  echo "❌ No wallet key found. Set MAINNET_PRIVATE_KEY in ~/.zo_secrets"
  exit 1
fi

if [ -z "$MAINNET_PRIVATE_KEY" ]; then
  echo "⚠️  Using SOLANA_PRIVATE_KEY. Recommend setting MAINNET_PRIVATE_KEY separately."
fi

# Kill any existing mainnet process
pkill -f "mainnet-trade-bot" 2>/dev/null || true
sleep 1

# Build a temporary mainnet version of the bot by swapping the config import
# This ensures 100% identical code to paper-trade-bot.ts, just different config
MAINNET_BOT="/tmp/mainnet-trade-bot.ts"
sed 's|from '"'"'../config/paper.config'"'"'|from '"'"'../config/mainnet.config'"'"'|g' \
    testing/paper-trade-bot.ts > "$MAINNET_BOT"

echo "✅ Mainnet bot built (config swapped to mainnet.config.ts)"
echo "⚡ Starting in 5 seconds... Ctrl+C to abort"
echo ""
sleep 5

# Start the bot
LOG_FILE="/tmp/mainnet-trade.log"
MAINNET_PRIVATE_KEY="$WALLET_KEY" \
  nohup bun run "$MAINNET_BOT" > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ Started with PID: $PID"
echo "📝 Log: $LOG_FILE"
echo "📊 Dashboard: bash monitoring/dashboard.sh mainnet"
echo ""
echo "Stop with: pkill -f mainnet-trade-bot"
