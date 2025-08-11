# Clean Infrastructure Rebuild Checklist: BuildingOS Platform

This document provides the **SAFE ORDER** for rebuilding BuildingOS infrastructure from scratch, with **COMPREHENSIVE ANALYSIS, TESTING, AND APPROVAL STEPS** for each component.

**Architect:** Senior AWS Solutions Architect  
**Status:** Clean Rebuild Strategy - Ready to Execute  
**Last Update:** Updated for clean rebuild approach (2025-08-11)  
**Methodology:** Analyze → Build → Test → Approve → Continue

---

## 🎯 **CLEAN REBUILD METHODOLOGY**

### **🌍 CRITICAL: GLOBAL ANALYSIS REQUIREMENT**

**⚠️ MANDATORY FOR EVERY STEP:** All analysis MUST start from the global `building-os-platform` directory and perform comprehensive dependency checking:

1. **📁 Global Directory Analysis:**
   - Start analysis from root: `C:\Projects\building-os-platform`
   - Review complete project structure and interdependencies
   - Check all modules in `terraform/modules/` for reusability
   - Analyze global configurations (`terraform/providers.tf`, `terraform/versions.tf`)

2. **🔍 Deep Code Analysis:**
   - Examine `src/` directory for application requirements
   - Review `frontend/` for deployment dependencies  
   - Check `tests/` for validation requirements
   - Analyze `docs/` for architectural requirements and constraints

3. **🔗 Dependency Mapping:**
   - Map all terraform module dependencies
   - Identify application code dependencies on infrastructure
   - Check environment-specific configurations (`dev/`, `stg/`, `prd/`)
   - Verify compliance and security requirements from documentation

### **4-Phase Approach for Each Step**
1. **🔍 ANALYSIS** - Analyze current code and requirements (preserve application logic)
2. **🏗️ BUILD CLEAN** - Build infrastructure with best practices from day 1
3. **🧪 TESTING** - Execute comprehensive tests with clear pass/fail criteria
4. **✅ APPROVAL** - Get explicit authorization before proceeding to next step

### **Code Preservation Strategy**
- **✅ PRESERVE:** All application code (`src/`, `frontend/`, `tests/`, `docs/`)
- **🔥 REBUILD:** Only AWS infrastructure (Lambda deployments, DynamoDB, VPC, etc.)
- **🚀 IMPROVE:** Apply best practices from start (VPC-enabled, clean IAM, proper modules)

### **Key Differences from Refactoring**
- **No "TEMPORARILY DISABLED"** configurations
- **VPC-enabled Lambda functions** from day 1
- **Clean IAM roles** with proper KMS permissions from start
- **Consistent module usage** throughout
- **No hidden configuration issues**

---

## 🔧 **PHASE 1: FOUNDATION LAYER (CLEAN BUILD)**

### **Step 1.1: Networking & VPC Clean Build** 🟢

**Status:** ⏳ Ready to Start  
**Goal:** Build networking foundation with best practices from day 1

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all networking dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current Architecture Review:**
- [ ] **Action:** Review existing `terraform/environments/dev/networking.tf` design patterns
- [ ] **Action:** Analyze what worked well (VPC endpoints, multi-AZ design, CIDR allocation)
- [ ] **Action:** Identify improvements needed (no temporary disables, consistent tagging)
- [ ] **Action:** Review application code networking requirements (`src/` directory)
- [ ] **Action:** Plan VPC-enabled Lambda deployment from start
- [ ] **Action:** Design security group rules for clean implementation

**Clean Build Planning:**
- [ ] **Action:** Plan VPC with same excellent CIDR design (10.0.0.0/16)
- [ ] **Action:** Design all 7 VPC endpoints (S3, DynamoDB, SNS, Bedrock, Lambda, Secrets, KMS)
- [ ] **Action:** Plan security groups for Lambda VPC integration
- [ ] **Action:** Design Network ACLs with appropriate rules
- [ ] **Action:** Plan NAT Gateway and Internet Gateway setup

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the clean networking architecture design
- [ ] **Action:** Detail improvements over previous implementation
- [ ] **Action:** Explain why VPC endpoints are critical for cost optimization
- [ ] **Action:** Present security improvements and best practices
- [ ] **Action:** Explain Lambda VPC integration strategy
- [ ] **Approval Required:** User approves networking design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**Infrastructure Creation:**
```bash
# Build clean networking foundation
terraform apply -target=aws_vpc.main
terraform apply -target=aws_subnet.public
terraform apply -target=aws_subnet.private
terraform apply -target=aws_internet_gateway.main
terraform apply -target=aws_nat_gateway.main
terraform apply -target=aws_vpc_endpoint.s3
terraform apply -target=aws_vpc_endpoint.dynamodb
terraform apply -target=aws_vpc_endpoint.bedrock
# ... all VPC endpoints
```

#### **🧪 TESTING PHASE**

**Connectivity Tests:**
```powershell
# Test 1.1.1: VPC and Subnets Validation
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=bos-dev-vpc" --query "Vpcs[0].{VpcId:VpcId,State:State,CidrBlock:CidrBlock}" --output table

# Test 1.1.2: Subnet Configuration Check
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "Subnets[*].{SubnetId:SubnetId,Type:Tags[?Key=='Type'].Value|[0],AZ:AvailabilityZone,CIDR:CidrBlock,MapPublicIP:MapPublicIpOnLaunch}" --output table

# Test 1.1.3: Internet Gateway Connectivity
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "InternetGateways[0].{GatewayId:InternetGatewayId,State:Attachments[0].State}" --output table

# Test 1.1.4: NAT Gateway Status
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "NatGateways[*].{NatGatewayId:NatGatewayId,State:State,SubnetId:SubnetId}" --output table

# Test 1.1.5: Route Tables Validation
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "RouteTables[*].{RouteTableId:RouteTableId,Type:Tags[?Key=='Type'].Value|[0],Routes:length(Routes)}" --output table

# Test 1.1.6: Security Groups Validation
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "SecurityGroups[*].{GroupId:GroupId,GroupName:GroupName,InboundRules:length(IpPermissions),OutboundRules:length(IpPermissionsEgress)}" --output table

# Test 1.1.7: VPC Endpoints Connectivity
aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "VpcEndpoints[*].{ServiceName:ServiceName,State:State,VpcEndpointType:VpcEndpointType}" --output table

# Test 1.1.8: Network ACLs Check
aws ec2 describe-network-acls --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=bos-dev-vpc' --query 'Vpcs[0].VpcId' --output text)" --query "NetworkAcls[*].{NetworkAclId:NetworkAclId,IsDefault:IsDefault,Entries:length(Entries)}" --output table
```

**Pass Criteria:**
- [ ] VPC exists and is in "available" state
- [ ] 2 public subnets and 2 private subnets across different AZs
- [ ] Internet Gateway attached and available
- [ ] NAT Gateway in available state
- [ ] Route tables properly configured (public and private)
- [ ] Security groups exist with appropriate rules for Lambda VPC integration
- [ ] All 7 VPC endpoints (S3, DynamoDB, Secrets Manager, Lambda, SNS, Bedrock, KMS) in available state
- [ ] Network ACLs configured correctly

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/networking.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed resource descriptions explaining purpose and configuration
- [ ] **Action:** Document variable usage and output purposes
- [ ] **Action:** Add inline comments explaining complex networking logic
- [ ] **Action:** Ensure all resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the networking architecture
- [ ] **Action:** Document security group rules and their purposes
- [ ] **Action:** Add comments explaining VPC endpoint configurations
- [ ] **Action:** Review and update any hardcoded values with explanatory comments

**Documentation Quality Check:**
- [ ] All Terraform resources have clear English descriptions
- [ ] Complex configurations include explanatory comments
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean networking build results with detailed explanation
- [ ] **Action:** Explain improvements over previous implementation
- [ ] **Action:** Document clean networking foundation status
- [ ] **Approval Required:** User confirms clean networking foundation is built correctly and approves proceeding to Step 1.2

---

### **Step 1.2: IAM & Security Clean Build** 🟢

**Status:** ⏳ Pending  
**Goal:** Build clean IAM roles with proper permissions from day 1 (no KMS access issues)

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all IAM dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current IAM Review:**
- [ ] **Action:** Review previous IAM refactoring work (modular approach was correct)
- [ ] **Action:** Analyze KMS permission requirements for Lambda functions
- [ ] **Action:** Review the 4 standalone policies (DynamoDB, SNS, Bedrock, API Gateway)
- [ ] **Action:** Plan clean IAM architecture with proper KMS permissions from start
- [ ] **Action:** Design least-privilege policies for all AWS services
- [ ] **Action:** Plan IAM role for VPC-enabled Lambda functions

**Clean IAM Architecture Design:**
- [ ] **Action:** Design global IAM role module usage
- [ ] **Action:** Plan managed policies vs custom policies strategy
- [ ] **Action:** Design KMS key policies and IAM integration
- [ ] **Action:** Plan Lambda execution role with VPC permissions
- [ ] **Action:** Design service-specific IAM policies with proper scoping

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the clean IAM architecture design
- [ ] **Action:** Detail how KMS permissions will be properly configured from start
- [ ] **Action:** Explain the modular IAM approach and its benefits
- [ ] **Action:** Present the 4 custom policies and their specific purposes
- [ ] **Action:** Explain least-privilege principle implementation
- [ ] **Approval Required:** User approves clean IAM design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**IAM Infrastructure Creation:**
```bash
# Build clean IAM foundation
terraform apply -target=aws_iam_policy.dynamodb_access
terraform apply -target=aws_iam_policy.sns_publish
terraform apply -target=aws_iam_policy.bedrock_access
terraform apply -target=aws_iam_policy.apigateway_management
terraform apply -target=module.lambda_iam_role
```

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

# Test 1.2.5: KMS Permissions Test (when KMS is enabled later)
aws sts get-caller-identity --query "Arn" --output text
```

**Pass Criteria:**
- [ ] IAM role `bos-dev-lambda-exec-role` exists and is assumable by Lambda
- [ ] All required policies attached (AWS managed + custom)
- [ ] All 4 custom policies exist and are attachable
- [ ] IAM role has proper permissions for VPC-enabled Lambda functions
- [ ] No permission errors when Lambda functions are deployed
- [ ] KMS permissions properly configured (when KMS is enabled in Phase 4)

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/iam.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed IAM policy descriptions explaining permissions and scope
- [ ] **Action:** Document each custom policy's purpose and security rationale
- [ ] **Action:** Add inline comments explaining IAM role trust relationships
- [ ] **Action:** Ensure all IAM resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the IAM security architecture
- [ ] **Action:** Document least-privilege principle implementation
- [ ] **Action:** Add comments explaining KMS permission strategy
- [ ] **Action:** Review and update module usage with explanatory comments

**Documentation Quality Check:**
- [ ] All IAM policies have clear English descriptions
- [ ] Security decisions are documented with rationale
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] IAM architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean IAM build results and test outcomes
- [ ] **Action:** Explain improved security posture over previous implementation
- [ ] **Action:** Document clean IAM foundation completion
- [ ] **Approval Required:** User confirms clean IAM foundation is built correctly and approves proceeding to Step 1.3

---

### **Step 1.3: Storage Foundation Clean Build** 🟢

**Status:** ⏳ Pending  
**Goal:** Build clean storage infrastructure using consistent module patterns

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all storage dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current Storage Review:**
- [ ] **Action:** Review existing storage architecture (3 modular + 1 hardcoded DynamoDB table)
- [ ] **Action:** Analyze S3 bucket configurations and CloudFront integration
- [ ] **Action:** Review application code storage dependencies
- [ ] **Action:** Plan clean storage architecture with consistent module usage
- [ ] **Action:** Design encryption-ready storage (for future KMS integration)
- [ ] **Action:** Plan storage for application code deployment

**Clean Storage Architecture Design:**
- [ ] **Action:** Design all DynamoDB tables using global modules
- [ ] **Action:** Plan S3 buckets with consistent module approach
- [ ] **Action:** Design CloudTrail S3 bucket with proper lifecycle policies
- [ ] **Action:** Plan point-in-time recovery and backup configurations
- [ ] **Action:** Design storage tagging and naming conventions

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the clean storage architecture design
- [ ] **Action:** Detail improvements: all tables using modules vs mixed approach
- [ ] **Action:** Explain S3 bucket organization and CloudFront integration
- [ ] **Action:** Present encryption readiness for future KMS integration
- [ ] **Action:** Explain storage cost optimization strategies
- [ ] **Approval Required:** User approves clean storage design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**Storage Infrastructure Creation:**
```bash
# Build clean storage foundation
terraform apply -target=module.short_term_memory_table
terraform apply -target=module.mission_state_table
terraform apply -target=module.elevator_monitoring_table
terraform apply -target=module.websocket_connections_table  # Now using module
terraform apply -target=module.frontend_s3_website
terraform apply -target=aws_s3_bucket.cloudtrail_logs
```

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
- [ ] All 4 DynamoDB tables exist and are in ACTIVE status (all using modules)
- [ ] DynamoDB read/write operations successful
- [ ] Point-in-time recovery configured where appropriate
- [ ] Frontend S3 bucket created and accessible
- [ ] CloudTrail S3 bucket exists with proper lifecycle policies
- [ ] S3 bucket policies properly configured
- [ ] All storage resources consistently use global modules

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/dynamodb.tf` and `frontend.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed DynamoDB table descriptions explaining data models and purpose
- [ ] **Action:** Document S3 bucket configurations and lifecycle policies
- [ ] **Action:** Add inline comments explaining storage performance optimizations
- [ ] **Action:** Ensure all storage resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the storage architecture
- [ ] **Action:** Document backup and recovery strategies
- [ ] **Action:** Add comments explaining module usage and benefits
- [ ] **Action:** Review and update hardcoded values with explanatory comments

**Documentation Quality Check:**
- [ ] All storage resources have clear English descriptions
- [ ] Data models and schemas are documented
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Storage architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean storage build results and test outcomes
- [ ] **Action:** Explain improvements: consistent module usage throughout
- [ ] **Action:** Document clean storage foundation completion
- [ ] **Approval Required:** User confirms clean storage foundation is built correctly and approves proceeding to Step 1.4

---

### **Step 1.4: Monitoring Foundation Clean Build** 🟢

**Status:** ⏳ Pending  
**Goal:** Build comprehensive monitoring and observability from day 1

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all monitoring dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current Monitoring Review:**
- [ ] **Action:** Review existing monitoring architecture (dashboards, alarms, log groups)
- [ ] **Action:** Analyze CloudWatch configuration and retention policies
- [ ] **Action:** Review SNS alerts and notification setup
- [ ] **Action:** Plan enhanced monitoring for VPC-enabled Lambda functions
- [ ] **Action:** Design cost monitoring for new clean infrastructure
- [ ] **Action:** Plan X-Ray tracing for improved observability

**Clean Monitoring Architecture Design:**
- [ ] **Action:** Design comprehensive CloudWatch dashboards
- [ ] **Action:** Plan alarm thresholds for all infrastructure components
- [ ] **Action:** Design log aggregation and structured logging
- [ ] **Action:** Plan VPC Flow Logs for network monitoring
- [ ] **Action:** Design cost monitoring and alerting
- [ ] **Action:** Plan performance monitoring for VPC-enabled Lambdas

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the comprehensive monitoring architecture design
- [ ] **Action:** Detail monitoring coverage across all infrastructure components
- [ ] **Action:** Explain alarm thresholds and their business impact
- [ ] **Action:** Present dashboard organization and metrics covered
- [ ] **Action:** Explain VPC Flow Logs and network monitoring strategy
- [ ] **Approval Required:** User approves clean monitoring design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**Monitoring Infrastructure Creation:**
```bash
# Build clean monitoring foundation
terraform apply -target=aws_cloudwatch_dashboard.main
terraform apply -target=aws_cloudwatch_dashboard.performance
terraform apply -target=aws_cloudwatch_dashboard.compliance
terraform apply -target=aws_cloudwatch_metric_alarm.lambda_errors
terraform apply -target=aws_cloudwatch_metric_alarm.lambda_duration
terraform apply -target=aws_sns_topic.alerts
```

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

# Test 1.4.5: Dashboard Content Validation
aws cloudwatch get-dashboard --dashboard-name bos-dev-monitoring --query "DashboardBody" --output text | jq .widgets[0]
```

**Pass Criteria:**
- [ ] All monitoring components created and operational
- [ ] CloudWatch dashboards exist and accessible
- [ ] All CloudWatch alarms configured and enabled
- [ ] SNS alerts topic exists and configured
- [ ] Log retention policies properly set
- [ ] VPC Flow Logs configured (if applicable)
- [ ] Cost monitoring alerts configured

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/monitoring.tf` and `compliance.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed CloudWatch dashboard descriptions explaining metrics and purpose
- [ ] **Action:** Document alarm configurations and threshold rationale
- [ ] **Action:** Add inline comments explaining log retention policies
- [ ] **Action:** Ensure all monitoring resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the monitoring strategy
- [ ] **Action:** Document compliance tracking and audit requirements
- [ ] **Action:** Add comments explaining performance monitoring approach
- [ ] **Action:** Review and update alerting configurations with explanatory comments

**Documentation Quality Check:**
- [ ] All monitoring resources have clear English descriptions
- [ ] Alerting strategies are documented with rationale
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Monitoring architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean monitoring build results and test outcomes
- [ ] **Action:** Explain comprehensive monitoring coverage achieved
- [ ] **Action:** Document clean monitoring foundation completion
- [ ] **Approval Required:** User confirms clean monitoring foundation is built correctly and approves proceeding to Phase 2

---

## 🏗️ **PHASE 2: CORE SERVICES CLEAN BUILD (MEDIUM RISK)**

### **Step 2.1: Messaging Infrastructure (SNS) Clean Build** 🟡

**Status:** ⏳ Pending  
**Goal:** Build clean SNS architecture for inter-agent communication

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all SNS dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current SNS Architecture Review:**
- [ ] **Action:** Review existing SNS topics and their communication patterns
- [ ] **Action:** Analyze application code SNS usage (`src/agents/` directory)
- [ ] **Action:** Map complete agent communication flow
- [ ] **Action:** Plan clean SNS architecture with consistent naming
- [ ] **Action:** Design SNS topic policies and access controls
- [ ] **Action:** Plan dead letter queues and error handling

**Clean SNS Architecture Design:**
- [ ] **Action:** Design all 8 SNS topics using global modules consistently
- [ ] **Action:** Plan SNS encryption settings (ready for KMS integration)
- [ ] **Action:** Design topic subscription patterns for Lambda functions
- [ ] **Action:** Plan message filtering and routing strategies
- [ ] **Action:** Design SNS monitoring and alerting

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the clean SNS-based communication architecture
- [ ] **Action:** Detail the 8 SNS topics and their specific roles in agent communication
- [ ] **Action:** Map out the complete message flow from user input to final response
- [ ] **Action:** Explain improvements in message routing and error handling
- [ ] **Action:** Present SNS cost optimization strategies
- [ ] **Approval Required:** User approves clean SNS design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**SNS Infrastructure Creation:**
```bash
# Build clean SNS foundation
terraform apply -target=module.intention_topic
terraform apply -target=module.mission_topic
terraform apply -target=module.task_result_topic
terraform apply -target=module.mission_result_topic
terraform apply -target=module.intention_result_topic
terraform apply -target=module.health_check_topic
terraform apply -target=module.error_topic
terraform apply -target=module.alerts_topic
```

#### **🧪 TESTING PHASE**

**SNS Configuration Tests:**
```powershell
# Test 2.1.1: SNS Topics Validation
aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-')]" --output table

# Test 2.1.2: Topic Details Check
aws sns get-topic-attributes --topic-arn $(aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-intention')].TopicArn" --output text) --query "Attributes.{DisplayName:DisplayName,SubscriptionsConfirmed:SubscriptionsConfirmed,SubscriptionsPending:SubscriptionsPending}" --output table

# Test 2.1.3: SNS Message Publishing Test
aws sns publish --topic-arn $(aws sns list-topics --query "Topics[?contains(TopicArn, 'bos-dev-health-check')].TopicArn" --output text) --message "Test message from clean rebuild validation" --subject "Health Check Test"
```

**Pass Criteria:**
- [ ] All 8 SNS topics exist and are accessible
- [ ] Topics created using consistent global modules
- [ ] SNS topics properly configured for Lambda subscriptions
- [ ] Message publishing successful
- [ ] Topic policies and access controls properly configured
- [ ] SNS monitoring and alerting configured

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/sns.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed SNS topic descriptions explaining communication patterns
- [ ] **Action:** Document message flow and agent communication architecture
- [ ] **Action:** Add inline comments explaining topic policies and access controls
- [ ] **Action:** Ensure all SNS resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the event-driven architecture
- [ ] **Action:** Document subscription patterns and message routing
- [ ] **Action:** Add comments explaining dead letter queue configurations
- [ ] **Action:** Review and update module usage with explanatory comments

**Documentation Quality Check:**
- [ ] All SNS resources have clear English descriptions
- [ ] Communication patterns are documented
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Event-driven architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean SNS build results and test outcomes
- [ ] **Action:** Explain improved messaging architecture
- [ ] **Action:** Document clean SNS foundation completion
- [ ] **Approval Required:** User confirms clean SNS infrastructure is built correctly and approves proceeding to Step 2.2

---

### **Step 2.2: Lambda Functions Clean Build (VPC-Enabled)** 🟡

**Status:** ⏳ Pending  
**Goal:** Deploy all Lambda functions with VPC integration from day 1 (NO "TEMPORARILY DISABLED")

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all Lambda dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Application Code Review:**
- [ ] **Action:** Review all Lambda function code in `src/` directory (preserved exactly)
- [ ] **Action:** Analyze current Lambda configurations and performance settings
- [ ] **Action:** Plan VPC configuration for all 10 Lambda functions from start
- [ ] **Action:** Review environment variables and dependencies
- [ ] **Action:** Plan Lambda layer usage and common utilities
- [ ] **Action:** Design Lambda function monitoring and alerting

**VPC-Enabled Lambda Design:**
- [ ] **Action:** Plan subnet placement for all Lambda functions (private subnets)
- [ ] **Action:** Design security group configurations for VPC-enabled Lambdas
- [ ] **Action:** Plan cold start mitigation strategies (provisioned concurrency)
- [ ] **Action:** Design Lambda function scaling and performance optimization
- [ ] **Action:** Plan Lambda function deployment and versioning

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the VPC-enabled Lambda architecture design
- [ ] **Action:** Detail benefits of VPC integration from day 1 (cost savings, security)
- [ ] **Action:** Explain how VPC endpoints will be utilized by Lambda functions
- [ ] **Action:** Present cold start mitigation strategies and performance optimization
- [ ] **Action:** Explain Lambda function deployment strategy with same application code
- [ ] **Approval Required:** User approves VPC-enabled Lambda design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**Lambda Infrastructure Creation:**
```bash
# Build Lambda layer first
terraform apply -target=module.common_utils_layer

# Build VPC-enabled Lambda functions (using preserved application code)
terraform apply -target=module.agent_health_check      # VPC enabled from start
terraform apply -target=module.agent_persona           # VPC enabled from start  
terraform apply -target=module.agent_director          # VPC enabled from start
terraform apply -target=module.agent_coordinator       # VPC enabled from start
terraform apply -target=module.agent_elevator          # VPC enabled from start
terraform apply -target=module.agent_psim              # VPC enabled from start
terraform apply -target=module.websocket_connect       # VPC enabled from start
terraform apply -target=module.websocket_disconnect    # VPC enabled from start
terraform apply -target=module.websocket_default       # VPC enabled from start
terraform apply -target=module.websocket_broadcast     # VPC enabled from start
```

#### **🧪 TESTING PHASE**

**Lambda Function Tests:**
```powershell
# Test 2.2.1: Lambda Functions Status
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'bos-dev-')].{FunctionName:FunctionName,State:State,VpcConfig:VpcConfig.VpcId}" --output table

# Test 2.2.2: VPC Configuration Check
aws lambda get-function-configuration --function-name bos-dev-agent-health-check --query "VpcConfig" --output table

# Test 2.2.3: Basic Lambda Invocation Test (should work without KMS issues)
aws lambda invoke --function-name bos-dev-agent-health-check --payload '{}' response.json && cat response.json && rm response.json

# Test 2.2.4: Lambda Performance Metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Duration --dimensions Name=FunctionName,Value=bos-dev-agent-health-check --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Average,Maximum --output table

# Test 2.2.5: Lambda Layer Validation
aws lambda get-function --function-name bos-dev-agent-health-check --query "Configuration.Layers[*].{LayerArn:Arn,LayerVersion:Version}" --output table

# Test 2.2.6: VPC Integration Test
aws lambda invoke --function-name bos-dev-agent-health-check --log-type Tail --query 'LogResult' --output text | base64 --decode

# Test 2.2.7: Cold Start Monitoring
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name InitDuration --dimensions Name=FunctionName,Value=bos-dev-agent-health-check --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Average,Maximum --output table
```

**Pass Criteria:**
- [ ] All 10 Lambda functions in Active state
- [ ] All Lambda functions have VPC configuration enabled (no temporary disables)
- [ ] Lambda layer exists and is attached to functions requiring it
- [ ] Basic Lambda invocation successful (no KMS access issues)
- [ ] VPC endpoints being utilized (reduced NAT Gateway usage)
- [ ] Lambda functions can access DynamoDB, S3, SNS through VPC endpoints
- [ ] Cold start times within acceptable ranges
- [ ] Lambda function monitoring and alerting operational

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/lambda_functions.tf`
- [ ] **Action:** Review all application code in `src/` directory for documentation
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed Lambda function descriptions explaining purpose and functionality
- [ ] **Action:** Document VPC configuration and networking requirements
- [ ] **Action:** Add inline comments explaining performance configurations (memory, timeout)
- [ ] **Action:** Ensure all Lambda resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the agent architecture
- [ ] **Action:** Document environment variables and their purposes
- [ ] **Action:** Add comments in Python code explaining business logic
- [ ] **Action:** Review and update module usage with explanatory comments

**Documentation Quality Check:**
- [ ] All Lambda resources have clear English descriptions
- [ ] Application code has comprehensive English comments
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Agent architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present VPC-enabled Lambda build results and test outcomes
- [ ] **Action:** Explain successful VPC integration and cost benefits achieved
- [ ] **Action:** Document VPC-enabled Lambda foundation completion
- [ ] **Approval Required:** User confirms VPC-enabled Lambda functions are working correctly and approves proceeding to Step 2.3

---

### **Step 2.3: API Gateway Clean Build** 🟡

**Status:** ⏳ Pending  
**Goal:** Build clean API Gateway with proper integration to VPC-enabled Lambdas

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all API Gateway dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current API Gateway Review:**
- [ ] **Action:** Review existing API Gateway configuration (HTTP API and WebSocket API)
- [ ] **Action:** Analyze API routes and integration patterns
- [ ] **Action:** Review CORS configuration and security settings
- [ ] **Action:** Plan clean API Gateway architecture with improved organization
- [ ] **Action:** Design API Gateway integration with VPC-enabled Lambda functions
- [ ] **Action:** Plan API Gateway monitoring and logging

**Clean API Gateway Design:**
- [ ] **Action:** Design clean API Gateway structure using global modules
- [ ] **Action:** Plan API routes with improved organization and naming
- [ ] **Action:** Design CORS policies for frontend integration
- [ ] **Action:** Plan API Gateway stage management and deployment
- [ ] **Action:** Design API Gateway throttling and rate limiting
- [ ] **Action:** Plan API Gateway custom domain and SSL certificate management

#### **📋 EXPLANATION PHASE**

- [ ] **Action:** Explain the clean API Gateway architecture design
- [ ] **Action:** Detail improvements in API organization and security
- [ ] **Action:** Explain integration with VPC-enabled Lambda functions
- [ ] **Action:** Present API Gateway performance and cost optimization strategies
- [ ] **Action:** Explain API Gateway monitoring and logging enhancements
- [ ] **Approval Required:** User approves clean API Gateway design and build plan

#### **🏗️ CLEAN BUILD PHASE**

**API Gateway Infrastructure Creation:**
```bash
# Build clean API Gateway infrastructure
terraform apply -target=module.websocket_api
terraform apply -target=aws_apigatewayv2_api.http_api
terraform apply -target=aws_apigatewayv2_stage.http_api_stage
terraform apply -target=aws_apigatewayv2_integration.health_check
terraform apply -target=aws_apigatewayv2_integration.persona
terraform apply -target=aws_apigatewayv2_integration.director
terraform apply -target=aws_apigatewayv2_route.health_check
terraform apply -target=aws_apigatewayv2_route.persona
terraform apply -target=aws_apigatewayv2_route.director
```

#### **🧪 TESTING PHASE**

**API Gateway Tests:**
```powershell
# Test 2.3.1: API Gateway Status
aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-')].{Name:Name,ApiId:ApiId,ProtocolType:ProtocolType,ApiEndpoint:ApiEndpoint}" --output table

# Test 2.3.2: API Routes Validation
aws apigatewayv2 get-routes --api-id $(aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-dev-http')].ApiId" --output text) --query "Items[*].{RouteKey:RouteKey,Target:Target}" --output table

# Test 2.3.3: WebSocket API Status
aws apigatewayv2 get-routes --api-id $(aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-dev-websocket')].ApiId" --output text) --query "Items[*].{RouteKey:RouteKey,Target:Target}" --output table

# Test 2.3.4: API Stage Deployment
aws apigatewayv2 get-stages --api-id $(aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-dev-http')].ApiId" --output text) --query "Items[*].{StageName:StageName,DeploymentId:DeploymentId,LastUpdatedDate:LastUpdatedDate}" --output table

# Test 2.3.5: HTTP API Endpoints Testing
$API_ENDPOINT = $(aws apigatewayv2 get-apis --query "Items[?starts_with(Name, 'bos-dev-http')].ApiEndpoint" --output text)
Invoke-RestMethod -Uri "$API_ENDPOINT/health" -Method GET

# Test 2.3.6: CORS Configuration Check
Invoke-RestMethod -Uri "$API_ENDPOINT/health" -Method OPTIONS -Headers @{"Origin"="https://buildingos-frontend-dev.s3-website-us-east-1.amazonaws.com"}

# Test 2.3.7: API Gateway Integration with VPC Lambda
Invoke-RestMethod -Uri "$API_ENDPOINT/health" -Method GET -TimeoutSec 30
```

**Pass Criteria:**
- [ ] HTTP API and WebSocket API exist and are accessible
- [ ] All API routes properly configured and working
- [ ] API Gateway stages deployed and accessible
- [ ] CORS configuration working for frontend integration
- [ ] API Gateway successfully integrates with VPC-enabled Lambda functions
- [ ] API response times within acceptable ranges
- [ ] API Gateway monitoring and logging operational

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/api_gateway.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed API Gateway descriptions explaining HTTP and WebSocket APIs
- [ ] **Action:** Document route configurations and integration patterns
- [ ] **Action:** Add inline comments explaining CORS policies and security settings
- [ ] **Action:** Ensure all API Gateway resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the API architecture
- [ ] **Action:** Document authentication and authorization strategies
- [ ] **Action:** Add comments explaining Lambda integrations and permissions
- [ ] **Action:** Review and update module usage with explanatory comments

**Documentation Quality Check:**
- [ ] All API Gateway resources have clear English descriptions
- [ ] API design patterns are documented
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] API architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean API Gateway build results and test outcomes
- [ ] **Action:** Explain successful integration with VPC-enabled Lambda functions
- [ ] **Action:** Document clean API Gateway foundation completion
- [ ] **Approval Required:** User confirms clean API Gateway is working correctly and approves proceeding to Phase 3

---

## 🔴 **PHASE 3: INTEGRATION SERVICES CLEAN BUILD (HIGH RISK)**

### **Step 3.1: Frontend Integration Clean Build** 🔴

**Status:** ⏳ Pending  
**Goal:** Deploy clean frontend with optimized CDN and S3 integration

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all frontend dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current Frontend Review:**
- [ ] **Action:** Review existing frontend code (`frontend/` directory - preserved exactly)
- [ ] **Action:** Analyze S3 website configuration and CloudFront distribution
- [ ] **Action:** Review frontend to API integration patterns
- [ ] **Action:** Plan clean frontend deployment with improved caching
- [ ] **Action:** Design CloudFront optimization and cost reduction
- [ ] **Action:** Plan frontend monitoring and performance tracking

#### **🧪 TESTING PHASE**

**Frontend Tests:**
```powershell
# Test 3.1.1: CloudFront Distribution Status
aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'bos-dev-')].{Id:Id,DomainName:DomainName,Status:Status,Enabled:Enabled}" --output table

# Test 3.1.2: S3 Website Configuration
aws s3api get-bucket-website --bucket buildingos-frontend-dev --output table

# Test 3.1.3: Frontend File Accessibility
$CLOUDFRONT_URL = $(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'bos-dev-')].DomainName" --output text)
Invoke-RestMethod -Uri "https://$CLOUDFRONT_URL/index.html" -Method GET

# Test 3.1.4: Frontend to API Integration
# Test frontend calling API Gateway endpoints

# Test 3.1.5: WebSocket Integration Test
# Test WebSocket connection from frontend
```

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all frontend code in `frontend/` directory
- [ ] **Action:** Review all Terraform files in `terraform/environments/dev/frontend.tf`
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed S3 website configuration descriptions
- [ ] **Action:** Document CloudFront distribution settings and caching strategies
- [ ] **Action:** Add inline comments in HTML/JavaScript explaining functionality
- [ ] **Action:** Ensure all frontend resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the frontend architecture
- [ ] **Action:** Document API integration patterns and WebSocket connections
- [ ] **Action:** Add comments explaining user interface components
- [ ] **Action:** Review and update module usage with explanatory comments

**Documentation Quality Check:**
- [ ] All frontend resources have clear English descriptions
- [ ] User interface functionality is documented
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Frontend architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean frontend build results and test outcomes
- [ ] **Action:** Explain frontend performance improvements and cost optimization
- [ ] **Action:** Document clean frontend foundation completion
- [ ] **Approval Required:** User confirms clean frontend is working correctly and approves proceeding to Step 3.2

---

### **Step 3.2: Bedrock AI Integration Clean Build** 🔴

**Status:** ⏳ Pending  
**Goal:** Build clean Bedrock AI integration with VPC endpoint utilization

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all Bedrock dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**Current Bedrock Integration Review:**
- [ ] **Action:** Review Bedrock usage in application code (`src/agents/agent_director/app.py`)
- [ ] **Action:** Analyze VPC endpoint for Bedrock configuration
- [ ] **Action:** Review IAM permissions for Bedrock access
- [ ] **Action:** Plan clean Bedrock integration with cost optimization
- [ ] **Action:** Design Bedrock monitoring and usage tracking
- [ ] **Action:** Plan Bedrock model selection and configuration

#### **🧪 TESTING PHASE**

**Bedrock Configuration Tests:**
```powershell
# Test 3.2.1: Bedrock Service Availability
aws bedrock list-foundation-models --query "modelSummaries[?starts_with(modelId, 'anthropic')].{ModelId:modelId,ModelName:modelName,ProviderName:providerName}" --output table

# Test 3.2.2: VPC Endpoint for Bedrock
aws ec2 describe-vpc-endpoints --filters "Name=service-name,Values=com.amazonaws.us-east-1.bedrock-runtime" --query "VpcEndpoints[*].{VpcEndpointId:VpcEndpointId,State:State,VpcId:VpcId}" --output table

# Test 3.2.3: Bedrock IAM Permissions
aws sts get-caller-identity --query "Arn" --output text

# Test 3.2.4: Direct Bedrock Model Invocation Test
aws bedrock-runtime invoke-model --model-id anthropic.claude-3-haiku-20240307-v1:0 --body '{"messages":[{"role":"user","content":"Hello, this is a test from clean BuildingOS infrastructure."}],"max_tokens":100,"anthropic_version":"bedrock-2023-05-31"}' response.json && cat response.json && rm response.json

# Test 3.2.5: Lambda Function Bedrock Integration
aws lambda invoke --function-name bos-dev-agent-director --payload '{"test":"bedrock_integration","message":"Hello from clean infrastructure"}' response.json && cat response.json && rm response.json

# Test 3.2.6: Bedrock VPC Endpoint Usage Validation
# Check CloudWatch metrics for VPC endpoint usage
aws cloudwatch get-metric-statistics --namespace AWS/VpcFlowLogs --metric-name PacketsTransferred --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Sum --output table
```

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all Bedrock-related code in `src/agents/agent_director/app.py`
- [ ] **Action:** Review all Terraform files related to Bedrock VPC endpoints
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed Bedrock integration descriptions explaining AI functionality
- [ ] **Action:** Document VPC endpoint configurations for secure AI access
- [ ] **Action:** Add inline comments in Python code explaining AI model usage
- [ ] **Action:** Ensure all AI-related resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the AI integration architecture
- [ ] **Action:** Document prompt engineering and model selection rationale
- [ ] **Action:** Add comments explaining error handling and retry logic
- [ ] **Action:** Review and update security configurations with explanatory comments

**Documentation Quality Check:**
- [ ] All AI integration resources have clear English descriptions
- [ ] AI functionality and model usage is documented
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] AI architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present clean Bedrock integration build results and test outcomes
- [ ] **Action:** Explain VPC endpoint cost savings and performance improvements
- [ ] **Action:** Document clean Bedrock foundation completion
- [ ] **Approval Required:** User confirms clean Bedrock integration is working correctly and approves proceeding to Step 3.3

---

### **Step 3.3: End-to-End Application Flow Clean Build** 🔴

**Status:** ⏳ Pending  
**Goal:** Validate complete application functionality with clean infrastructure

#### **🧪 TESTING PHASE**

**Complete Flow Tests:**
```powershell
# Test 3.3.1: Complete API Test Suite
cd tests/api
python run_tests.py --comprehensive

# Test 3.3.2: Agent Communication Flow
# Test persona → director → coordinator → agent flow

# Test 3.3.3: WebSocket Real-time Communication
# Test WebSocket connections and message broadcasting

# Test 3.3.4: Multi-Agent Communication Flow
# Test SNS-based communication between agents

# Test 3.3.5: Bedrock AI Integration Flow
# Test AI-powered responses through complete flow

# Test 3.3.6: Overall System Health
# Comprehensive health check of all components
```

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present complete end-to-end test results
- [ ] **Action:** Explain system performance improvements with clean infrastructure
- [ ] **Action:** Document complete application functionality validation
- [ ] **Approval Required:** User confirms complete system is working correctly and approves proceeding to Phase 4

---

## ⚫ **PHASE 4: ADVANCED FEATURES (OPTIONAL)**

### **Step 4.1: KMS Encryption Integration** ⚫

**Status:** ⏳ Pending (Optional)  
**Goal:** Enable KMS encryption with proper permissions (no access issues)

#### **🔍 ANALYSIS PHASE**

**🌍 MANDATORY: Global Analysis (following methodology above):**
- [ ] **Action:** Start from global `building-os-platform` directory analysis
- [ ] **Action:** Review complete project structure and all terraform modules
- [ ] **Action:** Map all KMS dependencies across `src/`, `frontend/`, `tests/`
- [ ] **Action:** Check global `terraform/providers.tf` and `terraform/versions.tf` configurations
- [ ] **Action:** Verify compliance requirements from `docs/` directory

**KMS Integration Planning:**
- [ ] **Action:** Design KMS key policies with proper IAM integration
- [ ] **Action:** Plan KMS encryption for DynamoDB tables
- [ ] **Action:** Design KMS encryption for S3 buckets
- [ ] **Action:** Plan KMS encryption for Lambda environment variables
- [ ] **Action:** Design KMS cost optimization strategies

#### **🧪 TESTING PHASE**

**KMS Integration Tests:**
```powershell
# Test 4.1.1: KMS Key Creation and Policies
aws kms list-keys --query "Keys[*].KeyId" --output table

# Test 4.1.2: Lambda Function KMS Integration
aws lambda invoke --function-name bos-dev-agent-health-check --payload '{}' response.json && cat response.json && rm response.json

# Test 4.1.3: DynamoDB Encryption at Rest
aws dynamodb describe-table --table-name bos-dev-short-term-memory --query "Table.SSEDescription" --output table

# Test 4.1.4: S3 Bucket Encryption
aws s3api get-bucket-encryption --bucket buildingos-frontend-dev --output table
```

#### **📝 DOCUMENTATION CLEANUP PHASE**

**Code Documentation Standards (English Only):**
- [ ] **Action:** Review all KMS-related Terraform files in `terraform/environments/dev/security.tf`
- [ ] **Action:** Review all encryption configurations across all resources
- [ ] **Action:** Clean existing comments and replace with comprehensive English documentation
- [ ] **Action:** Add detailed KMS key policy descriptions explaining access controls
- [ ] **Action:** Document encryption strategies for DynamoDB, S3, and Lambda
- [ ] **Action:** Add inline comments explaining key rotation and management
- [ ] **Action:** Ensure all security resource names and descriptions are in English
- [ ] **Action:** Add header comments explaining the security and encryption architecture
- [ ] **Action:** Document compliance requirements and implementation
- [ ] **Action:** Add comments explaining IAM integration with KMS
- [ ] **Action:** Review and update security best practices with explanatory comments

**Documentation Quality Check:**
- [ ] All security resources have clear English descriptions
- [ ] Encryption strategies and key management are documented
- [ ] Variable and output descriptions are comprehensive
- [ ] No non-English text remains in code or comments
- [ ] Security architecture decisions are documented inline

#### **✅ APPROVAL PHASE**

- [ ] **Action:** Present KMS integration results (if enabled)
- [ ] **Action:** Document KMS encryption completion
- [ ] **Approval Required:** User confirms KMS integration working correctly (if enabled)

---

## 📊 **STEP COMPLETION TRACKING**

### **Current Status**
- **Phase 1, Step 1.1:** ⏳ Ready to begin clean build
- **All other steps:** ⏳ Awaiting completion of prerequisite steps

### **Next Action Required**
**Begin Step 1.1 Clean Build Phase** - Build networking foundation with VPC endpoints and best practices from day 1

### **Key Advantages of Clean Rebuild**
- ✅ **No KMS access issues** - proper permissions from start
- ✅ **VPC-enabled Lambda functions** - no "TEMPORARILY DISABLED" configurations
- ✅ **Consistent module usage** - all resources follow global patterns
- ✅ **Cost optimization** - VPC endpoints utilized from day 1
- ✅ **Clean architecture** - no hidden configuration surprises

**Do I have your authorization to begin Step 1.1: Networking & VPC Clean Build Phase?**

---

## 🚨 **CRITICAL SUCCESS FACTORS**

1. **Preserve All Application Code** - Never lose business logic
2. **Build Clean From Start** - No temporary configurations
3. **Enable VPC Integration** - Lambda functions VPC-enabled from day 1
4. **Test Thoroughly** - All tests must pass before proceeding
5. **Document Everything** - Keep detailed records of clean build process
6. **Maintain Safe Order** - Foundation → Core → Integration → Advanced
