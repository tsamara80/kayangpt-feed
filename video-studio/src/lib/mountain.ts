/**
 * The "mountain" speed graph.
 *
 * Outgoing scene: starts very slow, accelerates sharply, peak speed on the cut.
 * Incoming scene: starts at that same peak speed, continues the same motion,
 * and slows down until it settles.
 *
 * Position curves:
 *   out(t) = t^k              speed k*t^(k-1)      -> peak k at t = 1
 *   in(t)  = 1 - (1 - t)^k    speed k*(1-t)^(k-1)  -> peak k at t = 0
 *
 * With the same duration and distance on both sides of the cut, the speed is
 * continuous across the cut, so the eye reads two scenes as one fluid move.
 * Higher k = sharper, narrower peak = snappier transition.
 */
export const DEFAULT_SHARPNESS = 5;

const clamp01 = (t: number) => Math.min(1, Math.max(0, t));

export const mountainOut = (t: number, k = DEFAULT_SHARPNESS) => Math.pow(clamp01(t), k);

export const mountainIn = (t: number, k = DEFAULT_SHARPNESS) => 1 - Math.pow(1 - clamp01(t), k);

/** Soft start and stop, for moves inside a scene (not for transitions). */
export const easeInOut = (t: number) => {
  const x = clamp01(t);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
