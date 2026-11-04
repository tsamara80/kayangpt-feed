import React from "react";
import { Audio, Sequence, staticFile, useVideoConfig } from "remotion";

export const dbToGain = (db: number) => Math.pow(10, db / 20);

/**
 * Places a sound so its LOUDEST moment lands on `atFrame`.
 * peakSec comes from scripts/analyze_sfx.py (field "peak_s").
 * Mix rule: effects sit roughly 10-15 dB under the voiceover.
 */
export const Sfx: React.FC<{
  src: string | null | undefined;
  atFrame: number;
  peakSec?: number;
  gainDb?: number;
}> = ({ src, atFrame, peakSec = 0, gainDb = -14 }) => {
  const { fps } = useVideoConfig();
  if (!src) return null;
  const ideal = atFrame - Math.round(peakSec * fps);
  const from = Math.max(0, ideal);
  const trim = from - ideal; // frames cut off the start if the sound would begin before frame 0
  return (
    <Sequence from={from} layout="none" name={`sfx ${src}`}>
      <Audio src={staticFile(src)} volume={dbToGain(gainDb)} trimBefore={trim || undefined} />
    </Sequence>
  );
};
