"""
ACP (Agent Communication Protocol) - Type-Safe Agent Communication

This module implements the Agent Communication Protocol for BuildingOS,
providing type-safe, validated communication between internal agents with
conversation threading and enhanced debugging capabilities.

Architecture Decision: ADR-019 - PydanticAI with ACP Communication Protocol Enhancement
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic_models import AgentType


class ACPMessageType(Enum):
    """Structured message types for agent communication"""
    INFORM = "inform"      # Information sharing between agents
    REQUEST = "request"    # Action requests with validation
    PROPOSE = "propose"    # Proposals and suggestions
    ACCEPT = "accept"      # Acceptance confirmation
    REJECT = "reject"      # Rejection with reason
    QUERY = "query"        # Information queries
    RESPONSE = "response"  # Response to queries/requests


class Priority(Enum):
    """Message priority levels for agent communication"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ACPMessage(BaseModel):
    """
    Enhanced Agent Communication Protocol message base class
    
    Provides type-safe, validated communication between BuildingOS agents
    with conversation threading and structured content validation.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid"
    )
    
    # Protocol identification
    protocol: Literal["ACP"] = Field(default="ACP", description="Protocol identifier")
    version: Literal["1.0"] = Field(default="1.0", description="ACP protocol version")
    
    # Message identification and routing
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID v4 unique message identifier"
    )
    conversation_id: str = Field(
        ..., 
        min_length=1,
        description="Thread tracking identifier for conversation grouping"
    )
    
    # Agent routing
    sender_agent: AgentType = Field(..., description="Typed sender agent")
    receiver_agent: AgentType = Field(..., description="Typed receiver agent")
    
    # Message classification
    message_type: ACPMessageType = Field(..., description="Structured message type")
    priority: Priority = Field(default=Priority.MEDIUM, description="Message priority level")
    
    # Content and metadata
    content: Dict[str, Any] = Field(..., description="Validated message content")
    reply_to: Optional[str] = Field(None, description="Reference to original message ID")
    
    # Timestamps
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Message creation timestamp (ISO format)"
    )
    expires_at: Optional[str] = Field(
        None, 
        description="Message expiration timestamp (ISO format)"
    )
    
    # Correlation and tracking
    correlation_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional correlation data for debugging"
    )

    @field_validator('message_id', 'conversation_id', 'reply_to')
    @classmethod
    def validate_uuid_format(cls, v):
        """Validate UUID format for message identifiers"""
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")

    @field_validator('created_at', 'expires_at')
    @classmethod
    def validate_iso_timestamp(cls, v):
        """Validate ISO timestamp format"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f"Invalid ISO timestamp format: {v}")

    def get_age_seconds(self) -> float:
        """Get message age in seconds"""
        created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - created).total_seconds()

    def is_expired(self) -> bool:
        """Check if message has expired"""
        if not self.expires_at:
            return False
        expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires

    def to_sns_payload(self) -> Dict[str, Any]:
        """Convert to SNS message payload with attributes"""
        return {
            "Message": self.model_dump_json(),
            "MessageAttributes": {
                "protocol": {"DataType": "String", "StringValue": self.protocol},
                "version": {"DataType": "String", "StringValue": self.version},
                "sender": {"DataType": "String", "StringValue": self.sender_agent.value},
                "receiver": {"DataType": "String", "StringValue": self.receiver_agent.value},
                "message_type": {"DataType": "String", "StringValue": self.message_type.value},
                "priority": {"DataType": "String", "StringValue": self.priority.value},
                "conversation_id": {"DataType": "String", "StringValue": self.conversation_id}
            }
        }


# ============================================================================
# AGENT-SPECIFIC MESSAGE MODELS
# ============================================================================

class PersonaToDirectorRequest(ACPMessage):
    """Persona requesting mission planning from Director"""
    sender_agent: Literal[AgentType.PERSONA] = AgentType.PERSONA
    receiver_agent: Literal[AgentType.DIRECTOR] = AgentType.DIRECTOR
    message_type: Literal[ACPMessageType.REQUEST] = ACPMessageType.REQUEST
    
    class ContentModel(BaseModel):
        user_intention: str = Field(..., min_length=1, max_length=1000, description="User's stated intention")
        user_id: str = Field(..., min_length=1, description="User identifier")
        context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
        priority: Priority = Field(default=Priority.MEDIUM, description="Request priority")
        persona_analysis: Optional[str] = Field(None, description="Persona's analysis of the request")
    
    content: ContentModel = Field(..., description="Validated persona request content")


class DirectorToCoordinatorMission(ACPMessage):
    """Director sending mission plan to Coordinator"""
    sender_agent: Literal[AgentType.DIRECTOR] = AgentType.DIRECTOR
    receiver_agent: Literal[AgentType.COORDINATOR] = AgentType.COORDINATOR
    message_type: Literal[ACPMessageType.INFORM] = ACPMessageType.INFORM
    
    class ContentModel(BaseModel):
        mission_id: str = Field(..., min_length=1, description="Unique mission identifier")
        mission_plan: str = Field(..., min_length=1, description="Detailed mission plan")
        tasks: List[Dict[str, Any]] = Field(..., min_items=1, description="List of tasks to execute")
        estimated_duration: int = Field(..., gt=0, description="Estimated duration in seconds")
        required_tools: List[str] = Field(default_factory=list, description="Required tool agents")
        success_criteria: Optional[str] = Field(None, description="Mission success criteria")
    
    content: ContentModel = Field(..., description="Validated mission content")


# ============================================================================
# CONVERSATION MANAGEMENT
# ============================================================================

class ConversationThread(BaseModel):
    """Manages a conversation thread between agents"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    conversation_id: str = Field(..., description="Unique conversation identifier")
    participants: List[AgentType] = Field(..., min_items=2, description="Participating agents")
    messages: List[ACPMessage] = Field(default_factory=list, description="Message history")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Conversation creation timestamp"
    )
    last_activity: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last message timestamp"
    )
    status: Literal["active", "completed", "failed", "expired"] = Field(
        default="active",
        description="Conversation status"
    )

    def add_message(self, message: ACPMessage) -> None:
        """Add message to conversation thread"""
        self.messages.append(message)
        self.last_activity = datetime.now(timezone.utc).isoformat()

    def get_messages_by_agent(self, agent: AgentType) -> List[ACPMessage]:
        """Get all messages from specific agent"""
        return [msg for msg in self.messages if msg.sender_agent == agent]

    def get_latest_message(self) -> Optional[ACPMessage]:
        """Get the most recent message"""
        return self.messages[-1] if self.messages else None

    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)

    def is_active(self) -> bool:
        """Check if conversation is still active"""
        return self.status == "active"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "ACPMessageType",
    "Priority",
    
    # Base classes
    "ACPMessage",
    "ConversationThread",
    
    # Agent-specific messages
    "PersonaToDirectorRequest",
    "DirectorToCoordinatorMission",
]
