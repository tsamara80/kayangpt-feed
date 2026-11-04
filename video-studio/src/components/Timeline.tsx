import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { enterTransform, exitTransform, TransitionSpec, transitionFrames } from "../lib/transitions";
import { theme } from "../style/theme";

export type Shot = {
  id: string;
  /** Length of the shot in frames (including its transition frames). */
  durationInFrames: number;
  /** How this shot leaves. The next shot enters with the same transition. */
  exit?: TransitionSpec;
  render: () => React.ReactNode;
};

const ShotFrame: React.FC<{ shot: Shot; enter?: TransitionSpec }> = ({ shot, enter }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const inFrames = transitionFrames(enter);
  const outFrames = transitionFrames(shot.exit);

  let scale = 1;
  let x = 0;
  if (inFrames > 0 && frame < inFrames) {
    // +1 so the first frame after the cut is already moving at peak speed
    const t = enterTransform(enter, (frame + 1) / inFrames, width);
    scale *= t.scale;
    x += t.x;
  }
  const outStart = shot.durationInFrames - outFrames;
  if (outFrames > 0 && frame >= outStart) {
    const t = exitTransform(shot.exit, (frame - outStart + 1) / outFrames, width);
    scale *= t.scale;
    x += t.x;
  }

  return (
    <AbsoluteFill style={{ backgroundColor: theme.background, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `translateX(${x}px) scale(${scale})`, transformOrigin: "50% 50%" }}>
        {shot.render()}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Back-to-back shots with hard cuts. No overlap, so scenes never blend. */
export const Timeline: React.FC<{ shots: Shot[] }> = ({ shots }) => {
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: theme.background }}>
      {shots.map((shot, i) => {
        const start = from;
        from += shot.durationInFrames;
        return (
          <Sequence key={shot.id} from={start} durationInFrames={shot.durationInFrames} name={shot.id}>
            <ShotFrame shot={shot} enter={shots[i - 1]?.exit} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const totalFrames = (shots: Shot[]) => shots.reduce((n, s) => n + s.durationInFrames, 0);

/** Frame numbers of every moving cut, for placing whooshes. */
export const cutFrames = (shots: Shot[]) => {
  const cuts: { frame: number; type: string }[] = [];
  let from = 0;
  for (const s of shots) {
    from += s.durationInFrames;
    if (s.exit && s.exit.type !== "cut") cuts.push({ frame: from, type: s.exit.type });
  }
  return cuts;
};
