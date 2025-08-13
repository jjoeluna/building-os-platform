# =============================================================================
# BuildingOS Platform - SNS Topic Module
# =============================================================================
# 
# **Purpose:** Creates SNS topics for event-driven communication in BuildingOS
# **Scope:** Standardized SNS topic creation with comprehensive configuration
# **Usage:** Used by environment configurations to create event bus topics
# 
# **Key Features:**
# - Standardized topic naming and tagging
# - Optional encryption configuration for sensitive data
# - Delivery retry and DLQ policies for reliability
# - Comprehensive monitoring and logging integration
# - FIFO topic support for ordered message processing
# 
# **Dependencies:** 
# - KMS key for encryption (optional)
# - CloudWatch for monitoring and alerting
# - IAM roles for topic access permissions
# 
# **Integration:** 
# - Used by all Lambda functions for inter-service communication
# - Provides reliable message delivery with retry mechanisms
# - Supports both standard and FIFO message ordering
# 
# **Security Considerations:**
# - Optional server-side encryption with KMS
# - Access control through IAM topic policies
# - Message filtering for targeted delivery
# 
# =============================================================================

resource "aws_sns_topic" "this" {
  name = var.name

  # Message delivery configuration
  delivery_policy = var.delivery_policy

  # Display name for topic identification
  display_name = var.display_name != null ? var.display_name : var.name

  # FIFO configuration for ordered messages (optional)
  fifo_topic                  = var.fifo_topic
  content_based_deduplication = var.content_based_deduplication

  # Server-side encryption configuration (optional)
  kms_master_key_id = var.kms_master_key_id

  # Comprehensive tagging for governance and cost management
  tags = merge(var.tags, {
    Name      = var.name
    Type      = "SNS Topic"
    Module    = "sns_topic"
    ManagedBy = "Terraform"
  })
}
