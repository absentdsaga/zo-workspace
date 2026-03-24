---
name: vurt-subtitles
description: Batch subtitle generator for VURT titles. Uses AssemblyAI API to generate SRT files from video/audio files at scale (~$0.003/min). Supports single files, directories, and URL lists.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Usage

1. Set `ASSEMBLYAI_API_KEY` in [Settings > Advanced](/?t=settings&s=advanced)
2. Run the script:

```bash
# Single file
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input /path/to/video.mp4

# Entire directory
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input /path/to/videos/

# From a text file of URLs (one per line)
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input urls.txt --url-list

# Custom output directory
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input /path/to/videos/ --output /path/to/srts/

# Control concurrency (default 5)
bun run Skills/vurt-subtitles/scripts/generate-srt.ts --input /path/to/videos/ --concurrency 10
```

Output: SRT files saved alongside source files (or in `--output` dir), named `<filename>.srt`.

## Notes
- Supported formats: mp4, mov, mkv, avi, webm, mp3, wav, m4a, flac, ogg
- Accuracy is 95%+ on produced dialogue (VURT's content is clean audio, so expect high accuracy)
- Cost: ~$0.003/min → ~$15 for 5,000 minutes of content
- The script handles retries, progress tracking, and generates a summary report
