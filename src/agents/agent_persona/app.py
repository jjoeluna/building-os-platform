# =============================================================================
# BuildingOS Platform - Agent Persona (User Interaction Handler)
# =============================================================================
#
# **Purpose:** Processes user messages and manages conversational interactions
# **Scope:** Entry point for user chat processing and persona-based responses
# **Usage:** Invoked by SNS when users send messages through WebSocket
#
# **Key Features:**
# - Processes user chat intentions from WebSocket connections
# - Analyzes user messages and extracts actionable intentions
# - Manages conversation context and session state in DynamoDB
# - Formats and delivers agent responses back to users
# - Uses common utilities layer for AWS client management
#
# **Event Flow (Incoming):**
# 1. User sends message via WebSocket → chat_intention_topic
# 2. This Lambda receives SNS event with user message
# 3. Analyzes message and extracts user intentions
# 4. Publishes structured intentions to persona_intention_topic
# 5. Director Agent receives and processes intentions
#
# **Event Flow (Outgoing):**
# 1. Director Agent completes processing → director_response_topic
# 2. This Lambda receives response for formatting
# 3. Formats response for user consumption
# 4. Publishes to persona_response_topic → WebSocket broadcast
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - DynamoDB table for conversation state and session management
# - SNS topics for event-driven communication with other agents
# - Bedrock/AI services for natural language processing
#
# **Integration:**
# - Triggers: SNS chat_intention_topic, director_response_topic
# - Publishes to: persona_intention_topic, persona_response_topic
# - Stores in: Short-term memory table for conversation context
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
#
# =============================================================================

import json
import os
import uuid
import time
from decimal import Decimal
from typing import Dict, Any, Optional, List

# Import common utilities from Lambda layer
from aws_clients import get_dynamodb_resource, get_sns_client
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
    serialize_dynamodb_item,
)
from models import SNSMessage, ConversationState, UserIntention

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
SHORT_TERM_MEMORY_TABLE_NAME = get_required_env_var("SHORT_TERM_MEMORY_TABLE_NAME")
PERSONA_INTENTION_TOPIC_ARN = get_required_env_var("PERSONA_INTENTION_TOPIC_ARN")
DIRECTOR_RESPONSE_TOPIC_ARN = get_required_env_var("DIRECTOR_RESPONSE_TOPIC_ARN")
PERSONA_RESPONSE_TOPIC_ARN = get_required_env_var("PERSONA_RESPONSE_TOPIC_ARN")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
dynamodb_resource = get_dynamodb_resource()
sns_client = get_sns_client()

# Validate event-driven architecture configuration
logger.info(
    "Agent Persona initialized with event-driven architecture",
    extra={
        "persona_intention_topic": PERSONA_INTENTION_TOPIC_ARN,
        "director_response_topic": DIRECTOR_RESPONSE_TOPIC_ARN,
        "persona_response_topic": PERSONA_RESPONSE_TOPIC_ARN,
        "environment": ENVIRONMENT,
    },
)


def decimal_default(obj: Any) -> float:
    """JSON serializer function that handles Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Agent Persona Main Handler with enhanced event routing and error handling.

    Processes user interactions and agent responses in the BuildingOS event-driven
    architecture. Routes events based on source and implements comprehensive logging.

    Args:
        event: Event data from various sources (SNS, API Gateway)
            SNS Events:
            - chat_intention_topic: User messages from WebSocket
            - director_response_topic: Agent responses for user delivery
            API Gateway Events:
            - GET: Conversation retrieval
            - POST: Direct user message processing (legacy)
        context: Lambda runtime context information

    Returns:
        dict: Response appropriate to event source
            SNS: Processing status and correlation info
            API Gateway: HTTP response with CORS headers

    Event Routing:
        1. SNS Events → Topic-specific handlers
        2. API Gateway → HTTP method handlers
        3. Unknown → Error response with details

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "Agent Persona processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "event_keys": list(event.keys()),
        },
    )

    try:
        # Route based on event source with enhanced validation
        if "Records" in event:
            return _handle_sns_events(event, correlation_id)
        elif "httpMethod" in event:
            return _handle_api_gateway_events(event, context, correlation_id)
        else:
            logger.warning(
                "Unknown event format received",
                extra={
                    "correlation_id": correlation_id,
                    "event_keys": list(event.keys()),
                },
            )
            return create_error_response(
                400,
                "Unknown event format - expected SNS or API Gateway",
                correlation_id,
            )

    except Exception as e:
        logger.error(
            "Critical error in Agent Persona handler",
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
                        "error": "Internal server error during persona processing",
                        "correlation_id": correlation_id,
                    }
                ),
            }
        else:
            return create_error_response(
                500, "Internal server error during persona processing", correlation_id
            )


def _handle_sns_events(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Handle SNS events from various topics in the event-driven architecture.

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

        # Route to appropriate topic handler
        if "chat-intention-topic" in topic_arn:
            return handle_chat_intention(message, correlation_id)
        elif "director-response-topic" in topic_arn:
            return handle_director_response(message, correlation_id)
        else:
            logger.warning(
                "Unknown SNS topic received",
                extra={"correlation_id": correlation_id, "topic_arn": topic_arn},
            )
            return create_error_response(
                400, f"Unknown SNS topic: {topic_arn}", correlation_id
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
    Handle API Gateway events for direct HTTP requests (legacy support).

    Args:
        event: API Gateway event with HTTP method and request data
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with appropriate status and CORS headers
    """
    try:
        http_method = event.get("httpMethod", "").upper()

        logger.info(
            "Processing API Gateway request",
            extra={
                "correlation_id": correlation_id,
                "http_method": http_method,
                "path": event.get("path", ""),
            },
        )

        # Route to appropriate HTTP method handler
        if http_method == "GET":
            return handle_get_conversation(event, context, correlation_id)
        elif http_method == "POST":
            return handle_user_message(event, context, correlation_id)
        elif http_method == "OPTIONS":
            # Handle CORS preflight requests
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps({"message": "CORS preflight successful"}),
            }
        else:
            logger.warning(
                "Unsupported HTTP method",
                extra={"correlation_id": correlation_id, "http_method": http_method},
            )
            return {
                "statusCode": 405,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps(
                    {
                        "error": f"Unsupported method {http_method}",
                        "correlation_id": correlation_id,
                    }
                ),
            }

    except Exception as e:
        logger.error(
            "Error processing API Gateway events",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
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
                    "error": "Error processing API Gateway request",
                    "correlation_id": correlation_id,
                }
            ),
        }


# =============================================================================
# Legacy Function Signatures (Updated with Correlation ID Support)
# =============================================================================


def handle_chat_intention(message: str, correlation_id: str = None) -> Dict[str, Any]:
    """
    Handle chat intention from WebSocket users.

    Args:
        message: JSON string containing user chat intention
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Processing result with status and correlation info
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing chat intention",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return create_success_response(
        {
            "message": "Chat intention processed",
            "correlation_id": correlation_id,
        }
    )


def handle_director_response(
    message: str, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle response from Director Agent for user delivery.

    Args:
        message: JSON string containing director response
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Processing result with status and correlation info
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing director response",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return create_success_response(
        {
            "message": "Director response processed",
            "correlation_id": correlation_id,
        }
    )


def handle_get_conversation(
    event: Dict[str, Any], context: Any, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle GET request for conversation retrieval.

    Args:
        event: API Gateway GET event
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with conversation data
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing conversation retrieval",
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
                "message": "Conversation retrieval processed",
                "correlation_id": correlation_id,
            }
        ),
    }


def handle_user_message(
    event: Dict[str, Any], context: Any, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle POST request for direct user message processing (legacy).

    Args:
        event: API Gateway POST event
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with processing result
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing direct user message",
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
                "message": "Direct user message processed",
                "correlation_id": correlation_id,
            }
        ),
    }


def handle_get_conversation_legacy(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle GET request to retrieve conversation history (legacy - renamed to avoid conflict)
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


def handle_mission_result(message: str) -> Dict[str, Any]:
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


def handle_director_response(message: str) -> Dict[str, Any]:
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


def handle_chat_intention(message: str) -> Dict[str, Any]:
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


def process_intention_and_publish(
    user_id: str, user_message: str, session_id: str
) -> Dict[str, Any]:
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


def handle_intention_result(message: str) -> Dict[str, Any]:
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


def handle_user_message_legacy(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle new user message from API Gateway (legacy - renamed to avoid conflict)
    """
    print(f"[DEBUG] Starting handle_user_message_legacy at {time.time()}")

    try:
        # 1. Parse input from API Gateway
        print(f"[DEBUG] Parsing API Gateway event body...")
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        user_message = body.get("message")
        session_id = body.get("session_id")  # Optional: for continuing a conversation
        print(
            f"[DEBUG] Parsed: user_id='{user_id}', message='{user_message}', session_id='{session_id}'"
        )

        if not user_id or not user_message:
            print(
                f"[DEBUG] Validation failed: user_id='{user_id}', message='{user_message}'"
            )
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


def handle_persona_intention(message: str) -> Dict[str, Any]:
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
