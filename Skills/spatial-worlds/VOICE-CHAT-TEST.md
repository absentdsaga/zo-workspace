# Voice Chat Testing Guide

## Current Status

Voice chat is **initialized and working** in the code:
- ✅ Daily.co integration active
- ✅ Room joining functional
- ✅ Participant tracking working
- ⚠️ Needs manual testing (can't test audio in headless browsers)

## Automated Test Results

From headless browser test:
```
🎤 Joining voice room: https://ourroom.daily.co/spatial-worlds
✅ Voice chat initialized
👤 Participant joined (x5 total participants detected)
Devices Error (No Mic): NotFoundError: Requested device not found
```

**Analysis**: The error is expected - headless browsers don't have microphones. The important parts work:
1. Connects to Daily.co room
2. Tracks participants
3. Initializes without crashing

## Manual Testing Instructions

To properly test voice chat with 2+ players:

### Step 1: Open Multiple Browser Windows

1. Open Chrome/Firefox in **two separate windows** (not tabs)
2. Navigate to: `https://spatial-worlds-dioni.zocomputer.io/`
3. **Grant microphone permissions** when prompted in both windows

### Step 2: Test Proximity Voice

1. In Window 1: Move your player around with arrow keys
2. In Window 2: Move your player around
3. **Speak into your microphone** in Window 1
4. **Listen for audio** in Window 2

Expected behavior:
- Voice should be **louder** when players are close
- Voice should **fade** as players move apart
- Voice should be **muted** when players are far apart

### Step 3: Verify in Console

Open Developer Console (F12) in each window and check for:

```
✅ Voice chat initialized
👤 Participant joined: <player_id>
🔊 Audio level updated: <level>
📍 Position updated: (x, y)
```

### Step 4: Test Multi-Player

Open a **third browser window** to test with 3+ players:
- All players should hear each other based on proximity
- Voice should spatialize (louder players = closer players)

## Known Issues

1. **Microphone Permission**: Must be granted explicitly
2. **HTTPS Required**: Voice won't work on `http://localhost`
3. **Browser Compatibility**: Works best in Chrome/Edge

## Daily.co Room

The voice room is:
```
https://ourroom.daily.co/spatial-worlds
```

You can visit this URL directly to see the Daily.co interface and test audio.

## Voice Manager Code

Location: `scripts/client/VoiceManager.ts`

Key features:
- Proximity-based volume
- Participant tracking
- Audio spatialization
- Name label sync

## Troubleshooting

### No Audio Heard
1. Check microphone permissions in browser
2. Verify other player is actually speaking
3. Check browser console for errors
4. Try refreshing both windows

### Volume Too Low
1. Check system volume
2. Check browser tab is not muted
3. Move players closer together
4. Check Daily.co room settings

### Participants Not Showing
1. Check WebSocket connection (should see "Connected to multiplayer server")
2. Verify both players joined the room
3. Check console for "Participant joined" messages
