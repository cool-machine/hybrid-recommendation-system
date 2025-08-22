# Production Recommendation System

**Status**: ✅ Deployed on Azure (ocp9funcapp-recsys)  
**Live Demo**: [ai-recommender.streamlit.app](https://ai-recommender.streamlit.app)

## Architecture

This is a production-grade hybrid recommendation system with context-aware user profiles, deployed on Azure Functions.

### 🧠 **Multi-Algorithm Ensemble**
1. **Collaborative Filtering (Item-to-Item)**: CF-based similarity from last clicked item
2. **ALS Matrix Factorization**: Implicit feedback collaborative filtering  
3. **Two-Tower Neural Network**: Deep learning user/item embeddings
4. **Popularity Fallback**: Context-aware popularity (OS, device, region)

### 🎯 **LightGBM Reranker**
Final scoring model with 6 engineered features:
- Candidate ranking positions from each algorithm
- User-item cosine similarity from neural embeddings  
- Global popularity rank

### 👤 **User Profile System**
**Hybrid Context Approach**: Uses stored user profiles with manual override capability

**Data Source**: Real device/OS/country extracted from `valid_clicks.parquet`
```python
user_profiles[user_id] = {
    "device": int(click_deviceGroup),    # 0=mobile, 1=desktop, 2=tablet
    "os": int(click_os),                 # 0-17 (Android, iOS, Windows, etc.)  
    "country": str(click_country)        # ISO country code
}
```

**API Behavior**:
- **Default**: Uses stored profile from user's historical data
- **Override**: Manual context via `env` parameter in request
- **Transparency**: Returns both stored and used profiles

### ❄️ **Cold-Start Strategy**
Multi-dimensional popularity blending using user context:

**Algorithm**: `_cold_reco(env, k=10)`
```python
# For k=10 recommendations:
2 items ← Global popularity by OS
2 items ← Global popularity by device  
3 items ← Regional popularity (OS + country)
3 items ← Regional popularity (device + country)
```

**Context Effect by User Type**:

| User Type | Context Change Effect | Algorithm Used |
|-----------|---------------------|----------------|
| **Cold Users** | ✅ **Changes recommendations** | Context-aware popularity blending |
| **Warm Users** | ❌ **No effect** | Multi-algorithm ML pipeline |

### 🔥 **Warm User Pipeline** 
**Multi-stage candidate generation** (context-independent):
1. **Stage 1**: 300 items from Collaborative Filtering (`cf_top300[last_click]`)
2. **Stage 2**: +100 items from ALS (`als_top100[user_id]`) 
3. **Stage 3**: +200 items from global popularity
4. **Stage 4**: +200 items from Two-Tower (`tt_top200[user_id]`)
5. **Final**: LightGBM reranking of 1000 candidates → top-k

## API Reference

### **Endpoint**: `POST /api/reco`
**URL**: `https://ocp9funcapp-recsys.azurewebsites.net/api/reco`

### **Request Format**
```json
{
    "user_id": 12345,
    "k": 10,
    "env": {
        "device": 1,
        "os": 2, 
        "country": "US"
    }
}
```

**Parameters**:
- `user_id` (int): User identifier (0 to 65,535)
- `k` (int, optional): Number of recommendations (default: 10, max: 100)
- `env` (dict, optional): Context overrides
  - `device` (int): 0=mobile, 1=desktop, 2=tablet
  - `os` (int): 0=Android, 1=iOS, 2=Windows, etc.
  - `country` (str): ISO 2-letter country code

### **Response Format**
```json
{
    "recommendations": [58793, 59156, 58020, 57771, 30605],
    "ground_truth": 26859,
    "user_profile": {
        "stored": {"device": 1, "os": 17, "country": "DE"},
        "used": {"device": 1, "os": 2, "country": "DE"},
        "overrides_applied": true
    }
}
```

**Response Fields**:
- `recommendations`: Array of article IDs ranked by relevance
- `ground_truth`: Actual clicked article (for evaluation)
- `user_profile.stored`: User's real context from dataset
- `user_profile.used`: Final context used for recommendations  
- `user_profile.overrides_applied`: Whether manual overrides were provided

### **Usage Examples**

**1. Default recommendations (using stored profile)**:
```bash
curl -X POST https://ocp9funcapp-recsys.azurewebsites.net/api/reco \
  -H "Content-Type: application/json" \
  -d '{"user_id": 12345, "k": 5}'
```

**2. Test context sensitivity (override device)**:
```bash
curl -X POST https://ocp9funcapp-recsys.azurewebsites.net/api/reco \
  -H "Content-Type: application/json" \
  -d '{"user_id": 12345, "k": 5, "env": {"device": 0}}'
```

**3. Full context override**:
```bash
curl -X POST https://ocp9funcapp-recsys.azurewebsites.net/api/reco \
  -H "Content-Type: application/json" \
  -d '{"user_id": 12345, "k": 5, "env": {"device": 0, "os": 1, "country": "US"}}'
```

## Deployment

- **Azure Function**: `ocp9funcapp-recsys` (Central US)
- **Runtime**: Python 3.10 + LightGBM + 406MB model artifacts
- **Pricing**: Consumption Plan (pay-per-request)
- **Cold Start**: ~2-3 seconds (lazy loading of 406MB models)

## Project Structure

```
recommender/
├── 📂 src/                      # Core source code
│   ├── models/                  # Recommendation algorithms
│   ├── algorithms/              # Algorithm implementations  
│   ├── training/                # Model training pipelines
│   └── service/                 # Business logic layer
├── 📂 deployment/               # Production deployments
│   ├── azure_functions/         # Azure Functions (production API)
│   └── streamlit/               # Web interface demo
├── 📂 artifacts/                # Model artifacts (406MB)
│   ├── cf_i2i_top300.npy       # Collaborative filtering
│   ├── als_top100.npy          # ALS matrix factorization
│   ├── tt_top200.npy           # Two-tower neural network
│   ├── valid_clicks.parquet    # User profiles dataset
│   └── reranker.txt            # LightGBM model
├── 📂 tests/                    # Comprehensive test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── fixtures/               # Test data and mocks
│   └── test_system.py          # End-to-end system tests
├── 📂 docs/                     # Complete documentation
│   ├── api/                    # API reference
│   ├── architecture/           # System design
│   ├── guides/                 # User guides
│   └── models/                 # Algorithm documentation
├── 📂 data/                     # Data management
│   ├── sample/                 # Sample datasets for testing
│   └── examples/               # Example data files
└── 📂 notebooks/                # Research and analysis
    ├── collaborative-filtering.ipynb
    ├── als.ipynb
    └── hybrid-rec.ipynb
```

## Performance

Production metrics from Azure deployment:
- **Warm Users**: Multi-algorithm ensemble with LightGBM reranking
- **Cold Users**: Context-aware popularity with 4-tier blending
- **Latency**: Sub-second response times on Consumption Plan
- **Scalability**: Auto-scaling based on request volume

## Development

### Quick Start
```bash
# Clone repository
git clone https://github.com/user/recommender.git
cd recommender

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start local development server
cd deployment/azure_functions
func start
```

### Testing
Comprehensive test suite covering:
- **Unit Tests**: Individual algorithm components
- **Integration Tests**: API endpoints and deployment
- **System Tests**: End-to-end workflows
- **Performance Tests**: Response time and load testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests
pytest tests/test_system.py # System tests

# Run with coverage
pytest --cov=src --cov-report=html
```

### Documentation
Complete documentation available in `/docs/`:
- **[Getting Started](docs/guides/getting-started.md)** - Quick setup guide
- **[API Reference](docs/api/README.md)** - Complete API documentation
- **[Architecture](docs/architecture/README.md)** - System design overview
- **[Developer Guide](docs/guides/developer-guide.md)** - Development setup

## Model Artifacts

The system uses pre-trained models (406MB total):
- **Collaborative Filtering**: Item-to-item similarity matrix
- **ALS Matrix Factorization**: User/item latent factors
- **Two-Tower Neural Network**: Deep learning embeddings
- **LightGBM Reranker**: Gradient boosting model
- **User Profiles**: 65K user device/OS/country data

> **Note**: Model artifacts are stored in Azure Blob Storage for production deployment. 
> For local development, contact the team for access to model files.

## Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- **Python 3.10+** required
- **Type hints** for all public interfaces
- **Docstrings** for all modules and functions
- **Tests** for all new features
- **No AI assistant references** in commits or code

## License

This project is proprietary. All rights reserved.

## Support

- **Issues**: Create GitHub issue for bugs or feature requests
- **Documentation**: Check `/docs/` directory
- **Questions**: Use GitHub Discussions

Built from p9/p9_v2 research projects and optimized for production deployment.