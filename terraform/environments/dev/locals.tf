# === BuildingOS Terraform Locals ===
# Centralized values and common tags for the BuildingOS infrastructure

locals {
  # Common tags for all resources
  common_tags = {
    Project     = "BuildingOS"
    Environment = var.environment
    Owner       = "DevOps Team"
    CostCenter  = "IT-001"
    ManagedBy   = "Terraform"
    Purpose     = "Building Automation Platform"
    Version     = "1.0.0"
  }

  # Resource naming prefix
  resource_prefix = "bos-${var.environment}"

  # AWS region (using data source instead of hardcoded)
  aws_region = data.aws_region.current.id

  # Account information
  aws_account_id = data.aws_caller_identity.current.account_id

  # Lambda configuration defaults
  lambda_defaults = {
    runtime     = "python3.11"
    timeout     = 30
    memory_size = 256
    log_level   = "INFO"
  }

  # API Gateway configuration
  api_gateway_defaults = {
    protocol_type = "HTTP"
    cors_configuration = {
      allow_origins = ["*"]
      allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
      allow_headers = ["Content-Type", "Authorization", "X-Requested-With"]
    }
  }

  # DynamoDB configuration defaults
  dynamodb_defaults = {
    billing_mode           = "PAY_PER_REQUEST"
    point_in_time_recovery = true
  }

  # SNS topic naming convention
  sns_topic_names = {
    chat_intention             = "${local.resource_prefix}-chat-intention-topic"
    persona_intention          = "${local.resource_prefix}-persona-intention-topic"
    director_mission           = "${local.resource_prefix}-director-mission-topic"
    coordinator_task           = "${local.resource_prefix}-coordinator-task-topic"
    agent_task_result          = "${local.resource_prefix}-agent-task-result-topic"
    coordinator_mission_result = "${local.resource_prefix}-coordinator-mission-result-topic"
    director_response          = "${local.resource_prefix}-director-response-topic"
    persona_response           = "${local.resource_prefix}-persona-response-topic"
  }

  # Lambda function names
  lambda_function_names = {
    agent_persona        = "${local.resource_prefix}-agent-persona"
    agent_director       = "${local.resource_prefix}-agent-director"
    agent_coordinator    = "${local.resource_prefix}-agent-coordinator"
    agent_elevator       = "${local.resource_prefix}-agent-elevator"
    agent_psim           = "${local.resource_prefix}-agent-psim"
    agent_health_check   = "${local.resource_prefix}-agent-health-check"
    websocket_connect    = "${local.resource_prefix}-websocket-connect"
    websocket_disconnect = "${local.resource_prefix}-websocket-disconnect"
    websocket_default    = "${local.resource_prefix}-websocket-default"
    websocket_broadcast  = "${local.resource_prefix}-websocket-broadcast"
  }

  # DynamoDB table names
  dynamodb_table_names = {
    short_term_memory     = "${local.resource_prefix}-short-term-memory"
    mission_state         = "${local.resource_prefix}-mission-state"
    elevator_monitoring   = "${local.resource_prefix}-elevator-monitoring"
    websocket_connections = "${local.resource_prefix}-websocket-connections"
  }

  # API Gateway names
  api_gateway_names = {
    http_api      = "${local.resource_prefix}-http-api"
    websocket_api = "${local.resource_prefix}-websocket-api"
  }

  # S3 bucket names
  s3_bucket_names = {
    frontend_website = "${local.resource_prefix}-frontend-website"
    terraform_state  = "bos-terraform-tfstate"
  }

  # IAM role names
  iam_role_names = {
    lambda_exec_role = "${local.resource_prefix}-lambda-exec-role"
  }

  # Lambda layer names
  lambda_layer_names = {
    common_utils = "${local.resource_prefix}-common-utils-layer"
  }
}
