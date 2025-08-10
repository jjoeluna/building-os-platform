variable "bucket_name" {
  description = "Name of the S3 bucket (without environment suffix)"
  type        = string
  default     = "buildingos-frontend"
}

variable "environment" {
  description = "Environment name (dev, stg, prd)"
  type        = string
}

variable "frontend_path" {
  description = "Path to the frontend files"
  type        = string
}

variable "enable_cloudfront" {
  description = "Whether to enable CloudFront distribution"
  type        = bool
  default     = true
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key to use for encryption"
  type        = string
  default     = null
}

variable "tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
  default     = {}
}
