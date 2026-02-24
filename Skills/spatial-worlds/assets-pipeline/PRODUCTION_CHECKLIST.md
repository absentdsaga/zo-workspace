# Spatial Worlds Asset Pipeline - Production Checklist

**Current Status: Step 1 (Workflow Freeze)**

## Implementation Progress

- [x] Freeze test script created (`freeze_workflow_test.py`)
- [x] Deterministic seed strategy implemented (`seed_strategy.py`)
- [x] API integration with retry logic ready (`batch_orchestrator_v2.py`)
- [x] Angle consistency QC gate #7 added (`qc_checker.py`)
- [ ] **NEXT → Run workflow freeze test** (3/3 must pass)
- [ ] Lock workflow JSON
- [ ] Run 20-frame pilot batch
- [ ] Hero-to-world calibration
- [ ] Tighten metadata for combat
- [ ] Full production scale-up

---

## Step 1: Lock Workflow JSON ← **YOU ARE HERE**

**Objective**: Freeze a single ComfyUI workflow that produces usable frames

### Action Required

```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline

# Start ComfyUI if not running
./start_comfyui.sh

# In another terminal, run freeze test
python3 freeze_workflow_test.py
```

### Success Criteria

- 3/3 smoke prompts pass ALL artifact checks
- No background card/box
- Feet visible at baseline
- Consistent 3/4 angle
- Silhouette readable
- Transparency present

### If Test Fails

**DO NOT PROCEED to Step 2 until this passes.**

1. Review failed outputs in `test_freeze_output/`
2. Identify failure modes (box artifacts, cropped feet, etc.)
3. Adjust workflow parameters:
   - Increase negative prompt weight for "rectangular frame, card, border"
   - Adjust denoise (currently 1.0, try 0.85-0.95 for tighter control)
   - Add controlnet or img2img refinement pass
   - Tune CFG scale (currently 6.0)
4. Re-run `freeze_workflow_test.py` until 3/3 pass
5. Only then proceed to Step 2

---

## Step 2: Wire API Integration

**Prerequisites**: Step 1 complete (workflow locked)

### Files Ready
- ✅ `batch_orchestrator_v2.py` - Full API integration with retry
- ✅ `seed_strategy.py` - Deterministic seed generation
- ✅ Locked workflow: `comfy/workflow_locked_v1.json` (created after Step 1 passes)

### Action Required

```bash
# Replace old orchestrator
mv batch_orchestrator.py batch_orchestrator_v1_backup.py
mv batch_orchestrator_v2.py batch_orchestrator.py

# Verify seed strategy
python3 seed_strategy.py
```

### Key Features Added
- ✅ `build_workflow()` - Injects prompts + deterministic seeds
- ✅ `submit_prompt()` - POST to ComfyUI /prompt endpoint
- ✅ `poll_until_done()` - GET /history with timeout
- ✅ `collect_output_files()` - Parse outputs from history
- ✅ `copy_to_output_raw()` - Download via /view endpoint
- ✅ Retry logic: 3 attempts with exponential backoff (2s, 4s, 8s)
- ✅ Failure tracking: JSON markers for failed frames
- ✅ Traceability: Log prompt_id per frame

---

## Step 3: Run 20-Frame Pilot Batch

**Prerequisites**: Step 2 complete (API integration active)

### Test Scope

Generate minimal viable set to validate full pipeline:

```json
{
  "character_id": "hero_orange",
  "states": ["idle"],
  "color_theme": "orange hero character",
  "character_type": "character"
}
```

```json
{
  "character_id": "npc_bear",
  "states": ["idle"],
  "color_theme": "brown bear character",
  "character_type": "character"
}
```

```json
{
  "character_id": "npc_raccoon",
  "states": ["idle"],
  "color_theme": "raccoon character",
  "character_type": "character"
}
```

- **hero_orange**: idle (8 frames) + walk (4 key frames) = 12 frames
- **npc_bear**: idle (4 frames)
- **npc_raccoon**: idle (4 frames)
- **Total**: 20 frames

### Action Required

```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline

# Run pilot jobs
python3 batch_orchestrator.py jobs/pilot_hero.json
python3 batch_orchestrator.py jobs/pilot_bear.json
python3 batch_orchestrator.py jobs/pilot_raccoon.json

# Check QC pass rate
grep "PASSED QC" logs/*.log | wc -l
grep "FAILED QC" logs/*.log | wc -l
```

### Success Criteria

- **QC pass rate > 70%** initially
- No box artifacts in pass set
- No baseline jitter visible in walk test
- All passed frames advance to atlas assembly

### If Pass Rate < 70%

**DO NOT SCALE YET.**

Tune prompts/denoise/negative prompt:
1. Analyze QC failure reasons: `cat output_qc_fail/*/\*_reason.json`
2. Identify common failure modes
3. Adjust `pipeline_config.json` prompts or workflow parameters
4. Re-run pilot batch
5. Iterate until pass rate > 70%

---

## Step 4: Hero-to-World Calibration

**Prerequisites**: Step 3 complete (pilot frames generated)

### Objective

Lock baseline + scale + shadow parameters **before** mass production

### Action Required

1. **Import 1 idle frame** for hero + 1 NPC into engine
2. **Stand both on same tile**
3. **Validate**:
   - Feet contact at y baseline
   - Same perceived scale class
   - Same sorting behavior at elevation seams
   - Shadow contact feels grounded

4. **Lock these values** in `pipeline_config.json`:
   ```json
   "normalization": {
     "target_char_height_px": 84,    // DO NOT CHANGE AFTER THIS
     "baseline_y": 108,               // DO NOT CHANGE AFTER THIS
     "pivot": [64, 108]               // DO NOT CHANGE AFTER THIS
   },
   "shadow": {
     "radius_x": 10,                  // DO NOT CHANGE AFTER THIS
     "radius_y": 4,                   // DO NOT CHANGE AFTER THIS
     "alpha": 0.28                    // DO NOT CHANGE AFTER THIS
   }
   ```

### Red Flag

If you keep changing these values after starting production, you'll get:
- Inconsistent character scales across batches
- Sorting glitches at elevation seams
- Floating/sinking characters on slopes

**Lock once. Do not revisit.**

---

## Step 5: Tighten Metadata for Combat

**Prerequisites**: Step 4 complete (calibration locked)

### Objective

Add tactical gameplay data to metadata before full production

### Updates to `batch_orchestrator.py` → `generate_metadata()`

Add these fields per frame:

```python
{
  "frames": [
    {
      "file": "hero_orange_attack_f06.png",
      "duration_ms": 66,
      "event": "hit_start",
      
      # NEW FIELDS
      "hurtbox": {           # Character vulnerable region
        "x": 48,
        "y": 32,
        "w": 32,
        "h": 52
      },
      "hitbox": {            # Attack damage region (only on active frames)
        "x": 80,
        "y": 40,
        "w": 24,
        "h": 16,
        "damage": 10
      },
      "eventFrames": {       # Timing markers for audio/VFX
        "footstep_l": 3,
        "footstep_r": 7,
        "hit_start": 6,
        "hit_end": 8
      },
      "sortBias": 0          # Override for tall props/stairs (usually 0)
    }
  ]
}
```

### Why This Matters

Combat timing breaks if you add this later and have to regenerate all metadata.

Add it now, fill with placeholder values, tune later during gameplay integration.

---

## Step 6: Full Production Scale-Up

**Prerequisites**: ALL previous steps complete + validated

### Character Set

Generate full animation sets for:

- `hero_orange`: idle, walk, attack, hit (29 frames total)
- `npc_bear`: idle, walk, attack, hit (29 frames total)
- `npc_raccoon`: idle, walk, attack, hit (29 frames total)
- (Add more characters as needed)

### Action Required

```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline

# Full production jobs
python3 batch_orchestrator.py jobs/hero_orange.json
python3 batch_orchestrator.py jobs/npc_bear.json
python3 batch_orchestrator.py jobs/npc_raccoon.json

# Monitor QC pass rates
watch -n 5 'tail -20 logs/*.log'

# Assemble atlases
python3 atlas_assembler.py output_qc_pass/hero_orange
python3 atlas_assembler.py output_qc_pass/npc_bear
python3 atlas_assembler.py output_qc_pass/npc_raccoon
```

### Expected Output

For each character:
- Atlas PNG: `atlas/hero_orange_atlas.png`
- Metadata JSON: `metadata/hero_orange_idle.json`, `metadata/hero_orange_walk.json`, etc.
- QC logs: `logs/hero_orange.log` + `logs/hero_orange_results.json`

---

## Red Flags to Watch During Production

### 🚨 Immediate Reject Signals

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Rectangular artifact** | Frame/card in prompt result | Strengthen negative prompt, add "no border" |
| **Feet baseline drift** | Normalization failing | Check `normalize_sprite.py` baseline detection |
| **Palette explosion** | Special effects bleeding | Separate FX layer or VFX sprites |
| **Camera angle drift** | Seed variation too high | Lock workflow tighter, reduce denoise |
| **Jitter in idle** | Center-of-mass unstable | Add pose consistency to positive prompt |
| **Scale inconsistency** | Normalization scale detection off | Manual review + fix scale gate threshold |

### 🔍 Quality Gates Summary

1. **Box artifacts** - Edge opacity check
2. **Feet visibility** - Bottom region pixel count
3. **Scale drift** - Bbox height vs target
4. **Palette overflow** - Unique color count
5. **Jitter** - Center-of-mass stability
6. **Silhouette break** - Bbox area delta
7. **Angle consistency** - L/R mass ratio (NEW)

If QC pass rate drops below 70% at any point, **STOP and debug** before continuing.

---

## Success Metrics

### Per-Character Batch

- QC pass rate > 70% (target: 80%+)
- No manual frame rejections in pass set
- Walk cycles play smoothly (no jitter)
- Attack frames have clear anticipation → impact → recovery arc
- All states loop cleanly (idle, walk) or terminate correctly (attack, hit)

### Full Production Set

- All characters at same scale (height ±2px)
- All characters share same baseline (y=108)
- Consistent sorting on slopes/elevation changes
- No palette drift across character set
- Atlas packing efficiency > 75%

---

## Final Verification

Before deploying to engine:

1. ✅ Import all atlases + metadata into engine
2. ✅ Spawn all characters on same tile
3. ✅ Verify scale + baseline + shadow consistency
4. ✅ Test walk cycles on flat + slopes
5. ✅ Test attack animations with hitbox visualization
6. ✅ Test sorting at elevation seams (characters behind/in-front of tiles)
7. ✅ Verify depth sorting with 10+ concurrent characters

If any of these fail, do NOT ship. Fix the pipeline and regenerate.

---

**Remember**: Lock the workflow first. Scale second. Debugging 1000 bad frames is way more expensive than tuning 3 good ones.
