# =============================================================================
# BuildingOS Platform - Common Data Models
# =============================================================================
#
# **Purpose:** Shared data structures and models for Lambda functions
# **Scope:** Provides standardized data classes for inter-service communication
# **Usage:** Import and use common models across all Lambda functions
#
# **Key Features:**
# - Standardized message formats for SNS communication
# - Common data structures for DynamoDB operations
# - Type safety with dataclasses and type hints
# - Validation methods for data integrity
# - ACP (Agent Communication Protocol) compliance
#
# **Dependencies:** Standard library dataclasses and typing modules
# **Integration:** Used across all BuildingOS Lambda functions for consistency
#
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json

# =============================================================================
# Enums for Standardized Values
# =============================================================================


class TaskStatus(Enum):
    """Task execution status values"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionStatus(Enum):
    """Mission execution status values"""

    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Available agent types"""

    ELEVATOR = "agent_elevator"
    PSIM = "agent_psim"
    PERSONA = "agent_persona"
    DIRECTOR = "agent_director"
    COORDINATOR = "agent_coordinator"
    HEALTH_CHECK = "agent_health_check"


# =============================================================================
# SNS Message Models
# =============================================================================


@dataclass
class SNSMessage:
    """
    Base SNS message structure for inter-service communication

    Provides standardized format for all SNS messages with correlation tracking
    and metadata for debugging and monitoring.
    """

    message_type: str
    correlation_id: str
    timestamp: str
    source_service: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SNS publishing"""
        return {
            "message_type": self.message_type,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "source_service": self.source_service,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class TaskMessage(SNSMessage):
    """
    Task-specific SNS message for agent coordination

    Extends base SNS message with task-specific fields for agent task execution.
    """

    mission_id: str = ""
    task_id: str = ""
    agent: str = ""
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self):
        """Set message type for task messages"""
        self.message_type = "task"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with task-specific fields"""
        base_dict = super().to_dict()
        base_dict["data"].update(
            {
                "mission_id": self.mission_id,
                "task_id": self.task_id,
                "agent": self.agent,
                "action": self.action,
                "parameters": self.parameters,
                "status": (
                    self.status.value
                    if isinstance(self.status, TaskStatus)
                    else self.status
                ),
            }
        )
        return base_dict


@dataclass
class MissionMessage(SNSMessage):
    """
    Mission-specific SNS message for mission coordination

    Extends base SNS message with mission-specific fields for mission planning
    and execution coordination.
    """

    mission_id: str = ""
    user_id: str = ""
    user_message: str = ""
    status: MissionStatus = MissionStatus.CREATED
    tasks: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Set message type for mission messages"""
        self.message_type = "mission"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with mission-specific fields"""
        base_dict = super().to_dict()
        base_dict["data"].update(
            {
                "mission_id": self.mission_id,
                "user_id": self.user_id,
                "user_message": self.user_message,
                "status": (
                    self.status.value
                    if isinstance(self.status, MissionStatus)
                    else self.status
                ),
                "tasks": self.tasks,
            }
        )
        return base_dict


# =============================================================================
# DynamoDB Models
# =============================================================================


@dataclass
class DynamoDBItem:
    """
    Base class for DynamoDB items with common fields

    Provides standardized structure for all DynamoDB table items with
    audit fields and consistent formatting.
    """

    # All fields have defaults to allow proper inheritance
    created_at: str = ""
    updated_at: str = ""
    ttl: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item format"""
        item = {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
        if self.ttl:
            item["ttl"] = self.ttl
        return item


@dataclass
class WebSocketConnection(DynamoDBItem):
    """
    WebSocket connection record for DynamoDB storage

    Represents an active WebSocket connection with user context
    and connection metadata for message routing.
    """

    # All fields must have defaults when inheriting from a class with default fields
    connection_id: str = ""
    user_id: Optional[str] = None
    connected_at: Optional[str] = None
    last_activity: Optional[str] = None

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item with connection-specific fields"""
        item = super().to_dynamodb_item()
        item.update(
            {
                "connection_id": self.connection_id,
                "user_id": self.user_id,
                "connected_at": self.connected_at,
                "last_activity": self.last_activity,
            }
        )
        return item


@dataclass
class MissionState(DynamoDBItem):
    """
    Mission state record for DynamoDB storage

    Represents the current state of a mission including tasks,
    status, and execution history.
    """

    # All fields must have defaults when inheriting from a class with default fields
    mission_id: str = ""
    user_id: str = ""
    user_message: str = ""
    status: MissionStatus = MissionStatus.CREATED
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item with mission-specific fields"""
        item = super().to_dynamodb_item()
        item.update(
            {
                "mission_id": self.mission_id,
                "user_id": self.user_id,
                "user_message": self.user_message,
                "status": self.status.value,
                "tasks": self.tasks,
                "results": self.results,
            }
        )
        return item


@dataclass
class ShortTermMemory(DynamoDBItem):
    """
    Short-term memory record for DynamoDB storage

    Represents user conversation context and temporary data
    with automatic expiration.
    """

    # All fields must have defaults when inheriting from a class with default fields
    user_id: str = ""
    conversation_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item with memory-specific fields"""
        item = super().to_dynamodb_item()
        item.update(
            {
                "user_id": self.user_id,
                "conversation_data": self.conversation_data,
                "context": self.context,
            }
        )
        return item


@dataclass
class ElevatorMonitoring(DynamoDBItem):
    """
    Elevator monitoring record for DynamoDB storage

    Represents elevator status, performance metrics, and
    operational data for building automation.
    """

    # All fields must have defaults when inheriting from a class with default fields
    elevator_id: str = ""
    status: str = ""
    floor: Optional[int] = None
    direction: Optional[str] = None
    last_maintenance: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item with elevator-specific fields"""
        item = super().to_dynamodb_item()
        item.update(
            {
                "elevator_id": self.elevator_id,
                "status": self.status,
                "floor": self.floor,
                "direction": self.direction,
                "last_maintenance": self.last_maintenance,
                "performance_metrics": self.performance_metrics,
            }
        )
        return item


# =============================================================================
# API Response Models
# =============================================================================


@dataclass
class APIResponse:
    """
    Standardized API response format for Lambda functions

    Provides consistent response structure for API Gateway integration
    with proper HTTP status codes and CORS headers.
    """

    success: bool
    data: Any = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: Optional[str] = None

    def to_api_gateway_response(self, status_code: int = None) -> Dict[str, Any]:
        """Convert to API Gateway response format"""
        if status_code is None:
            status_code = 200 if self.success else 500

        body_data = {"success": self.success, "timestamp": self.timestamp}

        if self.success:
            body_data["data"] = self.data
        else:
            body_data["error"] = {
                "message": self.error_message,
                "code": self.error_code,
            }

        if self.correlation_id:
            body_data["correlation_id"] = self.correlation_id

        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps(body_data, default=str),
        }


# Additional model classes required by Lambda functions
@dataclass
class ConversationState:
    """Conversation state model for persona agent"""

    user_id: str = ""
    conversation_id: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    last_message: str = ""
    timestamp: str = ""


@dataclass
class MissionPlan:
    """Mission plan model for director agent"""

    mission_id: str = ""
    user_id: str = ""
    plan: Dict[str, Any] = field(default_factory=dict)
    status: str = "created"
    timestamp: str = ""


@dataclass
class TaskExecution:
    """Task execution model for coordinator agent"""

    task_id: str = ""
    mission_id: str = ""
    agent: str = ""
    status: str = "pending"
    result: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class TaskResult:
    """Task result model for agent responses"""

    task_id: str = ""
    agent: str = ""
    success: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    timestamp: str = ""


# Health Status Enumeration for Health Check Agent
class HealthStatus(Enum):
    """Health status enumeration for system health monitoring"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    WARNING = "warning"
    UNKNOWN = "unknown"


# Connection State Enumeration for WebSocket Management
class ConnectionState(Enum):
    """Connection state enumeration for WebSocket connection management"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ConnectionState:
    """Connection state model for WebSocket functions"""

    connection_id: str = ""
    user_id: str = ""
    status: str = "connected"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIGatewayResponse:
    """API Gateway response model for WebSocket functions"""

    status_code: int = 200
    body: str = ""
    headers: Dict[str, str] = field(default_factory=dict)


# Legacy compatibility aliases
UserIntention = ConversationState
AgentCapability = Dict[str, Any]
ElevatorOperation = Dict[str, Any]
PSIMOperation = Dict[str, Any]


# =============================================================================
# ACP Protocol Integration
# =============================================================================


def convert_task_message_to_acp(task_message: TaskMessage) -> Dict[str, Any]:
    """Convert legacy TaskMessage to ACP standard format"""
    return {
        "header": {
            "message_type": "task",
            "source_agent": task_message.source_service,
            "correlation_id": task_message.correlation_id,
            "timestamp": task_message.timestamp,
        },
        "payload": {
            "action": task_message.action,
            "data": {
                "task_id": task_message.task_id,
                "mission_id": task_message.mission_id,
                "parameters": task_message.parameters,
                "assigned_agent": task_message.agent,
            },
            "metadata": task_message.metadata,
        },
        "status": (
            task_message.status.value
            if isinstance(task_message.status, TaskStatus)
            else task_message.status
        ),
    }


def convert_task_result_to_acp(task_result: TaskResult) -> Dict[str, Any]:
    """Convert legacy TaskResult to ACP standard format"""
    return {
        "header": {
            "message_type": "result",
            "source_agent": task_result.agent,
            "timestamp": task_result.timestamp,
        },
        "payload": {
            "action": f"result_{task_result.task_id}",
            "data": {
                "task_id": task_result.task_id,
                "result": task_result.data,
                "success": task_result.success,
                "error_message": (
                    task_result.error_message if task_result.error_message else None
                ),
            },
            "metadata": {"agent_type": task_result.agent},
        },
        "status": "completed" if task_result.success else "failed",
    }


def is_acp_message(message: Dict[str, Any]) -> bool:
    """Check if a message follows ACP standard format"""
    return (
        isinstance(message, dict)
        and "header" in message
        and "message_type" in message.get("header", {})
        and message["header"]["message_type"]
        in ["task", "result", "event", "heartbeat", "request", "response", "error"]
    )


# Final missing model classes for 100% Step 2.3 completion
@dataclass
class TaskDefinition:
    """Task definition model for director agent mission planning"""

    task_id: str = ""
    task_type: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 1
    estimated_duration: int = 0  # in seconds
    required_agent: str = ""


@dataclass
class ComponentHealth:
    """Component health model for health check agent monitoring"""

    component_name: str = ""
    status: str = "unknown"  # healthy, unhealthy, warning, unknown
    last_check: str = ""
    response_time: float = 0.0
    error_count: int = 0
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemHealth:
    """System health model for overall health monitoring"""

    system_status: str = "unknown"  # healthy, degraded, unhealthy
    components: List[ComponentHealth] = field(default_factory=list)
    overall_score: float = 0.0
    timestamp: str = ""
    alerts: List[str] = field(default_factory=list)
