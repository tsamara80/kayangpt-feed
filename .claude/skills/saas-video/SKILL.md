---
name: saas-video
description: Make or revise a studio-style SaaS / product launch video with Remotion in video-studio/. Use when the user asks for a launch video, explainer, motion graphics, transitions ("zoom in", "zoom out", "left slide in", "right slide in"), retiming to a new voiceover, or sound design for a video.
---

# SaaS video style kit

The user directs; you are motion designer, editor and sound designer. Work in `video-studio/` (see its README).

## Workflow
1. Check `video-studio/public/` for: voiceover, `REFERENCE ANIMATION/` (named after script lines), `VIDEO YOU CAN USE/`, logo, `SFX/`.
2. On a master prompt: if anything is unclear (aspect ratio, logo handling, exact label wording, sound now or later), ask first.
3. Study references: `scripts/extract_frames.sh`, then read the `_sheet.jpg` contact sheets and individual frames for timing, easing, layout, color, cursor.
4. Transcribe the voiceover: `python3 scripts/transcribe.py "public/<file>"` → `src/data/transcript.json`. Land every animation on its word.
5. Build shots in `src/scenes/main.tsx` using `Timeline`, `WordReveal`, `PromptBox` and new components as needed. Set `project.voiceover`. Brand tokens are in `src/style/theme.ts`.
6. Check your own work: render stills (`npx remotion still src/index.ts Main out/f.png --frame=N`) and contact sheets around every cut, then render a draft with `npm run render`.

## Pacing
Don't stretch the voiceover. Line plays → animation breathes → next line. Let total length float.
One scene ends before the next begins; scenes never touch or blend.

## Transitions (the mountain)
- Always hard cuts at peak speed. Never fades, crossfades, blends or blur.
- Speed graph: long slow start → sharp spike → cut at the peak → next scene continues the same motion at that speed → slows to rest.
- Defaults in `src/lib/transitions.ts`: 12 frames each side at 30 fps, sharpness 5, zoom 12% (keep small), slide 35% of width (never fully leaves the frame).
- "Too slow / too gentle" → raise sharpness (6–8) and/or shorten frames (8–10). Never add blur.
- Vocabulary (set as the outgoing shot's `exit`):
  - "zoom in" → `zoomIn`; "zoom out" → `zoomOut`
  - "left slide in" → `slideLeft`: scene drifts right, speeding up → cut → next arrives from the left
  - "right slide in" → `slideRight`: mirror
  - "hard cut" → `cut`: no movement
- Every moving cut gets an airy whoosh whose loudest moment lands on the cut frame (`WhooshOnCuts` handles it once `soundMap.whoosh` is set).

## Changes without starting over
- New voiceover: re-transcribe, retime by adding/removing breathing room only in calm moments. Keep animations and transition speeds unchanged; update on-screen text to the new words.
- Revisions: apply exactly what was asked; keep everything the user said must stay.

## Sound design
1. `python3 -I scripts/analyze_sfx.py public/SFX --subtle --top 20` and pick from the measurements (you can't listen; use loudness, peak_s, attack, brightness and category).
2. Default style: subtle, mostly UI sounds, nothing sharp (avoid near-zero attack and very bright files).
3. Fill `src/data/sound-map.ts` (src + peakSec from the index) and place `<Sfx>` per element:

| On screen | Sound |
|---|---|
| Each word revealing | soft UI tick, alternate wordTickA / wordTickB |
| Typing / type-on text | quiet keyboard clicks |
| Panels and boxes appearing | soft tonal confirm |
| Counters rolling up | light rapid ticks |
| Slides, rolling labels, morphs | soft swipes |
| Cards and list rows | small pops |
| Cursor clicks | gentle UI click |
| Every transition | airy whoosh peaking on the cut |
| Errors / success | gentle warning / soft positive chime |
| End card | light chime with shimmer |

4. Mix: effects 10–15 dB under the voiceover, nothing clips. If a sound grabs attention on its own, it's too loud.

## Eight rules
1. One folder: voiceover, references named by line, usable clips, logo.
2. One master prompt: files → format & style → pacing → transitions → line by line → ask first.
3. For every line: which reference, what to replace, what to keep.
4. Revision notes with timestamps that point at the reference.
5. Transitions are hard cuts at peak speed, never blends.
6. Describe motion as speed graphs; read attached graph screenshots and match their shape.
7. Change voice or words by retiming, not re-animating.
8. Sound-design every animation: subtle, mostly UI, well under the voice.
