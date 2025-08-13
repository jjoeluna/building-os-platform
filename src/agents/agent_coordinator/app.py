# =============================================================================
# BuildingOS Platform - Agent Coordinator (Task Orchestration & Management)
# =============================================================================
#
# **Purpose:** Orchestrates task execution across specialized building system agents
# **Scope:** Central task distribution and result aggregation for mission completion
# **Usage:** Invoked by SNS when Director Agent creates missions requiring execution
#
# **Key Features:**
# - Receives mission plans from Agent Director with task breakdowns
# - Distributes individual tasks to specialized agents (Elevator, PSIM, etc.)
# - Manages task execution state and progress tracking in DynamoDB
# - Aggregates task results and reports mission completion status
# - Handles task failures and retry logic for robust mission execution
# - Uses common utilities layer for AWS client management
#
# **Event Flow (Incoming - Missions):**
# 1. Agent Director creates mission plan → director_mission_topic
# 2. This Lambda receives mission with task breakdown
# 3. Distributes tasks to appropriate specialized agents
# 4. Tracks task execution progress and handles failures
#
# **Event Flow (Incoming - Results):**
# 1. Specialized agents complete tasks → agent_task_result_topic
# 2. This Lambda receives individual task completion results
# 3. Aggregates results and checks mission completion status
# 4. Reports final results to coordinator_mission_result_topic → Agent Director
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - DynamoDB table for mission and task state tracking
# - SNS topics for event-driven communication with agents
# - Specialized agent registry for capability-based task routing
#
# **Integration:**
# - Triggers: SNS director_mission_topic, agent_task_result_topic
# - Publishes to: coordinator_task_topic, coordinator_mission_result_topic
# - Stores in: Mission state table for task progress tracking
# - Coordinates: agent_elevator, agent_psim, and other specialized agents
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
#
# =============================================================================

import json
import os
import uuid
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Import common utilities from Lambda layer
from aws_clients import get_dynamodb_resource, get_sns_client, get_lambda_client
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
    serialize_dynamodb_item,
)
from models import (
    SNSMessage,
    MissionState,
    TaskExecution,
    AgentCapability,
    convert_task_message_to_acp,
    is_acp_message,
)
from acp_protocol import ACPProtocol, AgentType, MessageType, StandardActions

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
MISSION_STATE_TABLE_NAME = get_required_env_var("MISSION_STATE_TABLE_NAME")
COORDINATOR_TASK_TOPIC_ARN = get_required_env_var("COORDINATOR_TASK_TOPIC_ARN")
AGENT_TASK_RESULT_TOPIC_ARN = get_required_env_var("AGENT_TASK_RESULT_TOPIC_ARN")
COORDINATOR_MISSION_RESULT_TOPIC_ARN = get_required_env_var(
    "COORDINATOR_MISSION_RESULT_TOPIC_ARN"
)
# ACP Standard Topics
ACP_TASK_TOPIC_ARN = get_optional_env_var("ACP_TASK_TOPIC_ARN", "")
ACP_RESULT_TOPIC_ARN = get_optional_env_var("ACP_RESULT_TOPIC_ARN", "")
ACP_EVENT_TOPIC_ARN = get_optional_env_var("ACP_EVENT_TOPIC_ARN", "")
ACP_HEARTBEAT_TOPIC_ARN = get_optional_env_var("ACP_HEARTBEAT_TOPIC_ARN", "")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
dynamodb_resource = get_dynamodb_resource()
sns_client = get_sns_client()

# Initialize DynamoDB table reference
mission_table = dynamodb_resource.Table(MISSION_STATE_TABLE_NAME)

# Initialize ACP Protocol
acp = ACPProtocol("coordinator-001", AgentType.COORDINATOR)

# Validate event-driven architecture configuration
logger.info(
    "Agent Coordinator initialized with task orchestration capabilities",
    extra={
        "mission_state_table": MISSION_STATE_TABLE_NAME,
        "coordinator_task_topic": COORDINATOR_TASK_TOPIC_ARN,
        "agent_task_result_topic": AGENT_TASK_RESULT_TOPIC_ARN,
        "coordinator_result_topic": COORDINATOR_MISSION_RESULT_TOPIC_ARN,
        # ACP Topics
        "acp_task_topic": ACP_TASK_TOPIC_ARN,
        "acp_result_topic": ACP_RESULT_TOPIC_ARN,
        "acp_event_topic": ACP_EVENT_TOPIC_ARN,
        "acp_heartbeat_topic": ACP_HEARTBEAT_TOPIC_ARN,
        "acp_protocol": "enabled",
        "environment": ENVIRONMENT,
    },
)


# Helper function to handle Decimal serialization (legacy compatibility)
def decimal_default(obj):
    """Helper function to serialize Decimal objects for JSON compatibility."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _determine_event_source(event: Dict[str, Any]) -> str:
    """
    Helper function to determine the source of an incoming event.

    Args:
        event: The Lambda event dictionary

    Returns:
        str: Event source type ('sns', 'api_gateway', 'unknown')
    """
    if "Records" in event:
        for record in event["Records"]:
            if record.get("EventSource") == "aws:sns":
                return "sns"
    elif event.get("httpMethod") == "GET":
        return "api_gateway"
    return "unknown"


def _extract_sns_message_data(record: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """
    Helper function to extract topic ARN and message data from SNS record.

    Args:
        record: SNS record from event

    Returns:
        tuple: (topic_arn, message_body)
    """
    topic_arn = record["Sns"]["TopicArn"]
    message_body = json.loads(record["Sns"]["Message"])
    return topic_arn, message_body


def _route_sns_event(topic_arn: str, message_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to route SNS events to appropriate handlers.

    Args:
        topic_arn: The SNS topic ARN
        message_body: The parsed message content

    Returns:
        dict: Handler response
    """
    # Check if this is an ACP standard message
    if is_acp_message(message_body):
        return handle_acp_message(message_body)

    # Determine event type based on topic and message structure (legacy)
    if "mission-topic" in topic_arn or "director-mission-topic" in topic_arn:
        # This is a new mission from Director
        return handle_new_mission(message_body)
    elif "task-result-topic" in topic_arn or "agent-task-result-topic" in topic_arn:
        # This is a task completion from an agent
        return handle_task_completion(message_body)
    elif "acp-task-topic" in topic_arn:
        # ACP standard task message
        return handle_acp_task(message_body)
    elif "acp-result-topic" in topic_arn:
        # ACP standard result message
        return handle_acp_result(message_body)
    elif "acp-event-topic" in topic_arn:
        # ACP standard event message
        return handle_acp_event(message_body)
    elif "notification_type" in message_body and "mission_id" in message_body:
        # This is a monitoring notification from an agent
        return handle_monitoring_notification(message_body)
    else:
        logger.warning(
            "Unknown SNS event received from unrecognized topic",
            extra={"topic_arn": topic_arn, "message": message_body},
        )
        return {"status": "ERROR", "error": "Unknown event type"}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Agent Coordinator Main Handler with enhanced task orchestration and management.

    Orchestrates task execution across specialized building system agents in the BuildingOS
    event-driven architecture. Manages mission state and aggregates task results.

    Args:
        event: Event data from various sources (SNS, API Gateway)
            SNS Events:
            - director_mission_topic: Mission plans from Agent Director
            - agent_task_result_topic: Task completion results from specialized agents
        context: Lambda runtime context information

    Returns:
        dict: Response appropriate to event source

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "Agent Coordinator processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "event_keys": list(event.keys()),
        },
    )

    try:
        # Determine event source and route accordingly
        event_source = _determine_event_source(event)

        if event_source == "sns":
            # Process SNS events using helper functions
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    topic_arn, message_body = _extract_sns_message_data(record)
                    return _route_sns_event(topic_arn, message_body)
        elif event_source == "api_gateway":
            # Handle API Gateway requests (mission status queries)
            return handle_api_request(event, context)

        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid event format"}),
        }

    except Exception as e:
        logger.error(
            "Critical error in coordinator agent handler",
            extra={"correlation_id": correlation_id, "error": str(e)},
        )
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def handle_api_request(event, context):
    """
    Handle API Gateway GET request for mission status
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

        # Extract mission_id from path parameters
        path_parameters = event.get("pathParameters", {})
        mission_id = path_parameters.get("mission_id") if path_parameters else None

        # Check if this is a general status request (no mission_id)
        path = event.get("path", "")
        if path.endswith("/coordinator/status") or not mission_id:
            # Return general coordinator status
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(
                    {
                        "status": "healthy",
                        "service": "coordinator",
                        "timestamp": int(time.time()),
                        "message": "Coordinator agent is running",
                    }
                ),
            }

        print(f"Getting mission status for: {mission_id}")

        # Get mission from DynamoDB
        mission = get_mission(mission_id)

        if not mission:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"error": f"Mission {mission_id} not found"}),
            }

        # Calculate mission statistics
        total_tasks = len(mission.get("tasks", []))
        completed_tasks = len(
            [
                task
                for task in mission.get("tasks", [])
                if task.get("status") == "completed"
            ]
        )
        failed_tasks = len(
            [
                task
                for task in mission.get("tasks", [])
                if task.get("status") == "failed"
            ]
        )
        in_progress_tasks = len(
            [
                task
                for task in mission.get("tasks", [])
                if task.get("status") == "in_progress"
            ]
        )
        pending_tasks = total_tasks - completed_tasks - failed_tasks - in_progress_tasks

        mission_status = {
            "mission_id": mission_id,
            "user_id": mission.get("user_id"),
            "status": mission.get("status", "pending"),
            "created_at": mission.get("created_at"),
            "updated_at": mission.get("updated_at"),
            "statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
            },
            "tasks": mission.get("tasks", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(mission_status, default=decimal_default),
        }

    except Exception as e:
        logger.error(
            "Error processing API request",
            extra={"mission_id": mission_id, "error": str(e)},
        )
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }


def handle_new_mission(mission_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle new mission from Director Agent
    1. Store mission in DynamoDB
    2. Dispatch tasks to appropriate agents
    """
    try:
        mission_id = mission_data["mission_id"]

        # Store mission in DynamoDB
        mission_table.put_item(Item=mission_data)
        logger.info(
            "Mission stored successfully in DynamoDB", extra={"mission_id": mission_id}
        )

        # Dispatch tasks to agents
        for task in mission_data["tasks"]:
            dispatch_task_to_agent(mission_id, task)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Mission {mission_id} dispatched"}),
        }

    except Exception as e:
        logger.error(
            "Error handling new mission",
            extra={"mission_id": mission_id, "error": str(e)},
        )
        raise


def handle_task_completion(completion_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle task completion from Agent Tools
    1. Update task status in DynamoDB
    2. Check if mission is complete
    3. If complete, publish result
    """
    try:
        mission_id = completion_data["mission_id"]
        task_id = completion_data["task_id"]

        # Update task in DynamoDB
        update_task_completion(mission_id, task_id, completion_data)

        # Check if mission is complete
        mission = get_mission(mission_id)
        if is_mission_complete(mission):
            # Determine overall mission status
            failed_tasks = [
                task for task in mission["tasks"] if task.get("status") == "failed"
            ]
            overall_status = "failed" if failed_tasks else "completed"

            # Publish final result
            publish_mission_result(mission, overall_status)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Task {task_id} completed"}),
        }

    except Exception as e:
        logger.error(
            "Error handling task completion",
            extra={"task_id": completion_data.get("task_id"), "error": str(e)},
        )
        raise


def dispatch_task_to_agent(mission_id: str, task: Dict[str, Any]) -> None:
    """
    Dispatch a task to the appropriate agent using either new SNS architecture or legacy Lambda invocation
    """
    agent_name = task["agent"]
    task_message = {
        "mission_id": mission_id,
        "task_id": task["task_id"],
        "agent": agent_name,
        "action": task["action"],
        "parameters": task["parameters"],
        "status": "pending",
    }

    if USE_NEW_ARCHITECTURE:
        # Use new SNS-based architecture
        dispatch_task_via_sns(agent_name, task_message, mission_id, task["task_id"])
    else:
        # Use legacy Lambda invocation
        dispatch_task_via_lambda(agent_name, task_message, mission_id, task["task_id"])


def dispatch_task_via_sns(
    agent_name: str, task_message: Dict[str, Any], mission_id: str, task_id: str
) -> None:
    """
    Dispatch task via SNS architecture (both current and ACP standard)
    """
    try:
        # Current BuildingOS format
        sns.publish(
            TopicArn=COORDINATOR_TASK_TOPIC_ARN,
            Message=json.dumps(task_message),
            Subject=f"Task {task_id} for {agent_name}",
            MessageAttributes={
                "agent_name": {"DataType": "String", "StringValue": agent_name},
                "task_id": {"DataType": "String", "StringValue": task_id},
            },
        )
        print(f"Dispatched task {task_id} to {agent_name} via current SNS architecture")

        # ACP Standard format (if configured)
        if ACP_TASK_TOPIC_ARN:
            acp_task = acp.create_task(
                target_agent=agent_name,
                task_id=task_id,
                action=task_message.get("action", StandardActions.TASK_EXECUTE),
                parameters=task_message.get("parameters", {}),
                correlation_id=mission_id,
            )

            sns.publish(
                TopicArn=ACP_TASK_TOPIC_ARN,
                Message=acp_task.to_json(),
                Subject=f"ACP Task {task_id} for {agent_name}",
                MessageAttributes={
                    "message_type": {"DataType": "String", "StringValue": "task"},
                    "agent_name": {"DataType": "String", "StringValue": agent_name},
                    "task_id": {"DataType": "String", "StringValue": task_id},
                    "protocol": {"DataType": "String", "StringValue": "acp"},
                },
            )
            print(
                f"Dispatched ACP task {task_id} to {agent_name} via ACP standard protocol"
            )

        # Update task status to 'in_progress'
        update_task_status(mission_id, task_id, "in_progress")

    except Exception as e:
        logger.error(
            "Error dispatching task via SNS",
            extra={
                "agent_name": agent_name,
                "task_id": task_id,
                "mission_id": mission_id,
                "error": str(e),
            },
        )
        # Update task status to 'failed'
        update_task_status(mission_id, task_id, "failed")


def dispatch_task_via_lambda(
    agent_name: str, task_message: Dict[str, Any], mission_id: str, task_id: str
) -> None:
    """
    Legacy task dispatch using direct Lambda invocation
    """
    lambda_client = get_lambda_client()

    # Map agent names to Lambda function names using environment variable
    environment = os.environ.get("ENVIRONMENT", "dev")
    function_mapping = {
        "agent_elevator": f"bos-agent-elevator-{environment}",
        "agent_psim": f"bos-agent-psim-{environment}",
    }

    function_name = function_mapping.get(agent_name)
    if function_name:
        try:
            # Invoke agent Lambda asynchronously
            lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="Event",  # Async invocation
                Payload=json.dumps(task_message),
            )
            print(
                f"Dispatched task {task_id} to {agent_name} via LEGACY Lambda invocation"
            )

            # Update task status to 'in_progress'
            update_task_status(mission_id, task_id, "in_progress")

        except Exception as e:
            logger.error(
                "Error dispatching task via Lambda",
                extra={
                    "agent_name": agent_name,
                    "task_id": task_id,
                    "mission_id": mission_id,
                    "error": str(e),
                },
            )
            # Update task status to 'failed'
            update_task_status(mission_id, task_id, "failed")
    else:
        logger.warning(
            "Unknown agent requested for task dispatch",
            extra={
                "agent_name": agent_name,
                "task_id": task_id,
                "mission_id": mission_id,
            },
        )
        update_task_status(mission_id, task_id, "failed")


def update_task_completion(
    mission_id: str, task_id: str, completion_data: Dict[str, Any]
) -> None:
    """
    Update task completion in DynamoDB
    """
    try:
        # First, get the current mission to find the task index
        response = mission_table.get_item(Key={"mission_id": mission_id})
        mission = response.get("Item", {})

        if not mission or "tasks" not in mission:
            print(f"Mission {mission_id} not found")
            return

        # Find the task index
        task_index = None
        for i, task in enumerate(mission["tasks"]):
            if task["task_id"] == task_id:
                task_index = i
                break

        if task_index is None:
            print(f"Task {task_id} not found in mission {mission_id}")
            return

        # Update the specific task
        mission_table.update_item(
            Key={"mission_id": mission_id},
            UpdateExpression=f"SET tasks[{task_index}].#status = :status, tasks[{task_index}].#result = :result, tasks[{task_index}].completed_at = :completed_at, updated_at = :updated_at",
            ExpressionAttributeNames={"#status": "status", "#result": "result"},
            ExpressionAttributeValues={
                ":status": completion_data["status"],
                ":result": completion_data["result"],
                ":completed_at": datetime.now(timezone.utc).isoformat(),
                ":updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        print(f"Updated task {task_id} status to {completion_data['status']}")

    except Exception as e:
        logger.error(
            "Error updating task completion in DynamoDB",
            extra={"mission_id": mission_id, "task_id": task_id, "error": str(e)},
        )
        raise


def update_task_status(mission_id: str, task_id: str, status: str) -> None:
    """
    Update task status in DynamoDB
    """
    try:
        # Get the current mission to find the task index
        response = mission_table.get_item(Key={"mission_id": mission_id})
        mission = response.get("Item", {})

        if not mission or "tasks" not in mission:
            print(f"Mission {mission_id} not found")
            return

        # Find the task index
        task_index = None
        for i, task in enumerate(mission["tasks"]):
            if task["task_id"] == task_id:
                task_index = i
                break

        if task_index is None:
            print(f"Task {task_id} not found in mission {mission_id}")
            return

        # Update the task status
        update_expression = (
            f"SET tasks[{task_index}].#status = :status, updated_at = :updated_at"
        )
        expression_attribute_values = {
            ":status": status,
            ":updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Add started_at timestamp if status is 'in_progress'
        if status == "in_progress":
            update_expression += f", tasks[{task_index}].started_at = :started_at"
            expression_attribute_values[":started_at"] = datetime.now(
                timezone.utc
            ).isoformat()

        mission_table.update_item(
            Key={"mission_id": mission_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues=expression_attribute_values,
        )

        print(f"Updated task {task_id} status to {status}")

    except Exception as e:
        logger.error(
            "Error updating task status in DynamoDB",
            extra={
                "mission_id": mission_id,
                "task_id": task_id,
                "status": status,
                "error": str(e),
            },
        )


def get_mission(mission_id: str) -> Dict[str, Any]:
    """
    Retrieve mission from DynamoDB
    """
    try:
        response = mission_table.get_item(Key={"mission_id": mission_id})
        return response.get("Item", {})

    except Exception as e:
        logger.error(
            "Error retrieving mission from DynamoDB",
            extra={"mission_id": mission_id, "error": str(e)},
        )
        raise


def is_mission_complete(mission: Dict[str, Any]) -> bool:
    """
    Check if all tasks in the mission are complete
    """
    if not mission or "tasks" not in mission:
        return False

    for task in mission["tasks"]:
        if task.get("status") not in ["completed", "failed"]:
            return False

    return True


def publish_mission_result(mission: Dict[str, Any], overall_status: str) -> None:
    """
    Publish mission completion result using appropriate architecture
    """
    mission_id = mission["mission_id"]

    # Update mission in DynamoDB
    mission_table.update_item(
        Key={"mission_id": mission_id},
        UpdateExpression="SET #status = :status, updated_at = :updated_at",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": overall_status,
            ":updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Prepare result message
    result_message = {
        "mission_id": mission_id,
        "user_id": mission["user_id"],
        "status": overall_status,
        "tasks": mission["tasks"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    if USE_NEW_ARCHITECTURE:
        # Use new coordinator-mission-result-topic
        topic_arn = COORDINATOR_MISSION_RESULT_TOPIC_ARN
        print(
            f"Publishing mission result via NEW architecture to coordinator-mission-result-topic"
        )
    else:
        # Should not happen - new architecture is required
        print("ERROR: New architecture required but topics not available")
        raise ValueError("COORDINATOR_MISSION_RESULT_TOPIC_ARN not configured")

    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(result_message, default=decimal_default),
            Subject=f"Mission {mission_id} Complete",
        )
        print(f"Published mission result for {mission_id}")
    except Exception as e:
        logger.error(
            "Error publishing mission result to SNS",
            extra={"mission_id": mission_id, "topic_arn": topic_arn, "error": str(e)},
        )
        raise


def publish_monitoring_notification(notification_data: Dict[str, Any]) -> None:
    """
    Publish monitoring notification using appropriate architecture
    """
    mission_id = notification_data["mission_id"]
    notification_type = notification_data["notification_type"]
    message = notification_data["message"]

    user_notification = {
        "mission_id": mission_id,
        "user_id": notification_data.get("user_id", "unknown"),
        "notification_type": notification_type,
        "message": message,
        "timestamp": notification_data.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),
        "agent": notification_data.get("agent", "unknown"),
        "status": "notification",  # Distinguish from mission completion
    }

    if USE_NEW_ARCHITECTURE:
        # Use new coordinator-mission-result-topic for notifications too
        topic_arn = COORDINATOR_MISSION_RESULT_TOPIC_ARN
        print(
            f"Publishing notification via NEW architecture to coordinator-mission-result-topic"
        )
    else:
        # Should not happen - new architecture is required
        print("ERROR: New architecture required but topics not available")
        raise ValueError("COORDINATOR_MISSION_RESULT_TOPIC_ARN not configured")

    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(user_notification, default=decimal_default),
            Subject=f"Notification for Mission {mission_id}",
        )
        print(f"Forwarded monitoring notification for mission {mission_id} to user")
    except Exception as e:
        logger.error(
            "Error publishing monitoring notification to SNS",
            extra={"mission_id": notification_data.get("mission_id"), "error": str(e)},
        )
        raise


def handle_monitoring_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle monitoring notifications from agents (e.g., elevator arrival notifications)
    Forwards these notifications to users using appropriate architecture
    """
    try:
        mission_id = notification_data["mission_id"]
        notification_type = notification_data["notification_type"]
        message = notification_data["message"]

        print(
            f"Handling monitoring notification for mission {mission_id}: {notification_type}"
        )

        # Forward the notification to users
        publish_monitoring_notification(notification_data)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Notification forwarded successfully"}),
        }

    except Exception as e:
        logger.error(
            "Error handling monitoring notification",
            extra={"mission_id": notification_data.get("mission_id"), "error": str(e)},
        )
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# =============================================================================
# ACP Standard Message Handlers
# =============================================================================


def handle_acp_message(message_body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ACP standard format messages"""
    try:
        acp_message = acp.validate_message(message_body)

        if acp_message.header.message_type == MessageType.TASK:
            return handle_acp_task(message_body)
        elif acp_message.header.message_type == MessageType.RESULT:
            return handle_acp_result(message_body)
        elif acp_message.header.message_type == MessageType.EVENT:
            return handle_acp_event(message_body)
        else:
            logger.warning(
                f"Unsupported ACP message type: {acp_message.header.message_type}"
            )
            return {
                "status": "ERROR",
                "error": f"Unsupported ACP message type: {acp_message.header.message_type}",
            }

    except Exception as e:
        logger.error(f"Error processing ACP message: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_acp_task(message_body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ACP standard task messages"""
    try:
        acp_message = acp.validate_message(message_body)
        task_data = acp_message.payload.data

        logger.info(
            "Processing ACP standard task",
            extra={
                "task_id": task_data.get("task_id"),
                "target_agent": acp_message.header.target_agent,
                "action": acp_message.payload.action,
            },
        )

        # Convert ACP task to current format and process
        legacy_task = {
            "task_id": task_data.get("task_id"),
            "mission_id": acp_message.header.correlation_id,
            "agent": acp_message.header.target_agent,
            "action": acp_message.payload.action,
            "parameters": task_data.get("parameters", {}),
            "status": "pending",
        }

        # Process using existing mission handling logic
        return handle_new_mission(
            {"mission_id": acp_message.header.correlation_id, "tasks": [legacy_task]}
        )

    except Exception as e:
        logger.error(f"Error handling ACP task: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_acp_result(message_body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ACP standard result messages"""
    try:
        acp_message = acp.validate_message(message_body)
        result_data = acp_message.payload.data

        logger.info(
            "Processing ACP standard result",
            extra={
                "task_id": result_data.get("task_id"),
                "source_agent": acp_message.header.source_agent,
                "status": acp_message.status,
            },
        )

        # Convert ACP result to current format and process
        legacy_result = {
            "task_id": result_data.get("task_id"),
            "mission_id": acp_message.header.correlation_id,
            "agent": acp_message.header.source_agent,
            "success": acp_message.status == "completed",
            "result": result_data.get("result", {}),
            "timestamp": (
                acp_message.header.timestamp.isoformat()
                if hasattr(acp_message.header.timestamp, "isoformat")
                else str(acp_message.header.timestamp)
            ),
        }

        # Process using existing task completion logic
        return handle_task_completion(legacy_result)

    except Exception as e:
        logger.error(f"Error handling ACP result: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_acp_event(message_body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ACP standard event messages"""
    try:
        acp_message = acp.validate_message(message_body)

        logger.info(
            "Processing ACP standard event",
            extra={
                "event_action": acp_message.payload.action,
                "source_agent": acp_message.header.source_agent,
                "event_data": acp_message.payload.data,
            },
        )

        # Process event based on action
        if acp_message.payload.action == "mission_status_update":
            # Handle mission status updates
            return handle_monitoring_notification(acp_message.payload.data)
        else:
            logger.info(f"ACP event processed: {acp_message.payload.action}")
            return {"status": "SUCCESS", "message": "ACP event processed"}

    except Exception as e:
        logger.error(f"Error handling ACP event: {str(e)}")
        return {"status": "ERROR", "error": str(e)}
