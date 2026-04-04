---
name: vurt-subtitles
description: Batch subtitle generator for VURT titles. Frame.io v4 → AssemblyAI pipeline with speaker diarization, QC flagging, and editor handoff tools.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Frame.io Production Pipeline (primary)

Full pipeline: crawl Frame.io inventory → transcribe with speaker diarization → generate SRTs with QC flags + editor manifest.

### Prerequisites
- `VURT_ADOBE_CLIENT_ID` and `VURT_ADOBE_CLIENT_SECRET` in `/root/.zo_secrets`
- `ASSEMBLYAI_API_KEY` in Settings > Advanced
- Valid Adobe OAuth tokens in `/home/workspace/.secrets/adobe-tokens.json`

### Step 1: Crawl inventory
```bash
source /root/.zo_secrets
python3 Skills/vurt-subtitles/scripts/frameio-crawl.py
```
Outputs `frameio-inventory.json` + `frameio-inventory.csv` with all video files, sizes, and Frame.io URLs.

### Step 2: Run batch transcription
```bash
source /root/.zo_secrets

# Dry run (see what would be processed)
python3 Skills/vurt-subtitles/scripts/frameio-batch.py --dry-run

# Process everything
python3 Skills/vurt-subtitles/scripts/frameio-batch.py

# Limit to N files
python3 Skills/vurt-subtitles/scripts/frameio-batch.py --limit 10

# Process only a specific folder
python3 Skills/vurt-subtitles/scripts/frameio-batch.py --folder "Licensed Titles/1. SWIRL FILMS/Karma in Heels"
```

### Output
- `Documents/srts-full/*.srt` — SRT files (speaker-diarized, merged utterances)
- `Documents/srts-full/MANIFEST.csv` — Maps each SRT to Frame.io view URL, duration, word count, speakers, flag count
- `Documents/srts-full/REVIEW_FLAGS.csv` — Flagged segments for editor attention (low confidence + short utterance speaker changes)
- `Documents/srts-full/batch-report.json` — Full run report with stats

### Features
- **Speaker diarization**: Uses AssemblyAI universal-3-pro model with speaker labels
- **Merge pass**: Joins consecutive same-speaker utterances split mid-sentence (< 3s gap)
- **Low-confidence flagging**: Clusters of 3+ words below 60% confidence
- **Short-utterance flagging**: Utterances < 1 second with speaker changes (often misattributed)
- **Resume support**: Skips files that already have SRTs — safe to re-run after interruption
- **Editor handoff**: MANIFEST.csv links each SRT to its Frame.io video player URL

### Cost
- universal-3-pro: ~$0.006/min
- Current inventory: ~592 files, ~3,858 min estimated, ~$24

---

## Other Tools

### Local file transcription
```bash
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input /path/to/video.mp4
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input /path/to/videos/ --output /path/to/srts/
```

### Mux batch (legacy)
```bash
python3 Skills/vurt-subtitles/scripts/mux-batch-srt.py --output ./srts --limit 10
```
Requires `VURT_MUX_TOKEN_ID` and `VURT_MUX_TOKEN_SECRET`.

---

## Notes
- Supported formats: mp4, mov, mkv, avi, webm, mp3, wav, m4a, flac, ogg
- No grammar correction pass — VURT content includes intentional slang/vernacular that should be preserved as-spoken
- Accuracy: 95%+ on produced dialogue. QC flags catch the remaining 5%.
