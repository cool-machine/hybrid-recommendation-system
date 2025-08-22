"""Modern Azure Functions API with improved validation and error handling."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import azure.functions as func
from pydantic import BaseModel, Field, ValidationError

from .config import Config, set_config
from .service import RecommendationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instance (initialized once per container)
_service: Optional[RecommendationService] = None


class RecommendationRequest(BaseModel):
    """Request model with validation."""
    
    user_id: int = Field(ge=0, le=65535, description="User ID (0-65535)")
    k: int = Field(default=10, ge=1, le=100, description="Number of recommendations (1-100)")
    env: Dict[str, Any] = Field(default_factory=dict, description="User environment context")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 12345,
                "k": 10,
                "env": {
                    "device": 1,
                    "os": 3, 
                    "country": "US"
                }
            }
        }


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    
    recommendations: list[int] = Field(description="List of recommended item IDs")
    user_type: str = Field(description="User type: 'warm' or 'cold'")
    algorithm: str = Field(description="Algorithm used for recommendations")
    ground_truth: Optional[int] = Field(default=None, description="Ground truth item if available")
    candidate_count: Optional[int] = Field(default=None, description="Number of candidates generated")
    processing_time_ms: Optional[float] = Field(default=None, description="Processing time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "recommendations": [1234, 5678, 9012],
                "user_type": "warm",
                "algorithm": "ensemble_with_reranking",
                "ground_truth": 1234,
                "candidate_count": 800,
                "processing_time_ms": 45.2
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(description="Error message")
    error_type: str = Field(description="Type of error")
    user_id: Optional[int] = Field(default=None, description="User ID from request")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "User ID out of range",
                "error_type": "validation_error",
                "user_id": 99999
            }
        }


def get_service() -> RecommendationService:
    """Get or initialize the global recommendation service."""
    global _service
    
    if _service is None:
        try:
            # Determine artifacts path (Azure Functions context)
            artifacts_path = Path(__file__).parent.parent / "deployment" / "azure_functions" / "artifacts"
            if not artifacts_path.exists():
                # Fallback for local development
                artifacts_path = Path(__file__).parent / "artifacts"
            
            # Load configuration
            config = Config.load(artifacts_path)
            set_config(config)
            
            # Initialize and load models
            _service = RecommendationService(config)
            _service.load_models()
            
            logger.info("Recommendation service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize recommendation service: {e}")
            raise
    
    return _service


def create_error_response(error_msg: str, error_type: str, user_id: Optional[int] = None, 
                         status_code: int = 400) -> func.HttpResponse:
    """Create a standardized error response."""
    error_response = ErrorResponse(
        error=error_msg,
        error_type=error_type,
        user_id=user_id
    )
    
    return func.HttpResponse(
        error_response.json(),
        status_code=status_code,
        mimetype="application/json"
    )


def handle_recommendation_request(req: func.HttpRequest) -> func.HttpResponse:
    """Handle recommendation requests with proper validation and error handling."""
    start_time = time.time()
    
    try:
        # Parse and validate request
        try:
            body = req.get_json()
            if body is None:
                return create_error_response(
                    "Request body must be valid JSON",
                    "invalid_json"
                )
            
            request_data = RecommendationRequest(**body)
            
        except ValidationError as e:
            return create_error_response(
                f"Invalid request: {e}",
                "validation_error"
            )
        except ValueError:
            return create_error_response(
                "Request body must be valid JSON",
                "invalid_json"
            )
        
        # Get service instance
        try:
            service = get_service()
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return create_error_response(
                "Service temporarily unavailable",
                "service_error",
                status_code=503
            )
        
        # Check service readiness
        if not service.is_ready():
            return create_error_response(
                "Service not ready - models still loading",
                "service_not_ready",
                request_data.user_id,
                status_code=503
            )
        
        # Get recommendations
        try:
            result = service.get_recommendations(
                user_id=request_data.user_id,
                k=request_data.k,
                context=request_data.env
            )
            
            # Add processing time
            processing_time = (time.time() - start_time) * 1000
            result["processing_time_ms"] = round(processing_time, 2)
            
            # Validate and return response
            response = RecommendationResponse(**result)
            
            return func.HttpResponse(
                response.json(),
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return create_error_response(
                "Failed to generate recommendations",
                "recommendation_error",
                request_data.user_id,
                status_code=500
            )
    
    except Exception as e:
        logger.error(f"Unexpected error in recommendation handler: {e}")
        return create_error_response(
            "Internal server error",
            "internal_error",
            status_code=500
        )


def handle_health_check() -> func.HttpResponse:
    """Handle health check requests."""
    try:
        service = get_service()
        status = service.get_status()
        
        if service.is_ready():
            return func.HttpResponse(
                json.dumps({
                    "status": "healthy",
                    "service_ready": True,
                    "details": status
                }),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({
                    "status": "initializing",
                    "service_ready": False,
                    "details": status
                }),
                status_code=503,
                mimetype="application/json"
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return func.HttpResponse(
            json.dumps({
                "status": "unhealthy",
                "error": str(e)
            }),
            status_code=503,
            mimetype="application/json"
        )