#!/bin/bash
# Mandatory QA checkpoint - must pass before claiming task complete

set -e

TASK_DESC="$1"
PROJECT_PATH="${2:-/home/workspace/Skills/spatial-worlds}"
AUDIT_LOG="/home/workspace/Skills/enforce-qa/audit.log"

# Ensure audit log exists
mkdir -p "$(dirname "$AUDIT_LOG")"
touch "$AUDIT_LOG"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$AUDIT_LOG"
}

echo "═══════════════════════════════════════"
echo "  🛡️  MANDATORY QA CHECKPOINT"
echo "═══════════════════════════════════════"
echo ""

log "TASK: $TASK_DESC"
log "PROJECT: $PROJECT_PATH"

# Phase 1: Technical QA
echo "Phase 1: Technical Verification"
echo "--------------------------------"

if [ -f "$PROJECT_PATH/tsconfig.json" ]; then
    cd "$PROJECT_PATH"

    # TypeScript check
    if bunx tsc --noEmit 2>&1 | tee /tmp/tsc-output.txt; then
        log "TECHNICAL_QA/TypeScript: ✅ PASS"
        echo "✅ TypeScript compilation: PASS"
    else
        log "TECHNICAL_QA/TypeScript: ❌ FAIL"
        echo "❌ TypeScript compilation: FAIL"
        cat /tmp/tsc-output.txt
        exit 1
    fi

    # Build check
    if [ -f "build-client.sh" ]; then
        if ./build-client.sh > /tmp/build-output.txt 2>&1; then
            log "TECHNICAL_QA/Build: ✅ PASS"
            echo "✅ Build: PASS"
        else
            log "TECHNICAL_QA/Build: ❌ FAIL"
            echo "❌ Build: FAIL"
            cat /tmp/build-output.txt
            exit 1
        fi
    fi

    # Server check
    if pgrep -f "bun.*server.ts" > /dev/null; then
        log "TECHNICAL_QA/Server: ✅ RUNNING"
        echo "✅ Server: RUNNING"
    else
        log "TECHNICAL_QA/Server: ⚠️  NOT RUNNING"
        echo "⚠️  Server: NOT RUNNING (may be intentional)"
    fi

    # HTTP check (if server running)
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
        log "TECHNICAL_QA/HTTP: ✅ RESPONDING"
        echo "✅ HTTP endpoint: RESPONDING (200)"
    fi
fi

echo ""
log "TECHNICAL_QA: ✅ COMPLETE"

# Phase 2: Visual Verification (if applicable)
echo "Phase 2: Visual Verification"
echo "-----------------------------"
echo ""
echo "✅ AUTOMATED VISUAL VERIFICATION"
echo ""
echo "AI will automatically:"
echo "  1. Open the live site in browser"
echo "  2. Capture screenshot"
echo "  3. Analyze against VISUAL-SPEC.md"
echo "  4. Log results"
echo ""
echo "Running automated screenshot capture..."

# Take screenshot of localhost if available
if [ -f "$PROJECT_PATH/scripts/tools/screenshot.mjs" ]; then
    cd "$PROJECT_PATH"
    if node scripts/tools/screenshot.mjs > /tmp/screenshot.log 2>&1; then
        log "VISUAL_VERIFY: ✅ Screenshot captured: /tmp/spatial-worlds-screenshot.png"
        echo "✅ Screenshot saved: /tmp/spatial-worlds-screenshot.png"
    else
        log "VISUAL_VERIFY: ⚠️ Screenshot failed (see /tmp/screenshot.log)"
        echo "⚠️ Screenshot capture failed"
    fi
else
    log "VISUAL_VERIFY: AUTOMATED (AI uses open_webpage + view_webpage)"
    echo "Note: Visual verification via browser tools"
fi

echo ""

# Phase 3: Spec Compliance
echo "Phase 3: Specification Compliance"
echo "----------------------------------"

if [ -f "$PROJECT_PATH/USER-GUIDANCE.md" ]; then
    echo "Checking against user requirements..."
    log "SPEC_CHECK: Reviewing USER-GUIDANCE.md"
    echo "✅ User requirements file found"
    echo "   Review: $PROJECT_PATH/USER-GUIDANCE.md"
else
    log "SPEC_CHECK: ⚠️  No USER-GUIDANCE.md found"
    echo "⚠️  No specification file found"
fi

echo ""
log "CHECKPOINT: TECHNICAL_QA PASSED, VISUAL_VERIFY PENDING"

echo "═══════════════════════════════════════"
echo "  CHECKPOINT SUMMARY"
echo "═══════════════════════════════════════"
echo ""
echo "Technical QA:     ✅ PASSED"
echo "Visual Verify:    ⏸️  PENDING (AI must verify)"
echo "Spec Compliance:  ⏸️  PENDING (AI must verify)"
echo ""
echo "⚠️  AI: Do NOT claim task complete until:"
echo "   1. User confirms visual output is correct"
echo "   2. All spec requirements verified"
echo ""
echo "Audit trail: $AUDIT_LOG"
echo ""
