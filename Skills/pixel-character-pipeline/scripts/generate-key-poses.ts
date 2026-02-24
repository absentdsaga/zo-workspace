#!/usr/bin/env bun
/**
 * Generate pixel art key poses using Scenario.com free tier API
 * 
 * Usage:
 *   bun generate-key-poses.ts --character "pixel art warrior" --output warrior-idle.png
 */

const SCENARIO_API_KEY = process.env.SCENARIO_API_KEY;

interface GenerateOptions {
  character: string;
  style?: string;
  size?: string;
  output: string;
  model?: string;
}

async function generateKeyPose(options: GenerateOptions) {
  if (!SCENARIO_API_KEY) {
    console.error("❌ SCENARIO_API_KEY not found in environment");
    console.error("Add it at: /?t=settings&s=developers");
    process.exit(1);
  }

  const {
    character,
    style = "snes rpg, 16-bit pixel art, chrono trigger style",
    size = "32x32",
    output,
    model = "pixel-art-xl"
  } = options;

  const prompt = `${character}, ${size} resolution, ${style}, clean background, centered, game sprite`;

  console.log(`🎨 Generating: ${prompt}`);
  console.log(`📦 Model: ${model}`);
  console.log(`💾 Output: ${output}`);

  try {
    // Scenario.com API endpoint
    const response = await fetch("https://api.scenario.com/v1/models/inference", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${SCENARIO_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        modelId: model,
        parameters: {
          prompt: prompt,
          negativePrompt: "blurry, low quality, 3d, realistic, photo, watermark",
          numSamples: 1,
          width: parseInt(size.split("x")[0]),
          height: parseInt(size.split("x")[1]),
          guidance: 7.5,
          scheduler: "euler_a",
        }
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API error: ${response.status} ${error}`);
    }

    const result = await response.json();
    
    // Download the generated image
    const imageUrl = result.inference.images[0].url;
    const imageResponse = await fetch(imageUrl);
    const imageBuffer = await imageResponse.arrayBuffer();
    
    // Save to file
    await Bun.write(output, Buffer.from(imageBuffer));
    
    console.log(`✅ Generated successfully!`);
    console.log(`🔗 Image URL: ${imageUrl}`);
    console.log(`💳 Credits used: ~${result.inference.parameters.numSamples || 1}`);
    
    return output;
    
  } catch (error) {
    console.error(`❌ Generation failed:`, error);
    process.exit(1);
  }
}

// CLI argument parsing
const args = process.argv.slice(2);
const options: Partial<GenerateOptions> = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, "");
  const value = args[i + 1];
  options[key as keyof GenerateOptions] = value;
}

if (!options.character || !options.output) {
  console.log(`
Usage:
  bun generate-key-poses.ts --character "description" --output file.png

Options:
  --character   Character description (required)
  --output      Output filename (required)
  --style       Art style (default: "snes rpg, 16-bit pixel art")
  --size        Image size (default: "32x32")
  --model       Scenario model ID (default: "pixel-art-xl")

Examples:
  bun generate-key-poses.ts \\
    --character "pixel art mage, blue robes, staff, idle pose" \\
    --output Assets/mage-idle.png

  bun generate-key-poses.ts \\
    --character "pixel art knight, armor, sword, walking" \\
    --style "final fantasy tactics style" \\
    --size "48x48" \\
    --output Assets/knight-walk.png
  `);
  process.exit(1);
}

await generateKeyPose(options as GenerateOptions);
