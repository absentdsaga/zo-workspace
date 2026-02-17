#!/bin/bash

echo "🔄 Resetting Paper Trading Stats"
echo "================================="
echo ""

# Backup old data
BACKUP_DIR="/tmp/paper-backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f /tmp/paper-trades-master.json ]; then
  cp /tmp/paper-trades-master.json "$BACKUP_DIR/"
  echo "✅ Backed up trades to: $BACKUP_DIR/paper-trades-master.json"
fi

if [ -f /tmp/paper-trades-state.json ]; then
  cp /tmp/paper-trades-state.json "$BACKUP_DIR/"
  echo "✅ Backed up state to: $BACKUP_DIR/paper-trades-state.json"
fi

if [ -f /tmp/paper-trades-blacklist.json ]; then
  cp /tmp/paper-trades-blacklist.json "$BACKUP_DIR/"
  echo "✅ Backed up blacklist to: $BACKUP_DIR/paper-trades-blacklist.json"
fi

# Reset state (keep blacklist)
echo ""
echo "🗑️  Clearing trade data..."

cat > /tmp/paper-trades-state.json << 'EOFSTATE'
{
  "startingBalance": 0.5,
  "currentBalance": 0.5,
  "totalRefills": 0,
  "lastUpdated": $(date +%s)000
}
EOFSTATE

echo '{"balance":0.5,"totalPnl":0,"totalRefills":0,"trades":[]}' > /tmp/paper-trades-master.json

echo "✅ Reset state: 0.5 SOL starting balance"
echo "✅ Cleared all trades"
echo ""
echo "📊 Stats Reset Complete!"
echo ""
echo "Previous data backed up to: $BACKUP_DIR"
echo ""
echo "🚀 Ready to start fresh with real Jito costs (p75: $0.0088/trade)"
