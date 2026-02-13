# NFT Sprite Testing Guide

## How to Test NFT Sprites Before Implementation

This guide shows how to test individual NFT sprites in the actual game to verify they look good and move well, **without** building any character selection UI.

---

## Quick Start

### Test a Single NFT Sprite

```bash
cd /home/workspace/Skills/spatial-worlds

# Test the blue character (set2-char2)
./test-nft-sprite.sh set2-char2

# Or test any other sprite:
./test-nft-sprite.sh set1-char1
./test-nft-sprite.sh set3-char5
./test-nft-sprite.sh set4-char6
```

### Restore Normal Mode

```bash
./restore-normal-mode.sh
```

---

## What Gets Tested

When you run test mode, the game will:
- ✅ Load ONE specific NFT sprite instead of warrior
- ✅ Use that sprite as the player character
- ✅ Show the sprite moving in all 8 directions
- ✅ Display the sprite at game scale (1.5x)
- ✅ Show transparency (or lack thereof)
- ✅ Demonstrate animation smoothness
- ✅ Keep all NPCs as warriors (for size comparison)

---

## Testing Checklist

### ✅ Visual Quality
- [ ] **Sprite renders** - Character visible (not invisible/broken)
- [ ] **Correct size** - Matches NPC size (not giant or tiny)
- [ ] **Clean transparency** - No beige/tan background box
- [ ] **Sharp pixels** - Not blurry or anti-aliased

### ✅ Animation
- [ ] **Walk works** - Character animates when moving
- [ ] **4 directions** - Down, Up, Left, Right all work
- [ ] **Smooth motion** - No jittering or stuttering
- [ ] **Correct speed** - Matches NPC movement speed

### ✅ In-Game Appearance
- [ ] **Stands on ground** - Feet align with platform
- [ ] **Depth sorting** - Correctly overlaps NPCs
- [ ] **Fits aesthetic** - Matches Chrono Trigger style
- [ ] **Readable** - Can identify character features

---

## Available NFT Sprites

All 24 NFT character sprites available for testing:

### Set 1
- `set1-char1` - Purple/dark character
- `set1-char2` - Brown/tan character
- `set1-char3` - Orange fire character
- `set1-char4` - Blue glowing character
- `set1-char5` - Gray/stone character
- `set1-char6` - Purple/blue character

### Set 2
- `set2-char1` - Purple/dark character
- `set2-char2` - **Blue character** (default test)
- `set2-char3` - Cyan/aqua character
- `set2-char4` - Red/orange character
- `set2-char5` - Yellow/gold character
- `set2-char6` - Brown character

### Set 3
- `set3-char1` - Brown character
- `set3-char2` - Brown/red character
- `set3-char3` - Tan character
- `set3-char4` - Purple/dark character
- `set3-char5` - Blue/cyan character
- `set3-char6` - Brown/tan character

### Set 4
- `set4-char1` - Red/orange character
- `set4-char2` - Purple character
- `set4-char3` - White/gray character (skeleton?)
- `set4-char4` - Gray character
- `set4-char5` - Dark/blue character
- `set4-char6` - Purple/blue character

---

## Testing Different Sprites

### Test One at a Time
```bash
# Test sprite, check in browser, take notes
./test-nft-sprite.sh set1-char1
# Open browser, test movement, check visuals

# Test another
./test-nft-sprite.sh set1-char2
# Refresh browser, test again

# Continue for all 24...
```

### Test All Systematically
```bash
# Create a test log
touch nft-sprite-test-results.txt

# Test each set
for set in set1 set2 set3 set4; do
  for char in char1 char2 char3 char4 char5 char6; do
    echo "Testing ${set}-${char}..."
    ./test-nft-sprite.sh ${set}-${char}
    echo ""
    echo "Check browser, then press Enter to continue..."
    read
    echo "${set}-${char}: [YOUR NOTES HERE]" >> nft-sprite-test-results.txt
  done
done
```

---

## What Test Mode Does

### 1. **Swaps Game Scene**
Changes `config-iso.ts` to use `IsoGame-NFT-TEST.ts` instead of normal `IsoGame.ts`

### 2. **Loads NFT Sprite**
Adds preload:
```typescript
this.load.spritesheet(TEST_NFT_SPRITE, path, {
  frameWidth: 32,
  frameHeight: 48
});
```

### 3. **Creates NFT Animations**
Generates walk animations for the NFT sprite:
- Right (frames 0-3)
- Left (frames 4-7)
- Up (frames 8-11)
- Down (frames 12-15)

### 4. **Uses NFT as Player**
```typescript
this.player = this.physics.add.sprite(640, 360, TEST_NFT_SPRITE, 12);
this.player.setScale(1.5);
this.player.setData('isNFT', true);
```

### 5. **Shows Debug Info**
Top-left shows:
```
🧪 NFT TEST: set2-char2
FPS: 60
Position: 640, 360 [L0]
```

---

## Known Issues to Look For

### ❌ Background Not Transparent
**Symptom:** Sprite has beige/tan box around it
**Cause:** Background wasn't removed from sprite sheet
**Fix:** Need to re-process sprite with transparency

### ❌ Sprite Too Large/Small
**Symptom:** Character is giant or tiny compared to NPCs
**Cause:** Scale is wrong (should be 1.5)
**Fix:** Check test file uses `setScale(1.5)`

### ❌ Animation Not Working
**Symptom:** Character slides without walking animation
**Cause:** AnimationController not detecting NFT sprite
**Fix:** Check `isNFT` flag is set correctly

### ❌ Sprite Invisible
**Symptom:** Can't see character at all
**Cause:** Sprite failed to load (404 or wrong path)
**Fix:** Check console for load errors

### ❌ Wrong Alignment
**Symptom:** Character floating or feet below ground
**Cause:** Origin point incorrect
**Fix:** Should be `setOrigin(0.5, 0.85)` for feet

---

## Comparison to Warrior Sprite

### Warrior (Current)
- **Size:** 1.5x scale
- **Source:** Individual PNG files per frame
- **Animations:** 8 directions × 4 frames = 32 files
- **Background:** Transparent
- **Style:** Chrono Trigger inspired

### NFT Sprites
- **Size:** Should be 1.5x scale (same as warrior)
- **Source:** Single sprite sheet per character
- **Animations:** 4 directions × 4 frames = 16 frames total
- **Background:** May need transparency processing
- **Style:** 3D rendered, converted to pixel art

---

## Recording Test Results

Create a simple table:

```
Sprite      | Renders | Size | Transparency | Animation | Notes
------------|---------|------|--------------|-----------|-------
set1-char1  | ✅      | ✅   | ❌           | ✅        | Has tan background
set1-char2  | ✅      | ✅   | ✅           | ✅        | Looks great!
set1-char3  | ✅      | ⚠️   | ✅           | ✅        | Slightly large
...
```

---

## After Testing

### If Sprites Look Good
```bash
# Keep test results
mv nft-sprite-test-results.txt NFT-SPRITE-APPROVED.txt

# Restore normal mode
./restore-normal-mode.sh

# Now ready to implement character selection
```

### If Sprites Need Fixes
```bash
# Document issues
cat > NFT-SPRITE-ISSUES.txt << EOF
Issue 1: All sprites have background artifacts
  - Need to re-process with transparency
  - Use flood-fill algorithm from corners

Issue 2: Set 3 sprites too large
  - May need different scale value

Issue 3: Animations jerky on set4-char2
  - Check frame alignment
EOF

# Restore normal mode
./restore-normal-mode.sh

# Fix sprites, then test again
```

---

## Quick Reference Commands

```bash
# Test a sprite
./test-nft-sprite.sh set2-char2

# Test all sprites in set 1
for i in {1..6}; do ./test-nft-sprite.sh set1-char$i; sleep 10; done

# Restore normal
./restore-normal-mode.sh

# Check what's currently testing
grep "TEST_NFT_SPRITE =" scripts/client/scenes/IsoGame-NFT-TEST.ts

# View test scene code
cat scripts/client/scenes/IsoGame-NFT-TEST.ts

# Check if in test mode
[ -f "scripts/client/config-iso.ts.backup" ] && echo "TEST MODE" || echo "NORMAL MODE"
```

---

## Browser Testing Tips

1. **Hard Refresh**: Ctrl+Shift+R or Cmd+Shift+R to bypass cache
2. **Open DevTools**: F12 → Console to see load errors
3. **Check Network Tab**: See if sprite loaded (200 vs 404)
4. **Take Screenshots**: Document what each sprite looks like
5. **Test Movement**: Walk in all 4 directions, check smoothness

---

## Next Steps After Testing

Once you've verified sprites look good:

1. ✅ **All 24 sprites tested** - Know which work, which need fixes
2. ✅ **Size confirmed** - All at correct scale (1.5x)
3. ✅ **Transparency verified** - No background artifacts
4. ✅ **Animations smooth** - Walk cycles work properly
5. → **Build character selection** - Add CharacterSelect scene
6. → **Deploy** - Make NFT characters available to players

---

**Bottom line:** Test sprites individually in actual gameplay before building selection UI. Catch visual issues early!
