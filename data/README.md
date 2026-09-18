# Classification dataset

Place Person 2's final processed CSV at:

`data/processed/final_dataset.csv`

The training code expects:

- `text`: the cleaned document text used for classification
- `label`: `human` or `ai` (case-insensitive); numeric `0`/`1` is also accepted
- `id` (optional): a stable source identifier. If omitted, the CSV row index is used.

Extra columns are preserved in the source CSV but are not used by the current
raw-text TF-IDF classifiers. Empty text, unsupported labels, and datasets too
small for a stratified train/validation/test split are rejected with a clear
error.

The final group dataset is not currently present in the repository. Do not use
test fixtures as assignment data or report their metrics as model results.

