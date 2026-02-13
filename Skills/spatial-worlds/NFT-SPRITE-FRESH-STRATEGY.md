# NFT Sprite Integration - Fresh Strategy

**Date:** 2026-02-13
**Status:** Starting fresh after issues with previous approach
**Git Baseline:** commit 9fccd67 (clean working tree)

---

## What We Have: Working Foundation ✅

### Core Game (100% Working)
- Isometric multiplayer world with 8-direction movement
- WebSocket real-time sync (100+ players)
- Proximity voice chat (Daily.co integration)
- Beautiful FFT-style tiles with elevation
- Smooth camera, depth sorting, mobile controls
- FPS: 48-60, zero console errors
- **Currently uses:** Simple warrior sprite (works perfectly)

### NFT Assets Available
- **24 character sprites** in `/assets/sprites/nft-characters/`
- Organized as: `set1-char1` through `set4-char6`
- Each has a sprite sheet: `{name}-sheet.png`
- Frame layout: 4 directions × 4 frames = 16 frames
- Layout: [right-0,1,2,3, left-0,1,2,3, up-0,1,2,3, down-0,1,2,3]

---

## What Went Wrong Before ❌

### Previous Approach Issues
1. **Transparency Processing** - ImageMagick background removal was inconsistent
2. **Frame Alignment** - Sprite sheets had alignment issues
3. **Aesthetic Mismatch** - 3D-rendered sprites didn't match Chrono Trigger style
4. **Complex Integration** - Tried to build character selection before verifying sprites worked
5. **Iteration Degradation** - Made multiple changes without testing each one

### The Core Problem
We tried to integrate the sprites BEFORE verifying they looked good in-game. Built complex systems on top of broken foundations.

---

## Fresh Strategy: Test-First Approach ✅

### Phase 1: Single Sprite Verification (2 hours)
**Goal:** Get ONE NFT sprite working perfectly before building anything else

#### Step 1.1: Visual Inspection
- Pick one character (e.g., `set2-char2`)
- Open the sprite sheet in image viewer
- Document: dimensions, frame layout, background color, quality

#### Step 1.2: Basic Integration Test
- Create minimal test scene that loads just this one sprite
- No character selection, no complex systems
- Just: load sprite → create player → move around → verify it looks good

#### Step 1.3: Fix Issues One at a Time
For the single test sprite:
- [ ] Transparency (remove background if needed)
- [ ] Frame alignment (verify animations don't jitter)
- [ ] Scale (find the right size that looks good)
- [ ] Animation timing (frames per second)
- [ ] Visual quality (does it fit the aesthetic?)

**Success Criteria:** One sprite looks GREAT in-game, animations smooth, no visual issues

---

### Phase 2: Process Remaining Sprites (1-2 hours)
**Goal:** Apply working formula to all 24 characters

#### Step 2.1: Create Processing Script
- Extract the exact steps that worked for sprite #1
- Automate: transparency, scaling, frame extraction
- Run on all 24 sprite sheets

#### Step 2.2: Batch Verification
- Test each sprite individually (using test scene from Phase 1)
- Document which ones work, which need manual fixes
- Fix outliers by hand

**Success Criteria:** All 24 sprites verified working in-game

---

### Phase 3: Character Selection UI (2 hours)
**Goal:** Let players choose their character

#### Step 3.1: Simple Grid Selection
- Create `CharacterSelect` scene
- Show 24 sprites in 6×4 grid
- Click to select → save choice → start game

#### Step 3.2: Polish
- Add hover effects
- Show character name
- Preview animation on hover

**Success Criteria:** Players can pick a character and play with it

---

### Phase 4: Integration & Testing (1 hour)
**Goal:** Ensure multiplayer works with mixed characters

#### Step 4.1: Multiplayer Sync
- Update `MultiplayerManager` to sync character choice
- Test: 3 browsers, different characters, verify they see each other correctly

#### Step 4.2: Edge Cases
- Test: player joins mid-game with different character
- Test: same character chosen by multiple players
- Test: all 24 characters on screen at once

**Success Criteria:** Multiplayer works flawlessly with any character mix

---

## Testing Infrastructure

### Test Files to Create
1. `test-single-sprite.html` - Load one sprite, no game logic
2. `extract-sprite-info.js` - Analyze sprite sheet dimensions/frames
3. `verify-transparency.js` - Check for background artifacts
4. `batch-process-sprites.sh` - Apply fixes to all sprites

### Verification Checklist (Per Sprite)
- [ ] Sprite loads without 404
- [ ] No console errors
- [ ] Transparent background (no colored boxes)
- [ ] Correct size (not too big/small)
- [ ] Animations smooth (4 frames × 4 directions)
- [ ] Feet aligned with ground
- [ ] Matches Chrono Trigger aesthetic
- [ ] Readable at game scale

---

## Key Principles

### 1. Test BEFORE Building
- Verify sprites work → THEN build character selection
- Don't build on broken foundations

### 2. One Change at a Time
- Fix transparency → test
- Fix scale → test
- Fix alignment → test
- Never change 3 things and hope it works

### 3. Visual Verification
- Use screenshots, not just code inspection
- If it looks wrong, it IS wrong
- Trust your eyes over your assumptions

### 4. Incremental Integration
- ONE sprite working → THEN all sprites → THEN selection UI
- Each phase builds on verified previous phase

### 5. Rollback Points
- Git commit after each working phase
- Can always revert to last known good state

---

## Success Metrics

### Phase 1 Success
- Single sprite renders beautifully
- No transparency issues
- Animations smooth in all 4 directions
- Looks great standing still and moving

### Phase 2 Success
- All 24 sprites verified
- Consistent quality across all characters
- No visual artifacts or alignment issues

### Phase 3 Success
- Character selection UI feels smooth
- Easy to preview and choose
- Selected character appears correctly in game

### Phase 4 Success
- Multiplayer with mixed characters works perfectly
- No sprite sync issues
- Game feels polished and complete

---

## Next Steps

1. **Start Phase 1** - Pick one sprite, get it working perfectly
2. **Document** - Write down exact steps that worked
3. **Automate** - Turn manual steps into scripts
4. **Scale** - Apply to all 24 sprites
5. **Ship** - Deploy with character selection

---

**Bottom Line:** Don't rush. Get ONE sprite perfect, then replicate that perfection 24 times. Build character selection last, on a solid foundation.
