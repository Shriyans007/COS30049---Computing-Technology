"""Sentence splitting and engineered writing-style features."""

import re
import unicodedata

import pandas as pd


NUMERIC_FEATURES = [
    "char_count",
    "word_count",
    "avg_word_len",
    "vocab_div_ratio",
    "complex_word_ratio",
    "stopword_ratio",
    "upper_letter_ratio",
    "numeric_digit_ratio",
    "semicolon_dash_count",
    "doc_pos",
    "is_first_sent",
    "is_last_sent",
]

STOPWORDS = set(
    "a an the and or but if while of to in on for with as by at from "
    "is are were be been being this that these those it its he she "
    "they we you i".split()
)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip()


def split_sentences(text: str) -> list[str]:
    cleaned = clean_text(text)
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if re.search(r"\w", part)]


def sentence_features(sentence: str, position: int, total_sentences: int) -> dict[str, float | int]:
    words = re.findall(r"\b\w+\b", sentence)
    lower_words = [word.lower() for word in words]
    word_count = len(words)
    char_count = len(sentence)
    denominator = max(word_count, 1)
    position_denominator = max(total_sentences - 1, 1)
    return {
        "char_count": char_count,
        "word_count": word_count,
        "avg_word_len": sum(len(word) for word in words) / denominator,
        "vocab_div_ratio": len(set(lower_words)) / denominator,
        "complex_word_ratio": sum(len(word) >= 7 for word in words) / denominator,
        "stopword_ratio": sum(word in STOPWORDS for word in lower_words) / denominator,
        "upper_letter_ratio": sum(char.isupper() for char in sentence) / max(char_count, 1),
        "numeric_digit_ratio": sum(char.isdigit() for char in sentence) / max(char_count, 1),
        "semicolon_dash_count": len(re.findall(r";\s*[-–—]", sentence)),
        "doc_pos": position / position_denominator,
        "is_first_sent": int(position == 0),
        "is_last_sent": int(position == total_sentences - 1),
    }


def text_to_feature_frame(text: str) -> pd.DataFrame:
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError("Text must contain at least one word.")
    rows = []
    for position, sentence in enumerate(sentences):
        rows.append({
            "doc_id": 0,
            "sent_id": position,
            "sample_id": f"0:{position}",
            "text": sentence,
            **sentence_features(sentence, position, len(sentences)),
        })
    return pd.DataFrame(rows)
