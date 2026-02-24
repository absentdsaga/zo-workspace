#!/bin/bash
# Test the sprite pipeline with existing sprite assets

set -e

PIPELINE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PIPELINE_DIR"

echo "=== Sprite Pipeline Test ==="
echo ""

# Find an existing sprite to test with
TEST_SPRITE=$(find ../assets/sprites/player-characters -name "*.png" | head -1)

if [ -z "$TEST_SPRITE" ]; then
    echo "No test sprite found. Please add a sprite to assets/sprites/player-characters/"
    exit 1
fi

echo "Test sprite: $TEST_SPRITE"
echo ""

# Test normalization
echo "1. Testing normalization..."
python3 normalize_sprite.py "$TEST_SPRITE" "output_norm/test_normalized.png"

if [ -f "output_norm/test_normalized.png" ]; then
    echo "✓ Normalization successful"
else
    echo "✗ Normalization failed"
    exit 1
fi

echo ""

# Test QC
echo "2. Testing QC checker..."
python3 qc_checker.py "output_norm/test_normalized.png" | jq .

echo ""
echo "=== Pipeline Test Complete ==="
echo ""
echo "Check output:"
echo "  - Normalized sprite: output_norm/test_normalized.png"
echo ""
echo "Next steps:"
echo "  1. Start ComfyUI: ./start_comfyui.sh"
echo "  2. Configure ComfyUI workflow"
echo "  3. Run job: python3 batch_orchestrator.py jobs/hero_orange.json"
