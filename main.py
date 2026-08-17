import threading
import uuid
from deepgram.core.events import EventType
from dotenv import load_dotenv
from src.audio import AudioTimeline, MicStreamer
from src.coaching import CoachingEngine, OllamaServer
from src.config import (
    AUDIO_BUFFER_SECONDS, 
    CHANNELS, 
    CHUNK, 
    FORMAT, 
    RATE,
    COACH_BUFFER_SIZE,
    COACH_COOLDOWN_SECONDS,
    COACH_INTENSITY_THRESHOLD,
    COACH_MODEL,
    COACH_WARM_UP,
    OLLAMA_HOST,
    OLLAMA_STARTUP_TIMEOUT,
    )
from src.evaluation.logger import log_utterance, log_coaching
from src.sentiment import SentimentAnalyzer
from src.transcription import make_client, make_on_message, open_connection

load_dotenv()


# =====================================================
# Sentiment result callback (fires once per utterance) |
# =====================================================

def make_on_sentiment_result(coach: CoachingEngine, session_id: str):
    def on_sentiment_result(result):
        flag = " !! " if result["flagged"] else "    "
        print(
            f"{flag}Sentiment: {result['label']}"
            f"(arousal: {result['arousal']:.2f}, "
            f"valence: {result['valence']:.2f}, "
            f"dominance: {result['dominance']:.2f})"
        )
        metadata = result.get("metadata")
        if not metadata:
            return

        utterance_id = metadata["utterance_id"]   # extract from dict
        text = metadata["text"]                    # translated
        original = metadata["original"]            # original language
        language = metadata["language"]            # lang code

        log_utterance(                             # log every utterance
            utterance_id=utterance_id,
            session_id=session_id,
            language=language,
            original_text=original,
            translated_text=text,
            arousal=result["arousal"],
            valence=result["valence"],
            dominance=result["dominance"],
            label=result["label"],
            intensity=result["intensity"],
            flagged=result["flagged"],
        )

        coach.feed(text, result, utterance_id)   

    return on_sentiment_result

# =====================================================
# Coaching note callback (fires occasionally, only on  |
# flagged sentiment + past cooldown -- see coach.py)   |
# =====================================================

def on_coaching_note(note: str, utterance_id: str, latency_ms: float):
    print(f"\n[COACH]\n{note}\n")
    log_coaching(utterance_id, note, latency_ms) # Log coaching note


def main():
    client = make_client()
    session_id = str(uuid.uuid4())                 # one session id per run
    
    ollama_server = OllamaServer(host=OLLAMA_HOST, model=COACH_MODEL, startup_timeout=OLLAMA_STARTUP_TIMEOUT)
    ollama_server.start(warm_up=COACH_WARM_UP)
    
    coach = CoachingEngine(
        on_note=on_coaching_note,
        model=COACH_MODEL,
        host=OLLAMA_HOST,
        buffer_size=COACH_BUFFER_SIZE,
        cooldown_seconds=COACH_COOLDOWN_SECONDS,
        intensity_threshold=COACH_INTENSITY_THRESHOLD,
    )
    coach.start()

    # removed window_seconds and hop_seconds cuz we dont need
    sentiment = SentimentAnalyzer(on_result=make_on_sentiment_result(coach, session_id), sample_rate=RATE)
    sentiment.start()
    
    timeline = AudioTimeline(sample_rate=RATE, max_buffer_seconds=AUDIO_BUFFER_SECONDS)
    
    def on_utterance(start_sec, end_sec, transcript, translated, language):
        """Called once Deepgram signals an utterance just finished (UtteranceEnd).
        Slices that exact audio span out of the timeline and queues it for
        sentiment inference, so sentiment is tied to the same sound bite as
        the transcript/translation instead of a fixed clock."""
        
        segment = timeline.slice_seconds(start_sec, end_sec)
        if segment is not None:
            sentiment.feed_segment(segment, metadata={   # metadata is now a dict
                "utterance_id": str(uuid.uuid4()),
                "text": translated,
                "original": transcript,
                "language": language,
            })
    

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
            coach.stop()
            ollama_server.stop()


if __name__ == "__main__":
    main()
