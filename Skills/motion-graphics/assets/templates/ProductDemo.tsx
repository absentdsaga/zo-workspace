/**
 * Pro-level Product Demo template
 * Features: Staggered reveals, smooth transitions, professional pacing
 */
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Img,
  staticFile,
  Easing,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";

interface ProductDemoProps {
  productName: string;
  tagline: string;
  features: string[];
  productImage?: string;
  primaryColor?: string;
  accentColor?: string;
}

const IntroScene: React.FC<{ productName: string; tagline: string; primaryColor: string }> = ({
  productName,
  tagline,
  primaryColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({ frame, fps, config: { damping: 200 } });
  const taglineOpacity = interpolate(frame, [20, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const taglineY = interpolate(frame, [20, 40], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{ background: `linear-gradient(135deg, ${primaryColor} 0%, #000 100%)` }}
      className="flex flex-col items-center justify-center"
    >
      <div
        style={{ transform: `scale(${logoScale})` }}
        className="text-white text-8xl font-black tracking-tight"
      >
        {productName}
      </div>
      <div
        style={{ opacity: taglineOpacity, transform: `translateY(${taglineY}px)` }}
        className="text-white/80 text-3xl mt-6 font-light"
      >
        {tagline}
      </div>
    </AbsoluteFill>
  );
};

const FeatureScene: React.FC<{ feature: string; index: number; primaryColor: string }> = ({
  feature,
  index,
  primaryColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const numberScale = spring({ frame, fps, config: { damping: 12 } });
  const textOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const textX = interpolate(frame, [15, 30], [-30, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill className="bg-black flex items-center justify-center">
      <div className="flex items-center gap-12">
        <div
          style={{
            transform: `scale(${numberScale})`,
            color: primaryColor,
          }}
          className="text-[200px] font-black opacity-20"
        >
          {String(index + 1).padStart(2, "0")}
        </div>
        <div
          style={{ opacity: textOpacity, transform: `translateX(${textX}px)` }}
          className="text-white text-5xl font-bold max-w-xl"
        >
          {feature}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const OutroScene: React.FC<{ productName: string; primaryColor: string }> = ({
  productName,
  primaryColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 200 } });
  const glowOpacity = interpolate(
    frame,
    [0, durationInFrames],
    [0.5, 1],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{ background: `linear-gradient(135deg, #000 0%, ${primaryColor} 100%)` }}
      className="flex flex-col items-center justify-center"
    >
      <div
        style={{
          transform: `scale(${scale})`,
          textShadow: `0 0 60px ${primaryColor}`,
          opacity: glowOpacity,
        }}
        className="text-white text-9xl font-black"
      >
        {productName}
      </div>
      <div
        style={{ opacity: interpolate(frame, [30, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}
        className="text-white/60 text-2xl mt-8"
      >
        Available Now
      </div>
    </AbsoluteFill>
  );
};

export const ProductDemo: React.FC<ProductDemoProps> = ({
  productName = "Product",
  tagline = "The future is here",
  features = ["Lightning Fast", "Beautiful Design", "Secure by Default"],
  primaryColor = "#8B5CF6",
  accentColor = "#06B6D4",
}) => {
  const sceneDuration = 90;
  const transitionDuration = 15;

  return (
    <TransitionSeries>
      {/* Intro */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <IntroScene productName={productName} tagline={tagline} primaryColor={primaryColor} />
      </TransitionSeries.Sequence>

      {/* Features */}
      {features.map((feature, i) => (
        <>
          <TransitionSeries.Transition
            key={`trans-${i}`}
            presentation={slide({ direction: "from-right" })}
            timing={linearTiming({ durationInFrames: transitionDuration })}
          />
          <TransitionSeries.Sequence key={`scene-${i}`} durationInFrames={sceneDuration}>
            <FeatureScene feature={feature} index={i} primaryColor={primaryColor} />
          </TransitionSeries.Sequence>
        </>
      ))}

      {/* Outro */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <OutroScene productName={productName} primaryColor={primaryColor} />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
