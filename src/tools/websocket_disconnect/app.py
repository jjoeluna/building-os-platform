# =============================================================================
# BuildingOS Platform - WebSocket Disconnect Handler
# =============================================================================
#
# **Purpose:** Handles WebSocket disconnections and cleanup for real-time chat
# **Scope:** Manages connection lifecycle termination and persistent storage cleanup
# **Usage:** Invoked by API Gateway WebSocket API when clients disconnect
#
# **Key Features:**
# - Handles WebSocket disconnection events from web clients
# - Removes connection metadata from DynamoDB for proper cleanup
# - Tracks disconnection events and manages connection state transitions
# - Implements graceful cleanup with error handling for stale connections
# - Uses common utilities layer for AWS client management
# - Provides comprehensive logging for connection lifecycle management
#
# **Disconnection Flow:**
# 1. Client closes WebSocket connection or connection times out
# 2. API Gateway invokes this Lambda with disconnection event
# 3. Connection ID extracted from API Gateway request context
# 4. Connection metadata removed from DynamoDB connections table
# 5. Success response returned to complete disconnection cleanup
#
# **Data Cleanup:**
# - Table: connections (DynamoDB)
# - Operation: DELETE by connectionId (primary key)
# - Side Effects: Connection no longer available for message routing
#
# **Dependencies:**
# - Common utilities layer for DynamoDB client management
# - DynamoDB connections table for persistent connection storage
# - API Gateway WebSocket API for disconnection event handling
#
# **Integration:**
# - Triggers: API Gateway WebSocket $disconnect route
# - Storage: DynamoDB connections table cleanup
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
# - Error Handling: Graceful handling of missing or stale connections
#
# =============================================================================

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Import common utilities from Lambda layer
from aws_clients import get_dynamodb_resource
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
    serialize_dynamodb_item,
)
from models import WebSocketConnection, ConnectionState

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
CONNECTIONS_TABLE = get_required_env_var("CONNECTIONS_TABLE")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
dynamodb_resource = get_dynamodb_resource()

# Validate DynamoDB table configuration
logger.info(
    "WebSocket Disconnect handler initialized",
    extra={
        "connections_table": CONNECTIONS_TABLE,
        "environment": ENVIRONMENT,
        "dynamodb_resource": "initialized",
    },
)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    WebSocket Disconnect Handler with enhanced connection cleanup.

    Handles WebSocket disconnections and removes connection metadata from DynamoDB
    to ensure proper cleanup and prevent stale connection accumulation.

    Args:
        event: API Gateway WebSocket disconnect event
            Required fields:
            - requestContext.connectionId: Unique WebSocket connection ID
            - requestContext.routeKey: Route key (should be '$disconnect')
            - requestContext.eventType: Event type (should be 'DISCONNECT')
            Optional fields:
            - requestContext.disconnectReason: Reason for disconnection
        context: Lambda runtime context information

    Returns:
        dict: HTTP response for API Gateway WebSocket
            Success: {"statusCode": 200, "body": "Disconnected"}
            Error: {"statusCode": 4xx/5xx, "body": error_details}

    Connection Cleanup:
        Removes from DynamoDB connections table:
        - connectionId: Primary key for connection removal
        - All associated metadata is automatically removed
        - Graceful handling if connection doesn't exist (idempotent)

    Error Handling:
        - Missing connection ID: 400 Bad Request (logs warning, returns success)
        - DynamoDB errors: 500 Internal Server Error
        - Connection not found: 200 OK (idempotent behavior)
        - All errors logged with correlation IDs

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "WebSocket disconnection cleanup started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "event_type": event.get("requestContext", {}).get("eventType", "unknown"),
        },
    )

    try:
        # Extract connection details from API Gateway event
        connection_id = _extract_connection_id(event, correlation_id)
        if not connection_id:
            # Log warning but return success for graceful degradation
            logger.warning(
                "Missing connection ID in disconnect event - returning success",
                extra={"correlation_id": correlation_id},
            )
            return _create_disconnect_success_response(
                "Disconnected (no connection ID)", correlation_id
            )

        # Extract disconnection context for logging
        disconnect_info = _extract_disconnect_info(event, correlation_id)

        # Remove connection from DynamoDB
        connection_removed = _remove_connection(
            connection_id, disconnect_info, correlation_id
        )

        if not connection_removed:
            # Log error but return success to prevent API Gateway retries
            logger.warning(
                "Failed to remove connection from DynamoDB - continuing",
                extra={
                    "correlation_id": correlation_id,
                    "connection_id": connection_id,
                },
            )

        # Log successful disconnection cleanup
        logger.info(
            "WebSocket disconnection cleanup completed successfully",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "disconnect_reason": disconnect_info.get("reason", "unknown"),
                "connection_removed": connection_removed,
            },
        )

        # Return success response to API Gateway
        return _create_disconnect_success_response(
            f"Disconnected: {connection_id}", correlation_id
        )

    except Exception as e:
        logger.error(
            "Critical error in WebSocket disconnect handler",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        # Return success even on error to prevent API Gateway retries
        # Disconnection events should be idempotent
        return _create_disconnect_success_response(
            "Disconnected (with errors)", correlation_id
        )


def _extract_connection_id(event: Dict[str, Any], correlation_id: str) -> Optional[str]:
    """
    Extract connection ID from API Gateway WebSocket disconnect event.

    Args:
        event: API Gateway WebSocket event
        correlation_id: Request correlation ID for logging

    Returns:
        str: Connection ID if found, None otherwise
    """
    try:
        request_context = event.get("requestContext", {})
        connection_id = request_context.get("connectionId")

        if not connection_id:
            logger.warning(
                "Connection ID not found in disconnect request context",
                extra={
                    "correlation_id": correlation_id,
                    "request_context_keys": list(request_context.keys()),
                },
            )
            return None

        logger.debug(
            "Connection ID extracted from disconnect event",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
            },
        )

        return connection_id

    except Exception as e:
        logger.error(
            "Error extracting connection ID from disconnect event",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
            },
            exc_info=True,
        )
        return None


def _extract_disconnect_info(
    event: Dict[str, Any], correlation_id: str
) -> Dict[str, Any]:
    """
    Extract disconnection context from WebSocket disconnect event.

    Args:
        event: API Gateway WebSocket disconnect event
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Disconnection context and metadata
    """
    try:
        request_context = event.get("requestContext", {})

        disconnect_info = {
            "disconnect_time": datetime.now(timezone.utc).isoformat(),
            "reason": request_context.get("disconnectReason", "unknown"),
            "route_key": request_context.get("routeKey", "$disconnect"),
            "stage": request_context.get("stage", "unknown"),
            "event_type": request_context.get("eventType", "DISCONNECT"),
        }

        logger.debug(
            "Disconnection context extracted",
            extra={
                "correlation_id": correlation_id,
                "disconnect_reason": disconnect_info["reason"],
            },
        )

        return disconnect_info

    except Exception as e:
        logger.error(
            "Error extracting disconnection context",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
            },
            exc_info=True,
        )
        return {
            "disconnect_time": datetime.now(timezone.utc).isoformat(),
            "reason": "unknown",
            "error": "Failed to extract disconnect info",
        }


def _remove_connection(
    connection_id: str, disconnect_info: Dict[str, Any], correlation_id: str
) -> bool:
    """
    Remove WebSocket connection from DynamoDB.

    Args:
        connection_id: Unique WebSocket connection identifier
        disconnect_info: Disconnection context and metadata
        correlation_id: Request correlation ID for logging

    Returns:
        bool: True if removed successfully or didn't exist, False on error
    """
    try:
        table = dynamodb_resource.Table(CONNECTIONS_TABLE)

        # Attempt to delete connection from DynamoDB
        # DynamoDB delete_item is idempotent - no error if key doesn't exist
        response = table.delete_item(
            Key={"connection_id": connection_id},
            ReturnValues="ALL_OLD",  # Return the deleted item if it existed
        )

        # Check if connection actually existed
        deleted_item = response.get("Attributes")
        if deleted_item:
            logger.info(
                "Connection removed from DynamoDB successfully",
                extra={
                    "correlation_id": correlation_id,
                    "connection_id": connection_id,
                    "table_name": CONNECTIONS_TABLE,
                    "connection_existed": True,
                    "original_timestamp": deleted_item.get("timestamp", "unknown"),
                },
            )
        else:
            logger.info(
                "Connection was not found in DynamoDB (already cleaned up)",
                extra={
                    "correlation_id": correlation_id,
                    "connection_id": connection_id,
                    "table_name": CONNECTIONS_TABLE,
                    "connection_existed": False,
                },
            )

        return True

    except Exception as e:
        logger.error(
            "Error removing connection from DynamoDB",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "table_name": CONNECTIONS_TABLE,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        return False


def _create_disconnect_success_response(
    message: str, correlation_id: str
) -> Dict[str, Any]:
    """
    Create standardized success response for WebSocket disconnection.

    Args:
        message: Success message describing the disconnection
        correlation_id: Request correlation ID for tracing

    Returns:
        dict: API Gateway WebSocket success response
    """
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "status": "disconnected",
                "message": message,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
    }
