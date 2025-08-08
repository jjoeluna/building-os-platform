import json
import os
import boto3
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from decimal import Decimal


# Helper function to handle Decimal serialization
def decimal_default(obj):
    """Helper function to serialize Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


# AWS clients
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

# Environment variables
MISSION_STATE_TABLE_NAME = os.environ["MISSION_STATE_TABLE_NAME"]

# New standardized topics
COORDINATOR_TASK_TOPIC_ARN = os.environ.get("COORDINATOR_TASK_TOPIC_ARN")
AGENT_TASK_RESULT_TOPIC_ARN = os.environ.get("AGENT_TASK_RESULT_TOPIC_ARN")
COORDINATOR_MISSION_RESULT_TOPIC_ARN = os.environ.get(
    "COORDINATOR_MISSION_RESULT_TOPIC_ARN"
)

# Determine which architecture to use (require new architecture)
USE_NEW_ARCHITECTURE = bool(
    COORDINATOR_TASK_TOPIC_ARN
    and AGENT_TASK_RESULT_TOPIC_ARN
    and COORDINATOR_MISSION_RESULT_TOPIC_ARN
)

if not USE_NEW_ARCHITECTURE:
    print("ERROR: New architecture topics not configured")
    raise ValueError("Required SNS topics for new architecture not available")

print("Agent Coordinator using NEW architecture (legacy support removed)")

# DynamoDB table
mission_table = dynamodb.Table(MISSION_STATE_TABLE_NAME)


def handler(event, context):
    """
    Coordinator Agent - Manages mission state and orchestrates task execution

    Supports two types of events:
    1. SNS events (missions from Director Agent, task completions from Agent Tools)
    2. API Gateway GET requests (mission status queries for debugging)
    """
    try:
        print(f"Received event: {json.dumps(event)}")

        # Check if this is an SNS event
        if "Records" in event:
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    topic_arn = record["Sns"]["TopicArn"]
                    message_body = json.loads(record["Sns"]["Message"])

                    # Determine event type based on topic and message structure
                    if (
                        "mission-topic" in topic_arn
                        or "director-mission-topic" in topic_arn
                    ):
                        # This is a new mission from Director
                        return handle_new_mission(message_body)
                    elif (
                        "task-result-topic" in topic_arn
                        or "agent-task-result-topic" in topic_arn
                    ):
                        # This is a task completion from agents
                        return handle_task_completion(message_body)
                    elif (
                        "notification_type" in message_body
                        and "mission_id" in message_body
                    ):
                        # This is a monitoring notification from an agent
                        return handle_monitoring_notification(message_body)
                    else:
                        print(
                            f"Unknown SNS event from topic {topic_arn}: {message_body}"
                        )
                        return {"status": "ERROR", "error": "Unknown event type"}

        # Handle API Gateway requests (mission status queries)
        if event.get("httpMethod") == "GET":
            return handle_api_request(event, context)

        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid event format"}),
        }

    except Exception as e:
        print(f"Error in coordinator agent: {str(e)}")
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
        print(f"Error in API request: {str(e)}")
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
        print(f"Stored mission {mission_id} in DynamoDB")

        # Dispatch tasks to agents
        for task in mission_data["tasks"]:
            dispatch_task_to_agent(mission_id, task)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Mission {mission_id} dispatched"}),
        }

    except Exception as e:
        print(f"Error handling new mission: {str(e)}")
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
        print(f"Error handling task completion: {str(e)}")
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
    Dispatch task via new SNS architecture using coordinator-task-topic
    """
    try:
        sns.publish(
            TopicArn=COORDINATOR_TASK_TOPIC_ARN,
            Message=json.dumps(task_message),
            Subject=f"Task {task_id} for {agent_name}",
            MessageAttributes={
                "agent_name": {"DataType": "String", "StringValue": agent_name},
                "task_id": {"DataType": "String", "StringValue": task_id},
            },
        )
        print(f"Dispatched task {task_id} to {agent_name} via NEW SNS architecture")

        # Update task status to 'in_progress'
        update_task_status(mission_id, task_id, "in_progress")

    except Exception as e:
        print(f"Error dispatching task via SNS to {agent_name}: {str(e)}")
        # Update task status to 'failed'
        update_task_status(mission_id, task_id, "failed")


def dispatch_task_via_lambda(
    agent_name: str, task_message: Dict[str, Any], mission_id: str, task_id: str
) -> None:
    """
    Legacy task dispatch using direct Lambda invocation
    """
    lambda_client = boto3.client("lambda")

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
            print(f"Error dispatching task to {agent_name}: {str(e)}")
            # Update task status to 'failed'
            update_task_status(mission_id, task_id, "failed")
    else:
        print(f"Unknown agent: {agent_name}")
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
        print(f"Error updating task completion: {str(e)}")
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
        print(f"Error updating task status: {str(e)}")


def get_mission(mission_id: str) -> Dict[str, Any]:
    """
    Retrieve mission from DynamoDB
    """
    try:
        response = mission_table.get_item(Key={"mission_id": mission_id})
        return response.get("Item", {})

    except Exception as e:
        print(f"Error getting mission: {str(e)}")
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
        print(f"Error publishing mission result: {str(e)}")
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
        print(f"Error publishing monitoring notification: {str(e)}")
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
        print(f"Error handling monitoring notification: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
