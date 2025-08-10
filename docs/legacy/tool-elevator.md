---
status: "In Development"
category: "Integration"
last_updated: "2025-08-04"
owner: ""
dependencies:
  - "External: anna-minimal-api.neomot.com"
source_code: "src/tools/tool_elevator/"
---

# Tool: Elevator

## 1. Purpose

This tool is a Lambda function responsible for integrating with the external Neomot Elevator API. It provides a standardized interface for the BuildingOS platform to perform actions such as calling an elevator to a specific floor.

## 2. API Integration Details

- **Provider:** Neomot
- **Endpoint Base:** `https://anna-minimal-api.neomot.com/`
- **Authentication:** JWT (HS256) with a shared secret. A new token must be generated for each request.

### Key Endpoints

#### `POST /elevator/{id}/call`

Calls an elevator to a specific origin and destination floor.

-   **Parameters:**
    -   `id` (path): The unique ID of the elevator.
-   **Request Body:**
    ```json
    {
        "from": 1,
        "to": 5
    }
    ```
-   **Success Response:** `204 No Content`
-   **Error Response:** `400 Bad Request` with a JSON array of error messages.

#### `GET /elevator/{id}/floors`

Lists all floors that the specified elevator serves.

-   **Parameters:**
    -   `id` (path): The unique ID of the elevator.
-   **Success Response:** `200 OK` with a JSON array of floor objects.
    ```json
    [
        { "floor": 1, "description": "Lobby" },
        { "floor": 2, "description": "Garage" }
    ]
    ```

#### `GET /elevator/{id}/status`

Returns the current floor, direction, and status of the elevator.

-   **Parameters:**
    -   `id` (path): The unique ID of the elevator.
-   **Success Response:** `200 OK` with a JSON object describing the elevator's status.
    ```json
    {
      "floor": "10",
      "direction": "Up",
      "doorSensor": "NotActivated",
      "status": "Moving"
    }
    ```

## 3. Functionality

The Lambda function is designed to:
- Receive parameters from the Coordinator Agent (e.g., `elevator_id`, `from_floor`, `to_floor`).
- Generate a short-lived JWT for authentication.
- Make a `POST` request to the external API.
- Handle success (`204 No Content`) and error (`400 Bad Request`) responses.
- Return a structured result to the Coordinator Agent.
