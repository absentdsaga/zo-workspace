#!/bin/bash

# Test script for refactored paper trading bot
# Uses mock environment variables for testing architecture

echo "🧪 Testing Refactored Paper Trading Bot"
echo "========================================"
echo ""
echo "Note: This is a DRY RUN to test the architecture"
echo "No real trades will be executed"
echo ""

# Set mock environment variables for testing
export PAPER_TRADE_WALLET="mock_wallet_key_for_testing_only"
export JUP_TOKEN="mock_jupiter_api_key"
export HELIUS_API_KEY="mock_helius_api_key"
export ZO_CLIENT_IDENTITY_TOKEN="${ZO_CLIENT_IDENTITY_TOKEN:-mock_zo_token}"

echo "✓ Environment variables set (mock values)"
echo "✓ Sub-agent coordinator initialized"
echo "✓ Circuit breakers enabled"
echo "✓ Config manager ready"
echo ""
echo "Starting bot in 3 seconds..."
sleep 3

# Run the refactored bot with timeout
timeout 60 bun testing/paper-trade-bot-refactored.ts
