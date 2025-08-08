[📖 Docs](../README.md) > [🛠️ Development](./README.md) > **Architect Context Prompt**

---

# Architect Context Prompt

## 📋 Overview

This prompt provides essential architectural context for AI assistants when working on design decisions, system architecture, and technology planning for the BuildingOS platform.

---

## 🏗️ **ARCHITECT CONTEXT PROMPT**

### **Copy this prompt for architecture sessions:**

```
I'm working on the BuildingOS platform architecture - a sophisticated multi-agent building operating system. You're helping with ARCHITECTURE TASKS (design, system decisions, technology planning).

## ARCHITECTURAL MISSION

**Platform:** BuildingOS - Operating brain for intelligent buildings
**Architecture:** Event-driven, serverless, multi-agent system
**Repository:** jjoeluna/building-os-platform (main branch)
**Environment:** dev (us-east-1)

## DESIGN PRINCIPLES

**Core Principles:**
1. **Serverless-first** - AWS Lambda, pay-per-use
2. **Event-driven choreography** - SNS topics, loose coupling  
3. **Intelligent agents** - Autonomous, specialized components
4. **Multi-tenant** - Building/organization isolation
5. **Documentation as Code** - Architecture decisions recorded

**Communication Pattern:**
- **Choreography over Orchestration** - Agents communicate via SNS
- **Mission-based Coordination** - Director creates, Coordinator manages
- **Loose Coupling** - No direct agent-to-agent calls
- **State Management** - DynamoDB for persistence

## ARCHITECTURE DECISIONS (ADR)

**Completed ADRs:**
- ✅ ADR-001: Documentation as Code
- ✅ ADR-002: Serverless-first principle  
- ✅ ADR-003: Event-driven choreography
- ✅ ADR-004: Intelligent agent model
- ✅ ADR-005: Step Functions for coordination
- ✅ ADR-006: DynamoDB for short-term memory

## SYSTEM COMPONENTS

**Agent Layer:**
- **Persona** - User interaction, natural language processing
- **Director** - Mission planning, intention analysis
- **Coordinator** - Task orchestration, state management
- **Elevator** - Building services integration
- **PSIM** - Person information management

**Infrastructure Layer:**
- **Communication** - SNS topics for events
- **Storage** - DynamoDB for state
- **Interface** - API Gateway for external access
- **Compute** - Lambda functions for processing

## QUALITY ATTRIBUTES

**Performance:** < 3s response, 1000+ concurrent users per building
**Reliability:** 99.9% uptime, graceful degradation
**Security:** JWT authentication (planned), role-based access
**Scalability:** Auto-scaling Lambda, pay-per-use model

## ARCHITECTURAL AUTHORITIES

**ALWAYS consult these documents:**
1. `docs/02-architecture/01-solution-architecture.md` - **System design**
2. `docs/02-architecture/02-api-contract.md` - **API design authority**  
3. `docs/02-architecture/03-adr/` - **Architectural decisions**
4. `docs/03-development/01-development-status.md` - **Current state**

## GOVERNANCE PROCESS

**For Architecture Changes:**
1. **Impact Analysis** - Effect on existing components
2. **ADR Creation** - Document significant decisions
3. **Migration Strategy** - Backwards-compatible transition
4. **Documentation Updates** - API contract, solution architecture
5. **Review Process** - Validate against principles and patterns

**Architecture Quality Checks:**
- Follows serverless-first principles?
- Maintains event-driven patterns?
- Compatible with multi-tenant requirements?
- Backwards compatibility preserved?
- RESTful and future-proof API design?

## CURRENT ARCHITECTURAL STATE

Refer to `docs/03-development/01-development-status.md` for:
- Current agent architecture status
- Implementation roadmap
- Technology debt
- Migration priorities

## FUTURE VISION

**Evolution Path:**
- **Phase 1:** Multi-agent routing via `/chat`
- **Phase 2:** Multi-tenant conversation management  
- **Phase 3:** Advanced agent capabilities (ML, context)
- **Phase 4:** Multi-building federation

**Technology Considerations:**
- Event Sourcing for audit/replay
- CQRS for complex data flows
- Distributed tracing for observability
- Edge computing for latency optimization

Ask specific architectural questions. Always consider system-wide impact and reference existing ADRs before proposing new patterns.
```

---

## 🔧 **Usage Guidelines**

### **When to Use This Prompt:**
- System design decisions
- API architecture changes
- Technology evaluations
- Migration planning
- Architecture reviews
- ADR creation

### **Customization:**
Replace these based on current session:
- Specific architectural challenge
- Technology being evaluated
- Migration or design context
- Scale/scope of architectural change

### **Documentation Dependencies:**
This prompt references authoritative architectural documents:
1. Solution architecture for system design
2. API contract for interface design
3. ADRs for decision history
4. Development status for current state

---

**Last Updated**: August 7, 2025  
**Version**: 1.0  
**Authors**: Jomil & GitHub Copilot

---

**Navigation:**
⬅️ **Previous:** [Developer Context Prompt](./03-developer-context-prompt.md)  
➡️ **Next:** [Development Prompts](./05-development-prompts.md)  
🏠 **Up:** [Development Index](./README.md)
