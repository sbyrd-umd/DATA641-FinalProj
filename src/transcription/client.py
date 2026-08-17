import os
from typing import List, Optional

from deepgram import DeepgramClient

from ..config import LANGUAGES, UTTERANCE_END_MS
from .translation import get_translator


def make_client() -> DeepgramClient:
    """Create a Deepgram client using DEEPGRAM_API_KEY from the environment."""
    return DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))


def open_connection(client: DeepgramClient, sample_rate: int, utterance_end_ms: int = UTTERANCE_END_MS):
    """Open a real-time Deepgram listen connection with our standard settings.
    
        interim_results + utterance_end_ms are required for Deepgram to emit
        UtteranceEnd events.
    """
    return client.listen.v1.connect(
        model="nova-3",
        language="multi",  # allows constant language detection
        encoding="linear16",
        sample_rate=sample_rate,
        endpointing=100,  # recommended setting by deepgram
        interim_results=True,   # Required for utterance end
        utterance_end_ms=utterance_end_ms
    )

# new class to track the utterances
class _UtteranceTracker:
    """
    Accumulates finalized transcript pieces and their time range since the
    last utterance boundary.
    """

    def __init__(self):
        self._start: Optional[float] = None     # Start time
        self._end: Optional[float] = None       # End time
        self._parts: List[str] = []             # transcript parts
        self._translated_parts: List[str] = []
        self._lang_code: str = "en"

    def add_final(self, start: float, duration: float, text: str, translated: str, lang_code: str):
        """Record a finalized (is_final=True) transcript chunk."""
        if self._start is None:
            self._start = start
        self._end = start + duration
        if text:
            self._parts.append(text)
            self._translated_parts.append(translated)
        self._lang_code = lang_code 

    def close(self, last_word_end: float):
        """
        Called on UtteranceEnd. Returns (start, end, text), or None if
        nothing was accumulated.
        """
        if self._start is None:
            return None

        start = self._start
        end = max(self._end or last_word_end, last_word_end)
        text = " ".join(self._parts)
        translated = " ".join(self._translated_parts) # Build translated text
        lang_code = self._lang_code

        self._start = None
        self._end = None
        self._parts = []
        self._translated_parts = []
        self._lang_code = "en"

        return start, end, text, translated, lang_code


def make_on_message(on_utterance=None, print_fn=print):
    """
    Build an on_message handler for Deepgram transcription events.
    Prints the transcript in its original language, plus an English
    translation if the detected language isn't already English. Also tracks
    finalized chunks across an utterance, so that when Deepgram signals
    UtteranceEnd, `on_utterance(start_sec, end_sec, transcript)` is called
    with that utterance's full time range and text.
    """
    
    tracker = _UtteranceTracker()

    def on_message(result):
        if result.type == "Results":
            alt = result.channel.alternatives[0]
            transcript = alt.transcript  # grab top confidence transcript

            if transcript:  # if transcript is not empty
                if hasattr(alt, "languages") and alt.languages:
                    lang_code = alt.languages[0]  # first lang in list
                else:
                    lang_code = "en"  # default to english

                lang_name = LANGUAGES.get(lang_code, lang_code)  # grab the language name or default to code

                # print transcript in original lang
                if result.is_final: # Only print and track on final result
                    print_fn(f"Original ({lang_name}): {transcript}")

                    if lang_code != "en":  # if detected language is not English, translate to English
                        try:
                            translated = get_translator(lang_code).translate(transcript)
                            print_fn(f"Translated (English): {translated}")
                        except Exception as e:
                            print_fn(f"Translation error: {e}")
                            translated = transcript
                    else:
                        translated = transcript
                            
                    tracker.add_final(result.start, result.duration, transcript, translated, lang_code)
                    
        elif result.type == "UtteranceEnd":
            closed = tracker.close(result.last_word_end)
            if closed and on_utterance:
                start, end, text, translated, lang_code = closed           
                on_utterance(start, end, text, translated, lang_code)

    return on_message