import json
import os
import boto3
import uuid
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
TASK_COMPLETION_TOPIC_ARN = os.environ["TASK_COMPLETION_TOPIC_ARN"]
MISSION_RESULT_TOPIC_ARN = os.environ["MISSION_RESULT_TOPIC_ARN"]

# DynamoDB table
mission_table = dynamodb.Table(MISSION_STATE_TABLE_NAME)


def handler(event, context):
    """
    Coordinator Agent - Manages mission state and orchestrates task execution

    Handles two types of events:
    1. Mission from Director Agent (SNS from mission_topic)
    2. Task completion from Agent Tools (SNS from task_completion_topic)
    """
    try:
        print(f"Received event: {json.dumps(event)}")

        # Check if this is an SNS event
        if "Records" in event:
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    message_body = json.loads(record["Sns"]["Message"])

                    # Determine event type based on message structure
                    if "mission_id" in message_body and "tasks" in message_body:
                        # This is a new mission from Director
                        return handle_new_mission(message_body)
                    elif "task_id" in message_body and "result" in message_body:
                        # This is a task completion
                        return handle_task_completion(message_body)
                    elif (
                        "notification_type" in message_body
                        and "mission_id" in message_body
                    ):
                        # This is a monitoring notification from an agent
                        return handle_monitoring_notification(message_body)

        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid event format"}),
        }

    except Exception as e:
        print(f"Error in coordinator agent: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


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
            # Publish final result
            publish_mission_result(mission)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Task {task_id} completed"}),
        }

    except Exception as e:
        print(f"Error handling task completion: {str(e)}")
        raise


def dispatch_task_to_agent(mission_id: str, task: Dict[str, Any]) -> None:
    """
    Dispatch a task to the appropriate agent based on task type
    """
    agent_name = task["agent"]
    task_message = {
        "mission_id": mission_id,
        "task_id": task["task_id"],
        "action": task["action"],
        "parameters": task["parameters"],
    }

    # Map agent names to their specific topics/triggers
    # For now, we'll publish to a general task completion topic
    # In a more advanced setup, each agent would have its own topic

    # Since we're using individual Lambda agents, we can invoke them directly
    # or use separate topics. For simplicity, let's use direct Lambda invocation

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
            print(f"Dispatched task {task['task_id']} to {agent_name}")

            # Update task status to 'in_progress'
            update_task_status(mission_id, task["task_id"], "in_progress")

        except Exception as e:
            print(f"Error dispatching task to {agent_name}: {str(e)}")
            # Update task status to 'failed'
            update_task_status(mission_id, task["task_id"], "failed")
    else:
        print(f"Unknown agent: {agent_name}")
        update_task_status(mission_id, task["task_id"], "failed")


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


def publish_mission_result(mission: Dict[str, Any]) -> None:
    """
    Publish final mission result to mission_result_topic
    """
    try:
        # Update mission status
        mission_id = mission["mission_id"]

        # Determine overall mission status
        failed_tasks = [
            task for task in mission["tasks"] if task.get("status") == "failed"
        ]
        overall_status = "failed" if failed_tasks else "completed"

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

        # Publish to mission result topic
        sns.publish(
            TopicArn=MISSION_RESULT_TOPIC_ARN,
            Message=json.dumps(result_message, default=decimal_default),
            Subject=f"Mission {mission_id} Complete",
        )

        print(f"Published mission result for {mission_id}")

    except Exception as e:
        print(f"Error publishing mission result: {str(e)}")
        raise


def handle_monitoring_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle monitoring notifications from agents (e.g., elevator arrival notifications)
    Forwards these notifications to the Mission Result Topic for the user
    """
    try:
        mission_id = notification_data["mission_id"]
        notification_type = notification_data["notification_type"]
        message = notification_data["message"]

        print(
            f"Received monitoring notification for mission {mission_id}: {notification_type}"
        )

        # Get mission data from DynamoDB to get user_id
        response = mission_table.get_item(Key={"mission_id": mission_id})

        if "Item" not in response:
            print(f"Mission {mission_id} not found in DynamoDB")
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Mission {mission_id} not found"}),
            }

        mission = response["Item"]

        # Prepare notification message for user
        user_notification = {
            "mission_id": mission_id,
            "user_id": mission["user_id"],
            "notification_type": notification_type,
            "message": message,
            "timestamp": notification_data.get(
                "timestamp", datetime.now(timezone.utc).isoformat()
            ),
            "agent": notification_data.get("agent", "unknown"),
            "status": "notification",  # Distinguish from mission completion
        }

        # Publish to mission result topic so the user gets the notification
        sns.publish(
            TopicArn=MISSION_RESULT_TOPIC_ARN,
            Message=json.dumps(user_notification, default=decimal_default),
            Subject=f"Notification for Mission {mission_id}",
        )

        print(f"Forwarded monitoring notification for mission {mission_id} to user")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Notification forwarded successfully"}),
        }

    except Exception as e:
        print(f"Error handling monitoring notification: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
