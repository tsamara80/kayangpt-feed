import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { dbToGain } from "../components/Sfx";
import { Shot, Timeline } from "../components/Timeline";
import { spacedWords, WordReveal } from "../components/WordReveal";
import { project } from "../data/project";
import { Center } from "./common";
import { WhooshOnCuts } from "./SoundLayer";

/**
 * Your video. Claude builds the shot list here from the master prompt
 * (prompts/01-master-prompt.md), one or more shots per script line.
 * Every shot's `exit` names the transition into the next shot.
 */
export const mainShots: Shot[] = [
  {
    id: "placeholder",
    durationInFrames: 90,
    render: () => (
      <Center>
        <WordReveal words={spacedWords("Your SaaS video starts here.")} />
      </Center>
    ),
  },
];

export const Main: React.FC = () => (
  <AbsoluteFill>
    <Timeline shots={mainShots} />
    {project.voiceover ? <Audio src={staticFile(project.voiceover)} volume={dbToGain(project.voiceGainDb)} /> : null}
    <WhooshOnCuts shots={mainShots} />
  </AbsoluteFill>
);
