#!/usr/bin/env bun
/**
 * Batch generate multiple character key poses
 * 
 * Usage:
 *   bun batch-generate.ts --config characters.json --output-dir Assets/key-poses/
 */

import { $ } from "bun";

interface Character {
  name: string;
  description: string;
  style?: string;
  size?: string;
}

interface BatchOptions {
  config: string;
  outputDir: string;
  delay?: number; // Delay between requests to avoid rate limiting
}

async function batchGenerate(options: BatchOptions) {
  const { config, outputDir, delay = 2000 } = options;

  console.log(`📦 Batch generating characters...`);
  console.log(`📋 Config: ${config}`);
  console.log(`📁 Output: ${outputDir}`);

  // Read config file
  let characters: Character[];
  try {
    const configFile = Bun.file(config);
    const configText = await configFile.text();
    characters = JSON.parse(configText);
  } catch (error) {
    console.error(`❌ Failed to read config file: ${error}`);
    process.exit(1);
  }

  console.log(`👥 Found ${characters.length} characters to generate`);

  // Create output directory
  await $`mkdir -p ${outputDir}`;

  const results: Array<{ name: string; status: string; output?: string }> = [];

  // Generate each character
  for (let i = 0; i < characters.length; i++) {
    const char = characters[i];
    console.log(`\n[${i + 1}/${characters.length}] Generating: ${char.name}`);

    const outputFile = `${outputDir}/${char.name.toLowerCase().replace(/\s+/g, "-")}.png`;

    try {
      // Build command
      const args = [
        "scripts/generate-key-poses.ts",
        "--character", char.description,
        "--output", outputFile
      ];

      if (char.style) {
        args.push("--style", char.style);
      }

      if (char.size) {
        args.push("--size", char.size);
      }

      // Run generation
      await $`bun ${args}`;

      results.push({
        name: char.name,
        status: "✅ Success",
        output: outputFile
      });

      console.log(`✅ ${char.name} generated successfully`);

    } catch (error) {
      console.error(`❌ Failed to generate ${char.name}:`, error);
      results.push({
        name: char.name,
        status: "❌ Failed"
      });
    }

    // Delay between requests
    if (i < characters.length - 1) {
      console.log(`⏱️  Waiting ${delay}ms before next request...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  // Print summary
  console.log(`\n📊 Batch Generation Summary`);
  console.log(`─`.repeat(60));
  
  const successful = results.filter(r => r.status.includes("Success")).length;
  const failed = results.filter(r => r.status.includes("Failed")).length;

  results.forEach(r => {
    console.log(`${r.status} ${r.name}`);
    if (r.output) {
      console.log(`   → ${r.output}`);
    }
  });

  console.log(`─`.repeat(60));
  console.log(`✅ Successful: ${successful}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`💳 Estimated credits used: ${successful}`);
}

// CLI argument parsing
const args = process.argv.slice(2);
const options: Partial<BatchOptions> = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, "");
  const value = args[i + 1];
  
  if (key === "delay") {
    options.delay = parseInt(value);
  } else if (key === "output-dir") {
    options.outputDir = value;
  } else {
    options[key as keyof BatchOptions] = value;
  }
}

if (!options.config || !options.outputDir) {
  console.log(`
Usage:
  bun batch-generate.ts --config file.json --output-dir path/

Options:
  --config      JSON config file with character definitions (required)
  --output-dir  Output directory for generated images (required)
  --delay       Delay between requests in ms (default: 2000)

Config File Format:
  [
    {
      "name": "Warrior",
      "description": "pixel art warrior, red armor, sword, idle stance",
      "style": "snes rpg, chrono trigger style",
      "size": "32x32"
    },
    {
      "name": "Mage",
      "description": "pixel art mage, blue robes, staff, idle stance",
      "size": "32x32"
    }
  ]

Example:
  bun batch-generate.ts \\
    --config characters.json \\
    --output-dir Assets/key-poses/ \\
    --delay 3000
  `);
  process.exit(1);
}

await batchGenerate(options as BatchOptions);
