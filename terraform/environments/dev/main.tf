# =============================================================================
# BuildingOS Platform - Main Configuration (Dev Environment)
# =============================================================================
# This file serves as the entry point for the dev environment.
# 
# IMPORTANT: This file orchestrates the infrastructure by referencing:
# - Global providers: ../../providers.tf
# - Global versions: ../../versions.tf  
# - Global modules: ../../modules/
# - Environment-specific configs: [locals.tf, variables.tf, etc.]
# =============================================================================

# --- Terraform Configuration ---
# Note: Backend configuration is in backend.tf
# Note: Provider configuration is inherited from ../../providers.tf
# Note: Version constraints are inherited from ../../versions.tf

# --- Infrastructure Orchestration ---
# This file serves as the main entry point. All actual infrastructure
# components are defined in their respective specialized .tf files:
#
# - locals.tf: Common values and naming conventions
# - variables.tf: Environment-specific variables
# - data.tf: Data sources (AWS account, region, AZs)
# - lambda_functions.tf: All Lambda functions using global modules
# - api_gateway.tf: HTTP and WebSocket APIs
# - networking.tf: VPC, subnets, security groups
# - dynamodb.tf: Database tables using global modules
# - sns.tf: SNS topics using global modules
# - iam.tf: IAM roles and policies
# - monitoring.tf: CloudWatch, alarms, dashboards
# - security.tf: Security configurations
# - compliance.tf: Tags and compliance
# - performance.tf: Performance optimizations
# - frontend.tf: S3 website hosting using global modules
# - outputs.tf: All infrastructure outputs

# --- Validation ---
# Ensure this configuration is for the correct environment
resource "null_resource" "environment_validation" {
  lifecycle {
    precondition {
      condition     = var.environment == "dev"
      error_message = "This configuration is specifically for the dev environment."
    }
  }
}
