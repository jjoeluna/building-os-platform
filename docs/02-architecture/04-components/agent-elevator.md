---
status: "Defined"
category: "Agent"
last_updated: "2025-08-06"
owner: "Jomil"
dependencies:
  - "External: Neomot API"
  - "AWS: DynamoDB (Shared Memory)"
source_code: "src/agents/agent_elevator/"
---

# Agent: Elevator

## 1. Purpose

The Elevator Agent is the specialized component for all interactions with the building's elevator system. It handles both user-initiated commands (e.g., calling an elevator) and proactive automations triggered by other system events.

## 2. Core Functionality

### Primary Actions

*   **`call_elevator`**: Receives a request to call an elevator to a specific floor and sends the command to the elevator API.
*   **`get_elevator_status`**: Queries the current status of the elevator, including its floor, direction, and operational state.
*   **`monitor_arrival`**: After a `call_elevator` command, this function can be triggered to poll the elevator's status and send a notification (e.g., "[ARRIVED] Your elevator is here!") once it reaches the target floor.

## 3. Proactive Automation

*   **Trigger:** The agent listens for `access_event` messages on the event bus, published by `agent_psim`.
*   **Logic:** When a valid access event is detected for a resident or guest at an entrance floor (e.g., ground floor, garage), the agent automatically triggers the `call_elevator` function to send the elevator to that floor, anticipating the user's needs.

## 4. API Integration (Neomot)

*   **Provider:** Neomot
*   **Authentication:** JWT with a shared secret.
*   **Key Endpoints:**
    *   `POST /elevator/{id}/call`
    *   `GET /elevator/{id}/status`

## 5. Data Flow

1.  **User Command:** A user requests an elevator via chat. The `agent_coordinator` dispatches a `call_elevator` task to this agent. The agent calls the Neomot API and then initiates a monitoring process.
2.  **Proactive Trigger:** `agent_psim` publishes an access event. The `agent_elevator` is subscribed to these events, validates if the access location requires an elevator, and if so, calls the Neomot API.
3.  **Configuration:** Before executing a command, the agent can query DynamoDB to retrieve building-specific configurations, such as the mapping of entrance doors to specific elevator lobby floors.

## 6. Key Considerations

*   **Real-time Performance:** Elevator calls must be executed with very low latency to be useful. The agent's infrastructure must be optimized for quick responses.
*   **Stateful Monitoring:** The arrival monitoring process is stateful. The agent uses DynamoDB to track the status of a monitoring request to handle retries and timeouts correctly.

## 7. Multi-Vendor Integration Strategy

Different buildings use elevators from various manufacturers (e.g., Otis, Schindler, Thyssenkrupp), each with potentially different APIs.

*   **Adapter Pattern:** The agent will be built around a generic `IElevatorAdapter` interface defining common actions (`call_to_floor`, `query_status`). Each supported brand will have its own implementation (e.g., `NeomotAdapter`, `OtisApiAdapter`).
*   **Dynamic Adapter Loading:** The specific adapter for a building will be loaded at runtime based on configuration data stored in DynamoDB, which is set up during the building's onboarding.
*   **Partner Configuration:** The partner responsible for the building's implementation will configure the elevator integration, selecting the manufacturer and providing API credentials through the partner portal.
