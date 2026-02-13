#!/bin/bash
# Fix sprite alignment by ensuring consistent character positioning in frames

set -e

SPRITE_DIR="/home/workspace/Skills/spatial-worlds/assets/sprites/nft-characters"

echo "Fixing sprite alignment for all character sets..."

for char_dir in "$SPRITE_DIR"/set*-char*; do
    if [ -d "$char_dir" ]; then
        echo "Processing: $(basename "$char_dir")"

        # Process all individual PNG frames
        for frame in "$char_dir"/*.png; do
            # Skip sheet files
            if [[ "$frame" == *"-sheet.png" ]]; then
                continue
            fi

            if [ -f "$frame" ]; then
                # Trim whitespace and re-center in 32x48 frame with feet at bottom
                convert "$frame" \
                    -trim \
                    -gravity south \
                    -background none \
                    -extent 32x48 \
                    "$frame"
            fi
        done

        # Regenerate the sprite sheet
        echo "Regenerating sprite sheet for $(basename "$char_dir")..."
        montage "$char_dir"/right-walk-*.png "$char_dir"/left-walk-*.png \
                "$char_dir"/up-walk-*.png "$char_dir"/down-walk-*.png \
                -tile 4x4 -geometry 32x48+0+0 -background none \
                "$char_dir/$(basename "$char_dir")-sheet.png"

        echo "✓ Fixed $(basename "$char_dir")"
    fi
done

echo "All sprite alignment fixed!"
