import pyaudio

# ============================================================
# Shared config constants used across audio / transcription
# ============================================================
FORMAT = pyaudio.paInt16  # Audio bit format (standard 16-bit Ints)
CHANNELS = 1  # Mono
RATE = 16000  # Samples per second
CHUNK = 1024  # How many audio samples are bundled together before sending back to api

# How long (ms) Deepgram waits after the last word before firing an
# UtteranceEnd event. Requires interim_results=True on the connection.
UTTERANCE_END_MS = 1000
 
# How much raw mic audio (seconds) to keep buffered so we can slice out the
# exact span an UtteranceEnd event refers to. 
# Utterances should pretty much never be older than this by the time UtteranceEnd fires.
AUDIO_BUFFER_SECONDS = 30.0


#------------------
# LLM Coach Config |
#------------------

# Ollama server URL (run `ollama serve`, then `ollama pull llama3.2:3b`)
OLLAMA_HOST = "http://localhost:11434"  # Ollama API host
COACH_MODEL = "llama3.2:3b" # small local instructional model for coaching. 

# OpenAI model config (used in LLM-Feedback-openai branch)
OPENAI_COACH_MODEL = "gpt-4o-mini"

# how many recent utterances to keep as context for the LLM (text + sentiment)
COACH_BUFFER_SIZE = 8

# minimum number of seconds between coach responses (to avoid spamming the user)
COACH_COOLDOWN_SECONDS = 20

# minimum sentiment intensity threshold for the coach to respond 
# (0.0 = respond to all, 1.0 = only respond to very strong sentiment)
COACH_INTENSITY_THRESHOLD = 0.0

OLLAMA_STARTUP_TIMEOUT = 30.0  # seconds to wait for Ollama server to start up

COACH_WARM_UP = True  # whether to warm up the model into memory on startup (recommended)

# List of languages supported by Deepgram API (for real time transcription)
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "ru": "Russian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "it": "Italian",
    "nl": "Dutch",
}
