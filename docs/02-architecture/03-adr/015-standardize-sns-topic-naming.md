# ADR-015: Standardize SNS Topic Naming Convention

## Status
🚧 **In Progress** - 2025-08-07

## Context

The current SNS topic naming in our BuildingOS platform lacks consistency and clarity regarding publisher/subscriber relationships. This creates challenges in:

### Current Issues
- **Unclear Ownership**: Topic names don't indicate which agent publishes to them
- **Inconsistent Patterns**: Mixed naming conventions across topics
- **Debugging Difficulty**: Hard to trace message flow from topic names alone
- **Scalability Concerns**: Difficult to add new agent-specific topics

### Current Topic Structure
```
bos-intention-topic-dev         → Generic, unclear publisher
bos-mission-topic-dev           → Generic, unclear publisher  
bos-task-result-topic-dev       → Generic, unclear publisher
bos-mission-result-topic-dev    → Generic, unclear publisher
bos-intention-result-topic-dev  → Generic, unclear publisher
```

## Decision

We will implement a **standardized SNS topic naming convention** that clearly indicates publisher and purpose:

### New Naming Pattern
```
bos-{publisher-agent}-{action}-topic-{environment}
```

### New Topic Architecture

| **Topic Name** | **Publisher** | **Subscriber** | **Purpose** |
|----------------|---------------|----------------|-------------|
| `bos-chat-intention-topic` | Chat Lambda | Agent Persona | User intentions from WebSocket |
| `bos-persona-intention-topic` | Agent Persona | Agent Director | Processed and validated intentions |
| `bos-director-mission-topic` | Agent Director | Agent Coordinator | Structured missions with tasks |
| `bos-coordinator-task-topic` | Agent Coordinator | Agents (Elevator, etc.) | Specific tasks for execution |
| `bos-agent-task-result-topic` | Agents | Agent Coordinator | Task execution results |
| `bos-coordinator-mission-result-topic` | Agent Coordinator | Agent Director | Consolidated mission results |
| `bos-director-response-topic` | Agent Director | Agent Persona | Final structured responses |
| `bos-persona-response-topic` | Agent Persona | Chat Lambda | User-formatted responses |

### Benefits of New Convention

1. **✅ Clear Ownership**: Topic name immediately indicates the publisher
2. **✅ Consistent Structure**: Uniform `{agent}-{action}` pattern
3. **✅ Improved Debugging**: Easy to trace message flow and identify bottlenecks
4. **✅ Scalability**: Simple to add new agent-specific topics
5. **✅ Self-Documenting**: Architecture becomes clear from topic names alone

## Implementation Plan

### Phase 1: Infrastructure Setup ✅
- [x] Update Terraform modules with new topic definitions
- [x] Add new topics alongside legacy topics for migration
- [x] Update documentation and architecture diagrams
- [x] Create migration plan and rollback strategy

### Phase 2: Agent Migration (Week 1)
- [ ] Create Chat Lambda for WebSocket management
- [ ] Update Agent Persona to use new topic pattern
- [ ] Update Agent Director to use new topic pattern
- [ ] Update Agent Coordinator to use new topic pattern
- [ ] Update integration agents (Elevator, etc.) to use new pattern

### Phase 3: Testing & Validation (Week 1)
- [ ] End-to-end testing with new topic structure
- [ ] Performance validation and monitoring
- [ ] Parallel testing with legacy and new systems
- [ ] Message flow validation and error handling

### Phase 4: Legacy Cleanup (Week 2)
- [ ] Remove legacy topic references from code
- [ ] Remove legacy topics from Terraform
- [ ] Update monitoring and alerting
- [ ] Final documentation update

## Migration Strategy

### Coexistence Period
- Both legacy and new topics will exist simultaneously
- Agents will be migrated one by one to new topics
- Legacy topics marked with `Status = "Legacy"` tag
- Monitoring both old and new message flows

### Rollback Plan
- Legacy topics remain functional during migration
- Quick rollback by reverting agent environment variables
- No data loss during migration process
- Terraform state preserved for both topic sets

### Agent Migration Order
1. **Chat Lambda** (new component) → `chat-intention-topic`
2. **Agent Persona** → `persona-intention-topic` + `persona-response-topic`
3. **Agent Director** → `director-mission-topic` + `director-response-topic`
4. **Agent Coordinator** → `coordinator-task-topic` + `coordinator-mission-result-topic`
5. **Integration Agents** → `agent-task-result-topic`

## Consequences

### Positive
- ✅ **Clear Architecture**: Self-documenting topic structure
- ✅ **Better Debugging**: Easy message flow tracing
- ✅ **Improved Maintainability**: Clear ownership and responsibilities
- ✅ **Scalability**: Easy addition of new agent-specific flows
- ✅ **Team Productivity**: Faster onboarding and troubleshooting

### Negative
- ⚠️ **Migration Complexity**: Requires coordinated agent updates
- ⚠️ **Temporary Overhead**: Dual topic maintenance during migration
- ⚠️ **Testing Requirements**: Need to validate new message flows

### Neutral
- 🔄 **Infrastructure Costs**: Additional topics during migration period
- 🔄 **Documentation Updates**: Need to update all architectural docs
- 🔄 **Monitoring Updates**: Update CloudWatch dashboards and alerts

## Validation Criteria

### Success Metrics
- [ ] All agents successfully using new topic structure
- [ ] Message flow latency maintained or improved
- [ ] Zero message loss during migration
- [ ] Documentation reflects new architecture
- [ ] Team can easily identify publisher/subscriber relationships

### Acceptance Criteria
- [ ] New topics handle 100% of production traffic
- [ ] Legacy topics show zero message volume
- [ ] All integration tests pass with new structure
- [ ] Monitoring and alerting updated for new topics
- [ ] Team training completed on new naming convention

## References

- [ADR-014: Implement WebSocket Real-Time Messaging](./014-implement-websocket-real-time-messaging.md)
- [AWS SNS Best Practices](https://docs.aws.amazon.com/sns/latest/dg/sns-best-practices.html)
- [Solution Architecture Document](../01-solution-architecture.md)

---

**Author**: BuildingOS Development Team  
**Date**: 2025-08-07  
**Reviewers**: Architecture Team, DevOps Team
