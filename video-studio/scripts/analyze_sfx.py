#!/usr/bin/env python3
"""Measure a sound-effects library so Claude can choose sounds it cannot hear.

For every audio file it records loudness, peak level, where the loudest moment
falls (peak_s, used to align whooshes on cuts), attack time, brightness and a
category guessed from the file name. Then it can filter by style.

Usage:
  python3 -I scripts/analyze_sfx.py public/SFX                  # writes public/SFX/sfx_index.json
  python3 -I scripts/analyze_sfx.py public/SFX --subtle --top 20 # print subtle candidates per category

Needs only ffmpeg on PATH. No Python packages.
"""
import argparse
import array
import json
import math
import os
import subprocess
import sys

EXTS = {".wav", ".mp3", ".aif", ".aiff", ".flac", ".ogg", ".m4a"}
RATE = 22050
CATEGORIES = {
    "whoosh": ["whoosh", "swoosh", "woosh", "transition", "riser", "air"],
    "swipe": ["swipe", "slide", "swish"],
    "click": ["click", "tap", "mouse", "button"],
    "tick": ["tick", "blip", "beep", "select", "hover"],
    "pop": ["pop", "bubble", "plop"],
    "typing": ["type", "typing", "keyboard", "key"],
    "confirm": ["confirm", "notification", "notif", "ui", "interface"],
    "chime": ["chime", "success", "ding", "bell", "shimmer", "sparkle"],
    "error": ["error", "warning", "alert", "fail", "deny"],
}


def decode(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    a = array.array("h")
    a.frombytes(out[: len(out) - len(out) % 2])
    if sys.byteorder == "big":
        a.byteswap()
    return a


def db(x):
    return 20 * math.log10(x) if x > 0 else -120.0


def analyze(path):
    s = decode(path)
    n = len(s)
    if n == 0:
        return None
    win = RATE // 100  # 10 ms windows
    env = []
    for i in range(0, n, win):
        chunk = s[i : i + win]
        env.append(math.sqrt(sum(v * v for v in chunk) / len(chunk)) / 32768)
    peak_idx = max(range(len(env)), key=env.__getitem__)
    peak_rms = env[peak_idx]
    onset = next((i for i, v in enumerate(env) if v > peak_rms * 0.1), 0)
    total_rms = math.sqrt(sum(v * v for v in s) / n) / 32768
    zc = sum(1 for i in range(1, n) if (s[i - 1] < 0) != (s[i] < 0))
    return {
        "duration_s": round(n / RATE, 3),
        "rms_db": round(db(total_rms), 1),
        "peak_db": round(db(max(abs(min(s)), abs(max(s))) / 32768), 1),
        "peak_s": round(peak_idx * win / RATE + win / RATE / 2, 3),
        "attack_ms": round((peak_idx - onset) * 10),
        "brightness_hz": round(zc / 2 / (n / RATE)),
    }


def categorize(name):
    low = name.lower()
    for cat, words in CATEGORIES.items():
        if any(w in low for w in words):
            return cat
    return "other"


def is_subtle(m):
    # not sharp: no instant spike, not too bright, not too loud
    return m["attack_ms"] >= 10 and m["brightness_hz"] < 4500 and m["peak_db"] < -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", help="index path (default: <folder>/sfx_index.json)")
    ap.add_argument("--subtle", action="store_true", help="only list subtle sounds")
    ap.add_argument("--top", type=int, default=0, help="print N best candidates per category")
    args = ap.parse_args()

    index = []
    files = [
        os.path.join(r, f) for r, _, fs in os.walk(args.folder) for f in fs if os.path.splitext(f)[1].lower() in EXTS
    ]
    for i, p in enumerate(sorted(files), 1):
        try:
            m = analyze(p)
        except subprocess.CalledProcessError:
            m = None
        if not m:
            continue
        rel = os.path.relpath(p, os.path.join(args.folder, ".."))
        m.update({"file": rel, "category": categorize(os.path.basename(p))})
        m["subtle"] = is_subtle(m)
        index.append(m)
        if i % 100 == 0:
            print(f"  {i}/{len(files)}", file=sys.stderr)

    out = args.out or os.path.join(args.folder, "sfx_index.json")
    with open(out, "w") as f:
        json.dump(index, f, indent=1)
    print(f"Indexed {len(index)} sounds -> {out}")

    if args.top:
        pool = [m for m in index if m["subtle"]] if args.subtle else index
        for cat in list(CATEGORIES) + ["other"]:
            items = sorted((m for m in pool if m["category"] == cat), key=lambda m: m["brightness_hz"])[: args.top]
            if items:
                print(f"\n[{cat}]")
                for m in items:
                    print(f"  {m['file']}  peak_s={m['peak_s']}  attack={m['attack_ms']}ms  bright={m['brightness_hz']}Hz  rms={m['rms_db']}dB")


if __name__ == "__main__":
    main()
