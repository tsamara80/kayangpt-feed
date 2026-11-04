import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../style/theme";

/** A prompt box that types a request, with a model label. */
export const PromptBox: React.FC<{ text: string; model?: string; startSec?: number; charsPerSec?: number }> = ({
  text,
  model = "Opus 5.5",
  startSec = 0.3,
  charsPerSec = 28,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const chars = Math.max(0, Math.floor((frame / fps - startSec) * charsPerSec));
  const shown = text.slice(0, chars);
  const caretOn = Math.floor(frame / (fps / 2)) % 2 === 0;
  return (
    <div
      style={{
        width: 1200,
        background: theme.surface,
        border: `2px solid ${theme.border}`,
        borderRadius: theme.radius,
        boxShadow: "0 30px 80px rgba(31,30,29,0.12)",
        padding: "44px 52px 32px",
        fontFamily: theme.font,
      }}
    >
      <div style={{ fontSize: 46, color: theme.ink, minHeight: 120, lineHeight: 1.3 }}>
        {shown}
        <span style={{ opacity: caretOn ? 1 : 0, color: theme.accent }}>|</span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 24 }}>
        <span style={{ fontSize: 28, color: theme.muted }}>{model}</span>
        <span
          style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            background: theme.accent,
            color: "white",
            display: "grid",
            placeItems: "center",
            fontSize: 34,
          }}
        >
          ↑
        </span>
      </div>
    </div>
  );
};
