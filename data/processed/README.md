# Local processed dataset

Place Person 2's combined sentence-level CSV in this folder and rename it to:

`final_dataset.csv`

The expected local path is:

`data/processed/final_dataset.csv`

Place the supplied document-level CSV at:

`data/processed/para_dataset.csv`

Despite its original name, each row in `para_dataset.csv` contains one complete
source document/essay. Its `sent_id` column may remain present with the value 0.
The two files are trained and evaluated separately; they must not be combined.

Then train and compare all three models from the repository root:

```bash
python -m classification.train
```

Train the document-level experiment with:

```bash
python -m classification.train --unit document
```

The CSV is intentionally ignored by Git because it exceeds GitHub's file-size
limit. This instruction file keeps the folder available after cloning or
pulling the repository.

# Processed Datasets code

Two CSV files are required here, generated locally (not committed — exceed GitHub size limit):

Trained separately. Do not combine.

Labels: `0` = human, `1` = AI.

## Features

| Feature | Captures |

| `char_count` | Raw sentence length |
| `word_count` | Verbosity — AI tends toward uniform lengths |
| `avg_word_len` | Lexical complexity |
| `vocab_div_ratio` | Type-token ratio — lexical diversity |
| `complex_word_ratio` | Proportion of words ≥7 chars — sophistication |
| `stopword_ratio` | Function-word usage — strong stylometric signal |
| `upper_letter_ratio` | Emphasis style — humans capitalise more |
| `semicolon_dash_count` | Punctuation style |
| `char_entropy` | Shannon entropy — perplexity proxy, AI is "too smooth" |
| `rep_bigram` | Bigram repetition — AI loops phrasing |
| `ai_tell_count` | AI-associated lexicon hits (e.g. *delve*, *multifaceted*) |
| `doc_pos` | Normalised position in document |

## How to regenerate

Place these three source CSVs in the same folder as `final_dataset.py` and `para_dataset.py`:

- `train_v2_drcat_02.csv`
- `HC3_en_train_data.csv`
- `data_for_preprocessing.csv`
