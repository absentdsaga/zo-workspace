#!/bin/bash
# MAINNET Dashboard configuration
# Separate from paper config - points to mainnet data files

# Data sources
export LOG_FILE="/tmp/mainnet-trade.log"
export STATS_FILE="/home/workspace/Projects/survival-agent/data/mainnet-trades-master.json"

# Trading parameters (match mainnet.config.ts)
export STARTING_BALANCE=0.147808781
export MAX_POSITIONS=7

# Display settings
export REFRESH_INTERVAL=3  # seconds
export MODE_LABEL="MAINNET"
export MODE_COLOR='\033[0;31m'  # Red for mainnet

# Colors (same as paper)
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export CYAN='\033[0;36m'
export MAGENTA='\033[0;35m'
export WHITE='\033[1;37m'
export NC='\033[0m'
export BOLD='\033[1m'
export DIM='\033[2m'
