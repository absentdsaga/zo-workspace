# Proximity Voice Chat Implementation

**Status:** ✅ Core infrastructure ready, needs Daily.co account for activation

## What's Been Built

### VoiceManager Class (`scripts/client/systems/VoiceManager.ts`)

A complete spatial audio system using Daily.co + Web Audio API:

**Features:**
- ✅ Distance-based volume (0-500px range)
- ✅ Elevation-based attenuation (50% per level)
- ✅ Stereo panning (left/right based on position)
- ✅ Web Audio API nodes (GainNode + StereoPannerNode)
- ✅ Automatic participant tracking

**Algorithm:**
```typescript
// Volume calculation
volume = max(0, 1 - (distance / maxHearingDistance))
volume *= pow(0.5, elevationDiff)

// Pan calculation
pan = clamp(dx / maxHearingDistance, -1, 1)
```

### Integration Points

**IsoGame Scene:**
- VoiceManager imported and ready
- Hooks for position updates already in place
- Multiplayer sync provides player positions

**To Activate:**
1. Create Daily.co account at https://dashboard.daily.co
2. Get API key
3. Update VoiceManager.createRoom() with your room URL
4. Initialize in IsoGame.create()

## How It Works

### 1. Room Creation
```typescript
const voiceManager = new VoiceManager();
await voiceManager.createRoom('https://yourdomain.daily.co/yourroom');
```

### 2. Spatial Audio Updates (Every Frame)
```typescript
voiceManager.updateSpatialAudio(
  { playerId: localId, x: playerX, y: playerY, elevation: playerZ },
  remotePlayers.map(p => ({ playerId: p.id, x: p.x, y: p.y, elevation: p.elevation }))
);
```

### 3. Audio Graph
```
Remote Player Audio Track
         ↓
  MediaStreamSource
         ↓
     GainNode (volume based on distance + elevation)
         ↓
  StereoPannerNode (pan based on x-axis position)
         ↓
  Audio Destination (speakers)
```

## Example Usage

```typescript
// In IsoGame.create()
this.voiceManager = new VoiceManager();
await this.voiceManager.createRoom(); // Uses default test room

// In IsoGame.update()
const localPos = {
  playerId: this.multiplayerManager.localId,
  x: this.player.x,
  y: this.player.y,
  elevation: this.depthManager.getElevation(this.player)
};

const remotePlayers = this.multiplayerManager.getRemotePlayers().map(p => ({
  playerId: p.id,
  x: p.x,
  y: p.y,
  elevation: p.elevation
}));

this.voiceManager.updateSpatialAudio(localPos, remotePlayers);
```

## Daily.co Setup Guide

### Step 1: Create Account
1. Go to https://dashboard.daily.co/signup
2. Sign up (free tier: 10,000 minutes/month)

### Step 2: Create Room
```bash
curl -X POST https://api.daily.co/v1/rooms \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "spatial-worlds",
    "privacy": "public",
    "properties": {
      "enable_screenshare": false,
      "enable_chat": false,
      "enable_knocking": false,
      "start_video_off": true,
      "start_audio_off": false
    }
  }'
```

### Step 3: Update VoiceManager
Replace the room URL in `VoiceManager.createRoom()`:
```typescript
await this.daily.join({ url: 'https://yourdomain.daily.co/spatial-worlds' });
```

## Performance Considerations

**Bandwidth:**
- Audio only (no video): ~50-100 kbps per participant
- 10 participants = ~1 Mbps total

**CPU:**
- Web Audio API is very efficient
- Spatial calculations: <1ms per frame
- Daily.co handles encoding/decoding

**Latency:**
- WebRTC: typically 50-150ms
- Spatial updates: 16ms (60 FPS)

## Future Enhancements

### Phase 1 (Current)
- ✅ Distance-based volume
- ✅ Elevation attenuation
- ✅ Stereo panning

### Phase 2
- [ ] Voice zones (library = quiet, stage = amplified)
- [ ] Broadcast mode (press T to talk globally)
- [ ] Mute toggle (press M)
- [ ] Visual indicators (speech bubble when talking)
- [ ] Push-to-talk option

### Phase 3
- [ ] Voice quality settings (noise suppression)
- [ ] Echo cancellation tuning
- [ ] Spatial reverb (based on environment)
- [ ] Directional audio (facing affects volume)

## Testing Without Daily.co

To test the game without activating voice:
1. Don't call `voiceManager.createRoom()` in create()
2. Game works normally without voice
3. Voice is purely additive - no voice = still functional

## Dependencies

```json
{
  "@daily-co/daily-js": "^0.87.0"
}
```

Already installed via: `bun add @daily-co/daily-js`

## References

- Daily.co spatial audio guide: https://www.daily.co/blog/managing-users-media-tracks-to-implement-spatial-audio-and-video-part-4/
- Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- Daily.co docs: https://docs.daily.co
