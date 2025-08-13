# =============================================================================
# Lambda Layer CodeBuild Module - Variables
# =============================================================================

variable "environment" {
  description = "Environment name (dev, stg, prd)"
  type        = string
}

variable "layer_name" {
  description = "Name of the Lambda layer"
  type        = string
}

variable "requirements_file" {
  description = "Path to requirements.txt file"
  type        = string
}

variable "source_dir" {
  description = "Path to source directory containing Python files"
  type        = string
}

variable "source_archive" {
  description = "Path to source archive for upload"
  type        = string
}

variable "source_bucket" {
  description = "S3 bucket name for source storage"
  type        = string
}

variable "source_key" {
  description = "S3 key for source archive"
  type        = string
}

variable "source_bucket_arn" {
  description = "S3 source bucket ARN"
  type        = string
}

variable "artifacts_bucket" {
  description = "S3 bucket name for build artifacts"
  type        = string
}

variable "artifacts_bucket_arn" {
  description = "S3 artifacts bucket ARN"
  type        = string
}
