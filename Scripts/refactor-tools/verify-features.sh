#!/bin/bash
# Verify all features from original are in refactored
ORIGINAL=$1
REFACTORED=$2

if [ -z "$ORIGINAL" ] || [ -z "$REFACTORED" ]; then
  echo "Usage: $0 <original-file> <refactored-file>"
  exit 1
fi

echo "=== Extracting features from original ==="
grep -oP '(private|public|async|const).*(?=\(|=|:)' "$ORIGINAL" | sort | uniq > /tmp/original-features.txt

echo "=== Extracting features from refactored ==="
grep -oP '(private|public|async|const).*(?=\(|=|:)' "$REFACTORED" | sort | uniq > /tmp/refactored-features.txt

echo "=== Features REMOVED (should be ZERO) ==="
diff /tmp/original-features.txt /tmp/refactored-features.txt | grep "^<" || echo "✅ No features removed"

echo "=== Features ADDED ==="
diff /tmp/original-features.txt /tmp/refactored-features.txt | grep "^>" || echo "No new features"
