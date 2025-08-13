# =============================================================================
# BuildingOS Platform - WebSocket Broadcast Message Handler
# =============================================================================
#
# **Purpose:** Broadcasts messages to WebSocket clients via API Gateway Management
# **Scope:** Final step in agent response delivery to connected users
# **Usage:** Invoked by SNS when agents complete user request processing
#
# **Key Features:**
# - Receives agent responses from SNS persona_response_topic
# - Retrieves active WebSocket connections from DynamoDB
# - Broadcasts formatted responses to connected clients
# - Handles connection cleanup for stale/disconnected clients
# - Uses common utilities layer for AWS client management
#
# **Event Flow:**
# 1. Agent completes user request processing
# 2. Response published to SNS persona_response_topic
# 3. This Lambda receives SNS event with response data
# 4. Retrieves target connection from DynamoDB
# 5. Sends formatted message to WebSocket client
# 6. Handles connection errors and cleanup
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - DynamoDB table for WebSocket connection management
# - API Gateway Management API for WebSocket communication
# - SNS subscription to persona_response_topic
#
# **Integration:**
# - Triggers: SNS persona_response_topic subscription
# - Reads from: WebSocket connections table
# - Sends to: Connected WebSocket clients via API Gateway
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
#
# =============================================================================

import json
import os
import time
from typing import Dict, Any, List, Optional

# Import common utilities from Lambda layer
from aws_clients import get_dynamodb_resource, get_apigateway_management_client
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
)
from models import SNSMessage, APIGatewayResponse

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
CONNECTIONS_TABLE = get_required_env_var("CONNECTIONS_TABLE")
WEBSOCKET_API_ENDPOINT = get_required_env_var("WEBSOCKET_API_ENDPOINT")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
dynamodb_resource = get_dynamodb_resource()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    WebSocket Broadcast Message Handler with enhanced error handling and logging.

    Processes SNS events containing agent responses that need to be broadcast to WebSocket
    clients. Handles connection management, message delivery, and cleanup of stale connections.

    Args:
        event: SNS event containing one or more message records
            Expected structure:
            {
                "Records": [{
                    "Sns": {
                        "Message": "JSON string with broadcast data",
                        "MessageId": "message_id"
                    }
                }]
            }
        context: Lambda runtime context information

    Returns:
        dict: API Gateway response with status code and processing summary
            Success: {"statusCode": 200, "body": "broadcast_summary"}
            Error: {"statusCode": 4xx/5xx, "body": "error_message"}

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "WebSocket broadcast processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "records_count": len(event.get("Records", [])),
        },
    )

    try:
        # Validate SNS event structure
        records = event.get("Records", [])
        if not records:
            logger.warning(
                "No SNS records found in broadcast event",
                extra={"correlation_id": correlation_id},
            )
            return create_success_response(
                {"message": "No records to process", "correlation_id": correlation_id}
            )

        # Process each SNS record in the event
        broadcast_summary = _process_sns_records(records, correlation_id)

        logger.info(
            "WebSocket broadcast processing completed",
            extra={
                "correlation_id": correlation_id,
                "total_records": broadcast_summary["total_records"],
                "successful_broadcasts": broadcast_summary["successful_broadcasts"],
                "failed_broadcasts": broadcast_summary["failed_broadcasts"],
                "cleanup_actions": broadcast_summary["cleanup_actions"],
            },
        )

        return create_success_response(
            {
                "message": "Broadcast processing completed",
                "correlation_id": correlation_id,
                "summary": broadcast_summary,
            }
        )

    except Exception as e:
        logger.error(
            "Critical error in WebSocket broadcast processing",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        return create_error_response(
            500, "Internal server error during broadcast processing", correlation_id
        )


def _process_sns_records(
    records: List[Dict[str, Any]], correlation_id: str
) -> Dict[str, int]:
    """
    Process all SNS records in the broadcast event.

    Args:
        records: List of SNS records from the event
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Summary of broadcast processing results
    """
    summary = {
        "total_records": len(records),
        "successful_broadcasts": 0,
        "failed_broadcasts": 0,
        "cleanup_actions": 0,
    }

    # Initialize API Gateway Management client for WebSocket communication
    apigw_client = get_apigateway_management_client(WEBSOCKET_API_ENDPOINT)

    for record_index, record in enumerate(records):
        try:
            logger.debug(
                "Processing SNS record",
                extra={
                    "correlation_id": correlation_id,
                    "record_index": record_index,
                    "message_id": record.get("Sns", {}).get("MessageId"),
                },
            )

            # Extract and validate broadcast message
            broadcast_data = _extract_broadcast_data(record, correlation_id)
            if not broadcast_data:
                summary["failed_broadcasts"] += 1
                continue

            # Send message to WebSocket connection
            success = _send_websocket_message(
                apigw_client, broadcast_data, correlation_id
            )

            if success:
                summary["successful_broadcasts"] += 1
            else:
                summary["failed_broadcasts"] += 1

                # Attempt connection cleanup if message delivery failed
                cleanup_success = _cleanup_stale_connection(
                    broadcast_data.get("connection_id"), correlation_id
                )
                if cleanup_success:
                    summary["cleanup_actions"] += 1

        except Exception as e:
            logger.error(
                "Error processing SNS record",
                extra={
                    "correlation_id": correlation_id,
                    "record_index": record_index,
                    "error": str(e),
                },
                exc_info=True,
            )
            summary["failed_broadcasts"] += 1

    return summary


def _extract_broadcast_data(
    record: Dict[str, Any], correlation_id: str
) -> Optional[Dict[str, Any]]:
    """
    Extract and validate broadcast data from SNS record.

    Args:
        record: Individual SNS record from the event
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Validated broadcast data if successful, None otherwise
    """
    try:
        sns_data = record.get("Sns", {})
        message_body = sns_data.get("Message", "")

        if not message_body:
            logger.warning(
                "Empty SNS message body",
                extra={"correlation_id": correlation_id},
            )
            return None

        # Parse JSON message from SNS
        try:
            broadcast_data = json.loads(message_body)
        except json.JSONDecodeError as e:
            logger.warning(
                "Invalid JSON in SNS message",
                extra={"correlation_id": correlation_id, "json_error": str(e)},
            )
            return None

        # Validate required fields
        connection_id = broadcast_data.get("connection_id") or broadcast_data.get(
            "connectionId"
        )
        if not connection_id:
            logger.warning(
                "Missing connection ID in broadcast data",
                extra={
                    "correlation_id": correlation_id,
                    "data_keys": list(broadcast_data.keys()),
                },
            )
            return None

        # Normalize the data structure
        normalized_data = {
            "connection_id": connection_id,
            "payload": broadcast_data.get("payload", broadcast_data.get("message", {})),
            "user_id": broadcast_data.get("user_id", "anonymous"),
            "session_id": broadcast_data.get("session_id"),
            "timestamp": broadcast_data.get("timestamp", int(time.time())),
            "correlation_id": broadcast_data.get("correlation_id", correlation_id),
        }

        logger.debug(
            "Extracted broadcast data",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "user_id": normalized_data["user_id"],
            },
        )

        return normalized_data

    except Exception as e:
        logger.error(
            "Error extracting broadcast data",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
        return None


def _send_websocket_message(
    apigw_client: Any, broadcast_data: Dict[str, Any], correlation_id: str
) -> bool:
    """
    Send message to WebSocket connection via API Gateway Management API.

    Args:
        apigw_client: API Gateway Management client
        broadcast_data: Validated broadcast data
        correlation_id: Request correlation ID for logging

    Returns:
        bool: True if message sent successfully, False otherwise
    """
    connection_id = broadcast_data["connection_id"]

    try:
        # Format message for WebSocket client
        websocket_message = {
            "type": "agent_response",
            "data": broadcast_data["payload"],
            "metadata": {
                "user_id": broadcast_data["user_id"],
                "session_id": broadcast_data["session_id"],
                "timestamp": broadcast_data["timestamp"],
                "correlation_id": correlation_id,
                "environment": ENVIRONMENT,
            },
        }

        # Send message to WebSocket connection
        response = apigw_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(websocket_message).encode("utf-8"),
        )

        logger.info(
            "Successfully sent WebSocket message",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "user_id": broadcast_data["user_id"],
                "message_size": len(json.dumps(websocket_message)),
            },
        )

        return True

    except apigw_client.exceptions.GoneException:
        logger.warning(
            "WebSocket connection no longer exists",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
            },
        )
        return False

    except apigw_client.exceptions.ForbiddenException:
        logger.warning(
            "WebSocket connection access forbidden",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
            },
        )
        return False

    except Exception as e:
        logger.error(
            "Failed to send WebSocket message",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "error": str(e),
            },
            exc_info=True,
        )
        return False


def _cleanup_stale_connection(
    connection_id: Optional[str], correlation_id: str
) -> bool:
    """
    Remove stale WebSocket connection from DynamoDB connections table.

    Args:
        connection_id: WebSocket connection ID to cleanup
        correlation_id: Request correlation ID for logging

    Returns:
        bool: True if cleanup successful, False otherwise
    """
    if not connection_id:
        return False

    try:
        connections_table = dynamodb_resource.Table(CONNECTIONS_TABLE)

        # Remove connection from DynamoDB
        response = connections_table.delete_item(
            Key={"connectionId": connection_id},
            ReturnValues="ALL_OLD",
        )

        # Check if connection actually existed
        if response.get("Attributes"):
            logger.info(
                "Cleaned up stale WebSocket connection",
                extra={
                    "correlation_id": correlation_id,
                    "connection_id": connection_id,
                },
            )
            return True
        else:
            logger.debug(
                "Connection not found in cleanup attempt",
                extra={
                    "correlation_id": correlation_id,
                    "connection_id": connection_id,
                },
            )
            return False

    except Exception as e:
        logger.error(
            "Error cleaning up stale connection",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "error": str(e),
            },
            exc_info=True,
        )
        return False
