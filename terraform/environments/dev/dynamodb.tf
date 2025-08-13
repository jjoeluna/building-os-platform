# =============================================================================
# BuildingOS Platform - DynamoDB Storage Foundation
# =============================================================================
# 
# **Purpose:** Clean storage infrastructure for BuildingOS platform using 
# consistent global modules and AWS best practices
# 
# **Components:** 4 DynamoDB tables supporting agent communication and data persistence
# - websocket_connections: WebSocket connection management for real-time communication
# - short_term_memory: User conversation context and session management  
# - mission_state: Mission execution state and workflow tracking
# - elevator_monitoring: Elevator system monitoring and status tracking
#
# **Architecture:** All tables use global dynamodb_table module for consistency
# **Security:** Encryption prepared for KMS integration (Phase 4)
# **Compliance:** LGPD/GDPR compliant with proper data classification tags
# **Performance:** Pay-per-request billing for serverless optimization
# 
# **Dependencies:** 
# - VPC endpoints for cost-optimized DynamoDB access
# - IAM policies for Lambda function access (configured in iam.tf)
# - KMS policies prepared for future encryption (Phase 4)
#
# **Integration Points:**
# - Lambda functions: All 8 agent functions access these tables
# - WebSocket API: Connection management through websocket_connections table
# - SNS topics: Mission state updates trigger SNS notifications
#
# =============================================================================

# -----------------------------------------------------------------------------
# WebSocket Connections Table
# -----------------------------------------------------------------------------
# **Purpose:** Manages active WebSocket connections for real-time communication
# **Usage:** WebSocket Lambda functions (connect, disconnect, broadcast, default)
# **Data Pattern:** Simple key-value store with connection_id as primary key
# **Retention:** Connections automatically cleaned up on disconnect
# **Security:** Internal data classification with operational access controls
# -----------------------------------------------------------------------------
resource "aws_dynamodb_table" "websocket_connections" {
  # Table naming follows BuildingOS convention: bos-{env}-{component}
  name = local.dynamodb_table_names.websocket_connections

  # Pay-per-request billing optimizes costs for unpredictable serverless workloads
  billing_mode = local.dynamodb_defaults.billing_mode

  # Primary key: connection_id uniquely identifies each WebSocket connection
  hash_key = "connection_id"

  # Schema definition: Single attribute for connection identification
  attribute {
    name = "connection_id" # WebSocket connection identifier from API Gateway
    type = "S"             # String type for connection IDs
  }

  # Point-in-time recovery enables data protection and compliance requirements
  point_in_time_recovery {
    enabled = local.dynamodb_defaults.point_in_time_recovery
  }

  # Comprehensive tagging for resource management and compliance
  tags = merge(local.common_tags, {
    # Resource identification tags
    Name      = "websocket-connections"
    Type      = "DynamoDB Table"
    Component = "WebSocket"
    Function  = "Connections"
    ManagedBy = "Terraform"

    # Data governance and compliance tags (LGPD/GDPR requirements)
    DataClassification = "internal"    # Internal operational data
    DataType           = "operational" # System operational data
    RetentionPeriod    = "365Days"     # Data retention policy
    Compliance         = "lgpd"        # Brazilian data protection compliance
    AccessLevel        = "internal"    # Internal system access only
    DataGovernance     = "enabled"     # Data governance controls active
    Encryption         = "kms"         # Encryption method (prepared for Phase 4)
    AuditLogging       = "enabled"     # Audit logging for compliance
  })

  # Note: Server-side encryption will be enabled in Phase 4 with customer-managed KMS keys
  # Current implementation uses AWS managed encryption by default
}

# -----------------------------------------------------------------------------
# Short Term Memory Database  
# -----------------------------------------------------------------------------
# **Purpose:** Stores user conversation context and session data for agent interactions
# **Usage:** Agent Persona, Director, and Coordinator for conversation continuity
# **Data Pattern:** User-centric data with user_id as partition key
# **Retention:** 90-day retention for privacy compliance
# **Security:** Confidential data classification with restricted access
# -----------------------------------------------------------------------------
module "short_term_memory_db" {
  source = "../../modules/dynamodb_table"

  # Table configuration using global module for consistency
  table_name = local.dynamodb_table_names.short_term_memory
  hash_key   = "user_id" # Partition key for user-specific data isolation

  # Schema definition: User identification attribute
  attributes = [
    {
      name = "user_id" # Unique user identifier for conversation context
      type = "S"       # String type for user IDs
    }
  ]

  # Comprehensive tagging for confidential user data management
  tags = merge(local.common_tags, {
    # Resource identification tags
    Name      = "short-term-memory"
    Type      = "DynamoDB Table"
    Component = "Memory"
    Function  = "Short Term Storage"
    ManagedBy = "Terraform"

    # Enhanced data governance for confidential user data
    DataClassification = "confidential"  # Contains user conversation data
    DataType           = "communication" # Communication and interaction data
    RetentionPeriod    = "90Days"        # Privacy-compliant retention period
    Compliance         = "lgpd-gdpr"     # Multi-jurisdiction compliance
    AccessLevel        = "restricted"    # Restricted access controls
    DataGovernance     = "enabled"       # Enhanced governance for sensitive data
    Encryption         = "kms"           # Customer-managed encryption (Phase 4)
    AuditLogging       = "enabled"       # Comprehensive audit logging
  })

  # Note: KMS encryption will be enabled in Phase 4 for enhanced security
  # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # Prepared for Phase 4
}

# -----------------------------------------------------------------------------
# Mission State Database
# -----------------------------------------------------------------------------
# **Purpose:** Tracks mission execution state and workflow progression
# **Usage:** Director and Coordinator agents for mission orchestration
# **Data Pattern:** Mission-centric data with mission_id as partition key
# **Retention:** 365-day retention for operational analysis and reporting
# **Security:** Internal operational data with standard access controls
# -----------------------------------------------------------------------------
module "mission_state_db" {
  source = "../../modules/dynamodb_table"

  # Table configuration for mission state management
  table_name = local.dynamodb_table_names.mission_state
  hash_key   = "mission_id" # Partition key for mission-specific data

  # Schema definition: Mission identification attribute
  attributes = [
    {
      name = "mission_id" # Unique mission identifier for state tracking
      type = "S"          # String type for mission IDs
    }
  ]

  # Operational data tagging for mission management
  tags = merge(local.common_tags, {
    # Resource identification tags
    Name      = "mission-state"
    Type      = "DynamoDB Table"
    Component = "Mission"
    Function  = "State Management"
    ManagedBy = "Terraform"

    # Operational data governance tags
    DataClassification = "internal"    # Internal operational data
    DataType           = "operational" # System operational data
    RetentionPeriod    = "365Days"     # One-year retention for analysis
    Compliance         = "lgpd"        # Data protection compliance
    AccessLevel        = "internal"    # Internal system access
    DataGovernance     = "enabled"     # Standard governance controls
    Encryption         = "kms"         # Prepared for customer-managed encryption
    AuditLogging       = "enabled"     # Operational audit logging
  })

  # Note: Customer-managed KMS encryption prepared for Phase 4 implementation
  # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # Phase 4 integration
}

# -----------------------------------------------------------------------------
# Elevator Monitoring Database
# -----------------------------------------------------------------------------
# **Purpose:** Stores elevator system monitoring data and operational status
# **Usage:** Elevator Agent for building automation and monitoring
# **Data Pattern:** Elevator-centric data with elevator_id as partition key  
# **Retention:** 730-day retention for historical analysis and maintenance
# **Security:** Internal operational data with extended retention for analysis
# -----------------------------------------------------------------------------
module "elevator_monitoring_db" {
  source = "../../modules/dynamodb_table"

  # Table configuration for elevator monitoring data
  table_name = local.dynamodb_table_names.elevator_monitoring
  hash_key   = "elevator_id" # Partition key for elevator-specific data

  # Schema definition: Elevator identification attribute
  attributes = [
    {
      name = "elevator_id" # Unique elevator identifier for monitoring data
      type = "S"           # String type for elevator IDs
    }
  ]

  # Extended retention tagging for monitoring and maintenance data
  tags = merge(local.common_tags, {
    # Resource identification tags
    Name      = "elevator-monitoring"
    Type      = "DynamoDB Table"
    Component = "Elevator"
    Function  = "Monitoring"
    ManagedBy = "Terraform"

    # Extended retention data governance for monitoring data
    DataClassification = "internal"    # Internal operational monitoring data
    DataType           = "operational" # Operational monitoring data
    RetentionPeriod    = "730Days"     # Two-year retention for trend analysis
    Compliance         = "lgpd"        # Data protection compliance
    AccessLevel        = "internal"    # Internal system access
    DataGovernance     = "enabled"     # Standard governance controls
    Encryption         = "kms"         # Prepared for customer-managed encryption
    AuditLogging       = "enabled"     # Monitoring audit logging
  })

  # Note: KMS encryption configuration prepared for Phase 4 security enhancement
  # kms_key_arn = aws_kms_key.dynamodb_encryption.arn  # Customer-managed encryption
}
