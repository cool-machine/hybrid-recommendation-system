"""Test data fixtures and utilities."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any


def create_sample_users(n_users: int = 100) -> pd.DataFrame:
    """Create sample user data for testing.
    
    Args:
        n_users: Number of users to generate
        
    Returns:
        DataFrame with user profiles
    """
    np.random.seed(42)  # For reproducible tests
    
    devices = [0, 1, 2]  # desktop, mobile, tablet
    os_list = list(range(1, 18))  # Various OS types
    countries = ["US", "DE", "FR", "GB", "IT", "ES", "NL", "BR", "JP", "IN"]
    
    return pd.DataFrame({
        'user_id': range(1001, 1001 + n_users),
        'click_deviceGroup': np.random.choice(devices, n_users),
        'click_os': np.random.choice(os_list, n_users),
        'click_country': np.random.choice(countries, n_users),
        'registration_date': pd.date_range('2024-01-01', periods=n_users, freq='H'),
        'last_active': pd.date_range('2024-08-01', periods=n_users, freq='30min')
    })


def create_sample_interactions(n_interactions: int = 1000) -> pd.DataFrame:
    """Create sample interaction data for testing.
    
    Args:
        n_interactions: Number of interactions to generate
        
    Returns:
        DataFrame with user-item interactions
    """
    np.random.seed(42)
    
    user_ids = np.random.randint(1001, 1101, n_interactions)  # 100 users
    article_ids = np.random.randint(10000, 20000, n_interactions)  # 10k articles
    
    return pd.DataFrame({
        'user_id': user_ids,
        'click_article_id': article_ids,
        'click_timestamp': pd.date_range('2024-07-01', periods=n_interactions, freq='5min'),
        'click_deviceGroup': np.random.choice([0, 1, 2], n_interactions),
        'click_os': np.random.choice(range(1, 18), n_interactions),
        'click_country': np.random.choice(["US", "DE", "FR", "GB"], n_interactions),
        'session_id': np.random.randint(100000, 999999, n_interactions),
        'click_duration': np.random.exponential(30, n_interactions)  # seconds
    })


def create_sample_articles(n_articles: int = 500) -> pd.DataFrame:
    """Create sample article data for testing.
    
    Args:
        n_articles: Number of articles to generate
        
    Returns:
        DataFrame with article metadata
    """
    np.random.seed(42)
    
    categories = ["technology", "sports", "politics", "entertainment", "business", "health"]
    languages = ["en", "de", "fr", "es", "it"]
    
    return pd.DataFrame({
        'article_id': range(10000, 10000 + n_articles),
        'title': [f"Sample Article {i}" for i in range(n_articles)],
        'category': np.random.choice(categories, n_articles),
        'language': np.random.choice(languages, n_articles),
        'publish_date': pd.date_range('2024-01-01', periods=n_articles, freq='2H'),
        'word_count': np.random.randint(200, 2000, n_articles),
        'view_count': np.random.exponential(1000, n_articles).astype(int),
        'like_count': np.random.exponential(50, n_articles).astype(int)
    })


def create_mock_model_artifacts() -> Dict[str, np.ndarray]:
    """Create mock model artifacts for testing.
    
    Returns:
        Dictionary containing mock model data
    """
    np.random.seed(42)
    
    return {
        "cf_top300": np.random.randint(10000, 20000, size=(1000, 300)),
        "als_top100": np.random.randint(10000, 20000, size=(1000, 100)),
        "tt_top200": np.random.randint(10000, 20000, size=(1000, 200)),
        "pop_list": np.random.randint(10000, 20000, size=1000),
        "last_click": np.random.randint(10000, 20000, size=65536),
        "user_embeddings": np.random.random((1000, 128)),
        "item_embeddings": np.random.random((10000, 128))
    }


def create_mock_user_profiles() -> Dict[int, Dict[str, Any]]:
    """Create mock user profiles for testing.
    
    Returns:
        Dictionary mapping user IDs to profiles
    """
    return {
        1001: {"device": 1, "os": 17, "country": "DE"},
        1002: {"device": 0, "os": 1, "country": "US"},
        1003: {"device": 2, "os": 2, "country": "FR"},
        1004: {"device": 1, "os": 11, "country": "GB"},
        1005: {"device": 0, "os": 3, "country": "IT"},
        9999: {}  # Cold user with no profile
    }


def create_mock_recommendations() -> Dict[str, Any]:
    """Create mock recommendation results for testing.
    
    Returns:
        Dictionary with recommendation structure
    """
    return {
        "recommendations": [10001, 10002, 10003, 10004, 10005],
        "ground_truth": 10001,
        "user_profile": {
            "stored": {"device": 1, "os": 17, "country": "DE"},
            "used": {"device": 1, "os": 17, "country": "DE"},
            "overrides_applied": False
        },
        "algorithm_used": "collaborative_filtering",
        "confidence_scores": [0.95, 0.87, 0.82, 0.78, 0.71],
        "explanation": "Based on similar users who liked technology articles"
    }


def create_test_dataset(output_dir: Path = None) -> Dict[str, Path]:
    """Create complete test dataset and save to files.
    
    Args:
        output_dir: Directory to save test files (default: tests/fixtures/data/)
        
    Returns:
        Dictionary mapping dataset names to file paths
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "data"
    
    output_dir.mkdir(exist_ok=True)
    
    # Create datasets
    users_df = create_sample_users(100)
    interactions_df = create_sample_interactions(1000)
    articles_df = create_sample_articles(500)
    
    # Save to files
    file_paths = {}
    
    # CSV files
    users_path = output_dir / "test_users.csv"
    users_df.to_csv(users_path, index=False)
    file_paths["users"] = users_path
    
    interactions_path = output_dir / "test_interactions.csv"
    interactions_df.to_csv(interactions_path, index=False)
    file_paths["interactions"] = interactions_path
    
    articles_path = output_dir / "test_articles.csv"
    articles_df.to_csv(articles_path, index=False)
    file_paths["articles"] = articles_path
    
    # Parquet files (for better performance)
    users_parquet = output_dir / "test_users.parquet"
    users_df.to_parquet(users_parquet, index=False)
    file_paths["users_parquet"] = users_parquet
    
    interactions_parquet = output_dir / "test_interactions.parquet"
    interactions_df.to_parquet(interactions_parquet, index=False)
    file_paths["interactions_parquet"] = interactions_parquet
    
    # Model artifacts
    artifacts = create_mock_model_artifacts()
    for name, data in artifacts.items():
        artifact_path = output_dir / f"test_{name}.npy"
        np.save(artifact_path, data)
        file_paths[name] = artifact_path
    
    return file_paths


def load_test_config() -> Dict[str, Any]:
    """Load test configuration settings.
    
    Returns:
        Dictionary with test configuration
    """
    return {
        "test_user_id": 1001,
        "cold_user_id": 9999,
        "test_k_values": [1, 5, 10, 20],
        "test_contexts": [
            {"device": 0, "os": 1, "country": "US"},
            {"device": 1, "os": 17, "country": "DE"},
            {"device": 2, "os": 2, "country": "FR"}
        ],
        "performance_thresholds": {
            "max_response_time": 2.0,  # seconds
            "max_memory_mb": 500,
            "min_precision_at_5": 0.1
        },
        "api_endpoints": {
            "local": "http://localhost:7071/api",
            "azure": "https://ocp9funcapp-recsys.azurewebsites.net/api"
        }
    }


if __name__ == "__main__":
    # Generate test datasets when run directly
    print("Creating test datasets...")
    file_paths = create_test_dataset()
    
    print("Created test files:")
    for name, path in file_paths.items():
        print(f"  {name}: {path}")
    
    print("\nDataset statistics:")
    print(f"  Users: {len(create_sample_users())}")
    print(f"  Interactions: {len(create_sample_interactions())}")
    print(f"  Articles: {len(create_sample_articles())}")
    print(f"  User profiles: {len(create_mock_user_profiles())}")