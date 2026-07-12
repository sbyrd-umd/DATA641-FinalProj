
import pyaudio
import threading
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from dotenv import load_dotenv
import os
from deep_translator import GoogleTranslator

# ============================================================
# Config
# ============================================================
load_dotenv()
FORMAT = pyaudio.paInt16 # Audio bit format (standard 16-bit Ints)
CHANNELS = 1 # Mono
RATE = 16000 # Samples per second
CHUNK = 1024 # How many audio samples are bundled together before sending back to api
client = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

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

# Removed the user input for language selection
# Added cache for each GoogleTranslator object per language detected 
# instead of rebuilding every line.
# Defailts to English if language not supported by Deepgram API

translators = {}
def get_translator(lang_code):
    if lang_code not in translators:
        translators[lang_code] = GoogleTranslator(source=lang_code, target="en")
    return translators[lang_code]

# ============================================================
# API connection and real time transcript printing
# ============================================================
with client.listen.v1.connect(
    model="nova-3",
    language="multi",   # allows constant language detection
    encoding="linear16",
    sample_rate=RATE,
    endpointing=100,    # recomended setting by deepgram
) as connection:

    ready = threading.Event() # Ready to send audio flag initialised, synchronizes threads (main and stream)

    def on_message(result): # Prints transcript back (in original language), with translation to English
        if result.type == "Results":
            alt = result.channel.alternatives[0]
            transcript = alt.transcript    # grab top confidence transcript
            
            if transcript: # If transcript is not empty
                
                if hasattr(alt, 'languages') and alt.languages:
                    lang_code = alt.languages[0]    # first lang in list
                else: 
                    lang_code = 'en'    # default to english
                
                lang_name = LANGUAGES.get(lang_code, lang_code) # grab the language name or default to code

                # print transcript in original lang
                print(f"Original ({lang_name}): {transcript}")
                
                if lang_code != "en": # If detected language is not English, translate to English
                    try:
                        translated = get_translator(lang_code).translate(transcript)
                        print(f"Translated (English): {translated}")
                    except Exception as e:
                        print(f"Translation error: {e}")

    # Event listeners
    connection.on(EventType.OPEN, lambda _: ready.set()) # When connection ready set ready to send audio flag on go
    connection.on(EventType.MESSAGE, on_message) # When a message arrives on_message
    connection.on(EventType.ERROR, lambda e: print(f"Error: {e}")) # Print any error to terminal

    def stream(): # Runs on separate thread (main thread listens for Deepgram API responses)

        ready.wait() # Pause until connection is OPEN (wait for flag to be set)
        audio = pyaudio.PyAudio() # Stars PyAudio engine
        mic = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK) # Opens stream from mic (capturing audio)
        print("Listening... Press Ctrl+C to stop.")

        try:
            while True:
                data = mic.read(CHUNK, exception_on_overflow=False) # Grab next 1024 audio samples, don't crash if buffer fills up
                connection.send_media(data) # Send chunk to Deepgram (in real time)
        except KeyboardInterrupt: # On Ctrl + C shutdown mic stream and PyAudio engine
            mic.stop_stream()
            mic.close()
            audio.terminate()

    threading.Thread(target=stream, daemon=True).start() # Launch stream on a separate (background, killed automatically) thread
    connection.start_listening() # Wait for Deepgram api responses (fires on_message everytime a response arrives)