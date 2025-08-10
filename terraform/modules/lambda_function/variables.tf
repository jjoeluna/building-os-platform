# === Lambda Function Module Variables ===

variable "function_name" {
  description = "The name of the Lambda function."
  type        = string
}

variable "description" {
  description = "Description of the Lambda function."
  type        = string
  default     = ""
}

variable "role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  type        = string
}

variable "handler" {
  description = "The function entrypoint in your code."
  type        = string
  default     = "app.handler"
}

variable "runtime" {
  description = "The runtime environment for the Lambda function."
  type        = string
  default     = "python3.11"
}

variable "source_dir" {
  description = "The directory containing the Lambda function source code."
  type        = string
}

variable "timeout" {
  description = "The amount of time your Lambda function has to execute in seconds."
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Amount of memory in MB your Lambda function can use at runtime."
  type        = number
  default     = 256
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function."
  type        = map(string)
  default     = {}
}

variable "tracing_mode" {
  description = "Tracing mode for the Lambda function (Active, PassThrough)."
  type        = string
  default     = "Active"
  validation {
    condition     = contains(["Active", "PassThrough"], var.tracing_mode)
    error_message = "Tracing mode must be either 'Active' or 'PassThrough'."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs."
  type        = number
  default     = 14
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention days must be one of the allowed values: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653."
  }
}

variable "enable_api_gateway_integration" {
  description = "Whether to enable API Gateway integration for this Lambda function."
  type        = bool
  default     = false
}

variable "api_gateway_source_arn" {
  description = "The source ARN for API Gateway integration."
  type        = string
  default     = ""
}

variable "enable_sns_integration" {
  description = "Whether to enable SNS integration for this Lambda function."
  type        = bool
  default     = false
}

variable "sns_topic_arn" {
  description = "The ARN of the SNS topic for integration."
  type        = string
  default     = ""
}

# VPC Configuration
variable "vpc_config" {
  description = "VPC configuration for the Lambda function."
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}

variable "layers" {
  description = "List of Lambda Layer ARNs to attach to the function."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}
