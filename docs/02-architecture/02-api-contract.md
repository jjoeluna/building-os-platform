[⬅️ Back to Index](../README.md)

# API Contract (OpenAPI 3.0)

*This document provides a formal, machine-readable definition of our API. It serves as the single source of truth for all endpoints, request/response schemas, and authentication methods. This allows for automated testing, client generation, and clear documentation.*

*We will use the OpenAPI 3.0 specification.*

```yaml
openapi: 3.0.0
info:
  title: BuildingOS API
  version: 1.0.0
  description: The official API for the BuildingOS platform.

servers:
  - url: https://{api_id}.execute-api.us-east-1.amazonaws.com
    variables:
      api_id:
        default: 'replace-with-dev-api-id'
        description: The ID of the deployed API Gateway.

paths:
  /health:
    get:
      summary: Health Check
      description: A simple endpoint to verify that the service is running.
      responses:
        '200':
          description: Service is healthy.
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "OK"

  /persona:
    post:
      summary: Interact with the Persona Agent
      description: Sends a user message to start or continue a conversation.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
                  description: A unique identifier for the user.
                  example: "user-12345"
                message:
                  type: string
                  description: The message from the user.
                  example: "I need to book a flight to New York."
      responses:
        '202':
          description: The request has been accepted for processing.
          content:
            application/json:
              schema:
                type: object
                properties:
                  session_id:
                    type: string
                    description: A unique ID for this conversation session.
                    example: "session-abcde-12345"
                  message:
                    type: string
                    example: "Request received. The Director is analyzing the intention."

# Add other paths and component schemas as needed...
```
