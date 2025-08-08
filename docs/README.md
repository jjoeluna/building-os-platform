# 📖 BuildingOS Project Documentation

Welcome to the central documentation for **BuildingOS**. This directory contains all the essential artifacts that define the project's vision, architecture, and operational practices.

---

## 🧭 **Quick Navigation**

| Section | Purpose | Key Documents |
|---------|---------|---------------|
| **[📋 Project Vision](./01-project-vision/README.md)** | Business goals & requirements | Charter, Requirements |
| **[🏗️ Architecture](./02-architecture/README.md)** | System design & decisions | Solution Architecture, API Contract, ADRs |
| **[🛠️ Development](./03-development/README.md)** | Implementation tools & status | Development Status, CLI Commands, Context Prompts |
| **[⚙️ Operations](./04-operations/README.md)** | Production maintenance | Monitoring, Runbooks, Post-Mortems |

---

## Documentation Index

### 📄 [01 - Project Vision](./01-project-vision/)

*This section defines the **"why"** of the project. It is the starting point for understanding the business goals and requirements.*

- **[Project Charter](./01-project-vision/01-charter.md):** The high-level vision, scope, stakeholders, and success metrics.
- **[Requirements](./01-project-vision/02-requirements.md):** The functional (User Stories) and non-functional (NFRs) requirements that guide development.

---

### 📐 [02 - Architecture](./02-architecture/)

*This section describes **"how"** the system is designed and built.*

- **[Solution Architecture](./02-architecture/01-solution-architecture.md):** The technical blueprint of the system, including C4 diagrams and architectural patterns.
- **[API Contract](./02-architecture/02-api-contract.md):** The formal definition of our API using the OpenAPI specification.
- **[Architecture Decision Records (ADRs)](./02-architecture/03-adr/):** A log of all important architectural decisions made throughout the project.
- **[Component Registry](./02-architecture/04-components/):** A list and description of all major software components in the system.
- **[Architecture Adequation Plan](./02-architecture/06-architecture-adequation-plan.md):** Implementation roadmap and phase planning.

---

### 🛠️ [03 - Development](./03-development/)

*This section provides tools and tracking for the **"build"** phase - implementation, testing, and development workflow.*

- **[Development Status](./03-development/01-development-status.md):** Single source of truth for current implementation status and progress tracking.
- **[CLI Commands Reference](./03-development/02-cli-commands-reference.md):** Comprehensive reference for all command-line operations and procedures.
- **[Developer Context Prompt](./03-development/03-developer-context-prompt.md):** AI assistant context for development tasks (implementation, debugging, testing).
- **[Architect Context Prompt](./03-development/04-architect-context-prompt.md):** AI assistant context for architecture tasks (design, decisions).
- **[Development Prompts](./03-development/05-development-prompts.md):** Collection of AI-assisted development, debugging, and deployment prompts.
- **[Development Environment Setup Guide](./03-development/06-setup-guide.md):** Complete guide for setting up development environment and cloud infrastructure.

---

### ⚙️ [04 - Operations](./04-operations/)

*This section details how the system is maintained, monitored, and supported in production (the **"run"** and **"improve"** phases).*

- **[Monitoring Strategy](./04-operations/01-monitoring-strategy.md):** Our approach to monitoring, dashboards, and alerting.
- **[Runbook Templates](./04-operations/02-runbook-template.md):** Templates for step-by-step guides for operational tasks.
- **[Post-Mortem Template](./04-operations/03-post-mortem-template.md):** Template for root cause analysis of incidents.
- **[Lessons Learned](./04-operations/04-lessons/):** A log of lessons learned during development and operations.

---

## 🎯 **Getting Started**

**New to BuildingOS?** Start here:
1. **[📋 Project Charter](./01-project-vision/01-charter.md)** - Understand the vision
2. **[🏗️ Solution Architecture](./02-architecture/01-solution-architecture.md)** - Learn the system design  
3. **[🛠️ Development Status](./03-development/01-development-status.md)** - See current progress
4. **[🛠️ Setup Guide](./03-development/06-setup-guide.md)** - Set up your environment

**For Development Work:**
- **Current Status:** [Development Status](./03-development/01-development-status.md)
- **API Reference:** [API Contract](./02-architecture/02-api-contract.md)
- **Commands:** [CLI Reference](./03-development/02-cli-commands-reference.md)
- **AI Context:** [Developer](./03-development/03-developer-context-prompt.md) | [Architect](./03-development/04-architect-context-prompt.md)

**For Architecture Work:**
- **System Design:** [Solution Architecture](./02-architecture/01-solution-architecture.md)
- **Decisions:** [ADR Directory](./02-architecture/03-adr/)
- **Implementation Plan:** [Adequation Plan](./02-architecture/06-architecture-adequation-plan.md)

---

## 📚 **Documentation Principles**

- **Single Source of Truth** - Each topic has one authoritative document
- **Living Documentation** - Updated continuously with implementation
- **Cross-Referenced** - Clear navigation between related documents  
- **AI-Friendly** - Context prompts for consistent AI assistance
- **Version Controlled** - All changes tracked in git

```
