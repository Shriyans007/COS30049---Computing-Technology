import os
import re
import math
import unicodedata
from collections import Counter

import pandas as pd


# PATHS 
DATA_DIR    = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
BASE_PATH   = os.path.join(DATA_DIR, "train_v2_drcat_02.csv")
EXTRA_PATHS = [
    os.path.join(DATA_DIR, "HC3_en_train_data.csv"),
    os.path.join(DATA_DIR, "data_for_preprocessing.csv"),
]
OUTPUT_PATH = os.path.join(DATA_DIR, "para_dataset.csv")


# TEXT CLEANING 
def clean_text(t: str) -> str:
    
    t = unicodedata.normalize("NFKC", str(t))
    t = re.sub(r"\s+", " ", t).strip()
    return t


_BLOB_TOKEN_RE = re.compile(r"\b(?=[A-Za-z0-9]{40,})(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+\b")

def strip_blob_suffix(text: str) -> str:
   
    return _BLOB_TOKEN_RE.sub("", text).strip()


_URL_RE = re.compile(r"https?://\S+|www\.\S+")

def replace_urls(text: str) -> str:
    """Replace URLs with <URL>."""
    return _URL_RE.sub("<URL>", text)


_STUTTER_RE  = re.compile(r"\b(\w)(?:-\1){5,}\w?\b", re.IGNORECASE)
_DASH_RUN_RE = re.compile(r"[-_=]{5,}")

def strip_stutter_and_dash_runs(text: str) -> str:
    """Remove repeated-character runs and dash separators."""
    text = _STUTTER_RE.sub("", text)
    text = _DASH_RUN_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


# INVALID ENTRY FILTER 
MIN_CHARS = 20
MIN_WORDS = 5

def is_invalid_entry(text: str) -> bool:
    """True if too short or dominated by non-letters."""
    text = str(text).strip()
    if len(text) < MIN_CHARS:
        return True
    if len(re.findall(r"\b\w+\b", text)) < MIN_WORDS:
        return True
    return sum(c.isalpha() for c in text) / len(text) < 0.40


# FEATURE HELPERS 
_STOPWORDS = set(
    "a an the and or but if while of to in on for with as by at from "
    "is are were be been being this that these those it its he she "
    "they we you i not no do does did has have had will would can could "
    "should may might must about over under again further there here "
    "their our your".split()
)

_AI_TELLS = {
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
   
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _repetition_ratio(words: list, n: int) -> float:
  
    if len(words) < n + 1:
        return 0.0
    ngrams = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
    return 1.0 - (len(set(ngrams)) / len(ngrams)) if ngrams else 0.0


# DOCUMENT-LEVEL FEATURES 
def document_features(text: str) -> dict:
   
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    if word_count == 0:
        return None

    char_count     = len(text)
    lower_words    = [w.lower() for w in words]
    unique_words   = len(set(lower_words))
    long_words     = sum(1 for w in words if len(w) >= 7)
    stopword_count = sum(1 for w in lower_words if w in _STOPWORDS)
    uppercase      = sum(1 for c in text if c.isupper())

    return {
        "char_count":           char_count,
        "word_count":           word_count,
        "avg_word_len":         round(char_count / word_count, 2),
        "vocab_div_ratio":      round(unique_words / word_count, 2),
        "complex_word_ratio":   round(long_words / word_count, 2),
        "stopword_ratio":       round(stopword_count / word_count, 2),
        "upper_letter_ratio":   round(uppercase / max(char_count, 1), 2),
        "semicolon_dash_count": text.count(";") + text.count("-"),
        "char_entropy":         round(_char_entropy(text), 3),
        "rep_bigram":           round(_repetition_ratio(lower_words, 2), 3),
        "ai_tell_count":        sum(1 for t in _AI_TELLS if t in text.lower()),
        "doc_pos":              0.0,   # single-unit document
    }



def clean_pipeline(text_series):
    """Full cleaning chain """
    return (text_series
            .apply(clean_text)
            .apply(replace_urls)
            .apply(strip_blob_suffix)
            .apply(strip_stutter_and_dash_runs))


# BASE DATASET 

print("Loading base dataset: train_v2_drcat_02.csv")


df = pd.read_csv(BASE_PATH).rename(columns={"prompt_name": "prompt"})
df = df[["text", "label", "source", "prompt"]].copy()
n_start = len(df)

df["text"] = clean_pipeline(df["text"])

n_before = len(df)
df = df.dropna(subset=["text", "label"])
df = df[df["text"].str.strip() != ""]
n_missing = n_before - len(df)

n_before = len(df)
df = df.drop_duplicates(subset=["text"])
n_dupes = n_before - len(df)

df["label"] = df["label"].astype(int)

print(f"  Rows: {n_start} -> {len(df)}  (missing={n_missing}, duplicates={n_dupes})")
print(f"  Label balance: {df['label'].value_counts().to_dict()}")


# EXTRA DATASETS 
LABEL_MAP = {
    "AI": 1, "ai": 1, "machine": 1, "generated": 1, "chatgpt": 1, "gpt": 1,
    "Human": 0, "human": 0, "real": 0,
}

for path in EXTRA_PATHS:
    name = os.path.basename(path)
    print(f"\nLoading extra dataset: {name}")

    extra = pd.read_csv(path)
    print(f"  Raw columns: {list(extra.columns)}")

    rename_map = {}
    for col in extra.columns:
        low = str(col).strip().lstrip("\ufeff").lower()
        if low in ("text", "content", "abstract", "essay", "body"):
            rename_map[col] = "text"
        elif low in ("author", "label", "target", "class", "is_ai",
                     "category", "type", "origin", "source"):
            rename_map[col] = "label"
    extra = extra.rename(columns=rename_map)

    if "text"  not in extra.columns and "Text"   in extra.columns:
        extra = extra.rename(columns={"Text": "text"})
    if "label" not in extra.columns and "Author" in extra.columns:
        extra = extra.rename(columns={"Author": "label"})

    print(f"  Columns after rename: {list(extra.columns)}")

    if "text" not in extra.columns or "label" not in extra.columns:
        raise ValueError(f"{name}: no text/label columns. Found: {list(extra.columns)}")

    extra = extra[["text", "label"]].copy()

    if extra["label"].dtype == object:
        extra["label"] = extra["label"].astype(str).str.strip().map(LABEL_MAP)
        n_unmapped = extra["label"].isna().sum()
        if n_unmapped:
            print(f"  WARNING: {n_unmapped} rows had unmapped labels - dropping.")
            extra = extra.dropna(subset=["label"])
        extra["label"] = extra["label"].astype(int)

    extra["source"] = name.replace(".csv", "")
    extra["prompt"] = "unknown"

    n_start = len(extra)
    extra["text"] = clean_pipeline(extra["text"])

    n_before = len(extra)
    extra = extra.dropna(subset=["text", "label"])
    extra = extra[extra["text"].str.strip() != ""]
    n_missing = n_before - len(extra)

    n_before = len(extra)
    extra = extra.drop_duplicates(subset=["text"])
    n_dupes = n_before - len(extra)

    extra = extra[["text", "label", "source", "prompt"]]

    print(f"  Rows: {n_start} -> {len(extra)}  (missing={n_missing}, duplicates={n_dupes})")
    print(f"  Label balance: {extra['label'].value_counts().to_dict()}")

    df = pd.concat([df, extra], ignore_index=True)


# POST-MERGE CLEANING 

print("\nPost-merge cleaning")


n_before = len(df)
df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)


n_before = len(df)
df = df[~df["text"].apply(is_invalid_entry)].reset_index(drop=True)
print(f"\nInvalid/short entries removed: {n_before - len(df)}")

df["doc_id"] = df.index

print(f"\nTotal unique documents: {len(df)}")
print(f"\nLabel balance:\n{df['label'].value_counts().to_string()}")



# DOCUMENT-LEVEL FEATURES


rows = []
for _, r in df.iterrows():
    feats = document_features(r["text"])
    if feats is None:
        continue
    rows.append({
        "doc_id":  r["doc_id"],
        "sent_id": 0,                    
        "text":    r["text"],
        "label":   r["label"],
        "source":  r["source"],
        "prompt":  r["prompt"],
        **feats,
    })

para_df = pd.DataFrame(rows)
para_df.to_csv(OUTPUT_PATH, index=False)


print(f"Total documents: {len(para_df)}")
print(f"CSV saved")

