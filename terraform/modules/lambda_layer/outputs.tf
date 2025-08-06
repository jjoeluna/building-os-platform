output "layer_arn" {
  description = "The ARN of the Lambda Layer Version."
  value       = aws_lambda_layer_version.this.arn
}
