# =============================================================================
# Lambda Functions - BuildingOS Platform
# =============================================================================
# This file contains all Lambda function definitions using the global lambda_function module
# =============================================================================

# --- WebSocket Lambda Functions ---

# WebSocket Connect
module "websocket_connect" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.websocket_connect
  description   = "BuildingOS WebSocket Connect - Handles WebSocket connection establishment"
  role_arn      = aws_iam_role.lambda_exec_role.arn
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

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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
  role_arn      = aws_iam_role.lambda_exec_role.arn
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

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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
  role_arn      = aws_iam_role.lambda_exec_role.arn
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

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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
  role_arn      = aws_iam_role.lambda_exec_role.arn
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

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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
  role_arn      = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_health_check"
  timeout       = local.lambda_performance_configs.agent_health_check.timeout
  memory_size   = local.lambda_performance_configs.agent_health_check.memory_size

  environment_variables = {
    LOG_LEVEL = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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
  role_arn      = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_persona"
  timeout       = local.lambda_performance_configs.agent_persona.timeout
  memory_size   = local.lambda_performance_configs.agent_persona.memory_size

  environment_variables = {
    SHORT_TERM_MEMORY_TABLE_NAME = module.short_term_memory_db.table_name
    PERSONA_INTENTION_TOPIC_ARN  = module.persona_intention_topic.topic_arn
    DIRECTOR_RESPONSE_TOPIC_ARN  = module.director_response_topic.topic_arn
    PERSONA_RESPONSE_TOPIC_ARN   = module.persona_response_topic.topic_arn
    LOG_LEVEL                    = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # VPC Configuration - TEMPORARILY DISABLED FOR TESTING
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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

# Agent Director
module "agent_director" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_director
  description   = "BuildingOS Agent Director - Orchestrates mission planning and execution"
  role_arn      = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_director"
  timeout       = local.lambda_performance_configs.agent_director.timeout
  memory_size   = local.lambda_performance_configs.agent_director.memory_size

  environment_variables = {
    # Mission Topics
    DIRECTOR_MISSION_TOPIC_ARN  = module.director_mission_topic.topic_arn
    DIRECTOR_RESPONSE_TOPIC_ARN = module.director_response_topic.topic_arn
    # Memory and Logging
    MISSION_STATE_TABLE_NAME = module.mission_state_db.table_name
    LOG_LEVEL                = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # VPC Configuration - TEMPORARILY DISABLED FOR TESTING
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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

# Agent Coordinator
module "agent_coordinator" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_coordinator
  description   = "BuildingOS Agent Coordinator - Coordinates task execution and mission management"
  role_arn      = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_coordinator"
  timeout       = local.lambda_performance_configs.agent_coordinator.timeout
  memory_size   = local.lambda_performance_configs.agent_coordinator.memory_size

  environment_variables = {
    # Coordinator Topics
    COORDINATOR_TASK_TOPIC_ARN           = module.coordinator_task_topic.topic_arn
    AGENT_TASK_RESULT_TOPIC_ARN          = module.agent_task_result_topic.topic_arn
    COORDINATOR_MISSION_RESULT_TOPIC_ARN = module.coordinator_mission_result_topic.topic_arn
    # Memory and Logging
    MISSION_STATE_TABLE_NAME = module.mission_state_db.table_name
    LOG_LEVEL                = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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

# Agent Elevator
module "agent_elevator" {
  source = "../../modules/lambda_function"

  function_name = local.lambda_function_names.agent_elevator
  description   = "BuildingOS Agent Elevator - Manages elevator operations and monitoring"
  role_arn      = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_elevator"
  timeout       = local.lambda_performance_configs.agent_elevator.timeout
  memory_size   = local.lambda_performance_configs.agent_elevator.memory_size

  environment_variables = {
    # Elevator API Configuration
    ELEVATOR_API_BASE_URL = "http://elevador.clevertown.io:9090"
    ELEVATOR_API_SECRET   = "ACME_ELEVATOR_SECRET"
    # Agent Task Topics
    COORDINATOR_TASK_TOPIC_ARN  = module.coordinator_task_topic.topic_arn
    AGENT_TASK_RESULT_TOPIC_ARN = module.agent_task_result_topic.topic_arn
    # Monitoring and Logging
    ELEVATOR_MONITORING_TABLE_NAME = module.elevator_monitoring_db.table_name
    LOG_LEVEL                      = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers
  layers = [module.common_utils_layer.layer_arn]

  # VPC Configuration - TEMPORARILY DISABLED FOR TESTING
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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
  role_arn      = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler"
  runtime       = local.lambda_defaults.runtime
  source_dir    = "../../../src/agents/agent_psim"
  timeout       = local.lambda_performance_configs.agent_psim.timeout
  memory_size   = local.lambda_performance_configs.agent_psim.memory_size

  environment_variables = {
    PSIM_API_BASE_URL = "http://psim.clevertown.io:9091"
    PSIM_API_USERNAME = "integration_blubrain"
    PSIM_API_PASSWORD = "Blubrain@4565"
    # Agent Task Topics
    COORDINATOR_TASK_TOPIC_ARN  = module.coordinator_task_topic.topic_arn
    AGENT_TASK_RESULT_TOPIC_ARN = module.agent_task_result_topic.topic_arn
    LOG_LEVEL                   = local.lambda_defaults.log_level
  }

  tracing_mode       = "Active"
  log_retention_days = 14

  # Lambda layers
  layers = [module.common_utils_layer.layer_arn]

  # VPC Configuration - TEMPORARILY DISABLED
  # vpc_config = {
  #   subnet_ids         = aws_subnet.private[*].id
  #   security_group_ids = [aws_security_group.lambda.id]
  # }

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

# --- Lambda Layer ---

module "common_utils_layer" {
  source = "../../modules/lambda_layer"

  layer_name        = local.lambda_layer_names.common_utils
  requirements_file = "../../../src/layers/common_utils/requirements.txt"
  runtime           = local.lambda_defaults.runtime
}
