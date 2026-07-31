import threading

from deepgram.core.events import EventType
from dotenv import load_dotenv

from src.audio import AudioTimeline, MicStreamer
from src.config import AUDIO_BUFFER_SECONDS, CHANNELS, CHUNK, FORMAT, RATE
from src.sentiment import SentimentAnalyzer
from src.transcription import make_client, make_on_message, open_connection

load_dotenv()


# =====================================================
# Sentiment result callback (fires once per utterance) |
# =====================================================
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

    # removed window_seconds and hop_seconds cuz we dont need
    sentiment = SentimentAnalyzer(on_result=on_sentiment_result, sample_rate=RATE)
    sentiment.start()
    
    timeline = AudioTimeline(sample_rate=RATE, max_buffer_seconds=AUDIO_BUFFER_SECONDS)
    
    def on_utterance(start_sec, end_sec, transcript):
        """Called once Deepgram signals an utterance just finished (UtteranceEnd).
        Slices that exact audio span out of the timeline and queues it for
        sentiment inference, so sentiment is tied to the same sound bite as
        the transcript/translation instead of a fixed clock."""
        
        segment = timeline.slice_seconds(start_sec, end_sec)
        if segment is not None:
            sentiment.feed_segment(segment)
    

    # =================================================
    # API connection and real time transcript printing |
    # =================================================
    with open_connection(client, RATE) as connection:
        ready = threading.Event()  # ready to send audio flag, synchronizes threads (main and stream)

        connection.on(EventType.OPEN, lambda _: ready.set())  # connection ready -> set ready flag
        connection.on(EventType.MESSAGE, make_on_message(on_utterance=on_utterance))  # message arrives -> print transcript/translation trigger sentiment analysis
        connection.on(EventType.ERROR, lambda e: print(f"Error: {e}"))  # print any error to terminal

        mic = MicStreamer(FORMAT, CHANNELS, RATE, CHUNK, ready)
        mic.start(connection.send_media, timeline.append)  # launch mic streaming on a background thread

        try:
            connection.start_listening()  # start listening for Deepgram API responses (blocking call)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            mic.stop()
            sentiment.stop()


if __name__ == "__main__":
    main()
