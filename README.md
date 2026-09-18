# COS30049 AI-Generated Content Detection

This repository currently contains the Assignment 2 classification framework
for distinguishing human-written text from AI-generated text. The frontend is
out of scope for this stage.

## Current status

The training, comparison, export, model persistence, and prediction code is in
place. Person 2's final processed dataset is not yet in the repository, so no
final assignment metrics or trained model are committed.

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

## Dataset contract

Place the final CSV at `data/processed/final_dataset.csv`, or pass another path
with `--dataset`. Required columns are:

| Column | Required | Accepted values |
| --- | --- | --- |
| `text` | Yes | Non-empty cleaned document text |
| `label` | Yes | `human`/`ai` or `0`/`1` |
| `id` | No | Unique source identifier |

Different column names can be supplied with `--text-column`, `--label-column`,
and `--id-column`. The present pipeline uses raw text with TF-IDF unigrams and
bigrams. TF-IDF is fitted only on training data inside each scikit-learn
pipeline, preventing test-data leakage. If Person 2 supplies engineered numeric
features instead of raw text, the group should agree on the column contract
before adapting this pipeline.

## Train and compare

```bash
python -m classification.train --dataset data/processed/final_dataset.csv
```

The workflow uses a fixed, stratified 70/15/15 train/validation/test split. It
compares Logistic Regression, Linear SVM, and XGBoost. Selection uses validation
F1 (then validation accuracy); all models are refitted on train + validation and
evaluated once on the same untouched test set.

Generated files:

- `outputs/classification/validation_metrics.csv`
- `outputs/classification/model_comparison.csv`
- `outputs/classification/test_predictions.csv`
- `artifacts/classification/final_text_classifier.joblib`
- `artifacts/classification/model_metadata.json`

Generated outputs and artifacts are ignored by Git because final files must be
created from the group's approved dataset. `test_predictions.csv` includes the
source ID, text, true label, prediction, model, and score for Person 3's error
analysis. Linear SVM produces a decision score, not a probability.

## Predict without retraining

After training:

```bash
python -m classification.predict "Text to classify goes here"
```

Python code for a future backend:

```python
from classification import predict_text

result = predict_text("Text to classify goes here")
```

The saved scikit-learn pipeline contains both the fitted TF-IDF vectorizer and
selected classifier, so prediction applies the same transformation used during
training.

## Tests

```bash
python -m pytest -q
```

The tests use a small, clearly marked fixture only to verify that loading,
splitting, all three classifiers, metrics, exports, saving/loading, and
standalone prediction execute correctly. Fixture metrics are not assignment
results.
