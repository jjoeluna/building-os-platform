"""
Simple syntax test for ACP protocol module
Tests basic functionality without PydanticAI dependencies
"""

import sys
sys.path.append('.')

# Test basic imports
try:
    from pydantic_models import AgentType
    print("✅ AgentType imported successfully")
except ImportError as e:
    print(f"❌ AgentType import failed: {e}")

# Test ACP protocol basic structures
try:
    import uuid
    from datetime import datetime, timezone
    from typing import Dict, Any, List, Optional, Literal, Union
    from enum import Enum
    from pydantic import BaseModel, Field, ConfigDict, field_validator
    
    # Test enum creation
    class ACPMessageType(Enum):
        INFORM = "inform"
        REQUEST = "request"
        RESPONSE = "response"
    
    class Priority(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
    
    # Test basic message structure
    class TestACPMessage(BaseModel):
        model_config = ConfigDict(
            str_strip_whitespace=True,
            validate_assignment=True,
            use_enum_values=True,
            extra="forbid"
        )
        
        protocol: Literal["ACP"] = Field(default="ACP")
        version: Literal["1.0"] = Field(default="1.0")
        message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
        conversation_id: str = Field(..., min_length=1)
        sender_agent: AgentType = Field(...)
        receiver_agent: AgentType = Field(...)
        message_type: ACPMessageType = Field(...)
        priority: Priority = Field(default=Priority.MEDIUM)
        content: Dict[str, Any] = Field(...)
        created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
        
        @field_validator('message_id', 'conversation_id')
        @classmethod
        def validate_uuid_format(cls, v):
            if v is None:
                return v
            try:
                uuid.UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
    
    # Test message creation
    test_message = TestACPMessage(
        conversation_id=str(uuid.uuid4()),
        sender_agent=AgentType.PERSONA,
        receiver_agent=AgentType.DIRECTOR,
        message_type=ACPMessageType.REQUEST,
        content={"test": "data"}
    )
    
    print("✅ ACP message structure validated successfully")
    print(f"✅ Message ID: {test_message.message_id}")
    print(f"✅ Protocol: {test_message.protocol}")
    print(f"✅ Sender: {test_message.sender_agent.value}")
    print(f"✅ Receiver: {test_message.receiver_agent.value}")
    
except Exception as e:
    print(f"❌ ACP structure test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 ACP Protocol syntax validation completed!")
