import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { TextReveal } from "./TextReveal";
import { MyVideo } from "./MyVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyComp"
        component={MyComposition}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
    
      <Composition
        id="TextReveal"
        component={TextReveal}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      
      <Composition
        id="MyVideo"
        component={MyVideo}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
      </>
  );
};
