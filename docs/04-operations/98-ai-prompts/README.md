# AI Prompts - Operations

## 📋 Overview

This directory contains AI context prompts specifically designed for **operations work** on the BuildingOS platform. These prompts provide comprehensive context for AI assistants when working on monitoring, incident response, deployment management, and production operations using Sprint-based methodology.

---

## 🚨 **CRITICAL DOCUMENTATION STRUCTURE AWARENESS**

**MANDATORY:** Before starting any operations work, AI assistants MUST:

1. **Find the Main Documentation Index:** Always start by reading `docs/README.md` - this is the **main documentation index** that contains the complete project structure and navigation guide.

2. **Understand Documentation Tree:** Review `docs/documentation-tree.md` for the complete project structure overview and quick navigation paths.

3. **Locate Relevant Documents:** Use the documentation structure to find the specific documents you need for your task.

### **Documentation Navigation Strategy:**
- **Start Here:** `docs/README.md` - Main documentation index
- **Structure Overview:** `docs/documentation-tree.md` - Complete project structure
- **Operations Focus:** `docs/04-operations/README.md` - Operations-specific documentation
- **Monitoring Strategy:** `docs/04-operations/01-monitoring-strategy/README.md` - Monitoring and alerting system
- **Development Reference:** `docs/03-development/README.md` - Development status and current sprint
- **Architecture Reference:** `docs/02-architecture/README.md` - System architecture

### **Quick Documentation Paths:**
- **For Monitoring Issues:** `docs/04-operations/01-monitoring-strategy/README.md` → `docs/04-operations/02-runbook-template/runbook-template.md`
- **For Incident Response:** `docs/04-operations/03-post-mortem-template/post-mortem-template.md` → `docs/04-operations/99-lessons/README.md`
- **For Deployment Support:** `docs/03-development/01-project-management/current-sprint.md` → `docs/03-development/05-deployment-guide/README.md`
- **For Infrastructure Issues:** `docs/04-operations/terraform-best-practices-checklist.md` → `docs/04-operations/terraform-refactoring-guide.md`

---

## 🔧 **Available Prompts**

### **Operations Context Prompt**
**File:** `operations-context-prompt.md`

**Purpose:** Primary context prompt for AI assistants working on operational tasks, monitoring, and production management.

**Key Features:**
- **Sprint-Based Methodology:** Integrated with operations sprint cycles
- **Operations-First Approach:** Focus on monitoring, alerting, and production management
- **Documentation Standards:** Comprehensive documentation requirements
- **Best Practices:** AWS serverless patterns, event-driven architecture
- **Quality Gates:** Operational excellence and reliability standards
- **English Language Requirement:** All documentation, code, and comments must be in English
- **CI/CD Pipeline Integration:** Comprehensive pipeline understanding and operational responsibilities
- **Documentation Structure Awareness:** Mandatory navigation to main documentation index

**Use Cases:**
- System monitoring and health checks
- Incident response and troubleshooting
- Deployment coordination and management
- Performance optimization and capacity planning
- Security monitoring and compliance
- Sprint-based operational planning
- CI/CD pipeline operations and monitoring

**Sprint Integration:**
- Check current development sprint status
- Coordinate operations with development deployments
- Update operational documentation with sprint progress
- Document operational lessons learned

**CI/CD Pipeline Integration:**
- Monitor pipeline deployments and health checks
- Coordinate operational activities with deployment schedules
- Ensure operational readiness for deployments
- Update operational procedures for pipeline changes

---

## 🎯 **Usage Guidelines**

### **When to Use Operations Prompts:**
- **Daily Operations:** Health checks, performance monitoring, log analysis
- **Incident Response:** Service outages, performance issues, security incidents
- **Deployment Support:** Coordinate with development team on deployments
- **Capacity Planning:** Resource scaling, performance optimization
- **Security Operations:** Access reviews, compliance monitoring
- **Sprint Coordination:** Align operations with development sprint
- **CI/CD Pipeline Operations:** Monitor and support pipeline deployments

### **Prompt Customization:**
- **Sprint Context:** Always include current development sprint status
- **Operational Focus:** Specify the operational area (monitoring, deployment, security)
- **Documentation Requirements:** Include required runbook updates
- **Incident Priority:** Define incident severity and response procedures
- **Pipeline Integration:** Consider CI/CD pipeline impact and requirements

### **Documentation Integration:**
- **Runbooks:** Create/update operational procedures
- **Monitoring Strategy:** Update monitoring and alerting configuration
- **Incident Reports:** Document incidents and lessons learned
- **Sprint Status:** Update operational aspects of sprint progress
- **Pipeline Docs:** Update pipeline operational procedures

---

## 📚 **Related Documentation**

### **Operations Documents:**
- **[Monitoring Strategy](../01-monitoring-strategy/monitoring-strategy.md)** - Monitoring and alerting strategy
- **[Runbook Templates](../02-runbook-template/runbook-template.md)** - Operational procedure templates
- **[Post-Mortem Template](../03-post-mortem-template/post-mortem-template.md)** - Incident analysis templates
- **[Lessons Learned](../99-lessons/README.md)** - Operational lessons learned

### **Development Documents:**
- **[Current Sprint](../../03-development/01-project-management/current-sprint.md)** - Active development sprint
- **[Development Status](../../03-development/01-project-management/README.md)** - Development control system
- **[CLI Commands](../../03-development/02-cli-commands-reference/cli-commands-reference.md)** - Operational commands

### **Architecture Documents:**
- **[Solution Architecture](../../02-architecture/01-solution-architecture/solution-architecture.md)** - System architecture
- **[Components](../../02-architecture/04-components/README.md)** - Component architecture
- **[Data Model](../../02-architecture/03-data-model/README.md)** - Data architecture

### **CI/CD Pipeline Documents:**
- **[CI/CD Pipeline](../../03-development/05-deployment-guide/README.md)** - Pipeline documentation
- **[GitHub Actions](../../03-development/05-deployment-guide/README.md)** - Pipeline configuration
- **[Monitoring Strategy](../01-monitoring-strategy/monitoring-strategy.md)** - Pipeline monitoring

---

## 🔄 **Version History**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-08-07 | Initial operations prompt | Jomil & GitHub Copilot |
| 2.0 | 2025-08-07 | Sprint-based methodology, documentation practices | Jomil & GitHub Copilot |
| 3.0 | 2025-01-09 | CI/CD Pipeline integration, comprehensive pipeline understanding | Jomil & GitHub Copilot |

---

## 🎯 **Best Practices**

### **Operations Work:**
- **Documentation-First:** Update runbooks before operational changes
- **Sprint Coordination:** Align operations with development sprint
- **Proactive Monitoring:** Set up alerts before issues occur
- **Incident Learning:** Document and learn from all incidents
- **Process Improvement:** Continuously improve operational procedures
- **Pipeline Compliance:** Ensure operational procedures meet CI/CD pipeline requirements

### **AI Assistant Usage:**
- **Context Provision:** Always provide comprehensive operational context
- **Sprint Status:** Check current development sprint status
- **Documentation Updates:** Ensure all operational changes are documented
- **Incident Management:** Follow proper incident response procedures

### **Sprint Integration:**
- **Daily Coordination:** Align daily operations with development progress
- **Deployment Support:** Coordinate operational support for deployments
- **Incident Impact:** Assess impact of incidents on sprint progress
- **Retrospectives:** Document operational insights and improvements

---

## 🚨 **Incident Response Workflow**

### **For Service Outages:**
1. Check current sprint status and impact
2. Follow incident response procedures
3. Coordinate with development team
4. Update runbooks with lessons learned
5. Document sprint impact and recovery

### **For Performance Issues:**
1. Assess impact on sprint objectives
2. Coordinate optimization with development team
3. Update monitoring and alerting
4. Document performance improvements
5. Update sprint status with resolution

### **For Security Incidents:**
1. Assess security impact on sprint
2. Follow security incident procedures
3. Coordinate with development team on fixes
4. Update security procedures and runbooks
5. Document security lessons learned

---

## 📊 **Monitoring Integration**

### **Sprint-Based Monitoring:**
- **Development Metrics:** Monitor metrics relevant to current sprint
- **Deployment Tracking:** Track deployment success and impact
- **Performance Baselines:** Maintain performance baselines for sprint features
- **Quality Gates:** Monitor quality metrics for sprint deliverables

### **Operational Metrics:**
- **System Health:** Monitor overall system health and availability
- **Performance:** Track response times, throughput, error rates
- **Cost Management:** Monitor AWS costs and optimization opportunities
- **Security:** Track security metrics and compliance status

---

**Navigation:**
⬅️ **Previous:** [Development AI Prompts](../../03-development/98-ai-prompts/README.md)  
➡️ **Next:** [Monitoring Strategy](../01-monitoring-strategy/monitoring-strategy.md)  
🏠 **Up:** [Operations Index](../README.md)
