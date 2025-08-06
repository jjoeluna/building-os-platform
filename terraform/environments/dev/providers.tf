terraform {
  required_version = ">= 1.5" # Specifies a minimum Terraform CLI version

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
