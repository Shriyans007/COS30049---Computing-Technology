# Data Analysis


- `eda.py` — produces summary statistics and four visualisations from the
  sentence-level dataset.

## Input

Reads `final_dataset.csv`  from the
`data/processed/` folder.

## Outputs

Running `eda.py` writes into `visualisation/`:

- `summary_stats.csv` — mean/median/std per feature, split by label
- `bar_chart.png` — class balance (human vs AI)
- `feature_histograms.png` — per-feature distributions, by class
- `correlation_heatmap.png` — 12×12 feature correlation matrix
- `feature_boxplots.png` — class separability per feature


## What it analyses

- **Class balance** — how many human vs AI sentences (Bar Chart)
- **Feature distributions** — which features separate the classes visually (Histograms)
- **Correlation structure** — redundant vs independent features (informs
  feature selection and model choice) (Correlation Heatmap)
- **Class separability** — box plots showing where human and AI distributions
  differ

