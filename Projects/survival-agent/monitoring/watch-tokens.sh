#!/bin/bash
# Watch token positions in real-time

while true; do
  bun run /home/workspace/Projects/survival-agent/monitoring/token-monitor.ts
  sleep 30
done
