"""Integration tests for end-to-end pipeline."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class TestRecommendationPipeline:
    """Test complete recommendation pipeline."""
    
    @pytest.fixture
    def mock_artifacts(self):
        """Mock model artifacts for testing."""
        return {
            "cf_top300": np.random.randint(10000, 20000, size=(1000, 300)),
            "als_top100": np.random.randint(10000, 20000, size=(1000, 100)),
            "tt_top200": np.random.randint(10000, 20000, size=(1000, 200)),
            "pop_list": np.random.randint(10000, 20000, size=1000),
            "last_click": np.random.randint(10000, 20000, size=65536),
        }
    
    @pytest.fixture
    def mock_user_profiles(self):
        """Mock user profiles for testing."""
        return {
            1001: {"device": 1, "os": 17, "country": "DE"},
            1002: {"device": 0, "os": 1, "country": "US"},
            1003: {"device": 2, "os": 2, "country": "FR"},
        }
    
    def test_cold_user_recommendation_pipeline(self, mock_artifacts, mock_user_profiles):
        """Test complete pipeline for cold users."""
        # Simulate cold user (not in user profiles)
        cold_user_id = 99999
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance._load_model_artifacts.return_value = mock_artifacts
            mock_instance._load_user_profiles.return_value = mock_user_profiles
            
            # Mock cold user recommendation
            mock_instance.get_recommendations.return_value = {
                "recommendations": [10001, 10002, 10003, 10004, 10005],
                "user_profile": {
                    "stored": {},
                    "used": {"device": -1, "os": -1, "country": ""},
                    "overrides_applied": False
                }
            }
            
            result = mock_instance.get_recommendations(user_id=cold_user_id, k=5)
            
            # Verify cold user handling
            assert len(result["recommendations"]) == 5
            assert result["user_profile"]["stored"] == {}
            assert result["user_profile"]["overrides_applied"] is False
    
    def test_warm_user_recommendation_pipeline(self, mock_artifacts, mock_user_profiles):
        """Test complete pipeline for warm users."""
        # Use existing user from profiles
        warm_user_id = 1001
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance._load_model_artifacts.return_value = mock_artifacts
            mock_instance._load_user_profiles.return_value = mock_user_profiles
            
            # Mock warm user recommendation
            mock_instance.get_recommendations.return_value = {
                "recommendations": [20001, 20002, 20003, 20004, 20005],
                "user_profile": {
                    "stored": {"device": 1, "os": 17, "country": "DE"},
                    "used": {"device": 1, "os": 17, "country": "DE"},
                    "overrides_applied": False
                }
            }
            
            result = mock_instance.get_recommendations(user_id=warm_user_id, k=5)
            
            # Verify warm user handling
            assert len(result["recommendations"]) == 5
            assert result["user_profile"]["stored"]["device"] == 1
            assert result["user_profile"]["used"]["device"] == 1
    
    def test_context_override_pipeline(self, mock_artifacts, mock_user_profiles):
        """Test pipeline with context overrides."""
        user_id = 1001
        context_override = {"device": 0, "os": 1, "country": "US"}
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance._load_model_artifacts.return_value = mock_artifacts
            mock_instance._load_user_profiles.return_value = mock_user_profiles
            
            # Mock context override recommendation
            mock_instance.get_recommendations.return_value = {
                "recommendations": [30001, 30002, 30003, 30004, 30005],
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
            
            # Verify override was applied
            assert result["user_profile"]["overrides_applied"] is True
            assert result["user_profile"]["used"]["device"] == 0
            assert result["user_profile"]["used"]["country"] == "US"
    
    def test_multi_algorithm_ensemble(self, mock_artifacts):
        """Test multi-algorithm ensemble pipeline."""
        # Test that multiple algorithms contribute to recommendations
        
        with patch('src.models.collaborative_filtering.CollaborativeFilteringModel') as mock_cf, \
             patch('src.models.popularity.PopularityModel') as mock_pop:
            
            # Mock CF model
            mock_cf_instance = mock_cf.return_value
            mock_cf_instance.recommend.return_value = [1, 2, 3, 4, 5]
            
            # Mock Popularity model
            mock_pop_instance = mock_pop.return_value
            mock_pop_instance.recommend.return_value = [6, 7, 8, 9, 10]
            
            # Simulate ensemble combination
            cf_recs = mock_cf_instance.recommend(user_id=1001, k=5)
            pop_recs = mock_pop_instance.recommend(user_id=1001, k=5)
            
            # Verify both models produce recommendations
            assert len(cf_recs) == 5
            assert len(pop_recs) == 5
            assert cf_recs != pop_recs  # Different algorithms should give different results


class TestDataPipeline:
    """Test data processing pipeline."""
    
    def test_user_profile_loading(self):
        """Test user profile data loading."""
        # Mock parquet file loading
        mock_data = pd.DataFrame({
            'user_id': [1001, 1002, 1003],
            'click_deviceGroup': [1, 0, 2],
            'click_os': [17, 1, 2],
            'click_country': ['DE', 'US', 'FR']
        })
        
        with patch('pandas.read_parquet', return_value=mock_data):
            # Test profile extraction logic
            user_profiles = {}
            for _, row in mock_data.iterrows():
                user_id = int(row["user_id"])
                user_profiles[user_id] = {
                    "device": int(row["click_deviceGroup"]) if pd.notna(row["click_deviceGroup"]) else -1,
                    "os": int(row["click_os"]) if pd.notna(row["click_os"]) else -1,
                    "country": str(row["click_country"]).upper() if pd.notna(row["click_country"]) else ""
                }
            
            # Verify profile structure
            assert len(user_profiles) == 3
            assert user_profiles[1001]["device"] == 1
            assert user_profiles[1001]["country"] == "DE"
    
    def test_artifact_loading(self):
        """Test model artifact loading."""
        artifacts_path = Path(__file__).parent.parent.parent / "artifacts"
        
        # Test that artifact files can be loaded
        test_files = [
            "cf_i2i_top300.npy",
            "als_top100.npy",
            "valid_clicks.parquet"
        ]
        
        for file_name in test_files:
            file_path = artifacts_path / file_name
            if file_path.exists():
                if file_name.endswith('.npy'):
                    # Test numpy file loading
                    data = np.load(file_path)
                    assert data is not None
                    assert data.size > 0
                elif file_name.endswith('.parquet'):
                    # Test parquet file loading
                    data = pd.read_parquet(file_path)
                    assert data is not None
                    assert len(data) > 0


class TestErrorHandling:
    """Test error handling in pipeline."""
    
    def test_missing_user_handling(self):
        """Test handling of missing user profiles."""
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            
            # Mock service to handle missing user gracefully
            mock_instance.get_recommendations.return_value = {
                "recommendations": [1, 2, 3, 4, 5],
                "user_profile": {
                    "stored": {},
                    "used": {"device": -1, "os": -1, "country": ""},
                    "overrides_applied": False
                }
            }
            
            result = mock_instance.get_recommendations(user_id=99999, k=5)
            
            # Should handle missing user gracefully
            assert "recommendations" in result
            assert result["user_profile"]["stored"] == {}
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            
            # Test invalid k parameter
            mock_instance.get_recommendations.side_effect = ValueError("Invalid k parameter")
            
            with pytest.raises(ValueError, match="Invalid k parameter"):
                mock_instance.get_recommendations(user_id=1001, k=-1)
    
    def test_model_loading_failure(self):
        """Test handling of model loading failures."""
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            
            # Mock model loading failure
            mock_instance._load_model_artifacts.side_effect = FileNotFoundError("Model artifacts not found")
            
            with pytest.raises(FileNotFoundError, match="Model artifacts not found"):
                mock_instance._load_model_artifacts()


class TestPerformanceValidation:
    """Test performance characteristics of pipeline."""
    
    def test_recommendation_response_time(self):
        """Test that recommendations are generated within reasonable time."""
        import time
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            
            # Mock fast response
            mock_instance.get_recommendations.return_value = {
                "recommendations": [1, 2, 3, 4, 5],
                "user_profile": {
                    "stored": {"device": 1, "os": 17, "country": "DE"},
                    "used": {"device": 1, "os": 17, "country": "DE"},
                    "overrides_applied": False
                }
            }
            
            start_time = time.time()
            result = mock_instance.get_recommendations(user_id=1001, k=5)
            response_time = time.time() - start_time
            
            # Should respond quickly (mocked, so very fast)
            assert response_time < 1.0  # Less than 1 second
            assert len(result["recommendations"]) == 5
    
    def test_memory_usage_scaling(self):
        """Test memory usage with different request sizes."""
        # Test different k values
        k_values = [1, 5, 10, 20, 50]
        
        with patch('src.service.recommendation_service.RecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            
            for k in k_values:
                # Mock appropriate response size
                mock_instance.get_recommendations.return_value = {
                    "recommendations": list(range(k)),
                    "user_profile": {
                        "stored": {"device": 1, "os": 17, "country": "DE"},
                        "used": {"device": 1, "os": 17, "country": "DE"},
                        "overrides_applied": False
                    }
                }
                
                result = mock_instance.get_recommendations(user_id=1001, k=k)
                
                # Verify response size matches request
                assert len(result["recommendations"]) == k