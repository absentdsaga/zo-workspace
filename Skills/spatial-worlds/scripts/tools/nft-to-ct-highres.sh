#!/bin/bash
# High-Res NFT to CT Sprite Converter (64x96 or 128x192)
# Usage: ./nft-to-ct-highres.sh input.png output_name [size] [output_dir]

INPUT="$1"
OUTPUT_NAME="$2"
SIZE="${3:-64x96}"  # Default 64x96, can specify 128x192
OUTPUT_DIR="${4:-assets/sprites/nft-characters-hd}"

if [ -z "$INPUT" ] || [ -z "$OUTPUT_NAME" ]; then
    echo "Usage: $0 <input_image> <output_name> [size: 64x96|128x192] [output_dir]"
    exit 1
fi

# Parse size
if [[ "$SIZE" == "128x192" ]]; then
    WIDTH=128
    HEIGHT=192
    COLORS=32  # More colors for HD
elif [[ "$SIZE" == "112x168" ]]; then
    WIDTH=112
    HEIGHT=168
    COLORS=30  # 90% max quality
elif [[ "$SIZE" == "96x144" ]]; then
    WIDTH=96
    HEIGHT=144
    COLORS=28  # Sweet spot colors
else
    WIDTH=64
    HEIGHT=96
    COLORS=24  # Medium colors
fi

# Create output directory
mkdir -p "$OUTPUT_DIR/$OUTPUT_NAME"

echo "🎨 Converting: $OUTPUT_NAME (HD: ${WIDTH}x${HEIGHT})"
echo "   Input: $INPUT"

# Step 1: Remove background and crop to content
echo "   Removing background..."
convert "$INPUT" \
    -fuzz 10% -transparent white \
    -trim +repage \
    /tmp/step1-hd.png

# Step 2: Scale down to pixel art size using nearest-neighbor (sharper)
echo "   Pixelating to ${WIDTH}x${HEIGHT}..."
convert /tmp/step1-hd.png \
    -resize ${WIDTH}x${HEIGHT} \
    -filter point \
    -gravity center \
    -extent ${WIDTH}x${HEIGHT} \
    /tmp/step2-hd.png

# Step 3: Reduce colors (more colors for HD)
echo "   Reducing to $COLORS colors..."
convert /tmp/step2-hd.png \
    -colors $COLORS \
    -dither FloydSteinberg \
    /tmp/step3-hd.png

# Step 4: Enhance edges and add black outline
echo "   Adding pixel outline..."
convert /tmp/step3-hd.png \
    \( +clone -channel A -morphology EdgeOut Diamond:2 +channel +level-colors black \) \
    -compose DstOver -composite \
    /tmp/step4-hd.png

# Step 5: Sharpen for crisp pixels
echo "   Sharpening details..."
convert /tmp/step4-hd.png \
    -sharpen 0x1 \
    /tmp/step5-hd.png

# Step 6: Create 4 walk frames (more sophisticated variations for HD)
echo "   Generating walk cycle..."

# Frame 0 (base)
cp /tmp/step5-hd.png "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-0.png"

# Frame 1 (left leg forward)
convert /tmp/step5-hd.png \
    -roll +0+2 \
    "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-1.png"

# Frame 2 (opposite shift)
convert /tmp/step5-hd.png \
    -roll +0-2 \
    "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-2.png"

# Frame 3 (back to center)
cp /tmp/step5-hd.png "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-3.png"

# Create other directions
echo "   Creating other directions..."

# Up frames (flip vertical)
for i in 0 1 2 3; do
    convert "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-$i.png" \
        -flip \
        "$OUTPUT_DIR/$OUTPUT_NAME/up-walk-$i.png"
done

# Left frames (rotate and resize)
for i in 0 1 2 3; do
    convert "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-$i.png" \
        -rotate 270 -resize ${WIDTH}x${HEIGHT}! \
        "$OUTPUT_DIR/$OUTPUT_NAME/left-walk-$i.png"
done

# Right frames (mirror left)
for i in 0 1 2 3; do
    convert "$OUTPUT_DIR/$OUTPUT_NAME/left-walk-$i.png" \
        -flop \
        "$OUTPUT_DIR/$OUTPUT_NAME/right-walk-$i.png"
done

# Create sprite sheet
echo "   Creating sprite sheet..."
montage \
    "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-"{0,1,2,3}.png \
    "$OUTPUT_DIR/$OUTPUT_NAME/up-walk-"{0,1,2,3}.png \
    "$OUTPUT_DIR/$OUTPUT_NAME/left-walk-"{0,1,2,3}.png \
    "$OUTPUT_DIR/$OUTPUT_NAME/right-walk-"{0,1,2,3}.png \
    -tile 4x4 -geometry +0+0 -background transparent \
    "$OUTPUT_DIR/$OUTPUT_NAME/$OUTPUT_NAME-sheet.png"

# Create JSON config
cat > "$OUTPUT_DIR/$OUTPUT_NAME/$OUTPUT_NAME-sheet.json" <<EOF
{
  "frameWidth": $WIDTH,
  "frameHeight": $HEIGHT,
  "startFrame": 0,
  "endFrame": 15,
  "margin": 0,
  "spacing": 0
}
EOF

# Clean up temp files
rm -f /tmp/step*-hd.png

echo "✨ Done! Output: $OUTPUT_DIR/$OUTPUT_NAME/"
echo "   Sprite sheet: $OUTPUT_DIR/$OUTPUT_NAME/$OUTPUT_NAME-sheet.png"
echo ""
