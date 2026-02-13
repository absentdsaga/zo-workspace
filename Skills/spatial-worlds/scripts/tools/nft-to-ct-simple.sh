#!/bin/bash
# Simple NFT to CT Sprite Converter using ImageMagick
# Usage: ./nft-to-ct-simple.sh input.png output_name

INPUT="$1"
OUTPUT_NAME="$2"
OUTPUT_DIR="${3:-assets/sprites/nft-characters}"

if [ -z "$INPUT" ] || [ -z "$OUTPUT_NAME" ]; then
    echo "Usage: $0 <input_image> <output_name> [output_dir]"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR/$OUTPUT_NAME"

echo "🎨 Converting: $OUTPUT_NAME"
echo "   Input: $INPUT"

# Step 1: Remove background and crop to content
echo "   Removing background..."
convert "$INPUT" \
    -fuzz 10% -transparent white \
    -trim +repage \
    /tmp/step1.png

# Step 2: Scale down to pixel art size (32x48) using nearest-neighbor
echo "   Pixelating to 32x48..."
convert /tmp/step1.png \
    -resize 32x48 \
    -filter point \
    -gravity center \
    -extent 32x48 \
    /tmp/step2.png

# Step 3: Reduce colors to 16 (CT palette style)
echo "   Reducing to 16 colors..."
convert /tmp/step2.png \
    -colors 16 \
    -dither FloydSteinberg \
    /tmp/step3.png

# Step 4: Add black outline
echo "   Adding pixel outline..."
convert /tmp/step3.png \
    \( +clone -channel A -morphology EdgeOut Diamond:1 +channel +level-colors black \) \
    -compose DstOver -composite \
    /tmp/step4.png

# Step 5: Create 4 walk frames (simple variations)
echo "   Generating walk cycle..."

# Frame 0 (base)
cp /tmp/step4.png "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-0.png"

# Frame 1 (slight shift)
convert /tmp/step4.png -roll +0+1 "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-1.png"

# Frame 2 (opposite shift)
convert /tmp/step4.png -roll +0-1 "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-2.png"

# Frame 3 (back to center)
cp /tmp/step4.png "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-3.png"

# Create other directions by flipping/rotating
echo "   Creating other directions..."

# Up frames (flip vertical)
for i in 0 1 2 3; do
    convert "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-$i.png" \
        -flip \
        "$OUTPUT_DIR/$OUTPUT_NAME/up-walk-$i.png"
done

# Left frames (rotate)
for i in 0 1 2 3; do
    convert "$OUTPUT_DIR/$OUTPUT_NAME/down-walk-$i.png" \
        -rotate 270 -resize 32x48! \
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
  "frameWidth": 32,
  "frameHeight": 48,
  "startFrame": 0,
  "endFrame": 15,
  "margin": 0,
  "spacing": 0
}
EOF

# Clean up temp files
rm -f /tmp/step*.png

echo "✨ Done! Output: $OUTPUT_DIR/$OUTPUT_NAME/"
echo "   Sprite sheet: $OUTPUT_DIR/$OUTPUT_NAME/$OUTPUT_NAME-sheet.png"
echo ""
