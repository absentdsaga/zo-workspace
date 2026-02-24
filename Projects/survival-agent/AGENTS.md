# Survival Agent - Solana Trading Bot

## Single Source of Truth

**CRITICAL**: All position data must come from one canonical source to avoid inconsistencies.

### Data Source
- Primary: `/tmp/paper-trades-master.json`
- Monitor: Use `paper-trade-monitor` skill for clean display
- Command: `./show-positions.sh` (now uses the skill)

### Why This Matters
The old bash script had complex jq string formatting that created garbled output with:
- Duplicate percentage calculations (Entry % AND P&L %)
- Broken display formatting
- Scientific notation rendering issues

### Clean Monitor
The `paper-trade-monitor` skill provides:
1. Single source of truth from JSON
2. Validated data integrity
3. Clean formatting with proper price display
4. Accurate P&L calculations

### Commands
```bash
# View positions (clean)
./show-positions.sh

# Validate data integrity
bun /home/workspace/Skills/paper-trade-monitor/scripts/validate.ts

# Raw monitor
bun /home/workspace/Skills/paper-trade-monitor/scripts/monitor.ts
```

## Current Status

**Franklin Example:**
- The notification showing "+18.16% P&L" was from when price was pumping
- Current reality: **-6.76% P&L** (price dumped after)
- This is normal meme coin behavior (pump then dump)

Always trust the current monitor output, not old notifications.
