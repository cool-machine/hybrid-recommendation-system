# Datasets Directory

This directory is designed to hold large production datasets.

## Purpose

- Production datasets (too large for git)
- Processed model training data
- External dataset downloads
- Cached preprocessing results

## Gitignore

All files in this directory are automatically ignored by git due to:
```
datasets/
*.parquet
*.csv
*.npy
```

## Expected Files

When running the full system, expect these files:
- `valid_clicks.parquet` - User interaction data
- `articles_metadata.csv` - Article information
- `train_interactions.parquet` - Training data
- `test_interactions.parquet` - Test data

## Usage

```python
import pandas as pd

# Load production data
clicks = pd.read_parquet('datasets/valid_clicks.parquet')
articles = pd.read_csv('datasets/articles_metadata.csv')
```

## Data Sources

Production data should be downloaded from:
1. Data pipeline outputs
2. Azure Blob Storage
3. External APIs
4. Model training results