---
team: Inflection
week: 6
date: 2026-7-15
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
- Merged live-lang-detect into main. Our main branch program now performs automatic language detection using Deepgram's nova-3 multi-language mode, with cached per-language translators. This feature removed the need for manual language selection.
- Built the sentiment analysis layer on a new sentiment-analysis branch. This is the second major layer of our architecture: a wav2vec2-based emotion recognition module that runs in real time on the raw audio stream, in parallel with transcription and translation.
- Started work on the mid-semester presentation, including drafting slide content and creating a mockup of the envisioned end product.

## This Week's Updates
- Our new sentiment layer analyzes the original audio, not the translated text. Since the model works on acoustic features (mostly tone/energy/vocal inflections) rather than just the words, it is not specific to any particular language, which very much suits our multilingual use case.
- We moved from a simple threshold heuristic (our original tuning) to the octant-based mapping over valence/arousal/dominance, which gives richer labels and a tunable "deadzone" for low-confidence readings. The intensity score is currently used only for flagging, but we plan to feed it to the LLM coaching layer as additional context.
- With the development of the sentiment layer being finalized, both components of our first intended architecture layer are now in play together.

## Challenges / blockers
- Running wav2vec2 inference locally in real time with the streaming transcription raises latency and compute concerns.
- We still need to further test and develop the sentiment-analysis branch thuroughly and with actual users before merging to main 

## Next week's goal
- Finalize and merge the sentiment layer into main and test the combined transcription + translation + sentiment pipeline end to end
- Make pivots and other adjustments based on feedback from mid-semester presentation

## Individual contributions
- Alessandro Vivaldi (Engineer): Assisted with and tuned the sentiment analysis layer with Sawyer.
- Sawyer Byrd (Engineer): Developed initial sentiment analysis layer, and merged the live language detection branch to main
- Andrew Liu (Organizer): Handled weekly reporting and editing, drafted the mid-semester presentation slides, and created the end-product mockup.

