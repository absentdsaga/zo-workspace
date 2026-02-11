#!/bin/bash
# Visual verification via screenshot and analysis

URL="$1"
EXPECTED_FILE="$2"

if [ -z "$URL" ]; then
    echo "Usage: $0 <url> [expected-visuals-file]"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_DIR="/home/workspace/.visual-verify"
PROJECT_NAME=$(basename "$(pwd)")
SCREENSHOT="$OUTPUT_DIR/${PROJECT_NAME}-${TIMESTAMP}.jpg"

mkdir -p "$OUTPUT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  VISUAL VERIFICATION — Human Perception Check              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 URL: $URL"
echo "📂 Project: $PROJECT_NAME"
echo "📸 Screenshot: $SCREENSHOT"
echo ""

# Use Zo browser tools to capture and analyze
echo "📸 Capturing screenshot..."
echo ""

# This would integrate with Zo's browser tools
# For now, we'll do a manual checklist

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VISUAL CONTENT CHECKLIST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  MANUAL VERIFICATION REQUIRED:"
echo ""
echo "1. Open browser to: $URL"
echo "2. Wait 3 seconds for full render"
echo "3. Take screenshot or inspect visually"
echo "4. Check the following:"
echo ""

# Read expected visuals if file provided
if [ -n "$EXPECTED_FILE" ] && [ -f "$EXPECTED_FILE" ]; then
    echo "📋 Expected Visual Elements (from $EXPECTED_FILE):"
    echo ""
    grep "^- \[ \]" "$EXPECTED_FILE" 2>/dev/null | sed 's/^- \[ \] /  ☐ /' || echo "  (No checklist found in file)"
else
    echo "📋 Generic Visual Checks:"
    echo "  ☐ Main content visible (not black/blank screen)"
    echo "  ☐ UI elements rendered correctly"
    echo "  ☐ Colors match specification"
    echo "  ☐ Layout matches design"
    echo "  ☐ No visual glitches (clipping, z-fighting)"
    echo "  ☐ All claimed features actually visible"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 AUTOMATED CHECKS:"
echo ""

# Check if page loads
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "304" ]; then
    echo "✅ Page loads (HTTP $HTTP_CODE)"
else
    echo "❌ Page failed to load (HTTP $HTTP_CODE)"
    exit 1
fi

# Check if page has canvas element (for games)
PAGE_HTML=$(curl -s "$URL" 2>/dev/null || echo "")
if echo "$PAGE_HTML" | grep -q "<canvas"; then
    echo "✅ Canvas element present (game/graphics app)"
elif echo "$PAGE_HTML" | grep -q "game\|phaser"; then
    echo "⚠️  Game-related content found but no canvas detected"
fi

# Check for JavaScript errors (would need browser inspection)
echo "⚠️  JavaScript console check: MANUAL (open browser DevTools)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  CRITICAL REMINDER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⛔ DO NOT claim visual work is complete until:"
echo "   1. You've opened the URL in a browser"
echo "   2. You've verified with your eyes (or screenshot)"
echo "   3. What you SEE matches what you DESCRIBED"
echo ""
echo "Code working ≠ Visually correct!"
echo ""
echo "If the user's screenshot shows something different"
echo "than what you described, you FAILED visual verification."
echo ""
