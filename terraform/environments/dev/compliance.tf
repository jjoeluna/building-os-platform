# =============================================================================
# COMPLIANCE TAGS AND DATA CLASSIFICATION - BuildingOS Platform
# =============================================================================
# This file contains compliance tags, data classification, and retention policies
# for the BuildingOS platform to ensure LGPD compliance and data governance.
# =============================================================================

# -----------------------------------------------------------------------------
# Compliance Tags Configuration
# -----------------------------------------------------------------------------

locals {
  # Compliance Tags for Data Classification
  compliance_tags = {
    # Data Sensitivity Levels
    "DataClassification" = {
      "Public"     = "data-classification=public"      # Public information (building info, amenities)
      "Internal"   = "data-classification=internal"    # Internal business data (configurations, logs)
      "Confidential" = "data-classification=confidential" # Sensitive business data (financial, operational)
      "Restricted" = "data-classification=restricted"  # Highly sensitive data (PII, biometric, financial)
    }
    
    # Data Types
    "DataType" = {
      "PII"        = "data-type=pii"                   # Personally Identifiable Information
      "Biometric"  = "data-type=biometric"             # Biometric data (facial recognition)
      "Financial"  = "data-type=financial"             # Financial information
      "Operational" = "data-type=operational"          # Operational data
      "Log"        = "data-type=log"                   # Access logs and audit trails
      "Communication" = "data-type=communication"      # Chat history and communications
    }
    
    # Retention Periods (in days)
    "RetentionPeriod" = {
      "30Days"     = "retention-period=30"             # 30 days retention
      "90Days"     = "retention-period=90"             # 90 days retention
      "365Days"    = "retention-period=365"            # 1 year retention
      "730Days"    = "retention-period=730"            # 2 years retention
      "2555Days"   = "retention-period=2555"           # 7 years retention (legal requirement)
      "Permanent"  = "retention-period=permanent"      # Permanent retention
    }
    
    # Compliance Requirements
    "Compliance" = {
      "LGPD"       = "compliance=lgpd"                 # Brazilian General Data Protection Law
      "GDPR"       = "compliance=gdpr"                 # General Data Protection Regulation
      "SOC2"       = "compliance=soc2"                 # SOC 2 Type II compliance
      "ISO27001"   = "compliance=iso27001"             # ISO 27001 information security
    }
    
    # Access Control Levels
    "AccessLevel" = {
      "Public"     = "access-level=public"             # Public access
      "Internal"   = "access-level=internal"           # Internal access only
      "Restricted" = "access-level=restricted"         # Restricted access
      "Admin"      = "access-level=admin"              # Admin access only
    }
  }

  # Data Classification Matrix for BuildingOS Resources
  data_classification_matrix = {
    # DynamoDB Tables
    "websocket_connections" = {
      "data_classification" = "internal"
      "data_type"          = "operational"
      "retention_period"   = "365Days"
      "compliance"         = ["lgpd"]
      "access_level"       = "internal"
    }
    
    "short_term_memory" = {
      "data_classification" = "confidential"
      "data_type"          = "communication"
      "retention_period"   = "90Days"
      "compliance"         = ["lgpd", "gdpr"]
      "access_level"       = "restricted"
    }
    
    "mission_state" = {
      "data_classification" = "internal"
      "data_type"          = "operational"
      "retention_period"   = "365Days"
      "compliance"         = ["lgpd"]
      "access_level"       = "internal"
    }
    
    "elevator_monitoring" = {
      "data_classification" = "internal"
      "data_type"          = "operational"
      "retention_period"   = "730Days"
      "compliance"         = ["lgpd"]
      "access_level"       = "internal"
    }
    
    # S3 Buckets
    "frontend_website" = {
      "data_classification" = "public"
      "data_type"          = "operational"
      "retention_period"   = "permanent"
      "compliance"         = ["lgpd"]
      "access_level"       = "public"
    }
    
    "cloudtrail_logs" = {
      "data_classification" = "confidential"
      "data_type"          = "log"
      "retention_period"   = "2555Days"
      "compliance"         = ["lgpd", "soc2", "iso27001"]
      "access_level"       = "admin"
    }
  }
}

# -----------------------------------------------------------------------------
# Compliance Tags for DynamoDB Tables
# -----------------------------------------------------------------------------

# Function to generate compliance tags for a resource
locals {
  # Generate compliance tags for DynamoDB tables
  dynamodb_compliance_tags = {
    for table_name, config in local.data_classification_matrix : table_name => merge(
      local.common_tags,
      {
        "DataClassification" = config.data_classification
        "DataType"          = config.data_type
        "RetentionPeriod"   = config.retention_period
        "Compliance"        = join(",", config.compliance)
        "AccessLevel"       = config.access_level
        "DataGovernance"    = "enabled"
        "Encryption"        = "kms"
        "AuditLogging"      = "enabled"
      }
    ) if can(config)
  }
}

# -----------------------------------------------------------------------------
# Compliance Dashboard and Reporting
# -----------------------------------------------------------------------------

# CloudWatch Dashboard for Compliance Monitoring
resource "aws_cloudwatch_dashboard" "compliance" {
  dashboard_name = "${local.resource_prefix}-compliance-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", local.dynamodb_table_names.websocket_connections],
            ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", "TableName", local.dynamodb_table_names.websocket_connections],
            [".", ".", "TableName", local.dynamodb_table_names.short_term_memory],
            [".", ".", "TableName", local.dynamodb_table_names.mission_state],
            [".", ".", "TableName", local.dynamodb_table_names.elevator_monitoring]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.id
          title  = "DynamoDB Compliance Monitoring"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE 'aws.cloudtrail'\n| fields @timestamp, @message\n| filter @message like /UnauthorizedAccess/\n| stats count() by bin(5m)"
          region  = data.aws_region.current.id
          title   = "Compliance Audit Logs"
          view    = "table"
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Data Lifecycle Policies
# -----------------------------------------------------------------------------

# S3 Lifecycle Policy for CloudTrail Logs
resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    id     = "cloudtrail-lifecycle"
    status = "Enabled"

    filter {
      prefix = ""
    }

    # Transition to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Expire incomplete multipart uploads after 7 days
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }

    # Expire objects after 7 years (legal requirement)
    expiration {
      days = 2555
    }
  }

  depends_on = [aws_s3_bucket_versioning.cloudtrail_logs]
}

# DynamoDB TTL for automatic data cleanup
# Note: TTL is configured in the DynamoDB tables directly
# This is handled in the dynamodb.tf file with the ttl attribute

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "compliance_tags" {
  description = "Compliance tags configuration for the BuildingOS platform"
  value       = local.compliance_tags
}

output "data_classification_matrix" {
  description = "Data classification matrix for BuildingOS resources"
  value       = local.data_classification_matrix
}

output "compliance_dashboard_url" {
  description = "URL for the compliance monitoring dashboard"
  value       = "https://${data.aws_region.current.id}.console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.id}#dashboards:name=${aws_cloudwatch_dashboard.compliance.dashboard_name}"
}
