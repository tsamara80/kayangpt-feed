import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../style/theme";

export type TimedWord = { text: string; start: number };

/** Words appear one by one, each landing on its spoken timestamp (seconds, relative to the shot). */
export const WordReveal: React.FC<{ words: TimedWord[]; size?: number; color?: string; highlight?: string[] }> = ({
  words,
  size = 120,
  color = theme.ink,
  highlight = [],
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: `0 ${size * 0.28}px`,
        maxWidth: 1500,
        fontFamily: theme.font,
        fontWeight: 650,
        fontSize: size,
        letterSpacing: "-0.03em",
        lineHeight: 1.1,
      }}
    >
      {words.map((w, i) => {
        const local = frame - w.start * fps;
        const p = interpolate(local, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const eased = 1 - Math.pow(1 - p, 3);
        return (
          <span
            key={i}
            style={{
              opacity: eased,
              transform: `translateY(${(1 - eased) * size * 0.35}px)`,
              color: highlight.includes(w.text) ? theme.accent : color,
            }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
};

/** Evenly spaced words, for silent beats or before a transcript exists. */
export const spacedWords = (sentence: string, startSec = 0.2, gapSec = 0.28): TimedWord[] =>
  sentence.split(/\s+/).map((text, i) => ({ text, start: startSec + i * gapSec }));
