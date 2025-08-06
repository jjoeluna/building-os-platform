---
status: "Production Ready"
category: "Agent"
last_updated: "2025-08-06"
owner: ""
dependencies:
  - "External: anna-minimal-api.neomot.com"
  - "AWS: SNS (Task Completion Topic)"
  - "AWS: DynamoDB (Elevator Monitoring Table)"
  - "AWS: EventBridge (Monitoring Events)"
source_code: "src/agents/agent_elevator/"
---

# Agent: Elevator

## 1. Purpose

The Elevator Agent is a specialized Lambda function that handles all elevator-related operations within the BuildingOS platform. It integrates with the external Neomot Elevator API and provides advanced monitoring capabilities, including real-time elevator arrival detection with timeout and error handling.

## 2. Core Functionality

### Primary Actions

#### `call_elevator`
Calls an elevator to move from one floor to another.
- **Parameters:** `from_floor`, `to_floor`
- **Behavior:** 
  - Generates JWT token for API authentication
  - Makes POST request to elevator API
  - Implements retry logic (3 attempts with 2-second delays)
  - Automatically starts monitoring if mission_id provided
- **Returns:** Success/error status with floor information

#### `check_elevator_status`
Retrieves current elevator position and status.
- **Behavior:**
  - Implements retry logic for empty floor responses
  - Validates floor data reliability based on elevator status
  - Only trusts floor data when elevator is stopped
- **Returns:** Current floor, direction, status, door sensor state, and reliability flag

#### `list_floors`
Retrieves available floors for the elevator.
- **Behavior:**
  - Falls back to simulated data if API not configured
- **Returns:** Array of floor objects with numbers and descriptions

#### `monitor_elevator_arrival`
Monitors elevator arrival at a specific target floor.
- **Parameters:** `target_floor`, `mission_id`
- **Behavior:**
  - Checks if elevator is at target floor and remains for 5 seconds
- **Returns:** Arrival status and current position

#### `list_active_monitoring`
Lists all currently active monitoring missions.
- **Returns:** Active monitoring missions from DynamoDB

## 3. Advanced Monitoring System

### Continuous Monitoring Process

The agent implements a sophisticated monitoring system that:

1. **Persistent State Management**
   - Saves monitoring state to DynamoDB with TTL (10 minutes)
   - Tracks mission progress across Lambda invocations
   - Maintains retry counts and status updates

2. **Real-time Polling**
   - Polls elevator status every 1 second
   - Validates floor data reliability
   - Only processes when elevator is stopped

3. **Timeout Protection**
   - **Maximum monitoring time:** 5 minutes
   - **Maximum API retries:** 5 attempts
   - Sends timeout notifications: `[TIMEOUT] Elevador demorou mais de 5 minutos`
   - Sends error notifications: `[ERRO] Nao foi possivel monitorar o elevador apos 5 tentativas`

4. **Success Detection**
   - Confirms elevator arrival at target floor
   - Sends success notifications: `[CHEGOU] Elevador chegou no andar {floor}!`

### Notification System

All monitoring events trigger user notifications via SNS:
- **Success:** `[CHEGOU] Elevador chegou no andar X!`
- **Timeout:** `[TIMEOUT] Elevador demorou mais de 5 minutos`
- **Error:** `[ERRO] Nao foi possivel monitorar o elevador apos 5 tentativas`

## 4. API Integration

### External API Details
- **Provider:** Neomot
- **Base URL:** `https://anna-minimal-api.neomot.com`
- **Authentication:** JWT (HS256) with 5-minute expiration
- **Elevator ID:** `010504`

### Key Endpoints Used

#### `POST /elevator/010504/call`
```json
{
    "from": 5,
    "to": 5
}
```
- **Success:** `204 No Content`
- **Note:** `from` = pickup floor, `to` = destination floor

#### `GET /elevator/010504/status`
```json
{
    "floor": "5",
    "direction": "Stopped",
    "doorSensor": "NotActivated",
    "status": "Stopped"
}
```

#### `GET /elevator/010504/floors`
Returns available floors array.

## 5. Error Handling & Resilience

### Retry Logic
- **API calls:** 3 attempts with 2-second delays
- **Status checks:** Up to 5 retries for empty responses
- **Network timeouts:** 10 seconds per request

### Graceful Degradation
- Simulates responses when external API unavailable
- Continues monitoring despite temporary API failures
- Always provides user feedback (success, timeout, or error)

### State Cleanup
- Automatic DynamoDB cleanup on completion/timeout/error
- TTL-based automatic cleanup (10 minutes)
- Prevents resource leaks and infinite monitoring

## 6. Integration Points

### Input Sources
- **Coordinator Agent:** Task requests via direct invocation
- **EventBridge:** Monitoring triggers (if implemented)

### Output Destinations
- **SNS Topic:** Task completion notifications
- **DynamoDB:** Monitoring state persistence
- **Coordinator Agent:** Task results

### Message Format
```json
{
    "mission_id": "uuid",
    "task_id": "uuid", 
    "agent": "agent_elevator",
    "status": "completed|failed|notification",
    "result": {...},
    "completed_at": "ISO timestamp"
}
```

## 7. Configuration

### Environment Variables
- `ELEVATOR_API_BASE_URL`: Neomot API base URL
- `ELEVATOR_API_SECRET`: JWT signing secret
- `TASK_COMPLETION_TOPIC_ARN`: SNS topic for notifications
- `MONITORING_TABLE_NAME`: DynamoDB table for state (default: bos-elevator-monitoring-dev)

### DynamoDB Schema
**Table:** `bos-elevator-monitoring-{env}`
- **Primary Key:** `mission_id` (String)
- **Attributes:**
  - `target_floor`: Target floor number
  - `start_time`: ISO timestamp
  - `status`: monitoring|completed|timeout|error
  - `last_floor`: Last known elevator position
  - `retry_count`: API retry counter
  - `elevator_status`: Last elevator status
  - `ttl`: Automatic cleanup timestamp

## 8. Monitoring & Observability

### CloudWatch Logs
- Detailed monitoring progress logs
- API call success/failure tracking
- Error reporting with mission context

### Metrics
- Mission completion rates
- Average monitoring duration
- API reliability statistics
- Timeout and error frequencies

## 9. Security

### Authentication
- JWT tokens with 5-minute expiration
- Secure secret management via environment variables
- No sensitive data in logs

### Access Control
- Lambda execution role with minimal required permissions
- SNS publish permissions
- DynamoDB read/write access to monitoring table only

## 10. Performance Characteristics

### Latency
- **Immediate response:** Task acceptance and initial API calls
- **Monitoring duration:** Variable (typically 10-60 seconds)
- **Maximum monitoring:** 5 minutes with automatic timeout

### Throughput
- Supports concurrent monitoring missions
- Scales with Lambda concurrency limits
- DynamoDB scales with provisioned capacity

### Resource Usage
- **Memory:** 128-256 MB sufficient for most operations
- **Execution time:** Monitoring missions run continuously until completion
- **Network:** Minimal bandwidth for API polling

## 11. API Testing

### Manual Testing Commands

The following curl commands can be used to test the external elevator API directly. These commands use a JWT token with 1-year validity for convenience during development and testing.

#### Check Elevator Status
```bash
curl "https://anna-minimal-api.neomot.com/elevator/010504/status" \
  -H "Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJleHAiOiAxNzg2MDE5NTAwfQ.rjcJ6AneYYv3RlV2wd_EChefdkfwGbBWIenurIr_YBI"
```

**Expected Response:**
```json
{
  "floor": "5",
  "direction": "Stopped", 
  "doorSensor": "NotActivated",
  "status": "Stopped"
}
```

#### Call Elevator to Floor 5
```bash
curl -X POST "https://anna-minimal-api.neomot.com/elevator/010504/call" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJleHAiOiAxNzg2MDE5NTAwfQ.rjcJ6AneYYv3RlV2wd_EChefdkfwGbBWIenurIr_YBI" \
  -d '{"from": 5, "to": 5}'
```

**Expected Response:** `204 No Content` (success)

#### List Available Floors
```bash
curl "https://anna-minimal-api.neomot.com/elevator/010504/floors" \
  -H "Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJleHAiOiAxNzg2MDE5NTAwfQ.rjcJ6AneYYv3RlV2wd_EChefdkfwGbBWIenurIr_YBI"
```

**Expected Response:**
```json
[
  { "floor": 1, "description": "Térreo" },
  { "floor": 2, "description": "1º Andar" },
  { "floor": 3, "description": "2º Andar" },
  { "floor": 4, "description": "3º Andar" },
  { "floor": 5, "description": "4º Andar" }
]
```

### JWT Token Details
- **Expiration:** August 6, 2026 (1 year validity)
- **Algorithm:** HS256
- **Use Case:** Development and testing only

### Testing Notes
- The `from` parameter indicates where the elevator should pick up the user
- The `to` parameter indicates the destination floor
- For simple floor calls, use the same value for both `from` and `to`
- Monitor elevator movement by repeatedly calling the status endpoint
- Typical elevator movement takes 10-60 seconds depending on distance

## 12. Development Notes

### Testing
- Comprehensive retry logic testing
- Timeout scenario validation
- API error response handling
- DynamoDB state management verification

### Future Enhancements
- Multiple elevator support
- Predictive arrival algorithms
- Enhanced error recovery
- Performance optimization for high-frequency monitoring
