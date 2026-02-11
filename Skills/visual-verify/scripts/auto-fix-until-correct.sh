#!/bin/bash
# Auto-fix loop: Keep iterating until visual verification passes

PROJECT_DIR="$1"
MAX_ITERATIONS="${2:-5}"
URL="$3"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-dir> [max-iterations] [url]"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  AUTO-FIX UNTIL CORRECT — Visual Verification Loop        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Project: $(basename "$PROJECT_DIR")"
echo "🔄 Max iterations: $MAX_ITERATIONS"
echo "🌐 URL: ${URL:-Auto-detect}"
echo ""

# Auto-detect URL if not provided
if [ -z "$URL" ]; then
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    URL="https://${PROJECT_NAME}-dioni.zocomputer.io"
fi

ITERATION=1
VISUAL_SPEC="VISUAL-SPEC.md"

while [ $ITERATION -le $MAX_ITERATIONS ]; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "ITERATION $ITERATION of $MAX_ITERATIONS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Step 1: Build
    echo "🔨 Building project..."
    if [ -f "build-client.sh" ]; then
        ./build-client.sh > /tmp/build.log 2>&1
        if [ $? -ne 0 ]; then
            echo "❌ Build failed!"
            cat /tmp/build.log
            exit 1
        fi
        echo "✅ Build succeeded"
    fi
    
    echo ""
    
    # Step 2: Visual verification (manual for now, would be automated with AI vision)
    echo "📸 Visual verification check..."
    echo ""
    echo "Opening in browser: $URL"
    echo ""
    echo "Checking against VISUAL-SPEC.md:"
    
    if [ -f "$VISUAL_SPEC" ]; then
        # Extract unchecked items (what we're looking for)
        EXPECTED=$(grep "^- \[ \]" "$VISUAL_SPEC" | head -5)
        
        if [ -n "$EXPECTED" ]; then
            echo ""
            echo "Expected to see:"
            echo "$EXPECTED" | sed 's/^- \[ \] /  • /'
        fi
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❓ VISUAL VERIFICATION RESULT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Please open: $URL"
    echo ""
    echo "Do you see what's expected? (y/n/auto)"
    echo "  y    = Looks correct, pass"
    echo "  n    = Doesn't match spec, needs fix"
    echo "  auto = Use AI vision to verify (if available)"
    echo ""
    read -p "Verdict: " VERDICT
    
    if [ "$VERDICT" = "y" ]; then
        echo ""
        echo "✅ VISUAL VERIFICATION PASSED!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "SUCCESS after $ITERATION iteration(s)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 0
    fi
    
    # If not passing, analyze what's wrong
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "DIAGNOSTIC: What's wrong with the visuals?"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Common issues:"
    echo "  1. Graphics rendering off-screen (wrong coordinates)"
    echo "  2. Depth set wrong (graphics behind background)"
    echo "  3. Colors too dark to see"
    echo "  4. Camera zoom/position wrong"
    echo "  5. Graphics not being drawn at all"
    echo ""
    read -p "What issue did you observe? (1-5): " ISSUE
    
    echo ""
    echo "🔧 APPLYING FIX for issue $ISSUE..."
    echo ""
    
    case $ISSUE in
        1)
            echo "Fixing: Graphics off-screen - centering at viewport center..."
            # Would auto-edit code here
            echo "⚠️  Manual fix needed: Update coordinates to center (640, 360)"
            ;;
        2)
            echo "Fixing: Depth issue - setting graphics to depth -1..."
            # Would auto-edit code here
            echo "⚠️  Manual fix needed: Change graphics.setDepth() to -1 or 1"
            ;;
        3)
            echo "Fixing: Colors too dark - increasing opacity and line width..."
            echo "⚠️  Manual fix needed: Increase alpha to 1.0, lineStyle to 2px"
            ;;
        4)
            echo "Fixing: Camera issue - adjusting zoom and bounds..."
            echo "⚠️  Manual fix needed: Set zoom to 1, check camera.setBounds()"
            ;;
        5)
            echo "Fixing: Graphics not drawing - checking createWorld() is called..."
            echo "⚠️  Manual fix needed: Ensure createIsoWorld() is called in create()"
            ;;
        *)
            echo "Unknown issue. Skipping auto-fix."
            ;;
    esac
    
    echo ""
    read -p "Apply fix and continue? (y/n): " CONTINUE
    
    if [ "$CONTINUE" != "y" ]; then
        echo "Stopping iteration."
        exit 1
    fi
    
    ((ITERATION++))
    echo ""
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "❌ FAILED TO FIX AFTER $MAX_ITERATIONS ITERATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Manual intervention required."
exit 1
