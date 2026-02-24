# Manual Workflow Freeze (CPU Alternative)

**Context**: ComfyUI is running on CPU, making automated freeze test very slow (10-30min per image).

## Alternative Approach: Manual UI Validation

Instead of waiting for `freeze_workflow_test.py`, validate the workflow manually in ComfyUI UI first.

### Step 1: Open ComfyUI

Visit: http://localhost:8188

### Step 2: Load Base Workflow

Load `comfy/workflow_character_base.json` in the UI.

### Step 3: Test These 3 Prompts Manually

For each prompt, adjust the positive/negative text nodes and generate:

#### Prompt 1: hero_orange idle
**Positive:**
```
isometric 3/4 tactical RPG character sprite, orange hero character, neutral idle pose, weight balanced, readable silhouette, single character only, clean pixel-art readability, limited palette, crisp silhouette, feet fully visible, grounded stance, transparent background, no environment, no frame, no card, no text, no watermark
```

**Negative:**
```
rectangular frame, border, poster, card, background scene, floor texture, painterly smear, noisy texture, blurry edges, extra limbs, cropped feet, cut-off weapon, watermark, text, logo
```

**Seed:** 1001

#### Prompt 2: npc_bear walk_contact
**Positive:**
```
isometric 3/4 tactical RPG character sprite, brown bear character, walk cycle contact pose, one foot forward one back, single character only, clean pixel-art readability, limited palette, crisp silhouette, feet fully visible, grounded stance, transparent background, no environment, no frame, no card, no text, no watermark
```

**Negative:** (same as above)

**Seed:** 2001

#### Prompt 3: npc_raccoon attack_impact
**Positive:**
```
isometric 3/4 tactical RPG character sprite, raccoon character, attack impact pose, clear forward action line, single character only, clean pixel-art readability, limited palette, crisp silhouette, feet fully visible, grounded stance, transparent background, no environment, no frame, no card, no text, no watermark
```

**Negative:** (same as above)

**Seed:** 3001

### Step 4: Visual Inspection Checklist

For each generated image, manually check:

- [ ] ✅ **No box/frame artifacts** - edges are transparent, no rectangular border
- [ ] ✅ **Feet visible** - character's feet/bottom visible, not cropped
- [ ] ✅ **3/4 angle consistent** - character facing same direction (not flat front/side)
- [ ] ✅ **Silhouette readable** - clear character shape against transparent background
- [ ] ✅ **Transparent background** - no solid color behind character

### Step 5: If All 3 Pass

1. Export the workflow JSON from ComfyUI UI
2. Save it as `comfy/workflow_locked_v1.json`
3. Proceed to Step 2 (API integration)

### Step 6: If Any Fail

Common fixes:

**Box/frame artifacts:**
- Add to negative: "square border, rectangular frame, UI element, panel, card background"
- Increase negative prompt weight (CFG)

**Cropped feet:**
- Add to positive: "full body, complete character, feet touching ground"
- Adjust canvas size or composition

**Angle drift:**
- Add to positive: "isometric three-quarter view, 45 degree angle"
- Lock specific viewing angle in positive

**Background not transparent:**
- Check if output node is saving with alpha channel
- May need background removal node

## Quick GPU Alternative

If you have access to a GPU instance or cloud service:

1. Copy `freeze_workflow_test.py` to GPU machine
2. Install ComfyUI with GPU support
3. Run the automated test (will complete in ~5-10 minutes)

## Current Status

The automated freeze test is **running in background on CPU** but will take hours.

You can either:
- ✅ **Wait for CPU test** - check back in 2-3 hours
- ✅ **Manual UI validation** - faster, validates visually
- ✅ **Skip to API integration** - assume workflow is good, fix issues during pilot batch

Recommended: **Manual UI validation** for speed, then run automated test overnight as verification.
