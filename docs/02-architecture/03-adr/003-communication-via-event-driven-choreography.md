---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "Architecture"
  - "Messaging"
  - "Decoupling"
---

# ADR-003: Communication via Event-Driven Choreography

## Context

A decision was needed on how the different components and agents within the BuildingOS platform (e.g., Persona Agent, Director Agent, Tools) would communicate with each other. Direct, synchronous API calls (orchestration) were considered against an asynchronous, event-based model (choreography).

## Decision

We will use an **Event-Driven Choreography** model for all inter-service communication. A central, asynchronous event bus built with **Amazon SNS (Simple Notification Service)** and **SQS (Simple Queue Service)** will be the sole mechanism for communication.

Components will publish events (e.g., `IntentionCreated`) to the bus without knowledge of the consumers. Other components will subscribe to the events they are interested in and react accordingly. Direct, point-to-point communication between agents is explicitly forbidden.

## Consequences

### Positive

-   **Radical Decoupling:** Components are completely independent of each other, allowing them to be developed, deployed, and scaled separately.
-   **Increased Resilience:** The failure of a single consumer does not impact the producer or other consumers. The event bus provides durability.
-   **Improved Scalability:** The pub/sub model scales naturally without creating bottlenecks from direct calls.
-   **Extensibility:** New components can be added to the system by simply subscribing to existing events, without modifying the original producers.

### Negative

-   **Increased Complexity in Monitoring:** Tracing a single business process across multiple, decoupled events can be more complex than following a direct call chain.
-   **Potential for Eventual Consistency:** As the system is asynchronous, there is no immediate, synchronous response, which must be handled by the user-facing components.
