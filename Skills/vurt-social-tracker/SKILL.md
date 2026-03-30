---
name: vurt-social-tracker
description: Living state tracker for VURT social media operations. Maintains active titles, clip status, posting decisions, platform ops, and conversation context across sessions. Read this at the START of every VURT social conversation to have full context. Update at the END.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# VURT Social Tracker

## Purpose
Prevents context loss across VURT social conversations. This is the single source of truth for what's happening RIGHT NOW with VURT social ops.

## When to activate
- **START of any VURT social conversation**: Read `state.md` to load context
- **END of any VURT social conversation**: Update `state.md` with new decisions, clip status changes, or platform ops
- **When Dioni shares new info about titles, clips, or posting**: Update immediately

## Files
- `state.md` — The living state file. READ THIS FIRST, ALWAYS.
- `scripts/sync-state.py` — Helper to validate state file and flag stale entries

## How it works

### At conversation start
1. Read `Skills/vurt-social-tracker/state.md`
2. This gives you: active titles, clip status, what was posted where, pending decisions, and recent context

### During conversation
When Dioni shares new info, mentally note it for the state update.

### At conversation end
Update `state.md` with:
- Any new titles or clip information
- Posting decisions made
- Status changes (what was posted, what's pending)
- Platform changes
- Corrections to previous assumptions

## Rules
- State file is structured by active title, not by date
- Keep it concise but complete
- Remove titles that have completed their full arc
- Move completed titles to an "archive" section at the bottom
- Always include the date of last update
