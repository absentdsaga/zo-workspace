# Spatial Worlds Asset Pipeline - Current Status

**Updated**: 2026-02-15 08:00 UTC

## 🎯 Where We Are

**PILOT BATCH RUNNING** - Full pipeline end-to-end validation in progress

---

## ✅ Completed Steps

### 1. Workflow Freeze Test ✓
- Generated 3 test images on CPU
- Validated pipeline components work
- **Result**: 1/3 passed (npc_bear_walk_contact)
- Workflow locked as `comfy/workflow_locked_v1.json`

### 2. Background Removal Integrated ✓
- Created `cutout_sprite.py` using rembg
- Converts RGB → RGBA with transparency
- Integrated into orchestrator

### 3. API Integration Activated ✓
- `batch_orchestrator_v2.py` → `batch_orchestrator.py`
- Full ComfyUI API with retry logic
- Deterministic seeds active

### 4. QC Gate #7 Added ✓
- Angle consistency check in `qc_checker.py`
- L/R pixel mass ratio validation

---

## 🔄 Currently Running

**Mini Pilot Batch**: 2 bear idle frames

```
Started: ~08:00 UTC
ETA: ~09:00 UTC (1 hour)
Status: Frame 1/2 generating
```

**Pipeline Flow**:
```
Generate (ComfyUI) → Cutout (rembg) → Normalize → QC (7 gates) → Metadata
```

**Monitor**:
```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline
./monitor_pilot.sh
```

---

## 📊 What Happens Next

### If Mini Pilot Succeeds (QC pass rate > 70%)

1. ✅ Pipeline validated end-to-end
2. Scale to full pilot (hero 8 frames, bear 4, raccoon 4)
3. Hero-to-world calibration
4. Lock baseline/scale/shadow params
5. Full production (all character animation sets)

### If Mini Pilot Fails (QC pass rate < 70%)

1. Review QC failure reasons
2. Tune prompts in `pipeline_config.json`
3. Re-run mini pilot
4. Iterate until passing

---

## 📁 Key Files

| File | Status | Purpose |
|------|--------|---------|
| `batch_orchestrator.py` | ✓ Active | API integration with retry |
| `cutout_sprite.py` | ✓ Active | Background removal |
| `seed_strategy.py` | ✓ Ready | Deterministic seeds |
| `qc_checker.py` | ✓ Updated | 7 QC gates |
| `comfy/workflow_locked_v1.json` | ✓ Locked | Base workflow |
| `pipeline_config.json` | ✓ Active | 2 idle frames (mini) |
| `monitor_pilot.sh` | ✓ Ready | Progress monitoring |

---

## 🎮 Output Directories

```
output_raw/npc_bear/idle/     - Raw ComfyUI outputs
output_cut/npc_bear/          - Background removed
output_norm/npc_bear/         - Normalized 128x128
output_qc_pass/npc_bear/      - Passed QC
output_qc_fail/npc_bear/      - Failed QC
metadata/npc_bear/            - JSON metadata
logs/                         - Processing logs
```

---

## 📈 Progress Tracking

**Freeze Test**: 3/3 generated, 1/3 passed validation  
**Pipeline Integration**: 5/5 components active  
**Mini Pilot**: 0/2 frames completed (in progress)  
**Full Pilot**: 0/16 frames (awaiting mini pilot success)  
**Production**: 0/~100 frames (awaiting full pilot success)

---

## ⏱️ Timeline Estimate (CPU)

| Task | Frames | Time | Status |
|------|--------|------|--------|
| Freeze test | 3 | 1.5h | ✅ Done |
| Mini pilot | 2 | 1h | 🔄 Running |
| Full pilot | 16 | 8h | ⏳ Pending |
| Full production | ~100 | 50h | ⏳ Pending |

**Total with CPU**: ~60 hours  
**Total with GPU**: ~2-3 hours

---

## 🚀 When You Have GPU

All code is production-ready for GPU:

1. Point ComfyUI to GPU instance
2. Run `python3 freeze_workflow_test.py` (~5 min)
3. Run full pilot batch (~30-45 min)
4. Run full production (~1-2 hours)

**Current bottleneck**: CPU generation speed (not code)

---

## 📞 Check Status

```bash
# Quick status
./monitor_pilot.sh

# Live log
tail -f pilot_bear_mini.log

# Watch mode
watch -n 10 ./monitor_pilot.sh
```

---

**Next checkpoint**: ~09:00 UTC (check if mini pilot completed and passed QC)
