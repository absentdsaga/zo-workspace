#!/usr/bin/env python3
"""
Video recording script for reviewing web builds
Records gameplay/interaction with WebGL support
"""
import asyncio
import sys
from playwright.async_api import async_playwright
from pathlib import Path

async def record_gameplay(url: str, duration: int = 10, output_path: str = None):
    """
    Record video of gameplay with WebGL support
    
    Args:
        url: URL to record
        duration: Recording duration in seconds
        output_path: Output video path (default: auto-generated)
    """
    if output_path is None:
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')
        output_dir = Path('/home/.z/workspaces/previews/videos')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f'gameplay-{timestamp}.webm')
    
    print(f"🎥 Recording {url} for {duration}s with WebGL support...")
    
    async with async_playwright() as p:
        # Launch with WebGL support (same flags as our tests)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--use-angle=swiftshader',
                '--use-gl=angle',
            ]
        )
        
        # Create context with video recording
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir=str(Path(output_path).parent),
            record_video_size={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        # Navigate to the game
        await page.goto(url, wait_until='networkidle')
        print("✓ Page loaded")
        
        # Wait for game to initialize
        await asyncio.sleep(2)
        print("✓ Game initialized")
        
        # Simulate some movement to show multiplayer sync
        print("🎮 Simulating gameplay...")
        
        # Move right for 2 seconds
        await page.keyboard.down('d')
        await asyncio.sleep(2)
        await page.keyboard.up('d')
        
        # Move down for 2 seconds
        await page.keyboard.down('s')
        await asyncio.sleep(2)
        await page.keyboard.up('s')
        
        # Move up-left for 2 seconds
        await page.keyboard.down('w')
        await page.keyboard.down('a')
        await asyncio.sleep(2)
        await page.keyboard.up('w')
        await page.keyboard.up('a')
        
        # Wait a bit more
        await asyncio.sleep(2)
        
        print("✓ Recording complete")
        
        # Close page and context to save video
        await page.close()
        video_path = await page.video.path()
        await context.close()
        await browser.close()
        
        # Move video to final location
        import shutil
        shutil.move(video_path, output_path)
        
        print(f"✓ Video saved: {output_path}")
        return output_path

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    output = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = asyncio.run(record_gameplay(url, duration, output))
    print(f"\n📹 Video: {result}")
