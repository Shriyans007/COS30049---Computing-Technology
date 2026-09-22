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
