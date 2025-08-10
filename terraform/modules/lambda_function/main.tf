# === Lambda Function Module ===
# Standardized Lambda function creation with observability and security best practices

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.module}/.terraform/${var.function_name}.zip"
}

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  description   = var.description
  role          = var.role_arn
  handler       = var.handler
  runtime       = var.runtime

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  # Performance configuration
  timeout     = var.timeout
  memory_size = var.memory_size

  # Lambda layers
  layers = var.layers

  # VPC configuration (if provided)
  dynamic "vpc_config" {
    for_each = var.vpc_config != null ? [var.vpc_config] : []
    content {
      subnet_ids         = vpc_config.value.subnet_ids
      security_group_ids = vpc_config.value.security_group_ids
    }
  }

  # Environment variables
  dynamic "environment" {
    for_each = length(var.environment_variables) > 0 ? [1] : []
    content {
      variables = var.environment_variables
    }
  }

  # Tracing configuration for observability
  tracing_config {
    mode = var.tracing_mode
  }

  # Tags
  tags = merge(var.tags, {
    Name      = var.function_name
    Type      = "Lambda Function"
    ManagedBy = "Terraform"
  })
}

# CloudWatch Log Group for Lambda logs
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days

  tags = merge(var.tags, {
    Name      = "${var.function_name}-logs"
    Type      = "CloudWatch Log Group"
    ManagedBy = "Terraform"
  })
}

# Lambda permission for API Gateway (if needed)
resource "aws_lambda_permission" "api_gateway" {
  count = var.enable_api_gateway_integration ? 1 : 0

  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_gateway_source_arn}/*/*"
}

# Lambda permission for SNS (if needed)
resource "aws_lambda_permission" "sns" {
  count = var.enable_sns_integration ? 1 : 0

  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}

# SNS subscription (if needed)
resource "aws_sns_topic_subscription" "lambda" {
  count = var.enable_sns_integration ? 1 : 0

  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.this.arn
}
