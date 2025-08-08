---
status: "Defined"
category: "Agent"
last_updated: "2025-08-06"
owner: "Jomil"
dependencies:
  - "External: Situator API"
  - "AWS: DynamoDB (Shared Memory)"
source_code: "src/agents/agent_psim/"
---

# Agent: PSIM

## 1. Purpose

The PSIM Agent is the specialized component for integrating with Physical Security Information Management (PSIM) systems, starting with Seventh's Situator. Its primary role is to manage user identities and credentials for physical access control (e.g., facial recognition, RFID tags) in common areas of the building.

## 2. Core Functionality

### Primary Actions

*   **`provision_user`**: Receives user data (e.g., from `agent_erp` or `agent_brokers`) and creates or updates the user in the PSIM. This includes associating their photo for facial recognition and assigning them to the correct access groups.
*   **`revoke_user`**: Deactivates or deletes a user from the PSIM, immediately revoking their access permissions. This is critical for guest check-outs or when a resident moves out.
*   **`update_credentials`**: Updates a user's credentials, for example, by adding a new facial photo or a new vehicle tag.
*   **`receive_access_event`**: Listens for events sent *from* the PSIM (via webhooks or another mechanism) indicating an access event (e.g., "User X entered through the main gate"). It stores these events in the BuildingOS database for auditing and to trigger proactive automations (like calling the elevator).

## 3. API Integration (Situator)

*   **Provider:** Seventh Situator
*   **Authentication:** Session-based, requiring a login to obtain a `Seventh.Auth` cookie.
*   **Key Endpoints:**
    *   `PUT /api/login`: To authenticate and start a session.
    *   `POST /api/person`: To create or update users.
    *   `DELETE /api/person/{id}`: To remove users.
    *   Configuration of event forwarding from Situator to a BuildingOS webhook endpoint.

## 4. Data Flow

1.  **User Provisioning:** The `agent_coordinator` receives a mission to onboard a new user (resident or guest). It dispatches a `provision_user` task to `agent_psim`. The agent logs into the PSIM API, formats the user data correctly, and sends the request to create the user and their facial recognition credential.
2.  **Event Reception:** The PSIM is configured to send a webhook to a BuildingOS API Gateway endpoint whenever an access event occurs. This endpoint triggers `agent_psim`, which parses the event and stores the structured data (who, where, when) in a DynamoDB table for access logs. This event can then be used to trigger other workflows.

## 5. Security and Reliability

*   **Session Management:** The agent must efficiently manage its authentication session with the PSIM to avoid logging in for every request.
*   **Error Handling:** It must handle potential inconsistencies, such as trying to create a user that already exists or update one that doesn't.
*   **Credential Security:** The username and password for the PSIM API must be stored securely in AWS Secrets Manager.

## 6. Multi-Vendor Integration Strategy

The PSIM Agent must be architected to support a variety of PSIM vendors (e.g., Seventh Situator, Genetec, etc.) to be viable across different buildings.

*   **Adapter Pattern:** The agent will use a generic `IPsimAdapter` interface. Each supported PSIM will have its own concrete implementation (e.g., `SituatorAdapter`, `GenetecAdapter`) that handles the specific details of that vendor's API.
*   **Dynamic Adapter Loading:** Based on the building's configuration stored in DynamoDB, the agent will dynamically load and instantiate the correct adapter to handle an incoming task.
*   **Partner Configuration:** The partner portal will allow the implementing partner (e.g., the security company) to select the building's PSIM from a list of supported vendors and provide the necessary connection details and credentials securely.
