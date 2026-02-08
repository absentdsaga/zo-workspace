#!/usr/bin/env python3
"""Create a new composition from a template."""

import argparse
import os
import sys
from pathlib import Path

STUDIO_PATH = "/home/workspace/motion-graphics-studio"

TEMPLATES = {
    "basic": '''import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export const {name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1], {{
    extrapolateRight: "clamp",
  }});

  const scale = spring({{
    frame,
    fps,
    config: {{ damping: 200 }},
  }});

  return (
    <AbsoluteFill className="bg-gradient-to-br from-slate-900 to-black flex items-center justify-center">
      <div
        style={{{{
          opacity,
          transform: `scale(${{scale}})`,
        }}}}
        className="text-white text-6xl font-bold"
      >
        {name}
      </div>
    </AbsoluteFill>
  );
}};
''',
    
    "scenes": '''import {{
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Sequence,
}} from "remotion";
import {{ TransitionSeries, linearTiming }} from "@remotion/transitions";
import {{ fade }} from "@remotion/transitions/fade";
import {{ slide }} from "@remotion/transitions/slide";

const Scene1: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();
  const scale = spring({{ frame, fps, config: {{ damping: 200 }} }});
  
  return (
    <AbsoluteFill className="bg-gradient-to-br from-purple-900 to-black flex items-center justify-center">
      <div style={{{{ transform: `scale(${{scale}})` }}}} className="text-white text-5xl font-bold">
        Scene 1
      </div>
    </AbsoluteFill>
  );
}};

const Scene2: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();
  const scale = spring({{ frame, fps, config: {{ damping: 200 }} }});
  
  return (
    <AbsoluteFill className="bg-gradient-to-br from-blue-900 to-black flex items-center justify-center">
      <div style={{{{ transform: `scale(${{scale}})` }}}} className="text-white text-5xl font-bold">
        Scene 2
      </div>
    </AbsoluteFill>
  );
}};

const Scene3: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();
  const scale = spring({{ frame, fps, config: {{ damping: 200 }} }});
  
  return (
    <AbsoluteFill className="bg-gradient-to-br from-emerald-900 to-black flex items-center justify-center">
      <div style={{{{ transform: `scale(${{scale}})` }}}} className="text-white text-5xl font-bold">
        Scene 3
      </div>
    </AbsoluteFill>
  );
}};

export const {name}: React.FC = () => {{
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={{90}}>
        <Scene1 />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={{slide({{ direction: "from-right" }})}}
        timing={{linearTiming({{ durationInFrames: 15 }})}}
      />
      <TransitionSeries.Sequence durationInFrames={{90}}>
        <Scene2 />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={{fade()}}
        timing={{linearTiming({{ durationInFrames: 15 }})}}
      />
      <TransitionSeries.Sequence durationInFrames={{90}}>
        <Scene3 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
}};
''',

    "text-reveal": '''import {{
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
}} from "remotion";

const words = ["Create", "Beautiful", "Motion", "Graphics"];

export const {name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();

  return (
    <AbsoluteFill className="bg-black flex items-center justify-center">
      <div className="flex gap-4">
        {{words.map((word, i) => {{
          const delay = i * 8;
          const wordFrame = frame - delay;
          
          const y = spring({{
            frame: wordFrame,
            fps,
            config: {{ damping: 200 }},
          }});
          
          const opacity = interpolate(wordFrame, [0, 10], [0, 1], {{
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }});
          
          return (
            <span
              key={{i}}
              style={{{{
                opacity,
                transform: `translateY(${{interpolate(y, [0, 1], [50, 0])}})px`,
              }}}}
              className="text-white text-6xl font-bold"
            >
              {{word}}
            </span>
          );
        }})}}
      </div>
    </AbsoluteFill>
  );
}};
''',

    "counter": '''import {{
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
}} from "remotion";

interface Props {{
  from?: number;
  to?: number;
}}

export const {name}: React.FC<Props> = ({{ from = 0, to = 100 }}) => {{
  const frame = useCurrentFrame();
  const {{ fps, durationInFrames }} = useVideoConfig();

  const progress = interpolate(
    frame,
    [0, durationInFrames - 30],
    [0, 1],
    {{
      easing: Easing.inOut(Easing.quad),
      extrapolateRight: "clamp",
    }}
  );

  const value = Math.round(interpolate(progress, [0, 1], [from, to]));

  return (
    <AbsoluteFill className="bg-gradient-to-br from-indigo-900 to-black flex items-center justify-center">
      <div className="text-center">
        <div className="text-white text-9xl font-bold tabular-nums">
          {{value.toLocaleString()}}
        </div>
        <div className="text-white/60 text-2xl mt-4">
          Units processed
        </div>
      </div>
    </AbsoluteFill>
  );
}};
''',
}

def main():
    parser = argparse.ArgumentParser(description="Create a new Remotion composition")
    parser.add_argument("name", help="Name of the composition (PascalCase)")
    parser.add_argument("--template", "-t", default="basic", choices=list(TEMPLATES.keys()), 
                       help="Template to use")
    parser.add_argument("--duration", "-d", type=int, default=150, help="Duration in frames")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--width", "-w", type=int, default=1920, help="Width in pixels")
    parser.add_argument("--height", "-H", type=int, default=1080, help="Height in pixels")
    
    args = parser.parse_args()
    
    # Create component file
    src_path = Path(STUDIO_PATH) / "src"
    comp_path = src_path / f"{args.name}.tsx"
    
    if comp_path.exists():
        print(f"Error: {comp_path} already exists")
        sys.exit(1)
    
    template = TEMPLATES[args.template].format(name=args.name)
    
    with open(comp_path, "w") as f:
        f.write(template)
    
    print(f"Created: {comp_path}")
    
    # Add to Root.tsx
    root_path = src_path / "Root.tsx"
    with open(root_path) as f:
        content = f.read()
    
    # Add import
    import_line = f'import {{ {args.name} }} from "./{args.name}";\n'
    if import_line not in content:
        # Find last import and add after it
        import_end = content.rfind("import")
        import_end = content.find("\n", import_end) + 1
        content = content[:import_end] + import_line + content[import_end:]
    
    # Add composition
    comp_jsx = f'''
      <Composition
        id="{args.name}"
        component={{{args.name}}}
        durationInFrames={{{args.duration}}}
        fps={{{args.fps}}}
        width={{{args.width}}}
        height={{{args.height}}}
      />'''
    
    # Find closing </> and insert before it
    close_tag = content.rfind("</>")
    content = content[:close_tag] + comp_jsx + "\n      " + content[close_tag:]
    
    with open(root_path, "w") as f:
        f.write(content)
    
    print(f"Registered in: {root_path}")
    print()
    print(f"✅ Created composition '{args.name}'")
    print(f"   Template: {args.template}")
    print(f"   Duration: {args.duration} frames ({args.duration / args.fps:.1f}s)")
    print(f"   Resolution: {args.width}x{args.height}")
    print()
    print(f"Preview with: bun run dev")
    print(f"Render with:  bun run render {args.name} --output out/{args.name}.mp4")

if __name__ == "__main__":
    main()
