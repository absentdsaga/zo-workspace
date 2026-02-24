#!/bin/bash
cd /home/workspace/Projects/polymarket-bot
echo "🤖 Starting Polymarket 5-Minute Bot..."
echo "📍 Watching BTC Up/Down 5-min markets"
echo "⏸️  Press Ctrl+C to stop"
echo ""
/usr/local/bin/python3 -u HYBRID_bot.py
