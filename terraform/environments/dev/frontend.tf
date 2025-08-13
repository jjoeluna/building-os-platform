# =============================================================================
# BuildingOS Platform - S3 Frontend Storage Foundation
# =============================================================================
# 
# **Purpose:** Clean S3 static website hosting infrastructure for BuildingOS 
# frontend using global modules and AWS best practices
# 
# **Components:** S3 bucket with CloudFront CDN for optimal performance
# - Static website hosting with index.html and error.html
# - CloudFront distribution for global content delivery and HTTPS
# - CORS configuration for API Gateway integration
# - Public read access for web content delivery
#
# **Architecture:** Uses global s3_website module for consistency
# **Security:** Encryption prepared for KMS integration (Phase 4)
# **Performance:** CloudFront CDN for reduced latency and improved user experience
# **Compliance:** LGPD compliant with public data classification
# 
# **Dependencies:** 
# - Global s3_website module for consistent implementation
# - Frontend files in ../../../frontend/ directory
# - CloudFront for HTTPS and global distribution
#
# **Integration Points:**
# - API Gateway: CORS configured for API calls from frontend
# - WebSocket API: Real-time communication integration
# - Lambda functions: Frontend calls backend services
#
# =============================================================================

# -----------------------------------------------------------------------------
# Frontend Static Website Hosting
# -----------------------------------------------------------------------------
# **Purpose:** Hosts BuildingOS frontend as static website with CloudFront CDN
# **Usage:** Serves HTML, CSS, and JavaScript files to end users
# **Performance:** CloudFront CDN provides global edge locations for fast delivery
# **Security:** Public access for web content with encryption at rest
# **Scalability:** S3 static hosting scales automatically with demand
# -----------------------------------------------------------------------------
module "frontend_website" {
  source = "../../modules/s3_website"

  # S3 bucket configuration for static website hosting
  bucket_name       = "buildingos-frontend"     # Base bucket name (env suffix added by module)
  environment       = var.environment           # Environment suffix for multi-env support
  frontend_path     = "../../../frontend"       # Path to frontend files for upload
  
  # CloudFront CDN configuration for performance and HTTPS
  enable_cloudfront = true                      # Enable CDN for global distribution
  
  # Comprehensive tagging for public frontend resources
  tags = merge(local.common_tags, {
    # Resource identification tags
    Name      = "frontend-website"
    Type      = "S3 Website"
    Component = "Frontend"
    Function  = "Static Website"
    ManagedBy = "Terraform"
    
    # Public data governance and compliance tags
    DataClassification = "public"             # Public web content
    DataType          = "operational"         # Operational web assets
    RetentionPeriod   = "permanent"           # Frontend assets retained permanently
    Compliance        = "lgpd"               # Data protection compliance
    AccessLevel       = "public"             # Public internet access
    DataGovernance    = "enabled"            # Standard governance controls
    Encryption        = "kms"                # Prepared for customer-managed encryption
    AuditLogging      = "enabled"            # Access logging for monitoring
  })

  # Note: KMS encryption will be enabled in Phase 4 for enhanced security
  # kms_key_arn = aws_kms_key.s3_encryption.arn  # Prepared for Phase 4
}
