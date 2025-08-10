# 🚀 Deployment Guide - BuildingOS Platform

## 📋 Overview

This guide provides comprehensive instructions for deploying the BuildingOS platform to different environments (development, staging, and production). It covers the complete deployment process, from prerequisites to post-deployment validation.

---

## 🎯 **Prerequisites**

### **Required Tools**
- **AWS CLI** - Version 2.x or later
- **Terraform** - Version 1.5 or later
- **Python** - Version 3.11 or later
- **Git** - Version control
- **PowerShell** (Windows) or **Bash** (Linux/Mac)

### **AWS Requirements**
- **AWS Account** - Active AWS account with appropriate permissions
- **IAM User** - User with programmatic access and required permissions
- **S3 Bucket** - For Terraform state storage (created automatically)
- **DynamoDB Table** - For Terraform state locking (created automatically)

### **Required Permissions**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "sns:*",
                "dynamodb:*",
                "apigateway:*",
                "cloudwatch:*",
                "iam:*",
                "s3:*",
                "logs:*",
                "xray:*"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 🌍 **Environment Setup**

### **Environment Variables**

**Required Environment Variables:**
```bash
# Environment configuration
export TF_VAR_environment="dev"        # dev, stg, prd
export TF_VAR_aws_region="us-east-1"   # AWS region
export TF_VAR_project_name="BuildingOS" # Project name
export TF_VAR_owner="DevOps Team"      # Resource owner
export TF_VAR_cost_center="IT-001"     # Cost center
```

**Setting Environment Variables:**
```powershell
# Windows PowerShell
$env:TF_VAR_environment = "dev"
$env:TF_VAR_aws_region = "us-east-1"
$env:TF_VAR_project_name = "BuildingOS"
$env:TF_VAR_owner = "DevOps Team"
$env:TF_VAR_cost_center = "IT-001"

# Linux/Mac Bash
export TF_VAR_environment="dev"
export TF_VAR_aws_region="us-east-1"
export TF_VAR_project_name="BuildingOS"
export TF_VAR_owner="DevOps Team"
export TF_VAR_cost_center="IT-001"
```

### **AWS Configuration**

**Configure AWS CLI:**
```bash
# Configure AWS credentials
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1
aws configure set default.output json

# Verify configuration
aws sts get-caller-identity
```

---

## 🏗️ **Infrastructure Deployment**

### **Step 1: Initialize Terraform Backend**

**Create Backend Resources (One-time setup):**
```powershell
# Set variables
$S3_BUCKET_NAME="bos-terraform-tfstate"
$AWS_REGION="us-east-1"

# Create S3 bucket for Terraform state
if ($AWS_REGION -eq "us-east-1") {
    aws s3api create-bucket --bucket $S3_BUCKET_NAME --region $AWS_REGION
} else {
    aws s3api create-bucket --bucket $S3_BUCKET_NAME --region $AWS_REGION --create-bucket-configuration LocationConstraint=$AWS_REGION
}

# Enable versioning
aws s3api put-bucket-versioning --bucket $S3_BUCKET_NAME --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table `
    --table-name terraform-state-lock `
    --attribute-definitions AttributeName=LockID,AttributeType=S `
    --key-schema AttributeName=LockID,KeyType=HASH `
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 `
    --region $AWS_REGION
```

### **Step 2: Deploy Development Environment**

**Navigate to Development Environment:**
```bash
cd terraform/environments/dev
```

**Initialize Terraform:**
```bash
# Initialize Terraform with backend configuration
terraform init

# Verify backend configuration
terraform init -reconfigure
```

**Validate Configuration:**
```bash
# Validate Terraform configuration
terraform validate

# Check for any issues
terraform fmt -check
terraform plan
```

**Deploy Infrastructure:**
```bash
# Deploy to development environment
terraform apply -auto-approve

# Or review changes first
terraform plan -out=dev-plan.tfplan
terraform apply dev-plan.tfplan
```

### **Step 3: Deploy Staging Environment**

**Navigate to Staging Environment:**
```bash
cd ../stg
```

**Configure Environment:**
```bash
# Set staging environment variables
export TF_VAR_environment="stg"

# Initialize Terraform
terraform init
terraform validate
```

**Deploy to Staging:**
```bash
# Plan and deploy
terraform plan -out=stg-plan.tfplan
terraform apply stg-plan.tfplan
```

### **Step 4: Deploy Production Environment**

**Navigate to Production Environment:**
```bash
cd ../prd
```

**Configure Environment:**
```bash
# Set production environment variables
export TF_VAR_environment="prd"

# Initialize Terraform
terraform init
terraform validate
```

**Deploy to Production:**
```bash
# Plan and deploy (with extra caution)
terraform plan -out=prd-plan.tfplan
terraform apply prd-plan.tfplan
```

---

## 🔄 **Deployment Process**

### **Pre-Deployment Checklist**

**Development Environment:**
- [ ] AWS credentials configured
- [ ] Environment variables set
- [ ] Terraform backend initialized
- [ ] Code changes tested locally
- [ ] Documentation updated

**Staging Environment:**
- [ ] Development environment validated
- [ ] Integration tests passed
- [ ] Performance tests completed
- [ ] Security review completed
- [ ] Stakeholder approval obtained

**Production Environment:**
- [ ] Staging environment validated
- [ ] All tests passed
- [ ] Security audit completed
- [ ] Backup procedures verified
- [ ] Rollback plan prepared
- [ ] Change management approval

### **Deployment Workflow**

**1. Development Deployment:**
```bash
# Navigate to dev environment
cd terraform/environments/dev

# Validate and deploy
terraform validate
terraform plan
terraform apply -auto-approve

# Verify deployment
terraform output
```

**2. Staging Deployment:**
```bash
# Navigate to staging environment
cd ../stg

# Deploy with validation
terraform validate
terraform plan -out=stg-plan.tfplan
terraform apply stg-plan.tfplan

# Run integration tests
pytest tests/integration/ -v
```

**3. Production Deployment:**
```bash
# Navigate to production environment
cd ../prd

# Deploy with extra validation
terraform validate
terraform plan -out=prd-plan.tfplan
terraform apply prd-plan.tfplan

# Verify production deployment
terraform output
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-agent`) && contains(FunctionName, `prd`)].FunctionName'
```

---

## 🧪 **Post-Deployment Validation**

### **Health Checks**

**Lambda Functions:**
```bash
# Check Lambda function status
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-agent`)].{Name:FunctionName,Status:State,Runtime:Runtime}'

# Test Lambda functions
aws lambda invoke --function-name bos-dev-agent-health-check response.json
cat response.json
```

**API Gateway:**
```bash
# Check API Gateway status
aws apigatewayv2 get-apis --query 'Items[?contains(Name, `bos-dev`)].{Name:Name,Status:ProtocolType}'

# Test API endpoints
curl -X GET "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health"
```

**DynamoDB Tables:**
```bash
# Check DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `bos-dev`)]'

# Verify table structure
aws dynamodb describe-table --table-name bos-dev-short-term-memory
```

### **Integration Tests**

**Run End-to-End Tests:**
```bash
# Run integration tests
python tests/test_e2e_new_architecture.py

# Run specific test suites
pytest tests/agents/ -v
pytest tests/integration/ -v
```

**Performance Tests:**
```bash
# Run performance tests
python tests/test_performance.py

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Average
```

---

## 🔄 **Rollback Procedures**

### **Infrastructure Rollback**

**Terraform Rollback:**
```bash
# Check Terraform state
terraform state list

# Rollback to previous version
terraform plan -refresh-only
terraform apply -auto-approve

# Or rollback specific resources
terraform destroy -target=aws_lambda_function.agent_persona
terraform apply
```

**Manual Rollback:**
```bash
# Rollback Lambda functions
aws lambda update-function-code \
    --function-name bos-dev-agent-persona \
    --zip-file fileb://previous-version.zip

# Rollback API Gateway
aws apigatewayv2 update-api \
    --api-id YOUR_API_ID \
    --name "Previous Version"
```

### **Data Rollback**

**DynamoDB Rollback:**
```bash
# Restore from backup
aws dynamodb restore-table-from-backup \
    --target-table-name bos-dev-short-term-memory \
    --backup-arn YOUR_BACKUP_ARN
```

---

## 📊 **Monitoring and Alerting**

### **CloudWatch Monitoring**

**Set Up Dashboards:**
```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name BuildingOS-Monitoring \
    --dashboard-body file://dashboard-config.json
```

**Configure Alarms:**
```bash
# Create Lambda error alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "BuildingOS-Lambda-Errors" \
    --alarm-description "Lambda function errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold
```

### **Log Analysis**

**View Logs:**
```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bos-dev"

# Get recent log events
aws logs get-log-events \
    --log-group-name "/aws/lambda/bos-dev-agent-persona" \
    --log-stream-name "latest"
```

---

## 🚨 **Troubleshooting**

### **Common Deployment Issues**

**Terraform Errors:**
```bash
# Validate configuration
terraform validate

# Check for syntax errors
terraform fmt -check

# Review plan details
terraform plan -detailed-exitcode
```

**AWS Permission Issues:**
```bash
# Check current permissions
aws sts get-caller-identity

# Test specific permissions
aws lambda list-functions
aws s3 ls
aws dynamodb list-tables
```

**Resource Conflicts:**
```bash
# Check for existing resources
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-`)]'
aws s3 ls | grep bos-
aws dynamodb list-tables --query 'TableNames[?contains(@, `bos-`)]'
```

### **Performance Issues**

**Lambda Performance:**
```bash
# Check Lambda metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Average,Maximum
```

**API Gateway Performance:**
```bash
# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApiGateway \
    --metric-name Count \
    --dimensions Name=ApiName,Value=bos-dev-http-api \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Sum
```

---

## 📚 **Additional Resources**

### **Documentation Links**
- **[Setup Guide](../03-setup-guide/setup-guide.md)** - Complete environment setup
- **[CLI Commands Reference](../02-cli-commands-reference/cli-commands-reference.md)** - Command reference
- **[Terraform Best Practices](../../04-operations/terraform-best-practices-checklist.md)** - Infrastructure guidelines
- **[Monitoring Strategy](../../04-operations/01-monitoring-strategy/monitoring-strategy.md)** - Monitoring and alerting

### **Support and Help**
- **Issues:** Create an issue in the GitHub repository
- **Documentation:** Review the complete documentation
- **Community:** Join the project community
- **Emergency:** Contact the DevOps team

---

**🎯 Ready to deploy? Start with the [Setup Guide](../03-setup-guide/setup-guide.md) and follow this deployment guide step by step!**
