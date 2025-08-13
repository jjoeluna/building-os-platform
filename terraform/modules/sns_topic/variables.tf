# =============================================================================
# BuildingOS Platform - SNS Topic Module Variables
# =============================================================================
# 
# **Purpose:** Variable definitions for SNS topic module configuration
# **Scope:** Comprehensive configuration options for SNS topics
# **Usage:** Used by environment configurations to customize topic behavior
# 
# =============================================================================

variable "name" {
  description = "The name of the SNS topic"
  type        = string

  validation {
    condition     = length(var.name) > 0 && length(var.name) <= 256
    error_message = "Topic name must be between 1 and 256 characters."
  }
}

variable "display_name" {
  description = "The display name for the SNS topic (optional)"
  type        = string
  default     = null
}

variable "delivery_policy" {
  description = "The SNS delivery policy for the topic (JSON string)"
  type        = string
  default     = null
}

variable "fifo_topic" {
  description = "Boolean indicating whether or not to create a FIFO (first-in-first-out) topic"
  type        = bool
  default     = false
}

variable "content_based_deduplication" {
  description = "Enables content-based deduplication for FIFO topics"
  type        = bool
  default     = false
}

variable "kms_master_key_id" {
  description = "The ID of an AWS-managed customer master key (CMK) for Amazon SNS or a custom CMK"
  type        = string
  default     = null
}

variable "tags" {
  description = "A map of tags to assign to the resource"
  type        = map(string)
  default     = {}

  validation {
    condition = alltrue([
      for tag_key, tag_value in var.tags :
      length(tag_key) <= 128 && length(tag_value) <= 256
    ])
    error_message = "Tag keys must be <= 128 characters and tag values must be <= 256 characters."
  }
}
