#!/bin/bash
# Start paper trading with master-coordinator logic (1:1 simulation)

cd /home/workspace/Projects/survival-agent

# Load secrets
source ~/.zo_secrets 2>/dev/null || source ~/.bashrc 2>/dev/null

# Run paper trading
bun run testing/paper-trade-master.ts
