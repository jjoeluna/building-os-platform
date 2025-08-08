[📖 Docs](../README.md) > **🏗️ Architecture**

---

# 🏗️ Architecture

**The "How" of BuildingOS** - System design, technical decisions, and architectural patterns that define the platform structure.

---

## 📑 **Section Contents**

| Document | Description | Status |
|----------|-------------|--------|
| **[01 - Solution Architecture](./01-solution-architecture.md)** | Technical blueprint with C4 diagrams and patterns | ✅ Active |
| **[02 - API Contract](./02-api-contract.md)** | OpenAPI specification - single source of truth | ✅ Active |
| **[03 - Architecture Decision Records](./03-adr/README.md)** | Log of important architectural decisions | ✅ Active |
| **[04 - Component Registry](./04-components/README.md)** | Description of all major system components | ✅ Active |
| **[05 - Data Model](./05-data-model/README.md)** | Database schemas and data relationships | 📋 Planned |
| **[06 - Architecture Adequation Plan](./06-architecture-adequation-plan.md)** | Implementation roadmap and phase planning | ✅ Active |

---

## 🔗 **Related Sections**

- **[📋 Project Vision](../01-project-vision/README.md)** - Requirements that drive this architecture
- **[🛠️ Development](../03-development/README.md)** - Current implementation status and tools
- **[⚙️ Operations](../04-operations/README.md)** - How this architecture runs in production

---

## 🎯 **Architecture Principles**

1. **Serverless-first** - AWS Lambda, pay-per-use scaling
2. **Event-driven choreography** - SNS topics, loose coupling
3. **Intelligent agents** - Autonomous, specialized components
4. **Multi-tenant** - Building/organization isolation
5. **Documentation as Code** - All decisions recorded and versioned

---

## 📊 **Section Overview**

**Purpose:** Define the technical foundation and design decisions that guide implementation and ensure system quality.

**Key Stakeholders:** Architects, senior developers, DevOps engineers, and technical leads.

**Authority Documents:** API Contract and Solution Architecture serve as single sources of truth.

---

**Navigation:**
⬅️ **Previous:** [Project Vision](../01-project-vision/README.md)  
➡️ **Next:** [Development](../03-development/README.md)  
🏠 **Home:** [Documentation Index](../README.md)
