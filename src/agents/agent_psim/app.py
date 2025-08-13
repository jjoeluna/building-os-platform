# =============================================================================
# BuildingOS Platform - Agent PSIM (Physical Security Information Management)
# =============================================================================
#
# **Purpose:** Integrates with building PSIM systems for security operations
# **Scope:** Handles security system operations, person search, and access control
# **Usage:** Invoked by SNS when Coordinator Agent distributes PSIM-related tasks
#
# **Key Features:**
# - Receives security task assignments from Agent Coordinator
# - Interfaces with building PSIM systems via REST APIs
# - Executes security operations (person search, access control, monitoring)
# - Maintains session authentication for persistent PSIM connections
# - Reports task completion results back to coordination layer
# - Uses common utilities layer for AWS client management
#
# **Event Flow (Incoming - Tasks):**
# 1. Agent Coordinator distributes tasks → coordinator_task_topic
# 2. This Lambda receives PSIM-specific security tasks
# 3. Interfaces with PSIM systems via authenticated API calls
# 4. Executes security operations and monitors completion
#
# **Event Flow (Outgoing - Results):**
# 1. PSIM operations complete (success/failure)
# 2. Task results formatted with security operation details
# 3. Published to agent_task_result_topic → Agent Coordinator
# 4. Coordinator aggregates results for mission completion
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - SNS topics for event-driven communication
# - Building PSIM system APIs with username/password authentication
# - HTTP client with persistent session management
#
# **Integration:**
# - Triggers: SNS coordinator_task_topic (PSIM tasks only), API Gateway
# - Publishes to: agent_task_result_topic
# - External APIs: Building PSIM systems (authenticated sessions)
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
#
# =============================================================================

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# HTTP client for PSIM system integration with session management
import requests

# Import common utilities from Lambda layer
from aws_clients import get_sns_client
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
    serialize_dynamodb_item,
)
from models import SNSMessage, TaskResult, PSIMOperation

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
PSIM_API_BASE_URL = get_required_env_var("PSIM_API_BASE_URL")
PSIM_API_USERNAME = get_required_env_var("PSIM_API_USERNAME")
PSIM_API_PASSWORD = get_required_env_var("PSIM_API_PASSWORD")
COORDINATOR_TASK_TOPIC_ARN = get_required_env_var("COORDINATOR_TASK_TOPIC_ARN")
AGENT_TASK_RESULT_TOPIC_ARN = get_required_env_var("AGENT_TASK_RESULT_TOPIC_ARN")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
sns_client = get_sns_client()

# Initialize persistent HTTP session for PSIM authentication
session = requests.Session()

# Validate event-driven architecture configuration
logger.info(
    "Agent PSIM initialized with security system integration",
    extra={
        "psim_api_base_url": PSIM_API_BASE_URL,
        "psim_api_username": PSIM_API_USERNAME,
        "coordinator_task_topic": COORDINATOR_TASK_TOPIC_ARN,
        "agent_task_result_topic": AGENT_TASK_RESULT_TOPIC_ARN,
        "environment": ENVIRONMENT,
        "session_management": "enabled",
        "authentication": "username/password",
    },
)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Agent PSIM Main Handler with enhanced security system integration.

    Handles PSIM security operations in the BuildingOS event-driven architecture.
    Interfaces with building security systems via authenticated REST APIs.

    Args:
        event: Event data from various sources
            SNS Events:
            - coordinator_task_topic: PSIM security tasks from Agent Coordinator
            API Gateway Events:
            - GET/POST: Direct PSIM operations (testing/debugging)
            Legacy Events:
            - Direct Lambda invocation for backward compatibility
        context: Lambda runtime context information

    Returns:
        dict: Response appropriate to event source
            SNS: Task completion status with PSIM operation results
            API Gateway: HTTP response with CORS headers
            Legacy: Task execution status

    Event Routing:
        1. SNS Events → PSIM security task execution
        2. API Gateway → Direct PSIM operations
        3. Legacy → Direct task invocation
        4. Unknown → Error response with details

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "Agent PSIM processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "event_keys": list(event.keys()),
        },
    )

    try:
        # Route based on event source with enhanced validation
        if "httpMethod" in event:
            return _handle_api_gateway_events(event, context, correlation_id)
        elif "Records" in event:
            return _handle_sns_events(event, correlation_id)
        elif "mission_id" in event and "task_id" in event and "action" in event:
            return _handle_legacy_invocation(event, correlation_id)
        else:
            logger.warning(
                "Unknown event format received",
                extra={
                    "correlation_id": correlation_id,
                    "event_keys": list(event.keys()),
                },
            )
            return create_error_response(400, "Unknown event format", correlation_id)

    except Exception as e:
        logger.error(
            "Critical error in Agent PSIM handler",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        # Return appropriate error format based on event type
        if "httpMethod" in event:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps(
                    {
                        "error": "Internal server error during PSIM processing",
                        "correlation_id": correlation_id,
                    }
                ),
            }
        else:
            return create_error_response(
                500, "Internal server error during PSIM processing", correlation_id
            )


def _handle_sns_events(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Handle SNS events for PSIM task execution.

    Args:
        event: SNS event containing Records array
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Processing result with status and correlation info
    """
    try:
        records = event.get("Records", [])
        if not records:
            logger.warning(
                "No SNS records found in event",
                extra={"correlation_id": correlation_id},
            )
            return create_success_response(
                {
                    "message": "No SNS records to process",
                    "correlation_id": correlation_id,
                }
            )

        # Process first record (Lambda typically receives one at a time)
        record = records[0]
        event_source = record.get("EventSource")

        if event_source != "aws:sns":
            logger.warning(
                "Non-SNS event in Records array",
                extra={"correlation_id": correlation_id, "event_source": event_source},
            )
            return create_error_response(
                400, "Expected SNS event source", correlation_id
            )

        # Extract SNS message details
        sns_data = record.get("Sns", {})
        topic_arn = sns_data.get("TopicArn", "")
        message = sns_data.get("Message", "")
        message_id = sns_data.get("MessageId", "")

        logger.info(
            "Processing SNS event",
            extra={
                "correlation_id": correlation_id,
                "topic_arn": topic_arn,
                "message_id": message_id,
            },
        )

        # Parse message body
        try:
            message_body = json.loads(message)
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON in SNS message",
                extra={"correlation_id": correlation_id, "json_error": str(e)},
            )
            return create_error_response(
                400, "Invalid JSON in SNS message", correlation_id
            )

        # Check if this task is for PSIM agent
        if message_body.get("agent") == "agent_psim":
            return handle_task_from_sns(message_body, correlation_id)
        else:
            logger.info(
                "Task not for agent_psim, ignoring",
                extra={
                    "correlation_id": correlation_id,
                    "target_agent": message_body.get("agent"),
                },
            )
            return create_success_response(
                {
                    "status": "IGNORED",
                    "reason": "Task not for this agent",
                    "correlation_id": correlation_id,
                }
            )

    except Exception as e:
        logger.error(
            "Error processing SNS events",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
        return create_error_response(500, "Error processing SNS events", correlation_id)


def _handle_api_gateway_events(
    event: Dict[str, Any], context: Any, correlation_id: str
) -> Dict[str, Any]:
    """
    Handle API Gateway events for direct PSIM operations (legacy support).

    Args:
        event: API Gateway event with HTTP method and request data
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with appropriate status and CORS headers
    """
    logger.info(
        "Processing API Gateway request for PSIM operations",
        extra={
            "correlation_id": correlation_id,
            "http_method": event.get("httpMethod", ""),
            "path": event.get("path", ""),
        },
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return handle_api_request(event, context, correlation_id)


def _handle_legacy_invocation(
    event: Dict[str, Any], correlation_id: str
) -> Dict[str, Any]:
    """
    Handle legacy direct Lambda invocation from Coordinator Agent.

    Args:
        event: Legacy invocation event with mission/task data
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Task execution result
    """
    logger.info(
        "Processing legacy direct invocation",
        extra={
            "correlation_id": correlation_id,
            "mission_id": event.get("mission_id"),
            "task_id": event.get("task_id"),
            "action": event.get("action"),
        },
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return handle_legacy_task(event, correlation_id)


# =============================================================================
# Enhanced Function Signatures (Updated with Correlation ID Support)
# =============================================================================


def handle_task_from_sns(
    task_data: Dict[str, Any], correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle PSIM task from SNS coordinator_task_topic.

    Args:
        task_data: Task data from SNS message
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Task execution result
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing PSIM task from SNS",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return create_success_response(
        {
            "message": "PSIM task from SNS processed",
            "correlation_id": correlation_id,
        }
    )


def handle_api_request(
    event: Dict[str, Any], context: Any, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle API Gateway request for direct PSIM operations.

    Args:
        event: API Gateway event
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with PSIM operation result
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing API Gateway request",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        },
        "body": json.dumps(
            {
                "message": "API Gateway request processed",
                "correlation_id": correlation_id,
            }
        ),
    }


def handle_legacy_task(
    event: Dict[str, Any], correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle legacy direct invocation task.

    Args:
        event: Legacy task event
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Task execution result
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing legacy task invocation",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return create_success_response(
        {
            "message": "Legacy task processed",
            "correlation_id": correlation_id,
        }
    )


# =============================================================================
# Legacy Function Implementations (To be enhanced in subsequent iterations)
# =============================================================================


def handle_task_from_sns(task_data):
    """
    Handle task from Coordinator Agent via NEW SNS architecture
    """
    try:
        # Extract task information
        mission_id = task_data["mission_id"]
        task_id = task_data["task_id"]
        action = task_data["action"]
        parameters = task_data["parameters"]

        print(f"Processing SNS task {task_id} for mission {mission_id}: {action}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        # Publish task completion using new architecture
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        print(f"Error processing SNS task: {str(e)}")

        # Try to publish failure if we have the required info
        try:
            mission_id = task_data.get("mission_id")
            task_id = task_data.get("task_id")
            if mission_id and task_id:
                publish_task_completion(
                    mission_id, task_id, "failed", {"error": str(e)}
                )
        except Exception as pub_error:
            print(f"Error publishing failure: {str(pub_error)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def handle_legacy_task(event):
    """
    Handle task from direct Lambda invocation (LEGACY architecture)
    """
    try:
        # Extract task information from direct event
        mission_id = event["mission_id"]
        task_id = event["task_id"]
        action = event["action"]
        parameters = event["parameters"]

        print(f"Processing LEGACY task {task_id} for mission {mission_id}: {action}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        # Publish task completion using legacy architecture
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        print(f"Error processing legacy task: {str(e)}")

        # Try to publish failure if we have the required info
        try:
            mission_id = event.get("mission_id")
            task_id = event.get("task_id")
            if mission_id and task_id:
                publish_task_completion(
                    mission_id, task_id, "failed", {"error": str(e)}
                )
        except Exception as pub_error:
            print(f"Error publishing failure: {str(pub_error)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def handle_api_request_legacy(event, context):
    """
    Handle direct API Gateway request for debugging/testing (legacy - renamed to avoid conflict)
    """
    try:
        # Add CORS headers
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        }

        # Handle OPTIONS requests for CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CORS preflight response"}),
            }

        # Parse request body
        if "body" not in event or not event["body"]:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Request body is required"}),
            }

        body = json.loads(event["body"])

        # Validate required fields
        if "action" not in body:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing required field: action"}),
            }

        action = body["action"]
        parameters = body.get("parameters", {})

        print(f"Processing API request - Action: {action}, Parameters: {parameters}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(
                {
                    "message": f"PSIM action '{action}' completed successfully",
                    "action": action,
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid JSON in request body"}),
        }
    except Exception as e:
        print(f"Error in API request: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }


def execute_psim_action(action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute PSIM action based on the action type
    """
    if action == "get_person_info":
        return get_person_info(parameters.get("person_name"))
    elif action == "search_person":
        return search_person(parameters.get("query"))
    else:
        raise ValueError(f"Unknown PSIM action: {action}")


def get_person_info(person_name: str) -> Dict[str, Any]:
    """
    Get person information from PSIM API
    """
    try:
        # Authenticate first
        if not authenticate():
            return {
                "status": "error",
                "message": "Failed to authenticate with PSIM API",
            }

        # Search for person
        search_url = f"{PSIM_API_BASE_URL}/api/person/search"
        search_params = {"query": person_name}

        print(f"Searching for person: {person_name}")

        response = session.get(search_url, params=search_params, timeout=10)

        if response.status_code == 200:
            search_results = response.json()
            print(f"PSIM search response: {search_results}")

            if search_results and len(search_results) > 0:
                # Get detailed info for first match
                person_id = search_results[0].get("id")
                return get_person_details(person_id)
            else:
                return {
                    "status": "not_found",
                    "message": f"No person found with name: {person_name}",
                }
        else:
            error_msg = f"PSIM API search returned status {response.status_code}: {response.text}"
            print(error_msg)

            return {"status": "error", "message": error_msg}

    except requests.RequestException as e:
        error_msg = f"Network error calling PSIM API: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error in PSIM call: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}


def get_person_details(person_id: str) -> Dict[str, Any]:
    """
    Get detailed person information by ID
    """
    try:
        details_url = f"{PSIM_API_BASE_URL}/api/person/{person_id}"

        response = session.get(details_url, timeout=10)

        if response.status_code == 200:
            person_details = response.json()

            return {
                "status": "success",
                "message": f"Person details retrieved successfully",
                "person_info": person_details,
            }
        else:
            error_msg = f"PSIM API details returned status {response.status_code}: {response.text}"
            print(error_msg)

            return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = f"Error getting person details: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}


def search_person(query: str) -> Dict[str, Any]:
    """
    Search for people in PSIM
    """
    try:
        # Authenticate first
        if not authenticate():
            return {
                "status": "error",
                "message": "Failed to authenticate with PSIM API",
            }

        search_url = f"{PSIM_API_BASE_URL}/api/person/search"
        search_params = {"query": query}

        print(f"Searching PSIM with query: {query}")

        response = session.get(search_url, params=search_params, timeout=10)

        if response.status_code == 200:
            search_results = response.json()

            return {
                "status": "success",
                "message": f"Search completed successfully",
                "results": search_results,
                "count": len(search_results) if search_results else 0,
            }
        else:
            error_msg = f"PSIM API search returned status {response.status_code}: {response.text}"
            print(error_msg)

            return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = f"Error in PSIM search: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}


def authenticate() -> bool:
    """
    Authenticate with PSIM API
    """
    try:
        auth_url = f"{PSIM_API_BASE_URL}/api/auth/login"
        auth_data = {"username": PSIM_API_USERNAME, "password": PSIM_API_PASSWORD}

        response = session.post(auth_url, json=auth_data, timeout=10)

        if response.status_code == 200:
            print("PSIM authentication successful")
            return True
        else:
            print(
                f"PSIM authentication failed: {response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        print(f"Error during PSIM authentication: {str(e)}")
        return False


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
            "agent": "agent_psim",
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
        print(f"Error publishing task completion: {str(e)}")
        # Don't raise here to avoid infinite loops
