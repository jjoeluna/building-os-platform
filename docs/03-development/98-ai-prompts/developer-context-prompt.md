[📖 Docs](../README.md) > [🛠️ Development](./README.md) > **Developer Context Prompt**

---

# Developer Context Prompt

## 📋 Overview

This prompt provides essential development context for AI assistants when working on implementation, debugging, and testing tasks in the BuildingOS platform. **Now enhanced with Sprint-based development methodology and comprehensive documentation practices.**

---

## 🚨 **CRITICAL DOCUMENTATION STRUCTURE AWARENESS**

**MANDATORY:** Before starting any development work, you MUST:

1. **Find the Main Documentation Index:** Always start by reading `docs/README.md` - this is the **main documentation index** that contains the complete project structure and navigation guide.

2. **Understand Documentation Tree:** Review `docs/documentation-tree.md` for the complete project structure overview and quick navigation paths.

3. **Locate Relevant Documents:** Use the documentation structure to find the specific documents you need for your task.

### **Documentation Navigation Strategy:**
- **Start Here:** `docs/README.md` - Main documentation index
- **Structure Overview:** `docs/documentation-tree.md` - Complete project structure
- **Development Focus:** `docs/03-development/README.md` - Development-specific documentation
- **Current Sprint:** `docs/03-development/01-project-management/current-sprint.md` - Active sprint status
- **Architecture Reference:** `docs/02-architecture/README.md` - System architecture
- **Operations Reference:** `docs/04-operations/README.md` - Operations and monitoring

### **Quick Documentation Paths:**
- **For New Features:** `docs/03-development/01-project-management/current-sprint.md` → `docs/02-architecture/01-solution-architecture/solution-architecture.md`
- **For API Changes:** `docs/02-architecture/05-api-contract/api-contract.md` → `docs/03-development/02-cli-commands-reference/cli-commands-reference.md`
- **For Infrastructure:** `docs/04-operations/terraform-best-practices-checklist.md` → `docs/03-development/05-deployment-guide/README.md`
- **For Monitoring:** `docs/04-operations/01-monitoring-strategy/README.md` → `docs/04-operations/02-runbook-template/runbook-template.md`

---

## 👨‍💻 **DEVELOPER CONTEXT PROMPT**

### **Copy this prompt for development sessions:**

```
I'm working on the BuildingOS platform - an intelligent building operating system with a distributed agent-based architecture. You're helping with DEVELOPMENT TASKS (implementation, debugging, testing) using Sprint-based methodology.

## PROJECT BASICS

**Platform:** BuildingOS - Serverless AWS multi-agent system
**Repository:** jjoeluna/building-os-platform (main branch)
**Environment:** `c:\Projects\building-os-platform` (Windows/PowerShell)
**Active Env:** dev (us-east-1)
**API Gateway:** https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com

**Tech Stack:** AWS Lambda, SNS, DynamoDB, API Gateway, Terraform
**Agents:** persona, director, coordinator, elevator, psim

## 🚨 **CRITICAL LANGUAGE REQUIREMENT**

**MANDATORY:** All documentation, software implementation, and comments MUST be written in English.

### **Documentation Standards:**
- **All technical documentation:** Architecture documents, API contracts, runbooks, README files
- **All code comments:** Function documentation, inline comments, docstrings
- **All variable names:** Use descriptive English names following Python conventions
- **All function names:** Use clear English function names
- **All error messages:** Provide error messages in English
- **All log messages:** Write log messages in English
- **All commit messages:** Use English for Git commit messages
- **All documentation updates:** Sprint status, lessons learned, process documentation

### **Code Standards:**
- **Variable naming:** `user_id`, `building_data`, `elevator_status`
- **Function naming:** `process_elevator_request()`, `validate_user_permissions()`
- **Class naming:** `ElevatorAgent`, `UserManager`, `BuildingController`
- **Error messages:** "Invalid user credentials", "Elevator service unavailable"
- **Log messages:** "Processing elevator request for floor 5", "User authentication successful"

## 📚 INDEX OF IMPORTANT FILES FOR DEVELOPMENT

### **🚀 Sprint and Control Documents**
- **[Current Sprint](../01-project-management/current-sprint.md)** - Active sprint, objectives, progress
- **[Development Status](../01-project-management/README.md)** - Development control system
- **[Backlog](../01-project-management/backlog.md)** - Prioritized backlog and estimates
- **[Metrics](../01-project-management/metrics.md)** - KPIs and quality metrics
- **[Completed Work](../01-project-management/completed.md)** - Completed work and lessons learned

### **🛠️ Core Development Documents**
- **[CLI Commands](../02-cli-commands-reference/cli-commands-reference.md)** - CLI commands and procedures
- **[Setup Guide](../03-setup-guide/setup-guide.md)** - Environment setup guide
- **[Testing Tools](../04-testing-tools/README.md)** - Testing tools and strategies
- **[Deployment Guide](../05-deployment-guide/README.md)** - Deployment and CI/CD guide
- **[Code Standards](../06-code-standards/README.md)** - Code standards and best practices

### **🏗️ Architecture Documents (Reference)**
- **[Solution Architecture](../../02-architecture/01-solution-architecture/solution-architecture.md)** - General system architecture
- **[API Contract](../../02-architecture/05-api-contract/api-contract.md)** - OpenAPI specification
- **[Components](../../02-architecture/04-components/README.md)** - Component architecture
- **[Data Model](../../02-architecture/03-data-model/README.md)** - DynamoDB data model
- **[SNS Topics](../../02-architecture/06-sns/README.md)** - SNS topic design

### **🔧 Operations Documents (Reference)**
- **[Monitoring Strategy](../../04-operations/01-monitoring-strategy/monitoring-strategy.md)** - Monitoring strategy
- **[Runbook Templates](../../04-operations/02-runbook-template/runbook-template.md)** - Runbook templates
- **[Post-Mortem Template](../../04-operations/03-post-mortem-template/post-mortem-template.md)** - Post-mortem template
- **[Operations Lessons](../../04-operations/99-lessons/README.md)** - Operations lessons learned

### **📚 Business Documents (Reference)**
- **[Business Context](../../00-business-context/README.md)** - Business context
- **[Project Vision](../../01-project-vision/README.md)** - Project vision
- **[Requirements](../../01-project-vision/03-initial-requirements-questionnaire.md)** - Initial requirements

### **🗂️ Important Code Structure**
- **`src/agents/`** - Lambda agent implementation
  - **`agent_persona/`** - User interface agent
  - **`agent_director/`** - Strategic agent
  - **`agent_coordinator/`** - Tactical agent
  - **`agent_elevator/`** - Elevator integration agent
  - **`agent_psim/`** - PSIM integration agent
- **`src/tools/`** - Tools and utilities
- **`src/layers/common_utils/`** - Shared utilities
- **`terraform/`** - Infrastructure as code
  - **`environments/dev/`** - Development environment
  - **`modules/`** - Reusable modules
- **`tests/`** - Unit and integration tests
  - **`api/`** - API tests
  - **`agents/`** - Agent tests
  - **`tools/`** - Tool tests

### **📋 Configuration Documents**
- **`requirements.txt`** - Python dependencies
- **`terraform.tfvars`** - Terraform variables
- **`scripts/`** - Automation scripts
- **`frontend/`** - User interface

## SPRINT-BASED DEVELOPMENT METHODOLOGY

### **Current Sprint Status - ALWAYS CHECK FIRST:**
- **Sprint Planning:** `docs/03-development/01-project-management/current-sprint.md`
- **Backlog & Priorities:** `docs/03-development/01-project-management/backlog.md`
- **Quality Metrics:** `docs/03-development/01-project-management/metrics.md`
- **Completed Work:** `docs/03-development/01-project-management/completed.md`

### **Sprint Workflow:**
1. **Daily Standup:** Update progress, blockers, next steps
2. **Feature Development:** Implement by priority, update documentation
3. **Continuous Testing:** Unit tests, integration tests, performance validation
4. **Code Review:** Architecture compliance, best practices, security
5. **Sprint Review:** Demo functionality, gather feedback
6. **Retrospective:** Document lessons learned, process improvements

### **Documentation-First Development:**
- **BEFORE coding:** Update API contracts, component docs, ADRs
- **DURING development:** Update sprint status, technical docs
- **AFTER completion:** Update runbooks, lessons learned, metrics

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
- **NEW:** Sprint-based feature flags and versioning
- **LANGUAGE:** All code, comments, and documentation MUST be in English

**File Operations:**
- Use absolute paths: `c:\Projects\building-os-platform\...`
- Use `replace_string_in_file` with 3-5 lines context
- PowerShell commands for terminal operations

## DOCUMENTATION AUTHORITIES

**ALWAYS check these first:**
1. `docs/03-development/01-project-management/current-sprint.md` - **Current sprint status and priorities**
2. `docs/02-architecture/05-api-contract/api-contract.md` - **API design authority**
3. `docs/03-development/01-project-management/backlog.md` - **Feature priorities and estimates**
4. `docs/03-development/02-cli-commands-reference/cli-commands-reference.md` - **CLI procedures**
5. `terraform/environments/dev/main.tf` - **Infrastructure state**

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
- **Sprint Planning:** `diagnose_api.py` to assess current state
- **During Development:** `diagnose_api.py` for rapid feedback
- **Sprint Review:** `run_tests.py` for complete validation
- **Pre-Deploy:** Both tools for confidence

## SPRINT-BASED DEVELOPMENT WORKFLOW

### **Feature Development Process:**
1. **Sprint Planning:** Review backlog, estimate effort, set priorities
2. **Documentation First:** Update API contracts, component docs, ADRs
3. **Implementation:** Code with continuous testing and documentation
4. **Code Review:** Architecture compliance, security, best practices
5. **Testing:** Unit, integration, performance, security tests
6. **Sprint Review:** Demo, feedback, validation
7. **Documentation Update:** Complete technical docs, runbooks, lessons learned

### **Daily Development Workflow:**
1. **Morning:** Check sprint status, update progress, identify blockers
2. **Development:** Implement features by priority with continuous testing
3. **Evening:** Update sprint status, document progress, plan next day

### **Code Changes Workflow:**
1. **Update Documentation:** API contracts, component docs, sprint status
2. **Edit Source Code:** Make changes in `src/agents/{agent_name}/app.py`
3. **Install Dependencies:** Run `.\scripts\build_lambdas.ps1 -LambdaName {agent_name} -Type agents`
4. **Deploy via Terraform:** Run `terraform plan` and `terraform apply` from `terraform/environments/dev/`
5. **Test Changes:** Use `diagnose_api.py` for rapid validation
6. **Complete Validation:** Use `run_tests.py` for full test suite
7. **Update Sprint Status:** Document progress, blockers, next steps

### **Quality Gates:**
- **Code Quality:** 90%+ test coverage, no critical security issues
- **Documentation:** All changes documented, API contracts updated
- **Performance:** Response times within SLA, no regressions
- **Security:** Security review completed, vulnerabilities addressed
- **Language:** All code and documentation in English

**Python Code Deployment Process:**
```bash
# 1. Update documentation first
# Edit: docs/02-architecture/05-api-contract/api-contract.md
# Edit: docs/03-development/01-project-management/current-sprint.md

# 2. Make code changes in source files
# Edit: src/agents/agent_elevator/app.py

# 3. Install/update dependencies if needed
.\scripts\build_lambdas.ps1 -LambdaName agent_elevator -Type agents

# 4. Deploy via Terraform (Infrastructure as Code)
cd terraform/environments/dev
terraform plan     # Review changes
terraform apply    # Deploy changes

# 5. Validate deployment
cd ..\..\tests\api
python diagnose_api.py    # Quick validation
python run_tests.py       # Complete suite

# 6. Update sprint status
# Edit: docs/03-development/01-project-management/current-sprint.md
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

# Sprint Status Check
# Check current sprint: docs/03-development/01-project-management/current-sprint.md
# Check backlog: docs/03-development/01-project-management/backlog.md

# Python Code Changes Workflow
# 1. Update docs: docs/02-architecture/05-api-contract/api-contract.md
# 2. Edit source code: src/agents/{agent_name}/app.py
# 3. Install dependencies: .\scripts\build_lambdas.ps1 -LambdaName {agent_name} -Type agents
# 4. Deploy via Terraform: cd terraform/environments/dev && terraform apply
# 5. Test changes: cd tests\api && python diagnose_api.py
# 6. Update sprint status: docs/03-development/01-project-management/current-sprint.md

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

Refer to `docs/03-development/01-project-management/current-sprint.md` for:
- Current sprint objectives and priorities
- Active features being developed
- Blockers and dependencies
- Sprint timeline and milestones
- Quality metrics and targets

**Always start by checking the current sprint status before beginning any development work.**

Ask specific questions about the current task. Reference existing documentation before suggesting changes.
```

---

## 🔧 **Usage Guidelines**

### **When to Use This Prompt:**
- Implementation tasks within current sprint
- Bug fixes and debugging
- Code refactoring
- Testing and validation
- CLI operations
- Infrastructure deployment
- Sprint planning and execution

### **Customization:**
Replace these based on current session:
- Current sprint number and objectives
- Specific features being developed
- Recent changes since last session
- Particular focus area (frontend/backend/infrastructure)

### **Documentation Dependencies:**
This prompt references authoritative documents. Always check:
1. Current sprint status for active priorities
2. Development status for current state
3. API contract for endpoint specifications
4. CLI reference for procedures
5. Infrastructure files for current configuration

---

## 🚀 **CI/CD Pipeline Integration**

### **📋 Pipeline Overview**
The BuildingOS platform uses a **comprehensive CI/CD pipeline** that automatically validates, tests, and deploys changes across multiple environments.

### **🔄 Pipeline Stages**

#### **1. Validation Stage (All PRs and Pushes)**
- **Code Quality:** Flake8 linting, complexity checks (max 10, line length 127)
- **Security Scanning:** Bandit (Python vulnerabilities), Safety (dependency vulnerabilities)
- **Unit Testing:** Pytest with coverage reports (target >80%)
- **Infrastructure Validation:** TFLint, Terraform validate, Terraform plan
- **PR Comments:** Automatic Terraform plan comments on PRs

#### **2. Integration Testing (Push to main)**
- **API Testing:** Endpoint validation and health checks
- **Performance Testing:** Load and latency testing
- **Integration Tests:** Cross-component testing

#### **3. Deployment Pipeline (Push to main)**
- **Dev Environment:** Automatic deployment with validation
- **Staging Environment:** Deployment after dev success
- **Production Environment:** Deployment after staging success
- **Post-Deployment:** Health checks and monitoring setup

### **🎯 Developer Responsibilities in CI/CD**

#### **Before Making Changes:**
1. **Check Current Sprint:** Review `current-sprint.md` for priorities
2. **Plan Implementation:** Consider how changes affect existing functionality
3. **Update Documentation:** Ensure implementation docs reflect planned changes

#### **During Development:**
1. **Follow Code Standards:** Ensure code meets pipeline validation requirements
2. **Write Tests:** Include unit tests for all new functionality
3. **Update Documentation:** Keep implementation docs current

#### **After Changes:**
1. **Monitor Pipeline:** Check GitHub Actions for validation results
2. **Review PR Comments:** Check Terraform plan comments
3. **Validate Deployment:** Ensure changes deploy successfully
4. **Update Sprint Status:** Document progress and lessons learned

### **🔍 Pipeline Monitoring**

#### **GitHub Actions Dashboard:**
- **URL:** `https://github.com/jjoeluna/building-os-platform/actions`
- **Monitor:** Validation results, test coverage, deployment status

#### **Key Pipeline Files:**
- **`.github/workflows/ci_cd_pipeline.yml`** - Main pipeline configuration
- **`tests/api/`** - Integration tests
- **`terraform/environments/`** - Environment-specific configurations

#### **Pipeline Triggers:**
- **Pull Requests:** Validation and testing only
- **Push to main:** Full pipeline (validation → integration → deploy)
- **Push to develop:** Validation and testing

### **🚨 Pipeline Best Practices**

#### **Code Quality:**
- **Follow PEP 8:** Ensure code passes flake8 validation
- **Type Hints:** Use type hints for better code quality
- **Documentation:** Include docstrings and comments

#### **Testing:**
- **Unit Tests:** Write tests for all new functionality
- **Integration Tests:** Ensure cross-component compatibility
- **Coverage:** Maintain high test coverage (>80%)

#### **Infrastructure:**
- **Terraform Validation:** Ensure infrastructure changes are valid
- **Plan Review:** Review Terraform plans before deployment
- **Environment Consistency:** Maintain consistency across environments

#### **Security:**
- **Vulnerability Scanning:** Address security issues promptly
- **Dependency Management:** Keep dependencies updated
- **Access Control:** Follow least privilege principles

### **📊 Pipeline Metrics**

#### **Key Performance Indicators:**
- **Build Success Rate:** >95% successful builds
- **Test Coverage:** >80% code coverage
- **Deployment Time:** <15 minutes end-to-end
- **Rollback Time:** <5 minutes for critical issues

#### **Quality Gates:**
- **Code Quality:** Pass all linting checks
- **Security:** No critical vulnerabilities
- **Testing:** All tests pass with >80% coverage
- **Infrastructure:** Terraform plan validation successful

### **🔄 Pipeline Workflow**

#### **Development Workflow:**
1. **Create Feature Branch:** `git checkout -b feature/your-feature`
2. **Make Changes:** Follow coding standards and write tests
3. **Commit Changes:** Use descriptive commit messages
4. **Push Branch:** `git push origin feature/your-feature`
5. **Create PR:** Request review and trigger validation
6. **Monitor Pipeline:** Check GitHub Actions for results
7. **Address Issues:** Fix any validation failures
8. **Merge PR:** Merge after approval and successful validation

#### **Deployment Workflow:**
1. **Push to main:** Triggers full pipeline
2. **Validation:** Code quality, security, testing
3. **Integration Testing:** Cross-component validation
4. **Dev Deployment:** Automatic deployment to dev environment
5. **Staging Deployment:** Deployment to staging after dev success
6. **Production Deployment:** Deployment to production after staging success
7. **Monitoring Setup:** Automatic monitoring configuration
8. **Health Checks:** Post-deployment validation

### **🎯 Success Criteria**

#### **Pipeline Success:**
- ✅ **All validations pass:** Code quality, security, testing
- ✅ **Deployment successful:** All environments deployed successfully
- ✅ **Health checks pass:** Post-deployment validation successful
- ✅ **Monitoring active:** Dashboards and alerts configured

#### **Development Success:**
- ✅ **Code quality:** Passes all linting and quality checks
- ✅ **Test coverage:** >80% coverage maintained
- ✅ **Functionality:** New features work as expected
- ✅ **Integration:** Cross-component compatibility maintained

---

**Last Updated**: August 7, 2025  
**Version**: 2.0 (Sprint-based methodology)  
**Authors**: Jomil & GitHub Copilot

---

**Navigation:**
⬅️ **Previous:** [CLI Commands Reference](./02-cli-commands-reference.md)  
➡️ **Next:** [Development Prompts](./development-prompts.md)  
🏠 **Up:** [Development Index](./README.md)
