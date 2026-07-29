---
team: Inflection
week: 8
date: 2026-7-29
members:
  - name: Alessandro Vivaldi
    github: xandrov1
    hat: Product | Engineering | Data&Eval
  - name: Andrew Liu
    github: AndrewLiu-1
    hat: Product | Engineering | Data&Eval
  - name: Sawyer Byrd
    github: sawyerbyrd
    hat: Product | Engineering | Data&Eval
north_star:
  metric: Working translation layer
  value: working
  previous: Hone concept and idea and start structuring
---

## Shipped this week
- Our biggest focus this week was restructuring the codebase on our new `reorg-file-structure branch`. The program now has a single entry point (`main.py`), with functionality split into dedicated modules under `src/` based on what each piece does — replacing the previous single-script layout.

## New project structure:
- `main.py` — entry point that wires all components together
- `src/config.py` — shared configuration constants (audio format, sample rate, supported languages, buffer settings)
- `src/audio/` — microphone audio capturing (`MicStreamer`) and a new `AudioTimeline` module (see under weekly updates)
- `src/transcription/` — Deepgram client/connection setup and the cached per-language translation layer
- `src/sentiment/` — the sentiment layer, split from one file into `model.py` (wav2vec2 + regression head), `scoring.py` (emotion labeling heuristics), and `analyzer.py` (threaded real-time analyzer)

## This Week's Updates
- The restructure prepares the codebase for the remaining second-half work --> now our upcoming components have a clear home, modules can be tested independently, and shared settings live in one config file instead of being duplicated across scripts.
- Working on audio coherency between the translation/transcription path and the sentiment path. We want to make sure that the sentiment analysis runs on the same audio the transcript refers to, rather than on independent sliding windows. The new `AudioTimeline` component buffers raw microphone audio tagged by elapsed time, so the program can slice out the exact audio span corresponding to a Deepgram transcript's time range. 
- Aligning sentiment readings to utterances matters for our north star: escalation flagging that combines tone with text sentiment requires both signals to describe the same stretch of speech.
- The sentiment layer's planned merge to main was folded into the restructure --> It will land on main as part of the `reorg-file-structure` branch rather than as a separate merge.

## Challenges / blockers
- Utterance-aligned sentiment is the main open engineering problem. The `AudioTimeline` design handles matching transcript timestamps to the right stretch of buffered audio, but it still needs to be integrated and tested against the live stream.

## Next week's goal
- Following up on mid-semester feedback, we want to continue testing based on AI-generated audio samples, extending the multilingual AI-speaker testing we began last week into a more systematic test suite.
- Merge the restructured codebase into main and complete the utterance-aligned audio coherency work

## Individual contributions
- Alessandro Vivaldi (Engineer): Handled preliminary AI-generated audio sample testing and helped fine tune other areas.
- Sawyer Byrd (Engineer): Restructured the codebase into the new modular layout and began the audio coherency work, including the `AudioTimeline` design.
- Andrew Liu (Organizer): Continued with testing from last week and assisted Alessandro's testing. Completed weekly report and editing.

