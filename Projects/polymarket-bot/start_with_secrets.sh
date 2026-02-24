#!/bin/bash

# Start Polymarket Bot with Zo Secrets
# This script loads API credentials from Zo secrets and starts the bot

set -e

cd /home/workspace/Projects/polymarket-bot

echo "🔑 Loading Polymarket API credentials from Zo secrets..."

# Source Zo secrets file
if [ -f /root/.zo_secrets ]; then
    source /root/.zo_secrets
    echo "✅ Loaded secrets from /root/.zo_secrets"
else
    echo "❌ Error: /root/.zo_secrets not found"
    exit 1
fi

# Check if secrets are available
if [ -z "$POLYMARKET_API_KEY" ]; then
    echo "❌ Error: POLYMARKET_API_KEY not found in environment"
    echo ""
    echo "Please ensure you've added these secrets in Zo:"
    echo "  - POLYMARKET_API_KEY"
    echo "  - POLYMARKET_API_SECRET"
    echo "  - POLYMARKET_API_PASSPHRASE"
    echo ""
    echo "To add them:"
    echo "  1. Go to Zo settings/secrets"
    echo "  2. Add each secret with exact name above"
    echo "  3. Restart this script"
    exit 1
fi

echo "✅ API Key found: ${POLYMARKET_API_KEY:0:10}..."
echo "✅ API Secret found: ${POLYMARKET_API_SECRET:0:10}..."
echo "✅ Passphrase found: ${POLYMARKET_API_PASSPHRASE:0:5}..."
echo ""

# Stop any running bot
pkill -f paper_trading_websocket.py || true
sleep 2

echo "🚀 Starting paper trading bot with authentication..."
echo ""

# Start bot with secrets in environment
export POLYMARKET_API_KEY
export POLYMARKET_API_SECRET
export POLYMARKET_API_PASSPHRASE

echo "100" | /usr/local/bin/python3 paper_trading_websocket.py > paper_trading_ws.log 2>&1 &

BOT_PID=$!
echo "✅ Bot started (PID: $BOT_PID)"
echo ""
echo "📊 Monitor with:"
echo "   tail -f paper_trading_ws.log"
echo ""
echo "Check status in 5 seconds..."
sleep 5

# Check if bot is still running
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running"
    echo ""
    echo "Recent logs:"
    tail -20 paper_trading_ws.log
else
    echo "❌ Bot stopped unexpectedly"
    echo ""
    echo "Error logs:"
    tail -50 paper_trading_ws.log
    exit 1
fi
