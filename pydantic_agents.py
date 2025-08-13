"""
PydanticAI Agent Base Classes for BuildingOS

This module provides enhanced agent base classes using PydanticAI 0.6.2,
offering type-safe AI interactions, structured responses, and integrated
ACP communication protocol support.

Architecture Decision: ADR-019 - PydanticAI with ACP Communication Protocol Enhancement
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models import Model

from acp_protocol import ACPMessage, ACPMessageType, Priority, ConversationThread
from pydantic_models import AgentType, AgentStatus
from aws_clients import get_sns_client


@dataclass
class AgentContext:
    """Context data passed to PydanticAI agents"""
    agent_id: str
    agent_type: AgentType
    conversation_id: str
    user_id: Optional[str] = None
    session_data: Dict[str, Any] = None
    aws_region: str = "us-east-1"
    
    def __post_init__(self):
        if self.session_data is None:
            self.session_data = {}


class AgentResponse(BaseModel):
    """Standardized agent response structure"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    agent_id: str = Field(..., description="Responding agent identifier")
    agent_type: AgentType = Field(..., description="Agent type")
    success: bool = Field(..., description="Operation success status")
    response_data: Dict[str, Any] = Field(default_factory=dict, description="Response payload")
    message: str = Field(..., description="Human-readable response message")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Response timestamp"
    )
    conversation_id: str = Field(..., description="Conversation identifier")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence")
    
    # ACP integration
    acp_message_id: Optional[str] = Field(None, description="Related ACP message ID")
    next_actions: List[str] = Field(default_factory=list, description="Suggested next actions")


class BuildingOSAgent:
    """
    Enhanced base class for BuildingOS agents with PydanticAI integration
    
    Provides structured AI interactions, ACP communication, conversation history,
    and standardized response handling for all BuildingOS agents.
    """
    
    def __init__(
        self,
        agent_type: AgentType,
        model_name: str = "openai:gpt-4o",
        system_prompt: str = None,
        tools: List[Tool] = None,
        response_model: Type[BaseModel] = None
    ):
        """
        Initialize BuildingOS agent with PydanticAI integration
        
        Args:
            agent_type: Type of agent (from AgentType enum)
            model_name: AI model to use (default: gpt-4o)
            system_prompt: Base system prompt for the agent
            tools: List of PydanticAI tools available to the agent
            response_model: Pydantic model for structured responses
        """
        self.agent_type = agent_type
        self.agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        self.model_name = model_name
        self.status = AgentStatus.INITIALIZING
        
        # Initialize conversation tracking
        self.conversation_threads: Dict[str, ConversationThread] = {}
        self.message_history: List[ACPMessage] = []
        
        # Set up default system prompt if none provided
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        # Initialize PydanticAI agent
        self.pydantic_agent = Agent(
            model_name,
            deps_type=AgentContext,
            output_type=response_model or AgentResponse,
            system_prompt=system_prompt
        )
        
        # Register default tools
        self._register_default_tools()
        
        # Register custom tools if provided
        if tools:
            for tool in tools:
                self.pydantic_agent.tool(tool)
        
        self.status = AgentStatus.READY
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for the agent type"""
        prompts = {
            AgentType.PERSONA: """You are a Persona Agent in the BuildingOS platform. 
            Your role is to understand user intentions and communicate with the Director Agent 
            to fulfill user requests. You should be helpful, professional, and context-aware.""",
            
            AgentType.DIRECTOR: """You are a Director Agent in the BuildingOS platform.
            Your role is to analyze requests from Persona Agents and create detailed mission plans
            for the Coordinator Agent to execute. You should be strategic and comprehensive.""",
            
            AgentType.COORDINATOR: """You are a Coordinator Agent in the BuildingOS platform.
            Your role is to execute mission plans from the Director Agent by orchestrating
            tool agents and managing task execution. You should be efficient and reliable.""",
            
            AgentType.ELEVATOR: """You are an Elevator Tool Agent in the BuildingOS platform.
            Your role is to interface with elevator systems and execute elevator-related tasks.
            You should be precise and safety-focused.""",
            
            AgentType.PSIM: """You are a PSIM Tool Agent in the BuildingOS platform.
            Your role is to interface with PSIM systems and execute security-related tasks.
            You should be security-conscious and thorough."""
        }
        
        return prompts.get(self.agent_type, "You are a BuildingOS agent.")
    
    def _register_default_tools(self):
        """Register default tools available to all agents"""
        
        @self.pydantic_agent.tool
        async def send_acp_message(
            ctx: RunContext[AgentContext],
            receiver_agent: AgentType,
            message_type: ACPMessageType,
            content: Dict[str, Any],
            priority: Priority = Priority.MEDIUM
        ) -> str:
            """Send an ACP message to another agent via SNS"""
            try:
                message = ACPMessage(
                    conversation_id=ctx.deps.conversation_id,
                    sender_agent=self.agent_type,
                    receiver_agent=receiver_agent,
                    message_type=message_type,
                    content=content,
                    priority=priority
                )
                
                # Send via SNS
                sns_client = get_sns_client()
                topic_arn = self._get_sns_topic_arn(receiver_agent)
                
                response = sns_client.publish(
                    TopicArn=topic_arn,
                    **message.to_sns_payload()
                )
                
                # Track message
                self.message_history.append(message)
                
                return f"Message sent successfully to {receiver_agent.value}: {response['MessageId']}"
                
            except Exception as e:
                return f"Failed to send message: {str(e)}"
        
        @self.pydantic_agent.tool
        async def get_conversation_history(
            ctx: RunContext[AgentContext],
            limit: int = 10
        ) -> List[Dict[str, Any]]:
            """Get recent conversation history"""
            recent_messages = self.message_history[-limit:] if self.message_history else []
            return [
                {
                    "message_id": msg.message_id,
                    "sender": msg.sender_agent.value,
                    "receiver": msg.receiver_agent.value,
                    "type": msg.message_type.value,
                    "timestamp": msg.created_at,
                    "content": msg.content
                }
                for msg in recent_messages
            ]
        
        @self.pydantic_agent.tool
        async def report_agent_status(
            ctx: RunContext[AgentContext],
            status: AgentStatus,
            details: Optional[str] = None
        ) -> str:
            """Report current agent status"""
            self.status = status
            status_report = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "status": status.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details
            }
            
            # Could be extended to send status to monitoring system
            return f"Status updated to {status.value}"
    
    def _get_sns_topic_arn(self, receiver_agent: AgentType) -> str:
        """Get SNS topic ARN for target agent"""
        # This would typically be configured via environment variables
        # For now, using a placeholder pattern
        return f"arn:aws:sns:us-east-1:123456789012:bos-dev-{receiver_agent.value.lower()}-topic"
    
    async def process_message(
        self,
        message: ACPMessage,
        context: AgentContext
    ) -> AgentResponse:
        """
        Process an incoming ACP message using PydanticAI
        
        Args:
            message: Incoming ACP message
            context: Agent context data
            
        Returns:
            Structured agent response
        """
        start_time = datetime.now()
        
        try:
            # Update conversation thread
            if message.conversation_id not in self.conversation_threads:
                self.conversation_threads[message.conversation_id] = ConversationThread(
                    conversation_id=message.conversation_id,
                    participants=[message.sender_agent, message.receiver_agent]
                )
            
            thread = self.conversation_threads[message.conversation_id]
            thread.add_message(message)
            
            # Prepare prompt for PydanticAI
            prompt = self._format_message_prompt(message)
            
            # Run PydanticAI agent
            result = await self.pydantic_agent.run(prompt, deps=context)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Return structured response
            if isinstance(result.output, AgentResponse):
                result.output.processing_time_ms = processing_time
                result.output.acp_message_id = message.message_id
                return result.output
            else:
                # Wrap non-AgentResponse outputs
                return AgentResponse(
                    agent_id=self.agent_id,
                    agent_type=self.agent_type,
                    success=True,
                    response_data={"ai_output": result.output},
                    message=str(result.output),
                    conversation_id=message.conversation_id,
                    processing_time_ms=processing_time,
                    acp_message_id=message.message_id
                )
                
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                response_data={"error": str(e)},
                message=f"Error processing message: {str(e)}",
                conversation_id=message.conversation_id,
                processing_time_ms=processing_time,
                acp_message_id=message.message_id
            )
    
    def _format_message_prompt(self, message: ACPMessage) -> str:
        """Format ACP message into a prompt for PydanticAI"""
        return f"""
        You have received a {message.message_type.value} message from {message.sender_agent.value}.
        
        Message Details:
        - Priority: {message.priority.value}
        - Conversation ID: {message.conversation_id}
        - Created: {message.created_at}
        
        Message Content:
        {json.dumps(message.content, indent=2)}
        
        Please process this message according to your role as a {self.agent_type.value} agent.
        Provide a helpful and appropriate response.
        """
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status information"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "model": self.model_name,
            "active_conversations": len(self.conversation_threads),
            "total_messages": len(self.message_history),
            "uptime": datetime.now(timezone.utc).isoformat()
        }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "AgentContext",
    "AgentResponse", 
    "BuildingOSAgent",
]
