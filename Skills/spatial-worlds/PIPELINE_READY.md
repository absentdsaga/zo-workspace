# Spatial Worlds Asset Pipeline - READY TO EXECUTE

**Status**: All implementation complete. Workflow freeze test running on CPU (slow).

---

## ✅ What's Been Built

### Core Implementation

1. **Workflow Freeze Test** (`assets-pipeline/freeze_workflow_test.py`)
   - Tests 3 smoke prompts with zero-tolerance artifact checks
   - Currently running in background on CPU (will take 2-3 hours)
   - Alternative: Manual UI validation (see `MANUAL_FREEZE_WORKFLOW.md`)

2. **Deterministic Seed Strategy** (`assets-pipeline/seed_strategy.py`)
   - Formula: `base_seed + char_hash + state_offset + frame_index`
   - Verified unique across 400 test combinations
   - ✅ Self-test passed

3. **Full API Integration** (`assets-pipeline/batch_orchestrator_v2.py`)
   - Complete ComfyUI API workflow: POST /prompt → poll /history → fetch /view
   - Retry logic: 3 attempts with exponential backoff (2s, 4s, 8s)
   - Failure tracking with JSON markers
   - Traceability: logs prompt_id per frame
   - ✅ API connectivity verified

4. **QC Gate #7: Angle Consistency** (`assets-pipeline/qc_checker.py`)
   - L/R pixel mass ratio check
   - Detects 3/4 angle drift between adjacent frames
   - Threshold: max 0.15 change
   - ✅ Syntax validated

5. **Pilot Job Files**
   - `jobs/pilot_hero.json` - 8 idle frames
   - `jobs/pilot_bear.json` - 4 idle frames (NPC)
   - `jobs/pilot_raccoon.json` - 4 idle frames (NPC)
   - Total: 16 frames for pilot batch

### Documentation

- `WORKFLOW_FREEZE_CONTRACT.md` - Step 1 hard requirements
- `PRODUCTION_CHECKLIST.md` - Full 6-step workflow
- `MANUAL_FREEZE_WORKFLOW.md` - CPU workaround
- `STATUS.md` - Progress tracking
- `QUICK_START.md` - One-page reference

---

## 🎯 Current State

### ComfyUI Status
- ✅ Running on http://localhost:8188
- ✅ Model loaded: v1-5-pruned-emaonly.safetensors (4.0GB)
- ✅ API responsive and tested
- ⚠️  Running on CPU (slow but functional)

### Freeze Test Status
- 🔄 **Running in background** (started at 03:29 UTC)
- ⏱️  Estimated completion: ~2-3 hours
- 📁 Output dir: `assets-pipeline/test_freeze_output/`

### What's Next

You have **3 options**:

#### Option 1: Wait for Automated Test (Recommended for validation)
```bash
# Check progress
ls -lh /home/workspace/Skills/spatial-worlds/assets-pipeline/test_freeze_output/

# When complete, review results
cat /home/workspace/Skills/spatial-worlds/assets-pipeline/test_freeze_output/results.json
```

#### Option 2: Manual UI Validation (Fastest)
1. Open http://localhost:8188
2. Load `comfy/workflow_character_base.json`
3. Test 3 prompts manually (see `MANUAL_FREEZE_WORKFLOW.md`)
4. If all pass, save as `comfy/workflow_locked_v1.json`
5. Proceed to Step 2

#### Option 3: Skip to Pilot Batch (Assumes workflow is good)
```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline

# Activate API integration
mv batch_orchestrator.py batch_orchestrator_v1_backup.py
mv batch_orchestrator_v2.py batch_orchestrator.py

# Run pilot batch (will take time on CPU)
python3 batch_orchestrator.py jobs/pilot_hero.json

# Monitor progress
tail -f logs/hero_orange.log
```

---

## 📊 Expected Timeline (CPU)

| Task | Frames | Time Estimate |
|------|--------|---------------|
| Freeze test (3 prompts) | 3 | 2-3 hours |
| Pilot batch (hero) | 8 | 5-6 hours |
| Pilot batch (bear) | 4 | 2-3 hours |
| Pilot batch (raccoon) | 4 | 2-3 hours |
| **Total pilot** | 16 | **~12-15 hours** |

**Recommendation**: Run overnight or use GPU instance for production.

---

## 🚀 Production-Ready Checklist

When you're ready to scale:

- [ ] Step 1: Workflow locked (freeze test passed or manual validation)
- [ ] Step 2: API integration active (`batch_orchestrator_v2.py`)
- [ ] Step 3: Pilot batch QC pass rate > 70%
- [ ] Step 4: Hero-to-world calibration complete
- [ ] Step 5: Metadata tightened (hurtbox, hitbox, events)
- [ ] Step 6: Full character set generated
- [ ] Step 7: In-engine validation (slopes, sorting, combat)

---

## 🔥 Red Flags

Watch for these during execution:

| Signal | Action |
|--------|--------|
| **Box artifacts** | Strengthen negative prompt |
| **Cropped feet** | Adjust canvas/composition |
| **Angle drift** | Lock 3/4 pose tighter |
| **QC pass rate < 70%** | Debug before scaling |
| **Baseline jitter** | Check `normalize_sprite.py` |

---

## 🎮 Next Session Commands

### Check freeze test results:
```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline
ls -lh test_freeze_output/
python3 freeze_workflow_test.py  # Re-run if needed
```

### Activate API integration:
```bash
mv batch_orchestrator.py batch_orchestrator_v1_backup.py
mv batch_orchestrator_v2.py batch_orchestrator.py
```

### Run pilot batch:
```bash
python3 batch_orchestrator.py jobs/pilot_hero.json
grep "PASSED QC\|FAILED QC" logs/hero_orange.log
```

### Calculate QC pass rate:
```bash
passed=$(grep "PASSED QC" logs/*.log | wc -l)
total=$(ls output_norm/*/*.png 2>/dev/null | wc -l)
echo "Pass rate: $passed/$total"
```

---

## 📝 Implementation Notes

All 7 steps from your workflow are addressed:

1. ✅ **Workflow freeze** - Test created, running, manual fallback documented
2. ✅ **API integration** - Full implementation with retry logic
3. ✅ **Deterministic seeds** - Implemented and verified
4. ✅ **Angle consistency QC** - Gate #7 added to checker
5. ⏳ **Pilot batch** - Jobs ready, awaiting freeze test completion
6. ⏳ **Hero-to-world calibration** - Documented in checklist
7. ⏳ **Metadata tightening** - Template ready in checklist

**The pipeline is ready. Execution is now limited by CPU speed.**

For production use: Consider GPU instance or cloud ComfyUI service.
