#!/bin/bash
# Update state snapshot after changes

set -e

CONTEXT_DIR=".context"
MESSAGE="${1:-State update}"

if [ ! -d "$CONTEXT_DIR" ]; then
    echo "❌ Context Guardian not initialized. Run init-project.sh first."
    exit 1
fi

echo "📝 Updating state snapshot: $MESSAGE"

# Update timestamp in state-snapshot.md
TEMP_FILE=$(mktemp)
sed "s/\*Last Updated:.*/\*Last Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")*/" \
    "$CONTEXT_DIR/state-snapshot.md" > "$TEMP_FILE"
mv "$TEMP_FILE" "$CONTEXT_DIR/state-snapshot.md"

# Add to build history
echo "$(date -u +"%Y-%m-%d %H:%M:%S UTC"): $MESSAGE" >> "$CONTEXT_DIR/state-snapshot.md"

# Open for editing
echo ""
echo "✏️  Update the following sections in state-snapshot.md:"
echo "   - Current Working State"
echo "   - What Works and WHY"
echo "   - Do NOT Change (if new patterns emerged)"
echo ""
echo "💾 File: $CONTEXT_DIR/state-snapshot.md"

# Show current state for review
echo ""
echo "=== Current State Snapshot ==="
cat "$CONTEXT_DIR/state-snapshot.md"
echo "=============================="
echo ""
echo "✅ State updated with timestamp"
