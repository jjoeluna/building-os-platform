# === BuildingOS Terraform Providers ===
# Centralized provider configuration for all environments

provider "aws" {
  region = "us-east-1" # Default region, can be overridden per environment

  default_tags {
    tags = {
      Project     = "BuildingOS"
      Environment = "dev" # Will be overridden by environment-specific configuration
      Owner       = "DevOps Team"
      CostCenter  = "IT-001"
      ManagedBy   = "Terraform"
    }
  }
}

provider "archive" {
  # Archive provider configuration
}

provider "random" {
  # Random provider configuration
}
