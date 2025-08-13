# ADR-019: PydanticAI with ACP Communication Protocol Enhancement

**Date:** 2025-01-12  
**Status:** 🚀 **PROPOSED**  
**Authors:** Senior AWS Solutions Architect  
**Reviewers:** Development Team, Architecture Team  
**Supersedes:** Step 2.5 - Pydantic Data Models Migration  
**Related:** ADR-018 (CodeBuild Lambda Layer Building)

---

## 📋 **Context**

Following the successful implementation of Pydantic data models with CodeBuild-based Lambda layer building (ADR-018), we propose enhancing BuildingOS with **Agent Communication Protocol (ACP)** for internal agent coordination and preparing infrastructure for future **A2A (Agent-to-Agent)** external communication.

### **Current State:**
- ✅ **Step 2.5 Complete**: Pydantic models operational with Linux-compatible Lambda layers
- ✅ **CodeBuild Infrastructure**: Automated layer building for cross-platform compatibility
- ✅ **All Lambda Functions**: Updated to use Pydantic-enhanced layer (v19)
- ✅ **Current Communication**: SNS-based with unstructured mission/task messages

### **Communication Challenges:**
1. **Type Safety**: Current SNS messages use unstructured Dict[str, Any] data
2. **Debugging Complexity**: Limited correlation tracking and conversation threading
3. **Validation Gaps**: No automatic validation of message content and structure
4. **Monitoring Limitations**: Basic correlation IDs without rich agent communication metrics
5. **Future Scalability**: Need foundation for external A2A agent integration

---

## 🎯 **Decision**

**We will implement PydanticAI with enhanced internal communication protocol:**

### **🔄 ACP (Agent Communication Protocol) - Internal Communication** ⭐ **CURRENT SCOPE**
- **Purpose**: Type-safe, validated internal agent coordination
- **Scope**: Persona ↔ Director ↔ Coordinator ↔ Tool Agents communication
- **Technology**: SNS + PydanticAI with structured Pydantic validation
- **Benefits**: Type safety, conversation threading, enhanced debugging, performance monitoring

### **🌐 A2A (Agent-to-Agent) Protocol - External Communication** 📅 **FUTURE SCOPE**
- **Purpose**: Standardized communication with external A2A-compatible agent systems
- **Scope**: External intelligent agent systems (not APIs like PSIM/Elevator)
- **Technology**: Agent Diplomata + PydanticAI FastA2A library
- **Implementation**: Future phase when external A2A agents are identified

---

## 🏗️ **Architecture Design**

### **📐 Current vs Enhanced Communication Architecture**

#### **🔄 CURRENT ARCHITECTURE:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    BUILDINGOS - CURRENT STATE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🌐 EXTERNAL SYSTEMS         🔄 INTERNAL AGENTS               │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │                     │    │                                │ │
│  │  ┌─────────────┐   │    │  ┌─────────────────────────┐   │ │
│  │  │ PSIM API    │◄──┼────┼──│ Agent PSIM             │   │ │
│  │  └─────────────┘   │    │  │ (Direct HTTP)           │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │  ┌─────────────┐   │    │              ▲                 │ │
│  │  │ Elevator API│◄──┼────┼──│ Agent Elevator         │   │ │
│  │  └─────────────┘   │    │  │ (Direct HTTP)           │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │  ┌─────────────┐   │    │              ▲                 │ │
│  │  │ ERP API     │◄──┼────┼──│ Agent ERP              │   │ │
│  │  └─────────────┘   │    │  │ (Direct HTTP)           │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │                     │    │              ▲                 │ │
│  │                     │    │      📨 SNS (Unstructured)     │ │
│  │                     │    │  ┌─────────────────────────┐   │ │
│  │                     │    │  │ 🎯 AGENT DIRECTOR      │   │ │
│  │                     │    │  │ (Mission Orchestrator)  │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │                     │    │              ▲                 │ │
│  │                     │    │      📨 SNS (Unstructured)     │ │
│  │                     │    │  ┌─────────────────────────┐   │ │
│  │                     │    │  │ Persona/Coordinator/etc │   │ │
│  │                     │    │  │ (Basic SNS Messages)    │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### **🚀 ENHANCED ARCHITECTURE (ACP + Future A2A):**
```
┌─────────────────────────────────────────────────────────────────┐
│                    BUILDINGOS - ENHANCED COMMUNICATION          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🌐 EXTERNAL SYSTEMS         🔄 INTERNAL AGENTS (ACP)          │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │                     │    │                                │ │
│  │  ┌─────────────┐   │    │  ┌─────────────────────────┐   │ │
│  │  │ PSIM API    │◄──┼────┼──│ Agent PSIM             │   │ │
│  │  └─────────────┘   │    │  │ (Direct HTTP)           │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │  ┌─────────────┐   │    │              ▲                 │ │
│  │  │ Elevator API│◄──┼────┼──│ Agent Elevator         │   │ │
│  │  └─────────────┘   │    │  │ (Direct HTTP)           │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │  ┌─────────────┐   │    │              ▲                 │ │
│  │  │ ERP API     │◄──┼────┼──│ Agent ERP              │   │ │
│  │  └─────────────┘   │    │  │ (Direct HTTP)           │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │                     │    │              ▲                 │ │
│  │  ┌─────────────┐   │    │      🔒 ACP/SNS (Validated)     │ │
│  │  │ External    │   │    │  ┌─────────────────────────┐   │ │
│  │  │ A2A Agents  │◄──┼────┼──│ 🎯 AGENT DIPLOMATA     │   │ │
│  │  │ (Future)    │   │    │  │ (A2A Protocol - Future) │   │ │
│  │  └─────────────┘   │    │  └─────────────────────────┘   │ │
│  │                     │    │              ▲                 │ │
│  │                     │    │      🔒 ACP/SNS (Validated)     │ │
│  │                     │    │  ┌─────────────────────────┐   │ │
│  │                     │    │  │ 🎯 AGENT DIRECTOR      │   │ │
│  │                     │    │  │ (ACP Orchestrator)      │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  │                     │    │              ▲                 │ │
│  │                     │    │      🔒 ACP/SNS (Validated)     │ │
│  │                     │    │  ┌─────────────────────────┐   │ │
│  │                     │    │  │ Persona/Coordinator/etc │   │ │
│  │                     │    │  │ (ACP Enhanced)          │   │ │
│  │                     │    │  └─────────────────────────┘   │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     PYDANTIC AI CORE ENGINE                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐ ┌─────────────────┐ ┌─────────────────────┐  │
│  │ ACP Message   │ │ Conversation    │ │ Type Safety &       │  │
│  │ Validation    │ │ Threading       │ │ Auto Serialization  │  │
│  └───────────────┘ └─────────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Technical Implementation Strategy**

### **Phase 1: ACP Protocol Implementation (Current Scope - 6 Days)**

#### **1.1 Enhanced Message Models**

**Current Protocol:**
```python
@dataclass
class SNSMessage:
    message_type: str
    correlation_id: str
    data: Dict[str, Any]  # ❌ Unstructured

@dataclass  
class MissionMessage(SNSMessage):
    mission_id: str
    tasks: List[Dict[str, Any]]  # ❌ Unstructured
```

**ACP Protocol:**
```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum

class ACPMessageType(Enum):
    """Structured message types for agent communication"""
    INFORM = "inform"      # Information sharing
    REQUEST = "request"    # Action request
    PROPOSE = "propose"    # Proposal/suggestion
    ACCEPT = "accept"      # Acceptance confirmation
    REJECT = "reject"      # Rejection with reason

class Priority(Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ACPMessage(BaseModel):
    """Enhanced Agent Communication Protocol message"""
    protocol: Literal["ACP"] = "ACP"
    version: Literal["1.0"] = "1.0"
    message_id: str = Field(..., description="UUID v4 unique identifier")
    conversation_id: str = Field(..., description="Thread tracking identifier")
    sender_agent: AgentType = Field(..., description="Typed sender agent")
    receiver_agent: AgentType = Field(..., description="Typed receiver agent")
    message_type: ACPMessageType = Field(..., description="Structured message type")
    priority: Priority = Field(default=Priority.MEDIUM, description="Message priority")
    content: Dict[str, Any] = Field(..., description="Validated message content")
    reply_to: Optional[str] = Field(None, description="Reference to original message")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = Field(None, description="Message expiration")

class PersonaToDirectorRequest(ACPMessage):
    """Persona requesting mission planning from Director"""
    sender_agent: Literal[AgentType.PERSONA] = AgentType.PERSONA
    receiver_agent: Literal[AgentType.DIRECTOR] = AgentType.DIRECTOR
    message_type: Literal[ACPMessageType.REQUEST] = ACPMessageType.REQUEST
    
    class ContentModel(BaseModel):
        user_intention: str = Field(..., min_length=1, max_length=1000)
        user_id: str = Field(..., min_length=1)
        context: Dict[str, Any] = Field(default_factory=dict)
        priority: Priority = Field(default=Priority.MEDIUM)
    
    content: ContentModel = Field(..., description="Validated request content")

class DirectorToCoordinatorMission(ACPMessage):
    """Director sending mission plan to Coordinator"""
    sender_agent: Literal[AgentType.DIRECTOR] = AgentType.DIRECTOR
    receiver_agent: Literal[AgentType.COORDINATOR] = AgentType.COORDINATOR
    message_type: Literal[ACPMessageType.INFORM] = ACPMessageType.INFORM
    
    class ContentModel(BaseModel):
        mission_id: str = Field(..., min_length=1)
        mission_plan: str = Field(..., min_length=1)
        tasks: List[Dict[str, Any]] = Field(..., min_items=1)
        estimated_duration: int = Field(..., gt=0, description="Duration in seconds")
    
    content: ContentModel = Field(..., description="Validated mission content")
```

#### **1.2 PydanticAI Agent Enhancement**

```python
from pydantic_ai import Agent
from typing import Dict, Any, List

class BuildingOSAgent:
    """Enhanced BuildingOS agent with ACP communication capabilities"""
    
    def __init__(self, agent_type: AgentType, instructions: str):
        self.agent_type = agent_type
        self.conversation_threads: Dict[str, List[ACPMessage]] = {}
        
        # Initialize PydanticAI agent with tools
        self.pydantic_agent = Agent(
            'aws-bedrock:claude-3-sonnet',
            instructions=f"{instructions}\n\nYou communicate using structured ACP messages.",
            tools=[
                self.send_acp_message,
                self.get_conversation_history,
                self.validate_message_content
            ]
        )
    
    async def send_acp_message(self, message: ACPMessage) -> ACPMessage:
        """Send validated ACP message via SNS"""
        try:
            # Validate message structure
            validated_message = message.model_validate(message.model_dump())
            
            # Store in conversation thread
            if message.conversation_id not in self.conversation_threads:
                self.conversation_threads[message.conversation_id] = []
            self.conversation_threads[message.conversation_id].append(validated_message)
            
            # Publish to appropriate SNS topic with validation
            topic_arn = self._get_topic_for_receiver(message.receiver_agent)
            sns_payload = {
                "Message": validated_message.model_dump_json(),
                "MessageAttributes": {
                    "protocol": {"DataType": "String", "StringValue": "ACP"},
                    "sender": {"DataType": "String", "StringValue": message.sender_agent.value},
                    "receiver": {"DataType": "String", "StringValue": message.receiver_agent.value},
                    "message_type": {"DataType": "String", "StringValue": message.message_type.value},
                    "priority": {"DataType": "String", "StringValue": message.priority.value}
                }
            }
            
            # Publish via SNS
            response = await self.sns_client.publish(
                TopicArn=topic_arn,
                **sns_payload
            )
            
            return validated_message
            
        except ValidationError as e:
            logger.error(f"ACP message validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"ACP message sending failed: {e}")
            raise
    
    async def receive_acp_message(self, sns_event: Dict) -> ACPMessage:
        """Receive and validate ACP message from SNS"""
        try:
            message_body = json.loads(sns_event['Records'][0]['Sns']['Message'])
            
            # Validate as ACP message
            acp_message = ACPMessage.model_validate(message_body)
            
            # Store in conversation thread
            if acp_message.conversation_id not in self.conversation_threads:
                self.conversation_threads[acp_message.conversation_id] = []
            self.conversation_threads[acp_message.conversation_id].append(acp_message)
            
            return acp_message
            
        except ValidationError as e:
            logger.error(f"ACP message validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"ACP message processing failed: {e}")
            raise
    
    def get_conversation_history(self, conversation_id: str) -> List[ACPMessage]:
        """Get conversation thread history"""
        return self.conversation_threads.get(conversation_id, [])
    
    def validate_message_content(self, content: Dict[str, Any], message_type: str) -> bool:
        """Validate message content against expected schema"""
        # Implementation specific to message type
        pass
```

#### **1.3 SNS Topic Enhancement**

```python
class ACPSNSHandler:
    """Enhanced SNS handler with ACP protocol support"""
    
    def __init__(self, agent: BuildingOSAgent):
        self.agent = agent
    
    async def handle_sns_event(self, event: Dict, context: Any) -> Dict:
        """Handle SNS event with ACP protocol validation"""
        try:
            # Extract and validate ACP message
            acp_message = await self.agent.receive_acp_message(event)
            
            # Process based on message type
            if acp_message.message_type == ACPMessageType.REQUEST:
                response = await self._handle_request(acp_message)
            elif acp_message.message_type == ACPMessageType.INFORM:
                response = await self._handle_inform(acp_message)
            elif acp_message.message_type == ACPMessageType.PROPOSE:
                response = await self._handle_propose(acp_message)
            else:
                response = await self._handle_generic(acp_message)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "ACP message processed successfully",
                    "conversation_id": acp_message.conversation_id,
                    "processed_message_id": acp_message.message_id
                })
            }
            
        except ValidationError as e:
            logger.error(f"ACP validation error: {e}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid ACP message format"})
            }
        except Exception as e:
            logger.error(f"ACP processing error: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "ACP message processing failed"})
            }
```

### **Phase 2: Future A2A Infrastructure (Future Scope)**

#### **2.1 Agent Diplomata (Future Implementation)**

```python
from fasta2a import A2AServer
from fastapi import FastAPI

class AgentDiplomata:
    """Centralized gateway for external A2A agent communication (Future)"""
    
    def __init__(self):
        self.external_agents: Dict[str, Agent] = {}
        self.app = FastAPI()
        
    def register_external_agent(self, agent_id: str, capabilities: List[str]):
        """Register external A2A compatible agent"""
        agent = Agent(
            'aws-bedrock:claude-3-sonnet',
            instructions=f"External agent {agent_id} with capabilities: {capabilities}"
        )
        self.external_agents[agent_id] = agent
        
        # Expose as A2A endpoint
        self.app.mount(f"/{agent_id}", agent.to_a2a())
    
    async def translate_acp_to_a2a(self, acp_message: ACPMessage) -> Dict:
        """Translate internal ACP message to external A2A format"""
        # Future implementation
        pass
    
    async def translate_a2a_to_acp(self, a2a_message: Dict) -> ACPMessage:
        """Translate external A2A message to internal ACP format"""
        # Future implementation
        pass
```

---

## 🎯 **Benefits Analysis**

### **🔄 ACP Protocol Benefits (Current Implementation):**

#### **1. 🛡️ Type Safety & Validation**
- **Before**: `Dict[str, Any]` allows any unvalidated data
- **After**: Pydantic models with automatic validation and type checking
- **Impact**: Prevents runtime errors, catches issues at build time

#### **2. 🧵 Conversation Threading**
- **Before**: Basic correlation_id without conversation context
- **After**: Full conversation threading with message history
- **Impact**: Better debugging, context preservation, conversation analytics

#### **3. 🎯 Structured Message Types**
- **Before**: Free-form message_type strings
- **After**: Enum-based structured message types (inform, request, propose, accept, reject)
- **Impact**: Consistent communication patterns, better agent coordination

#### **4. 🔍 Enhanced Debugging**
- **Before**: Limited debugging with basic correlation
- **After**: Rich message metadata, conversation tracking, validation logs
- **Impact**: Faster issue resolution, better system observability

#### **5. 📊 Performance Monitoring**
- **Before**: Basic message counting
- **After**: Priority-based metrics, agent communication patterns, conversation analytics
- **Impact**: Better system optimization, SLA monitoring, capacity planning

#### **6. 🚀 Automatic Serialization**
- **Before**: Manual dict conversion prone to errors
- **After**: Pydantic automatic serialization/deserialization
- **Impact**: Consistent data formats, reduced serialization bugs

### **🌐 A2A Protocol Benefits (Future Implementation):**
1. **Industry Standard**: Compatible with Google's A2A specification
2. **Vendor Agnostic**: Works with any A2A-compliant external agent system
3. **Scalable Integration**: Easy addition of new external intelligent agents
4. **Protocol Translation**: Seamless ACP ↔ A2A message conversion

---

## 📊 **Success Metrics**

### **Technical Metrics:**
- **Type Safety**: 100% of internal messages validated via ACP protocol
- **Performance**: < 25ms additional latency for ACP validation
- **Error Rate**: < 0.05% ACP validation failures
- **Conversation Tracking**: 100% message threading coverage

### **Operational Metrics:**
- **Agent Reliability**: 99.95% successful agent-to-agent communications
- **Debugging Efficiency**: 50% faster issue resolution with conversation threading
- **Monitoring Coverage**: 100% ACP communications tracked in CloudWatch

### **Business Metrics:**
- **Development Velocity**: 30% faster agent integration with type-safe protocols
- **System Reliability**: 99.97% uptime for agent communication
- **Future Readiness**: Infrastructure prepared for external A2A agent integration

---

## 🚀 **Implementation Plan**

### **📅 Timeline: 6 Days (ACP Focus)**

**Days 1-2: ACP Message Models**
- [ ] Design and implement ACP message base classes
- [ ] Create agent-specific message types (Persona, Director, Coordinator)
- [ ] Implement Pydantic validation schemas
- [ ] Unit tests for message validation

**Days 3-4: Agent Enhancement**
- [ ] Enhance existing agents with ACP communication capabilities
- [ ] Implement conversation threading and history tracking
- [ ] Update SNS handlers with ACP protocol support
- [ ] Integration tests for ACP message flow

**Days 5-6: Integration & Monitoring**
- [ ] End-to-end testing of ACP protocol
- [ ] CloudWatch dashboards for ACP communication metrics
- [ ] Performance benchmarking and optimization
- [ ] Documentation and team training

### **📅 Future Phase: A2A Integration (When Needed)**
- Agent Diplomata implementation
- External A2A agent registration system
- Protocol translation layer (ACP ↔ A2A)
- A2A endpoint exposure via API Gateway

---

## 🔄 **Migration Strategy**

### **Backward Compatibility:**
1. **Dual Protocol Support**: Both current SNS and new ACP during transition
2. **Gradual Agent Migration**: One agent type at a time
3. **Fallback Mechanisms**: Automatic fallback to current protocol if ACP fails
4. **Feature Flags**: Toggle between protocols for controlled rollout

### **Rollback Plan:**
1. **Protocol Toggle**: Feature flags to disable ACP and revert to current SNS
2. **Infrastructure Rollback**: Keep existing SNS message handlers operational
3. **Data Rollback**: No data migration required, only protocol changes
4. **Monitoring**: Real-time monitoring of protocol performance and errors

---

## 🏁 **Conclusion**

This ADR proposes enhancing BuildingOS with **Agent Communication Protocol (ACP)** for internal agent coordination, providing significant improvements in type safety, debugging capabilities, and system observability. The implementation also prepares the foundation for future **A2A protocol integration** when external intelligent agent systems are identified.

### **Key Improvements:**
1. **Type-Safe Communication**: Pydantic-validated messages replace unstructured Dict data
2. **Conversation Threading**: Full conversation tracking and context preservation
3. **Enhanced Debugging**: Rich message metadata and validation logs
4. **Performance Monitoring**: Priority-based metrics and communication analytics
5. **Future-Ready Architecture**: Foundation for external A2A agent integration

### **Implementation Approach:**
- **Phase 1**: ACP protocol for internal agents (6 days)
- **Phase 2**: A2A infrastructure when external agents are identified
- **Migration**: Gradual rollout with backward compatibility

The implementation builds upon our successful Pydantic migration (Step 2.5) and CodeBuild infrastructure (ADR-018), ensuring a solid technical foundation for enhanced agent communication.

**Recommendation: APPROVE** for immediate implementation as **Step 2.6: ACP Communication Protocol Enhancement**.
