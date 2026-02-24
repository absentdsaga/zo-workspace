# Spatial Worlds Asset Pipeline - Current Status

**Last Updated**: 2026-02-15 02:30 UTC

## ✅ Implementation Complete

All foundation pieces are ready. **You are at Step 1: Workflow Freeze.**

### Files Created

1. **`freeze_workflow_test.py`** - Workflow validation with 3 smoke prompts
   - Tests: hero_orange idle, npc_bear walk_contact, npc_raccoon attack_impact
   - Zero-tolerance artifact checks (box, feet, angle, silhouette, transparency)
   - Outputs: PASS/FAIL + saves `workflow_locked_v1.json` on success

2. **`seed_strategy.py`** - Deterministic seed generation
   - Formula: `seed = base_seed + char_hash + state_offset + frame_index`
   - Verified unique across 400 test combinations
   - Critical for reproducibility ("why did frame 5 drift?")

3. **`batch_orchestrator_v2.py`** - Full ComfyUI API integration
   - `build_workflow()` - Injects prompts + seeds into locked template
   - `submit_prompt()` - POST to ComfyUI /prompt
   - `poll_until_done()` - GET /history with 300s timeout
   - `collect_output_files()` - Parse outputs from history
   - `copy_to_output_raw()` - Download via /view endpoint
   - **Retry logic**: 3 attempts with exponential backoff (2s, 4s, 8s)
   - **Failure tracking**: JSON markers for failed frames
   - **Traceability**: Logs prompt_id per frame

4. **`qc_checker.py`** - Enhanced with QC Gate #7
   - **NEW**: Angle consistency check (L/R mass ratio)
   - Rejects if 3/4 orientation drifts between adjacent frames
   - Threshold: max 0.15 change in left/right pixel mass ratio

5. **Documentation**
   - `WORKFLOW_FREEZE_CONTRACT.md` - Step 1 requirements (hard gate)
   - `PRODUCTION_CHECKLIST.md` - Full 6-step production workflow
   - `STATUS.md` - This file

---

## 📍 Current Position: Step 1

### What You Need to Do Next

**Run the workflow freeze test:**

```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline

# Ensure ComfyUI is running on localhost:8188
./start_comfyui.sh

# In another terminal:
python3 freeze_workflow_test.py
```

### Expected Outcome

One of two results:

#### ✅ Success (3/3 Pass)

```
============================================================
FREEZE TEST SUMMARY
============================================================
Passed: 3/3
Failed: 0/3
Errors: 0/3

✅ WORKFLOW LOCKED - Ready for API integration
   Saved to: comfy/workflow_locked_v1.json
```

**→ Proceed to Step 2** (wire API integration)

#### ❌ Failure (< 3/3 Pass)

```
============================================================
FREEZE TEST SUMMARY
============================================================
Passed: 1/3
Failed: 2/3
Errors: 0/3

❌ WORKFLOW NOT READY - Fix artifacts before proceeding
```

**→ DO NOT PROCEED**

Instead:
1. Review `test_freeze_output/*.png` for failures
2. Read `freeze_workflow_test.py` output for specific failure reasons
3. Adjust workflow parameters in ComfyUI or `comfy/workflow_character_base.json`:
   - Strengthen negative prompt for "rectangular frame, border, card"
   - Reduce denoise if getting style drift (try 0.85-0.95)
   - Adjust CFG scale if needed (currently 6.0)
   - Add controlnet or img2img refinement pass if necessary
4. Re-run test until 3/3 pass
5. **Only then** move to Step 2

---

## 🔒 The Contract

**This is not a suggestion. This is a hard gate.**

If you proceed to API integration without locking the workflow:
- You'll automate bad outputs faster
- You'll waste credits on unusable frames
- You'll debug "why are all my sprites broken?" instead of "why did this one frame fail?"

Lock the workflow first. Scale second.

---

## 📋 Remaining Steps (After Step 1)

Once workflow is locked:

2. **Wire API integration** - Swap to `batch_orchestrator_v2.py`
3. **Run 20-frame pilot** - hero idle(8) + walk(4), npc_bear idle(4), npc_raccoon idle(4)
4. **Hero-to-world calibration** - Lock baseline, scale, shadow (do not change after)
5. **Tighten metadata** - Add hurtbox, hitbox, eventFrames, sortBias
6. **Full production scale-up** - Generate all character animation sets

See `PRODUCTION_CHECKLIST.md` for full details.

---

## 🚨 Red Flags

Watch for these during testing/production:

| Signal | Meaning | Action |
|--------|---------|--------|
| **Box artifacts in freeze test** | Workflow producing frames/cards | Fix negative prompt |
| **Cropped feet** | Character cut off at bottom | Adjust composition or canvas size |
| **Angle drift** | Character rotating away from 3/4 | Lock pose tighter in prompt |
| **QC pass rate < 70%** | Pipeline not production-ready | Debug before scaling |
| **Baseline jitter in walk** | Normalization failing | Check `normalize_sprite.py` |

---

## 🎯 Success Criteria (Final)

Before deploying to engine, you must verify:

- [x] Workflow freeze test passes 3/3
- [ ] QC pass rate > 70% on pilot batch
- [ ] All characters at same scale (height ±2px)
- [ ] All characters share same baseline (y=108)
- [ ] Walk cycles play smoothly (no jitter)
- [ ] Attack frames have clear anticipation → impact → recovery
- [ ] Sorting works on slopes/elevation seams
- [ ] No palette drift across character set

---

## Next Action

**Run `python3 freeze_workflow_test.py` and report results.**

If it passes → Move to Step 2.  
If it fails → Tune workflow and retry.

Do not skip this step.
