#!/bin/bash
# Batch process all 24 NFT character sprites to add transparency
# Uses the formula proven to work in Phase 1

set -e  # Exit on error

cd "$(dirname "$0")"

echo "🎨 NFT Sprite Batch Transparency Processing"
echo "==========================================="
echo ""

total=24
processed=0
skipped=0
errors=0

for set in 1 2 3 4; do
    for char in 1 2 3 4 5 6; do
        sprite="set${set}-char${char}"
        input="assets/sprites/nft-characters-hd/${sprite}/${sprite}-sheet.png"
        output="assets/sprites/nft-characters-hd/${sprite}/${sprite}-sheet-transparent.png"

        # Skip if already exists
        if [ -f "$output" ]; then
            echo "⏭️  ${sprite} - already processed, skipping"
            ((skipped++))
            continue
        fi

        # Check if input exists
        if [ ! -f "$input" ]; then
            echo "❌ ${sprite} - input file not found!"
            ((errors++))
            continue
        fi

        echo -n "🔄 ${sprite} - processing... "

        # Apply transparency using proven formula
        convert "$input" \
          -fuzz 15% \
          -transparent "srgba(158,131,100,1)" \
          "$output"

        # Verify output
        if [ -f "$output" ]; then
            # Check for alpha channel
            alpha_check=$(identify -verbose "$output" | grep "Type:" | grep -c "Alpha" || true)
            if [ "$alpha_check" -gt 0 ]; then
                echo "✅ done"
                ((processed++))
            else
                echo "⚠️  warning - no alpha channel detected"
                ((errors++))
            fi
        else
            echo "❌ failed"
            ((errors++))
        fi
    done
done

echo ""
echo "==========================================="
echo "📊 Summary:"
echo "  Total sprites: $total"
echo "  Processed: $processed"
echo "  Skipped (already done): $skipped"
echo "  Errors: $errors"
echo ""

if [ $errors -eq 0 ]; then
    echo "✅ All sprites processed successfully!"
    exit 0
else
    echo "⚠️  Some errors occurred. Check output above."
    exit 1
fi
