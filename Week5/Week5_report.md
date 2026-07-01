---
team: <Inflection>
week: 5
date: 2026-7-1
members:
  - name: Alessandro Vivaldi
    github: xandrov1
    hat: Product | Engineering | Data&Eval
  - name: <Andrew Liu>
    github: <AndrewLiu-1>
    hat: Product | Engineering | Data&Eval
  - name: <Sawyer Byrd>
    github: <sawyerbyrd>
    hat: Product | Engineering | Data&Eval
north_star:
  metric: <e.g. task success rate>
  value: <this week>
  previous: <last week>
---

## Shipped this week
- <what is now merged or deployed>  (evidence: #12, PR #34; link the live product if it is deployed)

## User / validation learning
- We investigated Zendesk's community forum because it is one of the most widely used customer support platforms, making it a reliable proxy for what support teams actually need and complain about in practice. Users there were actively seeking better sentiment detection for voice tickets, confirming the pain exists at the tool level.
- We reviewed Zendesk's official documentation to verify what their sentiment feature actually does under the hood, not just what it claims. It confirmed their voice sentiment operates on post-call transcripts only, meaning acoustic tone is structurally invisible to their system by design.
- We examined G2 and third-party reviews of smaller tools like SentiSum to check whether the transcript-only limitation was a Zendesk-specific shortcut or an industry-wide pattern. Every tool marketed as doing "voice sentiment" turned out to be transcription-based under the hood, regardless of price point.
- We looked into SupportLogic specifically because it is the closest existing product to what we are building. Independent comparison sources confirmed it is explicitly positioned for enterprise scale, and SentiSum's entry price of $3,000/month prices out smaller teams, validating that the gap persists even for teams willing to pay.
- Across all sources, no tool was found that performs genuine acoustic tone analysis on customer calls. This reframes the project from building an affordable alternative to filling a capability gap no current tool addresses

## Metrics snapshot
- <metric>: <value> (was <previous>)

## Challenges / blockers
- <what is hard, and what help you need>

## Next week's goal
- <the one thing>

## Individual contributions
- Alessandro Vivaldi (Researcher): Conducted market research to map pain point
- <name> (<hat>): <what they did>  (evidence: ...)
- <name> (<hat>): <what they did>  (evidence: ...)

## Lean canvas changes (if any)
- <what shifted this week: user, problem, value proposition, cost, or risk>
