# COS30049 AI-Generated Content Detection

Assignment 2 machine-learning code for classifying human-written and
AI-generated text. The frontend is intentionally out of scope.

## Current results

Person 2 supplied two representations of the combined three-source dataset.
They are trained separately:

- Sentence level: 1,573,082 input rows. Conflict and duplicate cleanup leaves
  1,262,979 sentences from 120,069 documents.
- Document level: 122,740 rows, each containing one complete original
  document/essay. The file is named `para_dataset.csv`, but its rows are whole
  documents rather than individual paragraphs.

Both workflows use reproducible stratified 70/15/15 train/validation/test
partitions. Sentence rows are grouped by `doc_id`, preventing sentences from
one essay appearing across different partitions.

### Sentence-level test results

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.8099 | 0.6848 | 0.8341 | 0.7521 |
| Linear SVM | **0.8901** | **0.8175** | **0.8781** | **0.8468** |
| XGBoost | 0.7759 | 0.7882 | 0.4809 | 0.5973 |

### Document-level test results

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.9612 | 0.9642 | 0.9235 | 0.9434 |
| Linear SVM | **0.9897** | **0.9850** | **0.9857** | **0.9853** |
| XGBoost | 0.9543 | 0.9543 | 0.9132 | 0.9333 |

Linear SVM was selected independently for both levels because it had the
highest validation F1. Its returned score is a signed decision score, not a
probability. The document model is recommended when the application receives
a complete essay because it uses the full context and performed much better on
its held-out documents. Sentence and document metrics use different evaluation
units, so they are not a direct like-for-like comparison.

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Dataset

The CSVs are not committed because they exceed GitHub's file-size limit.
Recommended local paths are:

- `data/processed/final_dataset.csv` for sentence rows
- `data/processed/para_dataset.csv` for complete documents

Required columns:

| Column | Purpose |
| --- | --- |
| doc_id | Original document identifier used for grouped splitting |
| sent_id | Sentence order; it may be 0 for every document-level row |
| text | Sentence text or complete document text |
| label | 0 for human and 1 for AI |

The supplied `source` and `prompt` columns are retained for tracing results but
are not model inputs. TF-IDF unigrams/bigrams are combined with the numeric
writing-style features. The loader verifies and repairs derived feature values
from the text. TF-IDF and numeric scaling are fitted only on training data
inside each saved pipeline.

## Train and compare

Sentence model from a CSV:

```bash
python -m classification.train --dataset data/processed/final_dataset.csv
```

Document model from a CSV:

```bash
python -m classification.train --unit document --dataset data/processed/para_dataset.csv
```

The supplied ZIPs can also be used without extracting them:

```bash
python -m classification.train --dataset "final_dataset.csv.zip" --zip-member "final_dataset.csv"
python -m classification.train --unit document --dataset "Para dataset.zip" --zip-member "Para dataset/para_dataset.csv"
```

All three models use the same split and feature representation within each
experiment. Logistic Regression uses stochastic gradient descent with logistic
loss because the sentence dataset has more than one million sparse text rows.
XGBoost uses 80 histogram-based boosted trees without a large tuning search.

Generated summary files and saved models:

- `outputs/classification/` for sentence results
- `artifacts/classification/` for the selected sentence model
- `outputs/document_classification/` for document results
- `artifacts/document_classification/` for the selected document model
- `outputs/level_comparison.csv` for both test-result tables

The full `test_predictions.csv` in each output directory is generated locally
and excluded from Git because it is large. It contains sample ID, document ID,
sentence ID, source, prompt, text, true label, predicted label, model and score
for Person 3.

## Predict without retraining

Sentence model:

```bash
python -m classification.predict "Text to classify goes here."
```

Document model for a complete essay:

```bash
python -m classification.predict --unit document "Complete essay text goes here."
```

```python
from classification import predict_text

sentence_result = predict_text("Text to classify goes here.")
document_result = predict_text("Complete essay text goes here.", unit="document")
```

The sentence model splits input into sentences and aggregates their scores.
The document model represents the entire input as one sample. Both recreate
the same features and load the saved fitted pipeline without retraining.

## Tests

```bash
python -m pytest -q
```

The test fixtures verify loading, grouped splitting, all three models, metrics,
exports, model saving/reloading, and standalone sentence/document prediction.
Fixture metrics are not assignment results.
