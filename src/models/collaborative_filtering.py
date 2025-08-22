"""Collaborative Filtering recommendation models."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np

from .base import BaseRecommender, CandidateGenerator

logger = logging.getLogger(__name__)


class ItemToItemCF(BaseRecommender, CandidateGenerator):
    """Item-to-Item Collaborative Filtering based on last clicked item."""
    
    def __init__(self):
        super().__init__("ItemToItemCF")
        self._similarity_matrix: Optional[np.ndarray] = None
        self._last_clicks: Optional[np.ndarray] = None
    
    def load(self, artifacts_path: Path) -> None:
        """Load CF similarity matrix and last click data."""
        try:
            cf_file = artifacts_path / "cf_i2i_top300.npy"
            last_click_file = artifacts_path / "last_click.npy"
            
            self._similarity_matrix = np.load(cf_file, mmap_mode="r")
            self._last_clicks = np.load(last_click_file, allow_pickle=True)
            
            self._loaded = True
            logger.info(f"Loaded CF model - similarity matrix shape: {self._similarity_matrix.shape}")
            
        except Exception as e:
            logger.error(f"Failed to load CF model: {e}")
            raise
    
    def get_candidates(self, user_id: int, k: int = 300) -> List[int]:
        """Get candidates based on item-to-item similarity from last click."""
        if not self._loaded:
            raise RuntimeError(f"{self.name} model not loaded")
        
        return self.generate_candidates(user_id, set(), k)
    
    def generate_candidates(self, user_id: int, seen_items: set[int], k: int) -> List[int]:
        """Generate CF candidates excluding seen items."""
        if not self._loaded:
            return []
        
        try:
            last_item = int(self._last_clicks[user_id])
            if last_item == -1:  # No interaction history
                return []
            
            # Get similar items to the last clicked item
            similar_items = self._similarity_matrix[last_item]
            
            # Filter out seen items and convert to list
            candidates = []
            for item_id in similar_items:
                item_id = int(item_id)
                if item_id not in seen_items:
                    candidates.append(item_id)
                if len(candidates) >= k:
                    break
            
            return candidates
            
        except (IndexError, ValueError) as e:
            logger.warning(f"CF candidate generation failed for user {user_id}: {e}")
            return []


class ALSRecommender(BaseRecommender, CandidateGenerator):
    """Alternating Least Squares matrix factorization recommender."""
    
    def __init__(self):
        super().__init__("ALS")
        self._user_recommendations: Optional[np.ndarray] = None
    
    def load(self, artifacts_path: Path) -> None:
        """Load precomputed ALS recommendations."""
        try:
            als_file = artifacts_path / "als_top100.npy"
            self._user_recommendations = np.load(als_file, mmap_mode="r")
            
            self._loaded = True
            logger.info(f"Loaded ALS model - recommendations shape: {self._user_recommendations.shape}")
            
        except Exception as e:
            logger.error(f"Failed to load ALS model: {e}")
            raise
    
    def get_candidates(self, user_id: int, k: int = 100) -> List[int]:
        """Get ALS-based candidates for user."""
        if not self._loaded:
            raise RuntimeError(f"{self.name} model not loaded")
        
        return self.generate_candidates(user_id, set(), k)
    
    def generate_candidates(self, user_id: int, seen_items: set[int], k: int) -> List[int]:
        """Generate ALS candidates excluding seen items."""
        if not self._loaded:
            return []
        
        try:
            # Get precomputed recommendations for user
            user_recs = self._user_recommendations[user_id]
            
            # Filter out seen items
            candidates = []
            for item_id in user_recs:
                item_id = int(item_id)
                if item_id not in seen_items:
                    candidates.append(item_id)
                if len(candidates) >= k:
                    break
            
            return candidates
            
        except (IndexError, ValueError) as e:
            logger.warning(f"ALS candidate generation failed for user {user_id}: {e}")
            return []


class TwoTowerRecommender(BaseRecommender, CandidateGenerator):
    """Two-Tower neural network recommender using precomputed embeddings."""
    
    def __init__(self):
        super().__init__("TwoTower") 
        self._user_recommendations: Optional[np.ndarray] = None
    
    def load(self, artifacts_path: Path) -> None:
        """Load precomputed Two-Tower recommendations."""
        try:
            tt_file = artifacts_path / "tt_top200.npy"
            self._user_recommendations = np.load(tt_file, mmap_mode="r")
            
            self._loaded = True
            logger.info(f"Loaded Two-Tower model - recommendations shape: {self._user_recommendations.shape}")
            
        except Exception as e:
            logger.error(f"Failed to load Two-Tower model: {e}")
            raise
    
    def get_candidates(self, user_id: int, k: int = 200) -> List[int]:
        """Get Two-Tower candidates for user."""
        if not self._loaded:
            raise RuntimeError(f"{self.name} model not loaded")
        
        return self.generate_candidates(user_id, set(), k)
    
    def generate_candidates(self, user_id: int, seen_items: set[int], k: int) -> List[int]:
        """Generate Two-Tower candidates excluding seen items."""
        if not self._loaded:
            return []
        
        try:
            # Get precomputed recommendations for user
            user_recs = self._user_recommendations[user_id]
            
            # Filter out seen items
            candidates = []
            for item_id in user_recs:
                item_id = int(item_id)
                if item_id not in seen_items:
                    candidates.append(item_id)
                if len(candidates) >= k:
                    break
            
            return candidates
            
        except (IndexError, ValueError) as e:
            logger.warning(f"Two-Tower candidate generation failed for user {user_id}: {e}")
            return []