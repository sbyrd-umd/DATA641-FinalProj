---
team: Inflection
week: 9
date: 2026-8-5
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
  metric: Accurate real-time emotional escalation flagging
  value: in progress (tone layer complete and merged)
  previous: Accurate real-time emotional escalation flagging
---

## Shipped this week
- Merged the restructured codebase and the utterance-aligned sentiment pipeline into main. The sentiment layer now lives on main for the first time, in its new modular layout, and audio coherency between transcription and sentiment is complete: sentiment analysis runs on the exact same audio span as the transcript it accompanies.
- Fixed transcript double-printing in terminal. Deepgram's interim results (required for utterance-end detection) were causing each line to print twice --> the message handler now only prints and tracks the finalized results.
- Began testing an LLM feedback layer on a new branch. It generates short feedback from the pipeline's output using a small LLM (Llama 3.2 3B) running locally through Ollama — keeping the feedback layer on-device and free, in line with our affordability goal (requires installing Ollama and pulling the model before running).

#### How the utterance-aligned sentiment works:
- The microphone stream now sends audio to both Deepgram and an `AudioTimeline`, which stores the raw audio along with timestamps.
- We use an utterance tracker records each finalized transcript segment and its timing. When Deepgram detects the end of an utterance, the program pulls the matching audio from the timeline and sends it for sentiment analysis.
- Sentiment analysis now runs once per utterance using the exact audio that matches the transcript. This replaces the old sliding-window approach and prevents the duplicate sentiment result problem we were encountering in previous weeks.

## This Week's Updates
- With utterance alignment, the sentiment results now appear shortly after a speaker finishes a statement instead of updating continuously while they speak. This slight delay allows the analyzer to evaluate the complete statement and display the result alongside its transcript and translation.
- We followed up last week with continued testing. Our findings from this week showed that the tone analyzer was able to distinguish between moods more accurately after current alignment, including correctly identifying negative content even when spoken in a deliberately positive tone.

## Challenges / blockers
- Sentiment results now appear after the speaker finishes their statement, so longer statements naturally take more time to analyze. We’ll need to make sure this delay remains acceptable during live calls and other potential use cases for our persona.
- The LLM feedback prototype adds a second local model (Llama 3.2 3B alongside wav2vec2) running during calls. Before adding it to the main system, we still need to evaluate both its performance impact and the overall quality of its feedback before we move forward.

## Next week's goal
- Build the text sentiment layer and evaluate the LLM feedback prototype for integration

## Individual contributions
- Sawyer Byrd (Engineer): Completed and merged the utterance-aligned sentiment pipeline into main, and tested our new local LLM feedback layer on a new branch.
- Alessandro Vivaldi (Engineer): Focused on fine tuning and testing. Fixed double-printing issue, and developed a 9 step SER eval plan.
- Andrew Liu (Product/Reporting): Handled weekly reporting and documentation. Assisted with further testing.
