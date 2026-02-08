import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export const MyComposition: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  const scale = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  return (
    <AbsoluteFill className="bg-gradient-to-br from-purple-900 to-black flex items-center justify-center">
      <div
        style={{
          opacity,
          transform: `scale(${scale})`,
        }}
        className="text-white text-6xl font-bold"
      >
        Motion Graphics Studio
      </div>
    </AbsoluteFill>
  );
};
