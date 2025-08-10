# =============================================================================
# Security & Encryption - BuildingOS Platform
# =============================================================================
# This file contains all security-related configurations including encryption,
# KMS keys, and security policies for the BuildingOS platform.
# =============================================================================

# --- KMS Key for DynamoDB Encryption - TEMPORARILY DISABLED ---
# resource "aws_kms_key" "dynamodb_encryption" {
#   description             = "KMS key for DynamoDB table encryption - ${local.resource_prefix}"
#   deletion_window_in_days = 7
#   enable_key_rotation     = true

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid    = "Enable IAM User Permissions"
#         Effect = "Allow"
#         Principal = {
#           AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
#         }
#         Action   = "kms:*"
#         Resource = "*"
#       },
#       {
#         Sid    = "Allow DynamoDB to use the key"
#         Effect = "Allow"
#         Principal = {
#           Service = "dynamodb.amazonaws.com"
#         }
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = "*"
#       },
#       {
#         Sid    = "Allow Lambda to use the key"
#         Effect = "Allow"
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = "*"
#       }
#     ]
#   })

#   tags = merge(local.common_tags, {
#     Name      = "dynamodb-encryption-key"
#     Type      = "KMS Key"
#     Component = "Security"
#     Function  = "DynamoDB Encryption"
#     ManagedBy = "Terraform"
#   })
# }

# --- KMS Key Alias - TEMPORARILY DISABLED ---
# resource "aws_kms_alias" "dynamodb_encryption" {
#   name          = "alias/${local.resource_prefix}-dynamodb-encryption"
#   target_key_id = aws_kms_key.dynamodb_encryption.key_id
# }

# --- KMS Key for S3 Encryption - TEMPORARILY DISABLED ---
# resource "aws_kms_key" "s3_encryption" {
#   description             = "KMS key for S3 bucket encryption - ${local.resource_prefix}"
#   deletion_window_in_days = 7
#   enable_key_rotation     = true

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid    = "Enable IAM User Permissions"
#         Effect = "Allow"
#         Principal = {
#           AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
#         }
#         Action   = "kms:*"
#         Resource = "*"
#       },
#       {
#         Sid    = "Allow S3 to use the key"
#         Effect = "Allow"
#         Principal = {
#           Service = "s3.amazonaws.com"
#         }
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = "*"
#       },
#       {
#         Sid    = "Allow Lambda to use the key"
#         Effect = "Allow"
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = "*"
#       }
#     ]
#   })

#   tags = merge(local.common_tags, {
#     Name      = "s3-encryption-key"
#     Type      = "KMS Key"
#     Component = "Security"
#     Function  = "S3 Encryption"
#     ManagedBy = "Terraform"
#   })
# }

# --- KMS Key Alias for S3 - TEMPORARILY DISABLED ---
# resource "aws_kms_alias" "s3_encryption" {
#   name          = "alias/${local.resource_prefix}-s3-encryption"
#   target_key_id = aws_kms_key.s3_encryption.key_id
# }

# --- KMS Key for Secrets Management - TEMPORARILY DISABLED ---
# resource "aws_kms_key" "secrets_encryption" {
#   description             = "KMS key for secrets management - ${local.resource_prefix}"
#   deletion_window_in_days = 7
#   enable_key_rotation     = true

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid    = "Enable IAM User Permissions"
#         Effect = "Allow"
#         Principal = {
#           AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
#         }
#         Action   = "kms:*"
#         Resource = "*"
#       },
#       {
#         Sid    = "Allow Secrets Manager to use the key"
#         Effect = "Allow"
#         Principal = {
#           Service = "secretsmanager.amazonaws.com"
#         }
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = "*"
#       },
#       {
#         Sid    = "Allow Lambda to use the key"
#         Effect = "Allow"
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = "*"
#       }
#     ]
#   })

#   tags = merge(local.common_tags, {
#     Name      = "secrets-encryption-key"
#     Type      = "KMS Key"
#     Component = "Security"
#     Function  = "Secrets Management"
#     ManagedBy = "Terraform"
#   })
# }

# --- KMS Key Alias for Secrets - TEMPORARILY DISABLED ---
# resource "aws_kms_alias" "secrets_encryption" {
#   name          = "alias/${local.resource_prefix}-secrets-encryption"
#   target_key_id = aws_kms_key.secrets_encryption.key_id
# }

# --- IAM Policy for KMS Access - TEMPORARILY DISABLED ---
# resource "aws_iam_role_policy" "kms_access" {
#   name = "${local.resource_prefix}-lambda-kms-policy"
#   role = aws_iam_role.lambda_exec_role.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey",
#           "kms:Encrypt",
#           "kms:ReEncrypt*",
#           "kms:GenerateDataKey*"
#         ]
#         Resource = [
#           aws_kms_key.dynamodb_encryption.arn,
#           aws_kms_key.s3_encryption.arn,
#           aws_kms_key.secrets_encryption.arn
#         ]
#       }
#     ]
#   })
# }

# --- CloudTrail for Audit Logging ---
resource "aws_cloudtrail" "main" {
  name                          = "${local.resource_prefix}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true
    data_resource {
      type = "AWS::DynamoDB::Table"
      values = [
        "arn:aws:dynamodb:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:table/${local.dynamodb_table_names.websocket_connections}",
        "arn:aws:dynamodb:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:table/${local.dynamodb_table_names.short_term_memory}",
        "arn:aws:dynamodb:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:table/${local.dynamodb_table_names.mission_state}",
        "arn:aws:dynamodb:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:table/${local.dynamodb_table_names.elevator_monitoring}"
      ]
    }
  }

  tags = merge(local.common_tags, {
    Name      = "cloudtrail"
    Type      = "CloudTrail"
    Component = "Security"
    Function  = "Audit Logging"
    ManagedBy = "Terraform"
  })
}

# --- S3 Bucket for CloudTrail Logs ---
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "${local.resource_prefix}-cloudtrail-logs-${random_string.bucket_suffix.result}"

  tags = merge(local.common_tags, {
    Name      = "cloudtrail-logs"
    Type      = "S3 Bucket"
    Component = "Security"
    Function  = "Audit Logs"
    ManagedBy = "Terraform"
    # Compliance Tags
    DataClassification = "confidential"
    DataType           = "log"
    RetentionPeriod    = "2555Days"
    Compliance         = "lgpd-soc2-iso27001"
    AccessLevel        = "admin"
    DataGovernance     = "enabled"
    Encryption         = "kms"
    AuditLogging       = "enabled"
  })
}

# --- S3 Bucket Versioning for CloudTrail ---
resource "aws_s3_bucket_versioning" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# --- S3 Bucket Encryption for CloudTrail - TEMPORARILY DISABLED ---
# resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_logs" {
#   bucket = aws_s3_bucket.cloudtrail_logs.id
#
#   rule {
#     apply_server_side_encryption_by_default {
#       kms_master_key_id = aws_kms_key.s3_encryption.arn
#       sse_algorithm     = "aws:kms"
#     }
#   }
# }

# --- S3 Bucket Policy for CloudTrail ---
resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# --- Random String for Bucket Names ---
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
