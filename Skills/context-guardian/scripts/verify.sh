#!/bin/bash
# Run verification checklist

set -e

CONTEXT_DIR=".context"

if [ ! -d "$CONTEXT_DIR" ]; then
    echo "❌ Context Guardian not initialized. Run init-project.sh first."
    exit 1
fi

echo "✓ Running verification checklist..."
echo ""

cat "$CONTEXT_DIR/verification-checklist.md"

echo ""
echo "🎯 Manual verification required:"
echo "   Go through checklist above and verify each item"
echo ""
echo "📝 After verification:"
echo "   Update 'Last Verified' section with results"
echo "   If any tests failed, document in state-snapshot.md"
