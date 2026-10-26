"""Narrow, documented normalisation for Unicode detection-evasion attacks."""

import re
import unicodedata


ZERO_WIDTH_AND_FORMAT = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
WHITESPACE = re.compile(r"\s+")

# Deliberately limited to common Latin look-alikes used by the experiment.
# A broad transliteration would damage legitimate multilingual text.
CONFUSABLES = str.maketrans(
    {
        "а": "a", "А": "A", "е": "e", "Е": "E", "о": "o", "О": "O",
        "р": "p", "Р": "P", "с": "c", "С": "C", "х": "x", "Х": "X",
        "і": "i", "І": "I", "ј": "j", "Ј": "J", "у": "y", "У": "Y",
        "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I",
        "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T",
        "Χ": "X", "Υ": "Y", "ο": "o", "ρ": "p", "ν": "v",
    }
)


def normalise_security_text(text: str) -> str:
    normalised = unicodedata.normalize("NFKC", text)
    normalised = ZERO_WIDTH_AND_FORMAT.sub("", normalised)
    normalised = normalised.translate(CONFUSABLES)
    normalised = "".join(
        character
        for character in normalised
        if unicodedata.category(character) not in {"Cc", "Cs"} or character in "\n\t"
    )
    return WHITESPACE.sub(" ", normalised).strip()
