/**
 * Logo Reveal template
 * Features: Cinematic entrance, particle effects, glow
 */
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
  random,
} from "remotion";

interface LogoRevealProps {
  logoText: string;
  tagline?: string;
  primaryColor?: string;
  particleCount?: number;
}

interface Particle {
  x: number;
  y: number;
  size: number;
  delay: number;
  duration: number;
}

const Particle: React.FC<{ particle: Particle; color: string }> = ({
  particle,
  color,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const particleFrame = frame - particle.delay;
  const progress = interpolate(
    particleFrame,
    [0, particle.duration],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const opacity = interpolate(
    progress,
    [0, 0.2, 0.8, 1],
    [0, 1, 1, 0]
  );

  const y = interpolate(
    progress,
    [0, 1],
    [particle.y * height, particle.y * height - 200]
  );

  const scale = interpolate(
    progress,
    [0, 0.5, 1],
    [0, 1, 0.5]
  );

  return (
    <div
      style={{
        position: "absolute",
        left: particle.x * width,
        top: y,
        width: particle.size,
        height: particle.size,
        borderRadius: "50%",
        backgroundColor: color,
        opacity,
        transform: `scale(${scale})`,
        boxShadow: `0 0 ${particle.size * 2}px ${color}`,
      }}
    />
  );
};

export const LogoReveal: React.FC<LogoRevealProps> = ({
  logoText = "BRAND",
  tagline = "Innovation Redefined",
  primaryColor = "#8B5CF6",
  particleCount = 30,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();

  // Generate particles
  const particles: Particle[] = Array.from({ length: particleCount }, (_, i) => ({
    x: random(`x-${i}`) * 0.8 + 0.1,
    y: random(`y-${i}`) * 0.4 + 0.5,
    size: random(`size-${i}`) * 8 + 4,
    delay: random(`delay-${i}`) * 40,
    duration: random(`dur-${i}`) * 30 + 40,
  }));

  // Logo animation
  const logoDelay = 30;
  const logoFrame = frame - logoDelay;
  const logoScale = spring({
    frame: logoFrame,
    fps,
    config: { damping: 12 },
  });
  const logoOpacity = interpolate(logoFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Glow pulse
  const glowIntensity = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [40, 80]
  );

  // Tagline
  const taglineDelay = 60;
  const taglineOpacity = interpolate(frame, [taglineDelay, taglineDelay + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const taglineY = spring({
    frame: frame - taglineDelay,
    fps,
    config: { damping: 200 },
  });

  // Exit
  const exitStart = durationInFrames - 30;
  const exitProgress = interpolate(frame, [exitStart, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });

  return (
    <AbsoluteFill className="bg-black overflow-hidden">
      {/* Particles */}
      {particles.map((particle, i) => (
        <Particle key={i} particle={particle} color={primaryColor} />
      ))}

      {/* Radial gradient background */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(circle at center, ${primaryColor}20 0%, transparent 70%)`,
          opacity: interpolate(frame, [0, 50], [0, 1], { extrapolateRight: "clamp" }),
        }}
      />

      {/* Logo */}
      <AbsoluteFill
        className="flex flex-col items-center justify-center"
        style={{ opacity: 1 - exitProgress }}
      >
        <div
          style={{
            transform: `scale(${logoScale * (1 - exitProgress * 0.2)})`,
            opacity: logoOpacity,
            textShadow: `0 0 ${glowIntensity}px ${primaryColor}`,
          }}
          className="text-white text-9xl font-black tracking-widest"
        >
          {logoText}
        </div>

        {tagline && (
          <div
            style={{
              opacity: taglineOpacity,
              transform: `translateY(${interpolate(taglineY, [0, 1], [20, 0])}px)`,
            }}
            className="text-white/70 text-3xl mt-8 tracking-[0.3em] uppercase"
          >
            {tagline}
          </div>
        )}
      </AbsoluteFill>

      {/* Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.8) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
