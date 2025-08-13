# =============================================================================
# BuildingOS Platform - WebSocket Default Message Handler
# =============================================================================
#
# **Purpose:** Processes incoming WebSocket messages and publishes them to SNS
# **Scope:** Entry point for user chat interactions in BuildingOS platform
# **Usage:** Invoked by API Gateway WebSocket when users send messages
#
# **Key Features:**
# - Processes real-time WebSocket messages from connected clients
# - Publishes user intentions to SNS chat_intention_topic for agent processing
# - Maintains connection state in DynamoDB for session management
# - Implements standardized error handling and response formatting
# - Uses common utilities layer for AWS client management
#
# **Event Flow:**
# 1. User sends message through WebSocket connection
# 2. API Gateway invokes this Lambda with connection context
# 3. Message is validated and formatted for agent processing
# 4. Published to SNS topic for asynchronous agent handling
# 5. Success response returned to maintain WebSocket connection
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - DynamoDB table for WebSocket connection management
# - SNS topic for publishing chat intentions to agents
# - API Gateway WebSocket API for real-time communication
#
# **Integration:**
# - Triggers: API Gateway WebSocket $default route
# - Publishes to: chat_intention_topic (processed by agent_persona)
# - Stores in: WebSocket connections table for session tracking
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
#
# =============================================================================

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field
from aws_clients import get_sns_client, get_dynamodb_resource
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
)
from models import APIGatewayResponse
from pydantic_models import SNSMessage


# Simple structured logging models for debugging
class LogLevel(str, Enum):
    """Log level enumeration"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SimpleStructuredLog(BaseModel):
    """Simple structured log for debugging Pydantic issues"""

    level: LogLevel
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    correlation_id: str
    service: str = "websocket_default"
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None

    def print_log(self) -> None:
        """Print structured log to stdout for Lambda CloudWatch"""
        print(
            json.dumps(
                {
                    "timestamp": self.timestamp.isoformat(),
                    "level": self.level.value,
                    "service": self.service,
                    "correlation_id": self.correlation_id,
                    "message": self.message,
                    "data": self.data,
                    "error": self.error,
                },
                default=str,
                ensure_ascii=False,
            )
        )


# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
CONNECTIONS_TABLE = get_required_env_var("CONNECTIONS_TABLE")
CHAT_INTENTION_TOPIC_ARN = get_required_env_var("CHAT_INTENTION_TOPIC_ARN")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
sns_client = get_sns_client()
dynamodb_resource = get_dynamodb_resource()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    WebSocket Default Message Handler with enhanced error handling and logging.

    Processes incoming WebSocket messages from clients and publishes them to the SNS
    chat intention topic for further processing by the BuildingOS agent system.

    Args:
        event: WebSocket API Gateway event containing connection ID and message body
            Expected structure:
            {
                "requestContext": {
                    "connectionId": "connection_id",
                    "requestId": "request_id"
                },
                "body": "JSON string with user message"
            }
        context: Lambda runtime context information

    Returns:
        dict: API Gateway response with status code and response body
            Success: {"statusCode": 200, "body": "success_message"}
            Error: {"statusCode": 4xx/5xx, "body": "error_message"}

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "WebSocket message processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
        },
    )

    try:
        # Validate and extract connection ID from WebSocket context
        connection_id = _extract_connection_id(event, correlation_id)
        if not connection_id:
            return create_error_response(
                400, "Missing connection ID in WebSocket context", correlation_id
            )

        logger.info(
            "Processing WebSocket message",
            extra={"correlation_id": correlation_id, "connection_id": connection_id},
        )

        # Parse and validate message body from client
        message_body = _parse_message_body(event, correlation_id)
        if not message_body:
            return create_error_response(
                400, "Invalid or missing message body", correlation_id
            )

        # Create standardized message payload for SNS publishing
        chat_message = _create_chat_message_payload(
            connection_id, message_body, event, correlation_id
        )

        # Publish intention message to SNS topic for agent processing
        success = _publish_chat_intention(chat_message, correlation_id)
        if not success:
            return create_error_response(
                500, "Failed to publish message to agent system", correlation_id
            )

        logger.info(
            "WebSocket message processed successfully",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "user_id": chat_message.get("user_id", "anonymous"),
            },
        )

        return create_success_response(
            {
                "message": "Message processed successfully",
                "correlation_id": correlation_id,
            }
        )

    except Exception as e:
        logger.error(
            "Critical error in WebSocket message processing",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        return create_error_response(
            500, "Internal server error during message processing", correlation_id
        )


def _extract_connection_id(event: Dict[str, Any], correlation_id: str) -> Optional[str]:
    """
    Extract and validate connection ID from WebSocket event context.

    Args:
        event: WebSocket API Gateway event
        correlation_id: Request correlation ID for logging

    Returns:
        str: Connection ID if found and valid, None otherwise
    """
    try:
        connection_id = event.get("requestContext", {}).get("connectionId")

        if not connection_id:
            logger.warning(
                "Connection ID not found in WebSocket event",
                extra={
                    "correlation_id": correlation_id,
                    "event_keys": list(event.keys()),
                },
            )
            return None

        # Validate connection ID format (basic validation)
        if not isinstance(connection_id, str) or len(connection_id) < 10:
            logger.warning(
                "Invalid connection ID format",
                extra={
                    "correlation_id": correlation_id,
                    "connection_id": connection_id,
                },
            )
            return None

        return connection_id

    except Exception as e:
        logger.error(
            "Error extracting connection ID",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
        return None


def _parse_message_body(
    event: Dict[str, Any], correlation_id: str
) -> Optional[Dict[str, Any]]:
    """
    Parse and validate JSON message body from WebSocket event.

    Args:
        event: WebSocket API Gateway event
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Parsed message body if valid, None otherwise
    """
    try:
        body = event.get("body")

        if not body:
            logger.warning(
                "No message body provided in WebSocket event",
                extra={"correlation_id": correlation_id},
            )
            return None

        # Parse JSON body
        try:
            message_body = json.loads(body)

            # Structured logging to debug message content
            debug_log = SimpleStructuredLog(
                level=LogLevel.DEBUG,
                message="WebSocket message body parsed successfully",
                correlation_id=correlation_id,
                data={
                    "raw_body": body,
                    "parsed_body": message_body,
                    "body_keys": (
                        list(message_body.keys())
                        if isinstance(message_body, dict)
                        else []
                    ),
                    "step": "message_parsing",
                },
            )
            debug_log.print_log()

        except json.JSONDecodeError as e:
            logger.warning(
                "Invalid JSON in message body",
                extra={"correlation_id": correlation_id, "json_error": str(e)},
            )
            return None

        # Validate required fields
        if not isinstance(message_body, dict):
            logger.warning(
                "Message body is not a JSON object",
                extra={
                    "correlation_id": correlation_id,
                    "body_type": type(message_body),
                },
            )
            return None

        return message_body

    except Exception as e:
        logger.error(
            "Error parsing message body",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
        return None


def _create_chat_message_payload(
    connection_id: str,
    message_body: Dict[str, Any],
    event: Dict[str, Any],
    correlation_id: str,
) -> Dict[str, Any]:
    """
    Create standardized chat message payload for SNS publishing.

    Args:
        connection_id: WebSocket connection ID
        message_body: Parsed message body from client
        event: Original WebSocket event
        correlation_id: Request correlation ID

    Returns:
        dict: Standardized chat message payload
    """
    current_timestamp = int(time.time())

    # Create standardized SNS message using common utilities
    chat_message = {
        "connection_id": connection_id,
        "user_message": message_body.get("message", ""),
        "user_id": message_body.get("user_id", "anonymous"),
        "session_id": message_body.get("session_id"),
        "timestamp": current_timestamp,
        "correlation_id": correlation_id,
        "metadata": {
            "source": "websocket_default",
            "environment": ENVIRONMENT,
            "api_gateway_request_id": event.get("requestContext", {}).get("requestId"),
            "function_version": event.get("requestContext", {}).get("stage", "unknown"),
            "processing_timestamp": current_timestamp,
        },
    }

    logger.debug(
        "Created chat message payload",
        extra={
            "correlation_id": correlation_id,
            "user_id": chat_message["user_id"],
            "message_length": len(chat_message["user_message"]),
        },
    )

    return chat_message


def _publish_chat_intention(chat_message: Dict[str, Any], correlation_id: str) -> bool:
    """
    Publish chat intention message to SNS topic for agent processing.

    Args:
        chat_message: Standardized chat message payload
        correlation_id: Request correlation ID for logging

    Returns:
        bool: True if published successfully, False otherwise
    """
    # Structured logging for debugging
    start_log = SimpleStructuredLog(
        level=LogLevel.INFO,
        message="Starting chat intention publishing with Pydantic",
        correlation_id=correlation_id,
        data={
            "chat_message": chat_message,
            "topic_arn": CHAT_INTENTION_TOPIC_ARN,
            "step": "initialization",
        },
    )
    start_log.print_log()

    try:
        # Log SNSMessage creation attempt
        creation_log = SimpleStructuredLog(
            level=LogLevel.DEBUG,
            message="Creating SNSMessage with Pydantic validation",
            correlation_id=correlation_id,
            data={
                "message_type": "chat_intention",
                "source_service": "websocket_default",
                "step": "sns_message_creation",
            },
        )
        creation_log.print_log()

        # Create SNS message using Pydantic validation
        sns_message = SNSMessage(
            message_type="chat_intention",
            source_service="websocket_default",
            data={"message": chat_message},
            correlation_id=correlation_id,
        )

        # Log successful creation with validation details
        created_log = SimpleStructuredLog(
            level=LogLevel.INFO,
            message="SNSMessage created successfully with Pydantic validation",
            correlation_id=correlation_id,
            data={
                "sns_message_valid": True,
                "message_type": sns_message.message_type,
                "source_service": sns_message.source_service,
                "step": "sns_message_validated",
            },
        )
        created_log.print_log()

        # Publish to SNS topic using common client
        response = sns_client.publish(
            TopicArn=CHAT_INTENTION_TOPIC_ARN,
            Message=sns_message.to_json(),
            Subject="BuildingOS Chat Intention",
            MessageAttributes={
                "correlation_id": {"DataType": "String", "StringValue": correlation_id},
                "source": {"DataType": "String", "StringValue": "websocket_default"},
                "user_id": {
                    "DataType": "String",
                    "StringValue": chat_message.get("user_id", "anonymous"),
                },
            },
        )

        logger.info(
            "Successfully published chat intention to SNS",
            extra={
                "correlation_id": correlation_id,
                "sns_message_id": response.get("MessageId"),
                "topic_arn": CHAT_INTENTION_TOPIC_ARN,
            },
        )

        return True

    except Exception as e:
        # Structured error logging with Pydantic
        import traceback

        error_log = SimpleStructuredLog(
            level=LogLevel.ERROR,
            message="Failed to publish chat intention to SNS - Pydantic analysis",
            correlation_id=correlation_id,
            error={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "context": {
                    "correlation_id": correlation_id,
                    "topic_arn": CHAT_INTENTION_TOPIC_ARN,
                    "chat_message": chat_message,
                    "step": "sns_publishing_failed",
                },
            },
            data={"topic_arn": CHAT_INTENTION_TOPIC_ARN, "step": "exception_handling"},
        )
        error_log.print_log()

        # Legacy logging for compatibility
        logger.error(
            "Failed to publish chat intention to SNS",
            extra={
                "correlation_id": correlation_id,
                "topic_arn": CHAT_INTENTION_TOPIC_ARN,
                "error": str(e),
            },
            exc_info=True,
        )
        return False
