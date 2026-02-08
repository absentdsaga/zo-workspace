/**
 * Social Media Promo template (1080x1080 square format)
 * Features: Bold typography, eye-catching colors, fast pacing
 */
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Sequence,
  Easing,
} from "remotion";

interface SocialPromoProps {
  headline: string;
  subheadline?: string;
  callToAction: string;
  gradientFrom?: string;
  gradientTo?: string;
}

const Letter: React.FC<{ char: string; delay: number }> = ({ char, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const letterFrame = frame - delay;
  const scale = spring({
    frame: letterFrame,
    fps,
    config: { damping: 12, stiffness: 200 },
  });
  const opacity = interpolate(letterFrame, [0, 5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <span
      style={{
        display: "inline-block",
        transform: `scale(${Math.max(0, scale)})`,
        opacity: Math.max(0, opacity),
      }}
    >
      {char === " " ? "\u00A0" : char}
    </span>
  );
};

const AnimatedText: React.FC<{ text: string; startDelay?: number; stagger?: number }> = ({
  text,
  startDelay = 0,
  stagger = 2,
}) => {
  return (
    <div className="flex flex-wrap justify-center">
      {text.split("").map((char, i) => (
        <Letter key={i} char={char} delay={startDelay + i * stagger} />
      ))}
    </div>
  );
};

export const SocialPromo: React.FC<SocialPromoProps> = ({
  headline = "BIG NEWS",
  subheadline = "Something amazing is coming",
  callToAction = "Learn More →",
  gradientFrom = "#FF6B6B",
  gradientTo = "#4ECDC4",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Background pulse
  const pulse = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [0.95, 1.05]
  );

  // CTA animation
  const ctaDelay = 60;
  const ctaOpacity = interpolate(frame, [ctaDelay, ctaDelay + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ctaY = spring({
    frame: frame - ctaDelay,
    fps,
    config: { damping: 200 },
  });

  // Exit animation
  const exitStart = durationInFrames - 20;
  const exitProgress = interpolate(frame, [exitStart, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${gradientFrom} 0%, ${gradientTo} 100%)`,
        transform: `scale(${pulse * (1 - exitProgress * 0.1)})`,
        opacity: 1 - exitProgress,
      }}
      className="flex flex-col items-center justify-center p-16"
    >
      {/* Headline */}
      <div className="text-white text-7xl font-black text-center tracking-tight drop-shadow-lg">
        <AnimatedText text={headline} startDelay={0} stagger={3} />
      </div>

      {/* Subheadline */}
      {subheadline && (
        <div className="text-white/90 text-3xl mt-8 text-center font-medium">
          <AnimatedText text={subheadline} startDelay={30} stagger={2} />
        </div>
      )}

      {/* CTA */}
      <div
        style={{
          opacity: ctaOpacity,
          transform: `translateY(${interpolate(ctaY, [0, 1], [30, 0])}px)`,
        }}
        className="mt-12 bg-white text-black px-12 py-4 rounded-full text-2xl font-bold shadow-xl"
      >
        {callToAction}
      </div>
    </AbsoluteFill>
  );
};
