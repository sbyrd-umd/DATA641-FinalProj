# Inflection — Final Project Report

**DATA/MSML 641 · Summer 2026**
**Team:** Sawyer Bryd, Andrew Liu, Alessandro Vivaldi

---

## Problem and Users

The emotional content of a call is often the first thing lost when providing customer service over linguistic barriers. Our tool aims to bridge the divide created by these barriers in order to provide users with the best customer service possible. Our target user is a customer service agent (QA manager or team lead) at a business process outsourcer (BPO) or international support organization, taking calls from customers who may not be completely fluent in the language spoken by the agent. While translation tools are capable of translating a customer’s words, they are unable to capture any of the emotional context. An agent listening to a translated transcript can’t hear when a customer is getting frustrated, and a manager reviewing calls later reads emotionally neutral text rather than an emotionally charged conversation.

Before a tool like ours, these organizations had to choose between 3 poor options. First, they could have native agents or QA staff for each supported language. While this works, it can be extremely costly and doesn’t scale well to a large number of languages. Second, they could buy enterprise conversation-intelligence platforms like SupportLogic or CallMiner, which are priced for large call centers, meaning that they are unaffordable for smaller-sized operations. Third, they could use other generic translation tools and post-call transcript reviews, completely losing all emotional depth that the conversation had. Our research found that while most tools are sold as “voice sentiment analysis”, they only perform it on the transcript text and ignore the acoustic signals (tone of voice) that transmit emotion across languages. There is no existing tool that does real-time translation with real acoustic sentiment analysis. That combination is the problem Inflection aims to solve.


## Product

Inflection is a real-time, low-cost call companion that transcribes, translates, and reads back customer sentiment as the customer speaks. It runs as a standalone application alongside the agent’s calling software (this could be Zoom, a phone call, or anything that produces audio). As of now, it requires no integration or plugin; it just listens to whatever audio stream is provided. On a call, an agent is able to see the live transcript in the customer’s original language, an English translation, the customer’s current emotional state read from their tone of voice, and a flag when the call shows signs of escalating. An LLM-based “coach” layer is then able to convert these signals into short, actionable feedback for the agent

![Inflection architecture](InflectionArchitecture.png)

The system works end-to-end as follows: Two users simultaneously receive the live audio. The first is Deepgram’s nova-3 streaming API, which returns transcripts in real time and automatically detects which of ten supported languages is being spoken (per utterance, with no manual configuration). Non-English transcripts are translated to English using Google Translate, with cached instances of the translator for each detected language. The second consumer is our `AudioTimeline`, a rolling buffer of 30 seconds where each audio chunk is tagged with the time it was captured. Then, when Deepgram signals the end of an utterance, the pipeline extracts the audio segment corresponding to that utterance from the timeline and passes it to a wav2vec2 speech emotion recognition model, which generates the end emotional reading. This *utterance alignment* is the core design feature in the architecture: sentiment analysis runs once per complete statement, on the audio that statement takes up. This allows for the transcript, translation, and emotion reading to all describe the same speech. Finally, the coach layer (Llama 3.2 3B running locally through Ollama) receives the English translation and tone result to generate brief feedback. All layers run in parallel threads so that no component blocks another.

We chose 2 pivotal design choices that would define our product. We analyze sentiment on the *original-language audio* rather than on translated text. Again, this is because transcriptions lose the emotional information, but acoustic features like tone and speech pacing survive language boundaries. Second, everything possible runs locally and for free. The emotion model and coach LLM are on-device, and hosted components like Deepgram and Google Translate have free tiers. This allows us to keep our product as low-cost as possible and separates Inflection from industry-standard enterprise alternatives.

*The current build is a terminal app using microphone input.*

## NLP Method and Evaluation



## User Evidence



## Ethics and Limitations