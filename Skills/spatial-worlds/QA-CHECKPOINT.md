# QA Checkpoint - Character Selection Feature

## Automated Tests Required Before Claiming "Done"

### 1. Visual Rendering Test
- [ ] Character selection screen displays all 24 NFT sprites
- [ ] No "Failed to load sprite" errors in console
- [ ] Characters are clickable and selectable
- [ ] START GAME button enables after selection

### 2. Game Rendering Test
- [ ] Selected character renders in game (not colored blocks)
- [ ] Character is clearly visible (scale >= 3.0)
- [ ] Character has proper animations
- [ ] Screenshot proof saved

### 3. Console Error Check
- [ ] No texture loading errors
- [ ] No animation creation errors
- [ ] Scene transitions work (CharacterSelect → IsoGameScene)
- [ ] No JavaScript errors

### 4. Multiplayer Integration
- [ ] Multiplayer connection works with NFT character
- [ ] Other players can see your NFT character
- [ ] Voice chat initializes

## Test Script

Run: `bun run test-character-select.ts`

Expected output:
```
✅ No sprite loading errors visible
✅ Selected character: set2-char1
✅ Texture verified: set2-char1
✅ Player sprite created
✅ Game screen has content
```

## Screenshot Evidence

Must capture:
1. Character selection screen showing all 24 characters
2. Game screen with NFT character clearly visible (NOT tiny colored blocks)

Screenshots saved to: `test-screenshots/`

## Failure Criteria

❌ FAIL if:
- Character renders as colored blocks instead of sprite
- Character is too small to see clearly (< 100px)
- Console shows texture/loading errors
- Screenshot shows blank or broken game screen

## Why This Matters

Without visual verification, we ship broken features that look "working" in logs but are unusable to players. Always verify visually before claiming success.
