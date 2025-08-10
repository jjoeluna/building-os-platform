---
status: "In Development"
category: "Integration"
last_updated: "2025-08-04"
owner: ""
dependencies:
  - "External: Seventh Situator API (e.g., psim.clevertown.io)"
source_code: "src/tools/tool_psim/"
---

# Tool: PSIM (Seventh Situator)

## 1. Purpose

This tool is a Lambda function responsible for integrating with external Seventh Situator PSIM (Physical Security Information Management) systems. It provides a standardized interface for the BuildingOS platform to perform actions such as generating remote events (e.g., alarms, access control events) and managing user data.

## 2. API Integration Details

- **Provider:** Seventh
- **Endpoint Base:** Varies per customer installation (e.g., `http://psim.clevertown.io:9091/`). This must be configured per tenant.
- **Authentication:** Session-based, using a `Seventh.Auth` cookie.
    1.  A `PUT` request is made to `/api/login` with a username and password.
    2.  A successful response includes the `Seventh.Auth` session cookie.
    3.  All subsequent requests must include this cookie.
    4.  The session is terminated by calling `GET /api/logoff`.

### Key Endpoints

- `PUT /api/login`: Authenticates and retrieves a session cookie.
- `POST /api/remote-events`: Creates a new event (occurrence) in the PSIM monitoring screen.
- `GET /api/logoff`: Ends the current session.

## 3. Functionality

The Lambda function is designed to:
- Receive parameters from the Coordinator Agent (e.g., `psim_url`, `psim_credentials`, `event_code`, `account_code`).
- Manage the authentication lifecycle (login, store/cache cookie, logoff).
- Make authenticated calls to the PSIM API.
- Handle success and error responses.
- Return a structured result to the Coordinator Agent.

## 4. Multi-Tenancy Considerations

This tool must support multiple different PSIM instances. The `PSIM_API_BASE_URL` and credentials (`PSIM_API_USERNAME`, `PSIM_API_PASSWORD`) will be retrieved from a central configuration store (e.g., a DynamoDB table or AWS Secrets Manager) based on the `company_id` or `condominium_id` passed in the event payload.
