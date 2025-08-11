# Safe Infrastructure Refactoring Checklist: BuildingOS Platform

This document provides the **CORRECT and SAFE ORDER** for refactoring BuildingOS infrastructure, with **COMPREHENSIVE ANALYSIS, TESTING, AND APPROVAL STEPS** for each component.

**Architect:** Senior AWS Solutions Architect  
**Status:** Complete Safe Order with Analysis, Testing, and Approval Steps  
**Last Update:** Added missing analysis, explanation, and approval steps (2025-08-11)  
**Methodology:** Analyze → Explain → Test → Approve → Continue

---

## 🎯 **COMPLETE STEP METHODOLOGY**

### **4-Phase Approach for Each Step**
1. **🔍 ANALYSIS** - Deep dive into code and configuration (global to detailed)
2. **📋 EXPLANATION** - Explain structure, findings, and any corrections needed
3. **🧪 TESTING** - Execute comprehensive tests with clear pass/fail criteria
4. **✅ APPROVAL** - Get explicit authorization before proceeding to next step

### **Analysis Depth Levels**
- **Global Level** - Overall architecture and patterns
- **Module Level** - Terraform modules and their usage
- **Resource Level** - Individual AWS resources and configurations
- **Code Level** - Application code dependencies and integrations

---

## 🔧 **PHASE 1: FOUNDATION VALIDATION (LOW RISK)**

### **Step 1.1: Networking & VPC Analysis & Validation** 🟢

**Status:** ⏳ Ready to Start  
**Goal:** Analyze, understand, test, and validate networking foundation

#### **🔍 ANALYSIS PHASE**

**Global Architecture Analysis:**
- [ ] **Action:** Read and analyze `terraform/environments/dev/networking.tf` (545 lines)
- [ ] **Action:** Review VPC design patterns in solution architecture docs
- [ ] **Action:** Analyze dependencies: what services depend on this networking layer
- [ ] **Action:** Check if networking follows global module patterns or is hardcoded
- [ ] **Action:** Review security group rules and Network ACL configurations
- [ ] **Action:** Analyze VPC endpoints - which services need them and why

**Detailed Code Analysis:**
- [ ] **Action:** Examine VPC CIDR block allocation (10.0.0.0/16)
- [ ] **Action:** Analyze subnet design (public/private across 2 AZs)
- [ ] **Action:** Review route table configurations and associations
- [ ] **Action:** Examine NAT Gateway and Internet Gateway setup
- [ ] **Action:** Analyze all 6 VPC endpoints (S3, DynamoDB, Secrets Manager, Lambda, SNS, Bedrock, KMS)
- [ ] **Action:** Review security group rules for lambda, api_gateway, database

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current networking architecture to user
- [ ] **Action:** Document findings: what's correctly implemented vs what needs attention
- [ ] **Action:** Identify any networking configuration issues or improvements needed
- [ ] **Action:** Explain why this networking setup is foundation for everything else
- [ ] **Action:** Present analysis results and recommendations
- [ ] **Approval Required:** User approves analysis findings and testing plan

#### **🧪 TESTING PHASE**

**Connectivity Tests:**
```powershell
# Test 1.1.1: VPC and Subnets Validation
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=bos-dev-main-vpc" --query "Vpcs[0].{VpcId:VpcId,State:State,CidrBlock:CidrBlock}" --output table

# Test 1.1.2: Subnet Configuration Check
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "Subnets[*].{SubnetId:SubnetId,Type:Tags[?Key=='Type'].Value|[0],AZ:AvailabilityZone,CIDR:CidrBlock}" --output table

# Test 1.1.3: Internet Gateway Connectivity
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "InternetGateways[0].{GatewayId:InternetGatewayId,State:Attachments[0].State}" --output table

# Test 1.1.4: NAT Gateway Status
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "NatGateways[*].{NatGatewayId:NatGatewayId,State:State,SubnetId:SubnetId}" --output table

# Test 1.1.5: Route Tables Validation
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "RouteTables[*].{RouteTableId:RouteTableId,Type:Tags[?Key=='Type'].Value|[0],Routes:length(Routes)}" --output table

# Test 1.1.6: Security Groups Validation
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "SecurityGroups[*].{GroupId:GroupId,GroupName:GroupName,InboundRules:length(IpPermissions),OutboundRules:length(IpPermissionsEgress)}" --output table

# Test 1.1.7: VPC Endpoints Connectivity
aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "VpcEndpoints[*].{ServiceName:ServiceName,State:State,VpcEndpointType:VpcEndpointType}" --output table

# Test 1.1.8: Network ACLs Check
aws ec2 describe-network-acls --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-main-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "NetworkAcls[*].{NetworkAclId:NetworkAclId,IsDefault:IsDefault,InboundRules:length(Entries[?Egress==\`false\`]),OutboundRules:length(Entries[?Egress==\`true\`])}" --output table
```

**Pass Criteria:**
- [ ] VPC exists and is in "available" state
- [ ] 2 public subnets and 2 private subnets across different AZs
- [ ] Internet Gateway attached and available
- [ ] NAT Gateway in available state
- [ ] Route tables properly configured (public and private)
- [ ] Security groups exist with appropriate rules
- [ ] All 6 VPC endpoints (S3, DynamoDB, Secrets Manager, Lambda, SNS, Bedrock, KMS) in available state
- [ ] Network ACLs configured correctly

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present test results to user with detailed explanation
- [ ] **Action:** Explain any issues found and proposed corrections
- [ ] **Action:** Document networking foundation status
- [ ] **Approval Required:** User confirms networking foundation is validated and approves proceeding to Step 1.2

---

### **Step 1.2: IAM & Security Foundation Analysis & Validation** 🟢

**Status:** 🟡 Partially Complete - Needs Complete Analysis and Final Validation  
**Goal:** Complete analysis of IAM refactoring and validate security foundation

#### **🔍 ANALYSIS PHASE**

**Global IAM Architecture Analysis:**
- [ ] **Action:** Analyze current state of `terraform/environments/dev/iam.tf` (165 lines)
- [ ] **Action:** Review global IAM role module at `terraform/modules/iam_role/`
- [ ] **Action:** Examine what was changed in the recent refactoring
- [ ] **Action:** Analyze the 4 standalone policies created (DynamoDB, SNS, Bedrock, API Gateway)
- [ ] **Action:** Review IAM role usage across all 10 Lambda functions
- [ ] **Action:** Check for any security improvements or issues

**Code-Level Analysis:**
- [ ] **Action:** Examine policy permissions for least-privilege compliance
- [ ] **Action:** Analyze Bedrock policy - specific model ARNs vs wildcards
- [ ] **Action:** Review DynamoDB policy - table-specific vs broad permissions
- [ ] **Action:** Check SNS policy scope and resource restrictions
- [ ] **Action:** Analyze API Gateway management policy permissions
- [ ] **Action:** Review Lambda execution role assume role policy

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the IAM refactoring that was completed
- [ ] **Action:** Document the before/after comparison of IAM architecture
- [ ] **Action:** Explain why modular IAM role is better than hardcoded approach
- [ ] **Action:** Detail the 4 standalone policies and their specific purposes
- [ ] **Action:** Explain any security improvements achieved
- [ ] **Action:** Present findings and any remaining issues to address
- [ ] **Approval Required:** User approves IAM analysis and testing plan

#### **🧪 TESTING PHASE**

**IAM Security Tests:**
```powershell
# Test 1.2.1: IAM Role Validation
aws iam get-role --role-name bos-dev-lambda-exec-role --query "Role.{RoleName:RoleName,CreateDate:CreateDate,AssumeRolePolicyDocument:AssumeRolePolicyDocument}" --output table

# Test 1.2.2: Attached Policies Check
aws iam list-attached-role-policies --role-name bos-dev-lambda-exec-role --output table

# Test 1.2.3: Custom Policies Validation
aws iam list-policies --scope Local --query "Policies[?starts_with(PolicyName, 'bos-dev-')].{PolicyName:PolicyName,CreateDate:CreateDate,IsAttachable:IsAttachable}" --output table

# Test 1.2.4: Policy Permissions Check
aws iam get-policy --policy-arn $(aws iam list-policies --scope Local --query "Policies[?PolicyName=='bos-dev-bedrock-access-policy'].Arn" --output text) --query "Policy.{PolicyName:PolicyName,Description:Description}"

# Test 1.2.5: Lambda Function IAM Role Assignment
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'bos-dev-')].{FunctionName:FunctionName,Role:Role}" --output table

# Test 1.2.6: Simple Lambda Invocation Test
aws lambda invoke --function-name bos-dev-agent-health-check --payload '{}' response.json && cat response.json && rm response.json

# Test 1.2.7: IAM Permissions Test via Lambda
aws lambda invoke --function-name bos-dev-agent-health-check --log-type Tail --query 'LogResult' --output text | base64 --decode
```

**Pass Criteria:**
- [ ] IAM role `bos-dev-lambda-exec-role` exists and is assumable by Lambda
- [ ] 7 policies attached (3 AWS managed + 4 custom)
- [ ] All 4 custom policies exist and are attachable
- [ ] All 10 Lambda functions use the new IAM role
- [ ] Health check Lambda function invokes successfully
- [ ] No IAM permission errors in CloudWatch logs

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present complete IAM analysis and test results
- [ ] **Action:** Explain current IAM security posture
- [ ] **Action:** Recommend committing current state as "golden baseline"
- [ ] **Action:** Document IAM foundation completion
- [ ] **Approval Required:** User confirms IAM foundation is solid and approves committing changes
- [ ] **Approval Required:** User approves proceeding to Step 1.3

---

### **Step 1.3: Storage Foundation Analysis & Validation** 🟢

**Status:** ⏳ Pending  
**Goal:** Analyze storage infrastructure and validate DynamoDB/S3 configurations

#### **🔍 ANALYSIS PHASE**

**Global Storage Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/dynamodb.tf` (148 lines)
- [ ] **Action:** Review `terraform/environments/dev/frontend.tf` (34 lines)
- [ ] **Action:** Examine storage-related configurations in `security.tf`
- [ ] **Action:** Review global DynamoDB module at `terraform/modules/dynamodb_table/`
- [ ] **Action:** Analyze global S3 website module at `terraform/modules/s3_website/`
- [ ] **Action:** Check application code dependencies on storage services

**Detailed Storage Analysis:**
- [ ] **Action:** Examine 3 DynamoDB tables using global modules (short_term_memory, mission_state, elevator_monitoring)
- [ ] **Action:** Analyze the hardcoded websocket_connections table - why is it not using module?
- [ ] **Action:** Review DynamoDB encryption settings (currently commented out)
- [ ] **Action:** Examine S3 frontend bucket configuration and CloudFront integration
- [ ] **Action:** Analyze CloudTrail S3 bucket setup and lifecycle policies
- [ ] **Action:** Review point-in-time recovery and backup configurations

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current storage architecture to user
- [ ] **Action:** Detail the difference between modular vs hardcoded DynamoDB tables
- [ ] **Action:** Explain why websocket_connections might be hardcoded (simple structure?)
- [ ] **Action:** Present S3 configuration analysis (frontend vs CloudTrail buckets)
- [ ] **Action:** Explain encryption readiness (KMS keys commented out)
- [ ] **Action:** Recommend whether to modularize websocket_connections table or keep as-is
- [ ] **Approval Required:** User approves storage analysis and testing plan

#### **🧪 TESTING PHASE**

**DynamoDB Tests:**
```powershell
# Test 1.3.1: DynamoDB Tables Status
aws dynamodb list-tables --query "TableNames[?starts_with(@, 'bos-dev-')]" --output table

# Test 1.3.2: Table Details Check
aws dynamodb describe-table --table-name bos-dev-short-term-memory --query "Table.{TableName:TableName,TableStatus:TableStatus,ItemCount:ItemCount,TableSizeBytes:TableSizeBytes}" --output table
aws dynamodb describe-table --table-name bos-dev-mission-state --query "Table.{TableName:TableName,TableStatus:TableStatus,ItemCount:ItemCount,TableSizeBytes:TableSizeBytes}" --output table
aws dynamodb describe-table --table-name bos-dev-elevator-monitoring --query "Table.{TableName:TableName,TableStatus:TableStatus,ItemCount:ItemCount,TableSizeBytes:TableSizeBytes}" --output table
aws dynamodb describe-table --table-name bos-dev-websocket-connections --query "Table.{TableName:TableName,TableStatus:TableStatus,ItemCount:ItemCount,TableSizeBytes:TableSizeBytes}" --output table

# Test 1.3.3: DynamoDB Read/Write Test
aws dynamodb put-item --table-name bos-dev-short-term-memory --item '{"session_id":{"S":"test-validation"},"data":{"S":"validation-test"},"ttl":{"N":"'$(date -d '+1 hour' +%s)'"}}' --return-consumed-capacity TOTAL
aws dynamodb get-item --table-name bos-dev-short-term-memory --key '{"session_id":{"S":"test-validation"}}' --query "Item" --output table
aws dynamodb delete-item --table-name bos-dev-short-term-memory --key '{"session_id":{"S":"test-validation"}}'
```

**S3 Storage Tests:**
```powershell
# Test 1.3.4: S3 Buckets Validation
aws s3 ls | grep bos-dev

# Test 1.3.5: Frontend Bucket Test
aws s3 ls s3://buildingos-frontend-dev/ --recursive

# Test 1.3.6: CloudTrail Bucket Test
aws s3 ls s3://$(aws s3 ls | grep bos-dev-cloudtrail | awk '{print $3}') --recursive | head -10

# Test 1.3.7: S3 Bucket Policies Check
aws s3api get-bucket-policy --bucket buildingos-frontend-dev --query Policy --output text | jq .
```

**Pass Criteria:**
- [ ] All 4 DynamoDB tables exist and are in ACTIVE status
- [ ] DynamoDB read/write operations successful
- [ ] Point-in-time recovery enabled where configured
- [ ] Frontend S3 bucket accessible with proper files
- [ ] CloudTrail S3 bucket exists and receiving logs
- [ ] S3 bucket policies properly configured

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present storage analysis and test results
- [ ] **Action:** Explain any storage configuration issues found
- [ ] **Action:** Present recommendation on websocket_connections table approach
- [ ] **Action:** Document storage foundation status
- [ ] **Approval Required:** User confirms storage foundation is validated and approves proceeding to Step 1.4

---

### **Step 1.4: Basic Monitoring Foundation Analysis & Validation** 🟢

**Status:** ⏳ Pending  
**Goal:** Analyze monitoring infrastructure and validate observability setup

#### **🔍 ANALYSIS PHASE**

**Global Monitoring Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/monitoring.tf` (361 lines)
- [ ] **Action:** Review `terraform/environments/dev/compliance.tf` (257 lines)
- [ ] **Action:** Examine `terraform/environments/dev/performance.tf` (299 lines)
- [ ] **Action:** Check CloudWatch dashboard configurations
- [ ] **Action:** Review alarm thresholds and notification settings
- [ ] **Action:** Analyze log retention policies and log group structures

**Detailed Monitoring Analysis:**
- [ ] **Action:** Examine CloudWatch log groups for all Lambda functions
- [ ] **Action:** Review the 8 different CloudWatch alarms and their thresholds
- [ ] **Action:** Analyze SNS alerts topic and email subscription setup
- [ ] **Action:** Review the 3 dashboards (main, performance, compliance)
- [ ] **Action:** Check X-Ray tracing configuration
- [ ] **Action:** Examine log aggregation and structured logging patterns

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current monitoring and observability architecture
- [ ] **Action:** Detail the monitoring coverage across all infrastructure components
- [ ] **Action:** Explain alarm thresholds and their business impact
- [ ] **Action:** Present dashboard organization and metrics covered
- [ ] **Action:** Explain log retention policies and cost implications
- [ ] **Action:** Identify any monitoring gaps or improvements needed
- [ ] **Approval Required:** User approves monitoring analysis and testing plan

#### **🧪 TESTING PHASE**

**CloudWatch Tests:**
```powershell
# Test 1.4.1: Log Groups Validation
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bos-dev-" --query "logGroups[*].{LogGroupName:logGroupName,RetentionInDays:retentionInDays,StoredBytes:storedBytes}" --output table

# Test 1.4.2: CloudWatch Dashboards Check
aws cloudwatch list-dashboards --query "DashboardEntries[?starts_with(DashboardName, 'bos-dev-')]" --output table

# Test 1.4.3: CloudWatch Alarms Status
aws cloudwatch describe-alarms --alarm-name-prefix "bos-dev-" --query "MetricAlarms[*].{AlarmName:AlarmName,StateValue:StateValue,ActionsEnabled:ActionsEnabled}" --output table

# Test 1.4.4: SNS Topics for Alerts
aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-alerts')]" --output table

# Test 1.4.5: Test Log Generation
aws lambda invoke --function-name bos-dev-agent-health-check --payload '{}' response.json
aws logs filter-log-events --log-group-name "/aws/lambda/bos-dev-agent-health-check" --start-time $(date -d '5 minutes ago' +%s)000 --query "events[*].message" --output text

# Test 1.4.6: CloudWatch Metrics Test
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations --dimensions Name=FunctionName,Value=bos-dev-agent-health-check --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Sum --output table

# Test 1.4.7: Dashboard Content Validation
aws cloudwatch get-dashboard --dashboard-name bos-dev-monitoring --query "DashboardBody" --output text | jq .widgets[0]
```

**Pass Criteria:**
- [ ] All Lambda log groups exist with proper retention policies
- [ ] 3 CloudWatch dashboards exist and accessible
- [ ] All CloudWatch alarms configured and enabled
- [ ] SNS alerts topic exists and configured
- [ ] Log events generated and captured correctly
- [ ] CloudWatch metrics collected for Lambda functions
- [ ] Dashboard widgets display data correctly

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present monitoring analysis and test results
- [ ] **Action:** Explain monitoring coverage and any gaps identified
- [ ] **Action:** Document monitoring foundation status
- [ ] **Approval Required:** User confirms monitoring foundation is validated and approves proceeding to Phase 2

---

## 🏗️ **PHASE 2: CORE SERVICES VALIDATION (MEDIUM RISK)**

### **Step 2.1: Messaging Infrastructure (SNS) Analysis & Validation** 🟡

**Status:** ⏳ Pending  
**Goal:** Analyze SNS architecture and validate inter-agent communication

#### **🔍 ANALYSIS PHASE**

**Global SNS Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/sns.tf` (126 lines)
- [ ] **Action:** Review global SNS topic module at `terraform/modules/sns_topic/`
- [ ] **Action:** Examine application code to understand SNS usage patterns
- [ ] **Action:** Map the complete SNS communication flow between agents
- [ ] **Action:** Review SNS topic naming conventions and consistency
- [ ] **Action:** Check SNS subscription configurations and dead letter queues

**Agent Communication Flow Analysis:**
- [ ] **Action:** Trace persona → director → coordinator → agent communication flow
- [ ] **Action:** Examine SNS topic subscriptions in Lambda function configurations
- [ ] **Action:** Review SNS message formats and payload structures
- [ ] **Action:** Analyze error handling and retry mechanisms
- [ ] **Action:** Check SNS topic policies and access controls
- [ ] **Action:** Review SNS encryption settings (currently using default)

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the complete SNS-based communication architecture
- [ ] **Action:** Detail the 8 SNS topics and their specific roles in agent communication
- [ ] **Action:** Map out the message flow from user input to final response
- [ ] **Action:** Explain why SNS was chosen over direct Lambda invocation
- [ ] **Action:** Present any SNS configuration issues or improvements needed
- [ ] **Approval Required:** User approves SNS analysis and testing plan

#### **🧪 TESTING PHASE**

**SNS Configuration Tests:**
```powershell
# Test 2.1.1: SNS Topics Validation
aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-')]" --output table

# Test 2.1.2: Topic Subscriptions Check
aws sns list-subscriptions --query "Subscriptions[?contains(TopicArn, 'bos-dev-')].{TopicArn:TopicArn,Protocol:Protocol,Endpoint:Endpoint,SubscriptionArn:SubscriptionArn}" --output table

# Test 2.1.3: Topic Attributes Validation
aws sns get-topic-attributes --topic-arn $(aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-persona-intention-topic')].TopicArn" --output text) --query "Attributes" --output table
```

**Message Flow Tests:**
```powershell
# Test 2.1.4: SNS Message Publishing Test
aws sns publish --topic-arn $(aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-persona-intention-topic')].TopicArn" --output text) --message '{"test":"validation","timestamp":"'$(date --iso-8601)'"}'

# Test 2.1.5: Lambda Subscription Trigger Test
# Monitor CloudWatch logs for message processing
aws logs filter-log-events --log-group-name "/aws/lambda/bos-dev-agent-director" --start-time $(date -d '2 minutes ago' +%s)000 --query "events[*].message" --output text | grep -i "sns\|message\|event"

# Test 2.1.6: Complete Message Flow Test
# This will be done using the API testing suite
cd tests/api && python -c "
import requests
import json
response = requests.post('https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/dev/persona', 
    json={'user_id': 'test-sns-validation', 'message': 'Test SNS message flow'},
    headers={'Content-Type': 'application/json'})
print(f'Status: {response.status_code}, Response: {response.text}')
"
```

**Pass Criteria:**
- [ ] All 8 SNS topics exist and are accessible
- [ ] Lambda functions properly subscribed to topics
- [ ] Topic attributes configured correctly
- [ ] SNS message publishing successful
- [ ] Lambda functions triggered by SNS messages
- [ ] Complete persona → director message flow working

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present SNS analysis and test results
- [ ] **Action:** Explain inter-agent communication health
- [ ] **Action:** Document messaging infrastructure status
- [ ] **Approval Required:** User confirms SNS infrastructure is validated and approves proceeding to Step 2.2

---

### **Step 2.2: Compute Infrastructure (Lambda) Analysis & Validation** 🟡

**Status:** ⏳ Pending  
**Goal:** Analyze all Lambda functions and layer

#### **🔍 ANALYSIS PHASE**

**Global Lambda Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/lambda.tf` (400 lines)
- [ ] **Action:** Review global Lambda layer module at `terraform/modules/lambda_layer/`
- [ ] **Action:** Examine application code dependencies on Lambda functions
- [ ] **Action:** Review Lambda function configurations and VPC settings
- [ ] **Action:** Analyze Lambda function naming conventions and consistency
- [ ] **Action:** Check Lambda execution role assume role policy

**Detailed Lambda Analysis:**
- [ ] **Action:** Examine 10 Lambda functions using global modules (agent_health_check, agent_persona, agent_director)
- [ ] **Action:** Analyze the 3 standalone Lambda functions (websocket_connections, bedrock_lambda, api_gateway_lambda)
- [ ] **Action:** Review Lambda layer usage and dependencies
- [ ] **Action:** Check Lambda function VPC configurations
- [ ] **Action:** Analyze Lambda function timeout and memory settings
- [ ] **Action:** Review Lambda function error handling and logging

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current Lambda architecture to user
- [ ] **Action:** Detail the difference between modular vs hardcoded Lambda functions
- [ ] **Action:** Explain why some functions might be hardcoded (simple structure?)
- [ ] **Action:** Present Lambda layer analysis (agent_health_check, agent_persona, agent_director)
- [ ] **Action:** Explain Lambda function VPC requirements
- [ ] **Action:** Recommend whether to modularize hardcoded functions or keep as-is
- [ ] **Approval Required:** User approves Lambda analysis and testing plan

#### **🧪 TESTING PHASE**

**Lambda Function Tests:**
```powershell
# Test 2.2.1: Lambda Functions Status
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'bos-dev-')].{FunctionName:FunctionName,State:State,Runtime:Runtime,MemorySize:MemorySize,Timeout:Timeout}" --output table

# Test 2.2.2: Lambda Layer Validation
aws lambda list-layers --query "Layers[?starts_with(LayerName, 'bos-dev-')]" --output table

# Test 2.2.3: Individual Function Testing
aws lambda invoke --function-name bos-dev-agent-health-check --payload '{}' health_response.json && cat health_response.json
aws lambda invoke --function-name bos-dev-agent-persona --payload '{"user_id":"test","message":"health check"}' persona_response.json && cat persona_response.json
aws lambda invoke --function-name bos-dev-agent-director --payload '{"test":"validation"}' director_response.json && cat director_response.json
```

**Performance Tests:**
```powershell
# Test 2.2.4: Lambda Performance Metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Duration --dimensions Name=FunctionName,Value=bos-dev-agent-persona --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Average,Maximum --output table

# Test 2.2.5: Lambda Error Rates
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Errors --dimensions Name=FunctionName,Value=bos-dev-agent-persona --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Sum --output table

# Test 2.2.6: Concurrent Execution Test
# Use API testing suite for concurrent testing
cd tests/api && python run_tests.py performance
```

**VPC and Layer Tests:**
```powershell
# Test 2.2.7: VPC Configuration Check
aws lambda get-function-configuration --function-name bos-dev-agent-persona --query "VpcConfig" --output table

# Test 2.2.8: Lambda Layer Usage Validation
aws lambda get-function --function-name bos-dev-agent-persona --query "Configuration.Layers" --output table
```

**Pass Criteria:**
- [ ] All 10 Lambda functions in Active state
- [ ] Lambda layer exists and is attached to functions
- [ ] Individual function invocations successful
- [ ] Performance metrics within acceptable ranges
- [ ] Error rates at acceptable levels
- [ ] VPC configuration correct for functions that need it
- [ ] Concurrent execution tests pass

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present Lambda analysis and test results
- [ ] **Action:** Explain Lambda function health and performance
- [ ] **Action:** Document Lambda foundation status
- [ ] **Approval Required:** User confirms Lambda foundation is validated and approves proceeding to Step 2.3

---

### **Step 2.3: API Gateway Infrastructure Analysis & Validation** 🟡

**Status:** ⏳ Pending  
**Goal:** Analyze API Gateway functionality

#### **🔍 ANALYSIS PHASE**

**Global API Gateway Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/api_gateway.tf` (150 lines)
- [ ] **Action:** Review global API Gateway module at `terraform/modules/api_gateway/`
- [ ] **Action:** Examine application code dependencies on API Gateway
- [ ] **Action:** Review API Gateway configuration and route selection expressions
- [ ] **Action:** Analyze API Gateway naming conventions and consistency
- [ ] **Action:** Check API Gateway stage and deployment settings

**Detailed API Gateway Analysis:**
- [ ] **Action:** Examine HTTP API and WebSocket API configurations
- [ ] **Action:** Review route configurations (health, persona, director, websocket)
- [ ] **Action:** Analyze CORS configuration and origins
- [ ] **Action:** Check API Gateway stage deployment status
- [ ] **Action:** Review API Gateway logging and monitoring settings

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current API Gateway architecture to user
- [ ] **Action:** Detail the difference between HTTP API and WebSocket API
- [ ] **Action:** Explain CORS configuration and its importance
- [ ] **Action:** Present API Gateway route analysis (health, persona, director, websocket)
- [ ] **Action:** Explain API Gateway stage deployment and monitoring
- [ ] **Approval Required:** User approves API Gateway analysis and testing plan

#### **🧪 TESTING PHASE**

**API Gateway Tests:**
```powershell
# Test 2.3.1: API Gateway Status
aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-')].{ApiId:ApiId,Name:Name,ProtocolType:ProtocolType,RouteSelectionExpression:RouteSelectionExpression}" --output table

# Test 2.3.2: HTTP API Routes Validation
aws apigatewayv2 get-routes --api-id $(aws apigatewayv2 get-apis --query "Items[?contains(Name, 'http-api')].ApiId" --output text) --query "Items[*].{RouteKey:RouteKey,Target:Target}" --output table

# Test 2.3.3: WebSocket API Routes Validation
aws apigatewayv2 get-routes --api-id $(aws apigatewayv2 get-apis --query "Items[?contains(Name, 'websocket')].ApiId" --output text) --query "Items[*].{RouteKey:RouteKey,Target:Target}" --output table

# Test 2.3.4: API Gateway Stages Check
aws apigatewayv2 get-stages --api-id $(aws apigatewayv2 get-apis --query "Items[?contains(Name, 'http-api')].ApiId" --output text) --query "Items[*].{StageName:StageName,DeploymentId:DeploymentId,CreatedDate:CreatedDate}" --output table
```

**API Functionality Tests:**
```powershell
# Test 2.3.5: HTTP API Endpoints Testing
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/dev/health" -H "Content-Type: application/json"

# Test 2.3.6: CORS Configuration Test
curl -X OPTIONS "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/dev/health" -H "Origin: http://localhost" -v

# Test 2.3.7: Complete API Testing Suite
cd tests/api && python run_tests.py endpoints
```

**WebSocket Tests:**
```powershell
# Test 2.3.8: WebSocket API Connection Test
# This requires the frontend or a WebSocket client
# We'll use the existing test infrastructure
cd tests/api && python -c "
import websocket
import json
ws_url = 'wss://u00zcixboc.execute-api.us-east-1.amazonaws.com/dev'
try:
    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({'action': 'test', 'message': 'validation'}))
    result = ws.recv()
    print(f'WebSocket test result: {result}')
    ws.close()
    print('WebSocket connection successful')
except Exception as e:
    print(f'WebSocket test failed: {e}')
"
```

**Pass Criteria:**
- [ ] HTTP API and WebSocket API exist and are accessible
- [ ] All API routes properly configured and working
- [ ] API stages deployed correctly
- [ ] HTTP endpoints respond correctly
- [ ] CORS configuration working
- [ ] Complete API test suite passes
- [ ] WebSocket connections successful

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present API Gateway analysis and test results
- [ ] **Action:** Explain API Gateway health and functionality
- [ ] **Action:** Document API Gateway foundation status
- [ ] **Approval Required:** User confirms API Gateway foundation is validated and approves proceeding to Phase 3

---

## 🔴 **PHASE 3: INTEGRATION SERVICES (HIGH RISK)**

### **Step 3.1: Frontend Integration Analysis & Validation** 🔴

**Status:** ⏳ Pending  
**Goal:** Analyze frontend and CDN functionality

#### **🔍 ANALYSIS PHASE**

**Global Frontend Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/frontend.tf` (34 lines)
- [ ] **Action:** Review global CloudFront module at `terraform/modules/cloudfront/`
- [ ] **Action:** Examine application code dependencies on CloudFront
- [ ] **Action:** Review CloudFront distribution configurations and origins
- [ ] **Action:** Analyze CloudFront naming conventions and consistency
- [ ] **Action:** Check CloudFront SSL certificate and security policies

**Detailed Frontend Analysis:**
- [ ] **Action:** Examine CloudFront distribution status and enabled state
- [ ] **Action:** Review S3 website configuration and bucket policies
- [ ] **Action:** Analyze frontend file accessibility and caching
- [ ] **Action:** Check CloudFront to S3 origin setup
- [ ] **Action:** Review CORS configuration for frontend access

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current frontend and CDN architecture to user
- [ ] **Action:** Detail the difference between CloudFront and direct S3 access
- [ ] **Action:** Explain CORS configuration and its importance
- [ ] **Action:** Present CloudFront configuration analysis (distribution, origins, SSL)
- [ ] **Action:** Explain frontend file accessibility and caching
- [ ] **Approval Required:** User approves frontend analysis and testing plan

#### **🧪 TESTING PHASE**

**Frontend Tests:**
```powershell
# Test 3.1.1: CloudFront Distribution Status
aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'buildingos')].{Id:Id,DomainName:DomainName,Status:Status,Enabled:Enabled}" --output table

# Test 3.1.2: S3 Website Configuration
aws s3api get-bucket-website --bucket buildingos-frontend-dev --output table

# Test 3.1.3: Frontend File Accessibility
curl -I "https://$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'buildingos')].DomainName" --output text)/index.html"
curl -I "https://$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'buildingos')].DomainName" --output text)/chat.html"

# Test 3.1.4: Direct S3 Website Test
curl -I "http://buildingos-frontend-dev.s3-website-us-east-1.amazonaws.com/index.html"
```

**Frontend Integration Tests:**
```powershell
# Test 3.1.5: Frontend to API Integration
# Test if frontend can reach API endpoints
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/dev/health" -H "Origin: https://$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'buildingos')].DomainName" --output text)" -v

# Test 3.1.6: WebSocket Integration from Frontend
# This will be tested using browser automation or manual verification
echo "Manual Test Required: Open https://$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'buildingos')].DomainName" --output text)/chat.html and test WebSocket connectivity"
```

**Pass Criteria:**
- [ ] CloudFront distribution active and enabled
- [ ] S3 website configuration correct
- [ ] Frontend files accessible via CloudFront
- [ ] Direct S3 website access working
- [ ] Frontend can reach API endpoints with CORS
- [ ] WebSocket integration working from frontend

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present frontend analysis and test results
- [ ] **Action:** Explain frontend functionality and reliability
- [ ] **Action:** Document frontend foundation status
- [ ] **Approval Required:** User confirms frontend foundation is validated and approves proceeding to Step 3.2

---

### **Step 3.2: Bedrock AI Integration Analysis & Validation** 🔴

**Status:** ⏳ Pending  
**Goal:** Analyze Bedrock AI integration

#### **🔍 ANALYSIS PHASE**

**Global Bedrock Architecture Analysis:**
- [ ] **Action:** Analyze `terraform/environments/dev/bedrock.tf` (100 lines)
- [ ] **Action:** Review global Bedrock module at `terraform/modules/bedrock/`
- [ ] **Action:** Examine application code dependencies on Bedrock
- [ ] **Action:** Review Bedrock service availability and model configurations
- [ ] **Action:** Analyze VPC endpoint for Bedrock and its configuration
- [ ] **Action:** Check IAM permissions for Bedrock access

**Detailed Bedrock Analysis:**
- [ ] **Action:** Examine Bedrock foundation models and their availability
- [ ] **Action:** Review VPC endpoint for Bedrock and its state
- [ ] **Action:** Analyze IAM permissions for Bedrock access
- [ ] **Action:** Check direct Bedrock model invocation and response
- [ ] **Action:** Review Lambda function invocation of Bedrock models
- [ ] **Action:** Analyze end-to-end flow with Bedrock
- [ ] **Action:** Check Bedrock response times and costs

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain current Bedrock AI integration architecture
- [ ] **Action:** Detail the difference between direct invocation and Lambda-based invocation
- [ ] **Action:** Explain why modular Bedrock module is better than direct invocation
- [ ] **Action:** Present Bedrock configuration analysis (models, VPC endpoint, IAM)
- [ ] **Action:** Explain Bedrock response times and costs
- [ ] **Approval Required:** User approves Bedrock analysis and testing plan

#### **🧪 TESTING PHASE**

**Bedrock Configuration Tests:**
```powershell
# Test 3.2.1: Bedrock Service Availability
aws bedrock list-foundation-models --query "modelSummaries[?contains(modelId, 'anthropic.claude')].{ModelId:modelId,ModelName:modelName,ProviderName:providerName}" --output table

# Test 3.2.2: VPC Endpoint for Bedrock
aws ec2 describe-vpc-endpoints --filters "Name=service-name,Values=com.amazonaws.us-east-1.bedrock-runtime" --query "VpcEndpoints[*].{VpcEndpointId:VpcEndpointId,State:State,VpcId:VpcId}" --output table

# Test 3.2.3: IAM Permissions for Bedrock
aws iam get-policy-version --policy-arn $(aws iam list-policies --scope Local --query "Policies[?PolicyName=='bos-dev-bedrock-access-policy'].Arn" --output text) --version-id v1 --query "PolicyVersion.Document" --output json | jq .Statement[0]
```

**Bedrock Functionality Tests:**
```powershell
# Test 3.2.4: Direct Bedrock Model Invocation Test
aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
    --body '{"anthropic_version": "bedrock-2023-05-31", "max_tokens": 100, "messages": [{"role": "user", "content": "Hello, this is a test"}]}' \
    --content-type application/json \
    bedrock_test_response.json && cat bedrock_test_response.json | jq .content[0].text

# Test 3.2.5: Bedrock via Lambda (Agent Director)
aws lambda invoke --function-name bos-dev-agent-director --payload '{"Records":[{"EventSource":"aws:sns","Sns":{"Message":"{\"session_id\":\"test-bedrock\",\"user_id\":\"test\",\"intention\":\"Test Bedrock integration\",\"context\":{}}"}}]}' bedrock_lambda_response.json && cat bedrock_lambda_response.json

# Test 3.2.6: End-to-End Bedrock Flow Test
cd tests/api && python -c "
import requests
import json
import time

# Send message that should trigger Bedrock
response = requests.post('https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/dev/persona', 
    json={'user_id': 'test-bedrock-flow', 'message': 'Please help me understand how elevators work'},
    headers={'Content-Type': 'application/json'})
print(f'Persona response: {response.status_code} - {response.text}')

# Wait and check if director processed with Bedrock
time.sleep(5)
print('Check CloudWatch logs for Bedrock invocation in agent-director')
"
```

**Bedrock Performance Tests:**
```powershell
# Test 3.2.7: Bedrock Response Time Monitoring
aws logs filter-log-events --log-group-name "/aws/lambda/bos-dev-agent-director" --start-time $(date -d '10 minutes ago' +%s)000 --filter-pattern "bedrock" --query "events[*].message" --output text

# Test 3.2.8: Bedrock Cost Monitoring
aws ce get-cost-and-usage --time-period Start=$(date -d '1 day ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity DAILY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE --filter file://<(echo '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Bedrock"]}}') --query "ResultsByTime[*].Groups[*]" --output table
```

**Pass Criteria:**
- [ ] Bedrock foundation models accessible
- [ ] VPC endpoint for Bedrock in available state
- [ ] IAM permissions correctly configured for Bedrock
- [ ] Direct Bedrock model invocation successful
- [ ] Lambda function can invoke Bedrock models
- [ ] End-to-end flow with Bedrock working
- [ ] Bedrock response times acceptable
- [ ] Bedrock costs within expected range

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present Bedrock analysis and test results
- [ ] **Action:** Explain Bedrock AI integration health
- [ ] **Action:** Document Bedrock foundation status
- [ ] **Approval Required:** User confirms Bedrock foundation is validated and approves proceeding to Step 3.3

---

### **Step 3.3: End-to-End Application Flow Analysis & Validation** 🔴

**Status:** ⏳ Pending  
**Goal:** Analyze complete application functionality

#### **🔄 Complete Flow Tests**
```powershell
# Test 3.3.1: Complete API Test Suite
cd tests/api && python run_tests.py all

# Test 3.3.2: Performance Test Suite
cd tests/api && python run_tests.py performance

# Test 3.3.3: Rapid Diagnosis
cd tests/api && python diagnose_api.py
```

**System Integration Tests:**
```powershell
# Test 3.3.4: Multi-Agent Communication Flow
cd tests/api && python -c "
import requests
import json
import time

# Test complete persona -> director -> coordinator -> elevator flow
test_payload = {
    'user_id': 'test-complete-flow',
    'message': 'Call elevator to floor 5 please'
}

print('Testing complete agent communication flow...')
response = requests.post('https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/dev/persona', 
    json=test_payload, headers={'Content-Type': 'application/json'})
print(f'Initial response: {response.status_code} - {response.text}')

# Wait for processing
time.sleep(10)
print('Flow initiated. Check CloudWatch logs for complete processing chain.')
"

# Test 3.3.5: Data Persistence Validation
aws dynamodb scan --table-name bos-dev-short-term-memory --limit 5 --query "Items[*]" --output table
aws dynamodb scan --table-name bos-dev-mission-state --limit 5 --query "Items[*]" --output table
```

**System Health Check:**
```powershell
# Test 3.3.6: Overall System Health
echo "=== SYSTEM HEALTH CHECK ===" 
echo "Lambda Functions:"
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'bos-dev-')].{Name:FunctionName,State:State}" --output table

echo "DynamoDB Tables:"
aws dynamodb list-tables --query "TableNames[?starts_with(@, 'bos-dev-')]" | jq -r '.[]' | xargs -I {} aws dynamodb describe-table --table-name {} --query "Table.{Name:TableName,Status:TableStatus}" --output table

echo "SNS Topics:"
aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-')]" --output table

echo "API Gateway:"
aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-')].{Name:Name,Status:'Active'}" --output table

# Test 3.3.7: Error Rate Analysis
aws logs filter-log-events --log-group-name "/aws/lambda/bos-dev-agent-persona" --start-time $(date -d '1 hour ago' +%s)000 --filter-pattern "ERROR" --query "events[*].message" --output text
```

**Pass Criteria:**
- [ ] Complete API test suite passes (24 test cases)
- [ ] Performance tests within acceptable ranges
- [ ] Rapid diagnosis shows no critical issues
- [ ] Multi-agent communication flow working
- [ ] Data persistence across all tables working
- [ ] Overall system health check passes
- [ ] Error rates at acceptable levels across all components

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present end-to-end analysis and test results
- [ ] **Action:** Explain complete application functionality
- [ ] **Action:** Document application foundation status
- [ ] **Approval Required:** User confirms application foundation is validated and approves proceeding to Phase 4

---

## 📊 **STEP COMPLETION TRACKING**

### **Current Status**
- **Phase 1, Step 1.1:** ⏳ Ready to begin analysis
- **All other steps:** ⏳ Awaiting completion of prerequisite steps

### **Next Action Required**
**Begin Step 1.1 Analysis Phase** - Deep dive into networking.tf and VPC architecture

**Do I have your authorization to begin Step 1.1: Networking & VPC Analysis Phase?**

---

## 🚨 **CRITICAL SUCCESS FACTORS**

1. **Never Skip Analysis** - Always understand before testing
2. **Always Explain Findings** - User must understand what was found
3. **Get Explicit Approval** - Never proceed without user authorization
4. **Document Everything** - Keep detailed records of analysis and decisions
5. **Test Thoroughly** - All tests must pass before proceeding
6. **Maintain Safe Order** - Never skip to dependent components
