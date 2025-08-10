---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "Architecture"
  - "Database"
  - "AWS"
  - "DynamoDB"
---

# ADR-006: Use DynamoDB for Short-Term Memory

## Context

The Persona Agent needs to maintain the state and history of ongoing conversations to provide context for the Director Agent. A durable, scalable, and low-latency solution was required for this short-term memory store.

## Decision

We will use **Amazon DynamoDB** to implement the **Short-Term Memory** for conversations. The table will use a `SessionId` (e.g., a combination of user ID and conversation ID) as its primary key.

Crucially, we will enable the **Time To Live (TTL)** feature on the table, using an attribute like `ExpiresAt`. This will instruct DynamoDB to automatically delete conversation records after they have been inactive for a defined period, preventing the table from growing indefinitely and managing costs.

## Consequences

### Positive

-   **Low Latency:** DynamoDB provides single-digit millisecond latency, ensuring fast access to conversation history.
-   **Scalability:** As a fully managed NoSQL database, it scales seamlessly with the number of concurrent conversations.
-   **Automatic Data Pruning:** The TTL feature provides a cost-effective, hands-off mechanism for managing the lifecycle of conversation data.
-   **Serverless:** Aligns with our Serverless-First principle (ADR-002).

### Negative

-   **NoSQL Data Modeling:** Requires careful consideration of access patterns when designing the table schema.
-   **Cost at Scale:** While cost-effective for this use case, very high write/read throughput could become a significant cost factor.
