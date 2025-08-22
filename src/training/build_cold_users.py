#!/usr/bin/env python
"""Generate list of cold users (no last click) and save to artifacts/cold_users.npy.

Usage::

    python src/training/build_cold_users.py
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

ART = Path(__file__).parent / "functions_reco" / "artifacts"

last_click = np.load(ART / "last_click.npy", allow_pickle=True)

cold = np.where(last_click == -1)[0].astype(np.int32)
print(f"Found {len(cold)} cold users (no history)")
np.save(ART / "cold_users.npy", cold)
print("Saved ->", ART / "cold_users.npy")
