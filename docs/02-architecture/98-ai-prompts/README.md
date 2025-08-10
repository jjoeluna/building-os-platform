# AI Prompts - Architecture

## 📋 Overview

This directory contains AI context prompts specifically designed for **architecture work** on the BuildingOS platform. These prompts provide comprehensive context for AI assistants when working on architectural decisions, system design, and technical planning.

---

## 🚨 **CRITICAL DOCUMENTATION STRUCTURE AWARENESS**

**MANDATORY:** Before starting any architectural work, AI assistants MUST:

1. **Find the Main Documentation Index:** Always start by reading `docs/README.md` - this is the **main documentation index** that contains the complete project structure and navigation guide.

2. **Understand Documentation Tree:** Review `docs/documentation-tree.md` for the complete project structure overview and quick navigation paths.

3. **Locate Relevant Documents:** Use the documentation structure to find the specific documents you need for your task.

### **Documentation Navigation Strategy:**
- **Start Here:** `docs/README.md` - Main documentation index
- **Structure Overview:** `docs/documentation-tree.md` - Complete project structure
- **Architecture Focus:** `docs/02-architecture/README.md` - Architecture-specific documentation
- **Solution Architecture:** `docs/02-architecture/01-solution-architecture/solution-architecture.md` - Technical blueprint and C4 diagrams
- **Development Reference:** `docs/03-development/README.md` - Development status and current sprint
- **Operations Reference:** `docs/04-operations/README.md` - Operations and monitoring

### **Quick Documentation Paths:**
- **For System Design:** `docs/02-architecture/01-solution-architecture/solution-architecture.md` → `docs/02-architecture/04-components/README.md`
- **For API Design:** `docs/02-architecture/05-api-contract/api-contract.md` → `docs/02-architecture/06-sns/README.md`
- **For Data Modeling:** `docs/02-architecture/03-data-model/README.md` → `docs/02-architecture/02-adr/`
- **For Component Architecture:** `docs/02-architecture/04-components/README.md` → `docs/02-architecture/01-solution-architecture/solution-architecture.md`

---

## 🏗️ **Available Prompts**

### **Architect Context Prompt**
**File:** `architect-context-prompt.md`

**Purpose:** Primary context prompt for AI assistants working on architectural tasks, system design, and technical planning.

**Key Features:**
- **Sprint-Based Methodology:** Integrated with development sprint cycles
- **Architecture-First Approach:** Focus on system design and technical decisions
- **Documentation Standards:** Comprehensive documentation requirements
- **Best Practices:** AWS serverless patterns, event-driven architecture
- **Quality Gates:** Architecture compliance and validation
- **English Language Requirement:** All documentation, code, and comments must be in English
- **CI/CD Pipeline Integration:** Comprehensive pipeline understanding and responsibilities
- **Documentation Structure Awareness:** Mandatory navigation to main documentation index

**Use Cases:**
- System architecture design and review
- Technical decision making (ADRs)
- API contract design and validation
- Component architecture planning
- Performance and scalability analysis
- Security architecture review
- CI/CD pipeline architecture and optimization

**Sprint Integration:**
- Check current sprint status before architectural work
- Update sprint documentation with architectural decisions
- Maintain alignment with sprint objectives
- Document architectural lessons learned

**CI/CD Pipeline Integration:**
- Understand pipeline stages and responsibilities
- Monitor pipeline validation and deployment
- Ensure architectural changes meet pipeline requirements
- Update documentation for pipeline compliance

---

## 🎯 **Usage Guidelines**

### **When to Use Architecture Prompts:**
- **System Design:** New features requiring architectural decisions
- **Technical Planning:** Infrastructure changes and improvements
- **API Design:** New endpoints and service integrations
- **Performance Optimization:** Scalability and performance improvements
- **Security Review:** Security architecture and compliance
- **Sprint Planning:** Architectural considerations for sprint planning
- **CI/CD Pipeline:** Pipeline architecture and optimization

### **Prompt Customization:**
- **Sprint Context:** Always include current sprint number and objectives
- **Architecture Focus:** Specify the architectural area (API, infrastructure, security)
- **Documentation Requirements:** Include required documentation updates
- **Quality Gates:** Define acceptance criteria and validation requirements
- **Pipeline Integration:** Consider CI/CD pipeline impact and requirements

### **Documentation Integration:**
- **ADRs:** Create/update Architecture Decision Records
- **API Contracts:** Update OpenAPI specifications
- **Component Docs:** Update technical documentation
- **Sprint Status:** Update sprint documentation with architectural progress
- **Pipeline Docs:** Update pipeline documentation and procedures

---

## 📚 **Related Documentation**

### **Architecture Documents:**
- **[Solution Architecture](../01-solution-architecture/solution-architecture.md)** - Overall system architecture
- **[API Contract](../05-api-contract/api-contract.md)** - API specifications and contracts
- **[Components](../04-components/README.md)** - Component architecture and design
- **[Data Model](../03-data-model/README.md)** - Data architecture and modeling

### **Development Documents:**
- **[Current Sprint](../../03-development/01-project-management/current-sprint.md)** - Active sprint status
- **[Development Status](../../03-development/01-project-management/README.md)** - Development control system
- **[Lessons Learned](../99-lessons/README.md)** - Architectural lessons learned

### **Operations Documents:**
- **[Monitoring Strategy](../../04-operations/01-monitoring-strategy/monitoring-strategy.md)** - Operational architecture
- **[Runbook Templates](../../04-operations/02-runbook-template/runbook-template.md)** - Operational procedures

### **CI/CD Pipeline Documents:**
- **[CI/CD Pipeline](../../03-development/05-deployment-guide/README.md)** - Pipeline documentation
- **[GitHub Actions](../../03-development/05-deployment-guide/README.md)** - Pipeline configuration

---

## 🔄 **Version History**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-08-07 | Initial architecture prompt | Jomil & GitHub Copilot |
| 2.0 | 2025-08-07 | Sprint-based methodology, documentation practices | Jomil & GitHub Copilot |
| 3.0 | 2025-01-09 | CI/CD Pipeline integration, comprehensive pipeline understanding | Jomil & GitHub Copilot |

---

## 🎯 **Best Practices**

### **Architecture Work:**
- **Documentation-First:** Update architectural documentation before implementation
- **Sprint Alignment:** Ensure architectural decisions align with sprint objectives
- **Quality Gates:** Define clear acceptance criteria for architectural work
- **Lessons Learned:** Document architectural insights and decisions
- **Pipeline Compliance:** Ensure architectural changes meet CI/CD pipeline requirements

### **AI Assistant Usage:**
- **Context Provision:** Always provide comprehensive architectural context
- **Sprint Status:** Check current sprint status before architectural work
- **Documentation Updates:** Ensure all architectural changes are documented
- **Validation:** Validate architectural decisions against existing patterns

---

**Navigation:**
⬅️ **Previous:** [Components](../04-components/README.md)  
➡️ **Next:** [Development AI Prompts](../../03-development/98-ai-prompts/README.md)  
🏠 **Up:** [Architecture Index](../README.md)
