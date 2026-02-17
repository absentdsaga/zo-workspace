---
name: live-logger
description: Real-time logging system that captures all AI actions, tool calls, and decisions as they happen during conversations. These logs are easily retrievable by zo.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---
# Live Logger

Logs every significant action, tool call, decision, and result during conversations to conversation-specific log files. Prevents context loss and enables post-conversation analysis.

## Usage

The AI should automatically call the logging script after significant actions:

```bash
python3 /home/workspace/Skills/live-logger/scripts/log.py "<event_type>" '<json_data>' "<conversation_id>"
```

**Event Types:**
- `task_start` - When starting a new task
- `tool_call` - After any tool invocation
- `decision` - When making a strategic decision
- `result` - When completing an action
- `error` - When encountering an error

**Log Location:**
`/home/workspace/Logs/live/YYYY-MM-DD/<conversation_id>.jsonl`

## Example

```bash
# Log a decision
python3 /home/workspace/Skills/live-logger/scripts/log.py "decision" '{"action": "stop_bot", "reason": "poor_performance", "metrics": {"win_rate": 0.36, "pnl": -0.18}}' "conv_123"

# Log a tool result
python3 /home/workspace/Skills/live-logger/scripts/log.py "result" '{"tool": "Bash", "output": "Bot stopped", "success": true}' "conv_123"
```

## Benefits

- **No context loss** between conversation turns
- **Audit trail** of all AI actions and reasoning
- **Performance analysis** after sessions
- **Debugging** when things go wrong
- **Conversation replay** capability
