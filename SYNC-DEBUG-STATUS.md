# Multiplayer Sync Debugging - Current Status

## What I Built
Following your feedback that I needed better testing, I created:

1. **Side-by-side browser comparison tool** (`/tmp/side_by_side_capture.py`)
   - Opens two browser instances simultaneously
   - Moves player in one, captures both views
   - Creates comparison images showing both screens next to each other

2. **Pixel-level offset analyzer** (`/tmp/analyze_offset.py`)
   - Automatically detects sprite positions in both views
   - Calculates exact X/Y offset in pixels
   - Provides diagnostic analysis

## Current Measurement
After latest fixes:
```
Client 1 (local player):  (640, 453)
Client 2 (remote player): (638, 419)

OFFSET:
   ΔX = -2 pixels  ✓ (acceptable)
   ΔY = -34 pixels ❌ (remote player 34px higher)
```

## What I've Fixed So Far

### 1. Client Sends Logical Y (Not Visual Y)
**File:** `scripts/client/scenes/IsoGame.ts` line 377
```typescript
{ x: this.player.x, y: this.player.getData('logicalY') || this.player.y }
```

### 2. Remote Player Uses DepthManager.setIsoData()
**File:** `scripts/client/MultiplayerManager.ts`
- Added `depthManager` instance
- In `updateRemotePlayer()`: Set sprite.y to logical Y, then call `setIsoData()` to convert to visual
- In `update()`: Removed line that was overwriting sprite.y

### 3. Update Loop Doesn't Touch sprite.y
```typescript
update() {
  sprite.x = playerData.targetX;
  // Don't touch sprite.y - managed by setIsoData()
}
```

## Remaining Issue
Remote player is consistently **~34 pixels too high** (lower Y coordinate).

This suggests:
- Visual Y offset might be applied in wrong direction
- OR offset calculated incorrectly somewhere
- OR local player's logicalY calculation has a bug

## Test Files Created
All in `/home/workspace/`:
- `comparison_spawn.png` - Initial spawn positions
- `comparison_moved.png` - After movement
- `comparison_final.png` - Final positions
- `comparison_annotated.png` - With position markers
- `test_separated.png` - Test with players far apart

## Next Steps Needed
1. Verify that `setIsoData()` is actually being called on remote players
2. Check if logicalY recalculation for local player has a sign error
3. Test at different elevations (currently testing at elevation 0)
4. Add visual markers in-game to show exact sprite positions

## Tools Available
- `/tmp/side_by_side_capture.py` - Run full comparison test
- `/tmp/analyze_offset.py` - Analyze existing comparison images
- `/tmp/better_test.py` - Test with separated starting positions

All tools are ready to iterate quickly on fixes.
