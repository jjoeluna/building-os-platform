# === Lambda Function Module Outputs ===

output "function_name" {
  description = "The name of the Lambda function."
  value       = aws_lambda_function.this.function_name
}

output "function_arn" {
  description = "The ARN of the Lambda function."
  value       = aws_lambda_function.this.arn
}

output "function_invoke_arn" {
  description = "The invocation ARN of the Lambda function."
  value       = aws_lambda_function.this.invoke_arn
}

output "function_version" {
  description = "The version of the Lambda function."
  value       = aws_lambda_function.this.version
}

output "function_last_modified" {
  description = "The date this resource was last modified."
  value       = aws_lambda_function.this.last_modified
}

output "log_group_name" {
  description = "The name of the CloudWatch log group."
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "log_group_arn" {
  description = "The ARN of the CloudWatch log group."
  value       = aws_cloudwatch_log_group.lambda_logs.arn
}
