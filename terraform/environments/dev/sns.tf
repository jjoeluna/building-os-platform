# =============================================================================
# SNS Topics - BuildingOS Platform
# =============================================================================
# This file contains all SNS topic definitions using the global sns_topic module
# =============================================================================

# --- Chat Intention Topic ---
module "chat_intention_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.chat_intention

  tags = merge(local.common_tags, {
    Name      = "chat-intention-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Chat Intention"
    ManagedBy = "Terraform"
  })
}

# --- Persona Intention Topic ---
module "persona_intention_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.persona_intention

  tags = merge(local.common_tags, {
    Name      = "persona-intention-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Persona Intention"
    ManagedBy = "Terraform"
  })
}

# --- Director Mission Topic ---
module "director_mission_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.director_mission

  tags = merge(local.common_tags, {
    Name      = "director-mission-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Director Mission"
    ManagedBy = "Terraform"
  })
}

# --- Coordinator Task Topic ---
module "coordinator_task_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.coordinator_task

  tags = merge(local.common_tags, {
    Name      = "coordinator-task-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Coordinator Task"
    ManagedBy = "Terraform"
  })
}

# --- Agent Task Result Topic ---
module "agent_task_result_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.agent_task_result

  tags = merge(local.common_tags, {
    Name      = "agent-task-result-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Agent Task Result"
    ManagedBy = "Terraform"
  })
}

# --- Coordinator Mission Result Topic ---
module "coordinator_mission_result_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.coordinator_mission_result

  tags = merge(local.common_tags, {
    Name      = "coordinator-mission-result-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Coordinator Mission Result"
    ManagedBy = "Terraform"
  })
}

# --- Director Response Topic ---
module "director_response_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.director_response

  tags = merge(local.common_tags, {
    Name      = "director-response-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Director Response"
    ManagedBy = "Terraform"
  })
}

# --- Persona Response Topic ---
module "persona_response_topic" {
  source = "../../modules/sns_topic"

  name = local.sns_topic_names.persona_response

  tags = merge(local.common_tags, {
    Name      = "persona-response-topic"
    Type      = "SNS Topic"
    Component = "Communication"
    Function  = "Persona Response"
    ManagedBy = "Terraform"
  })
}
