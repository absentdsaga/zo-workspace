#!/bin/bash
# Batch convert all NFT character sets to CT sprites

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTER="$SCRIPT_DIR/nft-to-ct-simple.sh"
INPUT_DIR="/home/.z/chat-images"
OUTPUT_DIR="assets/sprites/nft-characters"

echo "🎮 NFT Character Set Batch Converter"
echo "========================================"
echo ""

# Process each character set image
# First, split the grid images into individual characters

process_grid() {
    local input_file="$1"
    local set_name="$2"
    local cols="$3"
    local rows="$4"

    echo "📦 Processing $set_name ($cols x $rows grid)..."

    # Get image dimensions
    dimensions=$(identify -format "%wx%h" "$input_file")
    width=$(echo $dimensions | cut -d'x' -f1)
    height=$(echo $dimensions | cut -d'x' -f2)

    char_width=$((width / cols))
    char_height=$((height / rows))

    char_num=1
    for ((row=0; row<rows; row++)); do
        for ((col=0; col<cols; col++)); do
            x=$((col * char_width))
            y=$((row * char_height))

            echo "  Extracting character $char_num..."

            # Extract individual character
            temp_file="/tmp/${set_name}-char${char_num}.png"
            convert "$input_file" \
                -crop "${char_width}x${char_height}+${x}+${y}" \
                +repage \
                "$temp_file"

            # Convert to CT sprite
            char_name="${set_name}-char${char_num}"
            $CONVERTER "$temp_file" "$char_name" "$OUTPUT_DIR"

            rm -f "$temp_file"
            ((char_num++))
        done
    done

    echo ""
}

# Process all character sets (3x2 grids = 6 characters each)
process_grid "$INPUT_DIR/set 1.png" "set1" 3 2
process_grid "$INPUT_DIR/set 2.png" "set2" 3 2
process_grid "$INPUT_DIR/set 3.png" "set3" 3 2
process_grid "$INPUT_DIR/set 4.png" "set4" 3 2

# Process single character
echo "🎯 Processing single character..."
$CONVERTER "$INPUT_DIR/single 1.png" "single1-cat" "$OUTPUT_DIR"

echo ""
echo "🎉 All conversions complete!"
echo "📁 Output directory: $OUTPUT_DIR"
echo ""
echo "Character count:"
ls -1 "$OUTPUT_DIR" | wc -l
echo ""
