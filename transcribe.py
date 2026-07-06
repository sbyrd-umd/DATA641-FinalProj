import pyaudio
import threading
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from dotenv import load_dotenv
import os

# ============================================================
# Config
# ============================================================
load_dotenv()
FORMAT = pyaudio.paInt16 # Audio bit format (standard 16-bit Ints)
CHANNELS = 1 # Mono
RATE = 16000 # Samples per second
CHUNK = 1024 # How many audio samples are bundled together before sending back to api
client = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

# ============================================================
# API connection and real time transcript printing
# ============================================================
with client.listen.v1.connect(
    model="nova-3",
    language="en",
    encoding="linear16",
    sample_rate=RATE,
) as connection:

    ready = threading.Event() # Ready to send audio flag initialised, synchronizes threads (main and stream)

    def on_message(result): # Prints transcript back
        if result.type == "Results": 
            transcript = result.channel.alternatives[0].transcript # Grab top confidence transcript from JSON
            if transcript:
                print(f"Transcript: {transcript}")

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