#!/usr/bin/env python3
"""
Direct Gmail sender for VURT daily report.

Reads the generated HTML file and sends via Pipedream Gmail action.
This script outputs instructions for the AI agent — it does NOT call Gmail directly.
The AI agent must follow the printed instructions exactly.

Usage:
  python3 send-email-direct.py <html_path> [to_email]
"""
import sys, os, json
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 send-email-direct.py <html_path> [to_email]")
        sys.exit(1)

    html_path = sys.argv[1]
    to_email = sys.argv[2] if len(sys.argv) > 2 else "dioni@myvurt.com"

    if not os.path.exists(html_path):
        print(f"ERROR: File not found: {html_path}")
        sys.exit(1)

    file_size = os.path.getsize(html_path)
    date_display = datetime.now().strftime("%B %d, %Y")
    subject = f"VURT Daily Analytics Report — {date_display}"

    print("SEND_INSTRUCTIONS_START")
    print(json.dumps({
        "action": "use_app_gmail",
        "tool_name": "gmail-send-email",
        "configured_props": {
            "email": "dioniproduces@gmail.com",
            "to": to_email,
            "subject": subject,
            "bodyType": "html",
            "body": f"READ_FROM_FILE:{html_path}"
        },
        "instructions": [
            f"1. Read the FULL file at: {html_path} ({file_size} bytes)",
            "2. Call use_app_gmail with tool_name='gmail-send-email'",
            f"3. Set bodyType='html' (NOT content_type)",
            f"4. Set body = the complete file contents (do NOT truncate)",
            f"5. Set to='{to_email}'",
            f"6. Set subject='{subject}'",
            "7. Set email='dioniproduces@gmail.com'"
        ]
    }, indent=2))
    print("SEND_INSTRUCTIONS_END")
    print(f"\nFile: {html_path}")
    print(f"Size: {file_size:,} bytes")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")

if __name__ == "__main__":
    main()
