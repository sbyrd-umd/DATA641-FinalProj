---
team: Inflection
week: 5
date: 2026-7-1
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
- We have created a rough structure and outline of our program. This gives us a blueprint for what we need to implement.

#### Structure:
- Sentiment analysis via open source like wav2vec2
- LLM for coaching/summary layer
- DONT build the translator, there are APIs that already exist which we can leverage.
- Run translator and Sentiment analysis in parallel and feed into LLM for live feedback

## User / validation learning
- After confirming that the pain does exist at a tool level, we continued to  investigate some industry practices.
- After reviewing the capabilities of industry standandards, we found that these tools either include audio based sentiment analysis but no translation **OR** translation features but no audio based sentiment analysis.
- A big point of our idea is to have the translation and sentiment analysis to be real time. This means we need to run translation and sentiment analysis in parallel. This will be the first layer
- We also want to implement a feedback LLM system. This will need to be fed by the outputs of the sentiment analysis and translation. This will be the second layer


## Metrics snapshot
- <metric>: no current metrics. We are just now starting to build

## Challenges / blockers
- This project will require a translator, sentiment analysis layer, and an LLM feedback layer. We plan to outsource the translator to stay in scope for this class.
- Since all of these layers need to run in real time, we need to factor in runtime and latency.

## Next week's goal
- Get the translation layer working

## Individual contributions
- Alessandro Vivaldi (Researcher): Conducted market research to see what structure and resources other companies use
- Sawyer Byrd (Researcher): Planned out the project structure an road map
- Andrew Liu (Organizer): Helped organize our research information and ideas in a clean format that we can keep track of.

## Lean canvas changes (if any)
- <what shifted this week: user, problem, value proposition, cost, or risk>
