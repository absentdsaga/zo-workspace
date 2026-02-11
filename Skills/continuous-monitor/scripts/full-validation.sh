#!/bin/bash
# Full Validation — Complete pre-delivery check (technical + spec)

PROJECT_DIR="$1"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-directory>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  FULL VALIDATION — Technical + Spec Compliance            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Project: $(basename "$PROJECT_DIR")"
echo "📍 Path: $PROJECT_DIR"
echo ""

TOTAL_FAILURES=0

# Phase 1: Technical Pre-Flight
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 1: Technical Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if "$SCRIPT_DIR/pre-flight.sh" "$PROJECT_DIR"; then
    echo ""
    echo "✅ Phase 1 PASSED: Technical checks successful"
else
    echo ""
    echo "❌ Phase 1 FAILED: Technical issues found"
    ((TOTAL_FAILURES++))
fi

echo ""
echo ""

# Phase 2: Spec Validation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 2: Spec Compliance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if "$SCRIPT_DIR/spec-validator.sh" "$PROJECT_DIR"; then
    echo ""
    echo "✅ Phase 2 PASSED: Spec requirements met"
else
    SPEC_EXIT=$?
    if [ "$SPEC_EXIT" -eq 1 ]; then
        echo ""
        echo "❌ Phase 2 FAILED: Spec requirements not met"
        ((TOTAL_FAILURES++))
    else
        echo ""
        echo "⚠️  Phase 2: Warnings found (not blocking)"
    fi
fi

echo ""
echo ""

# Phase 3: Browser Verification Reminder
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 3: Manual Browser Verification Required"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Next Steps (Manual):"
echo "  1. Open the application in browser"
echo "  2. Verify it loads without errors"
echo "  3. Test core functionality (movement, interactions, etc.)"
echo "  4. Check browser console for errors"
echo "  5. Measure actual FPS/performance"
echo "  6. Take screenshot for documentation"
echo ""

# Find service URL if registered
if [ -f "$PROJECT_DIR/package.json" ]; then
    SERVICE_NAME=$(basename "$PROJECT_DIR")
    echo "💡 If registered as Zo service, check:"
    echo "   https://$SERVICE_NAME-dioni.zocomputer.io"
    echo ""
fi

# Final Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$TOTAL_FAILURES" -eq 0 ]; then
    echo "✅ VALIDATION COMPLETE — Ready for Delivery"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "All automated checks passed!"
    echo ""
    echo "⚠️  IMPORTANT: Complete Phase 3 browser testing before claiming done"
    echo ""
    exit 0
else
    echo "❌ VALIDATION FAILED — $TOTAL_FAILURES Critical Issue(s)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🚫 DO NOT DELIVER until all phases pass"
    echo ""
    echo "Fix the issues above and re-run:"
    echo "  $0 $PROJECT_DIR"
    echo ""
    exit 1
fi
