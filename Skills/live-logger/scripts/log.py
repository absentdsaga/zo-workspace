#!/usr/bin/env python3
"""
Lightweight conversation logger - appends events to JSONL files
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def log_event(event_type: str, data: dict, conversation_id: str):
    """Log an event to conversation-specific file"""
    
    # Create log directory
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path(f"/home/workspace/Logs/live/{today}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file per conversation
    log_file = log_dir / f"{conversation_id}.jsonl"
    
    # Create event record
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        **data
    }
    
    # Append to JSONL
    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")
    
    print(f"✓ Logged {event_type} to {log_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: log.py <event_type> '<json_data>' <conversation_id>")
        sys.exit(1)
    
    event_type = sys.argv[1]
    data = json.loads(sys.argv[2])
    conversation_id = sys.argv[3]
    
    log_event(event_type, data, conversation_id)
