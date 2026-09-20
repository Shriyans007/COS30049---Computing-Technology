# Classification dataset

Person 2's combined dataset is not committed because it exceeds GitHub's file
size limit. Keep it locally at:

data/processed/final_dataset.csv

Required columns:

- doc_id: globally unique original-document ID
- sent_id: sentence order within that document
- text: cleaned sentence text
- label: 0 for human or 1 for AI

The current file also supplies source, prompt and twelve engineered numeric
features. source and prompt are retained only for traceability.

The loader validates labels and document consistency, repairs average-word
length and sentence-position calculations, removes exact overlap, and performs
the train/validation/test split by doc_id.
