---
name: motion-graphics
description: Create professional motion graphics and animated videos using Remotion. Use this skill when the user wants to create animated videos, motion graphics, product demos, social media videos, explainer videos, or any programmatic video content.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  tags: remotion, video, motion-graphics, animation, react
---
## Overview

This skill enables pro-level motion graphics creation using Remotion — a React-based video creation framework. Videos are created programmatically, giving you precise control over every frame.

## Project Location

The Remotion studio is at `/home/workspace/motion-graphics-studio/`. All compositions live in `/home/workspace/motion-graphics-studio/src/`.

## Quick Start

### 1. Start the Studio (for preview)
```bash
cd /home/workspace/motion-graphics-studio && bun run dev
```
This starts the Remotion Studio at http://localhost:3000 for live preview.

### 2. Render a Video
```bash
cd /home/workspace/motion-graphics-studio && bun run render MyComp --output out/video.mp4
```

## Core Concepts

### Animation Rules (CRITICAL)
- **ALL animations MUST use `useCurrentFrame()` hook** — CSS animations/transitions are FORBIDDEN
- Use `interpolate()` for linear animations, `spring()` for natural motion
- Always think in frames: `seconds * fps = frames`

### Basic Animation Pattern
```tsx
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

export const MyAnimation = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in over 1 second
  const opacity = interpolate(frame, [0, fps], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Spring scale
  const scale = spring({ frame, fps, config: { damping: 200 } });

  return <div style={{ opacity, transform: `scale(${scale})` }}>Hello</div>;
};
```

### Spring Configs (use these for pro-level motion)
```tsx
const smooth = { damping: 200 };           // Smooth, no bounce
const snappy = { damping: 20, stiffness: 200 }; // Snappy UI elements
const bouncy = { damping: 8 };             // Playful bounce
const heavy = { damping: 15, stiffness: 80, mass: 2 }; // Heavy, slow
```

## Creating New Compositions

### 1. Create Component
Create a new file in `src/`, e.g., `src/ProductDemo.tsx`:

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const ProductDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  
  // Your animation logic here
  
  return (
    <AbsoluteFill className="bg-black flex items-center justify-center">
      {/* Your content */}
    </AbsoluteFill>
  );
};
```

### 2. Register in Root.tsx
Add to `src/Root.tsx`:

```tsx
import { ProductDemo } from "./ProductDemo";

// Inside RemotionRoot:
<Composition
  id="ProductDemo"
  component={ProductDemo}
  durationInFrames={300} // 10 seconds at 30fps
  fps={30}
  width={1920}
  height={1080}
/>
```

## Pro Techniques

### Scene Transitions
```tsx
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}>
    <Scene1 />
  </TransitionSeries.Sequence>
  <TransitionSeries.Transition
    presentation={slide({ direction: "from-right" })}
    timing={linearTiming({ durationInFrames: 15 })}
  />
  <TransitionSeries.Sequence durationInFrames={90}>
    <Scene2 />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

### Light Leaks (cinematic overlays)
```tsx
import { LightLeak } from "@remotion/light-leaks";

<TransitionSeries.Overlay durationInFrames={30}>
  <LightLeak />
</TransitionSeries.Overlay>
```

### Staggered Animations
```tsx
const items = ["One", "Two", "Three"];
const staggerDelay = 10; // frames between each item

{items.map((item, i) => {
  const itemFrame = frame - i * staggerDelay;
  const scale = spring({ frame: itemFrame, fps, config: { damping: 200 } });
  
  return (
    <div key={i} style={{ transform: `scale(${Math.max(0, scale)})` }}>
      {item}
    </div>
  );
})}
```

### Exit Animations
```tsx
const { durationInFrames } = useVideoConfig();
const exitStart = durationInFrames - 30; // Start exit 1 second before end

const exitProgress = spring({
  frame,
  fps,
  delay: exitStart,
  config: { damping: 200 },
});

const scale = 1 - exitProgress; // Scale from 1 to 0
```

## Reference Documentation

Detailed rules for specific features are in `references/remotion-rules/`:
- `animations.md` — Core animation principles
- `timing.md` — Interpolation, springs, easing
- `transitions.md` — Scene transitions
- `text-animations.md` — Typography effects
- `audio.md` — Audio integration
- `videos.md` — Video embedding
- `charts.md` — Data visualization
- `3d.md` — Three.js integration

## Scripts

### Preview
```bash
python3 /home/workspace/Skills/motion-graphics/scripts/preview.py
```

### Render
```bash
python3 /home/workspace/Skills/motion-graphics/scripts/render.py <composition-id> [output-path]
```

### List Compositions
```bash
python3 /home/workspace/Skills/motion-graphics/scripts/list-compositions.py
```

## Output Formats

- **MP4** (default): Best for sharing, social media
- **WebM**: Smaller file size, web optimized
- **GIF**: For short loops
- **PNG Sequence**: For compositing in other software

Specify format with `--codec`:
```bash
bun run render MyComp --output out/video.webm --codec vp8
```

## Common Resolutions

| Format | Width | Height | Use Case |
|--------|-------|--------|----------|
| 1080p | 1920 | 1080 | Standard HD |
| 4K | 3840 | 2160 | High quality |
| Square | 1080 | 1080 | Instagram |
| Portrait | 1080 | 1920 | TikTok, Stories |
| Twitter | 1280 | 720 | Twitter video |

## Tips for Pro-Level Results

1. **Use spring() for all entrances/exits** — Linear motion looks robotic
2. **Stagger everything** — Never have multiple elements animate at exactly the same time
3. **Add micro-animations** — Subtle movement keeps videos alive
4. **Use easing on interpolate()** — `Easing.inOut(Easing.quad)` for smooth motion
5. **Match your fps to content** — 30fps for motion graphics, 60fps for smooth UI demos
6. **Keep transitions short** — 10-20 frames (0.3-0.6s) feels snappy
7. **Use light leaks sparingly** — One or two per video for cinematic feel
