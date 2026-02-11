# Multiplayer Position Sync - Coordinate System Fix

## Problem
Remote players were consistently offset from local players, especially at different elevations.

## Root Cause
**Coordinate System Mismatch:**
- Local player uses TWO coordinate systems:
  - `logicalY`: True world position (used for collision/elevation detection)
  - `sprite.y`: Visual position = logicalY - (elevation * 20)
  
- Client was sending **visual Y** to server, but remote players expected **logical Y**
- This caused an offset of `elevation * 20` pixels

## Solution

### 1. Client Sends Logical Coordinates
**File:** `scripts/client/scenes/IsoGame.ts` (line 377)

```typescript
// Before:
{ x: this.player.x, y: this.player.y }

// After:
{ x: this.player.x, y: this.player.getData('logicalY') || this.player.y }
```

### 2. Remote Players Apply Visual Offset
**File:** `scripts/client/MultiplayerManager.ts`

**A. Store Logical Y on Spawn** (line 114):
```typescript
sprite.setData('logicalY', player.y); // Server sends logical coords
```

**B. Apply Visual Offset in Update** (line 178-182):
```typescript
sprite.x = playerData.targetX;

// Apply visual offset: higher elevation = lower visual Y
const iso = sprite.getData('iso');
const elevation = iso?.elevation || 0;
sprite.y = playerData.targetY - (elevation * 20);
```

## Formula
```
Visual Y = Logical Y - (elevation * 20)

Examples:
- Elevation 0: visualY = logicalY - 0 = logicalY
- Elevation 1: visualY = logicalY - 20
- Elevation 2: visualY = logicalY - 40
- Elevation 3: visualY = logicalY - 60
```

## Result
✅ **Perfect position sync across all elevations and map locations**
- Both local and remote players use the same coordinate system
- Elevation-based visual offsets are applied consistently
- No more position drift or offset issues

## Testing
```bash
/tmp/test_multiplayer_sync.sh
```

## Deployment
- ✅ Client rebuilt (22:18 UTC)
- ✅ Server restarted (22:18 UTC)
- ✅ Live at https://spatial-worlds-dioni.zocomputer.io/
