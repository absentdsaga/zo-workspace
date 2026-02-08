---
name: tiktokify
description: Transform any video into viral-ready TikTok/Reels format with auto-captions, fast cuts, and vertical cropping
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---

# TikTokify Video Skill

Automatically transforms horizontal videos into viral-ready vertical shorts for TikTok, Reels, and YouTube Shorts.

## What It Does

- Converts to 9:16 vertical aspect ratio (1080x1920)
- Extracts most engaging 15-60 second clips
- Adds auto-generated captions (burned in)
- Removes silence and dead air
- Fast-paced cuts (avg 2-3 seconds per cut)
- Optional: Add trending audio, zoom effects
- Outputs ready-to-upload MP4

## Usage

### Basic TikTokify

```bash
bun scripts/tiktokify.ts --input video.mp4
```

### Advanced Options

```bash
bun scripts/tiktokify.ts \
  --input video.mp4 \
  --duration 30 \
  --add-captions \
  --auto-crop \
  --remove-silence \
  --output viral.mp4
```

### Batch Process

```bash
bun scripts/tiktokify.ts --batch /path/to/videos/*.mp4
```

## Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | Source video file | Required |
| `--duration` | Target length (seconds) | 30 |
| `--add-captions` | Burn-in auto-generated captions | true |
| `--auto-crop` | Smart crop to keep subject centered | true |
| `--remove-silence` | Cut out silent sections | true |
| `--fast-cuts` | Apply trending fast-cut style | true |
| `--output` | Output file path | `{input}_tiktok.mp4` |

## How It Works

1. **Transcription:** Uses `transcribe_video` to get timestamp-aligned text
2. **Scene Detection:** FFmpeg analyzes scenes, identifies best moments
3. **Smart Cropping:** Detects faces/subjects, crops to keep them centered
4. **Caption Rendering:** Burns captions with TikTok-style formatting
5. **Silence Removal:** Cuts dead air using audio analysis
6. **Fast Cuts:** Speeds up by 1.1-1.3x, removes pauses
7. **Export:** Outputs 9:16 MP4 optimized for mobile

## Examples

### Convert YouTube video to TikTok

```bash
# Download YouTube video
yt-dlp "https://youtube.com/watch?v=..." -o input.mp4

# TikTokify it
bun scripts/tiktokify.ts --input input.mp4 --duration 45
```

### Batch process all videos in a folder

```bash
bun scripts/tiktokify.ts --batch ~/Videos/raw/*.mp4 --output ~/Videos/tiktok/
```

## Technical Stack

- **FFmpeg:** Video processing, cropping, cutting
- **Whisper (via transcribe_video):** Accurate transcription with timestamps
- **ImageMagick:** Caption rendering with custom fonts
- **Scene detection:** FFmpeg's scene filter for smart cuts

## Output Format

- **Resolution:** 1080x1920 (9:16)
- **Codec:** H.264 (best compatibility)
- **Bitrate:** 8 Mbps (high quality, small file)
- **Audio:** AAC 128kbps
- **Captions:** Burned-in, yellow text, black outline

## Tips for Best Results

1. **Start with good source:** 1080p+ horizontal video works best
2. **Keep subjects centered:** Auto-crop works better when subject is in frame
3. **Good audio:** Clear speech = better captions
4. **Action-packed:** Videos with movement convert better than talking heads
5. **Test durations:** Try 15s, 30s, 60s to see what performs

## Roadmap

- [ ] Add trending audio library integration
- [ ] AI-powered "hook detector" (finds most engaging 3 seconds)
- [ ] Template system for different niches (fitness, tech, comedy)
- [ ] Auto-upload to TikTok/Reels via APIs
- [ ] A/B test multiple versions with different hooks
