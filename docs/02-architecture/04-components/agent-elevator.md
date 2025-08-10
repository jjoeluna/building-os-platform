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

## 8. Error Handling & Resilience

### **API Failure Scenarios**
*   **Network Timeout:** Retry with exponential backoff (3 attempts, 1s, 2s, 4s intervals)
*   **Authentication Failure:** Refresh JWT token and retry once
*   **Elevator Unavailable:** Return graceful error with fallback to manual mode
*   **Invalid Floor Request:** Validate against building configuration before API call

### **Circuit Breaker Pattern**
*   **Failure Threshold:** 5 consecutive failures
*   **Recovery Timeout:** 30 seconds
*   **Half-Open State:** Allow 1 test request before full recovery
*   **Fallback Action:** Notify user to use manual elevator controls

### **Error Response Format**
```json
{
  "error": {
    "code": "ELEVATOR_API_TIMEOUT",
    "message": "Elevator service temporarily unavailable",
    "retry_after": 30,
    "fallback_available": true
  }
}
```

## 9. Monitoring & Observability

### **Key Metrics**
*   **Response Time:** Target < 2 seconds for elevator calls
*   **Success Rate:** Target > 99% for API calls
*   **Circuit Breaker Status:** Track open/closed/half-open states
*   **Error Distribution:** Categorize by error type (timeout, auth, validation)

### **CloudWatch Alarms**
*   **High Error Rate:** Alert if > 5% errors in 5 minutes
*   **Slow Response:** Alert if p95 > 3 seconds
*   **Circuit Breaker Open:** Alert when circuit breaker opens
*   **API Unavailable:** Alert if Neomot API returns 503/504

### **Logging Strategy**
*   **Structured Logs:** JSON format with correlation IDs
*   **Log Levels:** DEBUG for API calls, INFO for user actions, ERROR for failures
*   **Sensitive Data:** Mask API credentials and user identifiers
*   **Retention:** 30 days for operational logs, 7 years for audit logs

## 10. Configuration Management

### **Building-Specific Settings**
```json
{
  "building_id": "lit760",
  "elevator_config": {
    "vendor": "neomot",
    "api_endpoint": "https://api.neomot.com/v1",
    "elevator_ids": ["elevator_1", "elevator_2"],
    "floor_mapping": {
      "ground": 0,
      "lobby": 1,
      "garage": -1
    },
    "timeout_seconds": 5,
    "retry_attempts": 3
  }
}
```

### **Environment Variables**
*   `ELEVATOR_API_TIMEOUT`: API timeout in seconds (default: 5)
*   `ELEVATOR_RETRY_ATTEMPTS`: Number of retry attempts (default: 3)
*   `ELEVATOR_CIRCUIT_BREAKER_THRESHOLD`: Failure threshold (default: 5)
*   `ELEVATOR_LOG_LEVEL`: Logging level (default: INFO)

### **Secrets Management**
*   **API Credentials:** Stored in AWS Secrets Manager
*   **JWT Secrets:** Rotated every 30 days
*   **Access Pattern:** `buildingos/elevator/{building_id}/credentials`
*   **Encryption:** AES-256 encryption at rest

## 11. Testing Strategy

### **Unit Tests**
*   **Adapter Tests:** Test each elevator vendor adapter independently
*   **Error Handling:** Test all error scenarios and fallback mechanisms
*   **Configuration:** Test building-specific configuration loading
*   **Mocking:** Use mock APIs for consistent test results

### **Integration Tests**
*   **API Integration:** Test with real Neomot API in staging environment
*   **End-to-End:** Test complete user journey from chat to elevator arrival
*   **Error Scenarios:** Test network failures and API outages
*   **Performance:** Test response times under load

### **Load Tests**
*   **Concurrent Users:** Test with 100+ simultaneous elevator requests
*   **API Limits:** Test rate limiting and throttling behavior
*   **Circuit Breaker:** Test circuit breaker behavior under failure conditions
*   **Memory Usage:** Monitor memory consumption during peak load
