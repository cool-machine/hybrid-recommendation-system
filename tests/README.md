# Tests Directory

Comprehensive test suite for the recommendation system.

## Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for system components
├── fixtures/          # Test data and mock objects
├── conftest.py       # Pytest configuration and fixtures
└── test_system.py    # System-level tests
```

## Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_models.py::test_collaborative_filtering
```

## Test Categories

### Unit Tests
- `test_models.py` - Model implementations
- `test_config.py` - Configuration management
- `test_service.py` - Service layer
- `test_training.py` - Training utilities

### Integration Tests
- `test_api.py` - API endpoints
- `test_deployment.py` - Deployment configurations
- `test_pipeline.py` - End-to-end pipeline

### Fixtures
- `sample_data.py` - Test datasets
- `mock_models.py` - Mock model objects
- `test_config.py` - Test configurations

## Test Data

Tests use sample data from `data/sample/` and test-specific fixtures from `tests/fixtures/`.

## Guidelines

1. **Isolate tests** - Each test should be independent
2. **Use fixtures** - Reuse test data and setup
3. **Mock external calls** - Don't hit real APIs in tests
4. **Test edge cases** - Include error conditions
5. **Keep tests fast** - Unit tests should run in seconds