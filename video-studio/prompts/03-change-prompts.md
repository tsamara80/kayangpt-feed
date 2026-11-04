# Changing things without starting over

## Transitions
The main problem is the transitions — they should be hard cuts, never blends. Every transition should follow a mountain-shaped speed graph: slow start, sharp peak at the cut, next scene continues the same motion and slows down. Smoothness matters more than length.

Still too slow? Attach a speed-graph screenshot and say: "Long slow start and a very big, sharp peak right at the cut. Remove all blur, keep zooms small." (raises `sharpness` / lowers `frames` in `src/lib/transitions.ts`)

Per cut: "At 00:03 use zoom out. At 00:20 and 00:31 use left slide in."

## New voiceover
I've changed the voiceover (new file is in `public/`). Retime the animations to it without changing the animations themselves, and update on-screen text to the new words. Add or remove breathing room only in calm moments — keep every transition's speed.

## Polish round
- Remove the colored overlay from the videos so they show in original colors.
- [ … ]
