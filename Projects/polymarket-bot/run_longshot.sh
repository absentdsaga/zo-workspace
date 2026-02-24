#!/bin/bash
# Launcher for Polymarket Longshot Bot

echo "🚀 Starting Polymarket Longshot Bot..."
echo "📊 Strategy: Buy everything under 5¢"
echo "💰 Paper Trading Mode: ON"
echo ""

cd /home/workspace/Projects/polymarket-bot
/usr/local/bin/python3 longshot_bot.py
