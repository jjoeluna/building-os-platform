# Architecture Decision Records (ADRs) Index

This directory contains all Architecture Decision Records (ADRs) for the BuildingOS platform. Each ADR documents important architectural decisions, their context, rationale, and consequences to provide guidance for future development and maintain architectural consistency.

## 📚 Complete ADRs Index

### Documentation & Development Process
- **[001-migrate-documentation-to-docs-as-code.md](001-migrate-documentation-to-docs-as-code.md)**  
  *Migrate Documentation from Notion to Docs-as-Code*  
  📅 2025-08-03 | 🏷️ Documentation, Tooling

### Core Architecture Principles
- **[002-adopt-serverless-first-principle.md](002-adopt-serverless-first-principle.md)**  
  *Adopt Serverless-First Principle*  
  📅 2025-08-03 | 🏷️ Architecture, Serverless, AWS

- **[003-communication-via-event-driven-choreography.md](003-communication-via-event-driven-choreography.md)**  
  *Communication via Event-Driven Choreography*  
  📅 2025-08-03 | 🏷️ Architecture, Messaging, Decoupling

- **[004-adopt-intelligent-agent-model.md](004-adopt-intelligent-agent-model.md)**  
  *Adopt Intelligent Agent Model*  
  📅 2025-08-03 | 🏷️ Architecture, AI, Design Pattern

### Infrastructure & Platform Services
- **[005-use-step-functions-for-coordinator.md](005-use-step-functions-for-coordinator.md)**  
  *Use AWS Step Functions for the Coordinator Agent* ⚠️ **SUPERSEDED by ADR-013**  
  📅 2025-08-03 | 🏷️ Orchestration, Step Functions

- **[006-use-dynamodb-for-short-term-memory.md](006-use-dynamodb-for-short-term-memory.md)**  
  *Use DynamoDB for Short-Term Memory*  
  📅 2025-08-03 | 🏷️ Database, Memory, DynamoDB

- **[007-select-terraform-for-iac.md](007-select-terraform-for-iac.md)**  
  *Select Terraform for Infrastructure as Code*  
  📅 2025-08-03 | 🏷️ Infrastructure, Terraform, IaC

### Infrastructure Organization & Management
- **[008-structure-terraform-with-modules.md](008-structure-terraform-with-modules.md)**  
  *Structure Terraform Code with Reusable Modules*  
  📅 2025-08-03 | 🏷️ Terraform, Modules, Organization

- **[009-dynamic-resource-naming.md](009-dynamic-resource-naming.md)**  
  *Dynamic Resource Naming by Environment*  
  📅 2025-08-03 | 🏷️ Infrastructure, Naming, Environment

### Security & Permissions
- **[010-use-shared-iam-role-for-lambdas.md](010-use-shared-iam-role-for-lambdas.md)**  
  *Use a Shared IAM Role for Agent Lambdas (Initial Phase)*  
  📅 2025-08-03 | 🏷️ IAM, Permissions, Terraform

- **[012-refactor-iam-resources-into-reusable-module.md](012-refactor-iam-resources-into-reusable-module.md)**  
  *Refactor IAM Resources into a Reusable Module*  
  📅 2025-08-03 | 🏷️ IAM, Terraform, Modules

### Development & Debugging
- **[011-expose-all-agents-via-api-gateway-for-debugging.md](011-expose-all-agents-via-api-gateway-for-debugging.md)**  
  *Expose All Agents via API Gateway for Debugging*  
  📅 2025-08-03 | 🏷️ API Gateway, Debugging, Development

### Revolutionary Architecture Changes
- **[013-transition-to-distributed-agent-architecture.md](013-transition-to-distributed-agent-architecture.md)**  
  *Transition from Centralized Coordinator to Distributed Agent Architecture*  
  📅 2025-08-05 | 🏷️ Architecture, Event-Driven, Stateless, Scalability

- **[014-implement-websocket-real-time-messaging.md](014-implement-websocket-real-time-messaging.md)** 🆕  
  *Implement WebSocket Real-Time Messaging Architecture*  
  📅 2025-08-07 | 🏷️ WebSocket, Real-time, SNS, Messaging

## 📊 ADRs by Category

### 🏗️ **Core Architecture** (5 ADRs)
Fundamental architectural decisions that shape the entire platform:
- **Serverless-First Principle** (ADR-002)
- **Event-Driven Choreography** (ADR-003)  
- **Intelligent Agent Model** (ADR-004)
- **Distributed Agent Architecture** (ADR-013)
- **WebSocket Real-Time Messaging** (ADR-014) 🆕

### ☁️ **Infrastructure & Cloud** (4 ADRs)
Infrastructure, deployment, and cloud service decisions:
- **DynamoDB for Memory** (ADR-006)
- **Terraform for IaC** (ADR-007)
- **Terraform Modules** (ADR-008)
- **Dynamic Resource Naming** (ADR-009)

### 🔐 **Security & Permissions** (2 ADRs)
Security model and IAM configuration decisions:
- **Shared IAM Role** (ADR-010)
- **IAM Module Refactoring** (ADR-012)

### 🛠️ **Development & Operations** (2 ADRs)
Development process and operational decisions:
- **Docs-as-Code Migration** (ADR-001)
- **API Gateway for Debugging** (ADR-011)

### ⚠️ **Deprecated/Superseded** (1 ADR)
Decisions that have been replaced by newer approaches:
- **Step Functions Coordinator** (ADR-005) - Replaced by ADR-013

## 🎯 Architectural Evolution Timeline

### **Phase 1: Foundation** (August 3, 2025)
- **ADR-001 to ADR-012**: Established core principles, infrastructure, and development practices
- Focus on serverless, event-driven, and intelligent agent patterns

### **Phase 2: Revolutionary Transformation** (August 5, 2025)  
- **ADR-013**: Complete architectural transformation to distributed, stateless model
- Superseded centralized coordinator approach
- Achieved true event-driven choreography

## 📈 Key Architectural Themes

### **Event-Driven Design**
Multiple ADRs reinforce event-driven patterns:
- Event-driven choreography (ADR-003)
- Distributed agent architecture (ADR-013)

### **Serverless & Stateless**
Consistent push toward serverless, stateless computing:
- Serverless-first principle (ADR-002)
- DynamoDB for external state (ADR-006)
- Stateless agent architecture (ADR-013)

### **Infrastructure as Code**
Strong emphasis on reproducible infrastructure:
- Terraform selection (ADR-007)
- Modular organization (ADR-008, ADR-012)
- Dynamic naming (ADR-009)

### **AI & Intelligence**
Platform designed around intelligent agents:
- Intelligent agent model (ADR-004)
- Distributed specialized agents (ADR-013)

## 🔄 ADR Status Overview

| Status | Count | ADRs |
|--------|-------|------|
| **Proposed** | 1 | ADR-014 |
| **Accepted** | 12 | ADR-001 to ADR-004, ADR-006 to ADR-013 |
| **Superseded** | 1 | ADR-005 (replaced by ADR-013) |
| **Total** | 14 | All documented decisions |

## 💡 How to Use These ADRs

### **For New Team Members**
1. Start with core architecture ADRs (002, 003, 004, 013)
2. Review infrastructure decisions (006, 007, 008)
3. Understand security model (010, 012)

### **For Architecture Reviews**
1. Reference relevant architectural patterns
2. Ensure consistency with established principles
3. Consider impact on existing decisions

### **For New Features**
1. Check alignment with event-driven model (ADR-003, ADR-013)
2. Follow serverless-first principle (ADR-002)
3. Integrate with agent model (ADR-004, ADR-013)

### **For Infrastructure Changes**
1. Follow Terraform modularity (ADR-007, ADR-008)
2. Use dynamic naming conventions (ADR-009)
3. Consider security implications (ADR-010, ADR-012)

## 🔄 Contributing New ADRs

When adding new ADRs, follow the established format:

```markdown
---
status: "Proposed|Accepted|Rejected|Superseded"
date: "YYYY-MM-DD"
author: "Author Name"
tags:
  - "Primary Category"
  - "Secondary Category"
  - "Technology"
---

# ADR-XXX: Decision Title

## Context
## Decision  
## Consequences
## Related (if applicable)
## Supersedes (if applicable)
```

### ADR Numbering
- Use sequential numbering (next available: **ADR-015**)
- Update this index when adding new ADRs
- Reference related/superseded ADRs appropriately

## 🔗 Related Documentation

- **[Solution Architecture Document](../01-solution-architecture.md)**: Overall system architecture
- **[API Contract](../02-api-contract.md)**: API specifications
- **[Lessons Learned](../../03-operations/05-lessons/README.md)**: Implementation lessons and best practices

Remember: ADRs capture **why** decisions were made, not just **what** was decided. They provide crucial context for future architectural evolution!
