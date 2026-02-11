---
name: live-logger
description: Real-time logging system that captures all AI actions, tool calls, and decisions as they happen during conversations
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---

# Live Logger

This skill provides real-time logging of all AI actions during conversations.

## How It Works

The live log is written to `/home/workspace/.live-log.jsonl` in append-only JSONL format.

Each line is a JSON object with:
- `timestamp`: ISO 8601 timestamp
- `conversation_id`: Current conversation ID
- `type`: Event type (tool_call, decision, result, error)
- `data`: Event-specific data

## Monitoring

Watch the live log in real-time:

```bash
tail -f /home/workspace/.live-log.jsonl
```

Or with pretty formatting:

```bash
tail -f /home/workspace/.live-log.jsonl | jq '.'
```

## Log Types

- `tool_call`: When a tool is invoked
- `decision`: Reasoning about what to do next
- `result`: Tool results and outcomes
- `error`: Errors encountered
- `task_start`: Beginning of a new task
- `task_end`: Task completion

## Query Logs

```bash
# Today's activity
jq 'select(.timestamp | startswith("2026-02-09"))' .live-log.jsonl

# Specific conversation
jq 'select(.conversation_id == "con_XAjfiRXfSuRTWTCe")' .live-log.jsonl

# All tool calls
jq 'select(.type == "tool_call")' .live-log.jsonl

# Errors only
jq 'select(.type == "error")' .live-log.jsonl
```
