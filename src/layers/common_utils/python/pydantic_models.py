# =============================================================================
# BuildingOS Platform - Pydantic Data Models (Version 2.0)
# =============================================================================
#
# **Purpose:** Enterprise-grade data validation with Pydantic BaseModel
# **Scope:** Type-safe data structures with automatic validation for all services
# **Usage:** Import and use Pydantic models across all Lambda functions
#
# **Key Features:**
# - Automatic data validation with detailed error messages
# - Type-safe serialization/deserialization
# - Field-level validation with constraints
# - Enhanced API integration with structured responses
# - Performance-optimized validation
#
# **Dependencies:** Pydantic v2+ for advanced validation capabilities
# **Integration:** Gradual migration from dataclasses to Pydantic models
# **Migration Strategy:** Maintain backward compatibility during transition
#
# =============================================================================

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json

# =============================================================================
# Enums for Standardized Values (Compatible with existing)
# =============================================================================

class TaskStatus(Enum):
    """Task execution status values - Enhanced with Pydantic compatibility"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionStatus(Enum):
    """Mission execution status values - Enhanced with Pydantic compatibility"""
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Available agent types - Enhanced with Pydantic compatibility"""
    ELEVATOR = "agent_elevator"
    PSIM = "agent_psim"
    PERSONA = "agent_persona"
    DIRECTOR = "agent_director"
    COORDINATOR = "agent_coordinator"
    HEALTH_CHECK = "agent_health_check"


class HealthStatus(Enum):
    """Health status enumeration for system health monitoring"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    WARNING = "warning"
    UNKNOWN = "unknown"


class ConnectionState(Enum):
    """Connection state enumeration for WebSocket connection management"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


# =============================================================================
# Pydantic Configuration
# =============================================================================

class BuildingOSConfig:
    """Base configuration for all BuildingOS Pydantic models"""
    model_config = ConfigDict(
        # Enable validation for assignment
        validate_assignment=True,
        # Use enum values in serialization
        use_enum_values=True,
        # Allow extra fields for backward compatibility
        extra='allow',
        # Validate default values
        validate_default=True,
        # Custom JSON encoders
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        }
    )


# =============================================================================
# Core SNS Message Models (Phase 2.5.1)
# =============================================================================

class SNSMessage(BaseModel):
    """
    Base SNS message structure for inter-service communication with Pydantic validation
    
    Provides standardized format for all SNS messages with automatic validation,
    correlation tracking, and enhanced metadata for debugging and monitoring.
    """
    model_config = BuildingOSConfig.model_config
    
    message_type: str = Field(..., min_length=1, description="Type of SNS message")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique correlation ID for request tracing"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp in UTC"
    )
    source_service: str = Field(..., min_length=1, description="Source service name")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message payload data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('correlation_id')
    @classmethod
    def validate_correlation_id(cls, v: str) -> str:
        """Validate correlation ID format"""
        if not v or len(v) < 8:
            raise ValueError('Correlation ID must be at least 8 characters')
        return v
    
    @field_validator('source_service')
    @classmethod
    def validate_source_service(cls, v: str) -> str:
        """Validate source service name"""
        if not v.startswith(('agent_', 'websocket_', 'tool_')):
            raise ValueError('Source service must start with agent_, websocket_, or tool_')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SNS publishing with enhanced serialization"""
        return self.model_dump(by_alias=True, exclude_none=True)
    
    def to_json(self) -> str:
        """Convert to JSON string for SNS publishing"""
        return self.model_dump_json(by_alias=True, exclude_none=True)


class TaskMessage(SNSMessage):
    """
    Task-specific SNS message for agent coordination with Pydantic validation
    
    Extends base SNS message with task-specific fields and automatic validation
    for agent task execution coordination.
    """
    
    # Override message_type with literal for type safety
    message_type: Literal["task"] = "task"
    
    mission_id: str = Field(..., min_length=1, description="Mission identifier")
    task_id: str = Field(..., min_length=1, description="Task identifier")
    agent: AgentType = Field(..., description="Target agent type")
    action: str = Field(..., min_length=1, description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task execution status")
    
    @field_validator('mission_id', 'task_id')
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Validate mission and task IDs format"""
        if not v or len(v) < 8:
            raise ValueError('ID must be at least 8 characters')
        return v
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate action name"""
        allowed_actions = [
            'call_elevator', 'check_status', 'provision_access',
            'query_permissions', 'send_notification', 'update_state'
        ]
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {allowed_actions}')
        return v


class MissionMessage(SNSMessage):
    """
    Mission-specific SNS message for mission coordination with Pydantic validation
    
    Extends base SNS message with mission-specific fields and validation
    for mission planning and execution coordination.
    """
    
    # Override message_type with literal for type safety
    message_type: Literal["mission"] = "mission"
    
    mission_id: str = Field(..., min_length=1, description="Mission identifier")
    user_id: str = Field(..., min_length=1, description="User identifier")
    user_message: str = Field(..., min_length=1, max_length=2000, description="User message")
    status: MissionStatus = Field(default=MissionStatus.CREATED, description="Mission status")
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="Mission tasks")
    
    @field_validator('user_message')
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Validate user message content"""
        if not v.strip():
            raise ValueError('User message cannot be empty')
        return v.strip()
    
    @field_validator('tasks')
    @classmethod
    def validate_tasks(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate tasks structure"""
        for task in v:
            if 'task_id' not in task or 'action' not in task:
                raise ValueError('Each task must have task_id and action')
        return v


# =============================================================================
# API Gateway Models (Phase 2.5.2) - Complete Implementation
# =============================================================================

class PersonaRequest(BaseModel):
    """Request model for Persona agent API with comprehensive validation"""
    model_config = BuildingOSConfig.model_config
    
    user_message: str = Field(
        ..., 
        min_length=1, 
        max_length=2000, 
        description="User message for processing"
    )
    conversation_id: Optional[str] = Field(
        None, 
        min_length=8, 
        description="Conversation identifier for context"
    )
    user_id: str = Field(..., min_length=1, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    
    @field_validator('user_message')
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Validate and clean user message"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('User message cannot be empty or whitespace only')
        return cleaned


class PersonaResponse(BaseModel):
    """Response model for Persona agent API with structured output"""
    model_config = BuildingOSConfig.model_config
    
    response: str = Field(..., min_length=1, description="Agent response message")
    conversation_id: str = Field(..., description="Conversation identifier")
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Response correlation ID"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class DirectorRequest(BaseModel):
    """Request model for Director agent API with mission planning validation"""
    model_config = BuildingOSConfig.model_config
    
    user_intention: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Processed user intention from Persona"
    )
    user_id: str = Field(..., min_length=1, description="User identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Mission context")
    priority: Literal["low", "medium", "high", "urgent"] = Field(
        default="medium", 
        description="Mission priority level"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")


class DirectorResponse(BaseModel):
    """Response model for Director agent API with structured mission plan"""
    model_config = BuildingOSConfig.model_config
    
    mission_id: str = Field(..., description="Generated mission identifier")
    mission_plan: Dict[str, Any] = Field(..., description="Detailed mission plan")
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="Mission tasks")
    estimated_duration: int = Field(gt=0, description="Estimated duration in seconds")
    required_agents: List[AgentType] = Field(default_factory=list, description="Required agents")
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Response correlation ID"
    )


class CoordinatorRequest(BaseModel):
    """Request model for Coordinator agent API with task coordination validation"""
    model_config = BuildingOSConfig.model_config
    
    mission_id: str = Field(..., min_length=8, description="Mission identifier")
    action: Literal["start_mission", "check_status", "cancel_mission"] = Field(
        ..., 
        description="Coordination action to perform"
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    user_id: str = Field(..., min_length=1, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")


class CoordinatorResponse(BaseModel):
    """Response model for Coordinator agent API with task status"""
    model_config = BuildingOSConfig.model_config
    
    mission_id: str = Field(..., description="Mission identifier")
    mission_status: MissionStatus = Field(..., description="Current mission status")
    task_results: List[Dict[str, Any]] = Field(default_factory=list, description="Task results")
    completion_percentage: int = Field(ge=0, le=100, description="Mission completion percentage")
    active_tasks: int = Field(ge=0, description="Number of active tasks")
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Response correlation ID"
    )


class PSIMRequest(BaseModel):
    """Request model for PSIM agent API with security validation"""
    model_config = BuildingOSConfig.model_config
    
    action: Literal["provision_access", "revoke_access", "check_permissions", "sync_users"] = Field(
        ..., 
        description="PSIM action to perform"
    )
    user_id: str = Field(..., min_length=1, description="Target user identifier")
    access_parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Access control parameters"
    )
    requester_id: str = Field(..., min_length=1, description="Requesting user identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    
    @field_validator('access_parameters')
    @classmethod
    def validate_access_parameters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate access parameters structure"""
        if 'access_level' in v and v['access_level'] not in ['guest', 'resident', 'admin', 'maintenance']:
            raise ValueError('Invalid access_level. Must be: guest, resident, admin, or maintenance')
        return v


class PSIMResponse(BaseModel):
    """Response model for PSIM agent API with security operation results"""
    model_config = BuildingOSConfig.model_config
    
    operation_result: Dict[str, Any] = Field(..., description="PSIM operation result")
    access_granted: bool = Field(..., description="Whether access was granted/confirmed")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    expiry_date: Optional[datetime] = Field(None, description="Access expiry date")
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Response correlation ID"
    )


class ElevatorRequest(BaseModel):
    """Request model for Elevator agent API with elevator control validation"""
    model_config = BuildingOSConfig.model_config
    
    action: Literal["call_elevator", "check_status", "emergency_stop"] = Field(
        ..., 
        description="Elevator action to perform"
    )
    floor: int = Field(ge=-5, le=50, description="Target floor number")
    user_id: str = Field(..., min_length=1, description="User requesting elevator")
    priority: Literal["normal", "high", "emergency"] = Field(
        default="normal", 
        description="Request priority"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    
    @field_validator('floor')
    @classmethod
    def validate_floor(cls, v: int) -> int:
        """Validate floor number is reasonable"""
        if v == 0:
            raise ValueError('Floor 0 is not valid. Use -1 for basement or 1 for ground floor')
        return v


class ElevatorResponse(BaseModel):
    """Response model for Elevator agent API with elevator status"""
    model_config = BuildingOSConfig.model_config
    
    elevator_id: str = Field(..., description="Elevator identifier")
    current_floor: int = Field(..., description="Current elevator floor")
    target_floor: int = Field(..., description="Target floor")
    estimated_arrival: int = Field(ge=0, description="Estimated arrival time in seconds")
    elevator_status: Literal["idle", "moving", "maintenance", "emergency"] = Field(
        ..., 
        description="Current elevator status"
    )
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Response correlation ID"
    )


class HealthCheckResponse(BaseModel):
    """Response model for Health Check endpoint with system status"""
    model_config = BuildingOSConfig.model_config
    
    service: str = Field(default="BuildingOS", description="Service name")
    status: HealthStatus = Field(..., description="Overall system health status")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Health check timestamp"
    )
    version: str = Field(default="2.5.0", description="System version")
    components: Dict[str, Any] = Field(default_factory=dict, description="Component health details")
    uptime_seconds: int = Field(ge=0, description="System uptime in seconds")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Response correlation ID"
    )


# =============================================================================
# DynamoDB Models (Phase 2.5.3) - Enhanced with Pydantic
# =============================================================================

class DynamoDBItem(BaseModel):
    """
    Base class for DynamoDB items with Pydantic validation
    
    Provides standardized structure for all DynamoDB table items with
    audit fields, TTL support, and consistent formatting.
    """
    model_config = BuildingOSConfig.model_config
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Item creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Item last update timestamp"
    )
    ttl: Optional[int] = Field(None, gt=0, description="TTL timestamp for item expiration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item format with proper serialization"""
        item_dict = self.model_dump(exclude_none=True)
        
        # Convert datetime to ISO string for DynamoDB
        if 'created_at' in item_dict:
            item_dict['created_at'] = self.created_at.isoformat()
        if 'updated_at' in item_dict:
            item_dict['updated_at'] = self.updated_at.isoformat()
            
        return item_dict


class WebSocketConnection(DynamoDBItem):
    """
    WebSocket connection model with enhanced Pydantic validation
    
    Represents active WebSocket connections with automatic validation
    for connection IDs, user information, and connection state management.
    """
    
    connection_id: str = Field(
        ..., 
        min_length=8,
        pattern=r'^[A-Za-z0-9+/=_-]+$',
        description="WebSocket connection identifier"
    )
    user_id: Optional[str] = Field(None, min_length=1, description="Connected user identifier")
    connection_state: ConnectionState = Field(
        default=ConnectionState.CONNECTED,
        description="Current connection state"
    )
    client_info: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Client connection information"
    )
    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last activity timestamp"
    )
    
    @field_validator('connection_id')
    @classmethod
    def validate_connection_id(cls, v: str) -> str:
        """Validate WebSocket connection ID format"""
        if not v or len(v) < 8:
            raise ValueError('Connection ID must be at least 8 characters')
        return v


class MissionState(DynamoDBItem):
    """
    Mission state model with comprehensive Pydantic validation
    
    Tracks mission execution state with automatic validation for
    mission data, task tracking, and state transitions.
    """
    
    mission_id: str = Field(..., min_length=8, description="Mission identifier")
    user_id: str = Field(..., min_length=1, description="Mission owner user ID")
    mission_status: MissionStatus = Field(
        default=MissionStatus.CREATED,
        description="Current mission status"
    )
    user_message: str = Field(..., min_length=1, max_length=2000, description="Original user message")
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="Mission tasks")
    results: Dict[str, Any] = Field(default_factory=dict, description="Mission results")
    completion_percentage: int = Field(
        default=0, 
        ge=0, 
        le=100, 
        description="Mission completion percentage"
    )
    
    @field_validator('tasks')
    @classmethod
    def validate_tasks(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate mission tasks structure"""
        for task in v:
            required_fields = ['task_id', 'action', 'agent', 'status']
            for field in required_fields:
                if field not in task:
                    raise ValueError(f'Task must contain {field}')
        return v


class ShortTermMemory(DynamoDBItem):
    """
    Short-term memory model with Pydantic validation for conversation context
    
    Stores temporary conversation data with automatic TTL and
    validation for memory content and user associations.
    """
    
    memory_id: str = Field(..., min_length=8, description="Memory identifier")
    user_id: str = Field(..., min_length=1, description="Associated user ID")
    conversation_id: str = Field(..., min_length=8, description="Conversation identifier")
    memory_type: Literal["conversation", "context", "preference", "session"] = Field(
        ..., 
        description="Type of memory stored"
    )
    content: Dict[str, Any] = Field(..., description="Memory content")
    relevance_score: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0, 
        description="Memory relevance score"
    )
    
    # Override TTL with default for short-term memory (24 hours)
    ttl: int = Field(
        default_factory=lambda: int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
        description="TTL for memory expiration (24 hours default)"
    )


class ElevatorMonitoring(DynamoDBItem):
    """
    Elevator monitoring model with validation for elevator system data
    
    Tracks elevator status, usage patterns, and maintenance information
    with comprehensive validation for operational data.
    """
    
    elevator_id: str = Field(..., min_length=1, description="Elevator system identifier")
    building_id: str = Field(..., min_length=1, description="Building identifier")
    current_floor: int = Field(ge=-5, le=50, description="Current elevator floor")
    status: Literal["idle", "moving", "maintenance", "emergency", "offline"] = Field(
        ..., 
        description="Current elevator status"
    )
    last_service_date: Optional[datetime] = Field(None, description="Last maintenance date")
    usage_count: int = Field(default=0, ge=0, description="Daily usage counter")
    error_log: List[str] = Field(default_factory=list, description="Recent error messages")
    
    @field_validator('current_floor')
    @classmethod
    def validate_floor(cls, v: int) -> int:
        """Validate elevator floor number"""
        if v == 0:
            raise ValueError('Floor 0 is not valid for elevator positioning')
        return v


# =============================================================================
# Backward Compatibility Layer
# =============================================================================

# Export existing names for backward compatibility during migration
__all__ = [
    # Enums
    'TaskStatus', 'MissionStatus', 'AgentType', 'HealthStatus', 'ConnectionState',
    # Core Models
    'SNSMessage', 'TaskMessage', 'MissionMessage',
    # API Models  
    'PersonaRequest', 'PersonaResponse', 'DirectorRequest', 'DirectorResponse',
    'CoordinatorRequest', 'CoordinatorResponse', 'PSIMRequest', 'PSIMResponse',
    'ElevatorRequest', 'ElevatorResponse', 'HealthCheckResponse',
    # DynamoDB Models
    'DynamoDBItem', 'WebSocketConnection', 'MissionState', 'ShortTermMemory',
    'ElevatorMonitoring',
    # Configuration
    'BuildingOSConfig'
]

class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredLog(BaseModel):
    """
    Pydantic model for structured logging with comprehensive validation
    
    Provides type-safe, validated logging with automatic serialization,
    correlation tracking, and enhanced debugging capabilities.
    """
    model_config = BuildingOSConfig.model_config
    
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., min_length=1, description="Log message")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Log timestamp in UTC"
    )
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Correlation ID for request tracing"
    )
    service: str = Field(..., min_length=1, description="Service generating the log")
    function_name: str = Field(..., min_length=1, description="Function name")
    request_id: Optional[str] = Field(None, description="AWS Lambda request ID")
    
    # Structured data
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured log data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    performance: Optional[Dict[str, Union[int, float]]] = Field(None, description="Performance metrics")
    
    # Context information
    user_id: Optional[str] = Field(None, description="User identifier")
    connection_id: Optional[str] = Field(None, description="WebSocket connection ID")
    
    @field_validator('service')
    @classmethod
    def validate_service(cls, v: str) -> str:
        """Validate service name"""
        if not v.startswith(('agent_', 'websocket_', 'tool_')):
            raise ValueError('Service must start with agent_, websocket_, or tool_')
        return v
    
    def to_cloudwatch_format(self) -> str:
        """Convert to CloudWatch structured log format"""
        log_data = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "service": self.service,
            "function": self.function_name,
            "correlation_id": self.correlation_id,
            "message": self.message
        }
        
        if self.request_id:
            log_data["request_id"] = self.request_id
        if self.user_id:
            log_data["user_id"] = self.user_id
        if self.connection_id:
            log_data["connection_id"] = self.connection_id
        if self.data:
            log_data["data"] = self.data
        if self.error:
            log_data["error"] = self.error
        if self.performance:
            log_data["performance"] = self.performance
            
        return self.model_dump_json(exclude_none=True)
    
    def print_log(self) -> None:
        """Print structured log to stdout for Lambda CloudWatch"""
        print(self.to_cloudwatch_format())

class PydanticError(BaseModel):
    """
    Pydantic model for structured error information
    """
    model_config = BuildingOSConfig.model_config
    
    error_type: str = Field(..., description="Error type/class name")
    error_message: str = Field(..., description="Error message")
    traceback: Optional[str] = Field(None, description="Full traceback")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    
    @classmethod
    def from_exception(cls, exc: Exception, context: Dict[str, Any] = None) -> "PydanticError":
        """Create PydanticError from Python exception"""
        import traceback as tb
        
        return cls(
            error_type=type(exc).__name__,
            error_message=str(exc),
            traceback=tb.format_exc(),
            context=context or {}
        )
