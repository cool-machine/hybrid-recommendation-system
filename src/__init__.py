"""Modern recommendation system package."""

__version__ = "2.0.0"
__author__ = "Production ML Team"

from .config import Config, get_config
from .service import RecommendationService

__all__ = ["Config", "get_config", "RecommendationService"]