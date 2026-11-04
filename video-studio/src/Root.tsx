import React from "react";
import { Composition } from "remotion";
import { totalFrames } from "./components/Timeline";
import { demoShots, TransitionDemo } from "./scenes/demo";
import { Main, mainShots } from "./scenes/main";
import { VIDEO } from "./style/theme";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Main" component={Main} durationInFrames={totalFrames(mainShots)} {...VIDEO} />
    <Composition id="TransitionDemo" component={TransitionDemo} durationInFrames={totalFrames(demoShots)} {...VIDEO} />
  </>
);
