# =============================================================================
# Data Sources - BuildingOS Platform
# =============================================================================
# This file contains all data source definitions for the BuildingOS platform
# =============================================================================

# --- AWS Account and Region Information ---
data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

# --- Availability Zones ---
data "aws_availability_zones" "available" {
  state = "available"

  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}
