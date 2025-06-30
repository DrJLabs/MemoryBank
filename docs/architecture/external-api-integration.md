# External API Integration

## OpenAI Custom GPT API

- **Purpose:** Receive webhook callbacks and provide Custom GPT integration
- **Documentation:** OpenAI Custom GPT documentation
- **Base URL:** Configured per Custom GPT instance
- **Authentication:** OAuth 2.0 Bearer tokens
- **Integration Method:** Standard webhook and REST API patterns

**Key Endpoints Used:**

- `POST /api/v1/search` - Custom GPT memory search requests
- `POST /api/v1/memories` - Custom GPT memory creation requests

**Error Handling:** Circuit breaker pattern with exponential backoff and graceful degradation

## Memory Bank Service API

- **Purpose:** Consume existing Memory Bank Service functionality
- **Documentation:** Existing OpenAPI specification
- **Base URL:** Configured environment variable
- **Authentication:** Existing API authentication (as external client)
- **Integration Method:** Standard REST API client with retry logic

**Key Endpoints Used:**

- `POST /v1/memories/search/` - Forward Custom GPT search requests
- `POST /v1/memories/` - Forward Custom GPT memory creation requests

**Error Handling:** Circuit breaker, retry with exponential backoff, comprehensive error logging
