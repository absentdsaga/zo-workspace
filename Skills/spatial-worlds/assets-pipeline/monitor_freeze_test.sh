#!/bin/bash
# Monitor freeze test progress

echo "=== Freeze Test Monitor ==="
echo ""

# Check if test is running
if pgrep -f "freeze_workflow_test.py" > /dev/null; then
    echo "✓ Freeze test is running"
    echo ""
else
    echo "✗ Freeze test not running"
    echo ""
fi

# Show recent log output
echo "=== Recent Log Output ==="
tail -15 freeze_test_output.log 2>/dev/null || echo "No log file yet"
echo ""

# Check ComfyUI queue
echo "=== ComfyUI Queue Status ==="
curl -s http://localhost:8188/queue | python3 -c "
import sys, json
q = json.load(sys.stdin)
running = len(q.get('queue_running', []))
pending = len(q.get('queue_pending', []))
print(f'Running: {running}')
print(f'Pending: {pending}')
print(f'Total: {running + pending}')
" 2>/dev/null || echo "Could not connect to ComfyUI"
echo ""

# Check output files
echo "=== Generated Images ==="
ls -lh test_freeze_output/*.png 2>/dev/null | awk '{print $9, "(" $5 ")"}' || echo "No images yet"
echo ""

# Check ComfyUI output folder
echo "=== ComfyUI Output ==="
ls -lt ../ComfyUI/output/*.png 2>/dev/null | head -5 | awk '{print $9, "(" $5 ")"}'
echo ""

echo "Run: watch -n 10 ./monitor_freeze_test.sh"
echo "Or: tail -f freeze_test_output.log"
