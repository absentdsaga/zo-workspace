import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 200 } });
  
  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #7c3aed 0%, #000 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          color: "white",
          fontSize: 80,
          fontWeight: "bold",
          fontFamily: "sans-serif",
        }}
      >
        Scene 1
      </div>
    </AbsoluteFill>
  );
};

const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 200 } });
  
  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #1e40af 0%, #000 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          color: "white",
          fontSize: 80,
          fontWeight: "bold",
          fontFamily: "sans-serif",
        }}
      >
        Scene 2
      </div>
    </AbsoluteFill>
  );
};

const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 200 } });
  
  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #047857 0%, #000 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          color: "white",
          fontSize: 80,
          fontWeight: "bold",
          fontFamily: "sans-serif",
        }}
      >
        Scene 3
      </div>
    </AbsoluteFill>
  );
};

export const MyVideo: React.FC = () => {
  return (
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
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />
      <TransitionSeries.Sequence durationInFrames={90}>
        <Scene3 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
