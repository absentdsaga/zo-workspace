# VURT Weekly Triage Card Creator

## Overview
This script creates a weekly triage card on the VURT Production Trello board every Monday at 9 AM.

## Script Location
`/home/workspace/Scripts/vurt_trello_weekly_triage.py`

## What It Does
1. Fetches the "This Week" list from the VURT Production Trello board (ID: PVtV7XaC)
2. Creates a new card titled "Weekly Triage: Review Inbox, prioritize This Week"
3. Card includes a checklist:
   - Review all Inbox cards
   - Move priority items to This Week
   - Archive anything in Inbox older than 3 weeks
   - Check Review/Blocked for stuck items
   - 15 minutes max
4. Card is positioned at the top of the list
5. Due date is set to the same day (Monday) at end of day

## Logs
Logs are written to: `/home/workspace/Logs/live/vurt_weekly_triage_YYYY-MM-DD.jsonl`

## Manual Setup Required
Since the `create_agent` tool is not available in the current session, you need to create the scheduled agent manually through the Zo UI:

1. Go to [Agents](/?t=agents)
2. Click "Create Agent" or the + button
3. Name: "VURT Weekly Triage"
4. Schedule: FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0 (Every Monday at 9 AM)
5. Instruction: Copy the contents of `/home/workspace/Scripts/vurt_trello_weekly_triage.py` or use the following prompt:

```
VURT Trello Weekly Triage Card Creator.

Run the script at /home/workspace/Scripts/vurt_trello_weekly_triage.py using python3.
Log output to /home/workspace/Logs/live/ with today's date.
```

## Environment Variables Required
- `TRELLO_VURT_API_KEY` - Trello API key
- `TRELLO_VURT_API_TOKEN` - Trello API token

These should already be set in your Zo Computer environment.

## Testing
Run the script manually to test:
```bash
python3 /home/workspace/Scripts/vurt_trello_weekly_triage.py
```

## Last Test Result
✅ Successfully created triage card on 2026-03-23
- Card ID: 69c13e5a3dbe8f1f5c6769a4
- Card URL: https://trello.com/c/u4eKbYc0