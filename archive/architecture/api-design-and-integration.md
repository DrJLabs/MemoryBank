# API Design and Integration

*The new API endpoints follow standard FastAPI patterns while being completely independent from your existing Memory Bank Service API structure. The adapter service consumes your existing APIs as a standard external client.*

## New API Endpoints

**API Integration Strategy:** Independent FastAPI application with separate OpenAPI documentation
**Authentication:** OAuth 2.0 with JWT tokens, completely separate from core service authentication
**Versioning:** Independent versioning (/api/v1/) with no relationship to core service versioning

### Custom GPT Memory Search

- **Method:** POST
- **Endpoint:** `/api/v1/search`
- **Purpose:** Search memories for Custom GPT applications
- **Integration:** Proxies to Memory Bank Service search API with Custom GPT context

**Request:**

```json
{
  "query": "natural language search query",
  "limit": 10,
  "filters": {
    "categories": ["TECHNICAL", "PROJECT"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    }
  },
  "context": {
    "custom_gpt_id": "gpt-custom-123",
    "conversation_id": "conv-456"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "request_id": "req-789",
  "results": [
    {
      "memory_id": "mem-001",
      "content": "Memory content text",
      "relevance_score": 0.95,
      "metadata": {
        "category": "TECHNICAL",
        "created_at": "2024-01-15T10:30:00Z"
      }
    }
  ],
  "total_found": 1,
  "processing_time_ms": 150
}
```

### Custom GPT Memory Creation

- **Method:** POST
- **Endpoint:** `/api/v1/memories`
- **Purpose:** Create new memories from Custom GPT conversations
- **Integration:** Asynchronously forwards to Memory Bank Service creation API

**Request:**

```json
{
  "content": "Memory content to store",
  "metadata": {
    "source": "custom_gpt",
    "custom_gpt_id": "gpt-custom-123",
    "conversation_id": "conv-456",
    "user_context": "Additional context"
  },
  "categories": ["PROJECT", "AI_INTEGRATION"],
  "priority": "normal"
}
```

**Response:**

```json
{
  "status": "accepted",
  "request_id": "req-890",
  "message": "Memory creation queued for processing",
  "estimated_processing_time": "2-5 seconds"
}
```

### OAuth Token Management

- **Method:** POST
- **Endpoint:** `/auth/token`
- **Purpose:** Generate OAuth 2.0 access tokens for Custom GPT applications
- **Integration:** Independent OAuth server, no integration with core service auth

**Request:**

```json
{
  "grant_type": "client_credentials",
  "client_id": "custom_gpt_app_123",
  "client_secret": "encrypted_secret",
  "scope": "memory:read memory:write"
}
```

**Response:**

```json
{
  "access_token": "jwt_token_here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here",
  "scope": "memory:read memory:write"
}
```
