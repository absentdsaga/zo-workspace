#!/bin/bash
# Reset mainnet JSON state to match actual on-chain wallet balance.
# Run this after manually selling stranded tokens, before restarting the bot.
#
# Usage: bash reset-mainnet-state.sh

TRADES_FILE="/home/workspace/Projects/survival-agent/data/mainnet-trades-master.json"
STATE_FILE="/home/workspace/Projects/survival-agent/data/mainnet-trades-state.json"
BLACKLIST_FILE="/home/workspace/Projects/survival-agent/data/mainnet-trades-blacklist.json"

# Archive old state before wiping
ARCHIVE_DIR="/tmp/mainnet-archive-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ARCHIVE_DIR"
cp "$TRADES_FILE" "$ARCHIVE_DIR/" 2>/dev/null && echo "📦 Archived old trades to $ARCHIVE_DIR"
cp "$STATE_FILE"  "$ARCHIVE_DIR/" 2>/dev/null
cp "$BLACKLIST_FILE" "$ARCHIVE_DIR/" 2>/dev/null

# Real on-chain balance (update this if it changes before you run the bot)
REAL_BALANCE=0.297

echo ""
echo "⚠️  This will reset the mainnet JSON state."
echo "    Starting balance will be set to: $REAL_BALANCE SOL (current on-chain balance)"
echo "    All trade history will be cleared."
echo ""
read -p "Type 'yes' to confirm: " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
    echo "Aborted."
    exit 0
fi

# Write fresh trades file
cat > "$TRADES_FILE" << EOF
{
  "balance": $REAL_BALANCE,
  "totalPnl": 0,
  "trades": [],
  "resetAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "resetReason": "Manual reset after sell-execution bug fix"
}
EOF

# Write fresh state file
cat > "$STATE_FILE" << EOF
{
  "lastScanTime": 0,
  "lastMonitorTime": 0
}
EOF

# Keep blacklist intact (tokens we know are bad should stay blocked)
if [[ ! -f "$BLACKLIST_FILE" ]]; then
    echo '{"rugged":[],"threeStrike":[]}' > "$BLACKLIST_FILE"
fi

echo ""
echo "✅ Reset complete."
echo "   Trades file:    $TRADES_FILE  (balance=$REAL_BALANCE SOL, 0 trades)"
echo "   State file:     $STATE_FILE"
echo "   Blacklist:      $BLACKLIST_FILE  (preserved)"
echo "   Archive:        $ARCHIVE_DIR"
echo ""
echo "Next: run  bash start-mainnet.sh  to start the bot fresh."
