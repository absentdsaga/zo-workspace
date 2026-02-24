#!/bin/bash
# Compare log patterns between original and refactored
ORIGINAL_LOG=$1
REFACTORED_LOG=$2

if [ -z "$ORIGINAL_LOG" ] || [ -z "$REFACTORED_LOG" ]; then
  echo "Usage: $0 <original-log> <refactored-log>"
  exit 1
fi

echo "=== Original log patterns ==="
grep "📊\|📈\|⚠️\|✅\|❌" "$ORIGINAL_LOG" | head -30

echo ""
echo "=== Refactored log patterns ==="
grep "📊\|📈\|⚠️\|✅\|❌" "$REFACTORED_LOG" | head -30

echo ""
echo "=== Pattern diff ==="
diff <(grep "📊\|📈\|⚠️" "$ORIGINAL_LOG" | cut -d' ' -f3- | sort | uniq) \
     <(grep "📊\|📈\|⚠️" "$REFACTORED_LOG" | cut -d' ' -f3- | sort | uniq) || echo "✅ Patterns match"
