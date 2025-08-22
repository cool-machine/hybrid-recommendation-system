"""Unit tests for recommendation models."""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.models.collaborative_filtering import CollaborativeFilteringModel
from src.models.popularity import PopularityModel
from src.models.base import BaseRecommendationModel


class TestBaseRecommendationModel:
    """Test base recommendation model interface."""
    
    def test_base_model_abstract(self):
        """Test that base model cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseRecommendationModel()
    
    def test_recommend_method_required(self):
        """Test that recommend method is required."""
        class IncompleteModel(BaseRecommendationModel):
            pass
        
        with pytest.raises(TypeError):
            IncompleteModel()


class TestCollaborativeFilteringModel:
    """Test collaborative filtering model."""
    
    def test_initialization(self):
        """Test model initialization."""
        model = CollaborativeFilteringModel()
        assert model is not None
        assert hasattr(model, 'recommend')
    
    def test_recommend_returns_list(self, mock_model_artifacts):
        """Test that recommend returns a list."""
        model = CollaborativeFilteringModel()
        
        # Mock the model's internal data
        with patch.object(model, '_load_artifacts') as mock_load:
            mock_load.return_value = mock_model_artifacts
            recommendations = model.recommend(user_id=1001, k=5)
            
            assert isinstance(recommendations, list)
            assert len(recommendations) <= 5
    
    def test_recommend_invalid_user(self):
        """Test recommendation with invalid user ID."""
        model = CollaborativeFilteringModel()
        
        with pytest.raises(ValueError):
            model.recommend(user_id=-1, k=5)
    
    def test_recommend_invalid_k(self):
        """Test recommendation with invalid k value."""
        model = CollaborativeFilteringModel()
        
        with pytest.raises(ValueError):
            model.recommend(user_id=1001, k=0)


class TestPopularityModel:
    """Test popularity-based model."""
    
    def test_initialization(self):
        """Test model initialization."""
        model = PopularityModel()
        assert model is not None
        assert hasattr(model, 'recommend')
    
    def test_recommend_cold_user(self, mock_user_profiles):
        """Test recommendation for cold user."""
        model = PopularityModel()
        
        with patch.object(model, '_get_user_context') as mock_context:
            mock_context.return_value = mock_user_profiles[1001]
            recommendations = model.recommend(user_id=9999, k=5)  # Cold user
            
            assert isinstance(recommendations, list)
            assert len(recommendations) <= 5
    
    def test_context_sensitivity(self, mock_user_profiles):
        """Test that context affects recommendations."""
        model = PopularityModel()
        
        # Test different contexts give different results
        context1 = {"device": 0, "os": 1, "country": "US"}
        context2 = {"device": 1, "os": 17, "country": "DE"}
        
        with patch.object(model, '_get_context_recommendations') as mock_rec:
            mock_rec.side_effect = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
            
            rec1 = model.recommend(user_id=9999, k=5, context=context1)
            rec2 = model.recommend(user_id=9999, k=5, context=context2)
            
            assert rec1 != rec2  # Different contexts should give different results


class TestModelIntegration:
    """Test model integration and consistency."""
    
    def test_all_models_implement_interface(self):
        """Test that all models implement the base interface."""
        from src.models import collaborative_filtering, popularity
        
        # Check that all model classes inherit from BaseRecommendationModel
        assert issubclass(collaborative_filtering.CollaborativeFilteringModel, BaseRecommendationModel)
        assert issubclass(popularity.PopularityModel, BaseRecommendationModel)
    
    def test_model_consistency(self, sample_interactions):
        """Test that models return consistent output formats."""
        cf_model = CollaborativeFilteringModel()
        pop_model = PopularityModel()
        
        user_id = 1001
        k = 5
        
        with patch.multiple(
            cf_model,
            _load_artifacts=Mock(return_value={}),
            _get_recommendations=Mock(return_value=[1, 2, 3, 4, 5])
        ), patch.multiple(
            pop_model,
            _get_context_recommendations=Mock(return_value=[6, 7, 8, 9, 10])
        ):
            cf_recs = cf_model.recommend(user_id, k)
            pop_recs = pop_model.recommend(user_id, k)
            
            # Both should return lists of the same length
            assert isinstance(cf_recs, list)
            assert isinstance(pop_recs, list)
            assert len(cf_recs) == k
            assert len(pop_recs) == k
            
            # All recommendations should be integers (article IDs)
            assert all(isinstance(rec, (int, np.integer)) for rec in cf_recs)
            assert all(isinstance(rec, (int, np.integer)) for rec in pop_recs)