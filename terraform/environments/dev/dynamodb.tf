# =============================================================================
# DynamoDB Tables - BuildingOS Platform
# =============================================================================
# This file contains all DynamoDB table definitions using the global dynamodb_table module
# =============================================================================

# --- WebSocket Connections Table ---
# Note: This table is defined directly because it has a simple structure
resource "aws_dynamodb_table" "websocket_connections" {
  name         = local.dynamodb_table_names.websocket_connections
  billing_mode = local.dynamodb_defaults.billing_mode
  hash_key     = "connection_id"

  attribute {
    name = "connection_id"
    type = "S"
  }

  # Encryption configuration
  # server_side_encryption {
  #   enabled     = true
  #   # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # TEMPORARILY DISABLED
  # }

  point_in_time_recovery {
    enabled = local.dynamodb_defaults.point_in_time_recovery
  }

  tags = merge(local.common_tags, {
    Name      = "websocket-connections"
    Type      = "DynamoDB Table"
    Component = "WebSocket"
    Function  = "Connections"
    ManagedBy = "Terraform"
    # Compliance Tags
    DataClassification = "internal"
    DataType           = "operational"
    RetentionPeriod    = "365Days"
    Compliance         = "lgpd"
    AccessLevel        = "internal"
    DataGovernance     = "enabled"
    Encryption         = "kms"
    AuditLogging       = "enabled"
  })
}

# --- Short Term Memory Database ---
module "short_term_memory_db" {
  source = "../../modules/dynamodb_table"

  table_name = local.dynamodb_table_names.short_term_memory
  hash_key   = "user_id"

  attributes = [
    {
      name = "user_id"
      type = "S"
    }
  ]

  # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # TEMPORARILY DISABLED

  tags = merge(local.common_tags, {
    Name      = "short-term-memory"
    Type      = "DynamoDB Table"
    Component = "Memory"
    Function  = "Short Term Storage"
    ManagedBy = "Terraform"
    # Compliance Tags
    DataClassification = "confidential"
    DataType           = "communication"
    RetentionPeriod    = "90Days"
    Compliance         = "lgpd-gdpr"
    AccessLevel        = "restricted"
    DataGovernance     = "enabled"
    Encryption         = "kms"
    AuditLogging       = "enabled"
  })
}

# --- Mission State Database ---
module "mission_state_db" {
  source = "../../modules/dynamodb_table"

  table_name = local.dynamodb_table_names.mission_state
  hash_key   = "mission_id"

  attributes = [
    {
      name = "mission_id"
      type = "S"
    }
  ]

  # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # TEMPORARILY DISABLED

  tags = merge(local.common_tags, {
    Name      = "mission-state"
    Type      = "DynamoDB Table"
    Component = "Mission"
    Function  = "State Management"
    ManagedBy = "Terraform"
    # Compliance Tags
    DataClassification = "internal"
    DataType           = "operational"
    RetentionPeriod    = "365Days"
    Compliance         = "lgpd"
    AccessLevel        = "internal"
    DataGovernance     = "enabled"
    Encryption         = "kms"
    AuditLogging       = "enabled"
  })
}

# --- Elevator Monitoring Database ---
module "elevator_monitoring_db" {
  source = "../../modules/dynamodb_table"

  table_name = local.dynamodb_table_names.elevator_monitoring
  hash_key   = "elevator_id"

  attributes = [
    {
      name = "elevator_id"
      type = "S"
    }
  ]

  # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # TEMPORARILY DISABLED

  tags = merge(local.common_tags, {
    Name      = "elevator-monitoring"
    Type      = "DynamoDB Table"
    Component = "Elevator"
    Function  = "Monitoring"
    ManagedBy = "Terraform"
    # Compliance Tags
    DataClassification = "internal"
    DataType           = "operational"
    RetentionPeriod    = "730Days"
    Compliance         = "lgpd"
    AccessLevel        = "internal"
    DataGovernance     = "enabled"
    Encryption         = "kms"
    AuditLogging       = "enabled"
  })
}
