---
team: Inflection
week: 11
date: 2026-8-19
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
- **Designed and executed a structured evaluation** of the full pipeline across two LLM coaching backends (Llama 3.2 3B via Ollama, and GPT-4o-mini via the OpenAI API), running the same test set on both.
- **Built a 90-utterance synthetic test set**: 30 sentences across three languages (English, Italian, Spanish) and three emotional categories (hostile, neutral, happy), 10 sentences per category per language. Sentences were written manually and recorded with text-to-speech (ElevenLabs), holding emotional delivery constant across languages to control for speaker variability.
- **Instrumented the pipeline with per-utterance logging** (`src/evaluation/logger.py`) capturing session and utterance IDs, sentiment fields, coaching notes, and coaching latency.
- **Created an OpenAI branch** swapping the local Ollama coach for GPT-4o-mini, so both backends could be measured under identical conditions.
- **Wrote the evaluation scripts** (`finalEvaluation.py`, `metric1_extractor.py`) to label, score, and compute all four metrics, and produced `final_evaluation.csv` along with per-model metric files and labeled logs, all committed under `src/evaluation/` on the `evaluation` branch.
- **Updated the final report and presentation slides**

## Results
Four metrics were computed on both backends:
- **Coaching trigger precision:** 75.56% (Ollama) and 76.67% (OpenAI) overall accuracy, against a majority-class baseline of 66.7%. The difference between backends is a single false positive — confirming that flagging behavior is driven by the acoustic model, not the LLM. Both runs produced 20 false negatives.
- **Cross-language consistency:** hostile-flag rate of 90% in English, 10% in Italian, and 0% in Spanish, identical across backends.
- **Processing latency:** Ollama averaged 4,579 ms (max 11,094 ms); OpenAI averaged 1,630 ms (max 3,437 ms) — roughly 3× faster, which settled our local-versus-API question.
- **Tone-text agreement:** on a manual 1–3 rubric, OpenAI scored higher on tone alignment (2.83 vs 2.57) while Ollama scored higher on actionability (2.71 vs 2.33).

## This Week's Updates
- - The cross-language finding is the headline finding. Since the same sentences were spoken with the same emotion in all three languages, we would expect a language-agnostic acoustic model to flag them at similar rates. Instead, detection collapses outside English, which we attribute to the emotion model being fine-tuned on a predominantly English corpus. This directly qualifies the assumption that motivated our architecture, that acoustic tone, unlike text, survives the language barrier, and confirms, with measurements, the bias risk we had previously raised only on theoretical grounds in our ethics section.
- The results also show the system is **precise but under-sensitive**: with one false positive in 90 utterances, a raised flag is almost always correct, but two-thirds of hostile utterances go undetected.
- The latency measurements resolved the coach blocker carried over from last week. The hosted model is now the preferred backend for live use, with the local Ollama path retained as a no-cost, fully on-device option.
- Both final deliverables were revised against these results rather than against our earlier expectations, including scoping the product's multilingual claims to what the evaluation actually supports.

## Challenges / blockers
- The acoustic model is definitively English biased. This is not a bug we can patch before deadline, but a real product limitation. We are disclosing it publicly and suggesting remediation strategies for future work, such as multilingual fine-tuning, giving non-English speech a higher weight for text sentiment, or reverting to text-only flagging.
- Coaching-note quality (Metric 1) rests on a small sample, since only utterances that triggered the coach produced notes to score (7 for Ollama, 6 for OpenAI). Those numbers are directional rather than conclusive, a consequence of the low hostile recall.
- The evaluation covered three of the ten supported languages; behavior in the remaining seven is untested.

## Next week's goal
- It's the final week of the semester --> we are looking to finalize our deliverables before our presentation on 8/19

## Individual contributions
- Sawyer Byrd (Engineer): Designed the evaluation methodology, built the synthetic test set, wrote the evaluation and scoring scripts, and computed the four metrics across both backends.
- Alessandro Vivaldi (Engineer): Added per-utterance logging to the pipeline, created the OpenAI branch swapping in GPT-4o-mini, and ran the full test set on both branches to collect the CSV logs.
- Andrew Liu (Product/Reporting): Completed full final report and designed and developed final presentation slides. Assisted with other testing and weekly reporting
