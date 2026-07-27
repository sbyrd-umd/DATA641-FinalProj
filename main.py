import threading

from deepgram.core.events import EventType
from dotenv import load_dotenv

from src.audio import MicStreamer
from src.config import CHANNELS, CHUNK, FORMAT, RATE
from src.sentiment import SentimentAnalyzer
from src.transcription import make_client, make_on_message, open_connection

load_dotenv()


# =======================================================================
# Sentiment result callback (runs parallel to translation/transcription) |
# =======================================================================
def on_sentiment_result(result):
    flag = " !! " if result["flagged"] else "    "
    print(
        f"{flag}Sentiment: {result['label']}"
        f"(arousal: {result['arousal']:.2f}, "
        f"valence: {result['valence']:.2f}, "
        f"dominance: {result['dominance']:.2f})"
    )


def main():
    client = make_client()

    sentiment = SentimentAnalyzer(
        on_result=on_sentiment_result, window_seconds=3.0, hop_seconds=1.5, sample_rate=RATE
    )
    sentiment.start()

    # =================================================
    # API connection and real time transcript printing |
    # =================================================
    with open_connection(client, RATE) as connection:
        ready = threading.Event()  # ready to send audio flag, synchronizes threads (main and stream)

        connection.on(EventType.OPEN, lambda _: ready.set())  # connection ready -> set ready flag
        connection.on(EventType.MESSAGE, make_on_message())  # message arrives -> print transcript/translation
        connection.on(EventType.ERROR, lambda e: print(f"Error: {e}"))  # print any error to terminal

        mic = MicStreamer(FORMAT, CHANNELS, RATE, CHUNK, ready)
        mic.start(connection.send_media, sentiment.feed)  # launch mic streaming on a background thread

        try:
            connection.start_listening()  # start listening for Deepgram API responses (blocking call)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            mic.stop()
            sentiment.stop()


if __name__ == "__main__":
    main()
