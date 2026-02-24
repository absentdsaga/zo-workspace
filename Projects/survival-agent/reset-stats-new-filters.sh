#!/bin/bash
# Reset paper trading stats for NEW filter test

echo "🔄 Resetting paper trading stats..."

# Backup old stats with descriptive name
timestamp=$(date +%Y%m%d_%H%M%S)
echo "📦 Backing up old stats to /tmp/paper-trades-OLD-FILTERS-${timestamp}.json"
cp /tmp/paper-trades-master.json /tmp/paper-trades-OLD-FILTERS-${timestamp}.json 2>/dev/null
cp /tmp/paper-trades-state.json /tmp/paper-trades-state-OLD-FILTERS-${timestamp}.json 2>/dev/null
cp /tmp/paper-trades-blacklist.json /tmp/paper-trades-blacklist-OLD-FILTERS-${timestamp}.json 2>/dev/null

# Stop bot
echo "🛑 Stopping paper bot..."
pkill -f paper-trade-bot

# Reset files
echo "🆕 Creating fresh state files..."
cat > /tmp/paper-trades-master.json << 'EOF'
{
  "balance": 1.0,
  "totalPnl": 0,
  "totalRefills": 0,
  "trades": []
}
EOF

cat > /tmp/paper-trades-state.json << 'EOF'
{
  "startingBalance": 1.0,
  "currentBalance": 1.0,
  "totalRefills": 0
}
EOF

cat > /tmp/paper-trades-blacklist.json << 'EOF'
{
  "ruggedTokens": [],
  "threeConsecutiveLosses": []
}
EOF

echo "✅ Stats reset complete!"
echo ""
echo "📊 Old stats backed up:"
ls -lh /tmp/paper-trades-OLD-FILTERS-${timestamp}*.json
echo ""
echo "🆕 New stats initialized:"
cat /tmp/paper-trades-master.json | jq '{balance, totalPnl, trades: (.trades | length)}'
echo ""
echo "🚀 To restart bot, run:"
echo "   cd /home/workspace/Projects/survival-agent && source ~/.zo_secrets && nohup bun testing/paper-trade-bot.ts > /dev/shm/paper-trade-bot-NEW-FILTERS.log 2>&1 &"
