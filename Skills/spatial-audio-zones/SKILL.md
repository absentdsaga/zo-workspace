---
name: spatial-audio-zones
description: Advanced 3D spatial audio system with elevation-aware proximity, reverb zones, occlusion, and broadcast modes for isometric multiplayer worlds.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: audio-engine
  version: 1.0.0
---

# Spatial Audio Zones

Professional-grade spatial audio for isometric tactical worlds with elevation-aware proximity, acoustic zones, and seamless voice room transitions.

## Acoustic Design Philosophy

In isometric worlds, **space = sound**:
- Elevated platforms feel isolated (quieter ambient)
- Ground plazas amplify crowd energy
- Narrow corridors create intimacy
- Open amphitheaters enable broadcasts

## 3D Audio Model

### Distance + Elevation Attenuation
```typescript
class SpatialAudioEngine {
  calculateVolume(
    listener: { x: number, y: number, elevation: number },
    speaker: { x: number, y: number, elevation: number }
  ): number {
    // 2D distance (XY plane)
    const dx = speaker.x - listener.x;
    const dy = speaker.y - listener.y;
    const distance2D = Math.sqrt(dx * dx + dy * dy);
    
    // Elevation distance (Z axis)
    const dz = Math.abs(speaker.elevation - listener.elevation) * 64; // pixels per level
    
    // 3D distance (Pythagorean)
    const distance3D = Math.sqrt(distance2D * distance2D + dz * dz);
    
    // Exponential falloff (more realistic than linear)
    const maxRange = 500; // pixels
    const rawVolume = Math.max(0, 1 - (distance3D / maxRange));
    const volume = Math.pow(rawVolume, 2); // Exponential curve
    
    return volume;
  }
  
  // Elevation attenuation (additional penalty)
  elevationPenalty(elevationDiff: number): number {
    // Each level reduces volume by 40%
    return Math.pow(0.6, elevationDiff);
  }
}
```

## Acoustic Zone Types

### 1. Intimate Zones (2-4 people)
```typescript
interface IntimateZone {
  type: 'intimate';
  maxRange: 200; // pixels
  reverb: 'dry'; // No echo
  occlusion: true; // Walls block sound
  maxParticipants: 4;
}

// Example: Garden alcove, private booth
```

### 2. Social Zones (5-15 people)
```typescript
interface SocialZone {
  type: 'social';
  maxRange: 350;
  reverb: 'room'; // Slight echo
  occlusion: true;
  maxParticipants: 15;
}

// Example: Tavern interior, small plaza
```

### 3. Plaza Zones (15-50 people)
```typescript
interface PlazaZone {
  type: 'plaza';
  maxRange: 500;
  reverb: 'hall'; // Medium echo
  occlusion: false; // Open air
  maxParticipants: 50;
}

// Example: Town square, market
```

### 4. Amphitheater Zones (50-100 people)
```typescript
interface AmphitheaterZone {
  type: 'amphitheater';
  maxRange: 800;
  reverb: 'large-hall'; // Strong echo
  occlusion: false;
  broadcastMode: true; // Speaker → audience
  maxParticipants: 100;
}

// Example: Lecture hall, concert stage
```

## Reverb Implementation

### Web Audio API Reverb
```typescript
class ReverbProcessor {
  private audioContext: AudioContext;
  private convolver: ConvolverNode;
  
  constructor() {
    this.audioContext = new AudioContext();
    this.convolver = this.audioContext.createConvolver();
    this.loadImpulseResponse('hall');
  }
  
  async loadImpulseResponse(type: 'dry' | 'room' | 'hall' | 'large-hall') {
    const impulseFiles = {
      'dry': null, // No reverb
      'room': 'reverb/small-room.wav',
      'hall': 'reverb/concert-hall.wav',
      'large-hall': 'reverb/cathedral.wav',
    };
    
    const file = impulseFiles[type];
    if (!file) {
      this.convolver.buffer = null;
      return;
    }
    
    const response = await fetch(file);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
    
    this.convolver.buffer = audioBuffer;
  }
  
  applyReverb(source: MediaStreamAudioSourceNode, wetness: number) {
    // Dry signal (direct)
    const dryGain = this.audioContext.createGain();
    dryGain.gain.value = 1 - wetness;
    source.connect(dryGain);
    dryGain.connect(this.audioContext.destination);
    
    // Wet signal (reverb)
    const wetGain = this.audioContext.createGain();
    wetGain.gain.value = wetness;
    source.connect(this.convolver);
    this.convolver.connect(wetGain);
    wetGain.connect(this.audioContext.destination);
  }
}
```

## Occlusion (Walls Block Sound)

### Raycast-Based Occlusion
```typescript
class OcclusionSystem {
  checkOcclusion(
    listener: { x: number, y: number, elevation: number },
    speaker: { x: number, y: number, elevation: number },
    tilemap: Phaser.Tilemaps.Tilemap
  ): number {
    // Only check occlusion if on same elevation
    if (listener.elevation !== speaker.elevation) {
      return 1.0; // Different levels = no occlusion
    }
    
    // Raycast from listener to speaker
    const line = new Phaser.Geom.Line(
      listener.x, listener.y,
      speaker.x, speaker.y
    );
    
    // Check for wall intersections
    const wallLayer = tilemap.getLayer('walls')!.tilemapLayer;
    const intersects = this.lineIntersectsWalls(line, wallLayer);
    
    if (intersects) {
      // Walls reduce volume by 80%
      return 0.2;
    }
    
    return 1.0; // No occlusion
  }
  
  lineIntersectsWalls(
    line: Phaser.Geom.Line,
    wallLayer: Phaser.Tilemaps.TilemapLayer
  ): boolean {
    const points = line.getPoints(16); // Sample 16 points along line
    
    for (const point of points) {
      const tile = wallLayer.getTileAtWorldXY(point.x, point.y);
      if (tile && tile.properties.blocking) {
        return true;
      }
    }
    
    return false;
  }
}
```

## Dynamic Voice Rooms

### Room Clustering Algorithm
```typescript
class VoiceRoomManager {
  calculateRooms(
    players: PlayerState[],
    zones: AcousticZone[]
  ): Map<string, string[]> {
    const rooms = new Map<string, string[]>();
    
    players.forEach(player => {
      // Determine which zone player is in
      const zone = this.getZoneAt(player.x, player.y, player.elevation, zones);
      
      // Find nearby players in same zone
      const nearby = players.filter(other => {
        if (other.id === player.id) return false;
        
        const sameZone = this.getZoneAt(other.x, other.y, other.elevation, zones) === zone;
        if (!sameZone) return false;
        
        // Check 3D distance
        const volume = this.audioEngine.calculateVolume(player, other);
        return volume > 0.1; // Audibility threshold
      });
      
      // Create or join room
      const roomId = this.assignRoom(player, nearby, zone);
      
      if (!rooms.has(roomId)) {
        rooms.set(roomId, []);
      }
      rooms.get(roomId)!.push(player.id);
    });
    
    return rooms;
  }
  
  assignRoom(
    player: PlayerState,
    nearby: PlayerState[],
    zone: AcousticZone
  ): string {
    // Use spatial hashing for room IDs
    const cellSize = zone.maxRange;
    const cellX = Math.floor(player.x / cellSize);
    const cellY = Math.floor(player.y / cellSize);
    
    return `${zone.name}-${cellX}-${cellY}-${player.elevation}`;
  }
}
```

## Broadcast Mode (Stages/Lectures)

### Asymmetric Audio Routing
```typescript
class BroadcastMode {
  setupBroadcast(
    speakerId: string,
    audienceIds: string[],
    dailyRoom: DailyCall
  ) {
    // Speaker's audio is heard by all
    audienceIds.forEach(audienceId => {
      dailyRoom.updateParticipantAudioLevel(speakerId, 1.0, audienceId);
    });
    
    // Audience members don't hear each other (unless nearby)
    audienceIds.forEach(id1 => {
      audienceIds.forEach(id2 => {
        if (id1 === id2) return;
        
        // Check if audience members are close (allow side conversations)
        const player1 = this.getPlayer(id1);
        const player2 = this.getPlayer(id2);
        
        const distance = this.calculateDistance(player1, player2);
        const volume = distance < 100 ? 0.3 : 0.0; // Quiet side chat
        
        dailyRoom.updateParticipantAudioLevel(id1, volume, id2);
      });
    });
  }
}
```

## Seamless Room Transitions

### Gradual Fade Between Rooms
```typescript
class RoomTransitionManager {
  private currentRoom?: string;
  private nextRoom?: string;
  private transitionProgress = 0;
  
  async transitionTo(newRoomId: string, dailyClient: DailyCall) {
    if (this.currentRoom === newRoomId) return;
    
    this.nextRoom = newRoomId;
    
    // Fade out current room
    await this.fadeVolume(this.currentRoom, 1.0, 0.0, 500);
    
    // Switch rooms
    await dailyClient.leave();
    await dailyClient.join({ url: `https://yourapp.daily.co/${newRoomId}` });
    
    // Fade in new room
    await this.fadeVolume(newRoomId, 0.0, 1.0, 500);
    
    this.currentRoom = newRoomId;
    this.nextRoom = undefined;
  }
  
  async fadeVolume(
    roomId: string,
    fromVolume: number,
    toVolume: number,
    duration: number
  ) {
    const steps = 30;
    const stepDuration = duration / steps;
    
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const volume = Phaser.Math.Linear(fromVolume, toVolume, t);
      
      // Apply to all participants in room
      this.setRoomVolume(roomId, volume);
      
      await this.sleep(stepDuration);
    }
  }
}
```

## Daily.co Integration

### Setup Spatial Audio
```typescript
import Daily, { DailyCall } from '@daily-co/daily-js';

class DailySpatialAudio {
  private call?: DailyCall;
  private audioEngine: SpatialAudioEngine;
  
  async init(roomUrl: string) {
    this.call = Daily.createCallObject();
    this.audioEngine = new SpatialAudioEngine();
    
    await this.call.join({ url: roomUrl });
    
    // Listen for participant updates
    this.call.on('participant-updated', this.updateParticipantAudio.bind(this));
  }
  
  updateParticipantAudio(event: any) {
    const participants = this.call!.participants();
    const localPlayer = this.getLocalPlayer();
    
    Object.values(participants).forEach((participant: any) => {
      if (participant.local) return;
      
      const remotePlayer = this.getPlayerById(participant.user_id);
      if (!remotePlayer) return;
      
      // Calculate 3D spatial volume
      const volume = this.audioEngine.calculateVolume(localPlayer, remotePlayer);
      
      // Apply occlusion
      const occlusionFactor = this.occlusionSystem.checkOcclusion(
        localPlayer,
        remotePlayer,
        this.tilemap
      );
      
      const finalVolume = volume * occlusionFactor;
      
      // Update Daily.co audio level
      this.call!.updateParticipantAudioLevel(participant.session_id, finalVolume);
    });
  }
}
```

## Performance Optimization

### Audio Update Throttling
```typescript
class AudioUpdateScheduler {
  private lastUpdate = 0;
  private updateRate = 100; // ms (10 Hz)
  
  shouldUpdate(): boolean {
    const now = Date.now();
    if (now - this.lastUpdate > this.updateRate) {
      this.lastUpdate = now;
      return true;
    }
    return false;
  }
  
  update(players: PlayerState[]) {
    if (!this.shouldUpdate()) return;
    
    // Update all spatial audio volumes
    this.audioEngine.updateAll(players);
  }
}
```

## Acoustic Zone Definition (Tiled)

### Define Zones in Tiled Maps
```json
{
  "name": "plaza-acoustic-zone",
  "type": "object",
  "properties": {
    "acoustic_type": "plaza",
    "max_range": 500,
    "reverb": "hall",
    "occlusion": false,
    "max_participants": 50
  },
  "polygon": [
    { "x": 0, "y": 0 },
    { "x": 800, "y": 0 },
    { "x": 800, "y": 800 },
    { "x": 0, "y": 800 }
  ]
}
```

### Load Zones from Tiled
```typescript
class AcousticZoneLoader {
  loadFromTilemap(tilemap: Phaser.Tilemaps.Tilemap): AcousticZone[] {
    const zones: AcousticZone[] = [];
    
    const objectLayer = tilemap.getObjectLayer('acoustic-zones');
    if (!objectLayer) return zones;
    
    objectLayer.objects.forEach(obj => {
      const zone: AcousticZone = {
        name: obj.name,
        type: obj.properties.acoustic_type,
        maxRange: obj.properties.max_range,
        reverb: obj.properties.reverb,
        occlusion: obj.properties.occlusion,
        maxParticipants: obj.properties.max_participants,
        bounds: this.polygonToBounds(obj.polygon),
      };
      
      zones.push(zone);
    });
    
    return zones;
  }
}
```

## Quality Metrics

### Audio Quality Monitoring
```typescript
class AudioQualityMonitor {
  monitorQuality(call: DailyCall) {
    setInterval(() => {
      const stats = call.getNetworkStats();
      
      const metrics = {
        packetLoss: stats.stats.latest.packetLoss,
        jitter: stats.stats.latest.jitter,
        latency: stats.stats.latest.rtt,
      };
      
      // Alert if quality degrades
      if (metrics.packetLoss > 0.05) {
        console.warn('High packet loss:', metrics.packetLoss);
      }
      
      if (metrics.latency > 200) {
        console.warn('High latency:', metrics.latency);
      }
      
      // Log metrics
      this.logMetrics(metrics);
    }, 5000);
  }
}
```

## Scripts

- `scripts/test-spatial-audio.ts` — Test 3D audio with mock players
- `scripts/benchmark-voice-zones.ts` — Measure zone calculation performance
- `scripts/generate-reverb-impulses.ts` — Create impulse response files
- `scripts/calibrate-attenuation.ts` — Tune distance curves

## Integration with Spatial Worlds

This skill provides the **voice layer** for Spatial Worlds:
1. 3D spatial audio with elevation
2. Acoustic zone system
3. Room clustering and transitions
4. Broadcast mode for events
5. Occlusion for realistic sound blocking

Use this on **Day 5-6** after multiplayer is working.

## Advanced Features

### Directional Audio (Stereo Panning)
```typescript
class DirectionalAudio {
  calculatePan(
    listener: { x: number, y: number, facing: number },
    speaker: { x: number, y: number }
  ): number {
    // Angle from listener to speaker
    const dx = speaker.x - listener.x;
    const dy = speaker.y - listener.y;
    const angle = Math.atan2(dy, dx);
    
    // Listener's facing direction
    const facingRad = listener.facing * Math.PI / 180;
    
    // Relative angle (-180 to 180)
    let relativeAngle = angle - facingRad;
    if (relativeAngle > Math.PI) relativeAngle -= 2 * Math.PI;
    if (relativeAngle < -Math.PI) relativeAngle += 2 * Math.PI;
    
    // Pan value (-1 left, 0 center, 1 right)
    const pan = Math.sin(relativeAngle);
    
    return pan;
  }
}
```

### Ambient Soundscapes
```typescript
class AmbientSoundManager {
  private ambientTracks = new Map<string, Howl>();
  
  loadAmbient(zone: AcousticZone) {
    const soundFile = this.getSoundForZone(zone.type);
    
    const ambient = new Howl({
      src: [soundFile],
      loop: true,
      volume: 0.3,
      spatial: true,
    });
    
    this.ambientTracks.set(zone.name, ambient);
  }
  
  updateAmbient(playerPosition: { x: number, y: number, elevation: number }) {
    // Fade ambient based on zone proximity
    this.ambientTracks.forEach((track, zoneName) => {
      const zone = this.getZone(zoneName);
      const distance = this.distanceToZone(playerPosition, zone);
      
      const volume = Math.max(0, 1 - (distance / 200)) * 0.3;
      track.volume(volume);
    });
  }
}
```

This skill brings **world-class spatial audio** to isometric multiplayer worlds.
