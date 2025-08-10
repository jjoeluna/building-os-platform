# =============================================================================
# Frontend Resources - BuildingOS Platform
# =============================================================================
# This file contains frontend-related resources using global modules
# =============================================================================

# --- Frontend Website ---
module "frontend_website" {
  source = "../../modules/s3_website"

  bucket_name       = "buildingos-frontend"
  environment       = var.environment
  frontend_path     = "../../../frontend"
  enable_cloudfront = true
  # kms_key_arn       = aws_kms_key.s3_encryption.arn  # TEMPORARILY DISABLED
  
  tags = merge(local.common_tags, {
    Name      = "frontend-website"
    Type      = "S3 Website"
    Component = "Frontend"
    Function  = "Static Website"
    ManagedBy = "Terraform"
    # Compliance Tags
    DataClassification = "public"
    DataType          = "operational"
    RetentionPeriod   = "permanent"
    Compliance        = "lgpd"
    AccessLevel       = "public"
    DataGovernance    = "enabled"
    Encryption        = "kms"
    AuditLogging      = "enabled"
  })
}
