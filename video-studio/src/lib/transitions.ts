import { mountainIn, mountainOut, DEFAULT_SHARPNESS } from "./mountain";

/**
 * Transition vocabulary (same words you use in prompts):
 *   zoomIn     scene zooms in, speeding up -> hard cut -> next keeps zooming in and settles
 *   zoomOut    scene zooms out, speeding up -> hard cut -> next keeps zooming out and settles
 *   slideLeft  "left slide in": scene drifts right (never fully leaving) -> cut -> next arrives from the left
 *   slideRight mirror of slideLeft
 *   cut        straight hard cut, no movement
 *
 * Never a blend, never a fade, never blur.
 */
export type TransitionType = "zoomIn" | "zoomOut" | "slideLeft" | "slideRight" | "cut";

export type TransitionSpec = {
  type: TransitionType;
  /** Frames on EACH side of the cut. */
  frames?: number;
  /** Zoom size: 0.12 means 12 percent. Keep zooms small. */
  zoom?: number;
  /** Slide distance as a fraction of frame width. Keep under 0.5 so the scene never fully leaves. */
  slide?: number;
  sharpness?: number;
};

export const TRANSITION_DEFAULTS = {
  frames: 12,
  zoom: 0.12,
  slide: 0.35,
  sharpness: DEFAULT_SHARPNESS,
};

type Transform = { scale: number; x: number };
const IDENTITY: Transform = { scale: 1, x: 0 };

const resolve = (s: TransitionSpec) => ({ ...TRANSITION_DEFAULTS, ...s });

/** Transform for the OUTGOING scene, t in [0,1] over its last `frames` frames. */
export const exitTransform = (spec: TransitionSpec | undefined, t: number, width: number): Transform => {
  if (!spec || spec.type === "cut") return IDENTITY;
  const s = resolve(spec);
  const p = mountainOut(t, s.sharpness);
  const logZoom = Math.log(1 + s.zoom);
  switch (s.type) {
    case "zoomIn":
      return { scale: Math.exp(logZoom * p), x: 0 };
    case "zoomOut":
      return { scale: Math.exp(-logZoom * p), x: 0 };
    case "slideLeft":
      return { scale: 1, x: s.slide * width * p };
    case "slideRight":
      return { scale: 1, x: -s.slide * width * p };
  }
  return IDENTITY;
};

/** Transform for the INCOMING scene, t in [0,1] over its first `frames` frames. */
export const enterTransform = (spec: TransitionSpec | undefined, t: number, width: number): Transform => {
  if (!spec || spec.type === "cut") return IDENTITY;
  const s = resolve(spec);
  const rest = 1 - mountainIn(t, s.sharpness); // 1 at the cut -> 0 when settled
  const logZoom = Math.log(1 + s.zoom);
  switch (s.type) {
    case "zoomIn":
      return { scale: Math.exp(-logZoom * rest), x: 0 };
    case "zoomOut":
      return { scale: Math.exp(logZoom * rest), x: 0 };
    case "slideLeft":
      return { scale: 1, x: -s.slide * width * rest };
    case "slideRight":
      return { scale: 1, x: s.slide * width * rest };
  }
  return IDENTITY;
};

export const transitionFrames = (spec?: TransitionSpec) =>
  spec && spec.type !== "cut" ? spec.frames ?? TRANSITION_DEFAULTS.frames : 0;
