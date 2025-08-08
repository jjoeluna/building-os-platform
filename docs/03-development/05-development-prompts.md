[📖 Docs](../README.md) > [🛠️ Development](./README.md) > **Development Prompts**

---

# Development Prompts Collection

## 📋 Overview

This document contains a curated collection of prompts for AI-assisted development, debugging, and deployment of the BuildingOS platform. These prompts are optimized for use with GitHub Copilot, Claude, and other AI coding assistants.

---

## 🚀 **1. DEVELOPMENT PROMPTS**

### **1.1 Agent Implementation**

#### **Create New Agent Prompt**
```
Create a new AWS Lambda function for {agent_name} following the BuildingOS architecture pattern.

Requirements:
- Function name: bos-agent-{agent_name}-${var.environment}
- Runtime: Python 3.11
- Handler: app.handler
- Use common_utils layer
- Environment variables: TASK_RESULT_TOPIC_ARN, MISSION_STATE_TABLE_NAME
- Implement error handling and logging
- Follow the existing agent pattern from agent_elevator

Integration points:
- Subscribe to mission tasks via coordinator
- Publish results to task_result_topic
- Store state in DynamoDB
- Integrate with external API: {external_api}

Include:
1. Lambda function definition in Terraform
2. Python app.py with handler function
3. IAM permissions
4. SNS topic subscription
5. Error handling and retry logic
```

#### **Update Agent Logic Prompt**
```
Update the {agent_name} agent to implement the following functionality:

Business Logic:
{describe_functionality}

Technical Requirements:
- Follow BuildingOS event-driven pattern
- Use existing DynamoDB tables: {table_names}
- Integrate with external API: {api_details}
- Implement proper error handling
- Add logging for debugging
- Ensure idempotency

Expected Flow:
1. Receive task from coordinator via SNS
2. {step_by_step_flow}
3. Publish result to task_result_topic

Please maintain the existing code structure and add the new functionality without breaking existing features.
```

### **1.2 Infrastructure Development**

#### **Terraform Module Creation Prompt**
```
Create a Terraform module for {resource_type} following BuildingOS patterns.

Requirements:
- Module location: terraform/modules/{module_name}/
- Include: main.tf, variables.tf, outputs.tf
- Support environment-specific naming: {resource_name}-${var.environment}
- Include common tags: Project, Environment, ManagedBy, Purpose
- Follow AWS best practices for {resource_type}

Specifications:
{detailed_specifications}

Include proper documentation and examples in the module.
```

#### **DynamoDB Table Design Prompt**
```
Design a DynamoDB table for {purpose} following BuildingOS patterns.

Requirements:
- Table name: bos-{table_name}-${var.environment}
- Primary key: {primary_key}
- Access patterns: {access_patterns}
- TTL: {ttl_requirements}
- Pay-per-request billing
- Include GSI if needed for {query_patterns}

Create:
1. Terraform module for the table
2. Python helper functions for CRUD operations
3. IAM policies for Lambda access
4. Example usage in agent code
```

### **1.3 Integration Development**

#### **External API Integration Prompt**
```
Implement integration with {external_service} API for the {agent_name} agent.

API Details:
- Base URL: {api_url}
- Authentication: {auth_method}
- Key endpoints: {endpoints}
- Rate limits: {rate_limits}

Requirements:
- Implement proper authentication handling
- Add retry logic with exponential backoff
- Handle rate limiting gracefully
- Log all API interactions
- Store credentials securely in environment variables
- Handle common error scenarios: {error_scenarios}

Create wrapper functions for each API endpoint with proper error handling and response parsing.
```

---

## 🐛 **2. DEBUGGING PROMPTS**

### **2.1 Lambda Function Debugging**

#### **Debug Lambda Errors Prompt**
```
Help debug this Lambda function error in {agent_name}:

Error Details:
- Function: {function_name}
- Error Message: {error_message}
- CloudWatch Log Group: {log_group}
- Event that triggered: {event_details}

Current Code:
{paste_relevant_code}

Environment:
- Runtime: Python 3.11
- Memory: {memory}
- Timeout: {timeout}
- Environment Variables: {env_vars}

Please analyze the error and provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Code fix with explanation
4. Prevention strategies for similar issues
```

#### **SNS Message Flow Debug Prompt**
```
Debug SNS message flow issue in BuildingOS:

Issue: Messages not flowing from {source_topic} to {target_agent}

Current Setup:
- Source Topic: {topic_arn}
- Target Function: {function_name}
- Subscription: {subscription_details}
- Lambda Permission: {permission_details}

Symptoms:
{describe_symptoms}

Recent Changes:
{recent_changes}

Please help identify:
1. Possible causes of message delivery failure
2. Step-by-step troubleshooting checklist
3. Monitoring commands to verify each step
4. Fix recommendations
```

### **2.2 Infrastructure Debugging**

#### **Terraform State Issues Prompt**
```
Help resolve Terraform state issue:

Error: {terraform_error}
Command: {terraform_command}
Environment: {environment}

Current State:
{terraform_state_relevant_portion}

Recent Changes:
{recent_changes}

Please provide:
1. Analysis of the state issue
2. Safe commands to resolve
3. Steps to prevent similar issues
4. State backup recommendations
```

#### **DynamoDB Performance Debug Prompt**
```
Debug DynamoDB performance issue:

Table: {table_name}
Issue: {performance_issue}
Metrics: {cloudwatch_metrics}

Access Patterns:
{access_patterns}

Recent Changes:
{recent_changes}

Please analyze:
1. Potential causes of performance degradation
2. CloudWatch metrics to monitor
3. Query optimization recommendations
4. Scaling considerations
```

---

## 🚢 **3. DEPLOYMENT PROMPTS**

### **3.1 Environment Setup**

#### **New Environment Deployment Prompt**
```
Deploy BuildingOS to new environment: {environment_name}

Requirements:
- Environment: {environment_name}
- Region: {aws_region}
- Copy configuration from: {source_environment}

Customizations for this environment:
{environment_specific_config}

Please provide:
1. Step-by-step deployment plan
2. Terraform commands sequence
3. Environment-specific variable files
4. Post-deployment verification checklist
5. Rollback plan if deployment fails
```

#### **Agent Deployment Pipeline Prompt**
```
Create deployment pipeline for {agent_name} agent:

Requirements:
- Source: {source_location}
- Target environments: dev, stg, prd
- Deploy on: {trigger_condition}
- Include: unit tests, integration tests
- Approval required for: production

Pipeline Steps:
1. Code validation
2. Unit tests
3. Package Lambda
4. Deploy to dev
5. Integration tests
6. {additional_steps}

Please create the deployment pipeline configuration and include proper error handling and notifications.
```

### **3.2 Production Deployment**

#### **Production Release Prompt**
```
Prepare production release for BuildingOS:

Release Version: {version}
Changes Since Last Release:
{changelog}

Components to Deploy:
{components_list}

Pre-deployment Checklist:
- [ ] All tests passing
- [ ] Staging validation complete
- [ ] Database migrations ready
- [ ] Rollback plan prepared

Please provide:
1. Detailed deployment plan
2. Risk assessment
3. Monitoring checkpoints
4. Rollback procedures
5. Communication plan
```

---

## 🔧 **4. MAINTENANCE PROMPTS**

### **4.1 Code Refactoring**

#### **Agent Code Standardization Prompt**
```
Refactor {agent_name} to follow BuildingOS coding standards:

Current Issues:
{identified_issues}

Standards to Apply:
- Error handling patterns from agent_elevator
- Logging standards
- Function naming conventions
- Code organization
- Documentation standards

Please refactor the code while maintaining all existing functionality and improving:
1. Code readability
2. Error handling
3. Logging consistency
4. Performance
5. Maintainability
```

#### **Infrastructure Optimization Prompt**
```
Optimize BuildingOS infrastructure for cost and performance:

Current Setup:
{current_infrastructure}

Optimization Goals:
- Reduce costs by {target_percentage}
- Improve performance for {specific_metrics}
- Maintain reliability standards

Areas to Review:
- Lambda memory/timeout settings
- DynamoDB provisioning
- API Gateway caching
- CloudWatch log retention

Please provide optimization recommendations with impact analysis.
```

### **4.2 Monitoring and Alerting**

#### **Monitoring Setup Prompt**
```
Create comprehensive monitoring for {component}:

Metrics to Monitor:
{metrics_list}

Alert Conditions:
{alert_conditions}

Notification Channels:
{notification_channels}

Requirements:
- CloudWatch dashboards
- Custom metrics
- Log-based alerts
- Performance baselines

Please create:
1. CloudWatch dashboard configuration
2. Alarm definitions
3. Custom metric implementations
4. Log pattern filters
5. Notification setup
```

---

## 📚 **5. DOCUMENTATION PROMPTS**

### **5.1 Technical Documentation**

#### **Agent Documentation Prompt**
```
Create comprehensive documentation for {agent_name}:

Include:
1. Purpose and responsibilities
2. Integration points
3. API endpoints (if any)
4. Event flow diagrams
5. Configuration parameters
6. Error scenarios and handling
7. Monitoring and alerts
8. Troubleshooting guide

Follow the documentation pattern from agent-elevator.md
```

#### **API Documentation Prompt**
```
Generate OpenAPI documentation for {api_name}:

Endpoints:
{endpoint_list}

Include:
- Request/response schemas
- Authentication requirements
- Error codes and messages
- Usage examples
- Rate limiting information

Follow OpenAPI 3.0 specification and include practical examples for each endpoint.
```

### **5.2 Operational Documentation**

#### **Runbook Creation Prompt**
```
Create operational runbook for {scenario}:

Scenario: {incident_type}
Impact: {impact_description}
Frequency: {frequency}

Include:
1. Symptoms and detection
2. Initial response steps
3. Diagnostic procedures
4. Resolution steps
5. Escalation procedures
6. Post-incident actions
7. Prevention measures

Follow the runbook template structure.
```

---

## 💡 **6. PROMPT USAGE GUIDELINES**

### **Best Practices:**
1. **Context First**: Always provide sufficient context about the BuildingOS architecture
2. **Specific Requirements**: Be specific about technical requirements and constraints
3. **Error Details**: Include complete error messages and relevant logs
4. **Environment Info**: Specify the environment (dev/stg/prd) and AWS region
5. **Recent Changes**: Mention any recent changes that might be related

### **Template Variables:**
- `{agent_name}`: Name of the agent (persona, director, coordinator, etc.)
- `{environment}`: Target environment (dev, stg, prd)
- `{function_name}`: AWS Lambda function name
- `{error_message}`: Complete error message from logs
- `{component}`: System component being worked on

### **Prompt Customization:**
- Replace placeholder variables with actual values
- Add specific requirements for your use case
- Include relevant code snippets or configuration
- Specify the desired output format

---

## 🔄 **7. PROMPT VERSIONING**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-08-07 | Initial prompt collection | Jomil & GitHub Copilot |

### **Update Process:**
1. Test new prompts in development environment
2. Validate effectiveness with team
3. Update version number and changelog
4. Commit changes to repository

---

**Note**: These prompts are living documents and should be updated based on experience and new requirements. Always test prompts in development environments before using in production scenarios.

---

**Navigation:**
⬅️ **Previous:** [Architect Context Prompt](./04-architect-context-prompt.md)  
➡️ **Next:** [Setup Guide](./06-setup-guide.md)  
🏠 **Up:** [Development Index](./README.md)
