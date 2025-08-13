"""
Unit tests for ACP (Agent Communication Protocol) models

Tests cover:
- Message model validation and serialization
- Conversation threading functionality
- Agent-specific message types
- Error handling and edge cases

Architecture Decision: ADR-019 - PydanticAI with ACP Communication Protocol Enhancement
"""

import pytest
import uuid
import json
from datetime import datetime, timezone
from unittest.mock import patch

from acp_protocol import (
    ACPMessage, ACPMessageType, Priority, ConversationThread,
    PersonaToDirectorRequest, DirectorToCoordinatorMission,
    CoordinatorToToolRequest, ToolToCoordinatorResponse,
    CoordinatorToDirectorUpdate, DirectorToPersonaResponse
)
from pydantic_models import AgentType


class TestACPMessageType:
    """Test ACPMessageType enum"""
    
    def test_message_type_values(self):
        """Test all message type enum values"""
        assert ACPMessageType.INFORM.value == "inform"
        assert ACPMessageType.REQUEST.value == "request"
        assert ACPMessageType.PROPOSE.value == "propose"
        assert ACPMessageType.ACCEPT.value == "accept"
        assert ACPMessageType.REJECT.value == "reject"
        assert ACPMessageType.QUERY.value == "query"
        assert ACPMessageType.RESPONSE.value == "response"


class TestPriority:
    """Test Priority enum"""
    
    def test_priority_values(self):
        """Test all priority enum values"""
        assert Priority.LOW.value == "low"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.HIGH.value == "high"
        assert Priority.URGENT.value == "urgent"


class TestACPMessage:
    """Test base ACPMessage class"""
    
    def test_create_valid_message(self):
        """Test creating a valid ACP message"""
        message = ACPMessage(
            conversation_id=str(uuid.uuid4()),
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            content={"test": "data"}
        )
        
        assert message.protocol == "ACP"
        assert message.version == "1.0"
        assert message.priority == Priority.MEDIUM
        assert message.sender_agent == AgentType.PERSONA
        assert message.receiver_agent == AgentType.DIRECTOR
        assert message.message_type == ACPMessageType.REQUEST
        assert message.content == {"test": "data"}
        assert message.reply_to is None
        assert message.correlation_data == {}
        
        # Test auto-generated fields
        assert uuid.UUID(message.message_id)  # Valid UUID
        assert message.created_at
        assert message.expires_at is None

    def test_message_with_all_fields(self):
        """Test creating message with all optional fields"""
        conversation_id = str(uuid.uuid4())
        reply_to = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc).isoformat()
        
        message = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.DIRECTOR,
            receiver_agent=AgentType.COORDINATOR,
            message_type=ACPMessageType.INFORM,
            priority=Priority.HIGH,
            content={"mission": "test"},
            reply_to=reply_to,
            expires_at=expires_at,
            correlation_data={"session_id": "test123"}
        )
        
        assert message.conversation_id == conversation_id
        assert message.priority == Priority.HIGH
        assert message.reply_to == reply_to
        assert message.expires_at == expires_at
        assert message.correlation_data == {"session_id": "test123"}

    def test_invalid_uuid_validation(self):
        """Test validation of UUID fields"""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            ACPMessage(
                conversation_id="invalid-uuid",
                sender_agent=AgentType.PERSONA,
                receiver_agent=AgentType.DIRECTOR,
                message_type=ACPMessageType.REQUEST,
                content={"test": "data"}
            )

    def test_invalid_timestamp_validation(self):
        """Test validation of timestamp fields"""
        with pytest.raises(ValueError, match="Invalid ISO timestamp format"):
            ACPMessage(
                conversation_id=str(uuid.uuid4()),
                sender_agent=AgentType.PERSONA,
                receiver_agent=AgentType.DIRECTOR,
                message_type=ACPMessageType.REQUEST,
                content={"test": "data"},
                created_at="invalid-timestamp"
            )

    def test_get_age_seconds(self):
        """Test message age calculation"""
        with patch('acp_protocol.datetime') as mock_datetime:
            # Mock current time
            now = datetime(2025, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
            created_time = datetime(2025, 1, 12, 9, 59, 30, tzinfo=timezone.utc)
            
            mock_datetime.now.return_value = now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            message = ACPMessage(
                conversation_id=str(uuid.uuid4()),
                sender_agent=AgentType.PERSONA,
                receiver_agent=AgentType.DIRECTOR,
                message_type=ACPMessageType.REQUEST,
                content={"test": "data"},
                created_at=created_time.isoformat()
            )
            
            age = message.get_age_seconds()
            assert age == 30.0  # 30 seconds difference

    def test_is_expired(self):
        """Test message expiration check"""
        with patch('acp_protocol.datetime') as mock_datetime:
            now = datetime(2025, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
            past_time = datetime(2025, 1, 12, 9, 0, 0, tzinfo=timezone.utc)
            future_time = datetime(2025, 1, 12, 11, 0, 0, tzinfo=timezone.utc)
            
            mock_datetime.now.return_value = now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            # Test expired message
            expired_message = ACPMessage(
                conversation_id=str(uuid.uuid4()),
                sender_agent=AgentType.PERSONA,
                receiver_agent=AgentType.DIRECTOR,
                message_type=ACPMessageType.REQUEST,
                content={"test": "data"},
                expires_at=past_time.isoformat()
            )
            assert expired_message.is_expired() is True
            
            # Test non-expired message
            valid_message = ACPMessage(
                conversation_id=str(uuid.uuid4()),
                sender_agent=AgentType.PERSONA,
                receiver_agent=AgentType.DIRECTOR,
                message_type=ACPMessageType.REQUEST,
                content={"test": "data"},
                expires_at=future_time.isoformat()
            )
            assert valid_message.is_expired() is False
            
            # Test message without expiration
            no_expiry_message = ACPMessage(
                conversation_id=str(uuid.uuid4()),
                sender_agent=AgentType.PERSONA,
                receiver_agent=AgentType.DIRECTOR,
                message_type=ACPMessageType.REQUEST,
                content={"test": "data"}
            )
            assert no_expiry_message.is_expired() is False

    def test_to_sns_payload(self):
        """Test SNS payload generation"""
        conversation_id = str(uuid.uuid4())
        message = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            priority=Priority.HIGH,
            content={"test": "data"}
        )
        
        payload = message.to_sns_payload()
        
        # Validate structure
        assert "Message" in payload
        assert "MessageAttributes" in payload
        
        # Validate message content
        message_data = json.loads(payload["Message"])
        assert message_data["protocol"] == "ACP"
        assert message_data["conversation_id"] == conversation_id
        
        # Validate attributes
        attributes = payload["MessageAttributes"]
        assert attributes["protocol"]["StringValue"] == "ACP"
        assert attributes["sender"]["StringValue"] == "persona"
        assert attributes["receiver"]["StringValue"] == "director"
        assert attributes["message_type"]["StringValue"] == "request"
        assert attributes["priority"]["StringValue"] == "high"
        assert attributes["conversation_id"]["StringValue"] == conversation_id


class TestPersonaToDirectorRequest:
    """Test PersonaToDirectorRequest message"""
    
    def test_create_valid_request(self):
        """Test creating valid persona to director request"""
        content = PersonaToDirectorRequest.ContentModel(
            user_intention="Turn on the lights in conference room A",
            user_id="user123",
            context={"room": "conf_a", "action": "lights_on"},
            priority=Priority.MEDIUM,
            persona_analysis="User wants to enable lighting for meeting"
        )
        
        message = PersonaToDirectorRequest(
            conversation_id=str(uuid.uuid4()),
            content=content
        )
        
        assert message.sender_agent == AgentType.PERSONA
        assert message.receiver_agent == AgentType.DIRECTOR
        assert message.message_type == ACPMessageType.REQUEST
        assert message.content.user_intention == "Turn on the lights in conference room A"
        assert message.content.user_id == "user123"
        assert message.content.priority == Priority.MEDIUM

    def test_content_validation(self):
        """Test content model validation"""
        # Test minimum required fields
        content = PersonaToDirectorRequest.ContentModel(
            user_intention="Test intention",
            user_id="user123"
        )
        assert content.user_intention == "Test intention"
        assert content.user_id == "user123"
        assert content.context == {}
        assert content.priority == Priority.MEDIUM
        assert content.persona_analysis is None
        
        # Test invalid user_intention (too short)
        with pytest.raises(ValueError):
            PersonaToDirectorRequest.ContentModel(
                user_intention="",
                user_id="user123"
            )
        
        # Test invalid user_intention (too long)
        with pytest.raises(ValueError):
            PersonaToDirectorRequest.ContentModel(
                user_intention="x" * 1001,
                user_id="user123"
            )


class TestDirectorToCoordinatorMission:
    """Test DirectorToCoordinatorMission message"""
    
    def test_create_valid_mission(self):
        """Test creating valid director to coordinator mission"""
        content = DirectorToCoordinatorMission.ContentModel(
            mission_id="mission_123",
            mission_plan="Execute lighting control in conference room A",
            tasks=[
                {"task_id": "task1", "action": "lights_on", "room": "conf_a"}
            ],
            estimated_duration=30,
            required_tools=["elevator", "psim"],
            success_criteria="Lights successfully turned on"
        )
        
        message = DirectorToCoordinatorMission(
            conversation_id=str(uuid.uuid4()),
            content=content
        )
        
        assert message.sender_agent == AgentType.DIRECTOR
        assert message.receiver_agent == AgentType.COORDINATOR
        assert message.message_type == ACPMessageType.INFORM
        assert message.content.mission_id == "mission_123"
        assert len(message.content.tasks) == 1
        assert message.content.estimated_duration == 30

    def test_content_validation(self):
        """Test mission content validation"""
        # Test minimum required fields
        content = DirectorToCoordinatorMission.ContentModel(
            mission_id="mission_123",
            mission_plan="Test plan",
            tasks=[{"task": "test"}],
            estimated_duration=30
        )
        assert content.required_tools == []
        assert content.success_criteria is None
        
        # Test invalid estimated_duration
        with pytest.raises(ValueError):
            DirectorToCoordinatorMission.ContentModel(
                mission_id="mission_123",
                mission_plan="Test plan",
                tasks=[{"task": "test"}],
                estimated_duration=0  # Must be > 0
            )
        
        # Test empty tasks list
        with pytest.raises(ValueError):
            DirectorToCoordinatorMission.ContentModel(
                mission_id="mission_123",
                mission_plan="Test plan",
                tasks=[],  # Must have at least 1 item
                estimated_duration=30
            )


class TestConversationThread:
    """Test ConversationThread functionality"""
    
    def test_create_conversation_thread(self):
        """Test creating conversation thread"""
        conversation_id = str(uuid.uuid4())
        thread = ConversationThread(
            conversation_id=conversation_id,
            participants=[AgentType.PERSONA, AgentType.DIRECTOR]
        )
        
        assert thread.conversation_id == conversation_id
        assert len(thread.participants) == 2
        assert thread.messages == []
        assert thread.status == "active"
        assert thread.is_active() is True

    def test_add_message(self):
        """Test adding message to conversation thread"""
        conversation_id = str(uuid.uuid4())
        thread = ConversationThread(
            conversation_id=conversation_id,
            participants=[AgentType.PERSONA, AgentType.DIRECTOR]
        )
        
        message = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            content={"test": "data"}
        )
        
        initial_activity = thread.last_activity
        thread.add_message(message)
        
        assert len(thread.messages) == 1
        assert thread.messages[0] == message
        assert thread.last_activity != initial_activity

    def test_get_messages_by_agent(self):
        """Test filtering messages by agent"""
        conversation_id = str(uuid.uuid4())
        thread = ConversationThread(
            conversation_id=conversation_id,
            participants=[AgentType.PERSONA, AgentType.DIRECTOR]
        )
        
        # Add messages from different agents
        persona_message = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            content={"from": "persona"}
        )
        
        director_message = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.DIRECTOR,
            receiver_agent=AgentType.PERSONA,
            message_type=ACPMessageType.RESPONSE,
            content={"from": "director"}
        )
        
        thread.add_message(persona_message)
        thread.add_message(director_message)
        
        persona_messages = thread.get_messages_by_agent(AgentType.PERSONA)
        director_messages = thread.get_messages_by_agent(AgentType.DIRECTOR)
        
        assert len(persona_messages) == 1
        assert len(director_messages) == 1
        assert persona_messages[0].content["from"] == "persona"
        assert director_messages[0].content["from"] == "director"

    def test_get_latest_message(self):
        """Test getting latest message"""
        conversation_id = str(uuid.uuid4())
        thread = ConversationThread(
            conversation_id=conversation_id,
            participants=[AgentType.PERSONA, AgentType.DIRECTOR]
        )
        
        # No messages initially
        assert thread.get_latest_message() is None
        
        # Add messages
        message1 = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            content={"order": 1}
        )
        
        message2 = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.DIRECTOR,
            receiver_agent=AgentType.PERSONA,
            message_type=ACPMessageType.RESPONSE,
            content={"order": 2}
        )
        
        thread.add_message(message1)
        thread.add_message(message2)
        
        latest = thread.get_latest_message()
        assert latest is not None
        assert latest.content["order"] == 2

    def test_get_message_count(self):
        """Test message count"""
        conversation_id = str(uuid.uuid4())
        thread = ConversationThread(
            conversation_id=conversation_id,
            participants=[AgentType.PERSONA, AgentType.DIRECTOR]
        )
        
        assert thread.get_message_count() == 0
        
        message = ACPMessage(
            conversation_id=conversation_id,
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            content={"test": "data"}
        )
        
        thread.add_message(message)
        assert thread.get_message_count() == 1

    def test_conversation_status(self):
        """Test conversation status management"""
        conversation_id = str(uuid.uuid4())
        
        # Test different status values
        for status in ["active", "completed", "failed", "expired"]:
            thread = ConversationThread(
                conversation_id=conversation_id,
                participants=[AgentType.PERSONA, AgentType.DIRECTOR],
                status=status
            )
            assert thread.status == status
            assert thread.is_active() == (status == "active")


class TestComplexScenarios:
    """Test complex scenarios and edge cases"""
    
    def test_full_conversation_flow(self):
        """Test complete conversation flow between agents"""
        conversation_id = str(uuid.uuid4())
        
        # Create conversation thread
        thread = ConversationThread(
            conversation_id=conversation_id,
            participants=[AgentType.PERSONA, AgentType.DIRECTOR, AgentType.COORDINATOR]
        )
        
        # 1. Persona to Director request
        persona_request = PersonaToDirectorRequest(
            conversation_id=conversation_id,
            content=PersonaToDirectorRequest.ContentModel(
                user_intention="Turn on conference room lights",
                user_id="user123"
            )
        )
        thread.add_message(persona_request)
        
        # 2. Director to Coordinator mission
        director_mission = DirectorToCoordinatorMission(
            conversation_id=conversation_id,
            content=DirectorToCoordinatorMission.ContentModel(
                mission_id="mission_123",
                mission_plan="Control conference room lighting",
                tasks=[{"task_id": "lights_on", "room": "conf_a"}],
                estimated_duration=30
            ),
            reply_to=persona_request.message_id
        )
        thread.add_message(director_mission)
        
        # 3. Coordinator to Director update
        coordinator_update = CoordinatorToDirectorUpdate(
            conversation_id=conversation_id,
            content=CoordinatorToDirectorUpdate.ContentModel(
                mission_id="mission_123",
                progress_percentage=100,
                completed_tasks=["lights_on"]
            ),
            reply_to=director_mission.message_id
        )
        thread.add_message(coordinator_update)
        
        # 4. Director to Persona response
        director_response = DirectorToPersonaResponse(
            conversation_id=conversation_id,
            content=DirectorToPersonaResponse.ContentModel(
                original_request_id=persona_request.message_id,
                mission_id="mission_123",
                success=True,
                summary="Conference room lights successfully turned on",
                total_duration_seconds=25
            ),
            reply_to=persona_request.message_id
        )
        thread.add_message(director_response)
        
        # Validate conversation
        assert thread.get_message_count() == 4
        assert len(thread.get_messages_by_agent(AgentType.PERSONA)) == 1
        assert len(thread.get_messages_by_agent(AgentType.DIRECTOR)) == 2
        assert len(thread.get_messages_by_agent(AgentType.COORDINATOR)) == 1
        
        latest_message = thread.get_latest_message()
        assert latest_message.sender_agent == AgentType.DIRECTOR
        assert latest_message.receiver_agent == AgentType.PERSONA
        assert latest_message.content.success is True

    def test_message_serialization_deserialization(self):
        """Test JSON serialization and deserialization"""
        original_message = ACPMessage(
            conversation_id=str(uuid.uuid4()),
            sender_agent=AgentType.PERSONA,
            receiver_agent=AgentType.DIRECTOR,
            message_type=ACPMessageType.REQUEST,
            priority=Priority.HIGH,
            content={"test": "data", "number": 42},
            correlation_data={"session": "test123"}
        )
        
        # Serialize to JSON
        json_data = original_message.model_dump_json()
        
        # Deserialize from JSON
        parsed_data = json.loads(json_data)
        reconstructed_message = ACPMessage.model_validate(parsed_data)
        
        # Validate reconstruction
        assert reconstructed_message.conversation_id == original_message.conversation_id
        assert reconstructed_message.sender_agent == original_message.sender_agent
        assert reconstructed_message.receiver_agent == original_message.receiver_agent
        assert reconstructed_message.message_type == original_message.message_type
        assert reconstructed_message.priority == original_message.priority
        assert reconstructed_message.content == original_message.content
        assert reconstructed_message.correlation_data == original_message.correlation_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
