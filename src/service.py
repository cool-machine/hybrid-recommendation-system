"""Main recommendation service orchestrating all models."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .config import Config, get_config
from .models.base import ModelRegistry
from .models.collaborative_filtering import ALSRecommender, ItemToItemCF, TwoTowerRecommender
from .models.popularity import ContextualPopularity, PopularityRecommender
from .models.reranking import LightGBMReranker

logger = logging.getLogger(__name__)


class RecommendationService:
    """Main service for generating recommendations."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.registry = ModelRegistry()
        self._last_clicks: Optional[np.ndarray] = None
        self._ground_truth: Dict[int, int] = {}
        
        logger.info("Initialized RecommendationService")
    
    def load_models(self) -> None:
        """Load all models and register them."""
        artifacts_path = self.config.model.artifacts_dir
        logger.info(f"Loading models from {artifacts_path}")
        
        try:
            # Load and register candidate generators
            cf_model = ItemToItemCF()
            cf_model.load(artifacts_path)
            self.registry.register_model(cf_model)
            self.registry.register_candidate_generator(cf_model)
            
            als_model = ALSRecommender()
            als_model.load(artifacts_path)
            self.registry.register_model(als_model)
            self.registry.register_candidate_generator(als_model)
            
            tt_model = TwoTowerRecommender()
            tt_model.load(artifacts_path)
            self.registry.register_model(tt_model)
            self.registry.register_candidate_generator(tt_model)
            
            pop_model = PopularityRecommender()
            pop_model.load(artifacts_path)
            self.registry.register_model(pop_model)
            self.registry.register_candidate_generator(pop_model)
            
            # Load and register reranker
            reranker = LightGBMReranker()
            reranker.load(artifacts_path)
            self.registry.register_reranker(reranker)
            
            # Load and register cold-start handler
            cold_start = ContextualPopularity()
            cold_start.load(artifacts_path)
            self.registry.register_cold_start_handler(cold_start)
            
            # Load additional data
            self._load_auxiliary_data(artifacts_path)
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
    
    def _load_auxiliary_data(self, artifacts_path: Path) -> None:
        """Load auxiliary data like last clicks and ground truth."""
        try:
            # Load last clicks for warm/cold user detection
            self._last_clicks = np.load(artifacts_path / "last_click.npy", allow_pickle=True)
            logger.info(f"Loaded last clicks data for {len(self._last_clicks)} users")
            
            # Load ground truth for evaluation (optional)
            try:
                import pandas as pd
                gt_df = pd.read_parquet(artifacts_path / "valid_clicks.parquet", 
                                       columns=["user_id", "click_article_id"])
                self._ground_truth = dict(zip(gt_df.user_id.astype(int), 
                                            gt_df.click_article_id.astype(int)))
                logger.info(f"Loaded ground truth for {len(self._ground_truth)} users")
            except Exception as e:
                logger.warning(f"Ground truth not available: {e}")
                
        except Exception as e:
            logger.error(f"Failed to load auxiliary data: {e}")
            raise
    
    def get_recommendations(self, user_id: int, k: int = 10, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get recommendations for a user."""
        if not self.registry.is_ready():
            raise RuntimeError("Recommendation service not ready - models not loaded")
        
        # Validate inputs
        k = max(1, min(k, self.config.api.max_recommendations))
        context = context or {}
        
        # Check if user is cold (no interaction history)
        is_cold_user = self._is_cold_user(user_id)
        
        if is_cold_user:
            return self._get_cold_start_recommendations(user_id, k, context)
        else:
            return self._get_warm_user_recommendations(user_id, k)
    
    def _is_cold_user(self, user_id: int) -> bool:
        """Check if user has no interaction history."""
        if self._last_clicks is None:
            return True
        
        try:
            return int(self._last_clicks[user_id]) == -1
        except (IndexError, ValueError):
            return True
    
    def _get_cold_start_recommendations(self, user_id: int, k: int, 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for cold-start users."""
        cold_start_handler = self.registry.get_cold_start_handler()
        if not cold_start_handler:
            raise RuntimeError("Cold-start handler not available")
        
        try:
            recommendations = cold_start_handler.get_recommendations(context, k)
            
            return {
                "recommendations": recommendations,
                "user_type": "cold",
                "algorithm": "contextual_popularity",
                "ground_truth": self._ground_truth.get(user_id)
            }
            
        except Exception as e:
            logger.error(f"Cold-start recommendation failed for user {user_id}: {e}")
            # Fallback to global popularity
            pop_model = self.registry.get_model("Popularity")
            if pop_model:
                fallback_recs = pop_model.get_candidates(user_id, k)
                return {
                    "recommendations": fallback_recs[:k],
                    "user_type": "cold",
                    "algorithm": "global_popularity_fallback",
                    "ground_truth": self._ground_truth.get(user_id)
                }
            else:
                return {
                    "recommendations": [],
                    "user_type": "cold", 
                    "algorithm": "none",
                    "error": "No fallback available",
                    "ground_truth": self._ground_truth.get(user_id)
                }
    
    def _get_warm_user_recommendations(self, user_id: int, k: int) -> Dict[str, Any]:
        """Get recommendations for users with interaction history."""
        try:
            # Generate candidates from all algorithms
            candidates = self._generate_candidate_pool(user_id)
            
            if not candidates:
                logger.warning(f"No candidates generated for user {user_id}")
                return {
                    "recommendations": [],
                    "user_type": "warm",
                    "algorithm": "ensemble",
                    "error": "No candidates generated",
                    "ground_truth": self._ground_truth.get(user_id)
                }
            
            # Rerank candidates using LightGBM
            reranker = self.registry.get_reranker()
            if reranker:
                final_recs = reranker.rerank(user_id, candidates)
            else:
                final_recs = candidates
            
            return {
                "recommendations": final_recs[:k],
                "user_type": "warm",
                "algorithm": "ensemble_with_reranking",
                "candidate_count": len(candidates),
                "ground_truth": self._ground_truth.get(user_id)
            }
            
        except Exception as e:
            logger.error(f"Warm user recommendation failed for user {user_id}: {e}")
            return {
                "recommendations": [],
                "user_type": "warm",
                "algorithm": "ensemble",
                "error": str(e),
                "ground_truth": self._ground_truth.get(user_id)
            }
    
    def _generate_candidate_pool(self, user_id: int) -> List[int]:
        """Generate unified candidate pool from all algorithms."""
        candidates = []
        seen = set()
        
        generators = self.registry.get_candidate_generators()
        config = self.config.model
        
        # Algorithm priorities and limits (matches original implementation)
        algorithm_limits = {
            "ItemToItemCF": config.max_candidates_cf,     # 300
            "ALS": config.max_candidates_als,             # 100  
            "Popularity": config.max_candidates_pop,      # 600
            "TwoTower": config.max_candidates_tt,         # 200
        }
        
        # Cumulative limits for pool building
        pool_limits = {
            "ItemToItemCF": 300,
            "ALS": 400,        # 300 + 100
            "Popularity": 600,  # 400 + 200 
            "TwoTower": 800,   # 600 + 200
        }
        
        for generator in generators:
            algo_name = type(generator).__name__
            if algo_name == "ItemToItemCF":
                algo_name = "ItemToItemCF"
            elif algo_name == "ALSRecommender":
                algo_name = "ALS"
            elif algo_name == "PopularityRecommender":
                algo_name = "Popularity"
            elif algo_name == "TwoTowerRecommender":  
                algo_name = "TwoTower"
            
            if algo_name not in algorithm_limits:
                continue
            
            try:
                # Get candidates from this algorithm
                algo_candidates = generator.generate_candidates(user_id, seen, algorithm_limits[algo_name])
                
                # Add to pool up to the cumulative limit
                for item_id in algo_candidates:
                    if item_id not in seen:
                        seen.add(item_id)
                        candidates.append(item_id)
                    
                    if len(candidates) >= pool_limits[algo_name]:
                        break
                
                if len(candidates) >= config.final_candidate_pool:
                    break
                    
            except Exception as e:
                logger.warning(f"Failed to get candidates from {algo_name}: {e}")
                continue
        
        logger.debug(f"Generated {len(candidates)} candidates for user {user_id}")
        return candidates
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and model readiness."""
        return {
            "service_ready": self.registry.is_ready(),
            "models": self.registry.get_status(),
            "config": {
                "max_candidates": self.config.model.final_candidate_pool,
                "max_recommendations": self.config.api.max_recommendations,
                "environment": self.config.env.environment
            },
            "auxiliary_data": {
                "last_clicks_loaded": self._last_clicks is not None,
                "ground_truth_count": len(self._ground_truth)
            }
        }
    
    def is_ready(self) -> bool:
        """Check if service is ready to serve requests."""
        return self.registry.is_ready() and self._last_clicks is not None