#!/bin/bash
# Root cause analysis for rendering issues

PROJECT_PATH="$1"
ISSUE="$2"

echo "🔍 ROOT CAUSE ANALYSIS"
echo "======================"
echo ""
echo "Issue: $ISSUE"
echo ""

cd "$PROJECT_PATH" || exit 1

echo "## Checking Rendering Pipeline"
echo ""

# Check if graphics are created
echo "### Graphics Creation"
grep -n "add.graphics()" scripts/client/scenes/*.ts

echo ""
echo "### Graphics Depth Settings"
grep -n "setDepth" scripts/client/scenes/*.ts

echo ""
echo "### Coordinate Systems"
echo "Checking if coordinates are within viewport (1280×720):"
grep -n "centerX\|centerY" scripts/client/scenes/*.ts

echo ""
echo "### Canvas/Camera Settings"
grep -n "width:\|height:\|setZoom\|setBounds" scripts/client/**/*.ts

echo ""
echo "### Asset Loading"
echo "Checking if assets exist:"
if [ -f "assets/sprites/warrior-iso.png" ]; then
    echo "✅ warrior-iso.png exists"
    ls -lh assets/sprites/warrior-iso.png
else
    echo "❌ warrior-iso.png NOT FOUND"
fi

echo ""
echo "### Console Errors Check"
echo "Build the project and check browser console for:"
echo "  - Asset loading errors"
echo "  - WebGL errors"
echo "  - Phaser initialization errors"

echo ""
echo "## Common Rendering Issues"
echo ""
echo "1. Graphics off-screen (wrong coordinates)"
echo "2. Graphics depth too low (behind background)"
echo "3. Graphics opacity/alpha too low (invisible)"
echo "4. Graphics not added to scene"
echo "5. Canvas size mismatch"
echo "6. Asset loading failures"
echo ""

echo "## Diagnostic Questions"
echo ""
echo "- Are graphics coordinates within viewport bounds?"
echo "- Is graphics depth higher than background?"
echo "- Is graphics opacity set to 1 (fully opaque)?"
echo "- Does browser console show any errors?"
echo "- Is the canvas size matching config (1280×720)?"
