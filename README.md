# COS30049 AI-Generated Content Detection

Assignment 2 machine-learning code for classifying human-written and
AI-generated text. The frontend is intentionally out of scope.

## Current status

Person 2 supplied sentence- and document-level representations of the combined
three-source dataset. The preprocessing and classification code is complete,
but the models must be retrained after the corrected feature formulas are used.
The model files and metric CSVs currently committed in the repository are from
an earlier dataset version and must not be quoted as final Assignment 2 results.

Both new training runs use reproducible, stratified 70/15/15
train/validation/test partitions. Sentence rows are grouped by `doc_id`, so
sentences from one essay cannot appear in different partitions. All three
models use the same held-out test set, and model selection uses validation F1
before the test set is evaluated.

## Setup

Conda (recommended for the submitted README requirement):

```bash
conda create --name cos30049-a2 python=3.12 -y
conda activate cos30049-a2
python -m pip install -r requirements.txt
```

Alternatively, use a Python virtual environment:

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
are not model inputs. TF-IDF unigrams/bigrams are combined with these 12
numeric features: `char_count`, `word_count`, `avg_word_len`,
`vocab_div_ratio`, `complex_word_ratio`, `stopword_ratio`,
`upper_letter_ratio`, `semicolon_dash_count`, `char_entropy`, `rep_bigram`,
`ai_tell_count`, and `doc_pos`. The loader verifies numeric data and recalculates
average word length and document position. TF-IDF and numeric scaling are
fitted only on training data inside each pipeline, preventing data leakage.

### Regenerate the processed datasets

Place these source files in `data/processed/`:

- `train_v2_drcat_02.csv`
- `HC3_en_train_data.csv`
- `data_for_preprocessing.csv`

Then run:

```bash
python data/processed/final_dataset.py
python data/processed/para_dataset.py
```

This creates `final_dataset.csv` (one sentence per row) and `para_dataset.csv`
(one complete source document per row). Do not combine these two outputs.

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
loss because the sentence dataset contains over one million sparse text rows.
Linear SVM probabilities are produced by valid three-fold sigmoid calibration;
they are not invented from its decision score. XGBoost uses 80 histogram-based
boosted trees without a large tuning search.

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

The sentence model splits input into sentences and aggregates their AI-class
probabilities. For multi-sentence input it also returns a reproducible 95%
bootstrap range across sentence probabilities. This range describes variation
between the submitted sentences; it is not a guarantee of real-world model
certainty. The document model represents the entire input as one sample. Both
recreate the same features and load the fitted pipeline without retraining.

## Clustering Models 
If needed, after generating 'final_dataset_csv', to refit/re-create either clustering models visiualizations or results please run: 

```bash
python clustering/clusteringKmeans.py
```

OR

```bash
python clustering/clusteringDBSCAN.py
```

To recreate tests for KMeans K value or DBSCAN's epsilon value, please uncomment the sections beneath labelled as such. (e.g | Elbow Method vs Silhouette Score to find K | or  | Nearest Neighbour K Distance Plot |). 

## Data analysis

After generating `final_dataset.csv`, recreate the summary statistics and four
visualisations with:

```bash
python visualisation/data_analysis/eda.py
```

Set `DATA_PATH` only when the sentence CSV is stored somewhere else.

## Tests

```bash
python -m pytest -q
```

The test fixtures verify loading, grouped splitting, all three models, metrics,
exports, model saving/reloading, and standalone sentence/document prediction.
Fixture metrics are not assignment results.
