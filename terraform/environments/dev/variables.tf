variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[1-9]$", var.aws_region))
    error_message = "AWS region must be a valid region format (e.g., us-east-1, eu-west-1)."
  }
}

variable "environment" {
  description = "The deployment environment name (e.g., dev, stg, prd)."
  type        = string

  validation {
    condition     = contains(["dev", "stg", "prd"], var.environment)
    error_message = "Environment must be one of: dev, stg, prd."
  }
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "BuildingOS"

  validation {
    condition     = length(var.project_name) > 0 && length(var.project_name) <= 50
    error_message = "Project name must be between 1 and 50 characters."
  }
}

variable "owner" {
  description = "The owner/team responsible for this infrastructure."
  type        = string
  default     = "DevOps Team"

  validation {
    condition     = length(var.owner) > 0 && length(var.owner) <= 100
    error_message = "Owner must be between 1 and 100 characters."
  }
}

variable "cost_center" {
  description = "The cost center for billing purposes."
  type        = string
  default     = "IT-001"

  validation {
    condition     = can(regex("^[A-Z]{2}-[0-9]{3}$", var.cost_center))
    error_message = "Cost center must be in format: XX-000 (e.g., IT-001)."
  }
}

variable "alert_email" {
  description = "Email address for receiving CloudWatch alerts (optional)."
  type        = string
  default     = null

  validation {
    condition     = var.alert_email == null || can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alert_email))
    error_message = "Alert email must be a valid email address or null."
  }
}
