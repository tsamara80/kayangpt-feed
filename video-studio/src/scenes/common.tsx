import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../style/theme";

export const Center: React.FC<{ children: React.ReactNode; bg?: string }> = ({ children, bg = theme.background }) => (
  <AbsoluteFill style={{ backgroundColor: bg, justifyContent: "center", alignItems: "center" }}>{children}</AbsoluteFill>
);

export const Card: React.FC<{ label: string; tone?: "accent" | "plain" }> = ({ label, tone = "plain" }) => (
  <div
    style={{
      width: 460,
      height: 300,
      borderRadius: theme.radius,
      background: tone === "accent" ? theme.accent : theme.surface,
      border: `2px solid ${tone === "accent" ? theme.accent : theme.border}`,
      boxShadow: "0 24px 60px rgba(31,30,29,0.10)",
      color: tone === "accent" ? "white" : theme.ink,
      fontFamily: theme.font,
      fontSize: 56,
      fontWeight: 650,
      display: "grid",
      placeItems: "center",
    }}
  >
    {label}
  </div>
);
