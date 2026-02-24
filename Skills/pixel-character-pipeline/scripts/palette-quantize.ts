#!/usr/bin/env bun
/**
 * Reduce image colors to retro palette using ImageMagick
 * 
 * Usage:
 *   bun palette-quantize.ts --input sprite.png --colors 16 --output sprite-16bit.png
 */

import { $ } from "bun";

interface QuantizeOptions {
  input: string;
  output: string;
  colors?: number;
  dither?: boolean;
  palette?: string;
}

const PRESET_PALETTES: Record<string, string[]> = {
  "nes": [
    "#000000", "#FFFFFF", "#7C7C7C", "#BCBCBC", 
    "#F87858", "#FCA044", "#F8B800", "#B8F818",
    "#00B800", "#00A844", "#00A8F8", "#0078F8",
    "#F878F8", "#F83800", "#A8000", "#501800"
  ],
  "gameboy": [
    "#0f380f", "#306230", "#8bac0f", "#9bbc0f"
  ],
  "c64": [
    "#000000", "#FFFFFF", "#68372B", "#70A4B2",
    "#6F3D86", "#588D43", "#352879", "#B8C76F",
    "#6F4F25", "#433900", "#9A6759", "#444444",
    "#6C6C6C", "#9AD284", "#6C5EB5", "#959595"
  ],
};

async function quantizePalette(options: QuantizeOptions) {
  const {
    input,
    output,
    colors = 16,
    dither = false,
    palette
  } = options;

  console.log(`🎨 Quantizing palette...`);
  console.log(`📥 Input: ${input}`);
  console.log(`🎯 Target colors: ${colors}`);
  console.log(`📤 Output: ${output}`);

  try {
    // Check if ImageMagick is installed
    await $`which convert`.quiet();
  } catch {
    console.error("❌ ImageMagick not found. Installing...");
    await $`apt install -y imagemagick`;
  }

  try {
    let cmd: string;

    if (palette && PRESET_PALETTES[palette]) {
      // Use preset palette
      const paletteColors = PRESET_PALETTES[palette];
      console.log(`🎨 Using preset palette: ${palette} (${paletteColors.length} colors)`);
      
      // Create temporary palette image
      const paletteFile = `/tmp/palette-${Date.now()}.png`;
      const paletteCmd = `convert -size 1x${paletteColors.length} xc: ${paletteColors.map((c, i) => `-fill "${c}" -draw "point 0,${i}"`).join(" ")} ${paletteFile}`;
      await $`sh -c ${paletteCmd}`;
      
      // Remap to palette
      const ditherFlag = dither ? "" : "+dither";
      cmd = `convert ${input} ${ditherFlag} -remap ${paletteFile} ${output}`;
      
    } else {
      // Quantize to N colors
      const ditherFlag = dither ? "-dither FloydSteinberg" : "+dither";
      cmd = `convert ${input} ${ditherFlag} -colors ${colors} ${output}`;
    }

    console.log(`⚙️  Processing...`);
    await $`sh -c ${cmd}`;

    console.log(`✅ Palette quantized successfully!`);
    
    // Analyze result
    const colorsOutput = await $`identify -format "%k" ${output}`.text();
    const actualColors = parseInt(colorsOutput.trim());
    console.log(`📊 Actual colors in output: ${actualColors}`);

    // File size comparison
    const inputStats = await $`stat -c%s ${input}`.text();
    const outputStats = await $`stat -c%s ${output}`.text();
    const inputSize = parseInt(inputStats.trim());
    const outputSize = parseInt(outputStats.trim());
    const savings = ((inputSize - outputSize) / inputSize * 100).toFixed(1);
    
    console.log(`💾 Size: ${inputSize} → ${outputSize} bytes (${savings}% smaller)`);

  } catch (error) {
    console.error(`❌ Quantization failed:`, error);
    process.exit(1);
  }
}

// CLI argument parsing
const args = process.argv.slice(2);
const options: Partial<QuantizeOptions> = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, "");
  const value = args[i + 1];
  
  if (key === "colors") {
    options.colors = parseInt(value);
  } else if (key === "dither") {
    options.dither = value === "true";
  } else {
    options[key as keyof QuantizeOptions] = value;
  }
}

if (!options.input || !options.output) {
  console.log(`
Usage:
  bun palette-quantize.ts --input sprite.png --output sprite-reduced.png

Options:
  --input     Input image (required)
  --output    Output image (required)
  --colors    Number of colors (default: 16)
  --dither    Use Floyd-Steinberg dithering (default: false)
  --palette   Use preset palette: nes, gameboy, c64

Examples:
  # Reduce to 16 colors
  bun palette-quantize.ts \\
    --input character.png \\
    --colors 16 \\
    --output character-16.png

  # Use Game Boy palette
  bun palette-quantize.ts \\
    --input sprite.png \\
    --palette gameboy \\
    --output sprite-gb.png

  # Use NES palette with dithering
  bun palette-quantize.ts \\
    --input background.png \\
    --palette nes \\
    --dither true \\
    --output background-nes.png

Available palettes: ${Object.keys(PRESET_PALETTES).join(", ")}
  `);
  process.exit(1);
}

await quantizePalette(options as QuantizeOptions);
