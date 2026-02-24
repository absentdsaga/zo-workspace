# Quick Start - Asset Pipeline

## Right Now: Step 1 (Workflow Freeze)

### One Command to Run

```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline
python3 freeze_workflow_test.py
```

### What It Does

Tests 3 smoke prompts with zero tolerance for artifacts:
1. hero_orange idle
2. npc_bear walk_contact  
3. npc_raccoon attack_impact

### What Happens Next

#### ✅ If 3/3 Pass

1. Workflow locked → `comfy/workflow_locked_v1.json`
2. You can proceed to Step 2 (API integration)

#### ❌ If < 3/3 Pass

1. Review failures in `test_freeze_output/`
2. Tune workflow in ComfyUI
3. Re-run test until 3/3 pass
4. **DO NOT PROCEED** until this passes

---

## After Lock: Step 2 (API Integration)

```bash
# Swap orchestrator
mv batch_orchestrator.py batch_orchestrator_v1_backup.py
mv batch_orchestrator_v2.py batch_orchestrator.py
```

---

## After API Wire: Step 3 (Pilot Batch)

```bash
# Run 20-frame pilot
python3 batch_orchestrator.py jobs/pilot_hero.json
python3 batch_orchestrator.py jobs/pilot_bear.json
python3 batch_orchestrator.py jobs/pilot_raccoon.json

# Check pass rate
grep "PASSED QC" logs/*.log | wc -l
grep "FAILED QC" logs/*.log | wc -l

# Pass rate must be > 70% to continue
```

---

## File Quick Reference

| File | Purpose |
|------|---------|
| `freeze_workflow_test.py` | Step 1: Lock workflow with 3 smoke tests |
| `batch_orchestrator_v2.py` | Step 2: Full API integration with retry |
| `seed_strategy.py` | Deterministic seeds for reproducibility |
| `qc_checker.py` | 7 QC gates including angle consistency |
| `WORKFLOW_FREEZE_CONTRACT.md` | Step 1 requirements (hard gate) |
| `PRODUCTION_CHECKLIST.md` | Full 6-step workflow |
| `STATUS.md` | Current status summary |

---

## Don't Forget

- **Lock workflow before API integration** - automate good outputs, not bad ones
- **QC pass rate > 70%** - tune before scaling
- **Lock baseline/scale/shadow after calibration** - do not change after production starts
- **Add metadata early** - hurtbox, hitbox, events (pain later if you don't)

---

**Start here:** `python3 freeze_workflow_test.py`
