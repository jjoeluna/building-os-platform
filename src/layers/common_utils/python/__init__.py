# =============================================================================
# BuildingOS Platform - Common Utils Layer
# =============================================================================
#
# **Purpose:** Lambda layer initialization and exports
# **Scope:** Provides centralized access to all common utilities and models
# **Usage:** Import from this layer in Lambda functions
#
# **Available Modules:**
# - aws_clients: Standardized AWS client management
# - utils: Common utility functions (JSON, logging, environment, etc.)
# - models: Shared data models and structures
# - acp_protocol: Agent Communication Protocol for standardized messaging
#
# **Example Usage:**
#   from common_utils import get_dynamodb, get_sns, decimal_default
#   from common_utils.models import TaskMessage, MissionStatus
#   from common_utils.utils import setup_logging, create_success_response
#
# =============================================================================

# Import and expose commonly used functions for easy access
from .aws_clients import AWSClients, get_dynamodb, get_sns, get_bedrock, get_lambda

from .utils import (
    decimal_default,
    safe_json_dumps,
    safe_json_loads,
    setup_logging,
    get_required_env,
    get_optional_env,
    detect_architecture_mode,
    generate_correlation_id,
    generate_timestamp,
    create_error_response,
    create_success_response,
)

# Models are typically imported explicitly when needed
from . import models

# ACP Protocol for standardized agent communication
from . import acp_protocol

# Version information for layer tracking
__version__ = "1.0.0"
__layer_name__ = "common-utils"

# Export commonly used items at package level for convenience
__all__ = [
    # AWS Clients
    "AWSClients",
    "get_dynamodb",
    "get_sns",
    "get_bedrock",
    "get_lambda",
    # Utilities
    "decimal_default",
    "safe_json_dumps",
    "safe_json_loads",
    "setup_logging",
    "get_required_env",
    "get_optional_env",
    "detect_architecture_mode",
    "generate_correlation_id",
    "generate_timestamp",
    "create_error_response",
    "create_success_response",
    # Models module
    "models",
    # ACP Protocol module
    "acp_protocol",
]
