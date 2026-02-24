#!/bin/bash
echo "=== Pilot Batch Monitor ==="
echo ""

if pgrep -f "batch_orchestrator.py" > /dev/null; then
    echo "✓ Pilot batch running"
else
    echo "✗ Pilot batch not running"
fi
echo ""

echo "=== Recent Log ==="
tail -15 pilot_bear_mini.log 2>/dev/null || echo "No log yet"
echo ""

echo "=== ComfyUI Queue ==="
curl -s http://localhost:8188/queue | python3 -c "
import sys, json
q = json.load(sys.stdin)
print(f'Running: {len(q.get(\"queue_running\", []))}')
print(f'Pending: {len(q.get(\"queue_pending\", []))}')
" 2>/dev/null
echo ""

echo "=== Generated Frames ==="
echo "Raw:"
ls output_raw/npc_bear/idle/*.png 2>/dev/null | wc -l || echo "0"
echo "Cut:"
ls output_cut/npc_bear/*.png 2>/dev/null | wc -l || echo "0"
echo "Normalized:"
ls output_norm/npc_bear/*.png 2>/dev/null | wc -l || echo "0"
echo "QC Pass:"
ls output_qc_pass/npc_bear/*.png 2>/dev/null | wc -l || echo "0"
echo "QC Fail:"
ls output_qc_fail/npc_bear/*.png 2>/dev/null | wc -l || echo "0"
echo ""

echo "Run: watch -n 10 ./monitor_pilot.sh"
