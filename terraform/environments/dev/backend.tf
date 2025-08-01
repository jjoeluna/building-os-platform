# --- Remote Backend Configuration ---
# This instructs Terraform to store its state file in a remote S3 bucket
# instead of a local file. This is essential for collaboration and CI/CD.
terraform {
  backend "s3" {
    bucket         = "bos-terraform-tfstate" # <-- Your S3 bucket name
    key            = "dev/terraform.tfstate" # Path to the state file within the bucket
    region         = "us-east-1"             # Must match the bucket's region
    dynamodb_table = "terraform-state-lock"  # The DynamoDB table for state locking
    encrypt        = true                    # Encrypt the state file at rest
  }
}
