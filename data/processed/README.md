# Local processed dataset

Place Person 2's combined CSV in this folder and rename it to:

`final_dataset.csv`

The expected local path is:

`data/processed/final_dataset.csv`

Then train and compare all three models from the repository root:

```bash
python -m classification.train
```

The CSV is intentionally ignored by Git because it exceeds GitHub's file-size
limit. This instruction file keeps the folder available after cloning or
pulling the repository.
.gitignore:25:
