#!/usr/bin/env python3
"""Send the VURT daily report as inline HTML email body.

Uses Zo's /zo/ask API to delegate email sending to a child agent
that has access to Gmail tools.

Usage: python3 gmail-send.py <html_file> <subject> <to_email>
"""
import sys, os, json, requests, base64, time

def send_report(html_file, subject, to_email):
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("ERROR: No ZO_CLIENT_IDENTITY_TOKEN")
        return False

    with open(html_file) as f:
        html = f.read()

    # Split into chunks if needed — but first try sending via
    # a child agent that reads the file directly
    prompt = f"""You must send an email. Here are the steps:

1. Read the file: {html_file}
2. Use gmail-send-email with:
   - to: {to_email}
   - subject: {subject}
   - bodyType: html
   - body: the ENTIRE file contents from step 1

Do this now. Respond with SENT and the message ID when done."""

    print(f"Sending report ({len(html)} chars) to {to_email}...")
    
    try:
        resp = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={"authorization": token, "content-type": "application/json"},
            json={"input": prompt, "model_name": "anthropic:claude-sonnet-4-5-20250929"},
            timeout=120
        )
        
        if resp.status_code == 200:
            result = resp.json()
            output = result.get("output", "")
            print(f"Result: {output[:300]}")
            return "SENT" in output.upper() or "success" in output.lower()
        else:
            print(f"API error: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gmail-send.py <html_file> <subject> [to_email]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    subject = sys.argv[2]
    to = sys.argv[3] if len(sys.argv) > 3 else "dioni@myvurt.com"
    
    ok = send_report(html_file, subject, to)
    sys.exit(0 if ok else 1)
