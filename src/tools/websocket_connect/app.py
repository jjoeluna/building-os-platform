# =============================================================================
# BuildingOS Platform - WebSocket Connect Handler
# =============================================================================
#
# **Purpose:** Establishes WebSocket connections for real-time chat communication
# **Scope:** Manages connection lifecycle and persistent connection storage
# **Usage:** Invoked by API Gateway WebSocket API when clients connect
#
# **Key Features:**
# - Handles WebSocket connection establishment from web clients
# - Stores connection metadata in DynamoDB for message routing
# - Validates connection requests and manages connection state
# - Tracks connection timestamps and client information
# - Uses common utilities layer for AWS client management
# - Implements enterprise-grade error handling and logging
#
# **Connection Flow:**
# 1. Client initiates WebSocket connection to API Gateway
# 2. API Gateway invokes this Lambda with connection event
# 3. Connection ID extracted from API Gateway request context
# 4. Connection metadata stored in DynamoDB connections table
# 5. Success response returned to complete connection establishment
#
# **Data Storage:**
# - Table: connections (DynamoDB)
# - Key: connectionId (string) - Unique WebSocket connection identifier
# - Attributes: timestamp, client_info, connection_state
#
# **Dependencies:**
# - Common utilities layer for DynamoDB client management
# - DynamoDB connections table for persistent connection storage
# - API Gateway WebSocket API for connection management
#
# **Integration:**
# - Triggers: API Gateway WebSocket $connect route
# - Storage: DynamoDB connections table
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
# - Error Handling: Structured error responses with correlation IDs
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
from models import WebSocketConnection

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
CONNECTIONS_TABLE = get_required_env_var("CONNECTIONS_TABLE")
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
dynamodb_resource = get_dynamodb_resource()

# Validate DynamoDB table configuration
logger.info(
    "WebSocket Connect handler initialized",
    extra={
        "connections_table": CONNECTIONS_TABLE,
        "environment": ENVIRONMENT,
        "dynamodb_resource": "initialized",
    },
)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    WebSocket Connect Handler with enhanced connection management.

    Establishes WebSocket connections and stores connection metadata in DynamoDB
    for persistent connection tracking and message routing capabilities.

    Args:
        event: API Gateway WebSocket connect event
            Required fields:
            - requestContext.connectionId: Unique WebSocket connection ID
            - requestContext.routeKey: Route key (should be '$connect')
            - requestContext.eventType: Event type (should be 'CONNECT')
            Optional fields:
            - headers: Client headers (User-Agent, Origin, etc.)
            - queryStringParameters: Connection query parameters
        context: Lambda runtime context information

    Returns:
        dict: HTTP response for API Gateway WebSocket
            Success: {"statusCode": 200, "body": "Connected"}
            Error: {"statusCode": 4xx/5xx, "body": error_details}

    Connection Storage:
        Stores in DynamoDB connections table:
        - connectionId: Unique identifier from API Gateway
        - timestamp: Connection establishment time (ISO format)
        - client_info: Headers and metadata from connection request
        - connection_state: CONNECTED status
        - ttl: Time-to-live for automatic cleanup

    Error Handling:
        - Missing connection ID: 400 Bad Request
        - DynamoDB errors: 500 Internal Server Error
        - Invalid event format: 400 Bad Request
        - All errors logged with correlation IDs

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "WebSocket connection establishment started",
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
            return _create_connection_error_response(
                400, "Missing connection ID in request", correlation_id
            )

        # Extract client information for connection tracking
        client_info = _extract_client_info(event, correlation_id)

        # Store connection in DynamoDB
        connection_stored = _store_connection(
            connection_id, client_info, correlation_id
        )

        if not connection_stored:
            return _create_connection_error_response(
                500, "Failed to store connection", correlation_id
            )

        # Log successful connection establishment
        logger.info(
            "WebSocket connection established successfully",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "client_user_agent": client_info.get("user_agent", "unknown"),
                "client_origin": client_info.get("origin", "unknown"),
            },
        )

        # Return success response to API Gateway
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "connected",
                    "connection_id": connection_id,
                    "correlation_id": correlation_id,
                }
            ),
        }

    except Exception as e:
        logger.error(
            "Critical error in WebSocket connect handler",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        return _create_connection_error_response(
            500, "Internal server error during connection", correlation_id
        )


def _extract_connection_id(event: Dict[str, Any], correlation_id: str) -> Optional[str]:
    """
    Extract connection ID from API Gateway WebSocket event.

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
                "Connection ID not found in request context",
                extra={
                    "correlation_id": correlation_id,
                    "request_context_keys": list(request_context.keys()),
                },
            )
            return None

        logger.debug(
            "Connection ID extracted successfully",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
            },
        )

        return connection_id

    except Exception as e:
        logger.error(
            "Error extracting connection ID",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
            },
            exc_info=True,
        )
        return None


def _extract_client_info(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Extract client information from WebSocket connection event.

    Args:
        event: API Gateway WebSocket event
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Client information including headers and metadata
    """
    try:
        headers = event.get("headers", {})
        query_params = event.get("queryStringParameters") or {}
        request_context = event.get("requestContext", {})

        client_info = {
            "user_agent": headers.get("User-Agent", "unknown"),
            "origin": headers.get("Origin", "unknown"),
            "host": headers.get("Host", "unknown"),
            "connection_time": datetime.now(timezone.utc).isoformat(),
            "route_key": request_context.get("routeKey", "$connect"),
            "stage": request_context.get("stage", "unknown"),
            "query_parameters": query_params,
        }

        logger.debug(
            "Client information extracted",
            extra={
                "correlation_id": correlation_id,
                "user_agent": client_info["user_agent"],
                "origin": client_info["origin"],
            },
        )

        return client_info

    except Exception as e:
        logger.error(
            "Error extracting client information",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
            },
            exc_info=True,
        )
        return {
            "user_agent": "unknown",
            "origin": "unknown",
            "connection_time": datetime.now(timezone.utc).isoformat(),
            "error": "Failed to extract client info",
        }


def _store_connection(
    connection_id: str, client_info: Dict[str, Any], correlation_id: str
) -> bool:
    """
    Store WebSocket connection in DynamoDB.

    Args:
        connection_id: Unique WebSocket connection identifier
        client_info: Client metadata and connection details
        correlation_id: Request correlation ID for logging

    Returns:
        bool: True if stored successfully, False otherwise
    """
    try:
        table = dynamodb_resource.Table(CONNECTIONS_TABLE)

        # Calculate TTL for automatic cleanup (24 hours from now)
        ttl_timestamp = int((datetime.now(timezone.utc).timestamp()) + (24 * 60 * 60))

        # Prepare connection item for DynamoDB
        connection_item = {
            "connection_id": connection_id,  # Match DynamoDB table schema (snake_case)
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "connection_state": "connected",  # Use simple string instead of enum
            "client_info": client_info,
            "ttl": ttl_timestamp,
            "correlation_id": correlation_id,
        }

        # Store connection in DynamoDB
        table.put_item(Item=connection_item)

        logger.info(
            "Connection stored in DynamoDB successfully",
            extra={
                "correlation_id": correlation_id,
                "connection_id": connection_id,
                "table_name": CONNECTIONS_TABLE,
                "ttl": ttl_timestamp,
            },
        )

        return True

    except Exception as e:
        logger.error(
            "Error storing connection in DynamoDB",
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


def _create_connection_error_response(
    status_code: int, error_message: str, correlation_id: str
) -> Dict[str, Any]:
    """
    Create standardized error response for WebSocket connection failures.

    Args:
        status_code: HTTP status code for the error
        error_message: Human-readable error description
        correlation_id: Request correlation ID for tracing

    Returns:
        dict: API Gateway WebSocket error response
    """
    return {
        "statusCode": status_code,
        "body": json.dumps(
            {
                "error": error_message,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
    }
