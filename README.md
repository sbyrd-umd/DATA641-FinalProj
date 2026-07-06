# DATA641-FinalProj

**Persona:** A QA manager or team lead at a BPO or international support org whose agents now handle calls in languages neither the agent nor the manager speaks

**Pain:**  The agent already can't hear tone in a foreign language even with translation running (translation renders words, not feeling), and when she reviews the call afterward, she's reading a translated transcript that's lost whatever emotional signal survived the live call in the first place.

**Hack:** Nothing... she doesn't speak the language. So you must hire an entire team that speaks that language

**Solution**: A tone-detection layer that reads the original audio directly (before or in parallel with translation), flags emotional intensity/distress in real time regardless of language, and archives it alongside the translated transcript. If we have time, feed both into live coaching LLM.

**Why us**: Products like this exist (CallMiner's LiveTranslate) and has more features. However, from our research, there is only one other company in this market which means almost no competition.

A user can **use our product in real time** and get **live translation PAIRED WITH live sentiment analysis and live feedback coaching**.


**Structure:**
- Sentiment analysis via open source like wav2vec2
- LLM for coaching/summary layer
- DONT build the translator, there are APIs that already exist which we can leverage.
- Run translator and Sentiment analysis in parallel and feed into LLM for live feedback

--- 

## Setup

### Prerequisites
- Python 3.x
- A Deepgram API key - sign up free at [deepgram.com](https://deepgram.com)

### Installation
#### 1. Clone repo: 
```bash
git clone <repo-url>
cd DATA641-FinalProj
```

#### 2. Create a virtual environment outside the repo folder:
```bash
python -m venv ../SERvenv
```

#### 3. Activate it:
Windows
```bash
..\SERvenv\Scripts\activate
```
Mac/Linux
```bash
source ../SERvenv/bin/activate
```

#### 4. Install dependencies:
```bash
pip install -r requirements.txt
```

#### 5. Create a .env file in the root of the repo:
```
DEEPGRAM_API_KEY=your_key_here
```

### Running
```bash 
python transcribe.py
```
You will be prompted to select a source language. Once selected, speak into your microphone and the terminal will print the original transcript alongside the English translation in real time.