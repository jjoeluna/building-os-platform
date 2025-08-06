variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "The deployment environment name (e.g., dev, stg, prd)."
  type        = string
}
