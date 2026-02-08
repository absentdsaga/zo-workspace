import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

const words = ["Create", "Beautiful", "Motion", "Graphics"];

export const TextReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill className="bg-black flex items-center justify-center">
      <div className="flex gap-4">
        {words.map((word, i) => {
          const delay = i * 8;
          const wordFrame = frame - delay;
          
          const y = spring({
            frame: wordFrame,
            fps,
            config: { damping: 200 },
          });
          
          const opacity = interpolate(wordFrame, [0, 10], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          
          return (
            <span
              key={i}
              style={{
                opacity,
                transform: `translateY(${interpolate(y, [0, 1], [50, 0])})px`,
              }}
              className="text-white text-6xl font-bold"
            >
              {word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
