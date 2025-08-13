# ACP Protocol - BuildingOS Platform
"""
Agent Communication Protocol (ACP) for BuildingOS Platform

This module implements the standardized communication protocol for all agents
in the BuildingOS ecosystem, ensuring type-safe and validated message exchange.

Features:
- Type-safe message definitions using Pydantic models
- Standardized request/response patterns
- Event-driven communication support
- Error handling and validation
- Agent registration and discovery
"""

from typing import Dict, Any, Optional, List, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import json
import uuid


class MessageType(str, Enum):
    """Standard message types for agent communication"""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    REGISTRATION = "registration"
    # ACP Standard types
    TASK = "task"
    RESULT = "result"


class AgentType(str, Enum):
    """Supported agent types in the BuildingOS platform"""

    DIRECTOR = "director"
    PERSONA = "persona"
    COORDINATOR = "coordinator"
    ELEVATOR = "elevator"
    PSIM = "psim"
    HEALTH_CHECK = "health_check"


class Priority(str, Enum):
    """Message priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageStatus(str, Enum):
    """Message processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ACPHeader(BaseModel):
    """Standard header for all ACP messages"""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    source_agent: str = Field(..., description="Source agent identifier")
    target_agent: Optional[str] = Field(
        None, description="Target agent identifier (null for broadcast)"
    )
    correlation_id: Optional[str] = Field(
        None, description="For tracking request-response pairs"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: Priority = Priority.NORMAL
    ttl_seconds: Optional[int] = Field(None, description="Time to live in seconds")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ACPPayload(BaseModel):
    """Base payload structure for ACP messages"""

    action: str = Field(..., description="Action to be performed")
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ACPError(BaseModel):
    """Error information structure"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    stack_trace: Optional[str] = Field(None, description="Stack trace for debugging")


class ACPMessage(BaseModel):
    """Complete ACP message structure"""

    header: ACPHeader
    payload: Optional[ACPPayload] = None
    error: Optional[ACPError] = None
    status: MessageStatus = MessageStatus.PENDING

    @field_validator("error")
    @classmethod
    def validate_error_for_error_messages(cls, v, info):
        """Ensure error messages include error information"""
        if (
            info.data.get("header")
            and info.data["header"].message_type == MessageType.ERROR
        ):
            if not v:
                raise ValueError("Error messages must include error information")
        return v

    def to_json(self) -> str:
        """Convert message to JSON string"""
        return self.model_dump_json(exclude_none=True)

    @classmethod
    def from_json(cls, json_str: str) -> "ACPMessage":
        """Create message from JSON string"""
        return cls.model_validate_json(json_str)


class AgentRegistration(BaseModel):
    """Agent registration information"""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: AgentType
    name: str = Field(..., description="Human-readable agent name")
    description: Optional[str] = Field(None, description="Agent description")
    capabilities: List[str] = Field(
        default_factory=list, description="List of supported actions"
    )
    endpoint: Optional[str] = Field(None, description="Agent endpoint URL")
    health_check_url: Optional[str] = Field(None, description="Health check endpoint")
    version: str = Field(default="1.0.0", description="Agent version")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ACPProtocol:
    """Main ACP Protocol handler class"""

    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.registered_agents: Dict[str, AgentRegistration] = {}

    def create_request(
        self,
        target_agent: str,
        action: str,
        data: Dict[str, Any] = None,
        priority: Priority = Priority.NORMAL,
        correlation_id: str = None,
    ) -> ACPMessage:
        """Create a standardized request message"""
        header = ACPHeader(
            message_type=MessageType.REQUEST,
            source_agent=self.agent_id,
            target_agent=target_agent,
            priority=priority,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )

        payload = ACPPayload(
            action=action,
            data=data or {},
            metadata={"agent_type": self.agent_type.value},
        )

        return ACPMessage(header=header, payload=payload)

    def create_response(
        self,
        original_message: ACPMessage,
        data: Dict[str, Any] = None,
        status: MessageStatus = MessageStatus.COMPLETED,
    ) -> ACPMessage:
        """Create a response to a request message"""
        header = ACPHeader(
            message_type=MessageType.RESPONSE,
            source_agent=self.agent_id,
            target_agent=original_message.header.source_agent,
            correlation_id=original_message.header.correlation_id,
        )

        payload = ACPPayload(
            action=f"response_{original_message.payload.action}",
            data=data or {},
            metadata={"original_message_id": original_message.header.message_id},
        )

        return ACPMessage(header=header, payload=payload, status=status)

    def create_event(
        self, action: str, data: Dict[str, Any] = None, target_agent: str = None
    ) -> ACPMessage:
        """Create an event message (broadcast or targeted)"""
        header = ACPHeader(
            message_type=MessageType.EVENT,
            source_agent=self.agent_id,
            target_agent=target_agent,
        )

        payload = ACPPayload(
            action=action,
            data=data or {},
            metadata={"event_source": self.agent_type.value},
        )

        return ACPMessage(header=header, payload=payload)

    def create_error(
        self,
        target_agent: str,
        error_code: str,
        error_message: str,
        details: Dict[str, Any] = None,
        correlation_id: str = None,
    ) -> ACPMessage:
        """Create an error message"""
        header = ACPHeader(
            message_type=MessageType.ERROR,
            source_agent=self.agent_id,
            target_agent=target_agent,
            correlation_id=correlation_id,
        )

        error = ACPError(code=error_code, message=error_message, details=details or {})

        return ACPMessage(header=header, error=error, status=MessageStatus.FAILED)

    def create_heartbeat(self) -> ACPMessage:
        """Create a heartbeat message"""
        header = ACPHeader(
            message_type=MessageType.HEARTBEAT, source_agent=self.agent_id
        )

        payload = ACPPayload(
            action="heartbeat",
            data={"status": "alive", "agent_type": self.agent_type.value},
            metadata={"timestamp": datetime.utcnow().isoformat()},
        )

        return ACPMessage(
            header=header, payload=payload, status=MessageStatus.COMPLETED
        )

    def create_task(
        self,
        target_agent: str,
        task_id: str,
        action: str,
        parameters: Dict[str, Any] = None,
        priority: Priority = Priority.NORMAL,
        correlation_id: str = None,
    ) -> ACPMessage:
        """Create a task message (ACP Standard)"""
        header = ACPHeader(
            message_type=MessageType.TASK,
            source_agent=self.agent_id,
            target_agent=target_agent,
            priority=priority,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )

        payload = ACPPayload(
            action=action,
            data={
                "task_id": task_id,
                "parameters": parameters or {},
                "assigned_agent": target_agent,
                "created_at": datetime.utcnow().isoformat(),
            },
            metadata={"agent_type": self.agent_type.value, "task_type": "acp_standard"},
        )

        return ACPMessage(header=header, payload=payload)

    def create_result(
        self,
        original_task: ACPMessage,
        task_result: Dict[str, Any],
        status: MessageStatus = MessageStatus.COMPLETED,
        execution_time_ms: int = None,
    ) -> ACPMessage:
        """Create a result message (ACP Standard)"""
        header = ACPHeader(
            message_type=MessageType.RESULT,
            source_agent=self.agent_id,
            target_agent=original_task.header.source_agent,
            correlation_id=original_task.header.correlation_id,
        )

        payload = ACPPayload(
            action=f"result_{original_task.payload.action}",
            data={
                "task_id": original_task.payload.data.get("task_id"),
                "result": task_result,
                "execution_time_ms": execution_time_ms,
                "completed_at": datetime.utcnow().isoformat(),
            },
            metadata={
                "original_task_id": original_task.header.message_id,
                "agent_type": self.agent_type.value,
                "result_type": "acp_standard",
            },
        )

        return ACPMessage(header=header, payload=payload, status=status)

    def register_agent(self, registration: AgentRegistration) -> None:
        """Register an agent in the local registry"""
        self.registered_agents[registration.agent_id] = registration

    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent registration by ID"""
        return self.registered_agents.get(agent_id)

    def list_agents(self, agent_type: AgentType = None) -> List[AgentRegistration]:
        """List all registered agents, optionally filtered by type"""
        agents = list(self.registered_agents.values())
        if agent_type:
            agents = [agent for agent in agents if agent.agent_type == agent_type]
        return agents

    def validate_message(self, message: Union[str, dict, ACPMessage]) -> ACPMessage:
        """Validate and parse an incoming message"""
        if isinstance(message, str):
            return ACPMessage.from_json(message)
        elif isinstance(message, dict):
            return ACPMessage.parse_obj(message)
        elif isinstance(message, ACPMessage):
            return message
        else:
            raise ValueError(f"Invalid message type: {type(message)}")


# Standard action definitions
class StandardActions:
    """Standard actions used across the BuildingOS platform"""

    # Director actions
    MISSION_START = "mission_start"
    MISSION_COMPLETE = "mission_complete"
    MISSION_ABORT = "mission_abort"

    # Persona actions
    PERSONA_ACTIVATE = "persona_activate"
    PERSONA_RESPOND = "persona_respond"
    PERSONA_STATUS = "persona_status"

    # Coordinator actions
    COORDINATE_AGENTS = "coordinate_agents"
    STATUS_UPDATE = "status_update"

    # Elevator actions
    ELEVATOR_CALL = "elevator_call"
    ELEVATOR_STATUS = "elevator_status"
    ELEVATOR_MOVE = "elevator_move"

    # PSIM actions
    PSIM_QUERY = "psim_query"
    PSIM_UPDATE = "psim_update"

    # Health check actions
    HEALTH_CHECK = "health_check"
    HEALTH_STATUS = "health_status"

    # WebSocket actions
    WS_CONNECT = "ws_connect"
    WS_DISCONNECT = "ws_disconnect"
    WS_BROADCAST = "ws_broadcast"

    # ACP Standard task/result actions
    TASK_ASSIGN = "task_assign"
    TASK_EXECUTE = "task_execute"
    TASK_COMPLETE = "task_complete"
    RESULT_SUCCESS = "result_success"
    RESULT_FAILURE = "result_failure"
    RESULT_PARTIAL = "result_partial"


# Utility functions
def create_acp_instance(agent_id: str, agent_type: str) -> ACPProtocol:
    """Factory function to create ACP protocol instance"""
    try:
        agent_type_enum = AgentType(agent_type.lower())
        return ACPProtocol(agent_id, agent_type_enum)
    except ValueError:
        raise ValueError(f"Invalid agent type: {agent_type}")


def serialize_message(message: ACPMessage) -> str:
    """Serialize ACP message to JSON string"""
    return message.to_json()


def deserialize_message(json_str: str) -> ACPMessage:
    """Deserialize JSON string to ACP message"""
    return ACPMessage.from_json(json_str)


# Example usage and testing
if __name__ == "__main__":
    # Example: Director agent creating a mission request
    director_acp = ACPProtocol("director-001", AgentType.DIRECTOR)

    # Create a mission start request
    mission_request = director_acp.create_request(
        target_agent="persona-licca",
        action=StandardActions.MISSION_START,
        data={
            "mission_id": "mission-001",
            "mission_type": "customer_service",
            "context": "Handle customer inquiry about elevator maintenance",
        },
        priority=Priority.HIGH,
    )

    print("=== ACP Protocol Example ===")
    print("Mission Request Message:")
    print(mission_request.to_json())
    print()

    # Example: Persona agent responding
    persona_acp = ACPProtocol("persona-licca", AgentType.PERSONA)

    mission_response = persona_acp.create_response(
        original_message=mission_request,
        data={
            "mission_id": "mission-001",
            "status": "accepted",
            "estimated_duration": "5 minutes",
            "response": "I'll handle this customer inquiry about elevator maintenance.",
        },
    )

    print("Mission Response Message:")
    print(mission_response.to_json())
    print()

    # Example: Event broadcast
    status_event = director_acp.create_event(
        action="mission_status_update",
        data={"mission_id": "mission-001", "status": "in_progress", "progress": 25},
    )

    print("Status Event Message:")
    print(status_event.to_json())
    print()

    # Example: ACP Standard Task/Result pattern
    print("=== ACP Standard Task/Result Pattern ===")

    # Coordinator creates a task for elevator agent
    coordinator_acp = ACPProtocol("coordinator-001", AgentType.COORDINATOR)

    elevator_task = coordinator_acp.create_task(
        target_agent="elevator-agent-001",
        task_id="task-elev-001",
        action=StandardActions.TASK_EXECUTE,
        parameters={
            "operation": "call_elevator",
            "from_floor": 1,
            "to_floor": 5,
            "building_id": "building-001",
        },
        priority=Priority.HIGH,
    )

    print("Task Message (ACP Standard):")
    print(elevator_task.to_json())
    print()

    # Elevator agent responds with result
    elevator_acp = ACPProtocol("elevator-agent-001", AgentType.ELEVATOR)

    task_result = elevator_acp.create_result(
        original_task=elevator_task,
        task_result={
            "operation_status": "completed",
            "elevator_id": "elev-001",
            "current_floor": 5,
            "execution_details": "Elevator successfully moved from floor 1 to floor 5",
        },
        execution_time_ms=3500,
    )

    print("Result Message (ACP Standard):")
    print(task_result.to_json())
    print()

    print("✅ ACP Protocol implementation completed successfully!")
    print("📋 Topic Structure Compatibility:")
    print(
        "   Current BuildingOS: intention → mission → task-result → mission-result → response"
    )
    print("   ACP Standard: task → result")
    print("   ✅ Both patterns supported in this implementation")
