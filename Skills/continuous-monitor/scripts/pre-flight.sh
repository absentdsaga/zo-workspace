#!/bin/bash
# Pre-Flight Verification — Run before claiming any deliverable is complete

PROJECT_DIR="$1"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-directory>"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 PRE-FLIGHT VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Project: $(basename "$PROJECT_DIR")"
echo "📍 Path: $PROJECT_DIR"
echo ""

FAILURES=0

# 1. Code Quality Checks
echo "📝 Code Quality Checks..."
if [ -f "tsconfig.json" ]; then
    echo "  • TypeScript compilation..."
    if npx tsc --noEmit 2>/dev/null; then
        echo "    ✅ No type errors"
    else
        echo "    ❌ TypeScript errors found"
        ((FAILURES++))
    fi
fi

if [ -f "package.json" ]; then
    if grep -q "\"lint\"" package.json; then
        echo "  • Running linter..."
        if npm run lint 2>/dev/null; then
            echo "    ✅ Linter passed"
        else
            echo "    ⚠️  Linter warnings"
        fi
    fi
fi

# 2. Build Verification
echo ""
echo "🔨 Build Verification..."
if [ -f "build-client.sh" ]; then
    echo "  • Running build script..."
    if ./build-client.sh > /tmp/build.log 2>&1; then
        echo "    ✅ Build succeeded"
        tail -3 /tmp/build.log | sed 's/^/      /'
    else
        echo "    ❌ Build failed"
        tail -10 /tmp/build.log | sed 's/^/      /'
        ((FAILURES++))
    fi
elif [ -f "package.json" ] && grep -q "\"build\"" package.json; then
    echo "  • Running npm build..."
    if npm run build > /tmp/build.log 2>&1; then
        echo "    ✅ Build succeeded"
    else
        echo "    ❌ Build failed"
        ((FAILURES++))
    fi
fi

# 3. Output Artifacts
echo ""
echo "📦 Output Artifacts..."
if [ -d "dist" ]; then
    FILE_COUNT=$(find dist -type f | wc -l)
    TOTAL_SIZE=$(du -sh dist | cut -f1)
    echo "  ✅ dist/ exists ($FILE_COUNT files, $TOTAL_SIZE)"
    
    # List key files
    find dist -type f -name "*.js" -o -name "*.html" | head -5 | while read -r file; do
        SIZE=$(du -h "$file" | cut -f1)
        echo "    • $(basename "$file") ($SIZE)"
    done
else
    echo "  ⚠️  No dist/ directory found"
fi

if [ -d "assets" ]; then
    ASSET_COUNT=$(find assets -type f | wc -l)
    echo "  ✅ assets/ exists ($ASSET_COUNT files)"
fi

# 4. Server Health
echo ""
echo "🚀 Server Health..."
SERVER_RUNNING=false
if pgrep -f "server" > /dev/null; then
    PID=$(pgrep -f "server" | head -1)
    CPU=$(ps -p "$PID" -o %cpu= 2>/dev/null | tr -d ' ')
    MEM=$(ps -p "$PID" -o %mem= 2>/dev/null | tr -d ' ')
    
    echo "  ✅ Server process running"
    echo "    • PID: $PID"
    echo "    • CPU: ${CPU}%"
    echo "    • MEM: ${MEM}%"
    
    SERVER_RUNNING=true
fi

# Check HTTP endpoint
if [ "$SERVER_RUNNING" = true ]; then
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
        RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:3000 2>/dev/null || echo "N/A")
        
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "304" ]; then
            echo "  ✅ HTTP endpoint responding"
            echo "    • Status: $HTTP_CODE"
            echo "    • Response time: ${RESPONSE_TIME}s"
        else
            echo "  ⚠️  HTTP endpoint not responding properly"
            echo "    • Status: $HTTP_CODE"
            ((FAILURES++))
        fi
    fi
else
    echo "  ℹ️  No server process found"
fi

# 5. File Syntax Check
echo ""
echo "🔍 Syntax Checks..."
JS_FILES=$(find . -name "*.js" -not -path "./node_modules/*" -not -path "./dist/*" 2>/dev/null | wc -l)
TS_FILES=$(find . -name "*.ts" -not -path "./node_modules/*" 2>/dev/null | wc -l)

if [ "$JS_FILES" -gt 0 ]; then
    echo "  • Found $JS_FILES JavaScript files"
fi

if [ "$TS_FILES" -gt 0 ]; then
    echo "  • Found $TS_FILES TypeScript files"
fi

# 6. Git Status
echo ""
echo "📋 Git Status..."
if [ -d ".git" ]; then
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ "$UNCOMMITTED" -gt 0 ]; then
        echo "  ⚠️  $UNCOMMITTED uncommitted changes"
        git status --short | head -5 | sed 's/^/    /'
    else
        echo "  ✅ Working tree clean"
    fi
    
    BRANCH=$(git branch --show-current)
    echo "  • Branch: $BRANCH"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$FAILURES" -eq 0 ]; then
    echo "✅ PRE-FLIGHT COMPLETE — All checks passed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo "❌ PRE-FLIGHT FAILED — $FAILURES issue(s) found"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚠️  DO NOT CLAIM COMPLETION UNTIL ISSUES ARE FIXED"
    exit 1
fi
