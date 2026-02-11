#!/bin/bash
cd /home/workspace/Skills/build-preview

echo "=== COMPREHENSIVE QA TEST SUITE ==="
echo "Starting systematic testing..."

# Test 1: Extended gameplay recording
echo "Test 1/5: Recording 30s extended gameplay..."
python3.12 scripts/record_video.py http://localhost:3000/ 30 /home/workspace/qa-test-extended.mp4

# Test 2: Multiple short recordings to catch frame-specific issues
echo "Test 2/5: Recording 5x 10s sessions..."
for i in {1..5}; do
  python3.12 scripts/record_video.py http://localhost:3000/ 10 /home/workspace/qa-test-session-$i.mp4
  sleep 2
done

# Extract frames from extended test at 1s intervals
echo "Test 3/5: Extracting frames every 1 second..."
for t in {1..30}; do
  ffmpeg -i /home/workspace/qa-test-extended.mp4 -ss 00:00:$(printf "%02d" $t) -vframes 1 /home/workspace/frames/frame-${t}s.png -y 2>&1 | tail -1
done

echo "Test 4/5: Extracting frames from all sessions..."
mkdir -p /home/workspace/frames/sessions
for i in {1..5}; do
  for t in {1..10}; do
    ffmpeg -i /home/workspace/qa-test-session-$i.mp4 -ss 00:00:$(printf "%02d" $t) -vframes 1 /home/workspace/frames/sessions/session-${i}-frame-${t}s.png -y 2>&1 | tail -1
  done
done

echo "Test 5/5: Creating analysis summary..."
echo "Total frames extracted: $(ls /home/workspace/frames/*.png 2>/dev/null | wc -l)"
echo "Session frames extracted: $(ls /home/workspace/frames/sessions/*.png 2>/dev/null | wc -l)"

echo "=== QA TEST COMPLETE ==="
echo "Videos saved to /home/workspace/qa-test-*.mp4"
echo "Frames saved to /home/workspace/frames/"
