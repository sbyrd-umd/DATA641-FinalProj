"""
Play a folder of test clips into your virtual mic, one at a time, so
main.py (already running and listening on the loopback device) picks
them up and logs them to evaluation_log.csv on its own.

This script does NOT read the log or score anything -- it just plays
audio. Check evaluation_log.csv yourself afterward to see the results.

Setup:
    pip install sounddevice soundfile

Usage:
    python play_all_clips.py clips --device 5
    python play_all_clips.py clips --device 5 --pause 3
"""

import argparse
import math
import re
import time
from pathlib import Path

import sounddevice as sd
import soundfile as sf
from scipy.signal import resample_poly


def natural_key(path: Path):
    """Sort by the first number found in the filename (e.g. ElevenLabs9
    before ElevenLabs10), falling back to the filename itself if no
    number is present."""
    match = re.search(r"\d+", path.stem)
    return (int(match.group()) if match else float("inf"), path.name)


def list_devices():
    for i, dev in enumerate(sd.query_devices()):
        kind = []
        if dev["max_input_channels"] > 0:
            kind.append("input")
        if dev["max_output_channels"] > 0:
            kind.append("output")
        print(f"{i}: {dev['name']}  ({'/'.join(kind)})")


def play_clip(path: Path, device: int):
    data, samplerate = sf.read(str(path), dtype="float32")

    def resampled_to(rate):
        if rate == samplerate:
            return data
        gcd = math.gcd(rate, samplerate)
        up, down = rate // gcd, samplerate // gcd
        return resample_poly(data, up, down, axis=0)

    candidate_rates = []
    if device is not None:
        reported = int(sd.query_devices(device)["default_samplerate"])
        candidate_rates.append(reported)
    candidate_rates += [44100, 48000, samplerate]

    last_error = None
    for rate in candidate_rates:
        try:
            sd.play(resampled_to(rate), rate, device=device)
            sd.wait()
            return
        except sd.PortAudioError as e:
            last_error = e
            continue

    raise last_error


def find_clips(root: Path, language: str | None = None, category: str | None = None):
    """Walk Audio/{Language}Audio/{Category}/*.mp3, yielding
    (language_dir_name, category_dir_name, clip_path) in a stable,
    naturally-sorted order."""
    lang_dirs = sorted(d for d in root.iterdir() if d.is_dir())
    for lang_dir in lang_dirs:
        if language and language.lower() not in lang_dir.name.lower():
            continue
        cat_dirs = sorted(d for d in lang_dir.iterdir() if d.is_dir())
        for cat_dir in cat_dirs:
            if category and category.lower() not in cat_dir.name.lower():
                continue
            clips = sorted(cat_dir.glob("*.mp3"), key=natural_key)
            for clip in clips:
                yield lang_dir.name, cat_dir.name, clip


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs="?", help="Root Audio folder (contains {Language}Audio subfolders)")
    parser.add_argument("--device", type=int, help="Output device index (CABLE Input)")
    parser.add_argument("--pause", type=float, default=2.0, help="Seconds to wait between clips")
    parser.add_argument("--language", default=None, help="Filter to one language, e.g. Italian")
    parser.add_argument("--category", default=None, help="Filter to one category, e.g. Hostile")
    parser.add_argument("--list", action="store_true", help="List available audio devices and exit")
    args = parser.parse_args()

    if args.list or not args.folder:
        list_devices()
        return

    root = Path(args.folder)
    clips = list(find_clips(root, language=args.language, category=args.category))

    if not clips:
        print(f"No .mp3 files found under {root.resolve()}")
        return

    print(f"Found {len(clips)} clips under {root.resolve()}")
    print("Make sure main.py is already running and listening before continuing.\n")

    for i, (lang, cat, clip) in enumerate(clips, 1):
        print(f"[{i}/{len(clips)}] {lang} / {cat} / {clip.name}")
        play_clip(clip, args.device)
        time.sleep(args.pause)

    print("\nDone. Check evaluation_log.csv for the results.")


if __name__ == "__main__":
    main()
