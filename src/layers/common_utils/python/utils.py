# =============================================================================
# BuildingOS Platform - Common Utilities
# =============================================================================
#
# **Purpose:** Shared utility functions for all Lambda functions
# **Scope:** Provides standardized helper functions for common operations
# **Usage:** Import specific utilities needed by Lambda functions
#
# **Key Features:**
# - JSON serialization with Decimal support (DynamoDB compatibility)
# - Standardized logging configuration
# - Error handling utilities
# - Environment variable helpers
# - Architecture detection utilities
#
# **Dependencies:** Standard library modules only (performance optimized)
# **Integration:** Used across all BuildingOS Lambda functions for consistency
#
# =============================================================================

import json
import os
import logging
import uuid
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional, Union

# =============================================================================
# JSON Serialization Utilities
# =============================================================================


def decimal_default(obj: Any) -> Union[float, Any]:
    """
    JSON serializer function that handles Decimal objects from DynamoDB

    DynamoDB returns numeric values as Decimal objects which are not JSON serializable.
    This function converts Decimal objects to float for JSON compatibility.

    Args:
        obj: Object to serialize (typically from DynamoDB response)

    Returns:
        float: Converted decimal value

    Raises:
        TypeError: If object is not a Decimal type

    Example:
        json.dumps(dynamodb_response, default=decimal_default)
    """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Safe JSON serialization with Decimal support

    Provides a standardized way to serialize data that may contain Decimal objects
    from DynamoDB operations.

    Args:
        data: Data to serialize
        **kwargs: Additional arguments passed to json.dumps()

    Returns:
        str: JSON string representation

    Example:
        json_str = safe_json_dumps({"price": Decimal("19.99")})
    """
    return json.dumps(data, default=decimal_default, **kwargs)


def safe_json_loads(json_str: str, **kwargs) -> Any:
    """
    Safe JSON deserialization with error handling

    Args:
        json_str: JSON string to parse
        **kwargs: Additional arguments passed to json.loads()

    Returns:
        Any: Parsed JSON data

    Raises:
        ValueError: If JSON string is invalid
    """
    try:
        return json.loads(json_str, **kwargs)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}")


# =============================================================================
# Logging Utilities
# =============================================================================


def setup_logging(level: str = None) -> logging.Logger:
    """
    Setup standardized logging for Lambda functions

    Configures logging with consistent format and level across all functions.
    Uses LOG_LEVEL environment variable if level not specified.

    Args:
        level: Optional logging level override

    Returns:
        logging.Logger: Configured logger instance

    Example:
        logger = setup_logging()
        logger.info("Function started")
    """
    if level is None:
        level = os.environ.get("LOG_LEVEL", "INFO")

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return logging.getLogger()


# =============================================================================
# Environment Variable Utilities
# =============================================================================


def get_required_env(var_name: str) -> str:
    """
    Get a required environment variable.

    Retrieves an environment variable and raises an error if it's not found.

    Args:
        var_name: The name of the environment variable

    Returns:
        The value of the environment variable

    Raises:
        ValueError: If the environment variable is not set

    Example:
        >>> database_url = get_required_env('DATABASE_URL')
    """
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    return value


def get_required_env_var(var_name: str) -> str:
    """
    Get a required environment variable (alias for compatibility).

    This function is deprecated. Use get_required_env() instead.
    Maintained for backward compatibility with existing Lambda functions.

    Args:
        var_name: The name of the environment variable

    Returns:
        The value of the environment variable

    Raises:
        ValueError: If the environment variable is not set
    """
    return get_required_env(var_name)


def get_optional_env(var_name: str, default: str = None) -> Optional[str]:
    """
    Get an optional environment variable with a default value.

    Retrieves an environment variable and returns the default if not found.

    Args:
        var_name: The name of the environment variable
        default: Default value if environment variable is not set

    Returns:
        The value of the environment variable or the default value

    Example:
        >>> debug_mode = get_optional_env('DEBUG_MODE', 'false')
    """
    return os.getenv(var_name, default)


def get_optional_env_var(var_name: str, default: str = None) -> Optional[str]:
    """
    Get an optional environment variable with a default value (alias for compatibility).

    This function is deprecated. Use get_optional_env() instead.
    Maintained for backward compatibility with existing Lambda functions.

    Args:
        var_name: The name of the environment variable
        default: Default value if environment variable is not set

    Returns:
        The value of the environment variable or the default value
    """
    return get_optional_env(var_name, default)


# =============================================================================
# Architecture Detection Utilities
# =============================================================================


def detect_architecture_mode() -> Dict[str, bool]:
    """
    Detect the current architecture mode based on environment variables.

    Analyzes environment variables to determine if the Lambda function is running
    in event-driven (SNS-based) or API-driven (HTTP API) architecture mode.

    Returns:
        Dict[str, bool]: Architecture mode flags
            - event_driven: True if SNS topics are configured
            - api_driven: True if API Gateway endpoints are available
            - hybrid_mode: True if both modes are available

    Example:
        >>> mode = detect_architecture_mode()
        >>> if mode["event_driven"]:
        ...     print("Using SNS-based event architecture")
    """
    # Common SNS topic patterns
    sns_topic_names = [
        # Current BuildingOS topics
        "COORDINATOR_TASK_TOPIC_ARN",
        "AGENT_TASK_RESULT_TOPIC_ARN",
        "PERSONA_INTENTION_TOPIC_ARN",
        "PERSONA_RESPONSE_TOPIC_ARN",
        "DIRECTOR_MISSION_TOPIC_ARN",
        "DIRECTOR_RESPONSE_TOPIC_ARN",
        "CHAT_INTENTION_TOPIC_ARN",
        "COORDINATOR_MISSION_RESULT_TOPIC_ARN",
        # ACP Standard topics
        "ACP_TASK_TOPIC_ARN",
        "ACP_RESULT_TOPIC_ARN",
        "ACP_EVENT_TOPIC_ARN",
        "ACP_HEARTBEAT_TOPIC_ARN",
    ]

    # Check if any SNS topics are configured
    has_sns_topics = any(os.environ.get(topic_name) for topic_name in sns_topic_names)

    # Check for legacy Lambda function environment
    has_api_gateway = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

    return {
        "event_driven": has_sns_topics,
        "api_driven": has_api_gateway,
        "hybrid_mode": has_sns_topics and has_api_gateway,
    }


# =============================================================================
# ID Generation Utilities
# =============================================================================


def generate_correlation_id() -> str:
    """
    Generate unique correlation ID for request tracking

    Returns:
        str: Unique correlation ID for tracing requests across services

    Example:
        correlation_id = generate_correlation_id()
        logger.info(f"Processing request: {correlation_id}")
    """
    return str(uuid.uuid4())


def generate_timestamp() -> str:
    """
    Generate ISO format timestamp

    Returns:
        str: Current timestamp in ISO format with timezone

    Example:
        timestamp = generate_timestamp()
        # Returns: "2025-01-11T16:30:45.123456+00:00"
    """
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# Error Handling Utilities
# =============================================================================


def create_error_response(
    error_message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 500
) -> Dict[str, Any]:
    """
    Create standardized error response for Lambda functions

    Args:
        error_message: Human-readable error description
        error_code: Standardized error code for client handling
        status_code: HTTP status code for API Gateway integration

    Returns:
        Dict[str, Any]: Standardized error response format

    Example:
        return create_error_response("Invalid request format", "INVALID_REQUEST", 400)
    """
    return {
        "statusCode": status_code,
        "body": safe_json_dumps(
            {
                "error": True,
                "error_code": error_code,
                "message": error_message,
                "timestamp": generate_timestamp(),
                "correlation_id": generate_correlation_id(),
            }
        ),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        },
    }


def create_success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """
    Create a standardized success response for API endpoints.

    Args:
        data: The response data to include
        status_code: HTTP status code (default: 200)

    Returns:
        Standardized success response dictionary

    Example:
        >>> response = create_success_response({"user_id": 123}, 201)
        >>> print(response["statusCode"])
        201
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        },
        "body": safe_json_dumps(
            {"success": True, "data": data, "timestamp": generate_timestamp()}
        ),
    }


def serialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a Python dictionary to DynamoDB item format.

    Converts Python types to DynamoDB attribute value format for storing items.
    Handles nested structures, lists, and various data types.

    Args:
        item: Python dictionary to serialize for DynamoDB

    Returns:
        DynamoDB-formatted item dictionary

    Example:
        >>> item = {"name": "John", "age": 30, "active": True}
        >>> serialized = serialize_dynamodb_item(item)
        >>> print(serialized["name"]["S"])
        John
    """

    def _serialize_value(value: Any) -> Dict[str, Any]:
        """Serialize a single value to DynamoDB format."""
        if value is None:
            return {"NULL": True}
        elif isinstance(value, bool):
            return {"BOOL": value}
        elif isinstance(value, str):
            return {"S": value}
        elif isinstance(value, (int, float)):
            return {"N": str(value)}
        elif isinstance(value, list):
            return {"L": [_serialize_value(v) for v in value]}
        elif isinstance(value, dict):
            return {"M": {k: _serialize_value(v) for k, v in value.items()}}
        elif isinstance(value, set):
            if all(isinstance(v, str) for v in value):
                return {"SS": list(value)}
            elif all(isinstance(v, (int, float)) for v in value):
                return {"NS": [str(v) for v in value]}
            else:
                # Mixed set, convert to list
                return {"L": [_serialize_value(v) for v in value]}
        else:
            # Fallback to string representation
            return {"S": str(value)}

    return {k: _serialize_value(v) for k, v in item.items()}


def deserialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deserialize a DynamoDB item to Python dictionary format.

    Converts DynamoDB attribute value format back to standard Python types.
    Handles nested structures, lists, and various data types.

    Args:
        item: DynamoDB-formatted item dictionary

    Returns:
        Python dictionary with standard types

    Example:
        >>> ddb_item = {"name": {"S": "John"}, "age": {"N": "30"}}
        >>> deserialized = deserialize_dynamodb_item(ddb_item)
        >>> print(deserialized["name"])
        John
    """

    def _deserialize_value(value: Dict[str, Any]) -> Any:
        """Deserialize a single DynamoDB value."""
        if "NULL" in value:
            return None
        elif "BOOL" in value:
            return value["BOOL"]
        elif "S" in value:
            return value["S"]
        elif "N" in value:
            num_str = value["N"]
            return int(num_str) if "." not in num_str else float(num_str)
        elif "L" in value:
            return [_deserialize_value(v) for v in value["L"]]
        elif "M" in value:
            return {k: _deserialize_value(v) for k, v in value["M"].items()}
        elif "SS" in value:
            return set(value["SS"])
        elif "NS" in value:
            return set(int(n) if "." not in n else float(n) for n in value["NS"])
        else:
            # Unknown type, return as-is
            return value

    return {k: _deserialize_value(v) for k, v in item.items()}
