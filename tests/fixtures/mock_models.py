"""Mock model objects for testing."""
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock

import numpy as np


class MockCollaborativeFilteringModel:
    """Mock collaborative filtering model for testing."""
    
    def __init__(self):
        """Initialize mock CF model."""
        self.is_trained = True
        self.user_similarity = np.random.random((1000, 1000))
        self.item_similarity = np.random.random((10000, 10000))
        
    def recommend(self, user_id: int, k: int = 10, 
                  exclude_seen: bool = True) -> List[int]:
        """Generate mock recommendations."""
        np.random.seed(user_id)  # Consistent results for same user
        recommendations = np.random.randint(10000, 20000, k).tolist()
        return recommendations
    
    def get_user_similarity(self, user_id1: int, user_id2: int) -> float:
        """Get similarity between two users."""
        return np.random.random()
    
    def get_item_similarity(self, item_id1: int, item_id2: int) -> float:
        """Get similarity between two items."""
        return np.random.random()


class MockPopularityModel:
    """Mock popularity-based model for testing."""
    
    def __init__(self):
        """Initialize mock popularity model."""
        self.global_popularity = list(range(10000, 11000))  # Most popular items
        self.device_popularity = {
            0: list(range(11000, 12000)),  # Desktop
            1: list(range(12000, 13000)),  # Mobile
            2: list(range(13000, 14000))   # Tablet
        }
        self.country_popularity = {
            "US": list(range(14000, 15000)),
            "DE": list(range(15000, 16000)),
            "FR": list(range(16000, 17000))
        }
    
    def recommend(self, user_id: int, k: int = 10, 
                  context: Optional[Dict[str, Any]] = None) -> List[int]:
        """Generate context-aware popularity recommendations."""
        if context is None:
            return self.global_popularity[:k]
        
        # Blend different popularity lists based on context
        recommendations = []
        
        # Add device-specific items
        device = context.get("device", -1)
        if device in self.device_popularity:
            recommendations.extend(self.device_popularity[device][:k//2])
        
        # Add country-specific items
        country = context.get("country", "")
        if country in self.country_popularity:
            recommendations.extend(self.country_popularity[country][:k//2])
        
        # Fill with global popularity if needed
        while len(recommendations) < k:
            recommendations.extend(self.global_popularity)
        
        return recommendations[:k]
    
    def get_popularity_score(self, item_id: int, context: Dict[str, Any] = None) -> float:
        """Get popularity score for an item."""
        return np.random.random()


class MockALSModel:
    """Mock ALS matrix factorization model for testing."""
    
    def __init__(self, factors: int = 50):
        """Initialize mock ALS model."""
        self.factors = factors
        self.user_factors = np.random.random((1000, factors))
        self.item_factors = np.random.random((10000, factors))
        self.is_fitted = True
    
    def recommend(self, user_id: int, k: int = 10, 
                  filter_already_liked_items: bool = True) -> List[int]:
        """Generate ALS-based recommendations."""
        # Simulate matrix factorization prediction
        if user_id < len(self.user_factors):
            user_vector = self.user_factors[user_id]
            scores = np.dot(self.item_factors, user_vector)
            top_items = np.argsort(scores)[-k:][::-1]
            return (top_items + 10000).tolist()  # Offset to item ID range
        else:
            # Cold user - return random items
            np.random.seed(user_id)
            return np.random.randint(10000, 20000, k).tolist()
    
    def predict(self, user_id: int, item_id: int) -> float:
        """Predict rating for user-item pair."""
        if user_id < len(self.user_factors):
            user_vector = self.user_factors[user_id]
            item_vector = self.item_factors[item_id - 10000]  # Offset for item IDs
            return float(np.dot(user_vector, item_vector))
        return 0.0


class MockNeuralModel:
    """Mock neural network model for testing."""
    
    def __init__(self, embedding_dim: int = 128):
        """Initialize mock neural model."""
        self.embedding_dim = embedding_dim
        self.user_embeddings = np.random.random((1000, embedding_dim))
        self.item_embeddings = np.random.random((10000, embedding_dim))
        self.model_weights = np.random.random((embedding_dim * 2, 1))
        
    def recommend(self, user_id: int, k: int = 10) -> List[int]:
        """Generate neural network recommendations."""
        if user_id < len(self.user_embeddings):
            user_emb = self.user_embeddings[user_id]
            
            # Calculate scores for all items
            scores = []
            for item_emb in self.item_embeddings:
                combined = np.concatenate([user_emb, item_emb])
                score = np.dot(combined, self.model_weights.flatten())
                scores.append(score)
            
            # Get top-k items
            top_indices = np.argsort(scores)[-k:][::-1]
            return (top_indices + 10000).tolist()
        else:
            # Cold user
            np.random.seed(user_id)
            return np.random.randint(10000, 20000, k).tolist()
    
    def get_user_embedding(self, user_id: int) -> np.ndarray:
        """Get user embedding vector."""
        if user_id < len(self.user_embeddings):
            return self.user_embeddings[user_id]
        return np.zeros(self.embedding_dim)
    
    def get_item_embedding(self, item_id: int) -> np.ndarray:
        """Get item embedding vector."""
        adjusted_id = item_id - 10000
        if 0 <= adjusted_id < len(self.item_embeddings):
            return self.item_embeddings[adjusted_id]
        return np.zeros(self.embedding_dim)


class MockReranker:
    """Mock LightGBM reranker for testing."""
    
    def __init__(self):
        """Initialize mock reranker."""
        self.is_trained = True
        self.feature_names = [
            "cf_score", "als_score", "popularity_score", 
            "neural_score", "user_item_affinity", "temporal_score"
        ]
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate reranking scores."""
        # Mock sophisticated reranking
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        # Simulate feature-based scoring
        scores = np.random.random(features.shape[0])
        
        # Add some logic based on features
        if features.shape[1] >= 3:
            # Boost items with high popularity
            popularity_boost = features[:, 2] * 0.3
            scores += popularity_boost
        
        return scores
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        importance = np.random.random(len(self.feature_names))
        importance = importance / importance.sum()  # Normalize
        
        return dict(zip(self.feature_names, importance))


class MockEnsembleModel:
    """Mock ensemble model combining multiple algorithms."""
    
    def __init__(self):
        """Initialize mock ensemble."""
        self.cf_model = MockCollaborativeFilteringModel()
        self.popularity_model = MockPopularityModel()
        self.als_model = MockALSModel()
        self.neural_model = MockNeuralModel()
        self.reranker = MockReranker()
        
        self.weights = {
            "cf": 0.3,
            "popularity": 0.2,
            "als": 0.25,
            "neural": 0.25
        }
    
    def recommend(self, user_id: int, k: int = 10, 
                  context: Optional[Dict[str, Any]] = None) -> List[int]:
        """Generate ensemble recommendations."""
        # Get candidates from each model
        cf_recs = self.cf_model.recommend(user_id, k * 2)
        pop_recs = self.popularity_model.recommend(user_id, k * 2, context)
        als_recs = self.als_model.recommend(user_id, k * 2)
        neural_recs = self.neural_model.recommend(user_id, k * 2)
        
        # Combine and deduplicate
        all_candidates = list(set(cf_recs + pop_recs + als_recs + neural_recs))
        
        # Mock reranking with features
        features = np.random.random((len(all_candidates), 6))
        rerank_scores = self.reranker.predict(features)
        
        # Sort by reranking scores and return top-k
        ranked_items = [item for _, item in sorted(zip(rerank_scores, all_candidates), reverse=True)]
        return ranked_items[:k]
    
    def explain_recommendation(self, user_id: int, item_id: int) -> Dict[str, Any]:
        """Provide explanation for a recommendation."""
        return {
            "item_id": item_id,
            "cf_score": np.random.random(),
            "popularity_score": np.random.random(),
            "als_score": np.random.random(),
            "neural_score": np.random.random(),
            "final_score": np.random.random(),
            "reasons": [
                "Similar users also liked this item",
                "Popular in your region",
                "Matches your preferences"
            ]
        }


def create_mock_service():
    """Create a mock recommendation service for testing."""
    mock_service = Mock()
    
    # Mock methods
    mock_service.get_recommendations = Mock()
    mock_service.get_user_profile = Mock()
    mock_service.update_user_profile = Mock()
    mock_service.get_item_details = Mock()
    
    # Configure default returns
    mock_service.get_recommendations.return_value = {
        "recommendations": [10001, 10002, 10003, 10004, 10005],
        "user_profile": {
            "stored": {"device": 1, "os": 17, "country": "DE"},
            "used": {"device": 1, "os": 17, "country": "DE"},
            "overrides_applied": False
        }
    }
    
    mock_service.get_user_profile.return_value = {
        "device": 1, "os": 17, "country": "DE"
    }
    
    mock_service.get_item_details.return_value = {
        "item_id": 10001,
        "title": "Sample Article",
        "category": "technology",
        "popularity_score": 0.85
    }
    
    return mock_service


def create_mock_artifacts():
    """Create mock model artifacts for testing."""
    np.random.seed(42)  # Reproducible artifacts
    
    return {
        "cf_top300": np.random.randint(10000, 20000, size=(1000, 300)),
        "als_top100": np.random.randint(10000, 20000, size=(1000, 100)),
        "tt_top200": np.random.randint(10000, 20000, size=(1000, 200)),
        "pop_list": np.random.randint(10000, 20000, size=1000),
        "last_click": np.random.randint(10000, 20000, size=65536),
        "user_embeddings": np.random.random((1000, 128)),
        "item_embeddings": np.random.random((10000, 128)),
        "similarity_matrix": np.random.random((1000, 1000)),
        "reranker_weights": np.random.random(6)
    }