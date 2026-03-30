#!/usr/bin/env python3
"""Send the VURT daily report as inline HTML email body.

Uses Zo's /zo/tools/use_app_gmail/run API to send directly.

Usage: python3 gmail-send.py <html_file> <subject> <to_email>
"""
import sys, os, json, requests

def send_report(html_file, subject, to_email):
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("ERROR: No ZO_CLIENT_IDENTITY_TOKEN")
        return False

    with open(html_file) as f:
        html = f.read()

    print(f"Sending report ({len(html)} chars) to {to_email}...")

    configured_props = json.dumps({
        "to": to_email,
        "subject": subject,
        "bodyType": "html",
        "body": html,
    })

    payload = {
        "args": {
            "tool_name": "gmail-send-email",
            "email": "dioniproduces@gmail.com",
            "configured_props": configured_props,
        }
    }

    try:
        resp = requests.post(
            "https://api.zo.computer/zo/tools/use_app_gmail/run",
            headers={"authorization": token, "content-type": "application/json"},
            json=payload,
            timeout=120,
        )

        if resp.status_code == 200:
            result = resp.json()
            if result.get("success"):
                print(f"SENT: {result.get('result', '')[:200]}")
                return True
            else:
                print(f"Tool error: {result.get('error', result)}")
                return False
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
