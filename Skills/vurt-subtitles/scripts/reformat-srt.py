"""
Reformat existing SRT files with new display settings.
Applies line wrapping and minimum duration without re-transcribing.
Used to create new versions from existing SRTs for A/B comparison.

Usage:
  python3 Skills/vurt-subtitles/scripts/reformat-srt.py --input DIR --output DIR [--max-chars 32] [--min-duration 1.0] [--merge]
"""
import os, re, argparse


def parse_srt(text):
    """Parse SRT text into list of blocks: {index, start_ms, end_ms, text}"""
    blocks = []
    # Split on double newline or block boundaries
    raw_blocks = re.split(r'\n\n+', text.strip())
    for raw in raw_blocks:
        lines = raw.strip().split('\n')
        if len(lines) < 3:
            continue
        # First line: index
        try:
            idx = int(lines[0].strip())
        except ValueError:
            continue
        # Second line: timestamps
        ts_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[1].strip())
        if not ts_match:
            continue
        start_ms = ts_to_ms(ts_match.group(1))
        end_ms = ts_to_ms(ts_match.group(2))
        # Remaining lines: text
        text_content = '\n'.join(lines[2:]).strip()
        blocks.append({
            'index': idx,
            'start_ms': start_ms,
            'end_ms': end_ms,
            'text': text_content,
        })
    return blocks


def ts_to_ms(ts):
    """Convert SRT timestamp to milliseconds."""
    match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', ts)
    if not match:
        return 0
    h, m, s, ms = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return h * 3600000 + m * 60000 + s * 1000 + ms


def ms_to_ts(ms):
    """Convert milliseconds to SRT timestamp."""
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    f = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{f:03d}"


def wrap_into_chunks(text, max_chars=32, max_lines=2):
    """Split text into chunks that each fit within max_chars x max_lines.
    Returns a list of strings. Each string has max_lines lines of max_chars.
    No text is dropped.
    """
    flat = ' '.join(text.split())
    if len(flat) <= max_chars:
        return [flat]

    words = flat.split()
    chunks = []
    current_chunk_lines = []
    current_line = ""

    for word in words:
        test = f"{current_line} {word}".strip() if current_line else word
        if len(test) <= max_chars:
            current_line = test
        else:
            if current_line:
                current_chunk_lines.append(current_line)
            current_line = word
            # If chunk is full, save it and start new chunk
            if len(current_chunk_lines) >= max_lines:
                chunks.append("\n".join(current_chunk_lines))
                current_chunk_lines = []

    # Don't forget remaining text
    if current_line:
        current_chunk_lines.append(current_line)
    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines))

    return chunks if chunks else [flat]


def enforce_min_duration(blocks, min_sec=1.0):
    """Ensure minimum display time per block."""
    min_ms = int(min_sec * 1000)
    result = []
    for i, b in enumerate(blocks):
        b = dict(b)
        dur = b['end_ms'] - b['start_ms']
        if dur < min_ms:
            new_end = b['start_ms'] + min_ms
            if i < len(blocks) - 1:
                next_start = blocks[i + 1]['start_ms']
                new_end = min(new_end, next_start - 1)
            b['end_ms'] = max(b['end_ms'], new_end)
        result.append(b)
    return result


def merge_blocks(blocks, gap_ms=3000):
    """Merge consecutive blocks that are close together and where
    the first doesn't end with sentence-ending punctuation.
    Note: without speaker data, this merges any consecutive close blocks."""
    if not blocks:
        return blocks
    merged = [dict(blocks[0])]
    for b in blocks[1:]:
        prev = merged[-1]
        gap = b['start_ms'] - prev['end_ms']
        prev_text = prev['text'].strip()
        ends_sentence = prev_text and prev_text[-1] in '.!?"\')'
        if gap < gap_ms and not ends_sentence:
            prev['end_ms'] = b['end_ms']
            prev['text'] = prev['text'].strip() + ' ' + b['text'].strip()
        else:
            merged.append(dict(b))
    return merged


def blocks_to_srt(blocks):
    """Convert blocks back to SRT text."""
    srt_parts = []
    for i, b in enumerate(blocks, 1):
        start = ms_to_ts(b['start_ms'])
        end = ms_to_ts(b['end_ms'])
        srt_parts.append(f"{i}\n{start} --> {end}\n{b['text']}\n")
    return "\n".join(srt_parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Reformat SRT files with new display settings")
    parser.add_argument("--input", "-i", required=True, help="Input directory with SRT files")
    parser.add_argument("--output", "-o", required=True, help="Output directory for reformatted SRTs")
    parser.add_argument("--max-chars", type=int, default=32, help="Max characters per line (default: 32)")
    parser.add_argument("--max-lines", type=int, default=2, help="Max lines per block (default: 2)")
    parser.add_argument("--min-duration", type=float, default=1.0, help="Min display duration in seconds (default: 1.0)")
    parser.add_argument("--merge", action="store_true", help="Enable merge pass for mid-sentence splits")
    parser.add_argument("--merge-gap", type=int, default=3000, help="Max gap in ms for merge (default: 3000)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    srt_files = [f for f in os.listdir(args.input) if f.endswith('.srt')]
    if not srt_files:
        print(f"No SRT files found in {args.input}")
        return

    print(f"Reformatting {len(srt_files)} SRT files")
    print(f"  Max chars/line: {args.max_chars}")
    print(f"  Max lines/block: {args.max_lines}")
    print(f"  Min duration: {args.min_duration}s")
    print(f"  Merge pass: {'ON' if args.merge else 'OFF'}")
    print()

    for fname in sorted(srt_files):
        in_path = os.path.join(args.input, fname)
        out_path = os.path.join(args.output, fname)

        with open(in_path) as f:
            content = f.read()

        blocks = parse_srt(content)
        original_count = len(blocks)

        # Apply transforms
        if args.merge:
            blocks = merge_blocks(blocks, args.merge_gap)
        blocks = enforce_min_duration(blocks, args.min_duration)

        # Wrap text — split long blocks into multiple blocks with proportional timing
        wrapped_blocks = []
        for b in blocks:
            chunks = wrap_into_chunks(b['text'], args.max_chars, args.max_lines)
            if len(chunks) == 1:
                b['text'] = chunks[0]
                wrapped_blocks.append(b)
            else:
                # Split timing proportionally across chunks
                total_dur = b['end_ms'] - b['start_ms']
                chunk_dur = total_dur // len(chunks)
                for j, chunk in enumerate(chunks):
                    start = b['start_ms'] + j * chunk_dur
                    end = b['start_ms'] + (j + 1) * chunk_dur if j < len(chunks) - 1 else b['end_ms']
                    wrapped_blocks.append({
                        'index': 0,
                        'start_ms': start,
                        'end_ms': end,
                        'text': chunk,
                    })
        blocks = wrapped_blocks

        srt = blocks_to_srt(blocks)
        with open(out_path, 'w') as f:
            f.write(srt)

        merged_count = len(blocks)
        merge_info = f" (merged {original_count}→{merged_count})" if args.merge and merged_count != original_count else ""
        print(f"  {fname}: {merged_count} blocks{merge_info}")

    print(f"\nDone. Output: {args.output}")


if __name__ == "__main__":
    main()
