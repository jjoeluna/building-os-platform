---
status: "Defined"
category: "Agent"
last_updated: "2025-08-06"
owner: "Jomil"
dependencies:
  - "External: TTLock API"
  - "AWS: DynamoDB (Shared Memory)"
source_code: "src/agents/agent_locks/"
---

# Agent: Locks

## 1. Purpose

The Locks Agent is responsible for integrating with smart lock systems, starting with TTLock. Its main function is to manage access credentials (typically numeric passcodes) for individual apartment doors, primarily for short-term rental guests.

## 2. Core Functionality

### Primary Actions

*   **`create_passcode`**: Generates a new, time-limited passcode for a specific lock. This is the primary function used for guest check-ins.
*   **`delete_passcode`**: Removes an existing passcode from a lock, typically used upon guest check-out or cancellation.
*   **`get_lock_status`**: Queries the status of a lock, including its battery level and connectivity.

## 3. API Integration (TTLock)

*   **Provider:** TTLock
*   **Authentication:** OAuth 2.0, requiring a token exchange.
*   **Key Endpoints:**
    *   `POST /oauth2/token`: To get an access token.
    *   `POST /v3/passcode/add`: To create a new passcode for a lock.
    *   `POST /v3/passcode/delete`: To delete a passcode.
    *   `GET /v3/lock/queryState`: To check the lock's battery status.

## 4. Data Flow

1.  **Password Creation:** The `agent_brokers` creates a numeric password and stores it in DynamoDB when a reservation is confirmed.
2.  **Provisioning Task:** At the time of check-in, the `agent_coordinator` dispatches a `create_passcode` task to `agent_locks`.
3.  **API Call:** The `agent_locks` retrieves the pre-generated password and guest stay details from DynamoDB. It then authenticates with the TTLock API and sends the command to program the passcode into the specific apartment's lock with the correct start and end validity dates.
4.  **Revocation Task:** Upon check-out, a similar process is triggered to call the `delete_passcode` function, ensuring the guest's access is immediately revoked.

## 5. Key Considerations

*   **Offline Operation:** Smart locks often operate via Bluetooth and may not be constantly connected to the internet. The agent must handle potential delays in command execution and rely on the lock's gateway to relay the command when the lock is next available.
*   **Credential Management:** The agent needs to securely store and manage the OAuth credentials for accessing the TTLock API for each operator's account.

## 6. Multi-Vendor Integration Strategy

To avoid vendor lock-in with a single smart lock brand, the agent will be designed for extensibility.

*   **Adapter Pattern:** A generic `ILockAdapter` interface will define standard operations (`create_passcode`, `delete_passcode`). Specific classes like `TtlockAdapter`, `YaleAdapter`, etc., will implement this interface.
*   **Dynamic Adapter Loading:** The system will retrieve the lock brand and API credentials associated with a specific property from a configuration database and load the appropriate adapter at runtime.
*   **Partner/Operator Configuration:** The operator's portal will provide a simple interface for them to select their lock brand and provide the necessary API keys, which will be stored securely.
