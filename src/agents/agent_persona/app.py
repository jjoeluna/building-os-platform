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
TABLE_NAME = os.environ.get("SHORT_TERM_MEMORY_TABLE_NAME")

# New standardized topics
PERSONA_INTENTION_TOPIC_ARN = os.environ.get("PERSONA_INTENTION_TOPIC_ARN")
DIRECTOR_RESPONSE_TOPIC_ARN = os.environ.get("DIRECTOR_RESPONSE_TOPIC_ARN")
PERSONA_RESPONSE_TOPIC_ARN = os.environ.get("PERSONA_RESPONSE_TOPIC_ARN")

# Determine which architecture to use (require new architecture)
USE_NEW_ARCHITECTURE = bool(PERSONA_INTENTION_TOPIC_ARN)

if not USE_NEW_ARCHITECTURE:
    print("ERROR: New architecture topics not configured")
    raise ValueError("Required SNS topics for new architecture not available")

print("Agent Persona using NEW architecture (legacy support removed)")


def decimal_default(obj):
    """JSON serializer function that handles Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


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
        # Route based on event source
        if "Records" in event and event["Records"][0].get("EventSource") == "aws:sns":
            # Handle SNS event
            record = event["Records"][0]
            topic_arn = record["Sns"]["TopicArn"]
            message = record["Sns"]["Message"]

            if "director-response-topic" in topic_arn:
                return handle_director_response(message)
            elif "chat-intention-topic" in topic_arn:
                return handle_chat_intention(message)
            else:
                print(f"Unknown SNS topic: {topic_arn}")
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Unknown SNS topic"}),
                }

        elif "httpMethod" in event:
            # Handle API Gateway event
            if event["httpMethod"] == "GET":
                return handle_get_conversation(event, context)
            elif event["httpMethod"] == "POST":
                return handle_user_message(event, context)
            else:
                return {
                    "statusCode": 405,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps(
                        {"error": f"Unsupported method {event['httpMethod']}"}
                    ),
                }

        else:
            # Fallback for unknown event types
            print(f"Unknown event format: {event}")
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Invalid event format"}),
            }

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
                FilterExpression="user_id = :user_id AND SessionId = :session_id",
                ExpressionAttributeValues={
                    ":user_id": user_id,
                    ":session_id": session_id,
                },
            )
        else:
            # Get all conversations for user
            response = table.scan(
                FilterExpression="user_id = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
                Limit=50,
            )

        messages = response.get("Items", [])

        # Sort messages by timestamp
        messages = sorted(messages, key=lambda x: x.get("Timestamp", 0))

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps(
                {"messages": messages, "user_id": user_id, "session_id": session_id},
                default=decimal_default,
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
        else:
            assistant_message = f"Mission failed to complete. Status: {status}"

        # Find the original session ID from recent conversations
        # Look for the most recent user message from this user to get the session
        table = dynamodb.Table(TABLE_NAME)
        response = table.scan(
            FilterExpression="user_id = :user_id AND #role = :role",
            ExpressionAttributeNames={"#role": "Role"},
            ExpressionAttributeValues={":user_id": user_id, ":role": "user"},
            Limit=50,
        )

        # Find the most recent session for this user
        original_session_id = None
        if response["Items"]:
            # Sort by timestamp to get most recent
            sorted_items = sorted(
                response["Items"], key=lambda x: x["Timestamp"], reverse=True
            )
            original_session_id = sorted_items[0].get("SessionId")

        if not original_session_id:
            original_session_id = f"session-{uuid.uuid4()}"

        # Save assistant response to conversation history using original session
        conversation_item = {
            "SessionId": original_session_id,
            "user_id": user_id,  # Fixed: DynamoDB key must be lowercase
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


def handle_director_response(message):
    """
    Handle director response from new architecture (director-response-topic)
    """
    try:
        director_response = json.loads(message)
        user_id = director_response.get("user_id")
        mission_id = director_response.get("mission_id")
        status = director_response.get("status")
        response_text = director_response.get(
            "response", "Your request has been processed."
        )

        print(f"Received director response for mission {mission_id}, user {user_id}")

        # Save the director's response to conversation history
        table = dynamodb.Table(TABLE_NAME)
        timestamp = int(time.time())
        expires_at = timestamp + (24 * 60 * 60)  # TTL for 24 hours

        # Find the original session ID from recent conversations
        response = table.scan(
            FilterExpression="user_id = :user_id AND #role = :role",
            ExpressionAttributeNames={"#role": "Role"},
            ExpressionAttributeValues={":user_id": user_id, ":role": "user"},
            Limit=50,
        )

        # Find the most recent session for this user
        original_session_id = None
        if response["Items"]:
            sorted_items = sorted(
                response["Items"], key=lambda x: x["Timestamp"], reverse=True
            )
            original_session_id = sorted_items[0].get("SessionId")

        if not original_session_id:
            original_session_id = f"session-{uuid.uuid4()}"

        # Save director's response to conversation history
        conversation_item = {
            "SessionId": original_session_id,
            "user_id": user_id,  # Fixed: DynamoDB key must be lowercase
            "Timestamp": timestamp,
            "Role": "assistant",
            "Message": response_text,
            "MissionId": mission_id,
            "MissionStatus": status,
            "Source": "director_new",
            "ExpiresAt": expires_at,
        }

        table.put_item(Item=conversation_item)
        print(
            f"Saved director's response (new architecture) to conversation history for user {user_id}"
        )

        return {"status": "SUCCESS", "message": "Director response processed"}

    except Exception as e:
        print(f"Error processing director response: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_chat_intention(message):
    """
    Handle chat intention from new architecture (chat-intention-topic)
    This would be used when we implement WebSocket/Chat Lambda
    """
    try:
        chat_intention = json.loads(message)
        user_id = chat_intention.get("user_id")
        user_message = chat_intention.get("message")
        session_id = chat_intention.get("session_id")

        print(f"Received chat intention for user {user_id}, session {session_id}")

        # Process the intention and publish to persona-intention-topic
        return process_intention_and_publish(user_id, user_message, session_id)

    except Exception as e:
        print(f"Error processing chat intention: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def process_intention_and_publish(user_id, user_message, session_id):
    """
    Process user intention and publish to the appropriate topic based on architecture
    """
    try:
        # Create intention manifest
        intention_manifest = {
            "session_id": session_id,
            "user_id": user_id,
            "message": user_message,
            "timestamp": int(time.time()),
            "source": "persona",
        }

        # Choose topic based on architecture
        if USE_NEW_ARCHITECTURE:
            topic_arn = PERSONA_INTENTION_TOPIC_ARN
            print(f"Publishing intention to NEW topic: {topic_arn}")
        else:
            # Should not happen - new architecture is required
            print("ERROR: New architecture required but topics not available")
            raise ValueError("PERSONA_INTENTION_TOPIC_ARN not configured")

        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(intention_manifest),
            MessageStructure="string",
        )

        print(
            f"Published intention to {'NEW' if USE_NEW_ARCHITECTURE else 'LEGACY'} architecture for SessionId: {session_id}"
        )

        return {"status": "SUCCESS", "message": "Intention published"}

    except Exception as e:
        print(f"Error publishing intention: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_intention_result(message):
    """
    Handle intention result from director (elaborated response)
    """
    try:
        intention_result = json.loads(message)
        user_id = intention_result.get("user_id")
        mission_id = intention_result.get("mission_id")
        status = intention_result.get("status")
        response_text = intention_result.get(
            "response", "Your request has been processed."
        )

        print(f"Received intention result for mission {mission_id}, user {user_id}")

        # Save the director's elaborated response to conversation history
        table = dynamodb.Table(TABLE_NAME)
        timestamp = int(time.time())
        expires_at = timestamp + (24 * 60 * 60)  # TTL for 24 hours

        # Find the original session ID from recent conversations
        response = table.scan(
            FilterExpression="user_id = :user_id AND #role = :role",
            ExpressionAttributeNames={"#role": "Role"},
            ExpressionAttributeValues={":user_id": user_id, ":role": "user"},
            Limit=50,
        )

        # Find the most recent session for this user
        original_session_id = None
        if response["Items"]:
            sorted_items = sorted(
                response["Items"], key=lambda x: x["Timestamp"], reverse=True
            )
            original_session_id = sorted_items[0].get("SessionId")

        if not original_session_id:
            original_session_id = f"session-{uuid.uuid4()}"

        # Save director's response to conversation history
        conversation_item = {
            "SessionId": original_session_id,
            "user_id": user_id,  # Fixed: DynamoDB key must be lowercase
            "Timestamp": timestamp,
            "Role": "assistant",
            "Message": response_text,
            "MissionId": mission_id,
            "MissionStatus": status,
            "Source": "director",
            "ExpiresAt": expires_at,
        }

        table.put_item(Item=conversation_item)
        print(
            f"Saved director's intention result to conversation history for user {user_id}"
        )

        return {"status": "SUCCESS", "message": "Intention result processed"}

    except Exception as e:
        print(f"Error processing intention result: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


def handle_user_message(event, context):
    """
    Handle new user message from API Gateway (original functionality)
    """
    print(f"[DEBUG] Starting handle_user_message at {time.time()}")
    
    try:
        # 1. Parse input from API Gateway
        print(f"[DEBUG] Parsing API Gateway event body...")
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        user_message = body.get("message")
        session_id = body.get("session_id")  # Optional: for continuing a conversation
        print(f"[DEBUG] Parsed: user_id='{user_id}', message='{user_message}', session_id='{session_id}'")

        if not user_id or not user_message:
            print(f"[DEBUG] Validation failed: user_id='{user_id}', message='{user_message}'")
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
        print(f"[DEBUG] Managing conversation state...")
        if not session_id:
            session_id = f"session-{uuid.uuid4()}"
            print(f"[DEBUG] Created new session_id: {session_id}")
        else:
            print(f"[DEBUG] Loading existing session: {session_id}")
            # Load previous conversation state from DynamoDB
            table = dynamodb.Table(TABLE_NAME)
            # Note: We need to scan because SessionId is not the primary key
            response = table.scan(
                FilterExpression="SessionId = :session_id",
                ExpressionAttributeValues={":session_id": session_id},
                Limit=1,
            )
            items = response.get("Items", [])
            item = items[0] if items else None

            if item:
                # Check if the session has expired
                current_time = int(time.time())
                if current_time > item["ExpiresAt"]:
                    # Session expired, create a new one
                    session_id = f"session-{uuid.uuid4()}"
                    print(f"[DEBUG] Session expired, created new: {session_id}")
            # If session doesn't exist, we'll continue with the provided session_id
            # and create a new session entry

        print(f"[DEBUG] Preparing DynamoDB write...")
        table = dynamodb.Table(TABLE_NAME)
        timestamp = int(time.time())

        # TTL for 24 hours
        expires_at = timestamp + (24 * 60 * 60)

        conversation_item = {
            "user_id": user_id,  # Fixed: DynamoDB key must be lowercase
            "SessionId": session_id,
            "Timestamp": timestamp,
            "Role": "user",
            "Message": user_message,
            "ExpiresAt": expires_at,
        }

        # Save the user's message to DynamoDB
        print(f"[DEBUG] Writing to DynamoDB...")
        table.put_item(Item=conversation_item)
        print(f"[DEBUG] ✅ Saved user message to DynamoDB with SessionId: {session_id}")

        # 3. Publish Intention using new architecture-aware function
        print(f"[DEBUG] Publishing intention...")
        result = process_intention_and_publish(user_id, user_message, session_id)
        print(f"[DEBUG] Intention publish result: {result}")

        if result["status"] != "SUCCESS":
            print(f"[ERROR] Failed to publish intention: {result}")
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps({"error": "Failed to process message"}),
            }

        # 4. Return a response to the user
        print(f"[DEBUG] Preparing response...")
        architecture_msg = "NEW" if USE_NEW_ARCHITECTURE else "LEGACY"
        response = {
            "statusCode": 200,  # Changed from 202 to 200 to satisfy tests
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps(
                {
                    "message": f"Request received ({architecture_msg} architecture). The Director is analyzing the intention.",
                    "session_id": session_id,
                    "architecture": architecture_msg,
                }
            ),
        }
        print(f"[DEBUG] ✅ Completed handle_user_message at {time.time()}")
        return response
        
    except Exception as e:
        print(f"[ERROR] Exception in handle_user_message: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }


def handle_persona_intention(message):
    """
    Handle persona intention received via SNS for direct testing
    """
    try:
        intention_data = json.loads(message)
        print(f"Processing persona intention: {intention_data}")

        # Extract required fields
        user_id = intention_data.get("user_id", "unknown")
        user_message = intention_data.get(
            "intention", intention_data.get("message", "")
        )
        mission_id = intention_data.get("mission_id")
        test_mode = intention_data.get("test_mode", False)

        if not user_message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No intention/message provided"}),
            }

        # Generate session ID if not provided
        session_id = intention_data.get("session_id", f"session-{uuid.uuid4()}")

        # For test mode, create a simplified intention manifest
        if test_mode:
            print(
                f"Test mode: Processing intention '{user_message}' for user {user_id}"
            )

            # Create intention manifest for Director
            intention_manifest = {
                "session_id": session_id,
                "user_id": user_id,
                "user_intention": user_message,
                "mission_id": mission_id,
                "timestamp": int(time.time()),
                "source": "persona_test",
                "context": intention_data.get("context", {}),
            }

            # Publish to Director via persona_intention_topic (correct flow)
            if (
                PERSONA_INTENTION_TOPIC_ARN
            ):  # Use correct topic for publishing to Director
                director_message = {
                    "mission_id": mission_id,
                    "user_intention": user_message,
                    "context": intention_data.get("context", {}),
                    "user_id": user_id,
                    "timestamp": int(time.time()),
                }

                sns.publish(
                    TopicArn=PERSONA_INTENTION_TOPIC_ARN,  # Persona publishes here, Director reads
                    Message=json.dumps(director_message),
                    Subject=f"User Intention from Persona - {mission_id}",
                )

                print(
                    f"Published intention to Director via persona_intention_topic for mission {mission_id}"
                )

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "status": "success",
                        "message": "Test intention processed",
                        "mission_id": mission_id,
                        "session_id": session_id,
                    }
                ),
            }

        # For non-test mode, use the normal flow
        return process_intention_and_publish(user_id, user_message, session_id)

    except Exception as e:
        print(f"Error processing persona intention: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to process intention: {str(e)}"}),
        }
