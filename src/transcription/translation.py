from deep_translator import GoogleTranslator

# Cache of GoogleTranslator objects per detected language, so we don't
# rebuild one every line.
_translators = {}


def get_translator(lang_code: str) -> GoogleTranslator:
    """Return a cached GoogleTranslator for lang_code -> English, creating one if needed."""
    if lang_code not in _translators:
        _translators[lang_code] = GoogleTranslator(source=lang_code, target="en")
    return _translators[lang_code]
