> **Deprecated:** This document has been consolidated into ../brownfield-architecture.md. Please refer to that file for the latest information.

# Data Models and Schema Changes

*No changes to existing Memory Bank Service database schema. All new data models are in the independent adapter service database.*

## New Data Models

## CustomGPTApplication

**Purpose:** Manage Custom GPT application credentials and permissions
**Integration:** Independent - no relationship with existing Memory Bank Service models

**Key Attributes:**

- id: UUID - Primary key for Custom GPT application
- name: String - Human-readable Custom GPT application name
- client_id: String - OAuth 2.0 client identifier
- client_secret: String - Encrypted OAuth 2.0 client secret
- permissions: JSON - Granular permissions for memory operations
- rate_limits: JSON - Per-application rate limiting configuration
- created_at: DateTime - Application registration timestamp
- last_used: DateTime - Last successful authentication

**Relationships:**

- **With Existing:** None - completely independent
- **With New:** One-to-many with CustomGPTSession, CustomGPTAuditLog

## CustomGPTSession

**Purpose:** Track active Custom GPT authentication sessions
**Integration:** Independent session management separate from core service

**Key Attributes:**

- id: UUID - Primary key for session
- application_id: UUID - Foreign key to CustomGPTApplication
- access_token: String - JWT access token
- refresh_token: String - JWT refresh token
- expires_at: DateTime - Token expiration timestamp
- last_activity: DateTime - Last API request timestamp

**Relationships:**

- **With Existing:** None - independent session tracking
- **With New:** Many-to-one with CustomGPTApplication

## CustomGPTAuditLog

**Purpose:** Comprehensive audit trail for Custom GPT operations
**Integration:** Independent audit system separate from core service logs

**Key Attributes:**

- id: UUID - Primary key for audit entry
- application_id: UUID - Foreign key to CustomGPTApplication
- operation_type: Enum - Type of operation (search, create, authenticate)
- request_data: JSON - Sanitized request payload
- response_status: Integer - HTTP response status code
- processing_time: Float - Request processing time in seconds
- memory_service_request_id: String - Correlation with Memory Bank Service requests
- created_at: DateTime - Audit entry timestamp

**Relationships:**

- **With Existing:** None - independent audit trail
- **With New:** Many-to-one with CustomGPTApplication

## Schema Integration Strategy

**Database Changes Required:**

- **New Tables:** CustomGPTApplication, CustomGPTSession, CustomGPTAuditLog, CustomGPTRateLimit
- **Modified Tables:** None - zero changes to existing Memory Bank Service schema
- **New Indexes:** Optimized indexes for OAuth lookups and audit queries
- **Migration Strategy:** Independent database deployment with separate migration scripts

**Backward Compatibility:**

- Core Memory Bank Service database schema remains completely unchanged
- Adapter service database is independent and removable without impact
