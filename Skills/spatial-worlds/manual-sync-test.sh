#!/bin/bash
# Manual multiplayer sync verification
# Opens game and captures screenshots to verify sync

set -e

echo "🧪 MANUAL MULTIPLAYER SYNC TEST"
echo "================================"
echo ""
echo "This will capture screenshots to verify multiplayer sync."
echo ""

# Clear old logs
> /dev/shm/spatial-worlds.log

echo "📸 Capturing screenshots of multiplayer session..."
echo ""

# Capture initial state
node << 'EOF'
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  console.log('Loading game...');
  await page.goto('https://spatial-worlds-dioni.zocomputer.io', {
    waitUntil: 'domcontentloaded',
    timeout: 15000,
  });

  await new Promise(r => setTimeout(r, 8000));

  console.log('Moving character right for 3 seconds...');
  await page.keyboard.down('ArrowRight');
  await new Promise(r => setTimeout(r, 3000));
  await page.keyboard.up('ArrowRight');

  await new Promise(r => setTimeout(r, 1000));

  await page.screenshot({ path: '/tmp/manual-sync-final.png' });
  console.log('Screenshot saved: /tmp/manual-sync-final.png');

  await browser.close();
})();
EOF

echo ""
echo "📊 Checking server logs for position updates..."
echo ""

if grep -q "position update" /dev/shm/spatial-worlds.log; then
  echo "✅ Server received position data from client"
  grep "position update" /dev/shm/spatial-worlds.log | tail -5
else
  echo "❌ Server did NOT receive position data from client"
  echo "   This means the client is not sending position!"
fi

echo ""
echo "📸 Screenshots saved to /tmp/manual-sync-*.png"
echo ""
echo "✅ Test complete - check screenshots and logs above"
