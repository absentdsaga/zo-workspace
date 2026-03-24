#!/usr/bin/env python3
"""Send VURT daily report as inline HTML email via Gmail API.

Usage: python3 send-gmail.py <html_file> <subject> [to_email]
"""
import sys, os, json, base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request

def get_gmail_access_token():
    """Get Gmail access token using Zo's app integration."""
    # We'll use the Zo API to send via Gmail instead
    # This script is meant to be called by the agent which has direct tool access
    pass

def build_raw_email(html_body, subject, to_email, from_email="dioniproduces@gmail.com"):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    
    # Plain text fallback
    plain = "View this email in an HTML-capable client for the full formatted report."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()

if __name__ == "__main__":
    html_file = sys.argv[1]
    subject = sys.argv[2]
    to = sys.argv[3] if len(sys.argv) > 3 else "dioni@myvurt.com"
    
    with open(html_file) as f:
        html = f.read()
    
    raw = build_raw_email(html, subject, to)
    
    # Output the raw base64 for the agent to use with Gmail API
    print(json.dumps({"raw": raw, "to": to, "subject": subject}))
