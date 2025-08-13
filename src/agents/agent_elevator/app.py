# =============================================================================
# BuildingOS Platform - Agent Elevator (Building Elevator System Integration)
# =============================================================================
#
# **Purpose:** Integrates with building elevator systems for automated control
# **Scope:** Handles elevator operations, status monitoring, and floor management
# **Usage:** Invoked by SNS when Coordinator Agent distributes elevator-related tasks
#
# **Key Features:**
# - Receives elevator task assignments from Agent Coordinator
# - Interfaces with building elevator control systems via REST APIs
# - Executes elevator operations (call, status check, floor listing)
# - Monitors elevator arrival and operational status with JWT authentication
# - Reports task completion results back to coordination layer
# - Uses common utilities layer for AWS client management
#
# **Event Flow (Incoming - Tasks):**
# 1. Agent Coordinator distributes tasks → coordinator_task_topic
# 2. This Lambda receives elevator-specific tasks
# 3. Interfaces with elevator control systems via authenticated API calls
# 4. Monitors operation completion and status
#
# **Event Flow (Outgoing - Results):**
# 1. Elevator operations complete (success/failure)
# 2. Task results formatted with operational details
# 3. Published to agent_task_result_topic → Agent Coordinator
# 4. Coordinator aggregates results for mission completion
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - DynamoDB table for elevator monitoring data (optional)
# - SNS topics for event-driven communication
# - Building elevator control system APIs with JWT authentication
# - EventBridge for elevator monitoring schedules
#
# **Integration:**
# - Triggers: SNS coordinator_task_topic, EventBridge schedules, API Gateway
# - Publishes to: agent_task_result_topic
# - External APIs: Building elevator control systems (authenticated)
# - Monitoring: CloudWatch logs, X-Ray tracing, DynamoDB monitoring data
#
# =============================================================================

import json
import os
import time
import jwt
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# HTTP client for elevator system integration
import requests

# Import common utilities from Lambda layer
from aws_clients import get_dynamodb_resource, get_sns_client, get_events_client
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
    serialize_dynamodb_item,
)
from models import SNSMessage, TaskResult, ElevatorOperation

# Initialize structured logging
logger = setup_logging(__name__)


def _determine_elevator_event_source(event: Dict[str, Any]) -> str:
    """
    Helper function to determine the source of an incoming elevator event.

    Args:
        event: The Lambda event dictionary

    Returns:
        str: Event source type ('sns', 'api_gateway', 'eventbridge', 'cors', 'unknown')
    """
    # Handle CORS preflight requests first
    if event.get("httpMethod") == "OPTIONS":
        return "cors"
    elif "Records" in event:
        for record in event["Records"]:
            if record.get("EventSource") == "aws:sns":
                return "sns"
    elif event.get("httpMethod") in ["GET", "POST"]:
        return "api_gateway"
    elif "source" in event and event["source"] == "aws.events":
        return "eventbridge"
    return "unknown"


def _handle_cors_request() -> Dict[str, Any]:
    """
    Helper function to handle CORS preflight requests.

    Returns:
        dict: CORS response with appropriate headers
    """
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": json.dumps({"message": "CORS preflight successful"}),
    }


def _extract_elevator_task_data(message_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to extract and validate elevator task data from SNS message.

    Args:
        message_body: The parsed SNS message content

    Returns:
        dict: Extracted task data with mission_id, task_id, and action
    """
    return {
        "mission_id": message_body.get("mission_id"),
        "task_id": message_body.get("task_id"),
        "action": message_body.get("action"),
        "agent": message_body.get("agent"),
        "task_data": message_body,
    }


# Environment variables configured by Terraform (validated at startup)
ELEVATOR_API_BASE_URL = get_required_env_var("ELEVATOR_API_BASE_URL")
ELEVATOR_API_SECRET = get_required_env_var("ELEVATOR_API_SECRET")
COORDINATOR_TASK_TOPIC_ARN = get_required_env_var("COORDINATOR_TASK_TOPIC_ARN")
AGENT_TASK_RESULT_TOPIC_ARN = get_required_env_var("AGENT_TASK_RESULT_TOPIC_ARN")
MONITORING_TABLE_NAME = get_optional_env_var("ELEVATOR_MONITORING_TABLE_NAME", None)
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
sns_client = get_sns_client()
events_client = get_events_client()
dynamodb_resource = get_dynamodb_resource() if MONITORING_TABLE_NAME else None

# Validate event-driven architecture configuration
logger.info(
    "Agent Elevator initialized with building system integration",
    extra={
        "elevator_api_base_url": ELEVATOR_API_BASE_URL,
        "coordinator_task_topic": COORDINATOR_TASK_TOPIC_ARN,
        "agent_task_result_topic": AGENT_TASK_RESULT_TOPIC_ARN,
        "monitoring_table": MONITORING_TABLE_NAME,
        "environment": ENVIRONMENT,
        "authentication": "JWT enabled",
    },
)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Agent Elevator Main Handler with enhanced building system integration.

    Handles elevator operations and monitoring in the BuildingOS event-driven architecture.
    Interfaces with building elevator control systems via authenticated REST APIs.

    Args:
        event: Event data from various sources
            SNS Events:
            - coordinator_task_topic: Elevator tasks from Agent Coordinator
            EventBridge Events:
            - Scheduled elevator monitoring and status checks
            API Gateway Events:
            - GET/POST: Direct elevator operations (testing/debugging)
            - OPTIONS: CORS preflight requests
        context: Lambda runtime context information

    Returns:
        dict: Response appropriate to event source
            SNS: Task completion status with elevator operation results
            EventBridge: Monitoring status and metrics
            API Gateway: HTTP response with CORS headers

    Event Routing:
        1. SNS Events → Elevator task execution
        2. EventBridge → Monitoring and status checks
        3. API Gateway → Direct elevator operations
        4. Unknown → Error response with details

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "Agent Elevator processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "event_keys": list(event.keys()),
        },
    )

    try:
        # Handle CORS preflight requests first
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": "",
            }

        # Check if this is an SNS event
        if "Records" in event:
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    topic_arn = record["Sns"]["TopicArn"]
                    message_body = json.loads(record["Sns"]["Message"])

                    print(f"Processing SNS event from topic: {topic_arn}")

                    # Check if this task is for us
                    if message_body.get("agent") == "agent_elevator":
                        return handle_task_from_sns(message_body)
                    else:
                        logger.warning(
                            "Received task for different agent, ignoring",
                            extra={
                                "expected_agent": "agent_elevator",
                                "received_agent": message_body.get("agent"),
                            },
                        )
                        return {
                            "status": "IGNORED",
                            "reason": "Task not for this agent",
                        }

        # Parse event based on source
        if "body" in event and "httpMethod" in event:
            # HTTP request via API Gateway
            try:
                body = json.loads(event["body"]) if event["body"] else {}
                print(f"Parsed API Gateway body: {body}")

                # Extract required fields
                mission_id = body.get("mission_id")
                task_id = body.get("task_id", f"http-{int(time.time())}")
                action = body.get("action", "call_elevator")
                parameters = body.get("parameters", {})

                if not mission_id:
                    return {
                        "statusCode": 400,
                        "headers": {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                        },
                        "body": json.dumps(
                            {"error": "mission_id is required in request body"}
                        ),
                    }

            except json.JSONDecodeError as e:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    },
                    "body": json.dumps(
                        {"error": f"Invalid JSON in request body: {str(e)}"}
                    ),
                }
        else:
            # Direct invocation from Coordinator Agent
            mission_id = event["mission_id"]
            task_id = event["task_id"]
            action = event["action"]
            parameters = event["parameters"]

        print(f"Processing task {task_id} for mission {mission_id}: {action}")

        # Execute the elevator action
        result = execute_elevator_action(action, parameters, mission_id)

        # Publish task completion
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        logger.error(
            "Critical error in elevator agent handler",
            extra={"correlation_id": correlation_id, "error": str(e)},
        )

        # Try to publish failure if we have the required info
        if "mission_id" in locals() and "task_id" in locals():
            publish_task_completion(mission_id, task_id, "failed", {"error": str(e)})

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)}),
        }


def handle_task_from_sns(message_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle task received from SNS (new architecture)
    """
    try:
        mission_id = message_body["mission_id"]
        task_id = message_body["task_id"]
        action = message_body["action"]
        parameters = message_body["parameters"]

        print(f"Processing SNS task {task_id} for mission {mission_id}: {action}")

        # Execute the elevator action
        result = execute_elevator_action(action, parameters, mission_id)

        # Publish task completion using new architecture
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        logger.error(
            "Error processing SNS task",
            extra={
                "task_id": message_body.get("task_id"),
                "mission_id": message_body.get("mission_id"),
                "error": str(e),
            },
        )

        # Try to publish failure
        try:
            mission_id = message_body.get("mission_id")
            task_id = message_body.get("task_id")
            if mission_id and task_id:
                publish_task_completion(
                    mission_id, task_id, "failed", {"error": str(e)}
                )
        except Exception as pub_error:
            logger.error(
                "Error publishing task failure notification",
                extra={
                    "mission_id": mission_id,
                    "task_id": task_id,
                    "error": str(pub_error),
                },
            )

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps({"error": str(e)}),
        }


def execute_elevator_action(
    action: str, parameters: Dict[str, Any], mission_id: str | None = None
) -> Dict[str, Any]:
    """
    Execute elevator action based on the action type
    """
    if action == "call_elevator":
        from_floor = parameters.get("from_floor")
        to_floor = parameters.get("to_floor")
        if from_floor is None or to_floor is None:
            raise ValueError("Missing required parameters for call_elevator")
        result = call_elevator(int(from_floor), int(to_floor))

        # If successful, start monitoring
        if result.get("status") == "success" and mission_id:
            start_monitoring(mission_id, int(to_floor))

        return result

    elif action == "check_elevator_status":
        return check_elevator_status()
    elif action == "list_floors":
        return list_floors()
    elif action == "monitor_elevator_arrival":
        target_floor = parameters.get("target_floor")
        mission_id_param = parameters.get("mission_id")
        if target_floor is None or mission_id_param is None:
            raise ValueError("Missing required parameters for monitor_elevator_arrival")
        return monitor_elevator_arrival(int(target_floor), str(mission_id_param))
    elif action == "list_active_monitoring":
        return list_active_monitoring()
    elif action == "test":
        # Test action for API diagnostics
        return {
            "status": "success",
            "message": "Elevator agent is responding correctly",
            "available_actions": [
                "call_elevator",
                "check_elevator_status",
                "list_floors",
                "monitor_elevator_arrival",
                "list_active_monitoring",
                "test",
            ],
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        raise ValueError(f"Unknown elevator action: {action}")


def call_elevator(from_floor: int, to_floor: int) -> Dict[str, Any]:
    """
    Call elevator using the elevator API
    Uses the correct endpoint format: /elevator/{id}/call
    """
    try:
        # Generate JWT token for authentication
        token = generate_jwt_token()

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Correct API endpoint with elevator ID
        elevator_id = "010504"  # ID correto fornecido
        url = f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/call"

        # Correct payload format according to documentation
        payload = {
            "from": from_floor,
            "to": to_floor,
        }

        print(f"Calling elevator API: {url}")
        print(f"Payload: {payload}")

        # Make API call
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 204:  # Success is 204 No Content
            print(f"Elevator API success: {response.status_code}")

            return {
                "status": "success",
                "message": f"Elevator called from floor {from_floor} to floor {to_floor}",
                "floor": from_floor,
                "target_floor": to_floor,
            }
        elif response.status_code == 400 and "Elevador não permitido" in response.text:
            # API externa não tem elevador configurado - simular sucesso para demo
            logger.warning(
                "External elevator API not configured, simulating success for demo",
                extra={"status_code": response.status_code},
            )

            return {
                "status": "success",
                "message": f"Elevator called from floor {from_floor} to floor {to_floor} (simulated)",
                "floor": from_floor,
                "target_floor": to_floor,
                "note": "External API not configured - using simulation",
            }
        else:
            error_msg = (
                f"Elevator API returned status {response.status_code}: {response.text}"
            )
            print(error_msg)

            return {"status": "error", "message": error_msg, "floor": from_floor}

    except requests.RequestException as e:
        error_msg = f"Network error calling elevator API: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg, "floor": from_floor}
    except Exception as e:
        error_msg = f"Unexpected error in elevator call: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg, "floor": from_floor}


def check_elevator_status() -> Dict[str, Any]:
    """
    Check current elevator status and position
    Uses the correct endpoint format: /elevator/{id}/status

    Improvements:
    - Retry logic for empty floor responses
    - Convert string floor to int
    - Validate elevator is stopped before trusting floor data
    """
    try:
        # Generate JWT token for authentication
        token = generate_jwt_token()

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Correct API endpoint with elevator ID
        elevator_id = "010504"  # ID correto fornecido
        url = f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/status"

        print(f"Checking elevator status: {url}")

        # Retry logic for API calls
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                # Make API call
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    print(f"Elevator status response (attempt {attempt + 1}): {result}")

                    # Extract and validate floor
                    floor_raw = result.get("floor", "")
                    elevator_status = result.get("status", "unknown")
                    direction = result.get("direction", "unknown")

                    # Handle empty floor - retry if not last attempt
                    if not floor_raw or floor_raw == "":
                        if attempt < max_retries - 1:
                            print(
                                f"Empty floor received, retrying in {retry_delay} seconds..."
                            )
                            time.sleep(retry_delay)
                            continue
                        else:
                            print("Empty floor received on final attempt")
                            return {
                                "status": "error",
                                "message": "API returned empty floor after retries",
                                "elevator_status": elevator_status,
                                "direction": direction,
                            }

                    # Convert floor to integer
                    try:
                        current_floor = int(floor_raw)
                    except (ValueError, TypeError):
                        print(f"Invalid floor format: {floor_raw}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            return {
                                "status": "error",
                                "message": f"Invalid floor format: {floor_raw}",
                                "elevator_status": elevator_status,
                            }

                    # Determine if we should trust the floor data
                    # Only trust floor when elevator is stopped
                    floor_reliable = elevator_status.lower() in [
                        "stopped",
                        "idle",
                        "stoping",
                    ]

                    return {
                        "status": "success",
                        "current_floor": current_floor,
                        "direction": direction,
                        "elevator_status": elevator_status,
                        "door_sensor": result.get("doorSensor", "unknown"),
                        "floor_reliable": floor_reliable,
                        "api_response": result,
                    }

                else:
                    error_msg = (
                        f"API returned status {response.status_code}: {response.text}"
                    )
                    print(error_msg)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue

            except requests.RequestException as e:
                error_msg = f"Network error on attempt {attempt + 1}: {str(e)}"
                print(error_msg)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        # If all retries failed, return error
        return {
            "status": "error",
            "message": "All API call attempts failed",
        }

    except Exception as e:
        error_msg = f"Unexpected error checking elevator status: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def list_floors() -> Dict[str, Any]:
    """
    List available floors in the building
    Uses the correct endpoint format: /elevator/{id}/floors
    """
    try:
        # Generate JWT token for authentication
        token = generate_jwt_token()

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Correct API endpoint with elevator ID
        elevator_id = "010504"  # ID correto fornecido
        url = f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/floors"

        print(f"Listing floors: {url}")

        # Make API call
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Floors list response: {result}")

            return {
                "status": "success",
                "floors": result,
                "api_response": result,
            }
        elif response.status_code == 400 and "Elevador não permitido" in response.text:
            # API externa não tem elevador configurado - simular lista para demo
            logger.warning(
                "External elevator API not configured, simulating floors list for demo",
                extra={"status_code": response.status_code},
            )

            simulated_floors = [
                {"floor": 1, "description": "Térreo"},
                {"floor": 2, "description": "1º Andar"},
                {"floor": 3, "description": "2º Andar"},
                {"floor": 4, "description": "3º Andar"},
                {"floor": 5, "description": "4º Andar"},
            ]

            return {
                "status": "success",
                "floors": simulated_floors,
                "note": "External API not configured - using simulation",
            }
        else:
            error_msg = (
                f"Elevator API returned status {response.status_code}: {response.text}"
            )
            print(error_msg)
            return {"status": "error", "message": error_msg}

    except requests.RequestException as e:
        error_msg = f"Network error listing floors: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error listing floors: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def list_active_monitoring() -> Dict[str, Any]:
    """
    List all active monitoring missions from DynamoDB
    Useful for debugging and recovery
    """
    try:
        table = dynamodb.Table(MONITORING_TABLE_NAME)

        response = table.scan(
            FilterExpression="attribute_exists(mission_id) AND #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": "monitoring"},
        )

        active_missions = []
        for item in response["Items"]:
            mission_info = {
                "mission_id": item["mission_id"],
                "target_floor": item.get("target_floor"),
                "start_time": item.get("start_time"),
                "last_floor": item.get("last_floor"),
                "consecutive_matches": item.get("consecutive_matches", 0),
                "retry_count": item.get("retry_count", 0),
                "elevator_status": item.get("elevator_status", "unknown"),
            }
            active_missions.append(mission_info)

        return {
            "status": "success",
            "active_monitoring_count": len(active_missions),
            "active_missions": active_missions,
        }

    except Exception as e:
        error_msg = f"Error listing active monitoring: {str(e)}"
        logger.error(
            "Error listing active monitoring from DynamoDB",
            extra={"error": str(e)},
        )
        return {"status": "error", "message": error_msg}


def monitor_elevator_arrival(target_floor: int, mission_id: str) -> Dict[str, Any]:
    """
    Monitor elevator arrival at target floor
    Checks if elevator stays at target floor for at least 5 seconds
    """
    try:
        import time

        print(f"Monitoring elevator arrival at floor {target_floor}")

        # Check if elevator is already at target floor
        status = check_elevator_status()
        if status["status"] != "success":
            return {"status": "error", "message": "Could not check elevator status"}

        current_floor = status.get("current_floor")

        if current_floor == target_floor:
            # Verify elevator stays for 5 seconds
            time.sleep(5)

            # Check again
            status_after = check_elevator_status()
            if (
                status_after["status"] == "success"
                and status_after.get("current_floor") == target_floor
            ):

                return {
                    "status": "success",
                    "message": f"Elevator arrived at floor {target_floor}",
                    "arrived": True,
                    "floor": target_floor,
                }
            else:
                return {
                    "status": "monitoring",
                    "message": f"Elevator moved from floor {target_floor}",
                    "arrived": False,
                    "floor": current_floor,
                }
        else:
            return {
                "status": "monitoring",
                "message": f"Elevator not yet at floor {target_floor} (currently at {current_floor})",
                "arrived": False,
                "current_floor": current_floor,
                "target_floor": target_floor,
            }

    except Exception as e:
        error_msg = f"Error monitoring elevator arrival: {str(e)}"
        logger.error(
            "Error monitoring elevator arrival",
            extra={
                "target_floor": target_floor,
                "mission_id": mission_id,
                "error": str(e),
            },
        )
        return {"status": "error", "message": error_msg}


def generate_jwt_token() -> str:
    """
    Generate JWT token for elevator API authentication
    """
    try:
        payload = {
            "iss": "building-os",
            "aud": "elevator-api",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() + 300,  # 5 minutes
        }

        token = jwt.encode(payload, ELEVATOR_API_SECRET, algorithm="HS256")
        return token

    except Exception as e:
        logger.error(
            "Error generating JWT token for elevator API",
            extra={"error": str(e)},
        )
        raise


def publish_task_completion(
    mission_id: str, task_id: str, status: str, result: Dict[str, Any]
) -> None:
    """
    Publish task completion using appropriate architecture
    """
    try:
        completion_message = {
            "mission_id": mission_id,
            "task_id": task_id,
            "agent": "agent_elevator",
            "status": status,
            "result": result,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        if USE_NEW_ARCHITECTURE:
            # Use new agent-task-result-topic
            topic_arn = AGENT_TASK_RESULT_TOPIC_ARN
            print(
                f"Publishing task completion via NEW architecture to agent-task-result-topic"
            )
        else:
            # New architecture should always be available now
            print("ERROR: New architecture topics not available")
            raise ValueError("AGENT_TASK_RESULT_TOPIC_ARN not configured")

        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(completion_message),
            Subject=f"Task {task_id} Completion",
        )

        print(f"Published task completion for {task_id}")

    except Exception as e:
        logger.error(
            "Error publishing task completion to SNS",
            extra={
                "mission_id": mission_id,
                "task_id": task_id,
                "status": status,
                "error": str(e),
            },
        )
        # Don't raise here to avoid infinite loops


def start_monitoring(mission_id: str, target_floor: int) -> None:
    """
    Start monitoring elevator arrival with continuous polling.

    ARCHITECTURAL NOTE: This polling approach is inefficient for Lambda.
    TODO: Replace with EventBridge scheduled rules or Step Functions for better cost/performance.
    This function will:
    1. Save monitoring state to DynamoDB for persistence
    2. Block and poll every 1 second until elevator arrives
    3. Update DynamoDB with progress
    4. Clean up DynamoDB when done
    """
    try:
        # Save initial monitoring state to DynamoDB
        table = dynamodb.Table(MONITORING_TABLE_NAME)

        monitoring_state = {
            "mission_id": mission_id,
            "target_floor": target_floor,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "monitoring",
            "consecutive_matches": 0,
            "last_floor": None,
            "retry_count": 0,
            "ttl": int(
                (datetime.now(timezone.utc).timestamp() + 600)
            ),  # 10 minutes TTL
        }

        table.put_item(Item=monitoring_state)
        print(f"Saved monitoring state for mission {mission_id} to DynamoDB")

        print(
            f"Starting continuous monitoring for mission {mission_id} to floor {target_floor}"
        )

        start_time = datetime.now(timezone.utc)
        consecutive_matches = 0
        retry_count = 0
        max_retries = 5
        timeout_seconds = 90  # 1.5 minutes - reduced for Lambda efficiency

        while True:
            # Check timeout
            elapsed_time = datetime.now(timezone.utc) - start_time
            if elapsed_time.total_seconds() > timeout_seconds:
                notify_user(
                    mission_id,
                    "timeout",
                    "⏰ Timeout: Elevador demorou mais de 1.5 minutos",
                )
                cleanup_monitoring_state(mission_id)
                print(f"Monitoring timeout for mission {mission_id}")
                return

            # Check elevator status
            status_result = check_elevator_status()

            if status_result.get("status") != "success":
                retry_count += 1
                print(
                    f"Error checking elevator status (attempt {retry_count}/{max_retries}): {status_result.get('message', 'Unknown error')}"
                )

                # Update retry count in DynamoDB
                table.update_item(
                    Key={"mission_id": mission_id},
                    UpdateExpression="SET retry_count = :retry",
                    ExpressionAttributeValues={":retry": retry_count},
                )

                if retry_count >= max_retries:
                    notify_user(
                        mission_id,
                        "error",
                        "❌ Erro: Não foi possível monitorar o elevador após 5 tentativas",
                    )
                    cleanup_monitoring_state(mission_id)
                    print(f"Max retries reached for mission {mission_id}")
                    return

                time.sleep(1)  # Wait before retry
                continue

            # Reset retry count on successful API call
            retry_count = 0

            current_floor = status_result.get("current_floor")
            floor_reliable = status_result.get("floor_reliable", False)
            elevator_status = status_result.get("elevator_status", "unknown")

            print(
                f"Mission {mission_id}: Floor {current_floor}, Status: {elevator_status}, Reliable: {floor_reliable}, Target: {target_floor}"
            )

            # Update DynamoDB with current status
            table.update_item(
                Key={"mission_id": mission_id},
                UpdateExpression="SET last_floor = :floor, retry_count = :retry, elevator_status = :status",
                ExpressionAttributeValues={
                    ":floor": current_floor,
                    ":retry": 0,
                    ":status": elevator_status,
                },
            )

            # Only process floor comparison when elevator is stopped and floor data is reliable
            if not floor_reliable:
                print(
                    f"Elevator not stopped ({elevator_status}) - continuing monitoring"
                )
                consecutive_matches = 0  # Reset when elevator is moving

                # Update consecutive matches in DynamoDB
                table.update_item(
                    Key={"mission_id": mission_id},
                    UpdateExpression="SET consecutive_matches = :matches",
                    ExpressionAttributeValues={":matches": consecutive_matches},
                )

                time.sleep(1)
                continue

            if current_floor == target_floor:
                consecutive_matches += 1
                print(
                    f"Elevator at target floor {target_floor} - consecutive matches: {consecutive_matches}/5"
                )

                # Update consecutive matches in DynamoDB
                table.update_item(
                    Key={"mission_id": mission_id},
                    UpdateExpression="SET consecutive_matches = :matches",
                    ExpressionAttributeValues={":matches": consecutive_matches},
                )

                if consecutive_matches >= 5:  # 5 seconds at target floor
                    notify_user(
                        mission_id,
                        "arrived",
                        f"✅ Elevador chegou no andar {target_floor}!",
                    )
                    cleanup_monitoring_state(mission_id)
                    print(
                        f"Elevator arrived at target floor {target_floor} for mission {mission_id}"
                    )
                    return
            else:
                if consecutive_matches > 0:
                    print(
                        f"Elevator moved from target floor {target_floor} to {current_floor} - resetting counter"
                    )
                consecutive_matches = 0

                # Update consecutive matches in DynamoDB
                table.update_item(
                    Key={"mission_id": mission_id},
                    UpdateExpression="SET consecutive_matches = :matches",
                    ExpressionAttributeValues={":matches": consecutive_matches},
                )

            # Wait 1 second before next check
            time.sleep(1)

    except Exception as e:
        print(f"Error in monitoring: {str(e)}")
        notify_user(mission_id, "error", f"❌ Erro no monitoramento: {str(e)}")
        cleanup_monitoring_state(mission_id)
        raise


def cleanup_monitoring_state(mission_id: str) -> None:
    """
    Remove monitoring state from DynamoDB when done
    """
    try:
        table = dynamodb.Table(MONITORING_TABLE_NAME)
        table.delete_item(Key={"mission_id": mission_id})
        print(f"Removed monitoring state for mission {mission_id}")
    except Exception as e:
        print(f"Error cleaning up monitoring state for mission {mission_id}: {str(e)}")
        # Don't raise - cleanup is best effort


def notify_user(mission_id: str, notification_type: str, message: str) -> None:
    """
    Notify user about monitoring status via SNS
    """
    try:
        notification_message = {
            "mission_id": mission_id,
            "notification_type": notification_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "agent_elevator",
        }

        # Use the appropriate topic based on architecture
        topic_arn = AGENT_TASK_RESULT_TOPIC_ARN if USE_NEW_ARCHITECTURE else None
        if not topic_arn:
            logger.warning(
                "No topic ARN available for notifications",
                extra={"mission_id": mission_id, "message": message},
            )
            return

        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(notification_message),
            Subject=f"Elevator Monitoring Update - {mission_id}",
        )

        print(f"Sent notification for mission {mission_id}: {message}")

    except Exception as e:
        logger.error(
            "Error sending monitoring notification",
            extra={"mission_id": mission_id, "message": message, "error": str(e)},
        )
        # Don't raise - notification failure shouldn't break monitoring
