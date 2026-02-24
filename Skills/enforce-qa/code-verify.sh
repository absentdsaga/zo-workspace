#!/bin/bash
set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file_or_directory>"
    exit 1
fi

TARGET="$1"

# Make path absolute if relative
if [[ ! "$TARGET" = /* ]]; then
    TARGET="/home/workspace/$TARGET"
fi

echo "═══════════════════════════════════════════════════════════════"
echo "  CODE VERIFICATION: $TARGET"
echo "═══════════════════════════════════════════════════════════════"
echo ""

FAILED=0

# Determine file type
if [ -d "$TARGET" ]; then
    FILES=$(find "$TARGET" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.py" \))
else
    FILES="$TARGET"
fi

# 1. Syntax check
echo "1️⃣  Checking syntax..."
echo "────────────────────────────────────────────────────────────"
for file in $FILES; do
    EXT="${file##*.}"
    FILENAME=$(basename "$file")
    
    case $EXT in
        ts|tsx)
            if ! bun build "$file" --target=node --outfile=/tmp/verify-build.js > /dev/null 2>&1; then
                echo "❌ FAIL: $FILENAME has TypeScript syntax errors"
                bun build "$file" --target=node --outfile=/tmp/verify-build.js 2>&1 | head -10
                FAILED=1
            else
                echo "✅ PASS: $FILENAME (TypeScript)"
            fi
            ;;
        js|jsx)
            if ! node --check "$file" 2>&1; then
                echo "❌ FAIL: $FILENAME has JavaScript syntax errors"
                FAILED=1
            else
                echo "✅ PASS: $FILENAME (JavaScript)"
            fi
            ;;
        py)
            if ! python3 -m py_compile "$file" 2>&1; then
                echo "❌ FAIL: $FILENAME has Python syntax errors"
                FAILED=1
            else
                echo "✅ PASS: $FILENAME (Python)"
            fi
            ;;
    esac
done
echo ""

# 2. Check for unfinished work
echo "2️⃣  Checking for unfinished work markers..."
echo "────────────────────────────────────────────────────────────"
TODOS=$(grep -rn "TODO\|FIXME\|XXX\|HACK" $FILES 2>/dev/null || true)
if [ -n "$TODOS" ]; then
    echo "⚠️  WARNING: Found unfinished work markers:"
    echo "$TODOS" | head -5
    if [ $(echo "$TODOS" | wc -l) -gt 5 ]; then
        echo "   ... and $(( $(echo "$TODOS" | wc -l) - 5 )) more"
    fi
    echo "   Consider finishing or removing these before claiming done."
else
    echo "✅ PASS: No unfinished work markers"
fi
echo ""

# 3. Check for common issues
echo "3️⃣  Checking for common issues..."
echo "────────────────────────────────────────────────────────────"

# Check for console.log in production code
CONSOLE_LOGS=$(grep -rn "console\.log\|console\.error" $FILES 2>/dev/null | grep -v "^\s*//" || true)
if [ -n "$CONSOLE_LOGS" ]; then
    COUNT=$(echo "$CONSOLE_LOGS" | wc -l)
    echo "ℹ️  INFO: Found $COUNT console.log/error statements"
    echo "   (This may be intentional for logging)"
else
    echo "✅ No console statements found"
fi

# Check for hardcoded credentials
SECRETS=$(grep -rni "password\s*=\|api_key\s*=\|secret\s*=\|token\s*=" $FILES 2>/dev/null | grep -v "process\.env\|os\.environ" || true)
if [ -n "$SECRETS" ]; then
    echo "⚠️  WARNING: Possible hardcoded secrets found:"
    echo "$SECRETS" | head -3
    FAILED=1
else
    echo "✅ No hardcoded secrets detected"
fi
echo ""

# 4. Final verdict
echo "═══════════════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo "✅ CODE VERIFICATION PASSED"
    echo ""
    echo "All syntax checks passed. Code is ready."
else
    echo "❌ CODE VERIFICATION FAILED"
    echo ""
    echo "Fix the issues above before claiming done."
    exit 1
fi
echo "═══════════════════════════════════════════════════════════════"
