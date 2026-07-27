import os

from deepgram import DeepgramClient

from ..config import LANGUAGES
from .translation import get_translator


def make_client() -> DeepgramClient:
    """Create a Deepgram client using DEEPGRAM_API_KEY from the environment."""
    return DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))


def open_connection(client: DeepgramClient, sample_rate: int):
    """Open a real-time Deepgram listen connection with our standard settings."""
    return client.listen.v1.connect(
        model="nova-3",
        language="multi",  # allows constant language detection
        encoding="linear16",
        sample_rate=sample_rate,
        endpointing=100,  # recommended setting by deepgram
    )


def make_on_message(print_fn=print):
    """
    Build an on_message handler for Deepgram transcription events.
    Prints the transcript in its original language, plus an English
    translation if the detected language isn't already English.
    """

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
                print_fn(f"Original ({lang_name}): {transcript}")

                if lang_code != "en":  # if detected language is not English, translate to English
                    try:
                        translated = get_translator(lang_code).translate(transcript)
                        print_fn(f"Translated (English): {translated}")
                    except Exception as e:
                        print_fn(f"Translation error: {e}")

    return on_message
