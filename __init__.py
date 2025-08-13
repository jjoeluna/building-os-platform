# Common utilities for BuildingOS Lambda functions
from .aws_clients import *
from .models import *
from .pydantic_models import *
from .acp_protocol import *
from .pydantic_agents import *
from .utils import *

__all__ = [
    # AWS clients
    'get_sns_client',
    'get_dynamodb_client', 
    'get_s3_client',
    'get_bedrock_client',
    
    # Models (legacy - keep for backward compatibility)
    'ComponentHealth',
    'HealthStatus',
    'SystemHealth',
    'SNSMessage',
    'TaskMessage', 
    'MissionMessage',
    'AgentType',
    'Priority',
    
    # Pydantic models (new enhanced models)
    'SNSMessage as PydanticSNSMessage',
    'TaskMessage as PydanticTaskMessage',
    'MissionMessage as PydanticMissionMessage',
    'PersonaRequest',
    'PersonaResponse',
    'DirectorRequest',
    'DirectorResponse',
    'CoordinatorRequest',
    'CoordinatorResponse',
    'PSIMRequest',
    'PSIMResponse', 
    'ElevatorRequest',
    'ElevatorResponse',
    'HealthCheckResponse',
    'DynamoDBItem',
    'WebSocketConnection',
    'MissionState',
    'ShortTermMemory',
    'ElevatorMonitoring',
    
    # ACP Protocol (Agent Communication Protocol)
    'ACPMessage',
    'ACPMessageType',
    'Priority as ACPPriority',
    'ConversationThread',
    'PersonaToDirectorRequest',
    'DirectorToCoordinatorMission',
    'CoordinatorToToolRequest',
    'ToolToCoordinatorResponse',
    'CoordinatorToDirectorUpdate',
    'DirectorToPersonaResponse',
    
    # PydanticAI Agents
    'BuildingOSAgent',
    'AgentContext',
    'AgentResponse',
    'PersonaAgent',
    'DirectorAgent',
    'CoordinatorAgent',
    
    # Utilities
    'setup_logging',
    'get_correlation_id',
    'create_response',
    'create_error_response',
    'get_environment_variable',
    'validate_required_env_vars',
]
