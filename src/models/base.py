"""Base classes for recommendation models."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

import numpy as np

logger = logging.getLogger(__name__)


class RecommendationModel(Protocol):
    """Protocol defining the interface for recommendation models."""
    
    def get_candidates(self, user_id: int, k: int = 100) -> List[int]:
        """Get candidate items for a user."""
        ...
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready."""
        ...


class BaseRecommender(ABC):
    """Base class for recommendation algorithms."""
    
    def __init__(self, name: str):
        self.name = name
        self._loaded = False
        logger.info(f"Initialized {self.name} recommender")
    
    @abstractmethod
    def load(self, artifacts_path: Any) -> None:
        """Load model artifacts."""
        pass
    
    @abstractmethod 
    def get_candidates(self, user_id: int, k: int = 100) -> List[int]:
        """Get candidate recommendations for user."""
        pass
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded
    
    def __str__(self) -> str:
        status = "loaded" if self._loaded else "not loaded"
        return f"{self.name} ({status})"


class CandidateGenerator(ABC):
    """Abstract base for candidate generation algorithms."""
    
    @abstractmethod
    def generate_candidates(self, user_id: int, seen_items: set[int], k: int) -> List[int]:
        """Generate candidate items for a user, excluding seen items."""
        pass


class Reranker(ABC):
    """Abstract base for reranking algorithms."""
    
    @abstractmethod
    def rerank(self, user_id: int, candidates: List[int]) -> List[int]:
        """Rerank candidates and return sorted by predicted relevance."""
        pass


class ColdStartHandler(ABC):
    """Abstract base for cold-start recommendation strategies."""
    
    @abstractmethod
    def get_recommendations(self, context: Dict[str, Any], k: int) -> List[int]:
        """Get recommendations for cold-start users based on context."""
        pass


class ModelRegistry:
    """Registry for managing multiple recommendation models."""
    
    def __init__(self):
        self._models: Dict[str, BaseRecommender] = {}
        self._candidate_generators: List[CandidateGenerator] = []
        self._reranker: Optional[Reranker] = None
        self._cold_start_handler: Optional[ColdStartHandler] = None
    
    def register_model(self, model: BaseRecommender) -> None:
        """Register a recommendation model."""
        self._models[model.name] = model
        logger.info(f"Registered model: {model.name}")
    
    def register_candidate_generator(self, generator: CandidateGenerator) -> None:
        """Register a candidate generation algorithm."""
        self._candidate_generators.append(generator)
        logger.info(f"Registered candidate generator: {type(generator).__name__}")
    
    def register_reranker(self, reranker: Reranker) -> None:
        """Register a reranking algorithm."""
        self._reranker = reranker
        logger.info(f"Registered reranker: {type(reranker).__name__}")
    
    def register_cold_start_handler(self, handler: ColdStartHandler) -> None:
        """Register cold-start handler."""
        self._cold_start_handler = handler
        logger.info(f"Registered cold-start handler: {type(handler).__name__}")
    
    def get_model(self, name: str) -> Optional[BaseRecommender]:
        """Get a registered model by name."""
        return self._models.get(name)
    
    def list_models(self) -> List[str]:
        """List all registered model names."""
        return list(self._models.keys())
    
    def get_candidate_generators(self) -> List[CandidateGenerator]:
        """Get all registered candidate generators."""
        return self._candidate_generators.copy()
    
    def get_reranker(self) -> Optional[Reranker]:
        """Get the registered reranker."""
        return self._reranker
    
    def get_cold_start_handler(self) -> Optional[ColdStartHandler]:
        """Get the registered cold-start handler."""
        return self._cold_start_handler
    
    def is_ready(self) -> bool:
        """Check if all registered models are loaded and ready."""
        models_ready = all(model.is_loaded() for model in self._models.values())
        has_generators = len(self._candidate_generators) > 0
        has_reranker = self._reranker is not None
        has_cold_start = self._cold_start_handler is not None
        
        return models_ready and has_generators and has_reranker and has_cold_start
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all registered components."""
        return {
            "models": {name: model.is_loaded() for name, model in self._models.items()},
            "candidate_generators": len(self._candidate_generators),
            "reranker_ready": self._reranker is not None,
            "cold_start_ready": self._cold_start_handler is not None,
            "overall_ready": self.is_ready()
        }