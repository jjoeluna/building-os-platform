# 📖 BuildingOS Project Documentation

Welcome to the central documentation for **BuildingOS**. This directory contains all the essential artifacts that define the project's vision, architecture, and operational practices.

---

## 🧭 **Quick Navigation**

| Section | Purpose | Key Documents |
|---------|---------|---------------|
| **[📊 Business Context](./00-business-context/)** | Campaign brief & business context | LIT760 Campaign Brief |
| **[📋 Project Vision](./01-project-vision/README.md)** | Business goals & requirements | Charter, Requirements, Questionnaire |
| **[🏗️ Architecture](./02-architecture/README.md)** | System design & decisions | Solution Architecture, API Contract, ADRs |
| **[🛠️ Development](./03-development/README.md)** | Implementation tools & status | Development Status, CLI Commands, Context Prompts |
| **[⚙️ Operations](./04-operations/README.md)** | Production maintenance | Monitoring, Runbooks, Post-Mortems |

---

## Documentation Index

### 📊 [00 - Business Context](./00-business-context/)

*This section provides the business context and campaign brief that initiated the BuildingOS project.*

- **[LIT760 Campaign Brief](./00-business-context/LIT760-Campaign-Brief.md):** The original campaign brief that defines the business opportunity and context.

---

### 📄 [01 - Project Vision](./01-project-vision/)

*This section defines the **"why"** of the project. It is the starting point for understanding the business goals and requirements.*

- **[Project Charter](./01-project-vision/01-charter.md):** The high-level vision, scope, stakeholders, and success metrics.
- **[Requirements](./01-project-vision/02-requirements.md):** The functional (User Stories) and non-functional (NFRs) requirements that guide development.
- **[Initial Requirements Questionnaire](./01-project-vision/03-initial-requirements-questionnaire.md):** Detailed questionnaire for gathering initial requirements and stakeholder needs.

---

### 📐 [02 - Architecture](./02-architecture/)

*This section describes **"how"** the system is designed and built.*

- **[Solution Architecture](./02-architecture/01-solution-architecture/solution-architecture.md):** The technical blueprint of the system, including C4 diagrams and architectural patterns.
- **[API Contract](./02-architecture/05-api-contract/api-contract.md):** The formal definition of our API using the OpenAPI specification.
- **[Architecture Decision Records (ADRs)](./02-architecture/02-adr/):** A log of all important architectural decisions made throughout the project.
- **[Data Model](./02-architecture/03-data-model/):** Database schemas and data relationships.
- **[Component Registry](./02-architecture/04-components/):** A list and description of all major software components in the system.
- **[SNS Event System](./02-architecture/06-sns/):** Event-driven communication patterns and message schemas.

---

### 🛠️ [03 - Development](./03-development/)

*This section provides tools and tracking for the **"build"** phase - implementation, testing, and development workflow.*

- **[Development Status](./03-development/01-project-management/README.md):** Single source of truth for current implementation status and progress tracking.
- **[CLI Commands Reference](./03-development/02-cli-commands-reference/cli-commands-reference.md):** Comprehensive reference for all command-line operations and procedures.
- **[Setup Guide](./03-development/03-setup-guide/setup-guide.md):** Complete guide for setting up development environment and cloud infrastructure.
- **[AI Prompts](./03-development/98-ai-prompts/README.md):** AI assistant contexts and development prompts for consistent assistance.
- **[Lessons Learned](./03-development/99-lessons/README.md):** Development lessons and best practices.

---

### ⚙️ [04 - Operations](./04-operations/)

*This section details how the system is maintained, monitored, and supported in production (the **"run"** and **"improve"** phases).*

- **[Monitoring Strategy](./04-operations/01-monitoring-strategy/monitoring-strategy.md):** Our approach to monitoring, dashboards, and alerting.
- **[Runbook Templates](./04-operations/02-runbook-template/runbook-template.md):** Templates for step-by-step guides for operational tasks.
- **[Post-Mortem Template](./04-operations/03-post-mortem-template/post-mortem-template.md):** Template for root cause analysis of incidents.
- **[AI Prompts](./04-operations/98-ai-prompts/README.md):** AI assistant context for operations tasks.
- **[Lessons Learned](./04-operations/99-lessons/README.md):** A log of lessons learned during development and operations.

---

## 🎯 **Getting Started**

**New to BuildingOS?** Start here:
1. **[📋 Project Charter](./01-project-vision/01-charter.md)** - Understand the vision
2. **[🏗️ Solution Architecture](./02-architecture/01-solution-architecture/solution-architecture.md)** - Learn the system design  
3. **[🛠️ Development Status](./03-development/01-project-management/README.md)** - See current progress
4. **[🛠️ Setup Guide](./03-development/03-setup-guide/setup-guide.md)** - Set up your environment

**For Development Work:**
- **Current Status:** [Development Status](./03-development/01-project-management/README.md)
- **API Reference:** [API Contract](./02-architecture/05-api-contract/api-contract.md)
- **Commands:** [CLI Reference](./03-development/02-cli-commands-reference/cli-commands-reference.md)
- **AI Context:** [Development Prompts](./03-development/98-ai-prompts/README.md) | [Architecture Prompts](./02-architecture/98-ai-prompts/README.md)

**For Architecture Work:**
- **System Design:** [Solution Architecture](./02-architecture/01-solution-architecture/solution-architecture.md)
- **Decisions:** [ADR Directory](./02-architecture/02-adr/)
- **API Contract:** [API Contract](./02-architecture/05-api-contract/api-contract.md)

---

## 📚 **Documentation Principles**

- **Single Source of Truth** - Each topic has one authoritative document
- **Living Documentation** - Updated continuously with implementation
- **Cross-Referenced** - Clear navigation between related documents  
- **AI-Friendly** - Context prompts for consistent AI assistance
- **Version Controlled** - All changes tracked in git

```
