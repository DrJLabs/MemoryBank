#!/usr/bin/env python3
"""
Generate API Documentation for Custom GPT Adapter Service

This script generates OpenAPI documentation and creates HTML documentation.
"""

import os
import sys
import json
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.main import app


def generate_openapi_spec(output_path: str):
    """Generate OpenAPI specification file"""
    openapi_schema = app.openapi()

    # Enhance the schema with additional information
    openapi_schema["info"]["title"] = "Custom GPT Adapter Service API"
    openapi_schema["info"]["description"] = """
# Custom GPT Adapter Service API

This API provides integration between ChatGPT Custom GPTs and the Memory Bank Service.

## Authentication

All endpoints (except `/health` and `/auth/token`) require OAuth 2.0 authentication using Bearer tokens.

To authenticate:
1. Obtain your `client_id` and `client_secret` from the administrator
2. Request an access token from `/auth/token`
3. Include the token in the `Authorization` header: `Bearer <token>`

## Rate Limiting

API requests are rate-limited per application. Default limits:
- 100 requests per minute for standard endpoints
- Rate limits are configurable per application

## Error Responses

All endpoints return consistent error responses:
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

## Async Processing

Memory creation operations are processed asynchronously. You'll receive a `202 Accepted` response with a request ID for tracking.
"""

    openapi_schema["info"]["version"] = "1.0.0"
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "support@example.com"
    }

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "clientCredentials": {
                    "tokenUrl": "/auth/token",
                    "scopes": {
                        "read": "Read access to memories",
                        "write": "Write access to create memories"
                    }
                }
            }
        }
    }

    # Add example requests/responses
    if "paths" in openapi_schema:
        # Enhance /auth/token endpoint
        if "/auth/token" in openapi_schema["paths"]:
            openapi_schema["paths"]["/auth/token"]["post"]["requestBody"] = {
                "content": {
                    "application/x-www-form-urlencoded": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "grant_type": {
                                    "type": "string",
                                    "example": "client_credentials"
                                },
                                "client_id": {
                                    "type": "string",
                                    "example": "cgpt_xxx"
                                },
                                "client_secret": {
                                    "type": "string",
                                    "example": "your-secret"
                                }
                            },
                            "required": ["grant_type", "client_id", "client_secret"]
                        }
                    }
                }
            }

        # Enhance search endpoint
        if "/api/v1/search" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/v1/search"]["post"]["security"] = [{"OAuth2": ["read"]}]

        # Enhance memories endpoint
        if "/api/v1/memories" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/v1/memories"]["post"]["security"] = [{"OAuth2": ["write"]}]

    # Save the schema
    with open(output_path, 'w') as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"OpenAPI specification saved to: {output_path}")
    return openapi_schema


def generate_html_docs(openapi_spec, output_dir: str):
    """Generate HTML documentation using ReDoc"""

    os.makedirs(output_dir, exist_ok=True)

    # Create ReDoc HTML
    redoc_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Custom GPT Adapter Service API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url='openapi.json'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>
"""

    # Save HTML
    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, 'w') as f:
        f.write(redoc_html)

    # Copy OpenAPI spec to docs directory
    spec_path = os.path.join(output_dir, "openapi.json")
    with open(spec_path, 'w') as f:
        json.dump(openapi_spec, f, indent=2)

    print(f"HTML documentation saved to: {html_path}")

    # Create a simple Python HTTP server script for local viewing
    server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving API documentation at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()
"""

    server_path = os.path.join(output_dir, "serve.py")
    with open(server_path, 'w') as f:
        f.write(server_script)
    os.chmod(server_path, 0o755)

    print(f"\nTo view the documentation locally, run:")
    print(f"  python {server_path}")


def generate_postman_collection(openapi_spec, output_path: str):
    """Generate Postman collection from OpenAPI spec"""

    collection = {
        "info": {
            "name": "Custom GPT Adapter Service",
            "description": openapi_spec["info"]["description"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "oauth2",
            "oauth2": [
                {
                    "key": "tokenUrl",
                    "value": "{{base_url}}/auth/token",
                    "type": "string"
                },
                {
                    "key": "clientId",
                    "value": "{{client_id}}",
                    "type": "string"
                },
                {
                    "key": "clientSecret",
                    "value": "{{client_secret}}",
                    "type": "string"
                },
                {
                    "key": "grant_type",
                    "value": "client_credentials",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "client_id",
                "value": "your-client-id",
                "type": "string"
            },
            {
                "key": "client_secret",
                "value": "your-client-secret",
                "type": "string"
            }
        ],
        "item": []
    }

    # Convert OpenAPI paths to Postman requests
    for path, methods in openapi_spec.get("paths", {}).items():
        folder = {
            "name": path,
            "item": []
        }

        for method, spec in methods.items():
            request = {
                "name": spec.get("summary", f"{method.upper()} {path}"),
                "request": {
                    "method": method.upper(),
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}" + path,
                        "host": ["{{base_url}}"],
                        "path": path.strip("/").split("/")
                    }
                }
            }

            # Add description
            if "description" in spec:
                request["request"]["description"] = spec["description"]

            # Add auth header for protected endpoints
            if path not in ["/health", "/auth/token", "/"]:
                request["request"]["header"].append({
                    "key": "Authorization",
                    "value": "Bearer {{access_token}}",
                    "type": "text"
                })

            # Add request body if present
            if "requestBody" in spec:
                content = spec["requestBody"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    example = {}

                    # Generate example from schema
                    if "properties" in schema:
                        for prop, prop_spec in schema["properties"].items():
                            if "example" in prop_spec:
                                example[prop] = prop_spec["example"]
                            elif prop_spec.get("type") == "string":
                                example[prop] = f"sample-{prop}"
                            elif prop_spec.get("type") == "integer":
                                example[prop] = 1
                            elif prop_spec.get("type") == "array":
                                example[prop] = []

                    request["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(example, indent=2),
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }

            folder["item"].append(request)

        if folder["item"]:
            collection["item"].append(folder)

    # Save collection
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)

    print(f"Postman collection saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate API Documentation")
    parser.add_argument("--output-dir", default="docs/api",
                       help="Output directory for documentation (default: docs/api)")
    parser.add_argument("--format", choices=["all", "openapi", "html", "postman"],
                       default="all", help="Documentation format to generate")

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate OpenAPI spec
    openapi_path = os.path.join(args.output_dir, "openapi.json")
    openapi_spec = generate_openapi_spec(openapi_path)

    if args.format in ["all", "html"]:
        # Generate HTML documentation
        generate_html_docs(openapi_spec, args.output_dir)

    if args.format in ["all", "postman"]:
        # Generate Postman collection
        postman_path = os.path.join(args.output_dir, "custom-gpt-adapter.postman_collection.json")
        generate_postman_collection(openapi_spec, postman_path)

    print(f"\nDocumentation generation complete!")
    print(f"Files are located in: {args.output_dir}")


if __name__ == "__main__":
    main()