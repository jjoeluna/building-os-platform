# AI Prompts - Development

## 📋 Overview

This directory contains AI context prompts specifically designed for **development work** on the BuildingOS platform. These prompts provide comprehensive context for AI assistants when working on implementation, debugging, testing, and deployment tasks using Sprint-based methodology.

---

## 🚨 **CRITICAL DOCUMENTATION STRUCTURE AWARENESS**

**MANDATORY:** Before starting any development work, AI assistants MUST:

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

## 🛠️ **Available Prompts**

### **Developer Context Prompt**
**File:** `developer-context-prompt.md`

**Purpose:** Primary context prompt for AI assistants working on development tasks, implementation, and debugging.

**Key Features:**
- **Sprint-Based Methodology:** Integrated with development sprint cycles
- **Development-First Approach:** Focus on implementation, debugging, and testing
- **Documentation Standards:** Comprehensive documentation requirements
- **Best Practices:** AWS serverless patterns, event-driven architecture
- **Quality Gates:** Code quality and testing standards
- **English Language Requirement:** All documentation, code, and comments must be in English
- **CI/CD Pipeline Integration:** Comprehensive pipeline understanding and responsibilities
- **Documentation Structure Awareness:** Mandatory navigation to main documentation index

**Use Cases:**
- Feature implementation and development
- Bug fixes and debugging
- Code refactoring and optimization
- Testing and validation
- Deployment and infrastructure management
- Sprint planning and execution
- CI/CD pipeline development and optimization

**Sprint Integration:**
- Check current sprint status before development work
- Update sprint documentation with progress
- Maintain alignment with sprint objectives
- Document development lessons learned

**CI/CD Pipeline Integration:**
- Understand pipeline stages and responsibilities
- Monitor pipeline validation and deployment
- Ensure code changes meet pipeline requirements
- Update documentation for pipeline compliance

### **Development Prompts Collection**
**File:** `development-prompts.md`

**Purpose:** Comprehensive collection of specialized prompts for different development scenarios.

**Key Features:**
- **Sprint-Based Prompts:** Planning, execution, review, retrospective
- **Development Prompts:** Agent implementation, infrastructure, integration
- **Debugging Prompts:** Lambda, SNS, Terraform, DynamoDB issues
- **Deployment Prompts:** Environment setup, production releases
- **Maintenance Prompts:** Code refactoring, optimization, monitoring
- **Documentation Prompts:** Technical and operational documentation
- **CI/CD Pipeline Prompts:** Pipeline development and optimization

**Categories:**
1. **Sprint-Based Development:** Planning, execution, review, retrospective
2. **Development:** Agent implementation, infrastructure, integration
3. **Debugging:** Lambda, SNS, Terraform, DynamoDB issues
4. **Deployment:** Environment setup, production releases
5. **Maintenance:** Code refactoring, optimization, monitoring
6. **Documentation:** Technical and operational documentation
7. **CI/CD Pipeline:** Pipeline development and optimization

---

## 🎯 **Usage Guidelines**

### **When to Use Development Prompts:**
- **Feature Development:** Implementing new features within current sprint
- **Bug Fixes:** Debugging and resolving issues
- **Code Refactoring:** Improving code quality and maintainability
- **Testing:** Unit tests, integration tests, performance validation
- **Deployment:** Infrastructure changes and production releases
- **Sprint Management:** Planning, execution, review, retrospective
- **CI/CD Pipeline:** Pipeline development and optimization

### **Prompt Customization:**
- **Sprint Context:** Always include current sprint number and objectives
- **Feature Focus:** Specify the feature or component being worked on
- **Documentation Requirements:** Include required documentation updates
- **Quality Gates:** Define acceptance criteria and validation requirements
- **Pipeline Integration:** Consider CI/CD pipeline impact and requirements

### **Documentation Integration:**
- **API Contracts:** Update OpenAPI specifications
- **Component Docs:** Update technical documentation
- **Sprint Status:** Update sprint documentation with progress
- **Runbooks:** Create/update operational procedures
- **Pipeline Docs:** Update pipeline documentation and procedures

---

## 📚 **Related Documentation**

### **Development Documents:**
- **[Current Sprint](../01-project-management/current-sprint.md)** - Active sprint status
- **[Development Status](../01-project-management/README.md)** - Development control system
- **[CLI Commands](../02-cli-commands-reference/cli-commands-reference.md)** - Development procedures
- **[Setup Guide](../03-setup-guide/setup-guide.md)** - Environment setup
- **[Lessons Learned](../99-lessons/README.md)** - Development lessons learned

### **Architecture Documents:**
- **[Solution Architecture](../../02-architecture/01-solution-architecture/solution-architecture.md)** - System architecture
- **[API Contract](../../02-architecture/05-api-contract/api-contract.md)** - API specifications
- **[Components](../../02-architecture/04-components/README.md)** - Component architecture

### **Operations Documents:**
- **[Monitoring Strategy](../../04-operations/01-monitoring-strategy/monitoring-strategy.md)** - Operational monitoring
- **[Runbook Templates](../../04-operations/02-runbook-template/runbook-template.md)** - Operational procedures

### **CI/CD Pipeline Documents:**
- **[CI/CD Pipeline](../05-deployment-guide/README.md)** - Pipeline documentation
- **[GitHub Actions](../05-deployment-guide/README.md)** - Pipeline configuration
- **[Testing Tools](../04-testing-tools/README.md)** - Testing strategies and tools

---

## 🔄 **Version History**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-08-07 | Initial development prompts | Jomil & GitHub Copilot |
| 2.0 | 2025-08-07 | Sprint-based methodology, documentation practices | Jomil & GitHub Copilot |

---

## 🎯 **Best Practices**

### **Development Work:**
- **Documentation-First:** Update documentation before implementation
- **Sprint Alignment:** Ensure development work aligns with sprint objectives
- **Quality Gates:** Meet code quality, performance, and security standards
- **Testing:** Comprehensive testing at all levels
- **Lessons Learned:** Document development insights and improvements

### **AI Assistant Usage:**
- **Context Provision:** Always provide comprehensive development context
- **Sprint Status:** Check current sprint status before development work
- **Documentation Updates:** Ensure all development changes are documented
- **Testing:** Validate all changes with appropriate tests

### **Sprint Integration:**
- **Daily Updates:** Update sprint status with daily progress
- **Quality Metrics:** Track and report quality metrics
- **Documentation:** Keep documentation current with development progress
- **Retrospectives:** Document lessons learned and process improvements

---

## 🚀 **Quick Start**

### **For New Features:**
1. Check current sprint status
2. Update API contract and component documentation
3. Implement feature with comprehensive testing
4. Update sprint status with progress
5. Create/update runbooks if needed

### **For Bug Fixes:**
1. Check current sprint status and impact
2. Update troubleshooting runbooks
3. Implement fix with regression testing
4. Update sprint status with resolution
5. Document root cause and prevention strategies

### **For Sprint Planning:**
1. Review backlog and priorities
2. Set sprint objectives and success criteria
3. Plan documentation updates needed
4. Define acceptance criteria and quality gates
5. Create sprint timeline and milestones

---

**Navigation:**
⬅️ **Previous:** [Architecture AI Prompts](../../02-architecture/98-ai-prompts/README.md)  
➡️ **Next:** [Operations AI Prompts](../../04-operations/98-ai-prompts/README.md)  
🏠 **Up:** [Development Index](../README.md)
