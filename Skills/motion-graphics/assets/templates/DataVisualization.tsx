/**
 * Data Visualization template
 * Features: Animated bar charts, counters, professional data presentation
 */
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
} from "remotion";

interface DataPoint {
  label: string;
  value: number;
  color?: string;
}

interface DataVisualizationProps {
  title: string;
  data: DataPoint[];
  showValues?: boolean;
}

const AnimatedBar: React.FC<{
  label: string;
  value: number;
  maxValue: number;
  color: string;
  delay: number;
  showValue: boolean;
}> = ({ label, value, maxValue, color, delay, showValue }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const barFrame = frame - delay;
  const progress = spring({
    frame: barFrame,
    fps,
    config: { damping: 200 },
    durationInFrames: 40,
  });

  const width = interpolate(progress, [0, 1], [0, (value / maxValue) * 100]);
  const displayValue = Math.round(interpolate(progress, [0, 1], [0, value]));

  const labelOpacity = interpolate(barFrame, [-10, 0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div className="mb-6">
      <div
        className="flex justify-between mb-2"
        style={{ opacity: labelOpacity }}
      >
        <span className="text-white text-xl font-medium">{label}</span>
        {showValue && (
          <span className="text-white/80 text-xl font-mono">
            {displayValue.toLocaleString()}
          </span>
        )}
      </div>
      <div className="h-12 bg-white/10 rounded-lg overflow-hidden">
        <div
          style={{
            width: `${width}%`,
            backgroundColor: color,
          }}
          className="h-full rounded-lg transition-none"
        />
      </div>
    </div>
  );
};

const AnimatedCounter: React.FC<{ value: number; delay: number }> = ({
  value,
  delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const counterFrame = frame - delay;
  const progress = interpolate(counterFrame, [0, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  const displayValue = Math.round(progress * value);
  const scale = spring({
    frame: counterFrame,
    fps,
    config: { damping: 200 },
  });

  return (
    <span style={{ transform: `scale(${scale})`, display: "inline-block" }}>
      {displayValue.toLocaleString()}
    </span>
  );
};

const defaultColors = [
  "#8B5CF6", // Purple
  "#06B6D4", // Cyan
  "#10B981", // Emerald
  "#F59E0B", // Amber
  "#EF4444", // Red
  "#EC4899", // Pink
];

export const DataVisualization: React.FC<DataVisualizationProps> = ({
  title = "Performance Metrics",
  data = [
    { label: "Revenue", value: 2500000 },
    { label: "Users", value: 150000 },
    { label: "Growth", value: 85 },
  ],
  showValues = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const maxValue = Math.max(...data.map((d) => d.value));
  const staggerDelay = 12;

  // Title animation
  const titleScale = spring({ frame, fps, config: { damping: 200 } });
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Total counter
  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <AbsoluteFill className="bg-gradient-to-br from-slate-900 to-slate-800 p-20">
      {/* Header */}
      <div
        className="mb-16"
        style={{
          transform: `scale(${titleScale})`,
          opacity: titleOpacity,
        }}
      >
        <h1 className="text-white text-6xl font-bold">{title}</h1>
        <div className="text-white/60 text-2xl mt-4">
          Total: <AnimatedCounter value={total} delay={20} />
        </div>
      </div>

      {/* Bars */}
      <div className="flex-1">
        {data.map((item, i) => (
          <AnimatedBar
            key={item.label}
            label={item.label}
            value={item.value}
            maxValue={maxValue}
            color={item.color || defaultColors[i % defaultColors.length]}
            delay={30 + i * staggerDelay}
            showValue={showValues}
          />
        ))}
      </div>

      {/* Footer */}
      <div
        className="text-white/40 text-lg"
        style={{
          opacity: interpolate(frame, [90, 110], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Data as of {new Date().toLocaleDateString()}
      </div>
    </AbsoluteFill>
  );
};
