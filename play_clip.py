"""
Play an audio clip out through a specific output device (e.g. a virtual
audio cable, so your program's mic input picks it up).

Setup:
    pip install sounddevice soundfile

Usage:
    python play_clip.py --list                     # show device names/indices
    python play_clip.py clips/H01_english.mp3 --device 6
"""

import argparse
import sounddevice as sd
import soundfile as sf


def list_devices():
    for i, dev in enumerate(sd.query_devices()):
        kind = []
        if dev["max_input_channels"] > 0:
            kind.append("input")
        if dev["max_output_channels"] > 0:
            kind.append("output")
        print(f"{i}: {dev['name']}  ({'/'.join(kind)})")


def play(path: str, device: int | None):
    data, samplerate = sf.read(path, dtype="float32")
    sd.play(data, samplerate, device=device)
    sd.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("clip", nargs="?", help="Path to audio file to play")
    parser.add_argument("--device", type=int, default=None, help="Output device index")
    parser.add_argument("--list", action="store_true", help="List available audio devices")
    args = parser.parse_args()

    if args.list or not args.clip:
        list_devices()
    else:
        play(args.clip, args.device)
