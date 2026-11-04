import React from "react";
import { AbsoluteFill } from "remotion";
import { PromptBox } from "../components/PromptBox";
import { Shot, Timeline } from "../components/Timeline";
import { spacedWords, WordReveal } from "../components/WordReveal";
import { Card, Center } from "./common";
import { WhooshOnCuts } from "./SoundLayer";

/** Shows every transition in the vocabulary. Render with: npm run render:demo */
export const demoShots: Shot[] = [
  {
    id: "words",
    durationInFrames: 75,
    exit: { type: "zoomOut" },
    render: () => (
      <Center>
        <WordReveal words={spacedWords("No keyframes, no timelines, no all-nighters.")} highlight={["all-nighters."]} />
      </Center>
    ),
  },
  {
    id: "cards",
    durationInFrames: 70,
    exit: { type: "slideLeft" },
    render: () => (
      <Center>
        <div style={{ display: "flex", gap: 48 }}>
          <Card label="Animation" />
          <Card label="Runs it" tone="accent" />
          <Card label="Renders it" />
        </div>
      </Center>
    ),
  },
  {
    id: "prompt",
    durationInFrames: 90,
    exit: { type: "zoomIn" },
    render: () => (
      <Center>
        <PromptBox text="Make a launch video for our new feature." />
      </Center>
    ),
  },
  {
    id: "end",
    durationInFrames: 60,
    exit: { type: "slideRight" },
    render: () => (
      <Center>
        <WordReveal words={spacedWords("Just say it.", 0.1, 0.2)} size={150} highlight={["it."]} />
      </Center>
    ),
  },
  {
    id: "logo",
    durationInFrames: 60,
    render: () => (
      <Center>
        <Card label="Your logo" tone="accent" />
      </Center>
    ),
  },
];

export const TransitionDemo: React.FC = () => (
  <AbsoluteFill>
    <Timeline shots={demoShots} />
    <WhooshOnCuts shots={demoShots} />
  </AbsoluteFill>
);
