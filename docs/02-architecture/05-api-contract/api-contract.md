[⬅️ Back to Index](../README.md)

# API Contract (OpenAPI 3.0)

*This document provides a formal, machine-readable definition of our API. It serves as the single source of truth for all endpoints, request/response schemas, and authentication methods. This allows for automated testing, client generation, and clear documentation.*

*We will use the OpenAPI 3.0 specification.*

```yaml
openapi: 3.0.0
info:
  title: BuildingOS API
  version: 2.0.0
  description: API for the BuildingOS platform, the operating brain for intelligent buildings.
  contact:
    name: BuildingOS Platform Team
    email: team@buildingos.com

servers:
  - url: https://{api_id}.execute-api.us-east-1.amazonaws.com
    variables:
      api_id:
        default: 'pj4vlvxrg7' # Current dev environment
        description: The deployed API Gateway ID.

# === SECURITY SCHEMES ===
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT token obtained from authentication endpoint.
        Token must be included in Authorization header as 'Bearer {token}'.
        Tokens expire after 24 hours and must be refreshed.
    
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key for service-to-service communication.
        Used for agent-to-agent communication and system integrations.
        Keys are rotated monthly and stored in AWS Secrets Manager.
    
    BuildingAuth:
      type: apiKey
      in: header
      name: X-Building-ID
      description: |
        Building identifier for multi-tenant isolation.
        Required for all endpoints to ensure proper data segregation.
        Must match the building ID associated with the user's JWT token.

  # === SECURITY REQUIREMENTS ===
  security:
    - BearerAuth: []
      BuildingAuth: []
    - ApiKeyAuth: []
      BuildingAuth: []

# === RATE LIMITING ===
x-rate-limit:
  description: |
    Rate limiting is applied per building and user:
    - 100 requests per minute per user
    - 1000 requests per minute per building
    - 10000 requests per hour per building
  headers:
    X-RateLimit-Limit: Maximum requests per window
    X-RateLimit-Remaining: Remaining requests in current window
    X-RateLimit-Reset: Time when the rate limit resets

# === AUDIT LOGGING ===
x-audit:
  description: |
    All API requests are logged for audit purposes:
    - User ID, Building ID, IP address, timestamp
    - Request method, path, query parameters
    - Response status code and processing time
    - Sensitive data is masked in logs
  retention: 7 years (compliance requirement)

paths:
  # === CORE PLATFORM ENDPOINTS ===
  /health:
    get:
      summary: Health Check
      description: Verifies the health of the platform.
      operationId: getHealth
      responses:
        '200':
          description: Service is operational.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
        '500':
          description: Service unavailable.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  # === CHAT ENDPOINTS (Multi-Agent Support) ===
  /chat:
    post:
      summary: Send Message via Chat
      description: |
        Main endpoint for users (residents, guests) to interact with the BuildingOS platform.
        Messages are intelligently routed to appropriate agents (persona, director, etc.) based on content and context.
        This design allows for future expansion to multiple agent types without API changes.
      operationId: sendChatMessage
      security:
        - BearerAuth: []
        - BuildingAuth: []
      x-rate-limit:
        user: 100/minute
        building: 1000/minute
      x-audit:
        level: "high"
        mask_fields: ["message_content", "user_personal_info"]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatMessage'
      responses:
        '200':
          description: Message processed successfully.
          headers:
            Access-Control-Allow-Origin:
              schema:
                type: string
                example: "*"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '400':
          description: Invalid request format.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /conversations/{user_id}:
    get:
      summary: Get User Conversation History
      description: |
        Returns the complete message history for a specific user across all agents and sessions.
        Supports multi-tenant architecture with proper user isolation.
      operationId: getUserConversations
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: string
          description: Unique user identifier for multi-tenant access
        - in: query
          name: session_id
          required: false
          schema:
            type: string
          description: Filter conversations by specific session ID
        - in: query
          name: agent_type
          required: false
          schema:
            type: string
            enum: [persona, director, coordinator, all]
            default: all
          description: Filter conversations by agent type
        - in: query
          name: limit
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 50
          description: Maximum number of messages to return
        - in: query
          name: offset
          required: false
          schema:
            type: integer
            minimum: 0
            default: 0
          description: Number of messages to skip for pagination
      responses:
        '200':
          description: User conversation history.
          headers:
            Access-Control-Allow-Origin:
              schema:
                type: string
                example: "*"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConversationHistory'
        '400':
          description: Invalid user ID or parameters.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: User not found or no conversations available.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  # === AGENT-SPECIFIC DEBUG ENDPOINTS ===
  # Note: These endpoints provide direct access to individual agents for debugging and monitoring
  
  /agents/persona:
    post:
      summary: Direct Persona Agent Access
      description: |
        **Debug endpoint**: Direct access to persona agent for testing and debugging.
        In production, messages should use /chat endpoint for intelligent routing.
      operationId: directPersonaMessage
      tags:
        - Debug
        - Agents
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatMessage'
      responses:
        '200':
          description: Message processed by persona agent.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PersonaResponse'
        '400':
          description: Invalid request format.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /agents/director:
    get:
      summary: Director Agent Status
      description: |
        **Debug endpoint**: Get current status and capabilities of the director agent.
      operationId: getDirectorStatus
      tags:
        - Debug
        - Agents
      responses:
        '200':
          description: Director agent status.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DirectorResponse'
        '500':
          description: Internal server error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /agents/elevator/call:
    post:
      summary: Direct Elevator Call
      description: |
        **Debug endpoint**: Direct elevator call for testing and debugging.
        In production, elevator calls should be made through /chat with natural language.
      operationId: directElevatorCall
      tags:
        - Debug
        - Agents
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ElevatorCallRequest'
      responses:
        '200':
          description: Elevator call initiated successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ElevatorResponse'
        '400':
          description: Invalid elevator request.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /agents/psim/search:
    post:
      summary: Direct PSIM Search
      description: |
        **Debug endpoint**: Direct search in PSIM system for debugging and monitoring.
        Note: This endpoint currently requires API Gateway handler implementation.
      operationId: directPsimSearch
      tags:
        - Debug
        - Agents
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PsimSearchRequest'
      responses:
        '200':
          description: Search results from PSIM.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PsimSearchResponse'
        '400':
          description: Invalid search parameters.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: PSIM service error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /agents/coordinator/missions/{mission_id}:
    get:
      summary: Get Mission Status
      description: |
        **Debug endpoint**: Get current status of a specific mission for debugging and monitoring.
        Note: This endpoint currently requires API Gateway handler implementation.
      operationId: getMissionStatus
      tags:
        - Debug
        - Agents
      parameters:
        - in: path
          name: mission_id
          required: true
          schema:
            type: string
          description: Unique mission identifier
      responses:
        '200':
          description: Mission status and details.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MissionResponse'
        '404':
          description: Mission not found.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  # === FUTURE PORTAL/DASHBOARD ENDPOINTS ===
  # Note: These endpoints are planned but not yet implemented
  /operator/reservations:
    get:
      summary: (Portal) List Reservations
      description: |
        **Future endpoint**: Returns a list of reservations for the logged-in operator.
        Status: Not implemented - requires portal implementation.
      operationId: listReservations
      tags:
        - Portal
        - Future
      security:
        - BearerAuth: []
      responses:
        '200':
          description: A list of reservation objects.
        '401':
          description: Unauthorized access.
        '501':
          description: Not implemented yet.

  /operator/reservations/{reservation_id}/approve:
    post:
      summary: (Portal) Approve Check-in
      description: |
        **Future endpoint**: Approves a guest's check-in after document verification.
        Status: Not implemented - requires portal implementation.
      operationId: approveCheckin
      tags:
        - Portal
        - Future
      security:
        - BearerAuth: []
      parameters:
        - in: path
          name: reservation_id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Check-in approved successfully.
        '401':
          description: Unauthorized access.
        '501':
          description: Not implemented yet.

  /team/maintenance_tasks:
    get:
      summary: (Panel) List Maintenance Tasks
      description: |
        **Future endpoint**: Returns the list of maintenance tickets for the building staff.
        Status: Not implemented - requires panel implementation.
      operationId: listMaintenanceTasks
      tags:
        - Panel
        - Future
      security:
        - BearerAuth: []
      responses:
        '200':
          description: A list of maintenance tasks.
        '401':
          description: Unauthorized access.
        '501':
          description: Not implemented yet.

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    # === CORE SCHEMAS ===
    ErrorResponse:
      type: object
      properties:
        error:
          type: string
          description: Error message description
        code:
          type: string
          description: Error code for programmatic handling
        timestamp:
          type: string
          format: date-time
          description: When the error occurred
      required:
        - error

    HealthResponse:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        timestamp:
          type: string
          format: date-time
        version:
          type: string
        services:
          type: object
          properties:
            database:
              type: string
              enum: [up, down]
            sns:
              type: string
              enum: [up, down]
            lambda:
              type: string
              enum: [up, down]

    # === CHAT SCHEMAS (Multi-Agent) ===
    ChatMessage:
      type: object
      properties:
        user_id:
          type: string
          description: "Unique user identifier for multi-tenant support."
          example: "tenant1_user123"
        session_id:
          type: string
          description: "Current chat session ID (optional)."
          example: "session-456"
        message:
          type: string
          description: "The user's message content."
          example: "Hello, I need help with my reservation"
        context:
          type: object
          description: "Optional context information for better agent routing"
          properties:
            location:
              type: string
              example: "lobby"
            intent:
              type: string
              example: "elevator_call"
            priority:
              type: string
              enum: [low, normal, high, urgent]
              default: normal
      required:
        - user_id
        - message

    ChatResponse:
      type: object
      properties:
        response:
          type: string
          description: "Agent's response message"
        session_id:
          type: string
          description: "Session ID for conversation continuity"
        user_id:
          type: string
          description: "User identifier"
        agent_used:
          type: string
          description: "Which agent processed the message"
          enum: [persona, director, coordinator, elevator, psim]
        timestamp:
          type: string
          format: date-time
        status:
          type: string
          enum: [success, processing, error]
        actions_taken:
          type: array
          description: "List of actions performed (e.g., elevator called, reservation checked)"
          items:
            type: object
            properties:
              action:
                type: string
              result:
                type: string
              timestamp:
                type: string
                format: date-time

    ConversationEntry:
      type: object
      properties:
        role:
          type: string
          enum: [user, assistant]
        content:
          type: string
        timestamp:
          type: string
          format: date-time
        session_id:
          type: string
        agent_type:
          type: string
          enum: [persona, director, coordinator, elevator, psim]
          description: "Which agent was involved in this message"
        metadata:
          type: object
          description: "Additional context and metadata"
          properties:
            intent:
              type: string
            actions:
              type: array
              items:
                type: string

    ConversationHistory:
      type: object
      properties:
        user_id:
          type: string
        conversations:
          type: array
          items:
            $ref: '#/components/schemas/ConversationEntry'
        total_messages:
          type: integer
        sessions:
          type: array
          items:
            type: object
            properties:
              session_id:
                type: string
              created_at:
                type: string
                format: date-time
              message_count:
                type: integer
              agents_involved:
                type: array
                items:
                  type: string
        pagination:
          type: object
          properties:
            current_page:
              type: integer
            total_pages:
              type: integer
            has_next:
              type: boolean
            has_previous:
              type: boolean

    # === AGENT-SPECIFIC SCHEMAS (Debug Endpoints) ===
    PersonaResponse:
      type: object
      properties:
        response:
          type: string
          description: "Agent's response message"
        session_id:
          type: string
          description: "Session ID for conversation continuity"
        user_id:
          type: string
          description: "User identifier"
        timestamp:
          type: string
          format: date-time
        status:
          type: string
          enum: [success, processing, error]
    DirectorResponse:
      type: object
      properties:
        status:
          type: string
          enum: [active, idle, processing]
        active_missions:
          type: integer
        capabilities:
          type: array
          items:
            type: string
        last_activity:
          type: string
          format: date-time

    # === ELEVATOR AGENT SCHEMAS ===
    ElevatorCallRequest:
      type: object
      properties:
        floor:
          type: integer
          minimum: 1
          maximum: 50
          description: "Target floor number"
        user_id:
          type: string
          description: "User requesting the elevator"
        priority:
          type: string
          enum: [normal, high, emergency]
          default: normal
      required:
        - floor

    ElevatorResponse:
      type: object
      properties:
        call_id:
          type: string
          description: "Unique call identifier"
        status:
          type: string
          enum: [requested, dispatched, arrived, completed, failed]
        estimated_arrival:
          type: integer
          description: "Estimated arrival time in seconds"
        elevator_id:
          type: string
          description: "ID of assigned elevator"

    # === PSIM AGENT SCHEMAS ===
    PsimSearchRequest:
      type: object
      properties:
        query:
          type: string
          description: "Search query for person information"
          example: "John Doe"
        search_type:
          type: string
          enum: [name, document, phone, email]
          default: name
        mission_id:
          type: string
          description: "Associated mission ID (required for SNS mode)"
        task_id:
          type: string
          description: "Associated task ID (required for SNS mode)"
      required:
        - query

    PsimSearchResponse:
      type: object
      properties:
        results:
          type: array
          items:
            type: object
            properties:
              person_id:
                type: string
              name:
                type: string
              documents:
                type: array
                items:
                  type: string
              status:
                type: string
        total_results:
          type: integer
        search_query:
          type: string

    # === COORDINATOR AGENT SCHEMAS ===
    MissionResponse:
      type: object
      properties:
        mission_id:
          type: string
        status:
          type: string
          enum: [pending, in_progress, completed, failed]
        tasks:
          type: array
          items:
            type: object
            properties:
              task_id:
                type: string
              agent:
                type: string
              status:
                type: string
              result:
                type: object
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
```

---

## **Implementation Status & Guidelines**

### **Current Implementation Status**

| Endpoint | Status | Notes |
|----------|--------|--------|
| **Core Platform Endpoints** |
| `GET /health` | ✅ **Implemented** | Health check endpoint |
| `POST /chat` | ❌ **Not Implemented** | **Needs implementation with intelligent agent routing** |
| `GET /conversations/{user_id}` | ❌ **Not Implemented** | **Needs implementation for multi-tenant support** |
| **Debug Endpoints (Agent-Specific)** |
| `POST /agents/persona` | ✅ **Implemented** | Currently mapped as `/persona` |
| `GET /agents/director` | ✅ **Implemented** | Currently mapped as `/director` |
| `POST /agents/elevator/call` | ✅ **Implemented** | Currently mapped as `/elevator/call` |
| `POST /agents/psim/search` | ⚠️ **Partial** | Currently mapped as `/psim/search` - **Needs API Gateway handler** |
| `GET /agents/coordinator/missions/{id}` | ⚠️ **Partial** | Currently mapped as `/coordinator/missions/{id}` - **Needs API Gateway handler** |
| **Future Endpoints** |
| Portal endpoints | ❌ **Not Implemented** | Future implementation |
| Panel endpoints | ❌ **Not Implemented** | Future implementation |

### **Migration Plan**

#### **Current → Target URL Mapping**
| Current Implementation | Target API Design | Migration Notes |
|----------------------|------------------|-----------------|
| `POST /persona` | `POST /chat` | Implement intelligent routing |
| `GET /persona/conversations` | `GET /conversations/{user_id}` | Add multi-tenant support |
| `GET /director` | `GET /agents/director` | Move to debug namespace |
| `POST /elevator/call` | `POST /agents/elevator/call` | Move to debug namespace |
| `POST /psim/search` | `POST /agents/psim/search` | Fix + move to debug namespace |
| `GET /coordinator/missions/{id}` | `GET /agents/coordinator/missions/{id}` | Fix + move to debug namespace |

#### **Implementation Priority**

1. **Phase 0** (Current): Complete PSIM and Coordinator API Gateway handlers
2. **Phase 1**: Implement `/chat` endpoint with intelligent agent routing
3. **Phase 2**: Implement `/conversations/{user_id}` with multi-tenant support
4. **Phase 3**: Migrate existing endpoints to `/agents/*` namespace (maintain backwards compatibility)
5. **Phase 4**: Implement portal/panel endpoints with JWT authentication

### **API Gateway Configuration**

- **Base URL**: `https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com`
- **Environment**: Development (`dev`)
- **CORS**: Enabled for frontend integration
- **Authentication**: None (planned JWT for portal/panel)

### **Agent Architecture Types**

1. **Direct API**: Health check only
2. **Hybrid (SNS + API)**: Persona, Director, Elevator
   - Primary: SNS for event-driven communication
   - Secondary: API Gateway for debugging and direct access
3. **SNS Only**: PSIM, Coordinator
   - **Action Required**: Implement API Gateway handlers for debug access

### **Best Practices & Guidelines**

#### **Request/Response Standards**
- All requests must include `Content-Type: application/json`
- All responses include CORS headers for frontend compatibility
- Error responses follow consistent schema with `error` field
- Timestamps use ISO 8601 format

#### **Error Handling**
```json
{
  "error": "Description of the error",
  "code": "ERROR_CODE", 
  "timestamp": "2025-08-07T10:30:00Z"
}
```

#### **Development Workflow**
1. Update this API contract first when adding new endpoints
2. Implement backend changes with proper error handling
3. Test via CLI before frontend integration
4. Update CLI reference documentation

#### **Testing Commands**
```bash
# Health Check
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health"

# Chat Endpoint (Future - with intelligent routing)
curl -X POST "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "tenant1_user123", "message": "Call elevator to floor 5"}'

# Conversations (Future - multi-tenant)
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/conversations/tenant1_user123"

# Debug Endpoints (Current Implementation)
# Direct Persona Agent
curl -X POST "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/persona" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "message": "Hello"}'

# Direct Director Agent
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/director"

# Direct Elevator Agent
curl -X POST "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/elevator/call" \
  -H "Content-Type: application/json" \
  -d '{"floor": 5, "user_id": "test-user"}'
```

### **Next Steps**

1. **Immediate Priority**: Complete PSIM and Coordinator API Gateway handlers for debug endpoints
2. **Phase 1**: Implement `/chat` endpoint with intelligent agent routing logic
3. **Phase 2**: Implement `/conversations/{user_id}` with proper multi-tenant isolation
4. **Phase 3**: Create URL migration strategy (maintain backwards compatibility)
5. **Phase 4**: Implement JWT authentication for portal/panel endpoints
6. **Phase 5**: Build portal and panel frontend implementations

### **Architecture Benefits**

- **`/chat`**: Generic endpoint allows routing to any agent without API changes
- **`/conversations/{user_id}`**: RESTful design with proper multi-tenant support
- **`/agents/*`**: Clear namespace for debugging and direct agent access
- **Multi-tenant**: User IDs can include tenant prefixes (e.g., `tenant1_user123`)
- **Future-proof**: Easy to add new agents without breaking existing integrations

---

**Last Updated**: August 7, 2025  
**API Version**: 2.0.0  
**Environment**: Development
```
