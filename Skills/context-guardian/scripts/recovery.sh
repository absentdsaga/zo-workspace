#!/bin/bash
# Emergency recovery when things break

set -e

CONTEXT_DIR=".context"

if [ ! -d "$CONTEXT_DIR" ]; then
    echo "❌ Context Guardian not initialized. Cannot recover."
    exit 1
fi

echo "🚨 EMERGENCY RECOVERY MODE"
echo "========================="
echo ""

echo "📜 Build history:"
grep -E "^[0-9]{4}-" "$CONTEXT_DIR/state-snapshot.md" | tail -10
echo ""

echo "🔍 Checking git history of state files..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo ""
    echo "Recent state changes:"
    git log --oneline -5 -- .context/
    echo ""
    echo "Last known good state snapshot:"
    git log -1 -p -- .context/state-snapshot.md | head -50
else
    echo "⚠️  Not a git repository. Cannot show history."
fi

echo ""
echo "🎯 Recovery options:"
echo ""
echo "1. Review state-snapshot.md for last known good configuration:"
echo "   cat $CONTEXT_DIR/state-snapshot.md"
echo ""
echo "2. Check what changed recently:"
echo "   git diff HEAD~3 HEAD"
echo ""
echo "3. Review decisions to understand original intent:"
echo "   cat $CONTEXT_DIR/decisions.md"
echo ""
echo "4. Restore from git if needed:"
echo "   git checkout HEAD~N -- [broken-file]"
echo ""
echo "5. Document what went wrong in decisions.md to prevent recurrence"
