#!/bin/bash
# Spec Validator — Verify deliverable meets user requirements

PROJECT_DIR="$1"
SPEC_FILE="$2"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-directory> [spec-file]"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

# Look for spec files (in priority order)
if [ -n "$SPEC_FILE" ] && [ -f "$SPEC_FILE" ]; then
    SPEC="$SPEC_FILE"
elif [ -f "REQUIREMENTS.md" ]; then
    SPEC="REQUIREMENTS.md"
elif [ -f "SPEC.md" ]; then
    SPEC="SPEC.md"
elif [ -f "USER-GUIDANCE.md" ]; then
    SPEC="USER-GUIDANCE.md"
elif [ -f "README.md" ]; then
    SPEC="README.md"
else
    echo "⚠️  No spec file found. Create REQUIREMENTS.md to define project specs."
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SPEC VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Project: $(basename "$PROJECT_DIR")"
echo "📄 Spec File: $SPEC"
echo ""

FAILURES=0
WARNINGS=0

# Parse requirements from spec file
# Look for checkboxes: - [ ] requirement or - [x] requirement
# Look for bullet points: • requirement, * requirement
# Look for "MUST", "SHOULD", "REQUIRED" keywords

echo "🎯 Extracting Requirements..."
echo ""

# Extract checkbox items
CHECKBOX_REQS=$(grep -E "^- \[[ x]\]" "$SPEC" 2>/dev/null || true)
if [ -n "$CHECKBOX_REQS" ]; then
    echo "$CHECKBOX_REQS" | while IFS= read -r line; do
        if echo "$line" | grep -q "\[x\]"; then
            echo "  ✅ $(echo "$line" | sed 's/^- \[x\] //')"
        else
            echo "  ⚠️  $(echo "$line" | sed 's/^- \[ \] //')"
            ((WARNINGS++))
        fi
    done
fi

echo ""
echo "🔍 Checking Requirements Against Implementation..."
echo ""

# Common requirement patterns
check_requirement() {
    local req_name="$1"
    local check_command="$2"
    local expected="$3"
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo "  ✅ $req_name"
    else
        echo "  ❌ $req_name"
        if [ -n "$expected" ]; then
            echo "     Expected: $expected"
        fi
        ((FAILURES++))
    fi
}

# Check for common requirements based on project type

# 1. If spec mentions "isometric" or "FFT style"
if grep -iq "isometric\|final fantasy tactics\|fft" "$SPEC" 2>/dev/null; then
    echo "🎮 Isometric Game Requirements:"
    
    # Check for isometric rendering
    if grep -rq "isometric\|iso" scripts/ 2>/dev/null; then
        echo "  ✅ Isometric rendering implementation found"
    else
        echo "  ❌ Isometric rendering not found"
        ((FAILURES++))
    fi
    
    # Check for elevated platforms
    if grep -iq "platform\|elevation\|level.*[0-3]" "$SPEC" 2>/dev/null; then
        if grep -rq "elevation\|platform" scripts/ 2>/dev/null; then
            echo "  ✅ Multi-level platforms implemented"
        else
            echo "  ❌ Multi-level platforms missing"
            ((FAILURES++))
        fi
    fi
    
    # Check for depth sorting
    if grep -rq "depth.*sort\|DepthManager" scripts/ 2>/dev/null; then
        echo "  ✅ Depth sorting system found"
    else
        echo "  ⚠️  Depth sorting may be missing"
        ((WARNINGS++))
    fi
fi

# 2. If spec mentions "Chrono Trigger" or pixel art
if grep -iq "chrono trigger\|pixel art\|sprite" "$SPEC" 2>/dev/null; then
    echo ""
    echo "🎨 Art Style Requirements:"
    
    if [ -d "assets/sprites" ]; then
        SPRITE_COUNT=$(find assets/sprites -name "*.png" | wc -l)
        echo "  ✅ Sprite directory exists ($SPRITE_COUNT sprites)"
        
        # Check sprite dimensions if mentioned
        if grep -iq "48.*64\|48x64" "$SPEC" 2>/dev/null; then
            if find assets/sprites -name "*.png" -exec identify {} \; 2>/dev/null | grep -q "48x64"; then
                echo "  ✅ 48x64px sprites found"
            else
                echo "  ⚠️  No 48x64px sprites detected"
                ((WARNINGS++))
            fi
        fi
    else
        echo "  ❌ No assets/sprites directory"
        ((FAILURES++))
    fi
fi

# 3. If spec mentions specific FPS target
if grep -iq "60.*fps\|60 fps\|target.*60" "$SPEC" 2>/dev/null; then
    echo ""
    echo "⚡ Performance Requirements:"
    echo "  ⚠️  FPS must be verified in browser (run browser test)"
    ((WARNINGS++))
fi

# 4. If spec mentions movement/controls
if grep -iq "8.*direction\|8-direction\|wasd" "$SPEC" 2>/dev/null; then
    echo ""
    echo "🎮 Movement Requirements:"
    
    if grep -rq "8.*direction\|directionMap" scripts/ 2>/dev/null; then
        echo "  ✅ 8-direction movement implemented"
    else
        echo "  ❌ 8-direction movement not found"
        ((FAILURES++))
    fi
    
    if grep -rq "WASD\|KeyCodes.W\|KeyCodes.A" scripts/ 2>/dev/null; then
        echo "  ✅ WASD controls implemented"
    else
        echo "  ⚠️  WASD controls may be missing"
        ((WARNINGS++))
    fi
fi

# 5. If spec mentions multiplayer/proximity voice
if grep -iq "multiplayer\|proximity.*voice\|voice.*chat\|websocket" "$SPEC" 2>/dev/null; then
    echo ""
    echo "🌐 Multiplayer Requirements:"
    
    if grep -rq "WebSocket\|socket\.io" scripts/ package.json 2>/dev/null; then
        echo "  ✅ WebSocket implementation found"
    else
        echo "  ⚠️  WebSocket/multiplayer not implemented yet"
        ((WARNINGS++))
    fi
fi

# 6. If spec mentions specific color coding
if grep -iq "color.*cod\|green.*blue.*orange.*pink" "$SPEC" 2>/dev/null; then
    echo ""
    echo "🎨 Color Coding Requirements:"
    
    if grep -rq "0x88ff88.*0x88ccff.*0xffcc88.*0xff88ff" scripts/ 2>/dev/null; then
        echo "  ✅ Color-coded elevation system found"
    else
        echo "  ⚠️  Color coding scheme not detected"
        ((WARNINGS++))
    fi
fi

# 7. Check for specific features mentioned in spec
echo ""
echo "📦 Feature Checklist:"

# Extract MUST/REQUIRED items
MUST_HAVE=$(grep -i "must\|required\|critical" "$SPEC" 2>/dev/null | head -10 || true)
if [ -n "$MUST_HAVE" ]; then
    echo "$MUST_HAVE" | while IFS= read -r req; do
        # Clean up the requirement text
        REQ_TEXT=$(echo "$req" | sed 's/.*MUST/MUST/' | sed 's/.*REQUIRED/REQUIRED/' | head -c 60)
        echo "  ⚠️  Manual check: $REQ_TEXT..."
    done
fi

# 8. Check against user's exact words from recent feedback
if [ -f "DAY-1-FEEDBACK.md" ] || [ -f "DAY-2-QA-REPORT.md" ]; then
    echo ""
    echo "📝 Previous Feedback Check:"
    
    # Look for unresolved issues from previous QA reports
    for qa_file in DAY-*-*.md QA-REPORT*.md; do
        if [ -f "$qa_file" ]; then
            UNRESOLVED=$(grep -E "❌|⚠️.*ISSUE|TODO" "$qa_file" 2>/dev/null | head -5 || true)
            if [ -n "$UNRESOLVED" ]; then
                echo "  ⚠️  Found unresolved items in $qa_file:"
                echo "$UNRESOLVED" | sed 's/^/     /'
                ((WARNINGS++))
            fi
        fi
    done
fi

# 9. Specific checks based on common user feedback patterns
echo ""
echo "🔬 Implementation Quality:"

# Check if loading screen is properly hidden
if grep -rq "loading.*hidden\|classList.add.*hidden" scripts/ 2>/dev/null; then
    echo "  ✅ Loading screen hide logic found"
else
    echo "  ⚠️  Loading screen may not hide properly"
    ((WARNINGS++))
fi

# Check if assets are being served
if grep -rq "/assets/\|assets/" scripts/server.ts 2>/dev/null; then
    echo "  ✅ Asset serving route configured"
else
    echo "  ⚠️  Asset serving may not be configured"
    ((WARNINGS++))
fi

# Check if build process exists
if [ -f "build-client.sh" ] || grep -q "\"build\"" package.json 2>/dev/null; then
    echo "  ✅ Build process configured"
else
    echo "  ❌ No build process found"
    ((FAILURES++))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$FAILURES" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "✅ SPEC VALIDATION PASSED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "All requirements validated successfully!"
    exit 0
elif [ "$FAILURES" -eq 0 ]; then
    echo "⚠️  SPEC VALIDATION: WARNINGS ONLY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ No critical failures"
    echo "⚠️  $WARNINGS warning(s) found - review recommended"
    echo ""
    echo "💡 Some requirements may need manual verification"
    exit 0
else
    echo "❌ SPEC VALIDATION FAILED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "❌ $FAILURES critical issue(s) found"
    echo "⚠️  $WARNINGS warning(s) found"
    echo ""
    echo "🚫 DO NOT DELIVER UNTIL SPEC REQUIREMENTS ARE MET"
    exit 1
fi
