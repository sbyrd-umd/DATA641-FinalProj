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
