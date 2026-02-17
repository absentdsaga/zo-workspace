#!/bin/bash
# Dashboard configuration - separate from bot version
# This file should remain stable across bot upgrades

# Data sources
export LOG_FILE="/tmp/paper-trade.log"
export STATS_FILE="/tmp/paper-trades-master.json"

# Trading parameters (update these when bot settings change)
export STARTING_BALANCE=0.5

# Display settings
export REFRESH_INTERVAL=3  # seconds
export MAX_POSITIONS=7
export MODE_LABEL="PAPER"
export MODE_COLOR='\033[0;36m'  # Cyan for paper

# Colors
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
