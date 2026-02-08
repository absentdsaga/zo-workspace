---
name: shared-claude
description: Share a Claude Pro subscription ($20/m) with another Zo user by configuring their Zo to use your Claude session as the AI provider.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Shared Claude Pro Setup

Share your Claude Pro subscription with another Zo user. They'll use your tokens through Claude Code (the ACP provider).

## How It Works

Zo can use "Claude Code" (ACP) as an AI provider, which connects to a Claude Pro subscription. By sharing your Claude session cookie, another Zo user can use your tokens.

## Setup Instructions

### Step 1: Get Your Claude Session Token

1. Log into https://claude.ai in your browser
2. Open DevTools (F12) → Application → Cookies → claude.ai
3. Find the cookie named `sessionKey` 
4. Copy its value (starts with `sk-ant-`)

### Step 2: On the Other Person's Zo

1. Go to [Settings > Advanced](/?t=settings&s=advanced)
2. Add a secret named `CLAUDE_SESSION_KEY` with the cookie value
3. Go to [Settings > AI > Providers](/?t=settings&s=your-ai&d=providers)
4. Select "Claude Code (ACP)" as the provider
5. It should automatically use the session key

## Important Notes

- **Session expires**: The cookie may expire periodically. You'll need to share a fresh one when it does.
- **Rate limits apply**: You're both sharing the same rate limits, so coordinate heavy usage.
- **Privacy**: They can't see your Claude.ai conversation history, but usage counts against your subscription.
- **Security**: Only share with people you trust. They could theoretically access your Claude account.

## Troubleshooting

If it stops working:
1. Log into claude.ai again in your browser
2. Get a fresh `sessionKey` cookie
3. Update the secret on their Zo
