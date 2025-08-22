"""Configuration management for the recommendation system."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for model artifacts and parameters."""
    
    # Model artifact paths
    artifacts_dir: Path = field(default_factory=lambda: Path("artifacts"))
    
    # Individual model files
    lightgbm_model: str = "reranker.txt"
    last_click_file: str = "last_click.npy"
    cf_candidates_file: str = "cf_i2i_top300.npy"
    als_candidates_file: str = "als_top100.npy"
    twotower_candidates_file: str = "tt_top200.npy"
    popularity_file: str = "pop_list.npy"
    user_embeddings_file: str = "final_twotower_user_vec.npy"
    item_embeddings_file: str = "final_twotower_item_vec.npy"
    ground_truth_file: str = "valid_clicks.parquet"
    
    # Model parameters
    max_candidates_cf: int = 300
    max_candidates_als: int = 100
    max_candidates_tt: int = 200
    max_candidates_pop: int = 600
    final_candidate_pool: int = 1000
    
    # Feature engineering
    feature_count: int = 6
    
    def get_artifact_path(self, filename: str) -> Path:
        """Get full path to an artifact file."""
        return self.artifacts_dir / filename


@dataclass 
class APIConfig:
    """Configuration for API behavior and limits."""
    
    # Request limits
    max_recommendations: int = 100
    default_recommendations: int = 10
    max_user_id: int = 65_535
    request_timeout_seconds: int = 30
    
    # Cold start parameters
    cold_start_allocation: dict[str, int] = field(default_factory=lambda: {
        "os_global": 2,
        "device_global": 2, 
        "os_regional": 3,
        "device_regional": 3
    })
    
    # Caching
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    cache_max_entries: int = 10000


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""
    
    log_level: str = "INFO"
    debug_mode: bool = False
    environment: str = "production"  # development, staging, production
    
    # Azure Function specific
    function_timeout_seconds: int = 230  # Azure Functions timeout - 10s buffer
    
    @classmethod
    def from_env(cls) -> EnvironmentConfig:
        """Create configuration from environment variables."""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "production"),
        )


@dataclass
class Config:
    """Main configuration container."""
    
    model: ModelConfig = field(default_factory=ModelConfig)
    api: APIConfig = field(default_factory=APIConfig)  
    env: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    
    @classmethod
    def load(cls, artifacts_dir: Optional[Path] = None) -> Config:
        """Load configuration with optional artifacts directory override."""
        config = cls()
        config.env = EnvironmentConfig.from_env()
        
        if artifacts_dir:
            config.model.artifacts_dir = artifacts_dir
            
        return config
    
    def validate(self) -> None:
        """Validate configuration and check file existence."""
        if not self.model.artifacts_dir.exists():
            raise ValueError(f"Artifacts directory not found: {self.model.artifacts_dir}")
            
        # Check critical model files exist
        critical_files = [
            self.model.lightgbm_model,
            self.model.last_click_file,
            self.model.cf_candidates_file,
            self.model.als_candidates_file,
            self.model.popularity_file,
        ]
        
        for filename in critical_files:
            filepath = self.model.get_artifact_path(filename)
            if not filepath.exists():
                raise FileNotFoundError(f"Critical model file not found: {filepath}")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
        _config.validate()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    config.validate()
    _config = config