---
team: Inflection
week: 7
date: 2026-7-22
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
- Delivered the mid-semester presentation, including a live demo of the working pipeline, and added the final presentation deck to the repository.
- Tuned and finalized our sentiment analysis layer on the sentiment-analysis branch. The branch is stable and we plan to merge it into main later this week and after one final review going into week 8.

## This Week's Updates
- This was a lighter week for us. Our primary focus was incorporating the feedback we received from the professor during the mid-semester presentation into our plans and materials for the second half of the semester.
- As part of finalizing the sentiment layer, we refined the emotion labeling heuristic. In addition to the full octant mapping over valence, arousal, and dominance, the heuristic now falls back to a simpler two-axis read (e.g., "Negative / Agitated," "High energy," "Calm / Neutral") whenever one of the dimensions sits inside the neutral deadzone. This helps the program in avoiding overconfident octant labels when the model's scores are more ambiguous.
- Another significant focus this week was continued testing. We continued our testing formula across all of the support languages (English, Spanish, French, German, Hindi, Russian, Portuguese, Japanese, Italian, and Dutch), using AI-generated speakers to produce test speech for languages where we lack native speakers. We were able to fully see if our language detection, translation, and sentiment analysis actually worked across the full supported language set, and further backed our tests with the actual native-speaker sessions.

## Challenges / blockers
- Few issues this week, but our biggest challenge in previous test was keeping the responses consistent with the native speakers. This week we aimed to tackle the issue with our proper tests across the full support language set.

## Next week's goal
- Merge the finalized sentiment layer into main and begin work on the text sentiment layer that feeds our combined escalation flagging

## Individual contributions
- Alessandro Vivaldi (Engineer): Further tuned the sentiment analysis layer with Sawyer. Assisted with testing.
- Sawyer Byrd (Engineer): Further tuned the sentiment analysis layer with Alessandro. Assisted with testing.
- Andrew Liu (Organizer): Lead testing with across the full language set. Completed weekly report and editing.

