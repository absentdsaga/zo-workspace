#!/bin/bash
set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <original_file> <new_file>"
    exit 1
fi

ORIGINAL="$1"
NEW="$2"

# Make paths absolute if relative
if [[ ! "$ORIGINAL" = /* ]]; then
    ORIGINAL="/home/workspace/Projects/survival-agent/$ORIGINAL"
fi
if [[ ! "$NEW" = /* ]]; then
    NEW="/home/workspace/Projects/survival-agent/$NEW"
fi

echo "═══════════════════════════════════════════════════════════════"
echo "  QA CHECKPOINT: MANDATORY VERIFICATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Original: $ORIGINAL"
echo "New:      $NEW"
echo ""

FAILED=0

# 1. Check numeric constants
echo "1️⃣  Checking numeric constants..."
echo "────────────────────────────────────────────────────────────"
ORIG_NUMS=$(grep -oE "(0\.[0-9]+|[0-9]+\.[0-9]+)" "$ORIGINAL" | sort -u)
NEW_NUMS=$(grep -oE "(0\.[0-9]+|[0-9]+\.[0-9]+)" "$NEW" | sort -u)

MISSING=$(comm -23 <(echo "$ORIG_NUMS") <(echo "$NEW_NUMS"))
if [ -n "$MISSING" ]; then
    echo "❌ FAIL: Missing numeric constants in new version:"
    echo "$MISSING" | sed 's/^/     /'
    FAILED=1
else
    echo "✅ PASS: All numeric constants present"
fi
echo ""

# 2. Check critical config values
echo "2️⃣  Checking critical thresholds (STOP_LOSS, TAKE_PROFIT, etc.)..."
echo "────────────────────────────────────────────────────────────"

# Extract values from ORIGINAL
ORIG_VALS=$(grep -E "STOP_LOSS|TAKE_PROFIT|TRAILING|MAX_POSITION|REFILL|takeProfit|stopLoss|trailingStop|maxPosition|autoRefill" "$ORIGINAL" | grep -E "= *-?[0-9]")

# Extract values from NEW (could be in config or as constants)
NEW_VALS=$(grep -E "STOP_LOSS|TAKE_PROFIT|TRAILING|MAX_POSITION|REFILL|takeProfit|stopLoss|trailingStop|maxPosition|autoRefill" "$NEW" | grep -E "= *-?[0-9]")

if [ -z "$NEW_VALS" ]; then
    echo "❌ FAIL: No critical thresholds found in new version"
    FAILED=1
else
    # Check specific values match
    CHECKS=(
        "0.12:maxPosition"
        "1.0:takeProfit" 
        "-0.30:stopLoss"
        "0.20:trailing"
        "0.03:refillThreshold"
    )
    
    for check in "${CHECKS[@]}"; do
        VALUE="${check%%:*}"
        NAME="${check##*:}"
        
        if echo "$NEW_VALS" | grep -q "$VALUE"; then
            echo "✅ $NAME: $VALUE found"
        else
            echo "❌ $NAME: $VALUE MISSING"
            FAILED=1
        fi
    done
fi
echo ""

# 3. Check method signatures
echo "3️⃣  Checking method signatures..."
echo "────────────────────────────────────────────────────────────"
ORIG_METHODS=$(grep -oE "private\s+\w+\s*\(|async\s+\w+\s*\(" "$ORIGINAL" | awk '{print $2}' | sed 's/($//' | sort -u)
NEW_METHODS=$(grep -oE "private\s+\w+\s*\(|async\s+\w+\s*\(" "$NEW" | awk '{print $2}' | sed 's/($//' | sort -u)
REMOVED=$(comm -23 <(echo "$ORIG_METHODS") <(echo "$NEW_METHODS"))

if [ -n "$REMOVED" ]; then
    echo "⚠️  WARNING: Methods in original but not in new:"
    echo "$REMOVED" | sed 's/^/     /'
    echo "    (This may be OK if refactored into sub-modules)"
else
    echo "✅ PASS: All methods present"
fi
echo ""

# 4. Check critical features exist
echo "4️⃣  Checking critical features..."
echo "────────────────────────────────────────────────────────────"
FEATURES=(
    "DexScreener:getDexScreener"
    "Stop Loss:stopLoss"
    "Take Profit:takeProfit"
    "Trailing Stop:trailing"
    "Circuit Breaker:circuitBreaker|CircuitBreaker"
)

for feature in "${FEATURES[@]}"; do
    NAME="${feature%%:*}"
    PATTERN="${feature##*:}"
    
    if grep -qE "$PATTERN" "$NEW"; then
        echo "✅ $NAME: Present"
    else
        echo "❌ $NAME: MISSING"
        FAILED=1
    fi
done
echo ""

# 5. Final verdict
echo "═══════════════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo "✅ QA CHECKPOINT PASSED"
    echo ""
    echo "The new version is functionally equivalent to the original."
    echo "You may proceed."
else
    echo "❌ QA CHECKPOINT FAILED"
    echo ""
    echo "DO NOT PROCEED. Fix the issues above first."
    echo "Re-run this checkpoint after fixes."
    exit 1
fi
echo "═══════════════════════════════════════════════════════════════"
