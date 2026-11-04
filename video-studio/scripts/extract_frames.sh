#!/usr/bin/env bash
# Pull frames from every reference clip so Claude can study timing, easing, layout and color.
# Usage: scripts/extract_frames.sh [fps]   (default 6 frames per second)
set -euo pipefail
cd "$(dirname "$0")/.."
FPS="${1:-6}"
mkdir -p out/reference-frames
find "public/REFERENCE ANIMATION" -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.webm' \) -print0 |
while IFS= read -r -d '' clip; do
  name="$(basename "${clip%.*}")"
  dir="out/reference-frames/$name"
  mkdir -p "$dir"
  ffmpeg -v error -y -i "$clip" -vf "fps=$FPS,scale=640:-1" "$dir/%04d.jpg"
  ffmpeg -v error -y -i "$clip" -vf "fps=$FPS,scale=320:-1,tile=6x6" -frames:v 1 "$dir/_sheet.jpg"
  echo "$name: $(ls "$dir" | wc -l) frames -> $dir"
done
