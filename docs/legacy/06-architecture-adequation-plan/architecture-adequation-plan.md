---
status: "Active"
date: "2025-08-07"
author: "Jomil & GitHub Copilot"
tags:
  - "Architecture"
  - "Planning"
  - "Implementation"
  - "Gap Analysis"
---

# Architecture Adequation Plan: BuildingOS Implementation Alignment

## 📋 Executive Summary

This document provides a comprehensive analysis comparing the defined BuildingOS architecture with the current implementation in `terraform/environments/dev/main.tf`, along with a detailed plan to align the implementation with the architectural vision.

**Key Findings:**
- ✅ Core agent framework is implemented and functional
- ❌ 4 critical integration agents are missing
- ❌ `intention_result_topic` SNS missing from event flow
- ⚠️ `task_completion_topic` needs renaming to `task_result_topic`
- ❌ Kendra (RAG) infrastructure not implemented
- ⚠️ S3 document storage partially implemented
- ⚠️ Agent naming inconsistency with architecture definitions

---

## 🔍 **1. COMPARATIVE ANALYSIS: DEFINED vs IMPLEMENTED**

### **1.1 Agent Architecture Comparison**

| **Agent** | **Status** | **Implemented** | **Observations** |
|------------|------------|------------------|-----------------|
| `agent_persona` | ✅ **Complete** | Yes | Functional with DynamoDB and SNS |
| `agent_director` | ✅ **Complete** | Yes | Functional with Bedrock LLM |
| `agent_coordinator` | ✅ **Complete** | Yes | Implemented as Lambda |
| `agent_elevator` | ✅ **Complete** | Yes | Neomot integration functional |
| `agent_psim` | ✅ **Complete** | Yes | PSIM integration implemented |
| `agent_erp` | ❌ **MISSING** | No | **Critical for ERP synchronization** |
| `agent_brokers` | ❌ **MISSING** | No | **Essential for hospitality** |
| `agent_locks` | ❌ **MISSING** | No | **Required for TTLock access** |
| `agent_metering` | ❌ **MISSING** | No | **Important for monitoring** |

### **1.2 SNS Event Bus Comparison**

| **SNS Topic** | **Status** | **Implemented** | **Usage** |
|----------------|------------|------------------|---------|
| `intention_topic` | ✅ **Complete** | Yes | Persona → Director |
| `mission_topic` | ✅ **Complete** | Yes | Director → Coordinator |
| `task_result_topic` | ⚠️ **Naming** | Yes (as task_completion_topic) | Agents → Coordinator |
| `mission_result_topic` | ✅ **Complete** | Yes | Coordinator → Director/Persona |
| `intention_result_topic` | ❌ **MISSING** | No | **Director → Persona (final response)** |

### **1.3 Infrastructure Components Comparison**

| **Component** | **Status** | **Implemented** | **Observations** |
|----------------|------------|------------------|-----------------|
| DynamoDB (Short-term Memory) | ✅ **Complete** | Yes | Persona agent memory |
| DynamoDB (Mission State) | ✅ **Complete** | Yes | Coordinator state |
| DynamoDB (Elevator Monitoring) | ✅ **Complete** | Yes | Agent elevator monitoring |
| Kendra (RAG Search) | ❌ **MISSING** | No | **RAG functionality missing** |
| S3 (File Storage) | ⚠️ **Partial** | Yes (Frontend) | Only frontend, missing docs |
| AWS Bedrock | ✅ **Complete** | Yes | LLM integration |

### **1.4 Agent Naming Inconsistencies**

| **Architecture Definition** | **Current Implementation** | **Status** |
|----------------------------|----------------------------|------------|
| `agent_persona` | `bos-agent-persona-${var.environment}` | ✅ **Consistent** |
| `agent_director` | `bos-agent-director-${var.environment}` | ✅ **Consistent** |
| `agent_coordinator` | `bos-agent-coordinator-${var.environment}` | ✅ **Consistent** |
| `agent_elevator` | `bos-agent-elevator-${var.environment}` | ✅ **Consistent** |
| `agent_psim` | `bos-agent-psim-${var.environment}` | ✅ **Consistent** |

**Issue**: Core agents use `<name>-agent` pattern while integration agents use `agent-<name>` pattern, creating inconsistency.

---

## 🎯 **2. IMPLEMENTATION ADEQUATION PLAN**

### **PHASE 0: AGENT NAMING STANDARDIZATION** ✅ **COMPLETED** 🏷️
*Priority: HIGH - Estimated Duration: 2-3 days*

#### **0.1 Standardize Agent Function Names** ✅ **COMPLETED**
All agents now follow the `bos-agent-<name>-${var.environment}` pattern for consistency:

```hcl
# Naming changes completed:
# bos-persona-agent-${var.environment}     → bos-agent-persona-${var.environment} ✅
# bos-director-agent-${var.environment}    → bos-agent-director-${var.environment} ✅
# bos-coordinator-agent-${var.environment} → bos-agent-coordinator-${var.environment} ✅
```

#### **0.2 Update All References** ✅ **COMPLETED**
All references automatically updated via Terraform resource references:
- Lambda permissions (using `aws_lambda_function.*.function_name`) ✅
- SNS subscriptions (using `aws_lambda_function.*.function_name`) ✅
- API Gateway integrations (using `aws_lambda_function.*.function_name`) ✅
- IAM policies (using `aws_lambda_function.*.arn`) ✅
- Environment variables (not using direct function name references) ✅

#### **0.3 Verify Functionality** ✅ **COMPLETED**
After renaming, all integrations tested and functional.

#### **0.4 Add API Endpoints for All Agents** 🔧 **NEW REQUIREMENT**
**Context**: During development transition from "tools" to "agents", some agents lost their API endpoints but kept SNS integration. For better debugging and testing, all agents should have both SNS and API access.

**Current Status**:
- ✅ **WITH API**: persona, director, elevator, health-check
- ❌ **WITHOUT API**: coordinator, psim

**Implementation Required**:
```hcl
# Add in main.tf - API Gateway routes for missing agents

# PSIM Agent API Route
resource "aws_apigatewayv2_route" "agent_psim_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /psim/search"
  target    = "integrations/${aws_apigatewayv2_integration.agent_psim_integration.id}"
}

# PSIM Agent API Integration  
resource "aws_apigatewayv2_integration" "agent_psim_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.agent_psim.invoke_arn
}

# PSIM Agent API Permission
resource "aws_lambda_permission" "api_gateway_permission_psim" {
  statement_id  = "AllowAPIGatewayInvokePSIM"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent_psim.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Coordinator Agent API Route
resource "aws_apigatewayv2_route" "agent_coordinator_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /coordinator/missions/{mission_id}"
  target    = "integrations/${aws_apigatewayv2_integration.agent_coordinator_integration.id}"
}

# Coordinator Agent API Integration
resource "aws_apigatewayv2_integration" "agent_coordinator_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.coordinator_agent.invoke_arn
}

# Coordinator Agent API Permission
resource "aws_lambda_permission" "api_gateway_permission_coordinator" {
  statement_id  = "AllowAPIGatewayInvokeCoordinator"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.coordinator_agent.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
```

**Agent Code Updates Required**:
- Modify `agent_psim/app.py` to handle HTTP API events
- Modify `coordinator/app.py` to handle HTTP API events  
- Add hybrid event detection (SNS vs API Gateway)

**Benefits**:
- 🐛 **Debug**: Direct testing of individual agents
- 🧪 **Testing**: Validate agent functionality independently  
- 📊 **Monitoring**: Health checks per agent
- 🔧 **Development**: Faster iteration cycles

### **PHASE 1: CRITICAL EVENT FLOW CORRECTIONS** 🚨
*Priority: HIGH - Estimated Duration: 3-5 days*

#### **1.1 Rename `task_completion_topic` to `task_result_topic`**
```hcl
# Update existing topic name in main.tf
module "task_result_topic" {
  source = "../../modules/sns_topic"
  name = "bos-task-result-topic-${var.environment}"
  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}
```

#### **1.2 Add `intention_result_topic` SNS**
```hcl
# Add in main.tf after other SNS topics
module "intention_result_topic" {
  source = "../../modules/sns_topic"
  name = "bos-intention-result-topic-${var.environment}"
  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "EventBus"
  }
}
```

#### **1.3 Update Agent Environment Variables**
- **All integration agents**: Update `TASK_COMPLETION_TOPIC_ARN` → `TASK_RESULT_TOPIC_ARN`
- **Coordinator Agent**: Update subscription from `task_completion_topic` → `task_result_topic`
- **Director Agent**: Add `INTENTION_RESULT_TOPIC_ARN`
- **Persona Agent**: Subscribe to `intention_result_topic`

#### **1.4 Implement SNS Subscriptions**
```hcl
# Subscription for persona agent on intention_result_topic
resource "aws_sns_topic_subscription" "persona_agent_intention_result_subscription" {
  topic_arn = module.intention_result_topic.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.persona_agent.arn
}

# Permission for SNS to invoke persona agent
resource "aws_lambda_permission" "sns_permission_persona_intention_result" {
  statement_id  = "AllowSNSInvokePersonaIntentionResult"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.persona_agent.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.intention_result_topic.topic_arn
}
```

### **PHASE 2: MISSING AGENTS IMPLEMENTATION** 📦
*Priority: HIGH - Estimated Duration: 10-15 days*

#### **2.1 Implement `agent_erp`**
- **Responsibility**: Superlógica ERP synchronization
- **Functionalities**:
  - Synchronize residents and financial data
  - Query bills and payment status
  - Manage owner/tenant data

**Required file structure:**
```
src/agents/agent_erp/
├── app.py
├── requirements.txt
└── config/
    └── erp_config.py
```

**main.tf additions:**
```hcl
data "archive_file" "agent_erp_zip" {
  type        = "zip"
  source_dir  = "../../../src/agents/agent_erp"
  output_path = "${path.module}/.terraform/agent_erp.zip"
}

resource "aws_lambda_function" "agent_erp" {
  function_name = "bos-agent-erp-${var.environment}"
  role          = module.lambda_exec_role.role_arn
  handler       = "app.handler"
  runtime       = "python3.11"
  layers        = [module.common_utils_layer.layer_arn]
  timeout       = 30

  filename         = data.archive_file.agent_erp_zip.output_path
  source_code_hash = data.archive_file.agent_erp_zip.output_base64sha256

  environment {
    variables = {
      ERP_API_BASE_URL      = "https://api.superlogica.com"
      ERP_API_TOKEN         = var.erp_api_token
      TASK_RESULT_TOPIC_ARN = module.task_result_topic.topic_arn
      MISSION_STATE_TABLE_NAME = module.mission_state_db.table_name
    }
  }
}
```

#### **2.2 Implement `agent_brokers`**
- **Responsibility**: Hospitality platform integration
- **Functionalities**:
  - Synchronize Airbnb/Booking reservations
  - Manage guest check-in/check-out
  - Coordinate with other agents for access
- **Environment Variables**: Include `TASK_RESULT_TOPIC_ARN`

#### **2.3 Implement `agent_locks`**
- **Responsibility**: Smart lock control
- **Functionalities**:
  - TTLock API integration
  - Generate/remove temporary passwords
  - Access history tracking
- **Environment Variables**: Include `TASK_RESULT_TOPIC_ARN`

#### **2.4 Implement `agent_metering`**
- **Responsibility**: Consumption monitoring
- **Functionalities**:
  - Water/gas meter readings
  - Abnormal consumption alerts
  - Monthly reports
- **Environment Variables**: Include `TASK_RESULT_TOPIC_ARN`

### **PHASE 3: KENDRA (RAG) IMPLEMENTATION** 🔍
*Priority: MEDIUM - Estimated Duration: 7-10 days*

#### **3.1 Add Kendra in Terraform**
```hcl
# Add Kendra module
module "kendra_index" {
  source = "../../modules/kendra_index"
  
  index_name = "bos-kendra-${var.environment}"
  role_arn   = aws_iam_role.kendra_role.arn
  
  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "RAG"
  }
}
```

#### **3.2 Update IAM Policies**
- Add Kendra permissions to `lambda_exec_role`
- Allow document indexing and search

#### **3.3 Update agent_persona**
- Implement RAG functionality
- Integrate with Kendra for document search

### **PHASE 4: INFRASTRUCTURE IMPROVEMENTS** 🏗️
*Priority: MEDIUM - Estimated Duration: 5-7 days*

#### **4.1 Implement S3 for Documents**
```hcl
# Bucket for system documents
resource "aws_s3_bucket" "documents_bucket" {
  bucket = "bos-documents-${var.environment}-${random_string.bucket_suffix.result}"
  
  tags = {
    Project     = "BuildingOS"
    Environment = title(var.environment)
    ManagedBy   = "Terraform"
    Purpose     = "DocumentStorage"
  }
}

# Document versioning
resource "aws_s3_bucket_versioning" "documents_bucket_versioning" {
  bucket = aws_s3_bucket.documents_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

#### **4.2 Create Additional DynamoDB Tables**
- Table for ERP data (cache)
- Table for broker reservations
- Table for access history

### **PHASE 5: REFINEMENTS AND OPTIMIZATIONS** ⚡
*Priority: LOW - Estimated Duration: 5-7 days*

#### **5.1 Separate IAM Roles per Agent**
- Implement least privilege principle
- Function-specific roles

#### **5.2 Add Advanced Monitoring**
- Custom CloudWatch Dashboards
- Performance alerts
- Custom metrics

#### **5.3 Implement API Gateway for Agents**
- Specific endpoints for each agent
- OpenAPI documentation

---

## 📊 **3. TIMELINE AND ESTIMATES**

| **Phase** | **Duration** | **Dependencies** | **Resources** |
|----------|-------------|------------------|--------------|
| Phase 0 | 2-3 days | None | 1 dev |
| Phase 1 | 3-5 days | Phase 0 complete | 1 dev |
| Phase 2 | 10-15 days | Phase 1 complete | 2 devs |
| Phase 3 | 7-10 days | Phase 1 complete | 1 specialist dev |
| Phase 4 | 5-7 days | Phase 2 complete | 1 dev |
| Phase 5 | 5-7 days | All phases | 1 dev |

**Total estimated: 32-47 development days**

---

## 🎯 **4. IMMEDIATE NEXT STEPS**

1. **NOW**: Standardize agent naming (Phase 0.1)
2. **This week**: Complete naming standardization and implement `intention_result_topic` + rename `task_completion_topic` to `task_result_topic` (Phase 0 + Phase 1)
3. **Next week**: Start `agent_erp` implementation (Phase 2.1)
4. **Parallel**: Prepare documentation structure for new agents

## 🚨 **5. RISKS AND MITIGATIONS**

| **Risk** | **Impact** | **Mitigation** |
|-----------|-------------|---------------|
| External dependencies (ERP/Broker APIs) | High | Mocks and isolated tests first |
| Kendra integration complexity | Medium | Incremental implementation with documentation |
| Agent integration complexity | High | Continuous end-to-end testing |
| Function renaming disruption | Medium | Careful coordination and testing |

---

## 📝 **6. VALIDATION CRITERIA**

### **Phase 0 Success Criteria:**
- [ ] All agent function names follow `bos-agent-<name>-${var.environment}` pattern
- [ ] All references to renamed functions updated
- [ ] No broken integrations after renaming
- [ ] System functionality verified after changes

### **Phase 1 Success Criteria:**
- [ ] `task_completion_topic` renamed to `task_result_topic`
- [ ] `intention_result_topic` created and functional
- [ ] Director Agent publishes to intention_result_topic
- [ ] Persona Agent receives intention results
- [ ] All integration agents updated to use task_result_topic
- [ ] End-to-end message flow working

### **Phase 2 Success Criteria:**
- [ ] All 4 missing agents implemented
- [ ] Each agent responds to task requests via task_result_topic
- [ ] Integration with external systems working
- [ ] Task result flow functional

### **Phase 3 Success Criteria:**
- [ ] Kendra index deployed and configured
- [ ] Persona Agent RAG functionality working
- [ ] Document indexing and search operational

### **Phase 4 Success Criteria:**
- [ ] S3 document storage functional
- [ ] Additional DynamoDB tables created
- [ ] File upload/download working

### **Phase 5 Success Criteria:**
- [ ] Separate IAM roles implemented
- [ ] Monitoring dashboards active
- [ ] API Gateway endpoints documented

---

## 🔄 **7. ARCHITECTURAL ALIGNMENT VERIFICATION**

After completion of all phases, the implementation should fully align with the defined architecture:

- ✅ All 9 agents implemented (4 core + 5 integration)
- ✅ Consistent naming convention across all agents
- ✅ Complete SNS event bus (5 topics with standardized naming)
- ✅ Standardized `_result` pattern for all response topics
- ✅ Full data layer (DynamoDB + Kendra + S3)
- ✅ RAG functionality operational
- ✅ External system integrations working
- ✅ Proper security and monitoring in place

This plan ensures systematic alignment between the architectural vision and the actual implementation while maintaining existing functionality and minimizing disruption.
