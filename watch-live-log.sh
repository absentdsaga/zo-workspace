#!/bin/bash
# Watch Zo's live activity log in real-time with pretty formatting

echo "🔴 LIVE: Watching Zo's activity log..."
echo "Press Ctrl+C to stop"
echo ""
echo "Legend:"
echo "  🎯 task_start    - Beginning a new task"
echo "  🔧 tool_call     - Using a tool"
echo "  🧠 decision      - AI reasoning/decision"
echo "  ✅ result        - Task outcome"
echo "  ❌ error         - Something went wrong"
echo ""
echo "────────────────────────────────────────────────────────────"
echo ""

tail -f /home/workspace/.live-log.jsonl | while read -r line; do
    # Parse JSON and format output
    type=$(echo "$line" | jq -r '.type')
    timestamp=$(echo "$line" | jq -r '.timestamp' | cut -d'T' -f2 | cut -d'.' -f1)
    
    case "$type" in
        "task_start")
            echo "🎯 [$timestamp] TASK START"
            echo "$line" | jq -r '.data.task' | sed 's/^/   → /'
            echo ""
            ;;
        "tool_call")
            echo "🔧 [$timestamp] TOOL CALL"
            echo "$line" | jq -r '.data.tool' | sed 's/^/   Tool: /'
            echo "$line" | jq -r '.data.purpose // empty' | sed 's/^/   Purpose: /'
            echo ""
            ;;
        "decision")
            echo "🧠 [$timestamp] DECISION"
            echo "$line" | jq -r '.data.reasoning // empty' | sed 's/^/   Reasoning: /'
            echo "$line" | jq -r '.data.action // empty' | sed 's/^/   Action: /'
            echo ""
            ;;
        "result")
            echo "✅ [$timestamp] RESULT"
            echo "$line" | jq -r '.data.status // empty' | sed 's/^/   Status: /'
            echo "$line" | jq -r '.data.outcome // empty' | sed 's/^/   Outcome: /'
            echo ""
            ;;
        "error")
            echo "❌ [$timestamp] ERROR"
            echo "$line" | jq -r '.data.message // empty' | sed 's/^/   Error: /'
            echo ""
            ;;
        *)
            echo "📝 [$timestamp] $type"
            echo "$line" | jq -r '.data' | sed 's/^/   /'
            echo ""
            ;;
    esac
done
