# Diagrama Visual: Chat ↔ SNS Communication Flow

```
                            🌐 BUILDINGOS - NOVA ARQUITETURA SNS
                                   Communication Flow Diagram

    ┌─────────────────────┐    HTTP POST     ┌─────────────────────┐    Lambda      ┌─────────────────────┐
    │                     │ ──────────────► │                     │ ────────────► │                     │
    │   💻 Chat Frontend  │  /persona        │  🌐 API Gateway     │   Invoke       │  🤖 Persona Agent   │
    │                     │                  │                     │                │     (Lambda)        │
    │  • User Input       │ ◄────────────── │  • CORS Headers     │ ◄──────────── │                     │
    │  • Real-time UI     │    202 Accepted  │  • Rate Limiting    │   Response     │  • Save to DynamoDB │
    │  • Polling (2s)     │                  │  • Authentication   │                │  • Publish to SNS   │
    └─────────────────────┘                  └─────────────────────┘                └─────────────────────┘
              │                                                                                    │
              │                                                                                    │ SNS Publish
              │ GET /persona                                                                       ▼
              │ ?user_id=123&session=456                                            ┌─────────────────────┐
              │                                                                     │                     │
              │                                                                     │  📡 SNS Topic       │
              │                                                                     │  bos-persona-       │
              │                                                                     │  intention-topic    │
              │                                                                     │                     │
              │                                                                     └─────────────────────┘
              │                                                                                    │
              │                                                                                    │ SNS Event
              │                                                                                    ▼
              │                                                                     ┌─────────────────────┐
              │                                                                     │                     │
              │                                                                     │  🎯 Director Agent  │
              │                                                                     │     (Lambda)        │
              │                                                                     │                     │
              │                                                                     │  • Claude AI        │
              │                                                                     │  • Mission Planning │
              │                                                                     │  • Agent Routing    │
              │                                                                     └─────────────────────┘
              │                                                                                    │
              │                                                                                    │ SNS Publish
              │                                                                                    ▼
              │                                                                     ┌─────────────────────┐
              │                                                                     │                     │
              │                                                                     │  📡 SNS Topic       │
              │                                                                     │  bos-director-      │
              │                                                                     │  mission-topic      │
              │                                                                     │                     │
              │                                                                     └─────────────────────┘
              │                                                                              │     │     │
              │                                                                              │     │     │ SNS Events
              │                                                                              ▼     ▼     ▼
              │                                                                     ┌─────────────────────┐
              │                                                                     │                     │
              │                                                                     │  🛗 Elevator Agent  │
              │                                                                     │     🚪 Door Agent   │
              │                                                                     │     🌡️ HVAC Agent   │
              │                                                                     │     💡 Light Agent  │
              │                                                                     │                     │
              │                                                                     │  • Execute Tasks    │
              │                                                                     │  • Call Building    │
              │                                                                     │    APIs             │
              │                                                                     └─────────────────────┘
              │                                                                                    │
              │                                                                                    │ SNS Publish
              │                                                                                    ▼
              │                                                                     ┌─────────────────────┐
              │                                                                     │                     │
              │                                                                     │  📡 SNS Topic       │
              │                                                                     │  bos-coordinator-   │
              │                                                                     │  mission-result     │
              │                                                                     │                     │
              │                                                                     └─────────────────────┘
              │                                                                                    │
              │                                                                                    │ SNS Event
              │                                                                                    ▼
              │                                                                     ┌─────────────────────┐
              │                                                                     │                     │
              │ ◄─ Polling ─── DynamoDB ◄─── Save Response ◄──────────────────── │  🤖 Persona Agent   │
              │    Every 2s       │                                                │     (Lambda)        │
              │                   │                                                │                     │
              │                   ▼                                                │  • Process Results  │
              │          ┌─────────────────────┐                                  │  • Update DynamoDB  │
              │          │                     │                                  │  • Format Messages  │
              │          │  💾 DynamoDB        │                                  └─────────────────────┘
              │          │                     │                                               ▲
              │          │  • Conversations    │                                               │
              │          │  • Sessions         │                                               │
              │          │  • Message History  │                    ┌─────────────────────┐   │
              │          │  • TTL (24h)        │                    │                     │   │
              │          │                     │                    │  📡 SNS Topic       │ ──┘
              │          └─────────────────────┘                    │  bos-director-      │
              │                                                     │  response-topic     │
              │                                                     │                     │
              │                                                     └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │                     │
    │  📱 User Interface  │
    │                     │
    │  • Real-time msgs   │
    │  • Notifications    │
    │  • Status updates   │
    │  • Error handling   │
    └─────────────────────┘


                               🕐 TIMING FLOW (Typical Request)

    T+0.0s ──► User types: "Chame o elevador para o andar 5"
    T+0.1s ──► Frontend sends HTTP POST to API Gateway
    T+0.2s ──► Persona Agent receives request, returns 202 Accepted
    T+0.3s ──► Persona Agent publishes to bos-persona-intention-topic
    T+0.4s ──► Director Agent receives intention via SNS
    T+0.5s ──► Director Agent calls Claude AI for analysis
    T+1.0s ──► Director Agent creates mission and publishes to bos-director-mission-topic
    T+1.1s ──► Elevator Agent receives mission via SNS
    T+1.5s ──► Elevator Agent calls Building API to control elevator
    T+2.0s ──► Elevator Agent publishes result to bos-coordinator-mission-result-topic
    T+2.1s ──► Persona Agent receives result and saves to DynamoDB
    T+4.0s ──► Frontend polls and receives new message: "✅ Elevador chamado para andar 5"
    T+4.1s ──► UI updates with success message and browser notification


                               📊 SNS TOPICS ARCHITECTURE

    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                          🏗️ BUILDINGOS SNS TOPICS                                   │
    │                                                                                     │
    │  📡 bos-persona-intention-topic-dev                                                │
    │  ├── Publisher: Persona Agent                                                      │
    │  ├── Subscriber: Director Agent                                                    │
    │  └── Purpose: User intentions and requests                                         │
    │                                                                                     │
    │  📡 bos-director-mission-topic-dev                                                 │
    │  ├── Publisher: Director Agent                                                     │
    │  ├── Subscribers: Elevator, Door, HVAC, Light Agents                             │
    │  └── Purpose: Mission distribution to specialist agents                            │
    │                                                                                     │
    │  📡 bos-director-response-topic-dev                                                │
    │  ├── Publisher: Director Agent                                                     │
    │  ├── Subscriber: Persona Agent                                                     │
    │  └── Purpose: Elaborated responses from Director                                   │
    │                                                                                     │
    │  📡 bos-coordinator-mission-result-topic-dev                                       │
    │  ├── Publishers: All specialist agents                                            │
    │  ├── Subscriber: Persona Agent                                                     │
    │  └── Purpose: Mission execution results                                            │
    │                                                                                     │
    └─────────────────────────────────────────────────────────────────────────────────────┘


                               💾 DATA FLOW AND PERSISTENCE

    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                              💾 DATA STORAGE                                        │
    │                                                                                     │
    │  🗃️ DynamoDB - Conversations Table                                                │
    │  ├── ConversationId (Primary Key)                                                  │
    │  ├── UserId + SessionId (GSI)                                                     │
    │  ├── Role (user|assistant)                                                         │
    │  ├── Message Content                                                               │
    │  ├── Timestamp                                                                     │
    │  └── TTL (24 hours)                                                               │
    │                                                                                     │
    │  🗃️ DynamoDB - Mission State Table                                                │
    │  ├── MissionId (Primary Key)                                                       │
    │  ├── UserId + SessionId                                                           │
    │  ├── Status (pending|in_progress|completed|failed)                                │
    │  ├── Tasks Array                                                                   │
    │  └── Timestamps                                                                    │
    │                                                                                     │
    └─────────────────────────────────────────────────────────────────────────────────────┘


                               🔄 FRONTEND POLLING STRATEGY

    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                           📱 INTELLIGENT POLLING                                    │
    │                                                                                     │
    │  Active Mode (User typing/interacting)                                            │
    │  ├── Interval: 2 seconds                                                           │
    │  ├── Timeout: 5 seconds                                                           │
    │  └── Retry: 3 attempts with exponential backoff                                   │
    │                                                                                     │
    │  Background Mode (Tab not focused)                                                 │
    │  ├── Interval: 5 seconds                                                           │
    │  ├── Reduced frequency to save battery                                            │
    │  └── Resume active mode when tab focused                                          │
    │                                                                                     │
    │  Offline Mode (Connection lost)                                                    │
    │  ├── Interval: 30 seconds                                                          │
    │  ├── Connection retry logic                                                        │
    │  └── Queue messages for when connection restored                                   │
    │                                                                                     │
    └─────────────────────────────────────────────────────────────────────────────────────┘


                               🛡️ ERROR HANDLING AND RESILIENCE

    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                           🛡️ RESILIENCE PATTERNS                                   │
    │                                                                                     │
    │  Circuit Breaker                                                                   │
    │  ├── API Gateway level rate limiting                                              │
    │  ├── Lambda concurrency controls                                                   │
    │  └── SNS delivery policies                                                         │
    │                                                                                     │
    │  Retry Logic                                                                       │
    │  ├── Frontend: Exponential backoff (2s, 4s, 8s)                                 │
    │  ├── SNS: Built-in retry with DLQ                                                │
    │  └── Lambda: Automatic retry on failures                                          │
    │                                                                                     │
    │  Graceful Degradation                                                             │
    │  ├── Show cached messages when API unavailable                                    │
    │  ├── Queue unsent messages locally                                                │
    │  └── Visual indicators for connection status                                      │
    │                                                                                     │
    └─────────────────────────────────────────────────────────────────────────────────────┘
```
