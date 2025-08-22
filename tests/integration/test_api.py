"""Integration tests for API endpoints."""
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from service.recommendation_service import RecommendationService


class TestAPIIntegration:
    """Test API endpoint integration."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for API testing."""
        return "https://ocp9funcapp-recsys.azurewebsites.net/api"
    
    def test_health_endpoint(self, base_url):
        """Test health check endpoint."""
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_recommendation_endpoint_structure(self, base_url):
        """Test recommendation endpoint response structure."""
        payload = {
            "user_id": 1001,
            "k": 5
        }
        
        response = requests.post(
            f"{base_url}/reco",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "recommendations" in data
        assert "user_profile" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) <= 5
    
    def test_recommendation_with_context_override(self, base_url):
        """Test context override functionality."""
        payload = {
            "user_id": 1001,
            "k": 3,
            "env": {
                "device": 0,
                "os": 1,
                "country": "US"
            }
        }
        
        response = requests.post(
            f"{base_url}/reco",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check override was applied
        user_profile = data["user_profile"]
        assert "stored" in user_profile
        assert "used" in user_profile
        assert "overrides_applied" in user_profile
        
        # Verify context was used
        used_profile = user_profile["used"]
        assert used_profile["device"] == 0
        assert used_profile["os"] == 1
        assert used_profile["country"] == "US"
    
    def test_invalid_user_id(self, base_url):
        """Test handling of invalid user ID."""
        payload = {
            "user_id": -1,
            "k": 5
        }
        
        response = requests.post(
            f"{base_url}/reco",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        # Should either return error or handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_invalid_k_parameter(self, base_url):
        """Test handling of invalid k parameter."""
        payload = {
            "user_id": 1001,
            "k": 0
        }
        
        response = requests.post(
            f"{base_url}/reco",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        # Should return error for invalid k
        assert response.status_code in [400, 422]


class TestServiceIntegration:
    """Test service layer integration."""
    
    def test_recommendation_service_initialization(self):
        """Test that service initializes correctly."""
        service = RecommendationService()
        assert service is not None
        assert hasattr(service, 'get_recommendations')
    
    @patch('src.service.recommendation_service.RecommendationService._load_user_profiles')
    @patch('src.service.recommendation_service.RecommendationService._load_model_artifacts')
    def test_service_recommendation_flow(self, mock_artifacts, mock_profiles):
        """Test complete recommendation flow through service."""
        # Mock dependencies
        mock_profiles.return_value = {
            1001: {"device": 1, "os": 17, "country": "DE"}
        }
        mock_artifacts.return_value = {
            "cf_top300": [[1, 2, 3, 4, 5]],
            "als_top100": [[6, 7, 8, 9, 10]],
            "pop_list": [11, 12, 13, 14, 15]
        }
        
        service = RecommendationService()
        
        # Test recommendation generation
        result = service.get_recommendations(
            user_id=1001,
            k=5
        )
        
        assert "recommendations" in result
        assert "user_profile" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) <= 5


class TestPipelineIntegration:
    """Test end-to-end pipeline integration."""
    
    def test_cold_user_pipeline(self):
        """Test cold user recommendation pipeline."""
        # Test with user that should be classified as cold
        user_id = 99999  # Non-existent user
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_recommendations.return_value = {
                "recommendations": [1, 2, 3, 4, 5],
                "user_profile": {
                    "stored": {},
                    "used": {"device": -1, "os": -1, "country": ""},
                    "overrides_applied": False
                }
            }
            
            result = mock_instance.get_recommendations(user_id=user_id, k=5)
            
            assert result["recommendations"] == [1, 2, 3, 4, 5]
            assert result["user_profile"]["overrides_applied"] is False
    
    def test_warm_user_pipeline(self):
        """Test warm user recommendation pipeline."""
        # Test with user that should have stored profile
        user_id = 1001
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_recommendations.return_value = {
                "recommendations": [10, 20, 30, 40, 50],
                "user_profile": {
                    "stored": {"device": 1, "os": 17, "country": "DE"},
                    "used": {"device": 1, "os": 17, "country": "DE"},
                    "overrides_applied": False
                }
            }
            
            result = mock_instance.get_recommendations(user_id=user_id, k=5)
            
            assert result["recommendations"] == [10, 20, 30, 40, 50]
            assert result["user_profile"]["stored"]["device"] == 1
    
    def test_context_override_pipeline(self):
        """Test context override functionality."""
        user_id = 1001
        context_override = {"device": 0, "os": 1, "country": "US"}
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_recommendations.return_value = {
                "recommendations": [100, 200, 300, 400, 500],
                "user_profile": {
                    "stored": {"device": 1, "os": 17, "country": "DE"},
                    "used": {"device": 0, "os": 1, "country": "US"},
                    "overrides_applied": True
                }
            }
            
            result = mock_instance.get_recommendations(
                user_id=user_id, 
                k=5, 
                env=context_override
            )
            
            assert result["user_profile"]["overrides_applied"] is True
            assert result["user_profile"]["used"]["device"] == 0
            assert result["user_profile"]["used"]["country"] == "US"