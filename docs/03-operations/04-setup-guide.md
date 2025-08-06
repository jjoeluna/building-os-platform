[⬅️ Back to Index](../README.md)

# 🚀 BuildingOS - Development System Setup Guide

**Objective:** This guide details the complete process for setting up a local development environment and the foundational cloud infrastructure for the BuildingOS project, starting from absolute zero.

---

## Part 1: Cloud Foundation (AWS)

This section covers the one-time setup of the AWS resources required to support our development system.

### 1.1. Install and Configure the AWS CLI

1.  **Install the AWS CLI:** Download and install the AWS Command Line Interface from the official AWS website for your operating system.
2.  **Generate an IAM User Access Key:**
3.  **Configure the CLI:** Open your terminal (PowerShell) and run `aws configure`. Enter the credentials you just saved, your preferred default region (e.g., `us-east-1`), and default output format (e.g., `json`).

### 1.2. Create the Terraform Backend Resources

The following PowerShell script creates a secure S3 bucket to store the Terraform state and a DynamoDB table for state locking.

```powershell
# 1. Set variables
$S3_BUCKET_NAME="bos-terraform-tfstate" # Use a globally unique name
$AWS_REGION="us-east-1"                 # Your chosen AWS region

# 2. Create S3 Bucket (handles the us-east-1 exception)
if ($AWS_REGION -eq "us-east-1") {
    aws s3api create-bucket --bucket $S3_BUCKET_NAME --region $AWS_REGION
} else {
    aws s3api create-bucket --bucket $S3_BUCKET_NAME --region $AWS_REGION --create-bucket-configuration LocationConstraint=$AWS_REGION
}

# 3. Enable Versioning on the Bucket
aws s3api put-bucket-versioning --bucket $S3_BUCKET_NAME --versioning-configuration Status=Enabled

# 4. Create DynamoDB Table
aws dynamodb create-table `
    --table-name terraform-state-lock `
    --attribute-definitions AttributeName=LockID,AttributeType=S `
    --key-schema AttributeName=LockID,KeyType=HASH `
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 `
    --region $AWS_REGION
```

## Part 2: Local Development Environment Setup

This section covers the setup of your local machine.

### 2.1. Project Scaffolding

1.  **Create GitHub Repository:** Create a new, private GitHub repository named building-os-platform. **Do not** initialize it with a README or .gitignore file.
2.  **Clone Repository:** Clone the empty repository to your local machine:
3.  **Create .gitignore:** Before anything else, create a .gitignore file in the project root with the following content to prevent committing sensitive files and large binaries:Generated code
4.  **Create Folder & File Structure:** Run the provided PowerShell script (create_structure.ps1) to generate the entire project directory and file skeleton.
5.  **Initial Commit:** Add all the generated files and push them to the main branch on GitHub.

### 2.2. VSCode and Python Setup

1.  **Open Project:** Open the building-os-platform folder in VSCode.
2.  **Install Recommended Extensions:** VSCode should prompt you to install the extensions recommended in .vscode/extensions.json. Approve this.
3.  **Create and Activate Virtual Environment:**
4.  **Select Python Interpreter:**
5.  **Install Dependencies:** Install initial tools into your virtual environment:

---

## Part 3: CI/CD and AWS Integration

This section covers the secure connection between GitHub Actions and AWS.

### 3.1. Configure IAM OIDC Trust

The following PowerShell script creates the IAM OIDC Provider and the IAM Role that GitHub Actions will assume to deploy resources.

Generated powershell

`# 1. Set variables
$GITHUB_ORG="your-github-username"
$REPO_NAME="building-os-platform"
$IAM_ROLE_NAME="GitHubAction-AssumeRole-BuildingOS"
$AWS_REGION="us-east-1"
$ACCOUNT_ID=(aws sts get-caller-identity --query "Account" --output text).Trim()

# 2. Create the OIDC Provider
aws iam create-open-id-connect-provider `
    --url https://token.actions.githubusercontent.com `
    --client-id-list sts.amazonaws.com `
    --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"

# 3. Define and Create the IAM Role
$trustPolicyJson = @"
{
    "Version": "2012-10-17",
    "Statement": [ {
            "Effect": "Allow",
            "Principal": { "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com" },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
                "StringLike": { "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${REPO_NAME}:*" }
            }
    } ]
}
"@
Set-Content -Path ".\trust-policy.json" -Value $trustPolicyJson
aws iam create-role --role-name $IAM_ROLE_NAME --assume-role-policy-document file://trust-policy.json
Remove-Item -Path ".\trust-policy.json"

# 4. Attach Permissions
aws iam attach-role-policy --role-name $IAM_ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AdministratorAccess"`

### 3.2. Update the GitHub Actions Workflow

1.  After running the script above, get the full ARN of the created role.
2.  Open .github/workflows/ci_and_deploy_to_dev.yml.
3.  Replace the placeholder role-to-assume values in both the validate and deploy-to-dev jobs with the full ARN of your GitHubAction-AssumeRole-BuildingOS role.

---

This guide provides the complete blueprint for bootstrapping the BuildingOS development system.
