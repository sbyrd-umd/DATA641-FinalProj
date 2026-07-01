---
team: <your-company-name>
week: 5
date: 2026-7-1
members:
  - name: Alessandro Vivaldi
    github: xandrov1
    hat: Product | Engineering | Data&Eval
  - name: Sawyer
    github: sbyrd-umd
    hat: Product | Engineering | Data&Eval
  - name: Andrew Liu
    github: AndrewLiu-1
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
- We investigated Zendesk's community forum because it is one of the most widely used customer support platforms, making it a reliable proxy for what support teams actually need and complain about in practice. Users there were actively seeking better sentiment detection for voice tickets, confirming the pain exists at the tool level.
- We reviewed Zendesk's official documentation to verify what their sentiment feature actually does under the hood, not just what it claims. It confirmed their voice sentiment operates on post-call transcripts only, meaning acoustic tone is structurally invisible to their system by design.
- We examined G2 and third-party reviews of smaller tools like SentiSum to check whether the transcript-only limitation was a Zendesk-specific shortcut or an industry-wide pattern. While there are audio based sentiment analysis tools, they are quite pricey and come with limited features.
- The standard seems to be text based sentiment analysis and there is almost no support for multilingual calls.
- We looked into SupportLogic and CallMiner specifically because they are the closest existing product to what we are building. Independent comparison sources confirmed it is explicitly positioned for enterprise scale, and SentiSum's entry price of $3,000/month prices out smaller teams. CallMiner uses live translators but the sentiment analysis is text-based.
- **The information we collected shows a gap that we wish to fill: Affordable live translation with audio based sentiment analysis, including a live LLM feedback coach.**

## Metrics snapshot
- <metric>: no current metrics. We are just now starting to build

## Challenges / blockers
- This project will require a translator, sentiment analysis layer, and an LLM feedback layer. We plan to outsource the translator to stay in scope for this class.

## Next week's goal
- Get the translation layer working

## Individual contributions
- Alessandro Vivaldi (Researcher): Conducted market research to map pain point
- Sawyer Byrd (Researcher): Planned out the project structure
- Andrew Liu (Organizer): Helped organize our research information and ideas in a clean format that we can keep track of.

## Lean canvas changes (if any)
- <what shifted this week: user, problem, value proposition, cost, or risk>
