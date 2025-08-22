"""Reranking models for final candidate scoring."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
import lightgbm as lgb

from .base import Reranker

logger = logging.getLogger(__name__)


class LightGBMReranker(Reranker):
    """LightGBM-based reranker with engineered features."""
    
    def __init__(self):
        self._loaded = False
        self._model: Optional[lgb.Booster] = None
        self._user_embeddings: Optional[np.ndarray] = None
        self._item_embeddings: Optional[np.ndarray] = None
    
    def load(self, artifacts_path: Path) -> None:
        """Load LightGBM model and embedding vectors."""
        try:
            # Load the LightGBM model
            model_file = artifacts_path / "reranker.txt"
            self._model = lgb.Booster(model_file=str(model_file))
            
            # Load user and item embeddings for similarity features
            self._user_embeddings = np.load(artifacts_path / "final_twotower_user_vec.npy", mmap_mode="r")
            self._item_embeddings = np.load(artifacts_path / "final_twotower_item_vec.npy", mmap_mode="r")
            
            self._loaded = True
            logger.info(f"Loaded LightGBM reranker - user embeddings: {self._user_embeddings.shape}, "
                       f"item embeddings: {self._item_embeddings.shape}")
            
        except Exception as e:
            logger.error(f"Failed to load LightGBM reranker: {e}")
            raise
    
    def rerank(self, user_id: int, candidates: List[int]) -> List[int]:
        """Rerank candidates using LightGBM scoring."""
        if not self._loaded:
            raise RuntimeError("LightGBM reranker not loaded")
        
        if not candidates:
            return candidates
        
        try:
            # Build feature matrix for all candidates
            features = self._build_features(user_id, candidates)
            
            # Get scores from LightGBM
            scores = self._model.predict(features)
            
            # Sort candidates by score (descending)
            sorted_indices = np.argsort(-scores)
            reranked = [candidates[i] for i in sorted_indices]
            
            return reranked
            
        except Exception as e:
            logger.error(f"Reranking failed for user {user_id}: {e}")
            # Return original order if reranking fails
            return candidates
    
    def _build_features(self, user_id: int, candidates: List[int]) -> np.ndarray:
        """Build feature matrix for LightGBM.
        
        Features (6 total):
        0. CF rank (1-300, or 1001 if not from CF)
        1. ALS rank (1-100, or 1001 if not from ALS) 
        2. Popularity rank (1-200, or 1001 if not from popularity)
        3. Two-Tower rank (1-200, or 1001 if not from Two-Tower)
        4. Global candidate rank (1-based position in final candidate list)
        5. User-item cosine similarity from embeddings
        """
        n_candidates = len(candidates)
        features = np.zeros((n_candidates, 6), dtype=np.float32)
        
        user_embedding = self._user_embeddings[user_id]
        
        for i, item_id in enumerate(candidates):
            # For now, we only compute global rank and similarity
            # The algorithm-specific ranks would need to be passed from the ensemble
            features[i, 4] = i + 1  # Global candidate rank
            
            # Cosine similarity between user and item embeddings
            item_embedding = self._item_embeddings[item_id]
            similarity = self._cosine_similarity(user_embedding, item_embedding)
            features[i, 5] = similarity
            
            # Set default values for algorithm ranks (would be set by ensemble)
            features[i, 0] = 1001  # CF rank default
            features[i, 1] = 1001  # ALS rank default  
            features[i, 2] = 1001  # Popularity rank default
            features[i, 3] = 1001  # Two-Tower rank default
        
        return features
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2 + 1e-9))
    
    def build_features_with_ranks(self, user_id: int, candidates: List[int], 
                                 algorithm_ranks: dict[str, dict[int, int]]) -> np.ndarray:
        """Build features with algorithm-specific ranks provided by ensemble."""
        n_candidates = len(candidates)
        features = np.zeros((n_candidates, 6), dtype=np.float32)
        
        user_embedding = self._user_embeddings[user_id]
        
        for i, item_id in enumerate(candidates):
            # Algorithm-specific ranks (1-based, 1001 if not present)
            features[i, 0] = algorithm_ranks.get("cf", {}).get(item_id, 1001)
            features[i, 1] = algorithm_ranks.get("als", {}).get(item_id, 1001)  
            features[i, 2] = algorithm_ranks.get("popularity", {}).get(item_id, 1001)
            features[i, 3] = algorithm_ranks.get("twotower", {}).get(item_id, 1001)
            
            # Global candidate rank
            features[i, 4] = i + 1
            
            # User-item cosine similarity
            item_embedding = self._item_embeddings[item_id]
            similarity = self._cosine_similarity(user_embedding, item_embedding)
            features[i, 5] = similarity
        
        return features
    
    def is_loaded(self) -> bool:
        """Check if reranker is loaded and ready."""
        return self._loaded