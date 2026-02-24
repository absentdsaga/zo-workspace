#!/usr/bin/env bun
/**
 * Convert animated GIF to sprite sheet using ImageMagick
 * 
 * Usage:
 *   bun gif-to-spritesheet.ts --input animation.gif --output spritesheet.png
 */

import { $ } from "bun";

interface ConvertOptions {
  input: string;
  output: string;
  frameWidth?: number;
  frameHeight?: number;
  columns?: number;
  transparent?: boolean;
}

async function gifToSpritesheet(options: ConvertOptions) {
  const {
    input,
    output,
    frameWidth,
    frameHeight,
    columns,
    transparent = true
  } = options;

  console.log(`🎬 Converting GIF to sprite sheet...`);
  console.log(`📥 Input: ${input}`);
  console.log(`📤 Output: ${output}`);

  try {
    // Check if ImageMagick is installed
    await $`which convert`.quiet();
  } catch {
    console.error("❌ ImageMagick not found. Installing...");
    await $`apt install -y imagemagick`;
  }

  try {
    // Get frame count
    const framesOutput = await $`identify ${input}`.text();
    const frameCount = framesOutput.trim().split("\n").length;
    console.log(`🎞️  Found ${frameCount} frames`);

    // Calculate layout
    const cols = columns || Math.ceil(Math.sqrt(frameCount));
    const rows = Math.ceil(frameCount / cols);
    console.log(`📐 Layout: ${cols} columns × ${rows} rows`);

    // Build ImageMagick command
    let cmd = `convert ${input} -coalesce`;
    
    // Apply frame size if specified
    if (frameWidth && frameHeight) {
      cmd += ` -resize ${frameWidth}x${frameHeight}!`;
    }
    
    // Make background transparent
    if (transparent) {
      cmd += ` -background none`;
    }
    
    // Arrange into sprite sheet
    cmd += ` -append +append -crop ${cols}x${rows}@ ${output}`;
    
    console.log(`⚙️  Running: ${cmd}`);
    await $`${cmd.split(" ")}`;

    console.log(`✅ Sprite sheet created successfully!`);
    
    // Show file info
    const stats = await Bun.file(output).exists() ? await $`file ${output}`.text() : null;
    if (stats) {
      console.log(`📊 ${stats.trim()}`);
    }

    // Print usage example
    console.log(`\n📋 Usage in game engine:`);
    console.log(`   Frames: ${frameCount}`);
    console.log(`   Layout: ${cols}x${rows}`);
    if (frameWidth && frameHeight) {
      console.log(`   Frame size: ${frameWidth}x${frameHeight}`);
    }

  } catch (error) {
    console.error(`❌ Conversion failed:`, error);
    process.exit(1);
  }
}

// CLI argument parsing
const args = process.argv.slice(2);
const options: Partial<ConvertOptions> = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, "");
  const value = args[i + 1];
  
  if (key === "frame-width" || key === "frame-height" || key === "columns") {
    options[key.replace("-", "") as keyof ConvertOptions] = parseInt(value);
  } else if (key === "transparent") {
    options.transparent = value === "true";
  } else {
    options[key as keyof ConvertOptions] = value;
  }
}

if (!options.input || !options.output) {
  console.log(`
Usage:
  bun gif-to-spritesheet.ts --input file.gif --output spritesheet.png

Options:
  --input         Input GIF file (required)
  --output        Output sprite sheet (required)
  --frame-width   Frame width in pixels (optional)
  --frame-height  Frame height in pixels (optional)
  --columns       Number of columns (default: auto)
  --transparent   Make background transparent (default: true)

Examples:
  bun gif-to-spritesheet.ts \\
    --input animation.gif \\
    --output spritesheet.png \\
    --frame-width 32 \\
    --frame-height 32

  bun gif-to-spritesheet.ts \\
    --input walk-cycle.gif \\
    --output character-walk.png \\
    --columns 8
  `);
  process.exit(1);
}

await gifToSpritesheet(options as ConvertOptions);
