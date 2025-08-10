# =============================================================================
# IAM Resources - BuildingOS Platform
# =============================================================================
# This file contains all IAM role and policy definitions
# =============================================================================

# --- Lambda Execution Role ---
resource "aws_iam_role" "lambda_exec_role" {
  name = local.iam_role_names.lambda_exec_role

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name      = "lambda-exec-role"
    Type      = "IAM Role"
    Component = "IAM"
    Function  = "Lambda Execution"
    ManagedBy = "Terraform"
  })
}

# --- Lambda Basic Execution Policy ---
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# --- Lambda VPC Access Policy ---
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# --- X-Ray Tracing Policy ---
resource "aws_iam_role_policy_attachment" "lambda_xray_write_only" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

# --- DynamoDB Access Policy ---
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "${local.iam_role_names.lambda_exec_role}-dynamodb-policy"
  role = aws_iam_role.lambda_exec_role.id

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
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.websocket_connections.arn,
          module.short_term_memory_db.table_arn,
          module.mission_state_db.table_arn,
          module.elevator_monitoring_db.table_arn
        ]
      }
    ]
  })
}

# --- SNS Publish Policy ---
resource "aws_iam_role_policy" "sns_publish" {
  name = "${local.iam_role_names.lambda_exec_role}-sns-policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [
          module.chat_intention_topic.topic_arn,
          module.persona_intention_topic.topic_arn,
          module.director_mission_topic.topic_arn,
          module.coordinator_task_topic.topic_arn,
          module.agent_task_result_topic.topic_arn,
          module.coordinator_mission_result_topic.topic_arn,
          module.director_response_topic.topic_arn,
          module.persona_response_topic.topic_arn
        ]
      }
    ]
  })
}

# --- Lambda Invoke Policy ---
resource "aws_iam_role_policy" "lambda_invoke" {
  name = "${local.iam_role_names.lambda_exec_role}-lambda-invoke-policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          module.agent_health_check.function_arn,
          module.agent_persona.function_arn,
          module.agent_director.function_arn,
          module.agent_coordinator.function_arn,
          module.agent_elevator.function_arn,
          module.agent_psim.function_arn
        ]
      }
    ]
  })
}

# --- Bedrock Access Policy ---
resource "aws_iam_role_policy" "bedrock_access" {
  name = "${local.iam_role_names.lambda_exec_role}-bedrock-policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      }
    ]
  })
}

# --- API Gateway Management Policy ---
resource "aws_iam_role_policy" "apigateway_management" {
  name = "${local.iam_role_names.lambda_exec_role}-apigateway-policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "execute-api:ManageConnections"
        ]
        Resource = "${module.websocket_api.websocket_api_execution_arn}/*"
      }
    ]
  })
}

# --- Additional Lambda Permissions ---

# EventBridge Permission for Elevator
resource "aws_lambda_permission" "allow_eventbridge_elevator" {
  statement_id  = "AllowEventBridgeInvokeElevator"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_elevator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = "arn:aws:events:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:rule/*"
}
