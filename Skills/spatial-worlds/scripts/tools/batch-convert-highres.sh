#!/bin/bash
# Batch convert all NFT characters to HIGH-RES CT sprites
# Choose size: 96x144 (2x) or 128x192 (4x)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTER="$SCRIPT_DIR/nft-to-ct-highres.sh"
INPUT_DIR="/home/.z/chat-images"
SIZE="${1:-96x144}"  # Default 96x144, pass 128x192 for ultra HD

if [[ "$SIZE" == "128x192" ]]; then
    OUTPUT_DIR="assets/sprites/nft-characters-ultrahd"
    echo "🎮 NFT Character HD Converter - ULTRA HD (128x192)"
elif [[ "$SIZE" == "112x168" ]]; then
    OUTPUT_DIR="assets/sprites/nft-characters-xxl"
    echo "🎮 NFT Character HD Converter - 90% MAX (112x168)"
else
    OUTPUT_DIR="assets/sprites/nft-characters-xl"
    echo "🎮 NFT Character HD Converter - HIGH RES (96x144)"
fi

echo "========================================"
echo ""

process_grid() {
    local input_file="$1"
    local set_name="$2"
    local cols="$3"
    local rows="$4"

    echo "📦 Processing $set_name ($cols x $rows grid)..."

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

            temp_file="/tmp/${set_name}-char${char_num}-hd.png"
            convert "$input_file" \
                -crop "${char_width}x${char_height}+${x}+${y}" \
                +repage \
                "$temp_file"

            char_name="${set_name}-char${char_num}"
            $CONVERTER "$temp_file" "$char_name" "$SIZE" "$OUTPUT_DIR"

            rm -f "$temp_file"
            ((char_num++))
        done
    done

    echo ""
}

# Process all character sets
process_grid "$INPUT_DIR/set 1.png" "set1" 3 2
process_grid "$INPUT_DIR/set 2.png" "set2" 3 2
process_grid "$INPUT_DIR/set 3.png" "set3" 3 2
process_grid "$INPUT_DIR/set 4.png" "set4" 3 2

# Process single character
echo "🎯 Processing single character..."
$CONVERTER "$INPUT_DIR/single 1.png" "single1-cat" "$SIZE" "$OUTPUT_DIR"

echo ""
echo "🎉 All HD conversions complete!"
echo "📁 Output directory: $OUTPUT_DIR"
echo "📏 Sprite size: $SIZE"
echo ""
echo "Character count:"
ls -1 "$OUTPUT_DIR" | wc -l
echo ""
