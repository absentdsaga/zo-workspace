# Workflow Freeze Contract

**DO NOT proceed to API integration until this contract is satisfied.**

## Current Status

- [x] Freeze test script created (`freeze_workflow_test.py`)
- [ ] 3/3 smoke prompts pass artifact checks
- [ ] Workflow locked (`workflow_locked_v1.json`)
- [ ] API integration implemented
- [ ] Deterministic seed strategy added
- [ ] Angle consistency QC gate added

## Smoke Test Requirements

### Test Prompts
1. **hero_orange idle** (seed: 1001)
2. **npc_bear walk_contact** (seed: 2001)
3. **npc_raccoon attack_impact** (seed: 3001)

### Zero-Tolerance Acceptance Criteria

Each frame MUST satisfy ALL checks:

#### ✅ No Background Card/Box
- **Check**: Edge region sampling (top/bottom/left/right)
- **Threshold**: <30% of edge samples opaque
- **Failure mode**: Rectangular frame/poster/card artifact

#### ✅ Feet Visible
- **Check**: Bottom 15% of canvas has character pixels
- **Threshold**: ≥100 visible pixels in bottom region
- **Failure mode**: Cropped feet, floating character

#### ✅ Consistent 3/4 Angle
- **Check**: Manual visual inspection (automated in next phase)
- **Threshold**: Character facing locked 3/4 direction
- **Failure mode**: Angle drift, flat frontal view

#### ✅ Silhouette Readable
- **Check**: Center region has character content
- **Threshold**: ≥1000 pixels in center 40% region
- **Failure mode**: Empty canvas, off-center character

#### ✅ Transparency
- **Check**: Background transparency present
- **Threshold**: At least some transparent pixels detected
- **Failure mode**: Solid background, failed cutout

## How to Run

```bash
# From assets-pipeline directory
cd /home/workspace/Skills/spatial-worlds/assets-pipeline

# Ensure ComfyUI is running on localhost:8188
# Then run freeze test:
python3 freeze_workflow_test.py
```

## Expected Output

### ✅ Success (Ready for API Integration)
```
============================================================
WORKFLOW FREEZE TEST - 3 SMOKE PROMPTS
============================================================

🔧 Testing: hero_orange_idle
   Seed: 1001
   ✓ Prompt queued: abc123
   ✓ Downloaded: hero_orange_idle.png
   🔍 Running artifact checks...
   ✓ PASS

🔧 Testing: npc_bear_walk_contact
   Seed: 2001
   ✓ Prompt queued: def456
   ✓ Downloaded: npc_bear_walk_contact.png
   🔍 Running artifact checks...
   ✓ PASS

🔧 Testing: npc_raccoon_attack_impact
   Seed: 3001
   ✓ Prompt queued: ghi789
   ✓ Downloaded: npc_raccoon_attack_impact.png
   🔍 Running artifact checks...
   ✓ PASS

============================================================
FREEZE TEST SUMMARY
============================================================
Passed: 3/3
Failed: 0/3
Errors: 0/3

✅ WORKFLOW LOCKED - Ready for API integration
   Saved to: comfy/workflow_locked_v1.json
```

### ❌ Failure (Tune Workflow)
```
   ✗ FAIL
      - Edge artifacts detected: 15/28 edge samples opaque (likely frame/card)
      - Feet likely cropped: only 42 visible pixels in bottom 15%

============================================================
FREEZE TEST SUMMARY
============================================================
Passed: 0/3
Failed: 3/3
Errors: 0/3

❌ WORKFLOW NOT READY - Fix artifacts before proceeding

Next steps:
1. Review failed outputs in test_freeze_output/
2. Adjust workflow parameters (denoise, negative prompt, etc.)
3. Re-run this test until 3/3 pass
4. Only then integrate API calls into batch_orchestrator.py
```

## What Happens After Lock

Once 3/3 tests pass:

1. **Locked workflow saved** → `comfy/workflow_locked_v1.json`
2. **Proceed to Step 2** → Implement full API integration in `batch_orchestrator.py`
3. **Add deterministic seeds** → Base seed + character hash + state offset + frame index
4. **Add angle consistency gate** → QC check #7
5. **Run 20-frame pilot** → hero idle(8) + walk(4), npc_bear idle(4), npc_raccoon idle(4)

## Red Flags That Block Lock

- **Any rectangular artifact** → Reject before normalization
- **Feet baseline drift** → Fix with frame recentering rules
- **Palette explosion** → Enforce FX layer or separate VFX sprites
- **Camera angle inconsistency** → Sprite illusion breaks in gameplay

## Contract Enforcement

**This is not a suggestion. This is a hard gate.**

If the freeze test doesn't pass 3/3, the workflow is not production-ready. 

Automate bad outputs faster = waste time and credits on unusable frames.

Lock the workflow first. Scale second.
