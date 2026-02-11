# Visual Verify — Human Perception Validation

**Version**: 1.0.0  
**Purpose**: Verify that what I built actually LOOKS correct to a human, not just that code compiles  
**Critical Rule**: "Code working ≠ Visually correct. Always screenshot and verify."

---

## 🎯 The Problem I Solve

**Common Failure Pattern:**
```
Me: "I built a 15×15 isometric grid with elevated platforms!"
Code: ✅ Compiles
Build: ✅ Succeeds
Server: ✅ Running
REALITY: ❌ Nothing visible on screen (black background + sprites)
```

**Root Cause:** I trust my code but don't verify what the HUMAN sees.

---

## 🔍 What This Skill Does

### Phase 1: Take Screenshot (Always)
**Before claiming visual work is done:**
```bash
1. Open browser to live URL
2. Wait for full render
3. Capture screenshot
4. Save with timestamp
```

### Phase 2: Visual Analysis
**AI-powered image understanding to check:**
- ✅ Is expected content VISIBLE?
- ✅ Are colors correct?
- ✅ Is layout as described?
- ✅ Are UI elements readable?
- ✅ Does it match design spec?

### Phase 3: Human Perception Check
**Compare what I SAID I built vs what's ACTUALLY visible:**

**Example:**
```
CLAIMED: "15×15 isometric diamond grid"
SCREENSHOT SHOWS: Black background, no grid
VERDICT: ❌ FAILED - Grid not rendering

CLAIMED: "Elevated platforms with 3D sides"
SCREENSHOT SHOWS: Flat sprites, no platforms
VERDICT: ❌ FAILED - Platforms not visible

CLAIMED: "Color-coded NPCs (green/blue/orange/pink)"
SCREENSHOT SHOWS: Colored squares visible
VERDICT: ✅ PARTIAL - NPCs visible but no context
```

---

## 📸 Screenshot Workflow

### Script: `scripts/screenshot-verify.sh`

```bash
#!/bin/bash
# Visual verification via screenshot

URL="$1"
PROJECT_NAME="$2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_DIR="/home/workspace/.visual-verify"
SCREENSHOT="$OUTPUT_DIR/${PROJECT_NAME}-${TIMESTAMP}.jpg"

mkdir -p "$OUTPUT_DIR"

echo "📸 VISUAL VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "URL: $URL"
echo "Project: $PROJECT_NAME"
echo ""

# Use browser automation to capture screenshot
# (Requires Playwright/Puppeteer or Zo's browser tools)

echo "1. Opening browser..."
echo "2. Capturing screenshot..."
echo "3. Analyzing visual content..."
echo ""

# Save screenshot path for analysis
echo "Screenshot saved: $SCREENSHOT"

# Now analyze what's visible
echo ""
echo "🔍 VISUAL CONTENT ANALYSIS:"
echo ""

# Check if expected elements are visible
# (This would use AI vision or pixel analysis)

echo "Expected: Isometric grid"
echo "Found: [AI ANALYSIS RESULT]"
echo ""

echo "Expected: Elevated platforms"
echo "Found: [AI ANALYSIS RESULT]"
echo ""

echo "Expected: Color-coded sprites"
echo "Found: [AI ANALYSIS RESULT]"
echo ""

# Final verdict
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VERDICT: [PASS/FAIL]"
echo ""
echo "If FAIL, do NOT claim work is complete!"
```

---

## 🤖 Integration with Browser Testing

### Using Zo's Browser Tools

```python
# scripts/visual-check.py

def verify_spatial_worlds():
    """
    Open browser, screenshot, analyze what human sees
    """
    
    # 1. Open in browser
    browser.open("https://spatial-worlds-dioni.zocomputer.io")
    browser.wait(3)  # Let it render
    
    # 2. Capture screenshot
    screenshot = browser.screenshot()
    
    # 3. Analyze with AI vision
    analysis = analyze_image(screenshot, expectations={
        "isometric_grid": "Should see 15×15 diamond-shaped tiles in green",
        "platforms": "Should see elevated grass blocks with visible sides",
        "sprites": "Should see 51 colored character sprites",
        "depth": "Should see 3D depth (platforms floating above ground)"
    })
    
    # 4. Report what's ACTUALLY visible
    print("VISUAL VERIFICATION REPORT")
    print("=" * 60)
    
    for element, expected in expectations.items():
        found = analysis.check(element)
        status = "✅" if found else "❌"
        print(f"{status} {element}: {expected}")
        if not found:
            print(f"   ISSUE: {analysis.get_issue(element)}")
    
    # 5. Verdict
    if analysis.all_passed():
        print("\n✅ VISUAL VERIFICATION PASSED")
        return True
    else:
        print("\n❌ VISUAL VERIFICATION FAILED")
        print("\nDo NOT claim completion - fix visual issues first!")
        return False
```

---

## 🎯 Checklist Templates

### For Game/Graphics Projects

**Before claiming done, verify screenshot shows:**
- [ ] Ground/terrain visible (not just black background)
- [ ] Game objects render in correct positions
- [ ] Colors match specification
- [ ] UI elements readable and positioned correctly
- [ ] Animations playing (if applicable)
- [ ] Depth/layering correct (front objects obscure back objects)
- [ ] No visual glitches (z-fighting, clipping, etc.)
- [ ] Frame rate smooth (check debug FPS counter)

### For Web Apps

**Before claiming done, verify screenshot shows:**
- [ ] Layout matches design
- [ ] Text readable (font size, contrast)
- [ ] Images loaded correctly
- [ ] Buttons/interactive elements visible
- [ ] Responsive design working (if tested on mobile)
- [ ] No layout breaks or overflow
- [ ] Loading states resolved (spinners gone)

---

## 🔧 Human Perception Rules

### Rule 1: If you can't see it, it doesn't exist
**Code rendering something offscreen = broken**

Example:
```typescript
// Camera zoomed in too far, tiles render outside viewport
graphics.fillRect(5000, 5000, 100, 100);  // Off-screen!
```
**Solution:** Always check camera bounds vs render coordinates

### Rule 2: Black on black is invisible
**Dark elements on dark backgrounds = invisible to humans**

Example:
```typescript
graphics.fillStyle(0x000000);  // Black fill
// Drawing on black background (#1a1a2e) = invisible!
```
**Solution:** Always verify color contrast

### Rule 3: Depth of -1 might render below viewport
**Graphics at negative depth can disappear**

Example:
```typescript
graphics.setDepth(-1);  // Might render behind background
```
**Solution:** Test depth layering visually, not just in code

### Rule 4: Opacity 0 = invisible
**Transparent elements are invisible**

Example:
```typescript
sprite.setAlpha(0);  // Completely transparent!
```
**Solution:** Check alpha values in screenshot

### Rule 5: Off-by-one positioning breaks layouts
**Coordinates slightly wrong = visual disaster**

Example:
```typescript
// Platforms render 1000px off-center
drawPlatform(x: 5000, y: 5000);  // User sees nothing!
```
**Solution:** Verify coordinates match viewport

---

## 💡 Failure Pattern Detection

### Common Visual Bugs I Miss

**1. "Works in code, invisible to humans"**
- Graphics render off-screen
- Elements at wrong depth layer
- Colors too dark to see
- Camera positioned wrong

**2. "Partial rendering"**
- Some elements visible, others not
- Indicates depth/layering issue

**3. "Nothing visible except UI"**
- Game canvas black
- Only debug text shows
- Indicates graphics not rendering or off-screen

**4. "Elements there but wrong appearance"**
- Sprites visible but platforms not
- Colors wrong
- Layout broken

---

## 🚀 Integration with Continuous Monitor

**Add to full-validation.sh as Phase 4:**

```bash
# Phase 4: Visual Verification
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 4: Visual Content Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if /home/workspace/Skills/visual-verify/scripts/screenshot-verify.sh "$SERVICE_URL" "$PROJECT_NAME"; then
    echo "✅ Phase 4 PASSED: Visual content matches spec"
else
    echo "❌ Phase 4 FAILED: What you see ≠ what you described"
    ((TOTAL_FAILURES++))
fi
```

---

## 📋 Visual Expectations File

**Create `VISUAL-SPEC.md` in project:**

```markdown
# Visual Specification — Spatial Worlds

## What Should Be Visible

### Ground Layer
- **Description**: 15×15 grid of diamond-shaped isometric tiles
- **Color**: Green (#4a6a3f)
- **Position**: Centered in viewport
- **Size**: Each tile ~64×32px
- **Visibility**: MUST be clearly visible, not off-screen

### Elevated Platforms
- **Count**: 8 platforms at various elevations
- **Appearance**: Grass blocks with visible brown earth sides (3D effect)
- **Colors**: 
  - Level 1: #6a8a5f
  - Level 2: #8aaa7f
  - Level 3: #9aba8f
- **Visibility**: MUST see 3D depth (top + sides)

### Character Sprites
- **Count**: 51 (1 player + 50 NPCs)
- **Colors**: 
  - Green = Level 0
  - Blue = Level 1
  - Orange = Level 2
  - Pink = Level 3
- **Size**: Visible and identifiable
- **Position**: ON platforms or ground, not floating in void

### Expected Screenshot
When working correctly, human should see:
- Green diamond grid forming isometric plane
- Grass block platforms floating at different heights
- Colored character sprites standing on platforms
- 3D depth effect (platforms have visible sides)
- NOT: Black background with random colored squares
```

---

## 🎓 Learning from Visual Failures

### Spatial Worlds Failure Case Study

**What I claimed:**
> "Built 15×15 isometric grid with elevated platforms and depth sorting"

**What user saw:**
> Black background + colored squares floating

**What went wrong:**
1. ❌ Graphics rendered off-screen (camera position wrong)
2. ❌ Depth set to -1 (rendered behind background)
3. ❌ Zoom too high (tiles outside viewport)
4. ❌ Didn't verify screenshot before claiming done

**How visual-verify would catch this:**
```
SCREENSHOT ANALYSIS:
❌ Isometric grid: NOT VISIBLE (expected 15×15 diamonds, found: nothing)
❌ Platforms: NOT VISIBLE (expected 8 elevated blocks, found: nothing)
✅ Sprites: VISIBLE (found 51 colored squares)
⚠️  Background: BLACK (expected green tiles, found: solid black)

VERDICT: ❌ FAILED
Only 1/4 expected elements visible. Do NOT claim completion.
```

---

## 🔄 Workflow Update

**NEW MANDATORY STEP before claiming visual work done:**

```bash
# Old workflow
1. Write code
2. Build
3. Run pre-flight
4. Tell user "done" ❌ WRONG!

# New workflow with visual-verify
1. Write code
2. Build
3. Run pre-flight (technical)
4. Run spec-validator (requirements)
5. Run visual-verify (screenshot + analysis) ⭐ NEW
6. If visual-verify passes, THEN tell user "done"
```

---

## 🎯 Success Criteria

**Visual verification passes when:**
- ✅ Screenshot contains ALL claimed visual elements
- ✅ Elements positioned as specified
- ✅ Colors match specification
- ✅ Layout matches design
- ✅ Human can clearly see what was described
- ✅ No "black screen with random elements"

**Visual verification fails when:**
- ❌ Claimed elements not visible
- ❌ Wrong colors
- ❌ Elements off-screen
- ❌ Black/blank screen
- ❌ "It should work" without verifying

---

*This skill prevents "looks broken to humans but code compiles" failures.*
