"""Security validation performed before model work begins."""

import unicodedata

from classification.features import split_sentences

from .config import Settings
from .errors import AppError


def validate_prediction_text(text: str, settings: Settings) -> str:
    if not text.strip():
        raise AppError(400, "EMPTY_TEXT", "Text must contain visible writing.")
    byte_count = len(text.encode("utf-8"))
    if len(text) > settings.max_characters or byte_count > settings.max_bytes:
        raise AppError(
            413,
            "TEXT_TOO_LARGE",
            f"Text must not exceed {settings.max_characters} characters or {settings.max_bytes} UTF-8 bytes.",
        )
    if len(text.strip()) < settings.min_characters:
        raise AppError(400, "TEXT_TOO_SHORT", f"Text must contain at least {settings.min_characters} characters.")
    unsafe_controls = [
        character
        for character in text
        if unicodedata.category(character) in {"Cc", "Cs"} and character not in "\n\r\t"
    ]
    if unsafe_controls:
        raise AppError(400, "UNSAFE_CONTROL_CHARACTER", "Text contains unsupported control characters.")
    sentence_count = len(split_sentences(text))
    if sentence_count == 0:
        raise AppError(400, "NO_WORDS", "Text must contain at least one word.")
    if sentence_count > settings.max_sentences:
        raise AppError(413, "TOO_MANY_SENTENCES", f"Text must not exceed {settings.max_sentences} sentences.")
    return text
