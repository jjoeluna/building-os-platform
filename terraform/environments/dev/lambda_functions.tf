# =============================================================================
# Lambda Functions Configuration - Enhanced with CodeBuild Layer Support
# =============================================================================

# S3 Buckets for CodeBuild
resource "aws_s3_bucket" "lambda_build_artifacts" {
  bucket = "buildingos-lambda-artifacts-${var.environment}"

  tags = {
    Name        = "buildingos-lambda-artifacts-${var.environment}"
    Environment = var.environment
    Component   = "Lambda Build"
    ManagedBy   = "Terraform"
    Project     = "BuildingOS"
  }
}

resource "aws_s3_bucket" "lambda_build_source" {
  bucket = "buildingos-lambda-source-${var.environment}"

  tags = {
    Name        = "buildingos-lambda-source-${var.environment}"
    Environment = var.environment
    Component   = "Lambda Build"
    ManagedBy   = "Terraform"
    Project     = "BuildingOS"
  }
}

# Create source archive for CodeBuild
data "archive_file" "layer_source" {
  type        = "zip"
  source_dir  = "../../../src/layers/common_utils"
  output_path = "../../.terraform/layer_source.zip"
}

# Common Utils Layer with CodeBuild (Pydantic-compatible)
module "common_utils_layer_codebuild" {
  source = "../../modules/lambda_layer_codebuild"

  environment          = var.environment
  layer_name           = "bos-${var.environment}-common-utils-layer"
  requirements_file    = "../../../src/layers/common_utils/requirements.txt"
  source_dir           = "../../../src/layers/common_utils"
  source_archive       = data.archive_file.layer_source.output_path
  source_bucket        = aws_s3_bucket.lambda_build_source.bucket
  source_key           = "common_utils/source.zip"
  source_bucket_arn    = aws_s3_bucket.lambda_build_source.arn
  artifacts_bucket     = aws_s3_bucket.lambda_build_artifacts.bucket
  artifacts_bucket_arn = aws_s3_bucket.lambda_build_artifacts.arn
}

# Fallback layer removed - using CodeBuild layer only
# module "common_utils_layer" {
#   source = "../../modules/lambda_layer"
#
#   layer_name        = "bos-${var.environment}-common-utils-layer-fallback"
#   requirements_file = "../../../src/layers/common_utils/requirements.txt"
#   source_dir        = "../../../src/layers/common_utils/python"
#   runtime          = "python3.11"
# }

# Use CodeBuild layer exclusively
locals {
  common_layer_arn = module.common_utils_layer_codebuild.layer_arn
}

# --- WebSocket Lambda Functions ---

# WebSocket Connect
module "websocket_connect" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.websocket_connect
  description   = "BuildingOS WebSocket Connect - Handles WebSocket connection establishment"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/tools/websocket_connect"
  timeout       = local.lambda_performance_configs.websocket_connect.timeout
  memory_size   = local.lambda_performance_configs.websocket_connect.memory_size

  environment_variables = {
    CONNECTIONS_TABLE = aws_dynamodb_table.websocket_connections.name
    LOG_LEVEL         = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  enable_api_gateway_integration = true
  api_gateway_source_arn         = "${module.websocket_api.websocket_api_execution_arn}/*"

  tags = merge(local.common_tags, {
    Name      = "websocket-connect"
    Type      = "Lambda Function"
    Component = "WebSocket"
    Function  = "Connect"
    ManagedBy = "Terraform"
  })
}

# WebSocket Disconnect
module "websocket_disconnect" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.websocket_disconnect
  description   = "BuildingOS WebSocket Disconnect - Handles WebSocket connection termination"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/tools/websocket_disconnect"
  timeout       = local.lambda_performance_configs.websocket_disconnect.timeout
  memory_size   = local.lambda_performance_configs.websocket_disconnect.memory_size

  environment_variables = {
    CONNECTIONS_TABLE = aws_dynamodb_table.websocket_connections.name
    LOG_LEVEL         = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  enable_api_gateway_integration = true
  api_gateway_source_arn         = "${module.websocket_api.websocket_api_execution_arn}/*"

  tags = merge(local.common_tags, {
    Name      = "websocket-disconnect"
    Type      = "Lambda Function"
    Component = "WebSocket"
    Function  = "Disconnect"
    ManagedBy = "Terraform"
  })
}

# WebSocket Default
module "websocket_default" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.websocket_default
  description   = "BuildingOS WebSocket Default - Handles default WebSocket message processing"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/tools/websocket_default"
  timeout       = local.lambda_performance_configs.websocket_default.timeout
  memory_size   = local.lambda_performance_configs.websocket_default.memory_size

  environment_variables = {
    CONNECTIONS_TABLE        = aws_dynamodb_table.websocket_connections.name
    CHAT_INTENTION_TOPIC_ARN = module.chat_intention_topic.topic_arn
    LOG_LEVEL                = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  enable_api_gateway_integration = true
  api_gateway_source_arn         = "${module.websocket_api.websocket_api_execution_arn}/*"

  tags = merge(local.common_tags, {
    Name      = "websocket-default"
    Type      = "Lambda Function"
    Component = "WebSocket"
    Function  = "Default"
    ManagedBy = "Terraform"
  })
}

# WebSocket Broadcast
module "websocket_broadcast" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.websocket_broadcast
  description   = "BuildingOS WebSocket Broadcast - Handles broadcasting messages to WebSocket connections"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/tools/websocket_broadcast"
  timeout       = local.lambda_performance_configs.websocket_broadcast.timeout
  memory_size   = local.lambda_performance_configs.websocket_broadcast.memory_size

  environment_variables = {
    CONNECTIONS_TABLE      = aws_dynamodb_table.websocket_connections.name
    WEBSOCKET_API_ENDPOINT = module.websocket_api.websocket_api_endpoint
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  enable_sns_integration = true
  sns_topic_arn          = module.persona_response_topic.topic_arn

  tags = merge(local.common_tags, {
    Name      = "websocket-broadcast"
    Type      = "Lambda Function"
    Component = "WebSocket"
    Function  = "Broadcast"
    ManagedBy = "Terraform"
  })
}

# --- Agent Lambda Functions ---

# Agent Health Check
module "agent_health_check" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_health_check
  description   = "BuildingOS Agent Health Check - Monitors the health of all agents"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_health_check"
  timeout       = local.lambda_performance_configs.agent_health_check.timeout
  memory_size   = local.lambda_performance_configs.agent_health_check.memory_size

  environment_variables = {
    # ACP Standard Topics (Health monitoring via heartbeat)
    ACP_TASK_TOPIC_ARN      = module.acp_task_topic.topic_arn
    ACP_RESULT_TOPIC_ARN    = module.acp_result_topic.topic_arn
    ACP_EVENT_TOPIC_ARN     = module.acp_event_topic.topic_arn
    ACP_HEARTBEAT_TOPIC_ARN = module.acp_heartbeat_topic.topic_arn
    LOG_LEVEL               = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  tags = merge(local.common_tags, {
    Name      = "agent-health-check"
    Type      = "Lambda Function"
    Component = "Agent"
    Function  = "Health Check"
    ManagedBy = "Terraform"
  })
}

# Agent Persona
module "agent_persona" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_persona
  description   = "BuildingOS Agent Persona - Manages user personas and conversations"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_persona"
  timeout       = local.lambda_performance_configs.agent_persona.timeout
  memory_size   = local.lambda_performance_configs.agent_persona.memory_size

  environment_variables = {
    SHORT_TERM_MEMORY_TABLE_NAME = module.short_term_memory_db.table_name
    # Persona Topics (Current)
    PERSONA_INTENTION_TOPIC_ARN = module.persona_intention_topic.topic_arn
    DIRECTOR_RESPONSE_TOPIC_ARN = module.director_response_topic.topic_arn
    PERSONA_RESPONSE_TOPIC_ARN  = module.persona_response_topic.topic_arn
    # ACP Standard Topics (New)
    ACP_TASK_TOPIC_ARN      = module.acp_task_topic.topic_arn
    ACP_RESULT_TOPIC_ARN    = module.acp_result_topic.topic_arn
    ACP_EVENT_TOPIC_ARN     = module.acp_event_topic.topic_arn
    ACP_HEARTBEAT_TOPIC_ARN = module.acp_heartbeat_topic.topic_arn
    LOG_LEVEL               = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment FOR TESTING
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  # SNS Integration - Multiple topic subscriptions for Persona Agent
  enable_sns_integration = true
  sns_topic_arn          = module.chat_intention_topic.topic_arn

  tags = merge(local.common_tags, {
    Name      = "agent-persona"
    Type      = "Lambda Function"
    Component = "Agent"
    Function  = "Persona"
    ManagedBy = "Terraform"
  })
}

# Additional SNS subscription for Persona Agent - Director Responses
resource "aws_sns_topic_subscription" "persona_director_responses" {
  topic_arn = module.director_response_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_persona.function_arn
}

# Lambda permission for Persona Agent - Director Responses
resource "aws_lambda_permission" "persona_director_responses" {
  statement_id  = "AllowExecutionFromDirectorResponses"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_persona.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.director_response_topic.topic_arn
}

# Agent Director
module "agent_director" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_director
  description   = "BuildingOS Agent Director - Orchestrates mission planning and execution"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_director"
  timeout       = local.lambda_performance_configs.agent_director.timeout
  memory_size   = local.lambda_performance_configs.agent_director.memory_size

  environment_variables = {
    # Director Topics (Current)
    PERSONA_INTENTION_TOPIC_ARN          = module.persona_intention_topic.topic_arn
    DIRECTOR_MISSION_TOPIC_ARN           = module.director_mission_topic.topic_arn
    DIRECTOR_RESPONSE_TOPIC_ARN          = module.director_response_topic.topic_arn
    COORDINATOR_MISSION_RESULT_TOPIC_ARN = module.coordinator_mission_result_topic.topic_arn
    # ACP Standard Topics (New)
    ACP_TASK_TOPIC_ARN      = module.acp_task_topic.topic_arn
    ACP_RESULT_TOPIC_ARN    = module.acp_result_topic.topic_arn
    ACP_EVENT_TOPIC_ARN     = module.acp_event_topic.topic_arn
    ACP_HEARTBEAT_TOPIC_ARN = module.acp_heartbeat_topic.topic_arn
    # Memory and Logging
    MISSION_STATE_TABLE_NAME = module.mission_state_db.table_name
    LOG_LEVEL                = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment FOR TESTING
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  # SNS Integration - Multiple topic subscriptions for Director Agent
  enable_sns_integration = true
  sns_topic_arn          = module.persona_intention_topic.topic_arn

  tags = merge(local.common_tags, {
    Name      = "agent-director"
    Type      = "Lambda Function"
    Component = "Agent"
    Function  = "Director"
    ManagedBy = "Terraform"
  })
}

# Additional SNS subscription for Director Agent - Coordinator Mission Results
resource "aws_sns_topic_subscription" "director_coordinator_results" {
  topic_arn = module.coordinator_mission_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_director.function_arn
}

# Lambda permission for Director Agent - Coordinator Mission Results
resource "aws_lambda_permission" "director_coordinator_results" {
  statement_id  = "AllowExecutionFromCoordinatorResults"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_director.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.coordinator_mission_result_topic.topic_arn
}

# Agent Coordinator
module "agent_coordinator" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_coordinator
  description   = "BuildingOS Agent Coordinator - Coordinates task execution and mission management"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_coordinator"
  timeout       = local.lambda_performance_configs.agent_coordinator.timeout
  memory_size   = local.lambda_performance_configs.agent_coordinator.memory_size

  environment_variables = {
    # Coordinator Topics (Current)
    COORDINATOR_TASK_TOPIC_ARN           = module.coordinator_task_topic.topic_arn
    AGENT_TASK_RESULT_TOPIC_ARN          = module.agent_task_result_topic.topic_arn
    COORDINATOR_MISSION_RESULT_TOPIC_ARN = module.coordinator_mission_result_topic.topic_arn
    # ACP Standard Topics (New)
    ACP_TASK_TOPIC_ARN      = module.acp_task_topic.topic_arn
    ACP_RESULT_TOPIC_ARN    = module.acp_result_topic.topic_arn
    ACP_EVENT_TOPIC_ARN     = module.acp_event_topic.topic_arn
    ACP_HEARTBEAT_TOPIC_ARN = module.acp_heartbeat_topic.topic_arn
    # Memory and Logging
    MISSION_STATE_TABLE_NAME = module.mission_state_db.table_name
    LOG_LEVEL                = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  # SNS Integration - Multiple topic subscriptions for Coordinator Agent  
  enable_sns_integration = true
  sns_topic_arn          = module.director_mission_topic.topic_arn

  tags = merge(local.common_tags, {
    Name      = "agent-coordinator"
    Type      = "Lambda Function"
    Component = "Agent"
    Function  = "Coordinator"
    ManagedBy = "Terraform"
  })
}

# Additional SNS subscription for Coordinator Agent - Agent Task Results
resource "aws_sns_topic_subscription" "coordinator_task_results" {
  topic_arn = module.agent_task_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_coordinator.function_arn
}

# Lambda permission for Coordinator Agent - Agent Task Results
resource "aws_lambda_permission" "coordinator_task_results" {
  statement_id  = "AllowExecutionFromTaskResults"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_coordinator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.agent_task_result_topic.topic_arn
}

# Agent Elevator
module "agent_elevator" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_elevator
  description   = "BuildingOS Agent Elevator - Manages elevator operations and monitoring"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_elevator"
  timeout       = local.lambda_performance_configs.agent_elevator.timeout
  memory_size   = local.lambda_performance_configs.agent_elevator.memory_size

  environment_variables = {
    # Elevator API Configuration
    ELEVATOR_API_BASE_URL = "http://elevador.clevertown.io:9090"
    ELEVATOR_API_SECRET   = "ACME_ELEVATOR_SECRET"
    # Agent Task Topics (Current)
    COORDINATOR_TASK_TOPIC_ARN  = module.coordinator_task_topic.topic_arn
    AGENT_TASK_RESULT_TOPIC_ARN = module.agent_task_result_topic.topic_arn
    # ACP Standard Topics (New)
    ACP_TASK_TOPIC_ARN      = module.acp_task_topic.topic_arn
    ACP_RESULT_TOPIC_ARN    = module.acp_result_topic.topic_arn
    ACP_EVENT_TOPIC_ARN     = module.acp_event_topic.topic_arn
    ACP_HEARTBEAT_TOPIC_ARN = module.acp_heartbeat_topic.topic_arn
    # Monitoring and Logging
    ELEVATOR_MONITORING_TABLE_NAME = module.elevator_monitoring_db.table_name
    LOG_LEVEL                      = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment FOR TESTING
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  enable_sns_integration = true
  sns_topic_arn          = module.coordinator_task_topic.topic_arn

  tags = merge(local.common_tags, {
    Name      = "agent-elevator"
    Type      = "Lambda Function"
    Component = "Agent"
    Function  = "Elevator"
    ManagedBy = "Terraform"
  })
}

# Agent PSIM
module "agent_psim" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_psim
  description   = "BuildingOS Agent PSIM - Integrates with PSIM system for building management"
  role_arn      = module.lambda_iam_role.role_arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_psim"
  timeout       = local.lambda_performance_configs.agent_psim.timeout
  memory_size   = local.lambda_performance_configs.agent_psim.memory_size

  environment_variables = {
    PSIM_API_BASE_URL = "http://psim.clevertown.io:9091"
    PSIM_API_USERNAME = "integration_blubrain"
    PSIM_API_PASSWORD = "Blubrain@4565"
    # Agent Task Topics (Current)
    COORDINATOR_TASK_TOPIC_ARN  = module.coordinator_task_topic.topic_arn
    AGENT_TASK_RESULT_TOPIC_ARN = module.agent_task_result_topic.topic_arn
    # ACP Standard Topics (New)
    ACP_TASK_TOPIC_ARN      = module.acp_task_topic.topic_arn
    ACP_RESULT_TOPIC_ARN    = module.acp_result_topic.topic_arn
    ACP_EVENT_TOPIC_ARN     = module.acp_event_topic.topic_arn
    ACP_HEARTBEAT_TOPIC_ARN = module.acp_heartbeat_topic.topic_arn
    LOG_LEVEL               = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers - Common utilities for all functions
  layers = [local.common_layer_arn]

  # VPC Configuration - Enabled for secure private subnet deployment
  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  enable_sns_integration = true
  sns_topic_arn          = module.coordinator_task_topic.topic_arn

  tags = merge(local.common_tags, {
    Name      = "agent-psim"
    Type      = "Lambda Function"
    Component = "Agent"
    Function  = "PSIM"
    ManagedBy = "Terraform"
  })
}

# =============================================================================
# ACP Standard Topic Subscriptions - Protocol Compliance
# =============================================================================

# ACP Task Topic Subscriptions - All agents can receive tasks
resource "aws_sns_topic_subscription" "acp_task_coordinator" {
  topic_arn = module.acp_task_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_coordinator.function_arn
}

resource "aws_sns_topic_subscription" "acp_task_elevator" {
  topic_arn = module.acp_task_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_elevator.function_arn
}

resource "aws_sns_topic_subscription" "acp_task_psim" {
  topic_arn = module.acp_task_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_psim.function_arn
}

# ACP Result Topic Subscriptions - Coordinator and Director receive results
resource "aws_sns_topic_subscription" "acp_result_coordinator" {
  topic_arn = module.acp_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_coordinator.function_arn
}

resource "aws_sns_topic_subscription" "acp_result_director" {
  topic_arn = module.acp_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_director.function_arn
}

# ACP Event Topic Subscriptions - All agents can receive events
resource "aws_sns_topic_subscription" "acp_event_persona" {
  topic_arn = module.acp_event_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_persona.function_arn
}

resource "aws_sns_topic_subscription" "acp_event_director" {
  topic_arn = module.acp_event_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_director.function_arn
}

resource "aws_sns_topic_subscription" "acp_event_coordinator" {
  topic_arn = module.acp_event_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_coordinator.function_arn
}

# ACP Heartbeat Topic Subscription - Health check monitors all heartbeats
resource "aws_sns_topic_subscription" "acp_heartbeat_health_check" {
  topic_arn = module.acp_heartbeat_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.agent_health_check.function_arn
}

# =============================================================================
# ACP Lambda Permissions - Allow SNS to invoke functions
# =============================================================================

# ACP Task Topic Permissions
resource "aws_lambda_permission" "acp_task_coordinator" {
  statement_id  = "AllowExecutionFromACPTask"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_coordinator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_task_topic.topic_arn
}

resource "aws_lambda_permission" "acp_task_elevator" {
  statement_id  = "AllowExecutionFromACPTask"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_elevator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_task_topic.topic_arn
}

resource "aws_lambda_permission" "acp_task_psim" {
  statement_id  = "AllowExecutionFromACPTask"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_psim.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_task_topic.topic_arn
}

# ACP Result Topic Permissions
resource "aws_lambda_permission" "acp_result_coordinator" {
  statement_id  = "AllowExecutionFromACPResult"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_coordinator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_result_topic.topic_arn
}

resource "aws_lambda_permission" "acp_result_director" {
  statement_id  = "AllowExecutionFromACPResult"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_director.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_result_topic.topic_arn
}

# ACP Event Topic Permissions
resource "aws_lambda_permission" "acp_event_persona" {
  statement_id  = "AllowExecutionFromACPEvent"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_persona.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_event_topic.topic_arn
}

resource "aws_lambda_permission" "acp_event_director" {
  statement_id  = "AllowExecutionFromACPEvent"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_director.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_event_topic.topic_arn
}

resource "aws_lambda_permission" "acp_event_coordinator" {
  statement_id  = "AllowExecutionFromACPEvent"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_coordinator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_event_topic.topic_arn
}

# ACP Heartbeat Topic Permission
resource "aws_lambda_permission" "acp_heartbeat_health_check" {
  statement_id  = "AllowExecutionFromACPHeartbeat"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_health_check.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.acp_heartbeat_topic.topic_arn
}
