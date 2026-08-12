---
team: Inflection
week: 10
date: 2026-8-12
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
Drafted a formal evaluation plan for measuring sentiment accuracy, now in the repository under ``EVAL/``. The plan includes the following:
1. Lock in the emotion taxonomy - pick a fixed label set (e.g. happy, sad, angry, fearful, neutral) that both the wav2vec2 model's describe() output and Ollama's new sentiment field will map to, so the two are directly comparable.
2. Add structured sentiment output to Ollama - update SYSTEM_PROMPT in prompts.py to require a sentiment label before the coaching note (e.g. JSON with sentiment and note keys), then update OllamaClient.chat() and coach.py to parse both fields separately, so the label isn't contaminated by the advice text. (First double check this way doesn't contaminate as well)
3. Build the synthetic generator - prompt a separate LLM to produce short utterances tagged with ground-truth emotions from taxonomy, ~10–20 per label to start.
4. Human-validate a subset - have a person confirm a sample of the generator's labels actually match, so ground truth is trustworthy before scoring against it.
5. Run the full pipeline on the test set - feed each utterance through wav2vec2 sentiment, then Ollama, logging: wav2vec2 label, Ollama sentiment label, and ground truth, per sample.
6. Score each stage separately - build a confusion matrix + accuracy for wav2vec2 alone, and another for Ollama's sentiment field alone.
7. Experiment with fusion - start with a confidence-weighted average of the two labels/scores, compare fused output against human judgment, and note where it disagrees most.
8. Iterate - adjust weighting or add override rules (e.g. tone wins on disagreement) based on where fusion misses, then re-test.

## This Week's Updates
- This was a lighter, testing-focused week. Most effort went into exercising the LLM feedback ("coach") layer and planning how we will measure accuracy — the core of our north-star metric.
- Testing the coach layer surfaced a latency blocker: on CPU-only machines, the local Llama 3.2 3B model frequently exceeds our 20-second response timeout. This lead to the script producing "coach unavailable" errors even though the code pre-warms the model. We evaluated alternatives — a hosted API model, or running Ollama on more powerful EC2 hardware. Our current plan is to first try to make local inference fast enough, then if we must, try different API-based model if it can't be.

## Challenges / blockers
- The main challenge we faced this week was the coach latency on CPUs. On machines without a usable GPU, Llama 3.2 3B routinely takes longer than our 20-second timeout to produce feedback, so the coach returns "unavailable" instead of a response — and a feedback layer that times out is effectively absent from the product. Our options to solve this problem are: getting local GPU inference working or switching to a hosted API model.

## Next week's goal
- Resolve the coach latency blocker, switch the coach to the translated transcript and begin executing the evaluation plan with a synthetic test set.

## Individual contributions
- Sawyer Byrd (Engineer): Debugged the coach timeout across machines. Helped with further testing.
- Alessandro Vivaldi (Engineer): Drafted the evaluation plan, tested the coach layer, diagnosed the CPU response-timeout blocker.
- Andrew Liu (Product/Reporting): Handled weekly reporting and documentation. Assisted with further testing.
