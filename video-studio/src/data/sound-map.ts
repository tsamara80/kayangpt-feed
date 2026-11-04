/**
 * The detailed UI sound map. Fill each role with a file path relative to public/
 * (for example "SFX/ui_tick_soft_01.wav"). Leave null and that sound is skipped.
 * scripts/analyze_sfx.py can suggest candidates and their peak_s values.
 */
export type SoundRole =
  | "wordTickA"
  | "wordTickB"
  | "typing"
  | "panelConfirm"
  | "counterTick"
  | "swipe"
  | "pop"
  | "cursorClick"
  | "whoosh"
  | "errorTone"
  | "successChime"
  | "endChime";

export type SoundSlot = { src: string | null; peakSec: number; gainDb: number };

const slot = (gainDb: number): SoundSlot => ({ src: null, peakSec: 0, gainDb });

// Gains sit 10-15 dB under the voiceover (voice is assumed near -3 dB peak).
export const soundMap: Record<SoundRole, SoundSlot> = {
  wordTickA: slot(-18),
  wordTickB: slot(-18),
  typing: slot(-20),
  panelConfirm: slot(-16),
  counterTick: slot(-20),
  swipe: slot(-16),
  pop: slot(-17),
  cursorClick: slot(-16),
  whoosh: slot(-13),
  errorTone: slot(-15),
  successChime: slot(-15),
  endChime: slot(-13),
};
