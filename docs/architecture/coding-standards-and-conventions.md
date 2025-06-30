# Coding Standards and Conventions

*The adapter service follows standard FastAPI microservice patterns, independent from your existing Memory Bank Service coding standards.*

## Existing Standards Compliance

**Code Style:** Existing Memory Bank Service patterns not modified
**Linting Rules:** Existing core service linting unchanged
**Testing Patterns:** Existing core service test patterns unchanged
**Documentation Style:** Existing core service documentation unchanged

## Enhancement-Specific Standards

- **FastAPI Standards:** Standard FastAPI application structure with async/await patterns
- **OAuth Implementation:** Industry-standard OAuth 2.0 with JWT token management
- **Error Handling:** Comprehensive error handling with circuit breaker patterns
- **Logging:** Structured logging with correlation IDs for request tracing
- **API Documentation:** Complete OpenAPI documentation with examples

## Critical Integration Rules

- **Existing API Compatibility:** Adapter service consumes existing APIs as external client only
- **Database Integration:** Independent database with zero schema changes to core service
- **Error Handling:** Independent error handling, does not modify core service error patterns
- **Logging Consistency:** Independent logging system with correlation to core service requests
