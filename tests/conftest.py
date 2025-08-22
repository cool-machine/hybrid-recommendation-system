"""Pytest configuration and shared fixtures."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_data_dir():
    """Path to sample data directory."""
    return Path(__file__).parent.parent / "data" / "sample"


@pytest.fixture
def sample_users(sample_data_dir):
    """Sample user data for testing."""
    return pd.read_csv(sample_data_dir / "sample_users.csv")


@pytest.fixture
def sample_interactions(sample_data_dir):
    """Sample interaction data for testing."""
    return pd.read_csv(sample_data_dir / "sample_interactions.csv")


@pytest.fixture
def sample_articles(sample_data_dir):
    """Sample article data for testing."""
    return pd.read_csv(sample_data_dir / "sample_articles.csv")


@pytest.fixture
def mock_user_profiles():
    """Mock user profiles for testing."""
    return {
        1001: {"device": 1, "os": 17, "country": "DE"},
        1002: {"device": 0, "os": 1, "country": "US"},
        1003: {"device": 2, "os": 2, "country": "FR"},
    }


@pytest.fixture
def mock_recommendations():
    """Mock recommendation results."""
    return {
        "recommendations": [10001, 10002, 10003, 10004, 10005],
        "ground_truth": 10001,
        "user_profile": {
            "stored": {"device": 1, "os": 17, "country": "DE"},
            "used": {"device": 1, "os": 17, "country": "DE"},
            "overrides_applied": False
        }
    }


@pytest.fixture
def mock_model_artifacts():
    """Mock model artifacts for testing."""
    return {
        "cf_top300": np.random.randint(10000, 20000, size=(1000, 300)),
        "als_top100": np.random.randint(10000, 20000, size=(1000, 100)),
        "tt_top200": np.random.randint(10000, 20000, size=(1000, 200)),
        "pop_list": np.random.randint(10000, 20000, size=1000),
        "last_click": np.random.randint(10000, 20000, size=65536),
    }