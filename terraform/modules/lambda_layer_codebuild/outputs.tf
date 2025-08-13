# =============================================================================
# Lambda Layer CodeBuild Module - Outputs
# =============================================================================

output "layer_arn" {
  description = "ARN of the Lambda layer"
  value       = aws_lambda_layer_version.this.arn
}

output "layer_version" {
  description = "Version of the Lambda layer"
  value       = aws_lambda_layer_version.this.version
}

output "codebuild_project_name" {
  description = "Name of the CodeBuild project"
  value       = aws_codebuild_project.lambda_layer_builder.name
}

output "codebuild_project_arn" {
  description = "ARN of the CodeBuild project"
  value       = aws_codebuild_project.lambda_layer_builder.arn
}
