import json
import os
import uuid
import time
import boto3
from decimal import Decimal

# Initialize AWS clients outside the handler for better performance
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

# Get table and topic names from environment variables set by Terraform
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
MISSION_RESULT_TOPIC_ARN = os.environ.get("MISSION_RESULT_TOPIC_ARN")


def decimal_to_native(obj):
    """
    Convert DynamoDB Decimal types to native Python types for JSON serialization
    """
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_native(item) for item in obj]
    else:
        return obj


def handler(event, context):
    """
    Handles user interactions, mission results, and conversation retrieval.

    Supports three types of events:
    1. API Gateway POST requests (new user messages)
    2. API Gateway GET requests (conversation retrieval)
    3. SNS events (mission results from mission_result_topic)
    """
    print(f"Persona Agent invoked with event: {event}")

    try:
        # Check if this is an SNS event (mission result)
        if "Records" in event:
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    return handle_mission_result(record["Sns"]["Message"])

        # Check if this is a GET request for conversation history
        if event.get("httpMethod") == "GET":
            return handle_get_conversation(event, context)

        # Otherwise, handle as API Gateway POST request (new user message)
        return handle_user_message(event, context)

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps({"error": "An internal error occurred."}),
        }


def handle_get_conversation(event, context):
    """
    Handle GET request to retrieve conversation history
    """
    try:
        # Get query parameters
        query_params = event.get("queryStringParameters") or {}
        user_id = query_params.get("user_id")
        session_id = query_params.get("session")

        if not user_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps({"error": "user_id is required"}),
            }

        table = dynamodb.Table(TABLE_NAME)

        if session_id:
            # Get specific session conversation
            response = table.scan(
                FilterExpression="UserId = :user_id AND SessionId = :session_id",
                ExpressionAttributeValues={
                    ":user_id": user_id,
                    ":session_id": session_id,
                },
            )
        else:
            # Get all conversations for user
            response = table.scan(
                FilterExpression="UserId = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
                Limit=50,
            )

        messages = response.get("Items", [])

        # Sort messages by timestamp
        messages = sorted(messages, key=lambda x: x.get("Timestamp", 0))

        # Convert Decimal types to native Python types for JSON serialization
        messages = decimal_to_native(messages)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps(
                {"messages": messages, "user_id": user_id, "session_id": session_id}
            ),
        }

    except Exception as e:
        print(f"Error retrieving conversation: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps({"error": "Failed to retrieve conversation"}),
        }


def handle_mission_result(message):
    """
    Handle mission result from SNS
    """
    try:
        mission_result = json.loads(message)
        mission_id = mission_result.get("mission_id")
        user_id = mission_result.get("user_id")
        status = mission_result.get("status")
        tasks = mission_result.get("tasks", [])

        print(
            f"Received mission result for mission {mission_id}, user {user_id}, status: {status}"
        )

        # Save the mission result as an assistant response in DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        timestamp = int(time.time())
        expires_at = timestamp + (24 * 60 * 60)  # TTL for 24 hours

        # Create a user-friendly response based on the mission result
        if status == "completed":
            # Extract results from successful tasks
            successful_results = []
            for task in tasks:
                if task.get("status") == "completed" and task.get("result"):
                    task_result = task["result"]
                    if isinstance(task_result, dict):
                        if task_result.get("status") == "success":
                            successful_results.append(
                                task_result.get(
                                    "message", "Task completed successfully"
                                )
                            )
                        else:
                            successful_results.append(
                                f"Task completed with issues: {task_result.get('message', 'Unknown issue')}"
                            )

            if successful_results:
                assistant_message = f"Mission completed successfully! Results: {'; '.join(successful_results)}"
            else:
                assistant_message = "Mission completed successfully!"
        elif status == "notification":
            # Handle notification messages (e.g., elevator arrival)
            notification_message = mission_result.get(
                "message", "Notification received"
            )
            assistant_message = notification_message
        else:
            assistant_message = f"Mission failed to complete. Status: {status}"

        # Find the original session ID from recent conversations
        # Look for the most recent user message from this user to get the session
        table = dynamodb.Table(TABLE_NAME)
        response = table.scan(
            FilterExpression="UserId = :user_id AND #role = :role",
            ExpressionAttributeNames={"#role": "Role"},
            ExpressionAttributeValues={":user_id": user_id, ":role": "user"},
            Limit=50,
        )

        # Find the most recent session for this user (within the last hour to be relevant)
        original_session_id = None
        current_time = int(time.time())
        one_hour_ago = current_time - 3600  # 1 hour ago

        if response["Items"]:
            # Sort by timestamp to get most recent
            sorted_items = sorted(
                response["Items"], key=lambda x: x["Timestamp"], reverse=True
            )
            # Look for a session within the last hour
            for item in sorted_items:
                if item["Timestamp"] >= one_hour_ago:
                    original_session_id = item.get("SessionId")
                    break

        if not original_session_id:
            # If no recent session found, create a new one
            original_session_id = f"session-{uuid.uuid4()}"

        # Save assistant response to conversation history using original session
        conversation_item = {
            "SessionId": original_session_id,
            "UserId": user_id,
            "Timestamp": timestamp,
            "Role": "assistant",
            "Message": assistant_message,
            "MissionId": mission_id,
            "MissionStatus": status,
            "ExpiresAt": expires_at,
        }

        table.put_item(Item=conversation_item)
        print(f"Saved mission result to conversation history for user {user_id}")

        return {"status": "SUCCESS", "message": "Mission result processed"}

    except Exception as e:
        print(f"Error processing mission result: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_user_message(event, context):
    """
    Handle new user message from API Gateway (original functionality)
    """
    # 1. Parse input from API Gateway
    body = json.loads(event.get("body", "{}"))
    user_id = body.get("user_id")
    user_message = body.get("message")
    session_id = body.get("session_id")  # Optional: for continuing a conversation

    if not user_id or not user_message:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps({"error": "user_id and message are required"}),
        }

    # 2. Manage Conversation State
    if not session_id:
        session_id = f"session-{uuid.uuid4()}"
    else:
        # Load previous conversation state from DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={"SessionId": session_id})
        item = response.get("Item")

        if item:
            # Check if the session has expired
            current_time = int(time.time())
            if current_time > item["ExpiresAt"]:
                # Session expired, create a new one
                session_id = f"session-{uuid.uuid4()}"
        # If session doesn't exist, we'll continue with the provided session_id
        # and create a new session entry

    table = dynamodb.Table(TABLE_NAME)
    timestamp = int(time.time())

    # TTL for 24 hours
    expires_at = timestamp + (24 * 60 * 60)

    conversation_item = {
        "SessionId": session_id,
        "UserId": user_id,
        "Timestamp": timestamp,
        "Role": "user",
        "Message": user_message,
        "ExpiresAt": expires_at,
    }

    # Save the user's message to DynamoDB
    table.put_item(Item=conversation_item)
    print(f"Saved user message to DynamoDB with SessionId: {session_id}")

    # 3. Publish Intention to SNS (for now, a simple passthrough)
    intention_manifest = {
        "session_id": session_id,
        "user_id": user_id,
        "message": user_message,
        "conversation_history": [
            conversation_item
        ],  # In a real scenario, you'd load previous turns
    }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(intention_manifest),
        MessageStructure="string",
    )
    print(f"Published intention to SNS for SessionId: {session_id}")

    # 4. Return a response to the user
    return {
        "statusCode": 202,  # 202 Accepted: The request has been accepted for processing
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        },
        "body": json.dumps(
            {
                "message": "Request received. The Director is analyzing the intention.",
                "session_id": session_id,
            }
        ),
    }
