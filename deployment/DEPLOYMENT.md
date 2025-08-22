# Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
- Azure CLI installed and configured
- Azure Functions Core Tools v4.x
- Python 3.10+

### Deploy to Existing Function App (ocp9funcapp-recsys)

```bash
# 1. Navigate to modernized deployment
cd deployment/azure_functions_v2

# 2. Copy model artifacts from v1
cp -r ../azure_functions/artifacts .

# 3. Deploy to existing function app
func azure functionapp publish ocp9funcapp-recsys --python
```

### Test Deployment

```bash
# Health check
curl -X GET "https://ocp9funcapp-recsys.azurewebsites.net/api/health?code=YOUR_FUNCTION_KEY"

# Test recommendation
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco?code=YOUR_FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 12345, "k": 10, "env": {"device": 1, "os": 3, "country": "US"}}'
```

## 🏗️ Architecture

### New Structure
```
deployment/azure_functions_v2/
├── function_app.py          # Modern function app entry point
├── requirements.txt         # Updated dependencies with Pydantic
├── host.json               # Enhanced runtime configuration
└── artifacts/              # Model artifacts (copied from v1)
```

### Key Improvements

**1. Modular Architecture**
- Clean separation of concerns
- Testable components
- Pluggable algorithms

**2. Enhanced API**
- Input validation with Pydantic
- Structured error responses
- Performance monitoring

**3. Better Configuration**
- Environment-aware settings
- Centralized configuration management
- Runtime validation

**4. Improved Monitoring**
- Health check endpoints
- Structured logging
- Application Insights integration

## 🔧 Configuration

### Environment Variables

```bash
# Optional configuration overrides
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
DEBUG_MODE=false                  # Enable debug features
ENVIRONMENT=production            # development, staging, production
```

### Model Configuration

Models are loaded from the `artifacts/` directory. Required files:
- `reranker.txt` - LightGBM model
- `last_click.npy` - User interaction history
- `cf_i2i_top300.npy` - CF similarity matrix
- `als_top100.npy` - ALS recommendations
- `tt_top200.npy` - Two-Tower recommendations
- `pop_list.npy` - Popularity rankings
- `final_twotower_user_vec.npy` - User embeddings
- `final_twotower_item_vec.npy` - Item embeddings

## 📊 Monitoring

### Health Checks

**GET /api/health**
```json
{
  "status": "healthy",
  "service_ready": true,
  "details": {
    "service_ready": true,
    "models": {
      "ItemToItemCF": true,
      "ALS": true,
      "TwoTower": true,
      "Popularity": true
    },
    "candidate_generators": 4,
    "reranker_ready": true,
    "cold_start_ready": true
  }
}
```

### API Metrics

All API responses include:
- `processing_time_ms`: Request processing time
- `algorithm`: Algorithm used for recommendations
- `user_type`: "warm" or "cold" user classification

### Application Insights

Enhanced logging provides:
- Request/response tracking
- Error monitoring with context
- Performance metrics
- Custom telemetry

## 🔄 Rollback Plan

If issues occur, rollback to v1:

```bash
# 1. Navigate to v1 deployment
cd deployment/azure_functions

# 2. Redeploy v1 function
func azure functionapp publish ocp9funcapp-recsys --python
```

## 🧪 Local Development

```bash
# 1. Install dependencies
cd deployment/azure_functions_v2
pip install -r requirements.txt

# 2. Copy artifacts
cp -r ../azure_functions/artifacts .

# 3. Run locally
func start --python
```

Access locally at: http://localhost:7071/api/reco

## 🔍 Troubleshooting

### Common Issues

**Service Not Ready (503)**
- Check that all model artifacts are present
- Verify artifacts directory permissions
- Review Application Insights logs

**Validation Errors (400)**
- Ensure user_id is 0-65535
- Check k parameter is 1-100
- Validate JSON request format

**Performance Issues**
- Monitor memory usage in Azure portal
- Check Application Insights performance metrics
- Consider increasing function timeout if needed

### Debug Mode

Enable debug logging:
```bash
# Set environment variable
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

This provides detailed request/response logging and model loading information.