# Custom GPT Adapter API Endpoints

This document provides details on the available API endpoints for the Custom GPT Adapter service.

## Authentication

### POST /auth/token

This endpoint is used to obtain an OAuth 2.0 access token.

-   **Request Body:**
    -   `grant_type`: Must be `client_credentials`.
    -   `client_id`: Your application's client ID.
    -   `client_secret`: Your application's client secret.
    -   `scope`: (Optional) A space-delimited list of requested scopes.
-   **Responses:**
    -   `200 OK`: Returns an access token and a refresh token.
    -   `401 Unauthorized`: If the `client_id` or `client_secret` are incorrect.

### POST /auth/refresh

This endpoint is used to obtain a new access token using a refresh token.

-   **Request Body:**
    -   `grant_type`: Must be `refresh_token`.
    -   `refresh_token`: The refresh token you received from the `/auth/token` endpoint.
-   **Responses:**
    -   `200 OK`: Returns a new access token.
    -   `401 Unauthorized`: If the refresh token is invalid or expired.

## Users

### GET /users/me

- **Purpose**: Get details about the currently authenticated application.
- **Headers**:
  - `Authorization`: `Bearer <access_token>`
- **Response**:
  ```json
  {
    "name": "string",
    "id": "string (uuid)",
    "client_id": "string"
  }
  ```

## Memories

### POST /search

- **Purpose**: Search for memories in the Memory Bank Service.
- **Headers**:
  - `Authorization`: `Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "query": "string",
    "limit": "integer (optional, default: 10)"
  }
  ```
- **Response**: The response from the Memory Bank Service search endpoint is returned directly.

### POST /memories

- **Purpose**: Create a new memory in the Memory Bank Service.
- **Headers**:
  - `Authorization`: `Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "content": "string",
    "context": "object (optional)"
  }
  ```
- **Response (202 Accepted)**:
    ```json
    {
        "message": "Memory creation request received. It will be processed asynchronously.",
        "request_id": "string (uuid)"
    }
    ``` 