# Voice Chat Setup Instructions

Voice chat is **already integrated** into the game! You just need to provide a Daily.co room.

## Quick Start (5 minutes)

### Option 1: Use a Public Demo Room (Easiest)
1. Go to https://daily.co
2. Click "Create a demo room" (no signup required)
3. Copy the room URL (e.g., `https://your-domain.daily.co/your-room`)
4. Update `scripts/client/systems/VoiceManager.ts` line 41:
   ```typescript
   const targetUrl = roomUrl || 'YOUR_ROOM_URL_HERE';
   ```
5. Rebuild: `bun run build`
6. Test with 2 browser windows!

### Option 2: Create a Daily.co Account (Recommended)
1. Sign up at https://dashboard.daily.co
2. Create a new room in the dashboard
3. Set room to "public" (no tokens required)
4. Copy the room URL
5. Update code (same as Option 1)

### Option 3: Dynamic Room Creation (Advanced)
1. Get your Daily API key from https://dashboard.daily.co/developers
2. Save it to `.env`:
   ```
   DAILY_API_KEY=your_key_here
   ```
3. Use the API to create rooms on-demand (requires server endpoint)

## Testing Voice Chat

### 1. Solo Test
Open https://spatial-worlds-dioni.zocomputer.io and check console:
```
🎤 Joining voice room: https://...
✅ Voice chat initialized
```

### 2. Multi-Player Test
1. Open game in 2 browser windows (or 2 devices)
2. Allow microphone in both
3. Walk characters close together → Hear each other
4. Walk apart → Voice fades (max 500px range)
5. Different elevations → Volume reduces 50% per level

## Current Room URL

The game is configured to use:
```
https://ourroom.daily.co/spatial-worlds
```

**This room doesn't exist!** You need to create it or use your own.

## Troubleshooting

**"Failed to join voice room"**
- Check the room URL exists
- Make sure it's public (no token required)
- Check microphone permissions

**"No audio from other players"**
- Both players must be in the same room
- Check browser console for errors
- Try moving characters closer (< 500px)

**"Audio is choppy/laggy"**
- Check network connection
- Voice updates run at 10 FPS (throttled for performance)
- Consider increasing update rate in `IsoGame.ts` line 385

## What's Already Implemented

✅ Daily.co WebRTC integration
✅ Distance-based volume (0-500px range)
✅ Elevation attenuation (50% per level)
✅ Stereo panning (left/right positioning)
✅ Automatic audio node management
✅ Web Audio API spatial processing
✅ 10 FPS spatial audio updates (optimized)

## Next Steps

Once voice is working, add:
- [ ] Mute button UI
- [ ] Voice indicator (speech bubble when talking)
- [ ] Push-to-talk mode
- [ ] Volume sliders
- [ ] Player names above sprites
