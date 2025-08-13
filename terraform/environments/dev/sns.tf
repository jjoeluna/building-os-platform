# =============================================================================
# BuildingOS Platform - SNS Topics & Event Bus Configuration
# =============================================================================
# 
# **Purpose:** Complete SNS event bus implementation for BuildingOS platform
# **Scope:** Defines all 8 SNS topics for inter-agent communication
# **Usage:** Deployed by Terraform in dev environment for event-driven architecture
# 
# **Event Bus Architecture:**
# 1. Chat Flow: WebSocket → chat-intention → persona-intention → director-mission
# 2. Task Flow: coordinator-task → agent-task-result → coordinator-mission-result
# 3. Response Flow: director-response → persona-response → WebSocket broadcast
# 
# **Key Features:**
# - Standardized topic naming convention using global module
# - Comprehensive tagging for governance and monitoring
# - IAM integration for secure publish/subscribe access
# - CloudWatch monitoring and alerting integration
# - Scalable event-driven communication patterns
# 
# **Dependencies:**
# - Global sns_topic module for standardized topic creation
# - IAM policies for Lambda function publish permissions
# - CloudWatch for monitoring and alerting
# - Lambda functions for event processing and subscriptions
# 
# **Integration:**
# - All 10 Lambda functions participate in event-driven communication
# - WebSocket API for real-time user interaction
# - DynamoDB for state persistence between events
# - Monitoring dashboards for event flow visibility
# 
# **Performance:**
# - Standard topics for high-throughput message processing
# - Optimized delivery policies for reliable message delivery
# - Dead letter queue support for failed message handling
# 
# =============================================================================

# =============================================================================
# Chat Flow Topics - User Interaction Processing
# =============================================================================

# --- Chat Intention Topic ---
# Purpose: Processes initial user messages from WebSocket connections
# Flow: WebSocket Default → Chat Intention Topic → Persona Agent
# Subscribers: agent_persona (processes user chat intentions)
module "chat_intention_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.chat_intention
  display_name = "BuildingOS Chat Intention Processing"

  tags = merge(local.common_tags, {
    Name      = "chat-intention-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Chat Intention"
    Phase     = "2-Communication"
    Flow      = "Chat Processing"
    ManagedBy = "Terraform"
  })
}

# --- Persona Intention Topic ---
# Purpose: Processes analyzed user intentions from Persona Agent
# Flow: Persona Agent → Persona Intention Topic → Director Agent  
# Subscribers: agent_director (receives structured user intentions)
module "persona_intention_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.persona_intention
  display_name = "BuildingOS Persona Intention Analysis"

  tags = merge(local.common_tags, {
    Name      = "persona-intention-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Persona Intention"
    Phase     = "2-Communication"
    Flow      = "Chat Processing"
    ManagedBy = "Terraform"
  })
}

# =============================================================================
# Mission Flow Topics - Task Planning and Execution
# =============================================================================

# --- Director Mission Topic ---
# Purpose: Distributes mission plans created by Director Agent
# Flow: Director Agent → Director Mission Topic → Coordinator Agent
# Subscribers: agent_coordinator (receives and orchestrates mission execution)
module "director_mission_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.director_mission
  display_name = "BuildingOS Director Mission Planning"

  tags = merge(local.common_tags, {
    Name      = "director-mission-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Director Mission"
    Phase     = "2-Communication"
    Flow      = "Mission Planning"
    ManagedBy = "Terraform"
  })
}

# --- Coordinator Task Topic ---
# Purpose: Distributes individual tasks to specialized agent tools
# Flow: Coordinator Agent → Coordinator Task Topic → Agent Tools (Elevator/PSIM)
# Subscribers: agent_elevator, agent_psim (execute specific building operations)
module "coordinator_task_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.coordinator_task
  display_name = "BuildingOS Coordinator Task Distribution"

  tags = merge(local.common_tags, {
    Name      = "coordinator-task-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Coordinator Task"
    Phase     = "2-Communication"
    Flow      = "Task Execution"
    ManagedBy = "Terraform"
  })
}

# --- Agent Task Result Topic ---
# Purpose: Collects task completion results from agent tools
# Flow: Agent Tools (Elevator/PSIM) → Agent Task Result Topic → Coordinator Agent
# Publishers: agent_elevator, agent_psim (report task completion status)
module "agent_task_result_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.agent_task_result
  display_name = "BuildingOS Agent Task Result Collection"

  tags = merge(local.common_tags, {
    Name      = "agent-task-result-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Agent Task Result"
    Phase     = "2-Communication"
    Flow      = "Task Execution"
    ManagedBy = "Terraform"
  })
}

# --- Coordinator Mission Result Topic ---
# Purpose: Reports mission completion status back to Director
# Flow: Coordinator Agent → Coordinator Mission Result Topic → Director Agent
# Subscribers: agent_director (receives mission completion notifications)
module "coordinator_mission_result_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.coordinator_mission_result
  display_name = "BuildingOS Coordinator Mission Result Reporting"

  tags = merge(local.common_tags, {
    Name      = "coordinator-mission-result-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Coordinator Mission Result"
    Phase     = "2-Communication"
    Flow      = "Mission Completion"
    ManagedBy = "Terraform"
  })
}

# =============================================================================
# Response Flow Topics - User Feedback and Communication
# =============================================================================

# --- Director Response Topic ---
# Purpose: Delivers Director's responses back to Persona for user communication
# Flow: Director Agent → Director Response Topic → Persona Agent
# Subscribers: agent_persona (formats responses for user presentation)
module "director_response_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.director_response
  display_name = "BuildingOS Director Response Communication"

  tags = merge(local.common_tags, {
    Name      = "director-response-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Director Response"
    Phase     = "2-Communication"
    Flow      = "Response Communication"
    ManagedBy = "Terraform"
  })
}

# --- Persona Response Topic ---
# Purpose: Delivers final formatted responses to WebSocket for user delivery
# Flow: Persona Agent → Persona Response Topic → WebSocket Broadcast
# Subscribers: websocket_broadcast (delivers responses to connected users)
module "persona_response_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.persona_response
  display_name = "BuildingOS Persona Response Delivery"

  tags = merge(local.common_tags, {
    Name      = "persona-response-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Persona Response"
    Phase     = "2-Communication"
    Flow      = "Response Communication"
    ManagedBy = "Terraform"
  })
}

# =============================================================================
# ACP Standard Topics - Protocol Compliance
# =============================================================================

# --- ACP Task Topic ---
# Purpose: Standard ACP task distribution following official protocol
# Flow: Any Agent → ACP Task Topic → Target Agents
# Subscribers: All agents that support ACP standard task processing
module "acp_task_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.acp_task
  display_name = "BuildingOS ACP Standard Task Distribution"

  tags = merge(local.common_tags, {
    Name      = "acp-task-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "ACP Task"
    Phase     = "2-Communication"
    Flow      = "ACP Standard"
    Protocol  = "ACP"
    ManagedBy = "Terraform"
  })
}

# --- ACP Result Topic ---
# Purpose: Standard ACP result collection following official protocol
# Flow: Target Agents → ACP Result Topic → Requesting Agents
# Publishers: All agents that complete ACP standard tasks
module "acp_result_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.acp_result
  display_name = "BuildingOS ACP Standard Result Collection"

  tags = merge(local.common_tags, {
    Name      = "acp-result-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "ACP Result"
    Phase     = "2-Communication"
    Flow      = "ACP Standard"
    Protocol  = "ACP"
    ManagedBy = "Terraform"
  })
}

# --- ACP Event Topic ---
# Purpose: Standard ACP event broadcasting following official protocol
# Flow: Any Agent → ACP Event Topic → All Subscribed Agents
# Subscribers: All agents that need to receive system-wide events
module "acp_event_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.acp_event
  display_name = "BuildingOS ACP Standard Event Broadcasting"

  tags = merge(local.common_tags, {
    Name      = "acp-event-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "ACP Event"
    Phase     = "2-Communication"
    Flow      = "ACP Standard"
    Protocol  = "ACP"
    ManagedBy = "Terraform"
  })
}

# --- ACP Heartbeat Topic ---
# Purpose: Standard ACP heartbeat monitoring following official protocol
# Flow: All Agents → ACP Heartbeat Topic → Health Monitoring
# Subscribers: agent_health_check (monitors agent health status)
module "acp_heartbeat_topic" {
  source = "../../modules/sns_topic"

  name         = local.sns_topic_names.acp_heartbeat
  display_name = "BuildingOS ACP Standard Heartbeat Monitoring"

  tags = merge(local.common_tags, {
    Name      = "acp-heartbeat-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "ACP Heartbeat"
    Phase     = "2-Communication"
    Flow      = "ACP Standard"
    Protocol  = "ACP"
    ManagedBy = "Terraform"
  })
}
