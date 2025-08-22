#!/usr/bin/env python
"""Build segment-based popularity lists for cold-start recommendations.

The script reads click log parquet that contains columns:
    click_deviceGroup  (0 mobile,1 desktop,2 tablet)
    click_os           (0 Android,1 iOS,2 Windows,3 macOS,4 Linux,5 other)
    click_country      (ISO-2 string or numeric)
    click_article_id

It outputs a pickle file under functions_reco/artifacts/top_lists.pkl
with keys:
    global_top: np.ndarray
    by_os: Dict[int, np.ndarray]
    by_dev: Dict[int, np.ndarray]
    by_os_reg: Dict[Tuple[int,str], np.ndarray]
    by_dev_reg: Dict[Tuple[int,str], np.ndarray]

Run once after refreshing logs:
    python azure_recommender/build_popularity_lists.py [click_log.parquet]
"""
from __future__ import annotations
import sys, pickle
from pathlib import Path
import pandas as pd
import numpy as np

ART = Path(__file__).parent / "functions_reco" / "artifacts"
CLICK_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ART / "click_log.parquet"

TOP_K = 50
print("Reading click log from", CLICK_PATH)
cols = ["click_deviceGroup", "click_os", "click_country", "click_article_id"]
df = pd.read_parquet(CLICK_PATH, columns=cols)

# helper
def topk(series, k=TOP_K):
    return series.value_counts().head(k).index.to_numpy(dtype=np.int32)

print("Computing global top ...")
res = dict()
res["global_top"] = topk(df["click_article_id"])

print("Computing by_os ...")
res["by_os"] = df.groupby("click_os")["click_article_id"].apply(topk).to_dict()
print("Computing by_dev ...")
res["by_dev"] = df.groupby("click_deviceGroup")["click_article_id"].apply(topk).to_dict()

print("Computing by_os_reg ...")
res["by_os_reg"] = (
    df.groupby(["click_os", "click_country"])["click_article_id"].apply(topk).to_dict()
)
print("Computing by_dev_reg ...")
res["by_dev_reg"] = (
    df.groupby(["click_deviceGroup", "click_country"])["click_article_id"].apply(topk).to_dict()
)

out_path = ART / "top_lists.pkl"
print("Saving ->", out_path)
out_path.write_bytes(pickle.dumps(res))
print("Done. Keys:", list(res))
