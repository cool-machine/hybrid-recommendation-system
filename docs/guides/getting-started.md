# Getting Started

Quick start guide to using the recommendation system.

## Overview

The recommendation system provides personalized content recommendations using a multi-algorithm ensemble approach. It supports both cold-start users (new users) and warm users (with interaction history).

## Quick Start

### 1. Make Your First Request

The simplest way to get recommendations:

```bash
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "k": 5}'
```

**Response:**
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

### 2. Understanding the Response

- **`recommendations`**: List of recommended item IDs
- **`user_profile.stored`**: User's profile from our database
- **`user_profile.used`**: Profile actually used for recommendations
- **`overrides_applied`**: Whether manual context was applied

### 3. Try Different Contexts

Override the user's context to see how recommendations change:

```bash
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001, 
    "k": 5,
    "env": {
      "device": 0,
      "os": 1,
      "country": "US"
    }
  }'
```

This simulates the user accessing from a Windows desktop in the US instead of their usual mobile device in Germany.

## Understanding User Types

### Cold Users
New users with no interaction history receive **context-aware popularity** recommendations:

```bash
# Test with a new user ID
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 99999, "k": 5}'
```

Cold users get different recommendations based on:
- **Device type** (desktop vs mobile vs tablet)
- **Operating system** (Windows, iOS, Android, etc.)
- **Geographic region** (country-specific popularity)

### Warm Users
Existing users with interaction history receive **personalized ML** recommendations:

```bash
# Test with an existing user
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "k": 5}'
```

Warm users get personalized recommendations from:
- **Collaborative Filtering**: Users with similar tastes
- **Matrix Factorization**: Latent preference modeling
- **Neural Networks**: Deep learning embeddings
- **Smart Reranking**: ML-based final scoring

## Common Use Cases

### 1. Website Homepage
Show personalized content on your homepage:

```python
import requests

def get_homepage_recommendations(user_id):
    response = requests.post(
        "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
        json={"user_id": user_id, "k": 10}
    )
    return response.json()["recommendations"]

# Usage
recommendations = get_homepage_recommendations(user_id=1001)
```

### 2. Mobile App Recommendations
Get mobile-optimized recommendations:

```python
def get_mobile_recommendations(user_id):
    response = requests.post(
        "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
        json={
            "user_id": user_id, 
            "k": 8,
            "env": {"device": 1}  # Force mobile context
        }
    )
    return response.json()["recommendations"]
```

### 3. A/B Testing Different Contexts
Test how context affects recommendations:

```python
def compare_contexts(user_id):
    # Default context
    default = requests.post(
        "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
        json={"user_id": user_id, "k": 5}
    ).json()
    
    # US desktop context
    us_desktop = requests.post(
        "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
        json={
            "user_id": user_id, 
            "k": 5,
            "env": {"device": 0, "country": "US"}
        }
    ).json()
    
    return {
        "default": default["recommendations"],
        "us_desktop": us_desktop["recommendations"]
    }
```

### 4. Real-time Personalization
Update recommendations based on current session:

```javascript
// JavaScript example for web applications
async function getContextualRecommendations(userId) {
    // Detect user's current context
    const context = {
        device: /Mobile/.test(navigator.userAgent) ? 1 : 0,
        country: await getUserCountry() // Your geolocation function
    };
    
    const response = await fetch(
        'https://ocp9funcapp-recsys.azurewebsites.net/api/reco',
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                k: 12,
                env: context
            })
        }
    );
    
    return await response.json();
}
```

## Parameters Reference

### Required Parameters
- **`user_id`**: Integer (1 to 999999999)
- **`k`**: Integer (1 to 100) - number of recommendations

### Optional Context Override (`env`)
- **`device`**: 0=desktop, 1=mobile, 2=tablet
- **`os`**: Operating system ID (1-17)
- **`country`**: ISO country code (US, DE, FR, etc.)

### Common Device/OS Combinations
```json
{
  "desktop_windows": {"device": 0, "os": 1},
  "mobile_ios": {"device": 1, "os": 17},
  "mobile_android": {"device": 1, "os": 11},
  "tablet_ipad": {"device": 2, "os": 17}
}
```

## Best Practices

### 1. Caching
Cache recommendations for better performance:

```python
import time
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_recommendations(user_id, k, cache_key):
    # cache_key includes timestamp for TTL
    response = requests.post(
        "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
        json={"user_id": user_id, "k": k}
    )
    return response.json()["recommendations"]

# Usage with 5-minute cache
cache_key = int(time.time() // 300)  # 5-minute buckets
recommendations = get_cached_recommendations(1001, 10, cache_key)
```

### 2. Error Handling
Always handle errors gracefully:

```python
def safe_get_recommendations(user_id, k=10, fallback=None):
    try:
        response = requests.post(
            "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
            json={"user_id": user_id, "k": k},
            timeout=5  # 5-second timeout
        )
        response.raise_for_status()
        return response.json()["recommendations"]
    except requests.RequestException:
        # Return fallback recommendations
        return fallback or [10001, 10002, 10003, 10004, 10005]
```

### 3. Batch Processing
For multiple users, make separate requests (no batch endpoint yet):

```python
import asyncio
import aiohttp

async def get_recommendations_batch(user_ids, k=5):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_id in user_ids:
            task = session.post(
                "https://ocp9funcapp-recsys.azurewebsites.net/api/reco",
                json={"user_id": user_id, "k": k}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [await resp.json() for resp in responses]

# Usage
user_ids = [1001, 1002, 1003]
results = asyncio.run(get_recommendations_batch(user_ids))
```

## Testing Your Integration

### 1. Health Check
Verify the service is working:

```bash
curl -X GET "https://ocp9funcapp-recsys.azurewebsites.net/api/health"
```

### 2. Known User Test
Test with a user that has a profile:

```bash
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "k": 3}'
```

### 3. Cold User Test
Test with a new user:

```bash
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 999999, "k": 3}'
```

### 4. Context Override Test
Test context sensitivity:

```bash
curl -X POST "https://ocp9funcapp-recsys.azurewebsites.net/api/reco" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001, 
    "k": 3,
    "env": {"device": 1, "country": "FR"}
  }'
```

## Next Steps

Once you're comfortable with basic usage:

1. **[API Documentation](../api/README.md)** - Complete API reference
2. **[Architecture Guide](../architecture/README.md)** - Understanding the system
3. **[Developer Guide](developer-guide.md)** - Setting up development environment
4. **[Examples](../api/examples.md)** - More detailed usage examples

## Common Issues

### Slow First Request
The first request may take 5-10 seconds due to cold start. Subsequent requests are much faster (< 500ms).

### Context Not Affecting Results
For warm users (existing users), context changes don't affect recommendations because the system uses personalized ML models. Context only affects cold users (new users).

### Large k Values
Requesting more than 50 recommendations may increase response time. Consider caching for large result sets.

## Getting Help

- **API Issues**: Check [troubleshooting guide](troubleshooting.md)
- **Integration Questions**: See [examples](../api/examples.md)
- **Bug Reports**: Create GitHub issue
- **Feature Requests**: Use GitHub Discussions