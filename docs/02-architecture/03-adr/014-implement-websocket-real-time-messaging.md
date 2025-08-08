# ADR-014: Implement WebSocket Real-Time Messaging Architecture

## Status
✅ **Accepted** - 2025-08-07

## Context

The current frontend implementation uses HTTP polling to check for conversation updates, which presents several architectural limitations:

### Current Architecture Limitations
- **Polling Overhead**: Frontend polls every 2 seconds for 30 seconds, creating unnecessary load
- **Latency**: Response delay of 2-15 seconds depending on polling cycle
- **Resource Waste**: Continuous HTTP requests even when no new messages exist
- **Scalability Issues**: Polling doesn't scale well with concurrent users
- **Poor UX**: Not truly real-time, creating delays in conversation flow

### Industry Reference Analysis
Modern messaging platforms like WhatsApp use event-driven, real-time architectures:
- **WhatsApp Stack**: Erlang/OTP + XMPP + WebSocket + Kafka + Cassandra
- **Core Principles**: Event-driven, pub/sub messaging, real-time bidirectional communication
- **Delivery Guarantees**: At-least-once delivery with message acknowledgments

### Business Requirements
- **Real-time Communication**: Immediate message delivery (< 500ms)
- **Scalability**: Support for concurrent users without performance degradation
- **Reliability**: Message delivery guarantees and connection resilience
- **Cost Efficiency**: Optimize infrastructure costs by eliminating polling overhead

## Decision

We will implement a **WebSocket-based real-time messaging architecture** using AWS native services, directly integrated with our existing SNS event bus.

### Target Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │    Lambda       │
│     Chat        │◄──►│   WebSocket     │◄──►│  Connection     │
│                 │    │                 │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DynamoDB      │    │      SNS        │    │    Lambda       │
│  Connections    │◄───│   Event Bus     │◄──►│   Message       │
│    Store        │    │ (Standardized)  │    │   Handler       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  BuildingOS     │
                       │    Agents       │
                       │   (Existing)    │
                       └─────────────────┘
```

### Key Components

1. **WebSocket API Gateway**
   - Persistent bidirectional connections
   - Automatic connection lifecycle management
   - Native AWS scaling and availability

2. **Connection Management Lambda**
   - `onConnect`: Register user connection in DynamoDB
   - `onDisconnect`: Clean up connection state
   - `sendMessage`: Publish message to `bos-chat-intention-topic`

3. **SNS Integration (Standardized Topics)**
   - Use new standardized SNS topic naming convention
   - Add WebSocket delivery subscriber to `bos-persona-response-topic`
   - Maintain current agent choreography with clear naming

4. **Response Handler Lambda**
   - Subscribe to `bos-persona-response-topic`
   - Push real-time responses via WebSocket
   - Handle delivery acknowledgments

5. **Connection Store (DynamoDB)**
   - Track active WebSocket connections
   - Map user_id → connection_id
   - TTL for automatic cleanup

## Consequences

### Positive
- ✅ **Real-time Performance**: Sub-500ms message delivery
- ✅ **Scalability**: Supports thousands of concurrent connections
- ✅ **Cost Optimization**: Eliminates polling overhead (~90% reduction in API calls)
- ✅ **Better UX**: Instant message delivery, typing indicators, presence
- ✅ **Architectural Consistency**: Leverages existing SNS event bus
- ✅ **Zero Backend Changes**: Existing agents continue working unchanged
- ✅ **Enterprise-grade**: WebSocket + SNS = WhatsApp-like reliability

### Negative
- ⚠️ **Implementation Complexity**: WebSocket connection management
- ⚠️ **State Management**: DynamoDB connection tracking required
- ⚠️ **Error Handling**: Connection drops, reconnection logic
- ⚠️ **Testing Complexity**: WebSocket testing more complex than HTTP

### Neutral
- 🔄 **Infrastructure**: Additional Lambda functions and DynamoDB table
- 🔄 **Monitoring**: New CloudWatch metrics for WebSocket connections
- 🔄 **Frontend Changes**: Replace polling with WebSocket client

## Implementation Plan

### Phase 1: Infrastructure (Week 1)
1. Create WebSocket API Gateway with Terraform
2. Implement connection management Lambda functions
3. Create DynamoDB connections table
4. Set up SNS → WebSocket integration

### Phase 2: Frontend Integration (Week 1)
1. Replace HTTP polling with WebSocket client
2. Implement connection state management
3. Add reconnection logic and error handling
4. Update UI for real-time indicators

### Phase 3: Testing & Optimization (Week 1)
1. Load testing with multiple concurrent connections
2. Performance monitoring and optimization
3. Error scenario testing and recovery
4. Documentation and deployment guides

## Alternatives Considered

### Alternative 1: Server-Sent Events (SSE)
- ❌ **Limitation**: Unidirectional only (server → client)
- ❌ **Complexity**: Still requires HTTP POST for client → server
- ❌ **Browser Support**: Less robust than WebSocket

### Alternative 2: Long Polling
- ❌ **Scalability**: Connection timeouts and resource holding
- ❌ **Complexity**: Timeout handling and reconnection logic
- ❌ **Performance**: Still not truly real-time

### Alternative 3: External Service (Pusher, Socket.io)
- ❌ **Cost**: Additional service costs and vendor lock-in
- ❌ **Integration**: Complex integration with existing SNS architecture
- ❌ **Control**: Less control over infrastructure and data flow

## References

- [ADR-015: Standardize SNS Topic Naming Convention](./015-standardize-sns-topic-naming.md)
- [AWS API Gateway WebSocket Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/websocket-api.html)
- [AWS WebSocket Best Practices](https://aws.amazon.com/blogs/compute/announcing-websocket-apis-in-amazon-api-gateway/)
- [Real-time Messaging Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/messaging.html)
- [WhatsApp Architecture Analysis](https://highscalability.com/whatsapp-architecture/)

---

**Author**: BuildingOS Development Team  
**Date**: 2025-08-07  
**Review**: Pending stakeholder approval
