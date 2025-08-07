# --- Data Sources ---
# These packages our Python code into a .zip file that Lambda can use.
data "archive_file" "agent_health_check_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_health_check" # Path to our Python code
  output_path = "${path.module}/.terraform/agent_health_check.zip"
}

data "archive_file" "agent_persona_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_persona" # Path to our Python code
  output_path = "${path.module}/.terraform/agent_persona.zip"
}

data "archive_file" "agent_director_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_director" # Path to our Python code
  output_path = "${path.module}/.terraform/agent_director.zip"
}

data "archive_file" "agent_elevator_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_elevator" # Path to our Python code
  output_path = "${path.module}/.terraform/agent_elevator.zip"
}

data "archive_file" "agent_psim_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_psim" # Path to our Python code
  output_path = "${path.module}/.terraform/agent_psim.zip"
}

data "archive_file" "agent_coordinator_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_coordinator" # Path to our Python code
  output_path = "${path.module}/.terraform/agent_coordinator.zip"
}

# --- IAM Policies ---
resource "aws_iam_policy" "dynamodb_short_term_memory_policy" {
  name        = "bos-dynamodb-short-term-memory-policy-${var.environment}"
  description = "Allows Lambda to read/write to the short-term memory table."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ],
        Effect   = "Allow",
        Resource = module.short_term_memory_db.table_arn
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_mission_state_policy" {
  name        = "bos-dynamodb-mission-state-policy-${var.environment}"
  description = "Allows Lambda to read/write to the mission state table."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ],
        Effect   = "Allow",
        Resource = module.mission_state_db.table_arn
      }
    ]
  })
}

resource "aws_iam_policy" "sns_publish_policy" {
  name        = "bos-sns-publish-policy-${var.environment}"
  description = "Allows Lambda to publish to SNS topics."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sns:Publish",
        Effect = "Allow",
        Resource = [
          module.intention_topic.topic_arn,
          module.mission_topic.topic_arn,
          module.mission_result_topic.topic_arn,
          module.task_result_topic.topic_arn,
          module.intention_result_topic.topic_arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "bedrock_invoke_policy" {
  name        = "bos-bedrock-invoke-policy-${var.environment}"
  description = "Allows Lambda to invoke Bedrock models."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "bedrock:InvokeModel",
        Effect   = "Allow",
        Resource = "*" # Bedrock does not support resource-level permissions for models
      }
    ]
  })
}



resource "aws_iam_policy" "lambda_invoke_policy" {
  name        = "bos-lambda-invoke-policy-${var.environment}"
  description = "Allows Lambda functions to invoke other Lambda functions."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "lambda:InvokeFunction",
        Effect = "Allow",
        Resource = [
          aws_lambda_function.agent_health_check.arn,
          aws_lambda_function.agent_persona.arn,
          aws_lambda_function.agent_director.arn,
          aws_lambda_function.agent_coordinator.arn,
          aws_lambda_function.agent_elevator.arn,
          aws_lambda_function.agent_psim.arn
        ]
      }
    ]
  })
}

# --- IAM Policy for Elevator Monitoring ---
resource "aws_iam_policy" "elevator_monitoring_policy" {
  name        = "bos-elevator-monitoring-policy-${var.environment}"
  description = "Policy for elevator monitoring operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = module.elevator_monitoring_db.table_arn
      },
      {
        Effect = "Allow"
        Action = [
          "events:PutRule",
          "events:DeleteRule",
          "events:PutTargets",
          "events:RemoveTargets",
          "events:DescribeRule"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:AddPermission",
          "lambda:RemovePermission"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
  }
}

# --- IAM Roles ---
module "lambda_exec_role" {
  source    = "../../modules/iam_role"
  role_name = "bos-lambda-exec-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    aws_iam_policy.dynamodb_short_term_memory_policy.arn,
    aws_iam_policy.dynamodb_mission_state_policy.arn,
    aws_iam_policy.sns_publish_policy.arn,
    aws_iam_policy.bedrock_invoke_policy.arn,
    aws_iam_policy.lambda_invoke_policy.arn,
    aws_iam_policy.elevator_monitoring_policy.arn
  ]
}



# --- Lambda Function Resources ---
# This is the core resource that creates our Lambda function in AWS.
resource "aws_lambda_function" "agent_health_check" {
  function_name = "bos-agent-health-check-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler" # File is app.py, function is handler
  runtime       = "python3.11"

  filename         = data.archive_file.agent_health_check_zip.output_path
  source_code_hash = data.archive_file.agent_health_check_zip.output_base64sha256
  layers           = [module.common_utils_layer.layer_arn]
}

resource "aws_lambda_function" "agent_persona" {
  function_name = "bos-agent-persona-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler"
  runtime       = "python3.11"

  filename         = data.archive_file.agent_persona_zip.output_path
  source_code_hash = data.archive_file.agent_persona_zip.output_base64sha256
  layers           = [module.common_utils_layer.layer_arn]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME      = module.short_term_memory_db.table_name
      SNS_TOPIC_ARN            = module.intention_topic.topic_arn
      MISSION_RESULT_TOPIC_ARN = module.mission_result_topic.topic_arn
    }
  }
}

resource "aws_lambda_function" "agent_director" {
  function_name = "bos-agent-director-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler"
  runtime       = "python3.11"
  timeout       = 30 # Increased timeout for potential LLM latency

  filename         = data.archive_file.agent_director_zip.output_path
  source_code_hash = data.archive_file.agent_director_zip.output_base64sha256
  layers           = [module.common_utils_layer.layer_arn]

  environment {
    variables = {
      MISSION_TOPIC_ARN          = module.mission_topic.topic_arn
      INTENTION_RESULT_TOPIC_ARN = module.intention_result_topic.topic_arn
      MISSION_STATE_TABLE_NAME   = module.mission_state_db.table_name
    }
  }
}

resource "aws_lambda_function" "agent_coordinator" {
  function_name = "bos-agent-coordinator-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler"
  runtime       = "python3.11"
  timeout       = 30
  layers        = [module.common_utils_layer.layer_arn]

  filename         = data.archive_file.agent_coordinator_zip.output_path
  source_code_hash = data.archive_file.agent_coordinator_zip.output_base64sha256

  environment {
    variables = {
      MISSION_STATE_TABLE_NAME = module.mission_state_db.table_name
      TASK_RESULT_TOPIC_ARN    = module.task_result_topic.topic_arn
      MISSION_RESULT_TOPIC_ARN = module.mission_result_topic.topic_arn
      ENVIRONMENT              = var.environment
    }
  }
}

resource "aws_lambda_function" "agent_elevator" {
  function_name = "bos-agent-elevator-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler"
  runtime       = "python3.11"
  layers        = [module.common_utils_layer.layer_arn]
  timeout       = 360 # 6 minutes - enough for 5 minute monitoring + buffer

  filename         = data.archive_file.agent_elevator_zip.output_path
  source_code_hash = data.archive_file.agent_elevator_zip.output_base64sha256

  environment {
    variables = {
      ELEVATOR_API_BASE_URL = "https://anna-minimal-api.neomot.com"
      ELEVATOR_API_SECRET   = "t3hILevRdzfFyd05U2g+XT4lPZCmT6CB+ytaQljWWOk="
      TASK_RESULT_TOPIC_ARN = module.task_result_topic.topic_arn
      MONITORING_TABLE_NAME = module.elevator_monitoring_db.table_name
      LAMBDA_FUNCTION_NAME  = "bos-agent-elevator-${var.environment}"
      ACCOUNT_ID            = data.aws_caller_identity.current.account_id
      REGION_NAME           = data.aws_region.current.id
    }
  }
}

# Allow EventBridge to invoke the elevator Lambda
resource "aws_lambda_permission" "allow_eventbridge_elevator" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_elevator.function_name
  principal     = "events.amazonaws.com"
}

resource "aws_lambda_function" "agent_psim" {
  function_name = "bos-agent-psim-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler"
  runtime       = "python3.11"
  layers        = [module.common_utils_layer.layer_arn]

  filename         = data.archive_file.agent_psim_zip.output_path
  source_code_hash = data.archive_file.agent_psim_zip.output_base64sha256

  environment {
    variables = {
      PSIM_API_BASE_URL     = "http://psim.clevertown.io:9091"
      PSIM_API_USERNAME     = "integration_blubrain"
      PSIM_API_PASSWORD     = "Blubrain@4565"
      TASK_RESULT_TOPIC_ARN = module.task_result_topic.topic_arn
    }
  }
}

# --- Lambda Layers ---
module "common_utils_layer" {
  source = "../../modules/lambda_layer"

  layer_name        = "bos-common-utils-${var.environment}"
  requirements_file = "../../../src/layers/common_utils/requirements.txt"
  runtime           = "python3.11"
}

# --- API Gateway to Expose the Lambda ---
# This creates a public URL that triggers our Lambda function.
resource "aws_apigatewayv2_api" "http_api" {
  name          = "bos-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = false
    allow_headers     = ["*"]
    allow_methods     = ["*"]
    allow_origins     = ["*"]
    expose_headers    = ["*"]
    max_age           = 86400
  }
}

resource "aws_apigatewayv2_integration" "agent_health_check_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_health_check.invoke_arn
}

resource "aws_apigatewayv2_route" "agent_health_check_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health" # The path will be /health
  target    = "integrations/${aws_apigatewayv2_integration.agent_health_check_integration.id}"
}

resource "aws_apigatewayv2_integration" "agent_persona_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_persona.invoke_arn
}

resource "aws_apigatewayv2_route" "agent_persona_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /persona" # The path will be /persona
  target    = "integrations/${aws_apigatewayv2_integration.agent_persona_integration.id}"
}

resource "aws_apigatewayv2_route" "agent_persona_get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /persona/conversations" # The path will be /persona/conversations
  target    = "integrations/${aws_apigatewayv2_integration.agent_persona_integration.id}"
}

resource "aws_apigatewayv2_integration" "agent_director_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_director.invoke_arn
}

resource "aws_apigatewayv2_route" "agent_director_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /director" # The path will be /director
  target    = "integrations/${aws_apigatewayv2_integration.agent_director_integration.id}"
}

# API Gateway Integration for Elevator Agent
resource "aws_apigatewayv2_integration" "agent_elevator_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_elevator.invoke_arn
}

resource "aws_apigatewayv2_route" "agent_elevator_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /elevator/call"
  target    = "integrations/${aws_apigatewayv2_integration.agent_elevator_integration.id}"
}

# API Gateway Integration for PSIM Agent
resource "aws_apigatewayv2_integration" "agent_psim_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_psim.invoke_arn
}

resource "aws_apigatewayv2_route" "agent_psim_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /psim/search"
  target    = "integrations/${aws_apigatewayv2_integration.agent_psim_integration.id}"
}

# API Gateway Integration for Coordinator Agent
resource "aws_apigatewayv2_integration" "agent_coordinator_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_coordinator.invoke_arn
}

resource "aws_apigatewayv2_route" "agent_coordinator_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /coordinator/missions/{mission_id}"
  target    = "integrations/${aws_apigatewayv2_integration.agent_coordinator_integration.id}"
}

resource "aws_apigatewayv2_route" "agent_coordinator_status_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /coordinator/status"
  target    = "integrations/${aws_apigatewayv2_integration.agent_coordinator_integration.id}"
}

# --- Lambda Permission ---
# This allows the API Gateway to invoke our Lambda function.
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_health_check.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_permission_persona" {
  statement_id  = "AllowAPIGatewayInvokePersona"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_persona.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_permission_director" {
  statement_id  = "AllowAPIGatewayInvokeDirector"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_director.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_permission_elevator" {
  statement_id  = "AllowAPIGatewayInvokeElevator"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_elevator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_permission_psim" {
  statement_id  = "AllowAPIGatewayInvokePSIM"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_psim.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_permission_coordinator" {
  statement_id  = "AllowAPIGatewayInvokeCoordinator"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_coordinator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# --- SNS Subscription for Director Agent ---
# This subscribes the Director Agent Lambda to the intention topic.
resource "aws_sns_topic_subscription" "agent_director_subscription" {
  topic_arn = module.intention_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.agent_director.arn
}

# --- SNS Subscription for Mission Result Topic ---
resource "aws_sns_topic_subscription" "agent_director_result_subscription" {
  topic_arn = module.mission_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.agent_director.arn
}

# --- SNS Subscription for Persona Agent Mission Results ---
resource "aws_sns_topic_subscription" "agent_persona_result_subscription" {
  topic_arn = module.mission_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.agent_persona.arn
}

resource "aws_sns_topic_subscription" "agent_persona_intention_result_subscription" {
  topic_arn = module.intention_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.agent_persona.arn
}

# --- SNS Subscription for Coordinator Agent ---
resource "aws_sns_topic_subscription" "agent_coordinator_subscription" {
  topic_arn = module.mission_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.agent_coordinator.arn
}

# --- SNS Subscription for Task Completion ---
resource "aws_sns_topic_subscription" "coordinator_task_result_subscription" {
  topic_arn = module.task_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.agent_coordinator.arn
}

# --- Lambda Permission for SNS ---
# This allows the SNS topic to invoke our Director Agent Lambda function.
resource "aws_lambda_permission" "sns_permission_director" {
  statement_id  = "AllowSNSInvokeDirector"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_director.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.intention_topic.topic_arn
}

resource "aws_lambda_permission" "sns_permission_director_result" {
  statement_id  = "AllowSNSInvokeDirectorResult"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_director.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.mission_result_topic.topic_arn
}

resource "aws_lambda_permission" "sns_permission_persona_result" {
  statement_id  = "AllowSNSInvokePersonaResult"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_persona.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.mission_result_topic.topic_arn
}

resource "aws_lambda_permission" "sns_permission_persona_intention_result" {
  statement_id  = "AllowSNSInvokePersonaIntentionResult"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_persona.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.intention_result_topic.topic_arn
}

resource "aws_lambda_permission" "sns_permission_coordinator" {
  statement_id  = "AllowSNSInvokeCoordinator"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_coordinator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.mission_topic.topic_arn
}

resource "aws_lambda_permission" "sns_permission_coordinator_task_result" {
  statement_id  = "AllowSNSInvokeCoordinatorTaskResult"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_coordinator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.task_result_topic.topic_arn
}



# --- SNS Topic for Intentions ---
module "intention_topic" {
  source = "../../modules/sns_topic"

  name = "bos-intention-topic-${var.environment}"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}

# --- SNS Topic for Missions ---
module "mission_topic" {
  source = "../../modules/sns_topic"

  name = "bos-mission-topic-${var.environment}"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}

# --- SNS Topic for Mission Results ---
module "mission_result_topic" {
  source = "../../modules/sns_topic"

  name = "bos-mission-result-topic-${var.environment}"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}

# --- SNS Topic for Task Results ---
module "task_result_topic" {
  source = "../../modules/sns_topic"

  name = "bos-task-result-topic-${var.environment}"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}

# --- SNS Topic for Intention Results ---
module "intention_result_topic" {
  source = "../../modules/sns_topic"

  name = "bos-intention-result-topic-${var.environment}"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}

# --- API Gateway Stage ---
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# --- S3 Bucket for Static Website Hosting ---
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "bos-frontend-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "StaticWebsiteHosting"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_website_configuration" "frontend_bucket_website" {
  bucket = aws_s3_bucket.frontend_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend_bucket_pab" {
  bucket = aws_s3_bucket.frontend_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend_bucket_policy" {
  bucket = aws_s3_bucket.frontend_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend_bucket.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend_bucket_pab]
}

# Upload chat files to S3
resource "aws_s3_object" "chat_with_notifications" {
  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = "chat-with-notifications.html"
  source       = "../../../frontend/chat-with-notifications.html"
  etag         = filemd5("../../../frontend/chat-with-notifications.html")
  content_type = "text/html"
}

resource "aws_s3_object" "error" {
  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = "error.html"
  source       = "../../../frontend/error.html"
  etag         = filemd5("../../../frontend/error.html")
  content_type = "text/html"
}

resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = "index.html"
  source       = "../../../frontend/index.html"
  etag         = filemd5("../../../frontend/index.html")
  content_type = "text/html"
}

# --- Outputs ---
# This will print the public URL of our API after it's deployed.
output "api_endpoint" {
  description = "The public invoke URL for the API Gateway."
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "website_url" {
  description = "The public URL for the static website."
  value       = "http://${aws_s3_bucket.frontend_bucket.bucket}.s3-website-${data.aws_region.current.id}.amazonaws.com"
}

output "bucket_name" {
  description = "The name of the S3 bucket hosting the website."
  value       = aws_s3_bucket.frontend_bucket.bucket
}

# Data source to get current AWS region
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}



# --- DynamoDB Table for Short-Term Memory ---
module "short_term_memory_db" {
  source = "../../modules/dynamodb_table"

  table_name = "bos-short-term-memory-${var.environment}"
  hash_key   = "SessionId"

  attributes = [
    {
      name = "SessionId"
      type = "S"
    }
  ]

  ttl_attribute = "ExpiresAt"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "ShortTermMemory"
  }
}

# --- DynamoDB Table for Mission State ---
module "mission_state_db" {
  source = "../../modules/dynamodb_table"

  table_name = "bos-mission-state-${var.environment}"
  hash_key   = "mission_id"

  attributes = [
    {
      name = "mission_id"
      type = "S"
    }
  ]

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "MissionState"
  }
}

# --- DynamoDB Table for Elevator Monitoring ---
module "elevator_monitoring_db" {
  source = "../../modules/dynamodb_table"

  table_name = "bos-elevator-monitoring-${var.environment}"
  hash_key   = "mission_id"

  attributes = [
    {
      name = "mission_id"
      type = "S"
    }
  ]

  ttl_attribute = "ttl"

  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "ElevatorMonitoring"
  }
}
