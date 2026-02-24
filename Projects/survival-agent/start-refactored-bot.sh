#!/bin/bash

# Start refactored paper trading bot
# This script runs the bot with proper environment

echo "🚀 Starting REFACTORED Paper Trading Bot..."
echo "==========================================="
echo ""

cd /home/workspace/Projects/survival-agent

# The bot will read credentials from Zo environment
# No need to set them here - they're already available via secrets

# Run the bot
exec bun testing/paper-trade-bot-refactored.ts
