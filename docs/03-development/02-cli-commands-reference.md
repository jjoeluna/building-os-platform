[📖 Docs](../README.md) > [🛠️ Development](./README.md) > **CLI Commands Reference**

---

# CLI Commands Reference

## 📋 Overview

This document contains essential command-line instructions for development, debugging, and deployment of the BuildingOS platform. All commands are organized by workflow and include both Windows PowerShell and general CLI commands.

---

## 🌍 **ENVIRONMENT MANAGEMENT**

### **Environment Variables Setup**

The BuildingOS platform supports multiple environments: `dev`, `stg`, and `prd`. You **MUST** set the environment variable before running any Terraform commands.

#### **Setting Environment Variables**
```powershell
# Option 1: Set for current session
$env:TF_VAR_environment = "dev"

# Option 2: Set permanently for user (recommended)
[Environment]::SetEnvironmentVariable("TF_VAR_environment", "dev", "User")

# Option 3: Create terraform.tfvars file (current approach)
# Create/edit terraform.tfvars in terraform/environments/{env}/ directory
echo 'environment = "dev"' > terraform.tfvars
```

#### **Switching Between Environments**

**For Development Environment:**
```powershell
cd terraform/environments/dev
$env:TF_VAR_environment = "dev"
# or edit terraform.tfvars: environment = "dev"
terraform init
terraform plan
terraform apply
```

**For Staging Environment:**
```powershell
cd terraform/environments/stg
$env:TF_VAR_environment = "stg"
# or edit terraform.tfvars: environment = "stg"
terraform init
terraform plan
terraform apply
```

**For Production Environment:**
```powershell
cd terraform/environments/prd
$env:TF_VAR_environment = "prd"
# or edit terraform.tfvars: environment = "prd"
terraform init
terraform plan
terraform apply
```

#### **Verify Current Environment**
```powershell
# Check environment variable
echo $env:TF_VAR_environment

# Check terraform.tfvars content
Get-Content terraform.tfvars

# Check deployed resources for specific environment
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-agent`) && contains(FunctionName, `dev`)].FunctionName'
```

#### **Environment-Specific Resource Naming**
All resources follow this naming pattern:
- **Lambda Functions**: `bos-agent-{name}-{environment}`
- **SNS Topics**: `bos-{topic-name}-topic-{environment}`  
- **DynamoDB Tables**: `bos-{table-name}-{environment}`
- **IAM Roles**: `bos-{role-name}-{environment}`

**Examples:**
- Development: `bos-agent-persona-dev`, `bos-intention-topic-dev`
- Staging: `bos-agent-persona-stg`, `bos-intention-topic-stg`
- Production: `bos-agent-persona-prd`, `bos-intention-topic-prd`

---

## 🚀 **1. DEVELOPMENT COMMANDS**

### **1.1 Environment Setup**

#### **AWS CLI Configuration**
```powershell
# Configure AWS CLI
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1
aws configure set default.output json

# Verify configuration
aws sts get-caller-identity
aws s3 ls
```

#### **Terraform Setup**
```powershell
# Navigate to environment directory
cd terraform/environments/dev

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan

# Apply changes
terraform apply
```

#### **Python Environment Setup**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest boto3 moto
```

### **1.2 Code Development & Deployment**

#### **Python Code Changes Workflow**

**🎯 IMPORTANT: Always Use Terraform for Deployment**
- ✅ **Correct Process:** Edit code → Install deps → Terraform deploy
- ❌ **Never Use:** Direct AWS CLI deployment (`aws lambda update-function-code`)
- **Reason:** Terraform manages Infrastructure as Code with `source_code_hash` detection

**Step-by-Step Code Deployment:**

```powershell
# STEP 1: Edit Source Code
# Edit files in: src/agents/{agent_name}/app.py
# Make your code changes...

# STEP 2: Install/Update Dependencies (if requirements.txt changed)
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents
.\scripts\build_lambdas.ps1 -LambdaName tool_psim -Type tools

# STEP 3: Deploy via Terraform (Infrastructure as Code)
cd terraform/environments/dev
terraform plan    # Review changes - Terraform detects code changes via source_code_hash
terraform apply   # Deploy both code and infrastructure changes

# STEP 4: Validate Deployment
cd ..\..\tests\api
.\.venv\Scripts\Activate.ps1
python diagnose_api.py    # Quick validation (30 seconds)
python run_tests.py       # Complete test suite
```

#### **Build Lambda Dependencies**

```powershell
# Prepare dependencies for agents
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents
.\scripts\build_lambdas.ps1 -LambdaName agent_persona -Type agents
.\scripts\build_lambdas.ps1 -LambdaName agent_director -Type agents

# Prepare dependencies for tools  
.\scripts\build_lambdas.ps1 -LambdaName tool_psim -Type tools
.\scripts\build_lambdas.ps1 -LambdaName tool_elevator -Type tools

# Script automatically:
# 1. Installs Python dependencies in source directory
# 2. Prepares for Terraform automatic ZIP creation
# 3. Maintains Infrastructure as Code consistency
```

#### **Code Quality & Testing**

```powershell
# Local code testing before deployment
python -m pytest tests/ -v

# Run specific test for agent
python -m pytest tests/agents/test_agent_elevator.py -v

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Code quality checks
black src/              # Format code
flake8 src/            # Lint code  
mypy src/              # Type checking
bandit -r src/         # Security check

# API endpoint testing (after deployment)
.\.venv\Scripts\Activate.ps1
cd tests\api
python diagnose_api.py              # Quick diagnosis
python run_tests.py                 # Complete suite
```

#### **Terraform Workflow for Code Changes**

```powershell
# Terraform automatically detects code changes through source_code_hash
cd terraform/environments/dev

# Review what Terraform will change
terraform plan
# Output will show: aws_lambda_function.agent_elevator will be updated in-place
# ~ resource "aws_lambda_function" "agent_elevator" {
#     ~ source_code_hash = "old_hash" -> "new_hash"

# Apply the changes
terraform apply

# Verify deployment
terraform output    # Get API endpoints
aws lambda get-function --function-name bos-agent-elevator-dev
```

---

## 🐛 **2. DEBUGGING COMMANDS**

### **2.1 AWS Lambda Debugging**

#### **Function Logs**
```powershell
# Get recent logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bos-agent"

# Tail logs in real-time
aws logs tail /aws/lambda/bos-agent-elevator-dev --follow

# Get logs for specific time range
aws logs filter-log-events --log-group-name "/aws/lambda/bos-agent-elevator-dev" --start-time 1691420400000

# Download logs to file
aws logs filter-log-events --log-group-name "/aws/lambda/bos-agent-elevator-dev" --output text > logs.txt
```

#### **Function Information**
```powershell
# List all Lambda functions (basic)
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-agent`)].FunctionName'

# List Lambda functions with detailed info (table format)
aws lambda list-functions --query "Functions[?contains(FunctionName, 'bos-agent-')].{Name:FunctionName,Runtime:Runtime,LastModified:LastModified}" --output table

# List functions by environment
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-agent`) && contains(FunctionName, `dev`)].FunctionName'

# Get function configuration
aws lambda get-function-configuration --function-name bos-agent-elevator-dev

# Get function code location
aws lambda get-function --function-name bos-agent-elevator-dev

# Invoke function for testing
aws lambda invoke --function-name bos-agent-elevator-dev --payload '{"test": true}' response.json
```

### **2.2 SNS Debugging**

#### **Topic Information**
```powershell
# List SNS topics
aws sns list-topics --query 'Topics[?contains(TopicArn, `bos-`)].TopicArn'

# Get topic attributes
aws sns get-topic-attributes --topic-arn arn:aws:sns:us-east-1:123456789012:bos-intention-topic-dev

# List subscriptions
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-east-1:123456789012:bos-intention-topic-dev

# Publish test message
aws sns publish --topic-arn arn:aws:sns:us-east-1:123456789012:bos-intention-topic-dev --message '{"test": "message"}'
```

### **2.3 DynamoDB Debugging**

#### **Table Operations**
```powershell
# List tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `bos-`)]'

# Describe table
aws dynamodb describe-table --table-name bos-short-term-memory-dev

# Scan table (use with caution)
aws dynamodb scan --table-name bos-short-term-memory-dev --max-items 10

# Get specific item
aws dynamodb get-item --table-name bos-short-term-memory-dev --key '{"SessionId": {"S": "user123"}}'

# Query with condition
aws dynamodb query --table-name bos-mission-state-dev --key-condition-expression "mission_id = :id" --expression-attribute-values '{":id": {"S": "mission-123"}}'
```

### **2.4 API Gateway Debugging**

#### **API Information**
```powershell
# List APIs
aws apigatewayv2 get-apis --query 'Items[?contains(Name, `bos-`)].{Name:Name,ApiId:ApiId,ApiEndpoint:ApiEndpoint}'

# Get API details
aws apigatewayv2 get-api --api-id YOUR_API_ID

# List routes
aws apigatewayv2 get-routes --api-id YOUR_API_ID

# List routes with details (table format)
aws apigatewayv2 get-routes --api-id YOUR_API_ID --query 'Items[].{Route:RouteKey,Target:Target}' --output table

# Test endpoint
curl -X GET "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health"
Invoke-RestMethod -Uri "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health" -Method GET
```

### **2.5 CloudWatch Debugging**

#### **Metrics and Alarms**
```powershell
# List metrics for Lambda
aws cloudwatch list-metrics --namespace AWS/Lambda --metric-name Invocations

# Get metric statistics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Duration --dimensions Name=FunctionName,Value=bos-agent-elevator-dev --start-time 2025-08-07T00:00:00Z --end-time 2025-08-07T23:59:59Z --period 3600 --statistics Average

# List alarms
aws cloudwatch describe-alarms --alarm-name-prefix bos-

# Create custom metric
aws cloudwatch put-metric-data --namespace BuildingOS/Agents --metric-data MetricName=TaskProcessed,Value=1,Unit=Count
```

---

## 🚢 **3. DEPLOYMENT COMMANDS**

### **3.1 Terraform Deployment**

#### **Environment Deployment**
```powershell
# STEP 1: Verify current environment
echo "Current environment: $env:TF_VAR_environment"
Get-Content terraform.tfvars  # Should show: environment = "dev"

# STEP 2: Deploy to development
cd terraform/environments/dev
terraform init
terraform plan -out=tfplan    # Review all changes including code updates
terraform apply tfplan

# STEP 3: Verify deployment
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-agent`) && contains(FunctionName, `dev`)].FunctionName'

# Deploy to staging (after dev testing)
cd ../stg
# Update terraform.tfvars: environment = "stg"
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Deploy to production (after stg validation)
cd ../prd  
# Update terraform.tfvars: environment = "prd"
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

#### **Code Changes Deployment Process**

```powershell
# Complete workflow for Python code changes
# 1. Edit code in src/agents/{agent_name}/app.py

# 2. Install dependencies if requirements.txt changed
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents

# 3. Deploy via Terraform (detects changes automatically)
cd terraform/environments/dev
terraform plan    # Shows code changes via source_code_hash
# Example output:
#   ~ resource "aws_lambda_function" "agent_elevator" {
#       ~ source_code_hash = "abc123..." -> "def456..."
#   }

terraform apply   # Deploys code + infrastructure changes

# 4. Test deployment
cd ..\..\tests\api
python diagnose_api.py    # Quick validation
python run_tests.py       # Complete testing

# 5. Promote to other environments if tests pass
cd terraform/environments/stg
terraform plan && terraform apply    # Deploy to staging
cd ../prd  
terraform plan && terraform apply    # Deploy to production
```

#### **Why Terraform for Code Deployment?**

```powershell
# ✅ CORRECT: Terraform manages everything
terraform apply    # Detects code changes, creates ZIP, deploys

# ❌ WRONG: Direct AWS deployment breaks IaC
aws lambda update-function-code --function-name bos-agent-elevator-dev --zip-file fileb://code.zip

# Problems with direct deployment:
# - Terraform state becomes inconsistent
# - Next terraform apply may overwrite manual changes  
# - No version control of deployments
# - Difficult rollbacks
# - Breaks Infrastructure as Code principles
```

#### **Environment Switching Workflow**
```powershell
# Complete environment switch example
# From DEV to STG:

# 1. Finish work in dev
cd terraform/environments/dev
terraform plan  # Verify no pending changes

# 2. Switch to staging
cd ../stg
echo 'environment = "stg"' > terraform.tfvars
$env:TF_VAR_environment = "stg"

# 3. Deploy to staging
terraform init
terraform plan    # Review changes including latest code
terraform apply

# 4. Verify staging deployment
aws lambda list-functions --query 'Functions[?contains(FunctionName, `stg`)].FunctionName'
```

#### **Targeted Deployment**
```powershell
# Deploy specific resource
terraform apply -target=aws_lambda_function.agent_elevator

# Deploy specific module
terraform apply -target=module.intention_topic

# Refresh state
terraform refresh

# Get infrastructure outputs (API endpoints, bucket names, etc.)
terraform output

# Get specific output value
terraform output api_endpoint

# Import existing resource
terraform import aws_lambda_function.agent_elevator bos-agent-elevator-dev
```

#### **State Management**
```powershell
# List state
terraform state list

# Show specific resource
terraform state show aws_lambda_function.agent_elevator

# Move resource in state
terraform state mv aws_lambda_function.old_name aws_lambda_function.new_name

# Remove resource from state
terraform state rm aws_lambda_function.agent_elevator

# Pull remote state
terraform state pull > backup.tfstate
```

### **3.2 Infrastructure as Code Principles**

#### **Code Deployment Best Practices**

```powershell
# ✅ CORRECT WORKFLOW: Infrastructure as Code
# 1. Edit Python code in source directory
code src/agents/agent_elevator/app.py

# 2. Install dependencies if needed
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents

# 3. Let Terraform manage deployment
cd terraform/environments/dev
terraform plan    # Shows source_code_hash changes
terraform apply   # Creates ZIP and deploys automatically

# 4. Validate deployment
cd ..\..\tests\api && python diagnose_api.py

# ❌ WRONG: Direct AWS deployment (breaks IaC)
aws lambda update-function-code --function-name bos-agent-elevator-dev --zip-file fileb://code.zip
# Problems: State drift, inconsistency, no version control

# ❌ WRONG: Manual ZIP creation
zip -r agent.zip src/agents/agent_elevator/
# Problem: Terraform uses data.archive_file for automatic ZIP creation
```

#### **Terraform Automatic Code Detection**

```powershell
# How Terraform detects code changes:
# 1. data.archive_file creates ZIP from source directory
# 2. source_code_hash computed from ZIP contents  
# 3. When code changes, hash changes
# 4. terraform plan shows function will be updated
# 5. terraform apply uploads new ZIP to Lambda

# View Terraform's automatic ZIP creation
terraform show | findstr "archive_file"
# Shows: data.archive_file.agent_elevator_zip

# View source code hash tracking
terraform show | findstr "source_code_hash" 
# Shows: source_code_hash = "abc123def456..."
```

#### **Multi-Environment Code Promotion**

```powershell
# Promote tested code through environments
# 1. Develop and test in dev
cd terraform/environments/dev
terraform apply

# 2. Test with Python test suite
cd ..\..\tests\api
python run_tests.py    # Ensure 90%+ pass rate

# 3. Promote to staging
cd terraform/environments/stg
terraform plan    # Shows same code changes for stg environment
terraform apply

# 4. Final validation in staging
cd ..\..\tests\api
# Update config for staging API endpoint
python run_tests.py

# 5. Promote to production
cd terraform/environments/prd
terraform plan && terraform apply
```

### **3.3 Post-Deployment Testing & Validation**

#### **Testing Workflow After Code Changes**

```powershell
# Complete testing workflow after terraform apply
cd tests\api
.\.venv\Scripts\Activate.ps1

# 1. Quick diagnosis (30 seconds) - immediate feedback
python diagnose_api.py
# Shows: Overall health, critical issues, performance metrics

# 2. Specific endpoint testing during development
python -m pytest test_endpoints.py::TestElevatorEndpoint -v
python -m pytest test_endpoints.py::TestPersonaEndpoint -v

# 3. Complete validation suite (2-3 minutes)
python run_tests.py
# Generates: HTML report, JSON report, comprehensive metrics

# 4. Review test results
# HTML Report: tests\api\reports\api-test-report-{timestamp}.html
# JSON Report: tests\api\reports\api-test-report-{timestamp}.json

# 5. Check specific issues if tests fail
python -m pytest test_endpoints.py -v --tb=long    # Detailed error info
aws logs tail "/aws/lambda/bos-agent-elevator-dev" --follow    # Live logs
```

#### **Performance and Health Monitoring**

```powershell
# Monitor deployment health
# API Gateway health
curl -s "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health" | jq

# Lambda function metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=bos-agent-elevator-dev \
  --start-time 2025-08-07T00:00:00Z \
  --end-time 2025-08-07T23:59:59Z \
  --period 300 \
  --statistics Average,Maximum

# Error rate monitoring
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=bos-agent-elevator-dev \
  --start-time 2025-08-07T00:00:00Z \
  --end-time 2025-08-07T23:59:59Z \
  --period 300 \
  --statistics Sum
```

#### **Rollback Procedures**

```powershell
# If deployment fails or tests show issues:

# 1. Quick rollback via Terraform (if previous state available)
cd terraform/environments/dev
terraform plan -destroy -target=aws_lambda_function.agent_elevator
# Review what will be destroyed/recreated

# 2. Revert code changes and redeploy
git checkout HEAD~1 -- src/agents/agent_elevator/app.py
terraform plan    # Shows reverting to previous source_code_hash
terraform apply

# 3. Alternative: Deploy specific Lambda version
aws lambda update-alias \
  --function-name bos-agent-elevator-dev \
  --name LIVE \
  --function-version {previous_version}

# 4. Validate rollback
cd ..\..\tests\api
python diagnose_api.py    # Confirm issues resolved
```

### **3.4 Infrastructure Verification**
```powershell
# Test all agents
Invoke-RestMethod -Uri "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health" -Method GET
Invoke-RestMethod -Uri "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/persona" -Method GET
Invoke-RestMethod -Uri "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/director" -Method GET

# Test elevator API
Invoke-RestMethod -Uri "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/elevator/call" -Method POST -Body '{"floor": 5}' -ContentType "application/json"

# Check SNS message flow
aws sns publish --topic-arn arn:aws:sns:us-east-1:123456789012:bos-intention-topic-dev --message '{"user_id": "test", "message": "test message"}'
```

---

## 🔧 **4. MAINTENANCE COMMANDS**

### **4.1 Backup and Recovery**

#### **State Backup**
```powershell
# Backup Terraform state
terraform state pull > "backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm').tfstate"

# Backup DynamoDB table
aws dynamodb create-backup --table-name bos-short-term-memory-dev --backup-name "backup-$(Get-Date -Format 'yyyy-MM-dd')"

# Export DynamoDB to S3
aws dynamodb export-table-to-point-in-time --table-arn arn:aws:dynamodb:us-east-1:123456789012:table/bos-short-term-memory-dev --s3-bucket your-backup-bucket --s3-prefix dynamodb-backups/
```

#### **Restore Operations**
```powershell
# Restore DynamoDB from backup
aws dynamodb restore-table-from-backup --target-table-name bos-short-term-memory-dev-restored --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/bos-short-term-memory-dev/backup/01691420400000-12345678

# Import Terraform state
terraform import aws_lambda_function.agent_elevator bos-agent-elevator-dev
```

### **4.2 Monitoring Commands**

#### **Performance Monitoring**
```powershell
# Check Lambda metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Duration --dimensions Name=FunctionName,Value=bos-agent-elevator-dev --start-time 2025-08-07T00:00:00Z --end-time 2025-08-07T23:59:59Z --period 300 --statistics Maximum,Average

# Check error rates
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Errors --dimensions Name=FunctionName,Value=bos-agent-elevator-dev --start-time 2025-08-07T00:00:00Z --end-time 2025-08-07T23:59:59Z --period 300 --statistics Sum

# Check DynamoDB metrics
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ConsumedReadCapacityUnits --dimensions Name=TableName,Value=bos-short-term-memory-dev --start-time 2025-08-07T00:00:00Z --end-time 2025-08-07T23:59:59Z --period 300 --statistics Sum
```

### **4.3 Cleanup Commands**

#### **Resource Cleanup**
```powershell
# Delete unused Lambda versions
aws lambda list-versions-by-function --function-name bos-agent-elevator-dev --query 'Versions[?Version!=`$LATEST`].Version' --output text | ForEach-Object { aws lambda delete-function --function-name bos-agent-elevator-dev --qualifier $_ }

# Clean old CloudWatch logs
aws logs delete-log-group --log-group-name /aws/lambda/old-function-name

# Clean Terraform cache
Remove-Item -Recurse -Force .terraform/
Remove-Item terraform.tfstate.backup
```

---

## 🔍 **5. TROUBLESHOOTING COMMANDS**

### **5.1 Network Connectivity**

#### **Connectivity Tests**
```powershell
# Test external API connectivity
curl -v https://anna-minimal-api.neomot.com/health
Invoke-RestMethod -Uri "https://anna-minimal-api.neomot.com/health" -Method GET -Verbose

# Test DNS resolution
nslookup anna-minimal-api.neomot.com
Resolve-DnsName anna-minimal-api.neomot.com

# Test AWS service connectivity
aws sts get-caller-identity
aws lambda list-functions --max-items 1
```

### **5.2 Permission Issues**

#### **IAM Debugging**
```powershell
# Get current identity
aws sts get-caller-identity

# Simulate policy
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::123456789012:role/bos-lambda-exec-role-dev --action-names lambda:InvokeFunction --resource-arns arn:aws:lambda:us-east-1:123456789012:function:bos-agent-elevator-dev

# List role policies
aws iam list-attached-role-policies --role-name bos-lambda-exec-role-dev
aws iam list-role-policies --role-name bos-lambda-exec-role-dev

# Get policy document
aws iam get-policy-version --policy-arn arn:aws:iam::123456789012:policy/bos-sns-publish-policy-dev --version-id v1
```

---

## 📚 **6. USEFUL ALIASES AND SHORTCUTS**

### **PowerShell Aliases & Functions**
```powershell
# Add to PowerShell profile
Set-Alias tf terraform
Set-Alias k kubectl
Set-Alias ll Get-ChildItem

# Custom functions for BuildingOS development
function Deploy-Code { 
    param($AgentName)
    Write-Host "🔧 Installing dependencies for $AgentName..."
    .\scripts\build_lambdas.ps1 -LambdaName $AgentName -Type agents
    
    Write-Host "🚀 Deploying via Terraform..."
    cd terraform/environments/dev
    terraform plan
    terraform apply -auto-approve
    
    Write-Host "🧪 Running quick tests..."
    cd ..\..\tests\api
    python diagnose_api.py
}

function Get-LambdaLogs { 
    param($FunctionName)
    aws logs tail "/aws/lambda/$FunctionName" --follow 
}

function Test-API { 
    param($Endpoint)
    Invoke-RestMethod -Uri $Endpoint -Method GET
}

function Quick-Test {
    cd tests\api
    .\.venv\Scripts\Activate.ps1
    python diagnose_api.py
}

function Full-Test {
    cd tests\api
    .\.venv\Scripts\Activate.ps1
    python run_tests.py
}

# Usage examples:
# Deploy-Code agent_elevator
# Get-LambdaLogs bos-agent-elevator-dev
# Quick-Test
# Full-Test
```

### **Environment Variables**
```powershell
# AWS Configuration
$env:AWS_REGION = "us-east-1"
$env:AWS_PROFILE = "default"

# Terraform Environment (REQUIRED - must match your target environment)
$env:TF_VAR_environment = "dev"    # Options: dev, stg, prd

# BuildingOS specific
$env:BOS_API_ENDPOINT = "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"
$env:BOS_ENVIRONMENT = "dev"       # Should match TF_VAR_environment

# Verification commands
echo "Current environment: $env:TF_VAR_environment"
echo "API endpoint: $env:BOS_API_ENDPOINT"

# Environment-specific API endpoints
# Dev:  https://YOUR_DEV_API_ID.execute-api.us-east-1.amazonaws.com
# Stg:  https://YOUR_STG_API_ID.execute-api.us-east-1.amazonaws.com  
# Prd:  https://YOUR_PRD_API_ID.execute-api.us-east-1.amazonaws.com
```

### **Important Notes**
- **Always verify your environment** before running terraform commands
- **Each environment has separate AWS resources** - changes in one environment don't affect others
- **Use terraform.tfvars files** for persistent environment configuration
- **Test in dev first**, then promote to stg, finally to prd

---

## 🔄 **7. COMMAND HISTORY**

| Date | Command | Purpose | Environment |
|------|---------|---------|-------------|
| 2025-08-07 | `terraform apply` | Agent naming standardization | dev |
| 2025-08-07 | `aws lambda list-functions --query "Functions[?contains(FunctionName, 'bos-agent-')].{Name:FunctionName,Runtime:Runtime,LastModified:LastModified}" --output table` | Verify renamed Lambda functions | dev |
| 2025-08-07 | `terraform output` | Get API Gateway endpoint for testing | dev |

### **Command Templates for New Workflow**

```powershell
# Template for complete code change workflow
# 1. Edit Code
code src/agents/agent_{NAME}/app.py

# 2. Install Dependencies  
.\scripts\build_lambdas.ps1 -LambdaName agent_{NAME} -Type agents

# 3. Deploy via Terraform
cd terraform/environments/{ENV}
terraform plan    # Review source_code_hash changes
terraform apply

# 4. Test Deployment
cd ..\..\tests\api
python diagnose_api.py                                    # Quick validation
python -m pytest test_endpoints.py::Test{NAME}Endpoint   # Specific tests
python run_tests.py                                       # Complete suite

# Template for multi-environment deployment
# Dev → Stg → Prd promotion
cd terraform/environments/dev && terraform apply
cd ../stg && terraform apply  
cd ../prd && terraform apply

# Template for troubleshooting deployment
aws lambda get-function --function-name bos-agent-{NAME}-{ENV}
aws logs tail "/aws/lambda/bos-agent-{NAME}-{ENV}" --follow --format short
terraform show | findstr "source_code_hash"
```

### **Development Lifecycle Templates**

```powershell
# Template: New Feature Development
# 1. Create feature branch
git checkout -b feature/elevator-improvements

# 2. Edit code
code src/agents/agent_elevator/app.py
# Make your changes...

# 3. Test locally if possible
python -m pytest tests/agents/test_agent_elevator.py -v

# 4. Deploy to dev and test
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents
cd terraform/environments/dev && terraform apply
cd ..\..\tests\api && python diagnose_api.py

# 5. If tests pass, commit changes
git add . && git commit -m "feat: improve elevator error handling"

# 6. Promote to staging
cd terraform/environments/stg && terraform apply
cd ..\..\tests\api && python run_tests.py

# 7. If staging tests pass, merge and deploy to production
git checkout main && git merge feature/elevator-improvements
cd terraform/environments/prd && terraform apply

# Template: Hot Fix Deployment
# 1. Quick fix in main branch
code src/agents/agent_elevator/app.py
# Fix critical issue...

# 2. Deploy directly to production (emergency only)
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents
cd terraform/environments/prd
terraform plan    # Verify only intended changes
terraform apply
cd ..\..\tests\api && python diagnose_api.py

# 3. Validate fix
python -m pytest test_endpoints.py::TestElevatorEndpoint -v

# Template: Dependency Updates
# 1. Update requirements.txt
code src/agents/agent_elevator/requirements.txt
# Add new package or update version...

# 2. Install and test locally
pip install -r src/agents/agent_elevator/requirements.txt
python -m pytest tests/agents/test_agent_elevator.py -v

# 3. Deploy dependency changes
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents
cd terraform/environments/dev && terraform apply
cd ..\..\tests\api && python run_tests.py
```

---

## 📋 **8. API CONTRACT SYNCHRONIZATION**

The API contract serves as the single source of truth for all endpoints. Always update the contract before implementing changes.

### **Contract Management Workflow**

```bash
# 1. Update API contract first
# Edit: docs/02-architecture/02-api-contract.md

# 2. Verify current implementation matches contract
aws apigatewayv2 get-routes --api-id pj4vlvxrg7 --region us-east-1 --output table

# 3. Test endpoints after implementation
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health"
curl -X POST "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/persona" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "test"}'
```

### **Implementation Status Verification**

```bash
# Check which endpoints are implemented
aws apigatewayv2 get-routes --api-id pj4vlvxrg7 --region us-east-1 \
  --query 'Items[].RouteKey' --output table

# Validate contract compliance
# Compare with: docs/02-architecture/02-api-contract.md -> Implementation Status table

# Test all working endpoints
curl -s "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health" | jq
curl -s "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/director" | jq
```

---

## 📋 **9. AI ASSISTANT CONTEXT MANAGEMENT**

To maintain continuity across AI assistant sessions, use the specialized context prompts for different work types.

### **Context Prompts Available**
- **Developer Context**: `docs/03-development/03-developer-context-prompt.md`
  - **Use for**: Implementation, debugging, testing, CLI operations
- **Architect Context**: `docs/03-development/04-architect-context-prompt.md`  
  - **Use for**: Design decisions, system architecture, technology planning

### **Session Workflow**

```bash
# 1. Choose appropriate context prompt based on session type:
# - Development tasks → Developer Context Prompt
# - Architecture tasks → Architect Context Prompt

# 2. Copy prompt from appropriate file and customize with:
#    - Current specific task
#    - Recent changes since last session
#    - Environment focus (dev/stg/prd)

# 3. Include current system status
terraform output  # Current infrastructure state
aws apigatewayv2 get-routes --api-id pj4vlvxrg7 --region us-east-1 --output table  # API status
```

### **Documentation Dependencies**

**All context prompts reference these authority documents:**
- `docs/02-architecture/02-api-contract.md` - **API design authority**
- `docs/03-development/01-development-status.md` - **Current implementation status**
- `docs/02-architecture/06-architecture-adequation-plan.md` - **Implementation roadmap**
- `docs/03-development/02-cli-commands-reference.md` - **Operational procedures**

### **Context Update Triggers**

```bash
# Update context prompts when:
# - New agents are added
# - API endpoints change  
# - Infrastructure evolves
# - Documentation structure changes
# - Development priorities shift

# Update development status when:
# - Implementation milestones completed
# - Endpoint status changes
# - New priorities identified
# - Testing results change
```

---

**Note**: Replace placeholder values (YOUR_API_ID, account numbers, etc.) with actual values from your environment. Always test commands in development environment first.

---

**Navigation:**
⬅️ **Previous:** [Development Status](./01-development-status.md)  
➡️ **Next:** [Developer Context Prompt](./03-developer-context-prompt.md)  
🏠 **Up:** [Development Index](./README.md)
