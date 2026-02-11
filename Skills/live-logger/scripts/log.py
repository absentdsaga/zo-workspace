#!/usr/bin/env python3
"""
Live logger for Zo conversations.
Logs to conversation-specific files in /home/workspace/Logs/live/YYYY-MM-DD/<conversation_id>.jsonl
"""

import json
import sys
from datetime import datetime
from pathlib import Path

GLOBAL_LOG = Path("/home/workspace/.live-log.jsonl")

def log_entry(event_type: str, data: dict, conversation_id: str = "con_XAjfiRXfSuRTWTCe"):
    """Append a log entry to conversation-specific log file."""
    entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "conversation_id": conversation_id,
        "type": event_type,
        "data": data
    }
    
    # Conversation-specific log
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path(f"/home/workspace/Logs/live/{date_str}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    conv_log = log_dir / f"{conversation_id}.jsonl"
    with open(conv_log, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also write to global log for backwards compatibility
    with open(GLOBAL_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: log.py <event_type> <json_data> [conversation_id]")
        sys.exit(1)
    
    event_type = sys.argv[1]
    data = json.loads(sys.argv[2])
    conversation_id = sys.argv[3] if len(sys.argv) > 3 else "con_XAjfiRXfSuRTWTCe"
    
    log_entry(event_type, data, conversation_id)
