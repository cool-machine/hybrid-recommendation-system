# API Documentation

Complete API reference for the recommendation system.

## Base URL

- **Production**: `https://ocp9funcapp-recsys.azurewebsites.net/api`
- **Local Development**: `http://localhost:7071/api`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

> **Note**: In production deployments, consider implementing API key authentication or OAuth 2.0.

## Common Headers

```http
Content-Type: application/json
Accept: application/json
```

## Response Format

All API responses follow a consistent JSON structure:

### Success Response
```json
{
  "recommendations": [item_id_1, item_id_2, ...],
  "user_profile": {
    "stored": {"device": 1, "os": 17, "country": "DE"},
    "used": {"device": 1, "os": 17, "country": "DE"}, 
    "overrides_applied": false
  },
  "metadata": {
    "algorithm_used": "ensemble",
    "request_time": "2024-08-22T10:30:00Z",
    "response_time_ms": 145
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "INVALID_USER_ID",
    "message": "User ID must be a positive integer",
    "details": {
      "provided_value": -1,
      "valid_range": "1 to 999999999"
    }
  }
}
```

## Endpoints

### 1. Health Check

Check system status and health.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-08-22T10:30:00Z",
  "version": "1.0.0",
  "components": {
    "models": "loaded",
    "database": "connected",
    "cache": "active"
  }
}
```

### 2. Get Recommendations

Generate personalized recommendations for a user.

**Endpoint**: `POST /reco`

**Request Body**:
```json
{
  "user_id": 1001,
  "k": 10,
  "env": {
    "device": 1,
    "os": 17,
    "country": "DE"
  }
}
```

**Parameters**:
- `user_id` (required): Integer user ID (1-999999999)
- `k` (required): Number of recommendations (1-100)
- `env` (optional): Context override object
  - `device`: Device type (0=desktop, 1=mobile, 2=tablet)
  - `os`: Operating system ID (1-17)
  - `country`: Country code (ISO 3166-1 alpha-2)

**Response**:
```json
{
  "recommendations": [58793, 59156, 58020, 57771, 30605],
  "user_profile": {
    "stored": {"device": 1, "os": 17, "country": "DE"},
    "used": {"device": 1, "os": 17, "country": "DE"},
    "overrides_applied": false
  }
}
```

### 3. Get User Profile

Retrieve stored user profile information.

**Endpoint**: `GET /user/{user_id}/profile`

**Parameters**:
- `user_id`: Integer user ID

**Response**:
```json
{
  "user_id": 1001,
  "profile": {
    "device": 1,
    "os": 17,
    "country": "DE",
    "last_active": "2024-08-20T15:30:00Z",
    "interaction_count": 127
  }
}
```

## Parameter Reference

### Device Types
| Code | Description |
|------|-------------|
| 0    | Desktop     |
| 1    | Mobile      |
| 2    | Tablet      |

### Operating Systems
| Code | OS          | Code | OS        |
|------|-------------|------|-----------|
| 1    | Windows     | 11   | Android   |
| 2    | macOS       | 17   | iOS       |
| 3    | Linux       | ...  | Others    |

### Country Codes
Common country codes (ISO 3166-1 alpha-2):
- `US` - United States
- `DE` - Germany
- `FR` - France
- `GB` - United Kingdom
- `IT` - Italy
- `ES` - Spain
- `NL` - Netherlands

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_USER_ID` | 400 | User ID is invalid or out of range |
| `INVALID_K_VALUE` | 400 | k parameter is invalid |
| `INVALID_CONTEXT` | 400 | Context parameters are invalid |
| `USER_NOT_FOUND` | 404 | User profile not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

Current rate limits:
- **Free Tier**: 100 requests per minute
- **No authentication**: Global limit of 1000 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1692700800
```

## SDKs and Libraries

### Python SDK
```python
from recommender_client import RecommenderClient

client = RecommenderClient(
    base_url="https://ocp9funcapp-recsys.azurewebsites.net/api"
)

recommendations = client.get_recommendations(
    user_id=1001,
    k=10,
    context={"device": 1, "country": "US"}
)
```

### JavaScript SDK
```javascript
import RecommenderClient from 'recommender-js-client';

const client = new RecommenderClient({
  baseUrl: 'https://ocp9funcapp-recsys.azurewebsites.net/api'
});

const recommendations = await client.getRecommendations({
  userId: 1001,
  k: 10,
  context: { device: 1, country: 'US' }
});
```

## Testing

### Using curl
```bash
# Health check
curl -X GET "https://ocp9funcapp-recsys.azurewebsites.net/api/health"

# Get recommendations
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "k": 5}'

# With context override
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "k": 5, "env": {"device": 0, "country": "US"}}'
```

### Using Python requests
```python
import requests

# Get recommendations
response = requests.post(
    "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
    json={"user_id": 1001, "k": 10}
)

data = response.json()
print(f"Recommendations: {data['recommendations']}")
```

## API Versioning

The API follows semantic versioning:
- **Current Version**: v1.0
- **Version Header**: `API-Version: 1.0`
- **Deprecation**: 6-month notice for breaking changes

## Performance

### Response Times
- **P50**: < 100ms
- **P95**: < 500ms
- **P99**: < 1000ms

### Availability
- **SLA**: 99.9% uptime
- **Monitoring**: Real-time health checks
- **Status Page**: [status.recommender.example.com](https://status.recommender.example.com)

## Support

For API questions or issues:
- **Documentation**: This API reference
- **Examples**: See [examples.md](examples.md)
- **Issues**: Create GitHub issue with 'api' label
- **Support**: Contact support@recommender.example.com