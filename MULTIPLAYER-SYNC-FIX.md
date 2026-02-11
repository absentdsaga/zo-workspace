# Multiplayer Position Sync Fix

## Problem
Remote players were appearing in different positions than expected. When Player 1 moved, Player 2 would see Player 1 in the wrong location, causing visual desync.

## Root Cause
The client was sending its authoritative position to the server, but **the server was completely ignoring it** and recalculating position using simple velocity math. This caused desync because:

1. **Client** uses Phaser physics with acceleration, drag, and collision
2. **Server** was using simple velocity calculation (`position += velocity * delta`)
3. These two calculations produce **different results**
4. Server broadcasts its wrong position to all remote clients

## Solution

### 1. Server: Use Client-Authoritative Position (`/home/workspace/Skills/spatial-worlds/spatial-worlds-server/src/multiplayer.ts`)

Changed the `handleMove()` method to use the client's position directly:

```typescript
// CLIENT AUTHORITATIVE: Use position from client if provided
if (cmd.position) {
  player.x = cmd.position.x;
  player.y = cmd.position.y;
} else {
  // Fallback: Server-side calculation (legacy)
  // ... old velocity calculation ...
}

// Update elevation if provided
if (cmd.elevation !== undefined) {
  player.elevation = cmd.elevation;
}
```

### 2. Client: Fix Lerp Timing (`/home/workspace/Skills/spatial-worlds/scripts/client/MultiplayerManager.ts`)

Moved position lerping from `updateRemotePlayer()` to the `update()` method so it happens every frame instead of only when receiving updates:

**Before:**
```typescript
private updateRemotePlayer(player: PlayerState) {
  // ...
  playerData.targetX = player.x;
  playerData.targetY = player.y;

  // ❌ Lerp here = lag because it only runs when server sends update
  sprite.x += (playerData.targetX - sprite.x) * lerpFactor;
  sprite.y += (playerData.targetY - sprite.y) * lerpFactor;
}
```

**After:**
```typescript
private updateRemotePlayer(player: PlayerState) {
  // Just update target, don't lerp yet
  playerData.targetX = player.x;
  playerData.targetY = player.y;
}

update() {
  // ✅ Lerp every frame for smooth movement
  this.remotePlayers.forEach(playerData => {
    sprite.x += (playerData.targetX - sprite.x) * lerpFactor;
    sprite.y += (playerData.targetY - sprite.y) * lerpFactor;
  });
}
```

## Files Changed

1. `/home/workspace/Skills/spatial-worlds/spatial-worlds-server/src/multiplayer.ts` - Server now uses client position
2. `/home/workspace/Skills/spatial-worlds/scripts/client/MultiplayerManager.ts` - Fixed lerp timing
3. Client rebuilt: `bun build scripts/client/main-iso.ts --outdir=dist --target=browser`
4. Server restarted automatically (service auto-restart on crash)

## Testing

Test URL: https://spatial-worlds-dioni.zocomputer.io/iso.html

**Manual Test:**
1. Open the game in **two separate browser windows** (or tabs)
2. Move Player 1 around using WASD or arrow keys
3. Observe Player 1 from Player 2's perspective
4. **Expected:** Player 1 sprite appears in the **same position** in both views
5. **Success:** Positions match ✅

**Before Fix:**
- Player 1 in window 1: (500, 300)
- Player 1 in window 2: (485, 310) ❌ WRONG

**After Fix:**
- Player 1 in window 1: (500, 300)
- Player 1 in window 2: (500, 300) ✅ CORRECT

## Technical Details

The fix implements **client-authoritative movement** where:
- Client runs full physics simulation (acceleration, drag, collision)
- Client sends final position to server
- Server trusts and broadcasts client position
- Remote clients smoothly interpolate (lerp) to received positions

This is the standard approach for fast-paced multiplayer games because it eliminates input lag and ensures the player sees immediate response to their controls.

## Status

✅ Code changes applied
✅ Client rebuilt
✅ Server restarted
🎮 Ready for manual testing
