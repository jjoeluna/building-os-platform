# =============================================================================
# BuildingOS Platform - SNS Topic Module Outputs
# =============================================================================
# 
# **Purpose:** Output values for SNS topic module integration
# **Scope:** Comprehensive topic information for downstream resources
# **Usage:** Used by environment configurations to reference topic details
# 
# =============================================================================

output "topic_arn" {
  description = "The ARN of the SNS topic"
  value       = aws_sns_topic.this.arn
}

output "topic_name" {
  description = "The name of the SNS topic"
  value       = aws_sns_topic.this.name
}

output "topic_id" {
  description = "The unique identifier of the SNS topic"
  value       = aws_sns_topic.this.id
}

output "topic_display_name" {
  description = "The display name of the SNS topic"
  value       = aws_sns_topic.this.display_name
}

output "topic_owner" {
  description = "The AWS account owner of the SNS topic"
  value       = aws_sns_topic.this.owner
}

output "topic_policy" {
  description = "The fully-formed AWS policy as JSON"
  value       = aws_sns_topic.this.policy
}

output "topic_tags" {
  description = "A map of tags assigned to the SNS topic"
  value       = aws_sns_topic.this.tags_all
}
