[📖 Docs](../README.md) > [🛠️ Development](./README.md) > **Setup Guide**

---

# Development Environment Setup Guide

## 📋 Overview

This guide details the complete process for setting up a local development environment and the foundational cloud infrastructure for the BuildingOS project, starting from absolute zero.

---

## 🌍 **Part 1: Cloud Foundation (AWS)**

This section covers the one-time setup of the AWS resources required to support our development system.

### **1.1. Install and Configure the AWS CLI**

1. **Install the AWS CLI:** Download and install the AWS Command Line Interface from the official AWS website for your operating system.
2. **Generate an IAM User Access Key:**
3. **Configure the CLI:** Open your terminal (PowerShell) and run `aws configure`. Enter the credentials you just saved, your preferred default region (e.g., `us-east-1`), and default output format (e.g., `json`).

### **1.2. Create the Terraform Backend Resources**

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

---

## 💻 **Part 2: Local Development Environment Setup**

This section covers the setup of your local machine.

### **2.1. Project Scaffolding**

1. **Create GitHub Repository:** Create a new, private GitHub repository named building-os-platform. **Do not** initialize it with a README or .gitignore file.
2. **Clone Repository:** Clone the empty repository to your local machine:
3. **Create .gitignore:** Before anything else, create a .gitignore file in the project root with the following content to prevent committing sensitive files and large binaries
4. **Create Folder & File Structure:** Run the provided PowerShell script (create_structure.ps1) to generate the entire project directory and file skeleton.
5. **Initial Commit:** Add all the generated files and push them to the main branch on GitHub.

### **2.2. VSCode and Python Setup**

1. **Open Project:** Open the building-os-platform folder in VSCode.
2. **Install Recommended Extensions:** VSCode should prompt you to install the extensions recommended in .vscode/extensions.json. Approve this.
3. **Create and Activate Virtual Environment:**
4. **Select Python Interpreter:**
5. **Install Dependencies:** Install initial tools into your virtual environment:

---

## 🚀 **Part 3: CI/CD and AWS Integration**

This section covers the secure connection between GitHub Actions and AWS.

### **3.1. Configure IAM OIDC Trust**

The following PowerShell script creates the IAM OIDC Provider and the IAM Role that GitHub Actions will assume to deploy resources.

```powershell
# 1. Set variables
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
aws iam attach-role-policy --role-name $IAM_ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AdministratorAccess"
```

### **3.2. Update the GitHub Actions Workflow**

1. After running the script above, get the full ARN of the created role.
2. Open .github/workflows/ci_and_deploy_to_dev.yml.
3. Replace the placeholder role-to-assume values in both the validate and deploy-to-dev jobs with the full ARN of your GitHubAction-AssumeRole-BuildingOS role.

---

## 🏗️ **Part 4: Environment Management**

### **4.1. Environment Structure**

The BuildingOS platform supports multiple environments:

- **dev**: Development environment for active development
- **stg**: Staging environment for testing before production
- **prd**: Production environment for live operations

### **4.2. Environment Variables**

Set the environment variable before running any Terraform commands:

```powershell
# Set for current session
$env:TF_VAR_environment = "dev"

# Set permanently for user (recommended)
[Environment]::SetEnvironmentVariable("TF_VAR_environment", "dev", "User")

# Or create terraform.tfvars file in terraform/environments/{env}/
echo 'environment = "dev"' > terraform.tfvars
```

### **4.3. Resource Naming Standards**

All resources follow this naming pattern:
- **Lambda Functions**: `bos-agent-{name}-{environment}`
- **SNS Topics**: `bos-{topic-name}-topic-{environment}`
- **DynamoDB Tables**: `bos-{table-name}-{environment}`
- **IAM Roles**: `bos-{role-name}-{environment}`

---

## 🔧 **Part 5: Development Workflow**

### **5.1. Daily Development Workflow**

1. **Update Documentation First:**
   - Check `docs/03-development/01-project-management.md` for current priorities
   - Update `docs/02-architecture/02-api-contract.md` before implementing endpoints

2. **Environment Setup:**
   ```powershell
   cd terraform/environments/dev
   $env:TF_VAR_environment = "dev"
   terraform plan
   ```

3. **Code Development:**
   ```powershell
   # Activate virtual environment
   venv\Scripts\Activate.ps1
   
   # Run tests
   python -m pytest tests/ -v
   
   # Build and deploy
   terraform apply
   ```

4. **Testing:**
   - Use commands from `docs/03-development/02-cli-commands-reference.md`
   - Test endpoints after deployment
   - Update development status with results

### **5.2. AI Assistant Context**

For consistent AI assistance, use the appropriate context prompt:

- **Development Tasks**: Copy from `docs/03-development/03-developer-context-prompt.md`
- **Architecture Tasks**: Copy from `docs/03-development/04-architect-context-prompt.md`

### **5.3. Rollback & Disaster Recovery**

#### **Infrastructure Rollback**
```powershell
# Rollback to previous Terraform state
cd terraform/environments/dev
terraform plan -out=rollback.tfplan
terraform apply rollback.tfplan

# Or rollback to specific version
terraform apply -var="version=1.2.3"
```

#### **Database Recovery**
```powershell
# Restore DynamoDB from backup
aws dynamodb restore-table-from-backup \
  --target-table-name bos-data-dev \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/bos-data-dev/backup/1234567890

# Point-in-time recovery
aws dynamodb restore-table-to-point-in-time \
  --target-table-name bos-data-dev-restored \
  --source-table-name bos-data-dev \
  --restore-date-time "2025-08-07T10:00:00Z"
```

#### **Code Rollback**
```powershell
# Revert to previous Git commit
git log --oneline -5
git reset --hard HEAD~1

# Revert specific file
git checkout HEAD~1 -- src/agents/agent_elevator/app.py

# Deploy rolled back code
terraform apply
```

#### **Emergency Procedures**
1. **Service Unavailable**: 
   - Check CloudWatch alarms
   - Verify Lambda function status
   - Check API Gateway logs

2. **Data Corruption**:
   - Stop all write operations
   - Restore from latest backup
   - Verify data integrity

3. **Security Breach**:
   - Rotate all API keys immediately
   - Review CloudTrail logs
   - Update IAM policies

### **5.4. Backup Strategy**

#### **Automated Backups**
- **DynamoDB**: Point-in-time recovery enabled
- **S3**: Versioning enabled for all buckets
- **Terraform State**: Stored in S3 with versioning
- **Code**: Git repository with full history

#### **Manual Backups**
```powershell
# Create manual DynamoDB backup
aws dynamodb create-backup \
  --table-name bos-data-dev \
  --backup-name manual-backup-$(Get-Date -Format "yyyyMMdd-HHmmss")

# Export DynamoDB data
aws dynamodb export-table \
  --table-arn arn:aws:dynamodb:us-east-1:123456789012:table/bos-data-dev \
  --s3-bucket bos-backups-dev \
  --export-format DYNAMODB_JSON
```

#### **Backup Verification**
```powershell
# List available backups
aws dynamodb list-backups --table-name bos-data-dev

# Verify backup integrity
aws dynamodb describe-backup --backup-arn <backup-arn>

# Test restore in isolated environment
aws dynamodb restore-table-from-backup \
  --target-table-name bos-data-test-restore \
  --backup-arn <backup-arn>
```

---

## 📚 **Documentation Dependencies**

### **Authority Documents**
This setup references:
- `docs/02-architecture/02-api-contract.md` - API design authority
- `docs/03-development/01-project-management.md` - Current implementation status
- `docs/03-development/02-cli-commands-reference.md` - Operational procedures
- `terraform/environments/dev/main.tf` - Infrastructure configuration

### **Next Steps**
After completing this setup:
1. Review current development status
2. Implement pending API Gateway handlers for PSIM and Coordinator agents
3. Implement multi-agent chat endpoint
4. Follow the documentation-first development workflow

---

**Last Updated**: August 7, 2025  
**Version**: 2.0  
**Authors**: Jomil & GitHub Copilot

This guide provides the complete blueprint for bootstrapping the BuildingOS development system.

---

**Navigation:**
⬅️ **Previous:** [Development Prompts](./05-development-prompts.md)  
🏠 **Up:** [Development Index](./README.md)
