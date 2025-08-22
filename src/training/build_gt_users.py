#!/usr/bin/env python
"""Build gt_users.npy containing user IDs that have a valid ground-truth click.

Run this once after the artefacts are generated. The file is saved under
`azure_recommender/functions_reco/artifacts/gt_users.npy` and can be loaded by
both the backend and the Streamlit front-end so that quick-pick bubbles only
contain users with a label.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ART = Path(__file__).parent / "functions_reco" / "artifacts"

if not ART.exists():
    raise SystemExit(f"Artifacts directory not found: {ART}")

valid_file = ART / "valid_clicks.parquet"
item_vec_file = ART / "final_twotower_item_vec.npy"

df = pd.read_parquet(valid_file, columns=["user_id", "click_article_id"])
NUM_ITEMS = np.load(item_vec_file, mmap_mode="r").shape[0]

# keep rows whose article ID exists in training
mask = (df["click_article_id"] >= 0) & (df["click_article_id"] < NUM_ITEMS) & (df["user_id"] > 0)
uid_arr = df.loc[mask, "user_id"].astype(np.int32).unique()

out_path = ART / "gt_users.npy"
np.save(out_path, uid_arr)
print(f"Saved {len(uid_arr)} user IDs -> {out_path}")
