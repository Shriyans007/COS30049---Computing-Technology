"""Sentence splitting and engineered writing-style features."""

import math
import re
import unicodedata
from collections import Counter

import pandas as pd


NUMERIC_FEATURES = [
    "char_count",
    "word_count",
    "avg_word_len",
    "vocab_div_ratio",
    "complex_word_ratio",
    "stopword_ratio",
    "upper_letter_ratio",
    "semicolon_dash_count",
    "char_entropy",
    "rep_bigram",
    "ai_tell_count",
    "doc_pos",
]

STOPWORDS = set(
    "a an the and or but if while of to in on for with as by at from "
    "is are were be been being this that these those it its he she "
    "they we you i not no do does did has have had will would can could "
    "should may might must about over under again further there here "
    "their our your".split()
)

AI_TELLS = {
    "delve", "tapestry", "underscore", "moreover", "furthermore",
    "in conclusion", "it is important to note", "a testament to",
    "navigating", "realm of", "leverage", "utilize", "facilitate",
    "comprehensive", "multifaceted", "nuanced", "paradigm", "ever-evolving",
    "crucial", "pivotal", "seamless", "robust", "holistic", "intricate",
    "plethora", "additionally", "in summary", "overall", "notably",
    "consequently", "in essence", "foster", "embark", "elevate", "unlock",
    "harness", "vibrant", "bustling", "meticulous", "testament",
    "landscape of", "world of", "when it comes to",
}


def _char_entropy(text: str) -> float:
    """Return Shannon entropy over the characters in a text sample."""
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _repetition_ratio(words: list[str], n: int = 2) -> float:
    """Return the proportion of repeated word n-grams."""
    if len(words) < n + 1:
        return 0.0
    ngrams = [tuple(words[index:index + n]) for index in range(len(words) - n + 1)]
    return 1.0 - len(set(ngrams)) / len(ngrams)


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
        "semicolon_dash_count": sentence.count(";") + sentence.count("-"),
        "char_entropy": _char_entropy(sentence),
        "rep_bigram": _repetition_ratio(lower_words),
        "ai_tell_count": sum(tell in sentence.lower() for tell in AI_TELLS),
        "doc_pos": position / position_denominator,
        # Retained outside NUMERIC_FEATURES so older saved pipelines still load.
        "numeric_digit_ratio": sum(char.isdigit() for char in sentence) / max(char_count, 1),
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


def text_to_document_feature_frame(text: str) -> pd.DataFrame:
    """Create the single-row representation used by the document model."""
    cleaned = clean_text(text)
    if not re.search(r"\w", cleaned):
        raise ValueError("Text must contain at least one word.")
    return pd.DataFrame(
        [
            {
                "doc_id": 0,
                "sent_id": 0,
                "sample_id": "0:0",
                "text": cleaned,
                **sentence_features(cleaned, 0, 1),
            }
        ]
    )
