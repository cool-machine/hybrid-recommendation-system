"""Test configuration settings."""
from pathlib import Path
from typing import Dict, Any, List


class TestConfig:
    """Test configuration class."""
    
    # Test data settings
    TEST_USER_ID = 1001
    COLD_USER_ID = 9999
    INVALID_USER_ID = -1
    
    # Test recommendation parameters
    DEFAULT_K = 5
    TEST_K_VALUES = [1, 5, 10, 20, 50]
    MAX_K = 100
    
    # Test contexts for context-aware recommendations
    TEST_CONTEXTS = [
        {"device": 0, "os": 1, "country": "US"},    # Desktop, Windows, US
        {"device": 1, "os": 17, "country": "DE"},   # Mobile, iOS, Germany
        {"device": 2, "os": 2, "country": "FR"},    # Tablet, macOS, France
        {"device": 1, "os": 11, "country": "GB"},   # Mobile, Android, UK
        {"device": 0, "os": 3, "country": "IT"},    # Desktop, Linux, Italy
    ]
    
    # Device mappings
    DEVICE_MAPPING = {
        0: "desktop",
        1: "mobile", 
        2: "tablet"
    }
    
    # OS mappings (simplified)
    OS_MAPPING = {
        1: "windows",
        2: "macos",
        3: "linux",
        11: "android",
        17: "ios"
    }
    
    # Country codes
    VALID_COUNTRIES = ["US", "DE", "FR", "GB", "IT", "ES", "NL", "BR", "JP", "IN"]
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        "max_response_time_seconds": 2.0,
        "max_memory_usage_mb": 500,
        "min_precision_at_5": 0.1,
        "min_recall_at_10": 0.05,
        "max_cold_start_time": 5.0
    }
    
    # API endpoints
    API_ENDPOINTS = {
        "local_azure_functions": "http://localhost:7071/api",
        "production_azure": "https://ocp9funcapp-recsys.azurewebsites.net/api",
        "streamlit_app": "https://recommender-system-demo.streamlit.app"
    }
    
    # File paths
    @classmethod
    def get_test_data_dir(cls) -> Path:
        """Get test data directory path."""
        return Path(__file__).parent / "data"
    
    @classmethod
    def get_sample_data_dir(cls) -> Path:
        """Get sample data directory path."""
        return Path(__file__).parent.parent.parent / "data" / "sample"
    
    @classmethod
    def get_artifacts_dir(cls) -> Path:
        """Get artifacts directory path."""
        return Path(__file__).parent.parent.parent / "artifacts"
    
    # Model configuration
    MODEL_CONFIG = {
        "collaborative_filtering": {
            "similarity_threshold": 0.1,
            "min_common_items": 5,
            "max_neighbors": 50
        },
        "als": {
            "factors": 50,
            "regularization": 0.01,
            "iterations": 15,
            "alpha": 1.0
        },
        "neural_network": {
            "embedding_dim": 128,
            "hidden_layers": [256, 128, 64],
            "dropout_rate": 0.2,
            "learning_rate": 0.001
        },
        "popularity": {
            "time_decay_factor": 0.9,
            "min_interactions": 10,
            "regional_weight": 0.3
        },
        "reranker": {
            "num_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1
        }
    }
    
    # Test dataset sizes
    TEST_DATASET_SIZES = {
        "small": {
            "users": 100,
            "items": 500,
            "interactions": 1000
        },
        "medium": {
            "users": 1000,
            "items": 5000,
            "interactions": 10000
        },
        "large": {
            "users": 10000,
            "items": 50000,
            "interactions": 100000
        }
    }
    
    # Evaluation metrics
    EVALUATION_METRICS = [
        "precision_at_k",
        "recall_at_k", 
        "ndcg_at_k",
        "mean_reciprocal_rank",
        "hit_rate",
        "coverage",
        "diversity",
        "novelty"
    ]
    
    # Test scenarios
    TEST_SCENARIOS = {
        "cold_start": {
            "description": "New users with no interaction history",
            "user_ids": [9999, 8888, 7777],
            "expected_algorithm": "popularity"
        },
        "warm_users": {
            "description": "Existing users with interaction history",
            "user_ids": [1001, 1002, 1003],
            "expected_algorithm": "collaborative_filtering"
        },
        "context_sensitive": {
            "description": "Users with different contexts",
            "test_cases": [
                {"user_id": 1001, "context": {"device": 0, "country": "US"}},
                {"user_id": 1001, "context": {"device": 1, "country": "DE"}},
                {"user_id": 1001, "context": {"device": 2, "country": "FR"}}
            ]
        },
        "edge_cases": {
            "description": "Invalid inputs and edge cases",
            "test_cases": [
                {"user_id": -1, "k": 5, "expected_error": "ValueError"},
                {"user_id": 1001, "k": 0, "expected_error": "ValueError"},
                {"user_id": 1001, "k": 1000, "expected_behavior": "truncate"},
                {"user_id": None, "k": 5, "expected_error": "TypeError"}
            ]
        }
    }
    
    # Mock response templates
    MOCK_RESPONSES = {
        "successful_recommendation": {
            "recommendations": [10001, 10002, 10003, 10004, 10005],
            "user_profile": {
                "stored": {"device": 1, "os": 17, "country": "DE"},
                "used": {"device": 1, "os": 17, "country": "DE"},
                "overrides_applied": False
            }
        },
        "cold_user_recommendation": {
            "recommendations": [15001, 15002, 15003, 15004, 15005],
            "user_profile": {
                "stored": {},
                "used": {"device": -1, "os": -1, "country": ""},
                "overrides_applied": False
            }
        },
        "context_override_recommendation": {
            "recommendations": [20001, 20002, 20003, 20004, 20005],
            "user_profile": {
                "stored": {"device": 1, "os": 17, "country": "DE"},
                "used": {"device": 0, "os": 1, "country": "US"},
                "overrides_applied": True
            }
        }
    }
    
    # Database connection settings (for integration tests)
    DATABASE_CONFIG = {
        "test_db_name": "recommender_test",
        "connection_timeout": 30,
        "max_connections": 10
    }
    
    # Logging configuration for tests
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "capture_warnings": True
    }


def get_test_user_profile(user_id: int) -> Dict[str, Any]:
    """Get test user profile by ID."""
    profiles = {
        1001: {"device": 1, "os": 17, "country": "DE"},
        1002: {"device": 0, "os": 1, "country": "US"},
        1003: {"device": 2, "os": 2, "country": "FR"},
        1004: {"device": 1, "os": 11, "country": "GB"},
        1005: {"device": 0, "os": 3, "country": "IT"}
    }
    return profiles.get(user_id, {})


def get_test_context(scenario: str) -> Dict[str, Any]:
    """Get test context for specific scenario."""
    contexts = {
        "us_mobile": {"device": 1, "os": 17, "country": "US"},
        "de_desktop": {"device": 0, "os": 1, "country": "DE"},
        "fr_tablet": {"device": 2, "os": 2, "country": "FR"},
        "gb_android": {"device": 1, "os": 11, "country": "GB"},
        "default": {"device": -1, "os": -1, "country": ""}
    }
    return contexts.get(scenario, contexts["default"])


def get_api_headers() -> Dict[str, str]:
    """Get standard API headers for testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "RecommenderSystem-Test/1.0"
    }


def get_test_payload(user_id: int = None, k: int = None, 
                    context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate test API payload."""
    payload = {}
    
    if user_id is not None:
        payload["user_id"] = user_id
    
    if k is not None:
        payload["k"] = k
    
    if context is not None:
        payload["env"] = context
    
    return payload


class TestEnvironment:
    """Test environment configuration."""
    
    def __init__(self, environment: str = "test"):
        """Initialize test environment.
        
        Args:
            environment: Environment name ("test", "staging", "local")
        """
        self.environment = environment
        self.config = TestConfig()
    
    def get_api_base_url(self) -> str:
        """Get API base URL for current environment."""
        if self.environment == "local":
            return self.config.API_ENDPOINTS["local_azure_functions"]
        elif self.environment == "staging":
            return self.config.API_ENDPOINTS["production_azure"]
        else:
            return "http://mock-api/api"  # Mock for unit tests
    
    def is_live_environment(self) -> bool:
        """Check if this is a live environment requiring real API calls."""
        return self.environment in ["staging", "production"]
    
    def get_timeout_seconds(self) -> float:
        """Get appropriate timeout for environment."""
        timeouts = {
            "local": 5.0,
            "staging": 10.0,
            "production": 15.0,
            "test": 1.0
        }
        return timeouts.get(self.environment, 5.0)