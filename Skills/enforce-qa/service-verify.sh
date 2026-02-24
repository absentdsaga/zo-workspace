#!/bin/bash
set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <service_identifier>"
    echo "Examples:"
    echo "  $0 paper-trade-bot-refactored    # Process name"
    echo "  $0 /dev/shm/paper-trade-bot.log  # Log file"
    echo "  $0 57738                          # PID"
    exit 1
fi

IDENTIFIER="$1"

echo "═══════════════════════════════════════════════════════════════"
echo "  SERVICE VERIFICATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

FAILED=0

# 1. Check if process is running
echo "1️⃣  Checking process status..."
echo "────────────────────────────────────────────────────────────"

if [[ "$IDENTIFIER" =~ ^[0-9]+$ ]]; then
    # PID provided
    if ps -p "$IDENTIFIER" > /dev/null 2>&1; then
        PROCESS_INFO=$(ps -p "$IDENTIFIER" -o pid,etime,cmd --no-headers)
        echo "✅ Process running (PID: $IDENTIFIER)"
        echo "   $PROCESS_INFO"
    else
        echo "❌ Process not running (PID: $IDENTIFIER)"
        FAILED=1
    fi
else
    # Process name provided
    PIDS=$(pgrep -f "$IDENTIFIER" | head -1)
    if [ -n "$PIDS" ]; then
        PROCESS_INFO=$(ps -p "$PIDS" -o pid,etime,cmd --no-headers)
        echo "✅ Process running"
        echo "   $PROCESS_INFO"
        PID="$PIDS"
    else
        echo "❌ Process not running (searched for: $IDENTIFIER)"
        FAILED=1
    fi
fi
echo ""

if [ $FAILED -eq 1 ]; then
    echo "═══════════════════════════════════════════════════════════════"
    echo "❌ SERVICE VERIFICATION FAILED"
    echo ""
    echo "Service is not running. Start it before claiming done."
    echo "═══════════════════════════════════════════════════════════════"
    exit 1
fi

# 2. Check for errors in logs
echo "2️⃣  Checking for errors in recent logs..."
echo "────────────────────────────────────────────────────────────"

# Find log file
if [ -f "$IDENTIFIER" ]; then
    LOGFILE="$IDENTIFIER"
elif [ -n "$PID" ]; then
    # Try common log locations
    POSSIBLE_LOGS=$(find /dev/shm /tmp -name "*.log" -type f 2>/dev/null | head -5)
    for log in $POSSIBLE_LOGS; do
        if tail -100 "$log" 2>/dev/null | grep -qi "$IDENTIFIER"; then
            LOGFILE="$log"
            break
        fi
    done
fi

if [ -n "$LOGFILE" ] && [ -f "$LOGFILE" ]; then
    echo "Checking: $LOGFILE"
    ERRORS=$(tail -100 "$LOGFILE" 2>/dev/null | grep -i "error\|exception\|failed\|fatal" | grep -v "0 error" || true)
    
    if [ -n "$ERRORS" ]; then
        echo "⚠️  WARNING: Found errors in recent logs:"
        echo "$ERRORS" | head -5 | sed 's/^/   /'
        echo "   Review logs to ensure errors are expected/handled."
    else
        echo "✅ No errors in recent logs"
    fi
else
    echo "ℹ️  No log file found, skipping log check"
fi
echo ""

# 3. Check uptime
echo "3️⃣  Checking service health..."
echo "────────────────────────────────────────────────────────────"
if [ -n "$PID" ]; then
    UPTIME=$(ps -p "$PID" -o etime= | xargs)
    echo "✅ Uptime: $UPTIME"
    
    # Warn if process just started (might crash soon)
    if echo "$UPTIME" | grep -q "^00:0[0-2]"; then
        echo "⚠️  WARNING: Process started very recently ($UPTIME)"
        echo "   Wait a few minutes to confirm stability."
    fi
fi
echo ""

# 4. Final verdict
echo "═══════════════════════════════════════════════════════════════"
echo "✅ SERVICE VERIFICATION PASSED"
echo ""
echo "Process is running and appears healthy."
echo "Monitor for a few more minutes to confirm stability."
echo ""
echo "Monitor commands:"
if [ -n "$LOGFILE" ]; then
    echo "  tail -f $LOGFILE"
fi
if [ -n "$PID" ]; then
    echo "  watch -n 2 'ps -p $PID -o pid,etime,%cpu,%mem,cmd'"
fi
echo "═══════════════════════════════════════════════════════════════"
