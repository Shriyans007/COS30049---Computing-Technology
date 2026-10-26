# COS30049 AI-Generated Content Detection

Assignment 2 machine-learning code for classifying human-written and
AI-generated text. The frontend is intentionally out of scope.

## Assignment 3 secure backend

The `backend/` folder adds the Person 1 Assignment 3 contribution: a FastAPI
service around the two Assignment 2 classifiers, bounded inference capacity,
safe validation/errors, and reproducible denial-of-service and detection-evasion
experiments. The React interface is developed separately against the contract
below.

### Request path

```text
React -> POST /api/v1/predict -> validation -> security normalisation
      -> bounded inference gate -> document + sentence pipelines -> JSON result
```

The document classifier supplies the overall Human/AI result. The sentence
classifier supplies each sentence's probability. Both were fitted during
Assignment 2 and are loaded once during FastAPI startup; the API never retrains
them.

### Windows PowerShell setup

Python 3.12 is recommended. From the repository root:

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example .env
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the generated API documentation. The
production/demo command intentionally omits `--reload`.

### Frontend API contract

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/predict` | Validate and classify one text |
| `GET` | `/api/v1/health` | Lightweight availability check |
| `GET` | `/api/v1/model-info` | Model names, class mapping and limits |

Request:

```json
{"text": "Paste at least 20 characters of plain text here."}
```

Successful response:

```json
{
  "prediction": "ai",
  "ai_probability": 0.91,
  "confidence": 0.91,
  "confidence_range": {
    "lower": 0.84,
    "upper": 0.96,
    "method": "95% bootstrap interval across sentence AI probabilities"
  },
  "sentence_results": [
    {"text": "Example sentence.", "label": "ai", "ai_probability": 0.93}
  ],
  "normalisation_applied": false
}
```

`ai_probability` always means probability of class 1 (AI). `confidence` means
the probability assigned to the returned class. The confidence range is only
returned for multi-sentence input and measures variation across sentence
probabilities; it is not a guarantee of real-world accuracy.

All errors use the same safe structure:

```json
{"error": {"code": "TEXT_TOO_LARGE", "message": "Text must not exceed the configured limits."}}
```

The default limits are 20–10,000 characters, 40,000 UTF-8 bytes and 100
sentences. Relevant failures use `400`, `413`, `415`, `422`, `429`, `503` or
`500`; internal paths and stack traces are logged server-side only.

### Security design

The API applies NFKC, removes zero-width/unsafe format characters, normalises
whitespace and maps a deliberately small set of Latin-looking Cyrillic/Greek
characters before inference. Original text remains in the JSON sentence display
and React must render it as text, never HTML.

Model calls run in worker threads, outside the asynchronous event loop. A
semaphore permits two simultaneous inferences and a bounded wait rejects excess
work with `503`, leaving the health route responsive. Timeouts bound how long a
caller waits, although Python cannot forcibly stop a worker thread already
running. Character, byte and sentence limits prevent small requests expanding
into disproportionate work. A separate high per-client request limit returns
`429`; this supports general hygiene but is not the marked DoS mechanism.

CORS accepts only the exact origins in `A3_ALLOWED_ORIGINS`; wildcard origins
are rejected at startup. The backend performs no user-controlled outbound
requests, database queries, file uploads or shell commands, so SSRF, SQL
injection, unsafe upload and command injection are not exposed by this design.

### Tests and experiments

```powershell
python -m pytest -q
python -m backend.experiments.detection_evasion
python -m backend.experiments.dos_experiment --requests 20
```

The detection-evasion script tests four variants against a fixed set, then
repeats the same measurements after normalisation. The DoS script sends real
concurrent HTTP requests to controlled baseline and protected localhost servers.
Raw CSV rows and JSON summaries are saved under
`backend/experiments/results/`. Results depend on the committed model and local
hardware and must be regenerated rather than quoted without running them.

The committed run produced 48 variants from 12 eligible AI examples. Evasion
was 47.92% before normalisation and 0% afterwards on this fixed set; none of
eight clean controls changed class. In the 20-request localhost overload run,
the baseline accepted all 20 requests, while protected mode completed two and
rejected 18 with `503`. The health endpoint returned `200` during both runs.

The fixed evasion corpus is intentionally small and is not evidence of model
accuracy. The confusable mapping is incomplete; making it aggressive would
damage legitimate multilingual writing. The DoS experiment uses an explicit
local-only delay for reproducible cost and does not claim to simulate a network
level distributed attack.

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
