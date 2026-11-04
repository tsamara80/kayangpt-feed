# Video studio

SaaS launch videos made by prompting Claude Code, built with [Remotion](https://www.remotion.dev).
You are the director. Claude is the motion designer, editor and sound designer.

This folder is separate from the feed pipeline. The daily workflow never touches it.

## Setup

```bash
cd video-studio
npm install
npm run studio        # live preview in the browser
npm run render:demo   # renders out/demo.mp4 showing every transition
npm run render        # renders out/final.mp4 (the Main composition)
```

Optional, for word-level voiceover sync: `pip install faster-whisper`.

## The six-step workflow

| Step | What you do | Where |
|---|---|---|
| 1 Prepare | Put the voiceover, references (named by script line), usable clips and logo in `public/` | `public/` |
| 2 Master prompt | Fill in and send the master prompt | `prompts/01-master-prompt.md` |
| 3 Review | Timestamped notes that point at the reference | `prompts/02-revision-notes.md` |
| 4 Change | Transitions, a new voiceover, polish | `prompts/03-change-prompts.md` |
| 5 Sound | Hand over the SFX library and describe the style | `prompts/04-sound-design.md` |
| 6 Render | `npm run render` | `out/final.mp4` |

```
public/
├── RAW AUDIO.mp3            voiceover
├── REFERENCE ANIMATION/
│   ├── first 3 line.mp4     motion for lines 1–3
│   └── 4th and 5th line.mp4 motion for lines 4–5
├── VIDEO YOU CAN USE/       clips shown inside the animation
├── SFX/                     sound effects library
└── logo.svg
```

Large media files in `public/` are git-ignored by default (see `.gitignore`).

## What is already built

| Piece | File |
|---|---|
| Mountain speed graph (slow start, sharp peak on the cut) | `src/lib/mountain.ts` |
| Transitions: zoomIn, zoomOut, slideLeft, slideRight, cut. Hard cuts only, no blur | `src/lib/transitions.ts` |
| Shot timeline with no overlap between scenes | `src/components/Timeline.tsx` |
| Sound placed so its loudest moment lands on a frame | `src/components/Sfx.tsx` |
| Detailed UI sound map, 10–15 dB under the voice | `src/data/sound-map.ts` |
| Word-by-word text, prompt box | `src/components/` |
| Brand colors and size | `src/style/theme.ts` |
| Your video's shot list | `src/scenes/main.tsx` |
| Voiceover transcription with word timestamps | `scripts/transcribe.py` |
| Frames from reference clips | `scripts/extract_frames.sh` |
| SFX library measurement (loudness, peak time, attack, brightness) | `scripts/analyze_sfx.py` |

## Your saved style

The style lives in `.claude/skills/saas-video/SKILL.md` at the repo root. Next time you can just say
"zoom out", "zoom in", "left slide in" or "right slide in", and Claude uses the whole recipe:
the curve, the hard cut, the size of the move and the whoosh on the cut.
