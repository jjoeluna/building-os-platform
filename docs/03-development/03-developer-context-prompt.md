[📖 Docs](../README.md) > [🛠️ Development](./README.md) > **Developer Context Prompt**

---

# Developer Context Prompt

## 📋 Overview

This prompt provides essential development context for AI assistants when working on implementation, debugging, and testing tasks in the BuildingOS platform.

---

## 👨‍💻 **DEVELOPER CONTEXT PROMPT**

### **Copy this prompt for development sessions:**

```
I'm working on the BuildingOS platform - an intelligent building operating system with a distributed agent-based architecture. You're helping with DEVELOPMENT TASKS (implementation, debugging, testing).

## PROJECT BASICS

**Platform:** BuildingOS - Serverless AWS multi-agent system
**Repository:** jjoeluna/building-os-platform (main branch)
**Environment:** `c:\Projects\building-os-platform` (Windows/PowerShell)
**Active Env:** dev (us-east-1)
**API Gateway:** https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com

**Tech Stack:** AWS Lambda, SNS, DynamoDB, API Gateway, Terraform
**Agents:** persona, director, coordinator, elevator, psim

## DEVELOPMENT STANDARDS

**Naming Convention:**
- Lambda: `bos-agent-{name}-{environment}`
- SNS: `bos-{topic-name}-topic-{environment}`
- DynamoDB: `bos-{table-name}-{environment}`

**Code Standards:**
- Follow `src/agents/persona_agent/app.py` pattern for hybrid architecture
- Include CORS headers for frontend compatibility
- Standardized error responses with `error` field
- Environment variables for configuration
- Proper logging for debugging

**File Operations:**
- Use absolute paths: `c:\Projects\building-os-platform\...`
- Use `replace_string_in_file` with 3-5 lines context
- PowerShell commands for terminal operations

## DOCUMENTATION AUTHORITIES

**ALWAYS check these first:**
1. `docs/02-architecture/02-api-contract.md` - **API design authority**
2. `docs/03-development/01-development-status.md` - **Current implementation status**
3. `docs/03-development/02-cli-commands-reference.md` - **CLI procedures**
4. `terraform/environments/dev/main.tf` - **Infrastructure state**

## TESTING TOOLS

**Available Test Suite in `tests/api/`:**

**🔍 `diagnose_api.py` - Rapid Diagnostics**
- ⚡ Quick execution (~30 seconds)
- 🔗 CloudWatch logs integration
- 🎯 Automatic problem prioritization  
- 📊 Real-time performance analysis
- **Use for:** Quick validation during development

**🧪 `run_tests.py` - Comprehensive Testing**
- 🔬 24 structured pytest cases
- 📋 Detailed HTML/JSON reports
- 🔄 Retry logic and timeouts
- 📈 Quality metrics and performance data
- **Use for:** Complete validation and documentation

**Testing Strategy per Development Phase:**
- **Initial:** `diagnose_api.py` to map current issues
- **During Development:** `diagnose_api.py` for rapid feedback
- **Post-Implementation:** `run_tests.py` for full validation
- **Pre-Deploy:** Both tools for complete confidence

## DEVELOPMENT WORKFLOW

**Documentation-First Approach:**
1. Update API contract BEFORE implementing endpoints
2. Update CLI reference with new commands
3. **Progressive Testing:** Use `diagnose_api.py` for quick validation during development
4. **Complete Validation:** Use `run_tests.py` for comprehensive testing post-changes
5. Update development status with results

**Code Changes Workflow:**
1. **Edit Source Code:** Make changes in `src/agents/{agent_name}/app.py`
2. **Install Dependencies:** Run `.\scripts\build_lambdas.ps1 -LambdaName {agent_name} -Type agents`
3. **Deploy via Terraform:** Run `terraform plan` and `terraform apply` from `terraform/environments/dev/`
4. **Test Changes:** Use `diagnose_api.py` for rapid validation
5. **Complete Validation:** Use `run_tests.py` for full test suite

**Testing Strategy:**
- **Rapid Feedback Loop:** `diagnose_api.py` → fix → test again
- **Validation Checkpoints:** `run_tests.py` after major changes
- **Baseline Documentation:** Save test results for comparison
- **Quality Gates:** Achieve 90%+ test pass rate before deployment

**Python Code Deployment Process:**
```bash
# 1. Make code changes in source files
# Edit: src/agents/agent_elevator/app.py

# 2. Install/update dependencies if needed
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents

# 3. Deploy via Terraform (Infrastructure as Code)
cd terraform/environments/dev
terraform plan     # Review changes
terraform apply    # Deploy changes

# 4. Validate deployment
cd ..\..\tests\api
python diagnose_api.py    # Quick validation
python run_tests.py       # Complete suite
```

**IMPORTANT: Never Deploy Code Directly to AWS**
- ❌ **Wrong:** `aws lambda update-function-code` (breaks Infrastructure as Code)
- ✅ **Correct:** `terraform apply` (maintains IaC consistency)
- **Reason:** Terraform uses `source_code_hash` to detect changes and manages deployments

**Testing Requirements:**
- **Primary Tools:** Use Python test suite in `tests/api/`
- **Quick Diagnosis:** `python tests\api\diagnose_api.py` for rapid troubleshooting
- **Complete Validation:** `python tests\api\run_tests.py` for full test suite
- **Environment:** Always activate `.venv` before testing
- **Progressive Testing:** Test incrementally after each change
- **Post-Deploy:** Validate with both diagnostic and complete test tools

**Testing Workflow:**
```bash
# 1. Setup testing environment
.\.venv\Scripts\Activate.ps1
cd tests\api

# 2. Quick diagnosis (30s) - for rapid feedback
python diagnose_api.py

# 3. Specific endpoint testing during development
python -m pytest test_endpoints.py::TestElevatorEndpoint -v

# 4. Complete validation after major changes
python run_tests.py

# 5. Legacy curl testing (when needed)
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health"
```

## COMMON COMMANDS

```bash
# Environment status
terraform output
aws apigatewayv2 get-routes --api-id pj4vlvxrg7 --region us-east-1 --output table

# Python Code Changes Workflow
# 1. Edit source code: src/agents/{agent_name}/app.py
# 2. Install dependencies: .\scripts\build_lambdas.ps1 -LambdaName {agent_name} -Type agents
# 3. Deploy via Terraform: cd terraform/environments/dev && terraform apply
# 4. Test changes: cd tests\api && python diagnose_api.py

# API Testing (Primary Method)
.\.venv\Scripts\Activate.ps1
cd tests\api
python diagnose_api.py                                    # Quick diagnosis
python run_tests.py                                       # Complete suite
python -m pytest test_endpoints.py::TestElevatorEndpoint # Specific endpoint

# Lambda Dependencies Management
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents  # Install deps
.\scripts\build_lambdas.ps1 -LambdaName tool_psim -Type tools        # For tools

# Terraform Deployment (Infrastructure as Code)
cd terraform/environments/dev
terraform plan      # Review changes detected by source_code_hash
terraform apply     # Deploy code changes + infrastructure

# Legacy endpoint testing (when needed)
curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health"
curl -X POST "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/persona" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "message": "Hello"}'
```

## CURRENT FOCUS

Refer to `docs/03-development/01-development-status.md` for:
- Current implementation status
- Immediate priorities
- Recent completions
- Next steps

Ask specific questions about the current task. Reference existing documentation before suggesting changes.
```

---

## 🔧 **Usage Guidelines**

### **When to Use This Prompt:**
- Implementation tasks
- Bug fixes and debugging
- Code refactoring
- Testing and validation
- CLI operations
- Infrastructure deployment

### **Customization:**
Replace these based on current session:
- Current specific task
- Recent changes since last session
- Particular focus area (frontend/backend/infrastructure)

### **Documentation Dependencies:**
This prompt references authoritative documents. Always check:
1. Development status for current state
2. API contract for endpoint specifications
3. CLI reference for procedures
4. Infrastructure files for current configuration

---

**Last Updated**: August 7, 2025  
**Version**: 1.0  
**Authors**: Jomil & GitHub Copilot

---

**Navigation:**
⬅️ **Previous:** [CLI Commands Reference](./02-cli-commands-reference.md)  
➡️ **Next:** [Architect Context Prompt](./04-architect-context-prompt.md)  
🏠 **Up:** [Development Index](./README.md)
