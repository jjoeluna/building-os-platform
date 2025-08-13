# =============================================================================
# IAM Resources - BuildingOS Platform
# =============================================================================
# This file contains all IAM role and policy definitions
# =============================================================================

# -----------------------------------------------------------------------------
# Standalone IAM Policies for Lambda Execution Role
# -----------------------------------------------------------------------------

# --- DynamoDB Access Policy ---
resource "aws_iam_policy" "dynamodb_access" {
  name        = "${local.resource_prefix}-lambda-dynamodb-access"
  description = "Policy for Lambda to access DynamoDB tables"

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
          "dynamodb:Scan",
          "dynamodb:ListTagsOfResource" # Required for validation scripts and compliance checking
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
resource "aws_iam_policy" "sns_publish" {
  name        = "${local.resource_prefix}-lambda-sns-publish"
  description = "Policy for Lambda to publish to SNS topics"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["sns:Publish"]
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

# --- Bedrock Access Policy ---
resource "aws_iam_policy" "bedrock_access" {
  name        = "${local.resource_prefix}-lambda-bedrock-access"
  description = "Policy for Lambda to invoke Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = [
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/amazon.titan-text-express-v1"
        ]
      }
    ]
  })
}

# --- API Gateway Management Policy ---
resource "aws_iam_policy" "apigateway_management" {
  name        = "${local.resource_prefix}-lambda-apigateway-management"
  description = "Policy for Lambda to manage WebSocket connections"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["execute-api:ManageConnections"]
        Resource = "${module.websocket_api.websocket_api_execution_arn}/*"
      }
    ]
  })
}

# --- KMS Access Policy (Phase 4 Preparation) ---
resource "aws_iam_policy" "kms_access" {
  name        = "${local.resource_prefix}-lambda-kms-access"
  description = "Policy for Lambda to access KMS keys for encryption/decryption (Phase 4 preparation)"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:ReEncrypt*"
        ]
        Resource = [
          # Phase 4: Will be updated with specific KMS key ARNs when encryption is enabled
          # For now, this policy is prepared but will be attached when KMS keys are created
          "arn:aws:kms:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:key/*"
        ]
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "dynamodb.${data.aws_region.current.name}.amazonaws.com",
              "s3.${data.aws_region.current.name}.amazonaws.com",
              "sns.${data.aws_region.current.name}.amazonaws.com"
            ]
          }
        }
      }
    ]
  })

  # Add lifecycle management to prevent accidental deletion during Phase 4 implementation
  lifecycle {
    create_before_destroy = true
  }

  tags = merge(local.common_tags, {
    Name        = "kms-access-policy"
    Type        = "IAM Policy"
    Component   = "KMS"
    Function    = "Encryption Access"
    Phase       = "4-Preparation"
    Status      = "Prepared-Not-Attached"
    Description = "KMS policy prepared for Phase 4 encryption implementation"
  })
}

# -----------------------------------------------------------------------------
# Lambda Execution Role Module
# -----------------------------------------------------------------------------
# This module creates the IAM role that all Lambda functions will use.
# It consumes the standalone policies created above.
# Note: KMS policy will be attached in Phase 4 when encryption is enabled
# -----------------------------------------------------------------------------

module "lambda_iam_role" {
  source    = "../../modules/iam_role"
  role_name = local.iam_role_names.lambda_exec_role

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

  policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
  ]

  custom_policy_arns = [
    aws_iam_policy.dynamodb_access.arn,
    aws_iam_policy.sns_publish.arn,
    aws_iam_policy.bedrock_access.arn,
    aws_iam_policy.apigateway_management.arn
    # Note: KMS policy (aws_iam_policy.kms_access.arn) will be added in Phase 4
    # when encryption is enabled. Policy is prepared but not attached yet.
  ]

  tags = merge(local.common_tags, {
    Name      = "lambda-exec-role"
    Type      = "IAM Role Module"
    Component = "IAM"
    Function  = "Lambda Execution"
    ManagedBy = "Terraform"
  })
}

# -----------------------------------------------------------------------------
# Additional Lambda Permissions
# -----------------------------------------------------------------------------
# These permissions are granted at the resource level, which is more specific
# and secure than granting broad invoke permissions at the role level.
# -----------------------------------------------------------------------------

# EventBridge Permission for Elevator Agent
resource "aws_lambda_permission" "allow_eventbridge_elevator" {
  statement_id  = "AllowEventBridgeInvokeElevator"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_elevator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = "arn:aws:events:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:rule/*"
}
