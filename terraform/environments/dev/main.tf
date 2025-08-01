# --- Provider and Backend Configuration ---
terraform {
  required_version = ">= 1.5" # Specifies a minimum Terraform CLI version

  required_providers {
    aws = {
      source = "hashicorp/aws"
      # This locks the provider to the latest major version series (v6).
      # It will allow updates within the 6.x line (e.g., 6.7.0 -> 6.8.0)
      # but will prevent an automatic, potentially breaking update to v7.0.
      # This is the correct, modern application of the best practice.
      version = "~> 6.0"
    }
  }
}

# --- Data Sources ---
# This block packages our Python code into a .zip file that Lambda can use.
data "archive_file" "health_check_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/health_check" # Path to our Python code
  output_path = "${path.module}/.terraform/health_check.zip"
}

# --- IAM Role for Lambda ---
# This defines the permissions our Lambda function will have.
resource "aws_iam_role" "lambda_exec_role" {
  name = "bos-lambda-exec-role-dev"

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
}

# --- Lambda Function Resource ---
# This is the core resource that creates our Lambda function in AWS.
resource "aws_lambda_function" "health_check" {
  function_name = "bos-health-check-dev"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "app.handler" # File is app.py, function is handler
  runtime       = "python3.11"

  filename         = data.archive_file.health_check_zip.output_path
  source_code_hash = data.archive_file.health_check_zip.output_base64sha256
}

# --- API Gateway to Expose the Lambda ---
# This creates a public URL that triggers our Lambda function.
resource "aws_apigatewayv2_api" "http_api" {
  name          = "bos-api-dev"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "health_check_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.health_check.invoke_arn
}

resource "aws_apigatewayv2_route" "health_check_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health" # The path will be /health
  target    = "integrations/${aws_apigatewayv2_integration.health_check_integration.id}"
}

# --- Lambda Permission ---
# This allows the API Gateway to invoke our Lambda function.
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_check.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# --- API Gateway Stage ---
# This creates the default stage and enables automatic deployment.
# THIS WAS THE MISSING PIECE.
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# --- CloudWatch Log Group for Lambda ---
# It's a best practice to create a log group for our Lambda function
# so we can see its output (like our "print" statement).
resource "aws_cloudwatch_log_group" "health_check_logs" {
  name              = "/aws/lambda/${aws_lambda_function.health_check.function_name}"
  retention_in_days = 7 # Keep logs for 7 days
}

# We also need to attach the logging policy to our IAM role.
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# --- Outputs ---
# This will print the public URL of our API after it's deployed.
output "api_endpoint" {
  description = "The public invoke URL for the API Gateway."
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}
