# Sprite Pipeline - Quick Reference

## 🚀 Common Commands

### Start ComfyUI Server
```bash
cd /home/workspace/Skills/spatial-worlds/assets-pipeline
./start_comfyui.sh
```
Access at: http://localhost:8188

### Test Pipeline (No ComfyUI Needed)
```bash
./test_pipeline.sh
```

### Run Character Job
```bash
python3 batch_orchestrator.py jobs/hero_orange.json
```

### Monitor Job Progress
```bash
tail -f logs/hero_orange.log
```

### Check Job Results
```bash
cat logs/hero_orange_results.json | jq
```

### Normalize Single Sprite
```bash
python3 normalize_sprite.py input.png output.png
```

### QC Check Single Frame
```bash
python3 qc_checker.py frame.png [prev_frame.png]
```

### Build Texture Atlas
```bash
# For specific animation
python3 atlas_assembler.py character_id state_name

# For all animations
python3 atlas_assembler.py character_id
```

---

## 📋 Quick Specs

### Frame Specification
- **Canvas**: 128×128 px
- **Character Height**: 84 px
- **Baseline (feet)**: y=108
- **Pivot**: (64, 108) - bottom-center
- **Palette**: max 36 colors
- **Scaling**: nearest-neighbor (pixel-perfect)

### Animation Frame Counts
- **idle**: 8 frames @ 8 fps
- **walk**: 10 frames @ 12 fps
- **attack**: 12 frames @ 15 fps (events: hit_start=6, hit_end=8)
- **hit**: 5 frames @ 12 fps

### QC Thresholds
- Box artifacts: ≤5 opaque border pixels
- Feet baseline: ±2 px tolerance
- Scale drift: ±5% of target height
- Palette: ≤36 unique colors
- Jitter: ≤2 px frame-to-frame shift
- Silhouette: ≤18% area change

---

## 📁 Key File Locations

### Input
- References: `input/refs/`
- Masks: `input/masks/`

### Output
- Raw generation: `output_raw/<character>/`
- Cutout: `output_cut/<character>/`
- Normalized: `output_norm/<character>/`
- QC passed: `output_qc_pass/<character>/`
- QC failed: `output_qc_fail/<character>/`
- Atlases: `atlas/`
- Metadata: `metadata/<character>/`
- Logs: `logs/`

### Configuration
- Master config: `pipeline_config.json`
- Job specs: `jobs/*.json`
- Workflows: `comfy/*.json`

---

## 🎨 Prompt Templates

### Global Style (Always Included)
```
isometric 3/4 tactical RPG character sprite, single character only,
clean pixel-art readability, limited palette, crisp silhouette,
feet fully visible, grounded stance, transparent background,
no environment, no frame, no card, no text, no watermark
```

### Negative (Always Included)
```
rectangular frame, border, poster, card, background scene,
floor texture, painterly smear, noisy texture, blurry edges,
extra limbs, cropped feet, cut-off weapon, watermark, text, logo
```

### Pose Modifiers
- **idle**: neutral idle pose, weight balanced, readable silhouette
- **walk_contact**: walk cycle contact pose, one foot forward, one back
- **walk_passing**: walk cycle passing pose, hips centered
- **attack_anticipation**: attack anticipation, weapon drawn back
- **attack_impact**: attack impact pose, clear forward action line
- **hit**: hit reaction pose, recoil stance

---

## 🔧 Common Issues

### All Frames Failing QC
```bash
# Check failure reasons
cat output_qc_fail/*/*.json | jq '.failures'

# Most common fixes:
# - Feet not aligned → adjust baseline_y in config
# - Scale drift → adjust target_char_height_px
# - Palette overflow → reduce colors or increase limit
```

### ComfyUI Not Responding
```bash
# Check if server running
curl http://localhost:8188

# Restart server
pkill -f "python main.py"
./start_comfyui.sh
```

### Pipeline Crashes
```bash
# Check logs
cat logs/<character>.log

# Common issues:
# - Missing dependencies → pip3 install -r requirements.txt
# - Permissions → chmod +x *.py *.sh
# - Disk space → df -h
```

---

## 📊 Expected Results

### Successful Job Run
```json
{
  "character_id": "hero_orange",
  "states": {
    "idle": {
      "passed_frames": 8,
      "total_frames": 8,
      "metadata": "metadata/hero_orange/hero_orange_idle.json"
    },
    "walk": {
      "passed_frames": 10,
      "total_frames": 10,
      "metadata": "metadata/hero_orange/hero_orange_walk.json"
    }
  }
}
```

### QC Pass Example
```json
{
  "image": "output_norm/hero_orange/hero_orange_idle_f01.png",
  "passed": true,
  "failures": []
}
```

### QC Fail Example
```json
{
  "image": "output_norm/hero_orange/hero_orange_idle_f02.png",
  "passed": false,
  "failures": [
    {
      "check": "feet_visibility",
      "reason": "Feet at y=112, expected baseline=108±2"
    }
  ]
}
```

---

## 🎯 Workflow Checklist

### First Time Setup
- [ ] Install dependencies: `pip3 install -r requirements.txt`
- [ ] Test pipeline: `./test_pipeline.sh`
- [ ] Start ComfyUI: `./start_comfyui.sh`
- [ ] Configure workflow in UI
- [ ] Export workflow JSON to `comfy/`
- [ ] Implement API calls in `batch_orchestrator.py`

### Style Calibration
- [ ] Add references to `input/refs/`
- [ ] Generate 12 test frames
- [ ] Validate in-scene fit
- [ ] Lock `pipeline_config.json`

### Character Production
- [ ] Create job file in `jobs/`
- [ ] Run `batch_orchestrator.py`
- [ ] Monitor logs
- [ ] Review QC failures
- [ ] Build atlas
- [ ] Load in engine

---

## 💡 Pro Tips

1. **Always run style calibration first** - lock your parameters before batch production

2. **Use fixed seeds** - deterministic generation prevents random variations

3. **Monitor QC failures** - they tell you exactly what's wrong

4. **Start small** - test with 1 character before batching all characters

5. **Keep references consistent** - use same style board for all characters

6. **Check output at each stage** - don't wait until the end to discover issues

7. **Backup working configs** - before making changes, copy `pipeline_config.json`

8. **Use version control** - commit after each successful character

---

## 📞 Help

- **Technical docs**: `README.md`
- **Full guide**: `SPRITE_PIPELINE_GUIDE.md`
- **Status**: `PIPELINE_STATUS.md`
- **ComfyUI help**: https://github.com/comfyanonymous/ComfyUI

---

**Pipeline Version**: 1.0 (saga_iso_v1 preset)
**Last Updated**: 2026-02-15
