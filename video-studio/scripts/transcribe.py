#!/usr/bin/env python3
"""Transcribe the voiceover with word-level timestamps into src/data/transcript.json.

Usage:
  pip install faster-whisper
  python3 scripts/transcribe.py "public/RAW AUDIO.mp3"
"""
import json
import os
import sys

if len(sys.argv) < 2:
    sys.exit(__doc__)

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit("Install first: pip install faster-whisper")

audio = sys.argv[1]
model = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, word_timestamps=True)

lines, words = [], []
for seg in segments:
    lines.append({"text": seg.text.strip(), "start": round(seg.start, 3), "end": round(seg.end, 3)})
    for w in seg.words or []:
        words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)})

out = os.path.join(os.path.dirname(__file__), "..", "src", "data", "transcript.json")
with open(out, "w") as f:
    json.dump({"audio": os.path.basename(audio), "duration": round(info.duration, 3), "lines": lines, "words": words}, f, indent=1, ensure_ascii=False)
print(f"{len(words)} words, {info.duration:.1f}s -> {os.path.normpath(out)}")
