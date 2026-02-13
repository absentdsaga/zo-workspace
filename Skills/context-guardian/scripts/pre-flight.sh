#!/bin/bash
# Pre-flight check before making changes

set -e

CONTEXT_DIR=".context"

if [ ! -d "$CONTEXT_DIR" ]; then
    echo "❌ Context Guardian not initialized. Run init-project.sh first."
    exit 1
fi

echo "🔍 PRE-FLIGHT CHECK"
echo "=================="
echo ""

echo "📋 Reading current state..."
echo ""
echo "=== WHAT'S WORKING ===" 
grep -A 20 "## Current Working State" "$CONTEXT_DIR/state-snapshot.md" | grep -v "^##" || echo "[Not documented yet]"
echo ""

echo "=== DO NOT CHANGE ==="
grep -A 10 "## Do NOT Change" "$CONTEXT_DIR/state-snapshot.md" | grep -v "^##" || echo "[Not documented yet]"
echo ""

echo "=== RECENT DECISIONS ==="
tail -20 "$CONTEXT_DIR/decisions.md"
echo ""

echo "⚠️  Before proceeding:"
echo "   1. What are you about to change?"
echo "   2. Could this break anything in 'Current Working State'?"
echo "   3. Does this align with decisions in decisions.md?"
echo "   4. Do you need to add a verification test?"
echo ""
echo "✅ Pre-flight check complete. Proceed with caution."
