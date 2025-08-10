# 🚨 Troubleshooting Guide - BuildingOS Platform

## 📋 Overview

This guide provides comprehensive troubleshooting procedures for common issues encountered during development, deployment, and operation of the BuildingOS platform. It includes error codes, debugging procedures, and resolution steps.

---

## 🎯 **Quick Troubleshooting Index**

### **Common Issues by Category**
- **[🔧 Terraform Issues](#terraform-issues)** - Infrastructure deployment problems
- **[🐍 Python Issues](#python-issues)** - Lambda function and code problems
- **[☁️ AWS Issues](#aws-issues)** - AWS service and permission problems
- **[🔗 API Issues](#api-issues)** - API Gateway and endpoint problems
- **[📊 Monitoring Issues](#monitoring-issues)** - CloudWatch and logging problems
- **[🔐 Security Issues](#security-issues)** - Authentication and authorization problems
- **[⚡ Performance Issues](#performance-issues)** - Performance and scalability problems

---

## 🔧 **Terraform Issues**

### **Common Terraform Errors**

#### **Error: Missing Required Provider**
```bash
Error: Missing required provider "hashicorp/random"
```

**Solution:**
```bash
# Initialize Terraform to download providers
terraform init

# Verify provider versions in versions.tf
cat terraform/environments/dev/versions.tf
```

#### **Error: Invalid Configuration**
```bash
Error: Invalid value for variable "environment"
```

**Solution:**
```bash
# Check variable validation rules
cat terraform/environments/dev/variables.tf

# Verify terraform.tfvars file
cat terraform/environments/dev/terraform.tfvars

# Set correct environment variable
export TF_VAR_environment="dev"
```

#### **Error: Backend Configuration**
```bash
Error: Backend configuration changed
```

**Solution:**
```bash
# Reconfigure backend
terraform init -reconfigure

# Verify backend configuration
cat terraform/environments/dev/backend.tf
```

#### **Error: State Lock**
```bash
Error: Error acquiring the state lock
```

**Solution:**
```bash
# Check DynamoDB table for locks
aws dynamodb scan --table-name terraform-state-lock

# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

### **Terraform Validation Issues**

#### **Error: Unsupported Argument**
```bash
Error: Unsupported argument "description" in module "lambda_function"
```

**Solution:**
```bash
# Check module variables
cat terraform/modules/lambda_function/variables.tf

# Remove unsupported arguments from module call
# Update terraform/environments/dev/lambda_functions.tf
```

#### **Error: Missing Required Argument**
```bash
Error: Missing required argument "name" in module "sns_topic"
```

**Solution:**
```bash
# Check module requirements
cat terraform/modules/sns_topic/variables.tf

# Add required arguments to module call
# Update terraform/environments/dev/sns.tf
```

---

## 🐍 **Python Issues**

### **Lambda Function Errors**

#### **Error: Module Not Found**
```bash
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
# Check Lambda layer dependencies
cat src/layers/common_utils/requirements.txt

# Install dependencies in layer
cd src/layers/common_utils
pip install -r requirements.txt -t .

# Rebuild and deploy Lambda layer
cd ../../../terraform/environments/dev
terraform apply -target=aws_lambda_layer_version.common_utils_layer
```

#### **Error: Import Error**
```bash
ImportError: cannot import name 'boto3'
```

**Solution:**
```bash
# Verify boto3 is included in Lambda runtime
# Check Lambda function configuration
aws lambda get-function --function-name bos-dev-agent-persona

# Update Lambda function to use correct runtime
terraform apply -target=aws_lambda_function.agent_persona
```

#### **Error: Timeout**
```bash
Task timed out after 30.0 seconds
```

**Solution:**
```bash
# Check Lambda timeout configuration
aws lambda get-function-configuration --function-name bos-dev-agent-persona

# Increase timeout if needed
# Update terraform/environments/dev/lambda_functions.tf
```

### **Code Issues**

#### **Error: Syntax Error**
```bash
SyntaxError: invalid syntax
```

**Solution:**
```bash
# Check Python syntax
python -m py_compile src/agents/agent_persona/main.py

# Use flake8 for linting
flake8 src/agents/agent_persona/
```

#### **Error: Type Error**
```bash
TypeError: 'NoneType' object is not subscriptable
```

**Solution:**
```bash
# Add type hints and null checks
# Example:
def process_data(data: dict) -> dict:
    if data is None:
        return {}
    return data.get('key', {})
```

---

## ☁️ **AWS Issues**

### **Permission Issues**

#### **Error: Access Denied**
```bash
AccessDenied: User is not authorized to perform: lambda:InvokeFunction
```

**Solution:**
```bash
# Check IAM permissions
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# Verify Lambda execution role
aws iam get-role --role-name bos-dev-lambda-exec-role
aws iam list-attached-role-policies --role-name bos-dev-lambda-exec-role
```

#### **Error: Resource Not Found**
```bash
ResourceNotFoundException: Function not found
```

**Solution:**
```bash
# List Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-dev`)].FunctionName'

# Check if function exists
aws lambda get-function --function-name bos-dev-agent-persona
```

### **Service Issues**

#### **Error: Service Unavailable**
```bash
ServiceUnavailable: The service is temporarily unavailable
```

**Solution:**
```bash
# Check AWS service status
# Visit: https://status.aws.amazon.com/

# Retry with exponential backoff
# Implement retry logic in code
```

#### **Error: Throttling**
```bash
ThrottlingException: Rate exceeded
```

**Solution:**
```bash
# Implement exponential backoff
# Check CloudWatch metrics for throttling
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Throttles \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Sum
```

---

## 🔗 **API Issues**

### **API Gateway Errors**

#### **Error: 404 Not Found**
```bash
HTTP/1.1 404 Not Found
```

**Solution:**
```bash
# Check API Gateway routes
aws apigatewayv2 get-routes --api-id YOUR_API_ID

# Verify Lambda integration
aws apigatewayv2 get-integrations --api-id YOUR_API_ID

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix "/aws/apigateway"
```

#### **Error: 500 Internal Server Error**
```bash
HTTP/1.1 500 Internal Server Error
```

**Solution:**
```bash
# Check Lambda function logs
aws logs get-log-events \
    --log-group-name "/aws/lambda/bos-dev-agent-persona" \
    --log-stream-name "latest"

# Verify Lambda function configuration
aws lambda get-function --function-name bos-dev-agent-persona
```

### **WebSocket Issues**

#### **Error: Connection Failed**
```bash
WebSocket connection failed
```

**Solution:**
```bash
# Check WebSocket API status
aws apigatewayv2 get-apis --query 'Items[?ProtocolType==`WEBSOCKET`]'

# Verify WebSocket routes
aws apigatewayv2 get-routes --api-id YOUR_WEBSOCKET_API_ID

# Check WebSocket logs
aws logs describe-log-groups --log-group-name-prefix "/aws/apigateway"
```

---

## 📊 **Monitoring Issues**

### **CloudWatch Issues**

#### **Error: No Logs Found**
```bash
No log streams found
```

**Solution:**
```bash
# Check if log group exists
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bos-dev"

# Create log group if missing
aws logs create-log-group --log-group-name "/aws/lambda/bos-dev-agent-persona"

# Check Lambda function logging configuration
aws lambda get-function --function-name bos-dev-agent-persona
```

#### **Error: Metrics Not Available**
```bash
No metrics data available
```

**Solution:**
```bash
# Check if metrics are being published
aws cloudwatch list-metrics --namespace AWS/Lambda

# Verify Lambda function is running
aws lambda get-function --function-name bos-dev-agent-persona

# Check CloudWatch agent configuration
```

### **X-Ray Issues**

#### **Error: Tracing Not Working**
```bash
X-Ray tracing not available
```

**Solution:**
```bash
# Check X-Ray tracing configuration
aws lambda get-function --function-name bos-dev-agent-persona

# Verify X-Ray permissions
aws iam get-role --role-name bos-dev-lambda-exec-role

# Check X-Ray service status
aws xray get-trace-summaries --start-time $(date -d '1 hour ago' --iso-8601=seconds) --end-time $(date --iso-8601=seconds)
```

---

## 🔐 **Security Issues**

### **Authentication Issues**

#### **Error: Invalid Credentials**
```bash
InvalidAccessKeyId: The AWS Access Key ID you provided does not exist
```

**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Reconfigure AWS CLI
aws configure

# Verify IAM user permissions
aws iam get-user
```

#### **Error: Insufficient Permissions**
```bash
AccessDenied: User is not authorized to perform: lambda:InvokeFunction
```

**Solution:**
```bash
# Check IAM policies
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# Verify Lambda execution role
aws iam get-role --role-name bos-dev-lambda-exec-role

# Check role policies
aws iam list-attached-role-policies --role-name bos-dev-lambda-exec-role
```

### **Encryption Issues**

#### **Error: Encryption Failed**
```bash
KMSInvalidStateException: The key is not available
```

**Solution:**
```bash
# Check KMS key status
aws kms describe-key --key-id YOUR_KEY_ID

# Verify KMS permissions
aws iam list-attached-role-policies --role-name bos-dev-lambda-exec-role

# Check KMS key policy
aws kms get-key-policy --key-id YOUR_KEY_ID --policy-name default
```

---

## ⚡ **Performance Issues**

### **Lambda Performance**

#### **Error: Cold Start**
```bash
High latency on first request
```

**Solution:**
```bash
# Check Lambda function configuration
aws lambda get-function --function-name bos-dev-agent-persona

# Optimize function size
# Use Lambda layers for dependencies
# Implement connection pooling

# Monitor cold start metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Average,Maximum
```

#### **Error: Memory Issues**
```bash
Memory limit exceeded
```

**Solution:**
```bash
# Check memory usage
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name UsedMemory \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Average,Maximum

# Increase memory allocation
# Update terraform/environments/dev/lambda_functions.tf
```

### **API Gateway Performance**

#### **Error: High Latency**
```bash
API Gateway response time > 5 seconds
```

**Solution:**
```bash
# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApiGateway \
    --metric-name Latency \
    --dimensions Name=ApiName,Value=bos-dev-http-api \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Average,Maximum

# Optimize Lambda function performance
# Implement caching strategies
# Use API Gateway caching
```

---

## 🔍 **Debugging Procedures**

### **Step-by-Step Debugging**

#### **1. Identify the Issue**
```bash
# Check error messages and logs
aws logs get-log-events \
    --log-group-name "/aws/lambda/bos-dev-agent-persona" \
    --log-stream-name "latest" \
    --limit 50
```

#### **2. Reproduce the Issue**
```bash
# Create a test case
python tests/test_debug_issue.py

# Run with verbose output
pytest tests/test_debug_issue.py -v -s
```

#### **3. Analyze the Root Cause**
```bash
# Check system resources
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Average,Maximum,Count
```

#### **4. Implement the Fix**
```bash
# Make necessary changes
# Test the fix
pytest tests/test_fix.py -v

# Deploy the fix
terraform apply -target=aws_lambda_function.agent_persona
```

#### **5. Verify the Fix**
```bash
# Run integration tests
pytest tests/integration/ -v

# Monitor for issues
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Sum
```

---

## 📚 **Additional Resources**

### **Documentation Links**
- **[Setup Guide](../03-setup-guide/setup-guide.md)** - Environment setup
- **[Deployment Guide](../05-deployment-guide/deployment-guide.md)** - Deployment procedures
- **[CLI Commands Reference](../02-cli-commands-reference/cli-commands-reference.md)** - Command reference
- **[Monitoring Strategy](../../04-operations/01-monitoring-strategy/monitoring-strategy.md)** - Monitoring and alerting

### **Support and Help**
- **GitHub Issues:** Create an issue in the repository
- **AWS Support:** Contact AWS support for service issues
- **Community:** Join the project community
- **Emergency:** Contact the DevOps team

### **Useful Commands**

#### **Health Check Commands**
```bash
# Check all Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `bos-dev`)].FunctionName'

# Check API Gateway status
aws apigatewayv2 get-apis --query 'Items[?contains(Name, `bos-dev`)].{Name:Name,Status:ProtocolType}'

# Check DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `bos-dev`)]'

# Check SNS topics
aws sns list-topics --query 'Topics[?contains(TopicArn, `bos-dev`)].TopicArn'
```

#### **Log Analysis Commands**
```bash
# Get recent Lambda logs
aws logs get-log-events \
    --log-group-name "/aws/lambda/bos-dev-agent-persona" \
    --log-stream-name "latest" \
    --limit 100

# Search for errors in logs
aws logs filter-log-events \
    --log-group-name "/aws/lambda/bos-dev-agent-persona" \
    --filter-pattern "ERROR"

# Get CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=bos-dev-agent-persona \
    --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 300 \
    --statistics Sum
```

---

**🎯 Need help? Start with the [Setup Guide](../03-setup-guide/setup-guide.md) and use this troubleshooting guide to resolve issues!**
