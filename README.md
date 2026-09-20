# COS30049 AI-Generated Content Detection

Assignment 2 machine-learning code for classifying human-written and
AI-generated text. The frontend is intentionally out of scope.

## Current result

The final Person 2 dataset contains 1,580,111 sentence rows from 123,474 source
documents. Before splitting, the training loader removes repeated documents,
exact duplicate sentences, and sentence texts that appear with both labels.
This leaves 1,262,979 rows from 120,069 documents.

All sentences from one document stay in the same 70/15/15
train/validation/test partition. This prevents sentences from one essay
appearing in both training and testing.

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.8391 | 0.8332 | 0.6682 | 0.7417 |
| Linear SVM | **0.8901** | **0.8175** | **0.8780** | **0.8467** |
| XGBoost | 0.7759 | 0.7882 | 0.4809 | 0.5973 |

Linear SVM was selected because it produced the highest validation F1 and also
performed best on the untouched test set. Its returned score is a signed
decision score, not a probability.

## Setup

~~~bash
python -m venv .venv
~~~

Windows PowerShell:

~~~powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

macOS/Linux:

~~~bash
source .venv/bin/activate
python -m pip install -r requirements.txt
~~~

## Dataset

The CSV is not committed because it is over GitHub's file-size limit. The
training command accepts either:

- A CSV such as data/processed/final_dataset.csv
- Person 2's ZIP containing clean_dataset.csv

Required columns:

| Column | Purpose |
| --- | --- |
| doc_id | Original document identifier used for grouped splitting |
| sent_id | Sentence order inside the document |
| text | Sentence text |
| label | 0 for human and 1 for AI |

The supplied source and prompt columns are retained for tracing results but are
not model inputs. TF-IDF unigrams/bigrams are combined with the supplied
numeric writing-style features. TF-IDF and numeric scaling are fitted only on
training data inside each saved pipeline.

## Train and compare

From a CSV:

~~~bash
python -m classification.train --dataset data/processed/final_dataset.csv
~~~

Directly from Person 2's ZIP:

~~~bash
python -m classification.train --dataset "CSV files.zip" --zip-member "CSV files/clean_dataset.csv"
~~~

The three models use the same rows, split and feature representation. Logistic
Regression uses stochastic gradient descent with logistic loss because the
dataset has more than one million sparse text rows. XGBoost uses 80
histogram-based boosted trees without a large tuning search.

Generated files:

- outputs/classification/validation_metrics.csv
- outputs/classification/model_comparison.csv
- outputs/classification/test_predictions.csv
- artifacts/classification/final_text_classifier.joblib
- artifacts/classification/model_metadata.json

The model, metadata and summary metrics are committed. The full prediction CSV
is generated locally and excluded from Git because it is approximately 130 MB.
It contains sample ID, document ID, sentence ID, source, prompt, text, true
label, predicted label, model and score for Person 3.

## Predict without retraining

~~~bash
python -m classification.predict "Text to classify goes here."
~~~

~~~python
from classification import predict_text

result = predict_text("Text to classify goes here.")
~~~

The function splits a document into sentences, recreates the same numeric
features, applies the saved TF-IDF transformation, returns sentence results and
aggregates them into one document label.

## Tests

~~~bash
python -m pytest -q
~~~

The test fixture verifies loading, document-grouped splitting, all three models,
metrics, exports, saving/loading and standalone prediction. Fixture metrics are
not assignment results.
