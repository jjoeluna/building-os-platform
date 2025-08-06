---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "Architecture"
  - "AI"
  - "Design Pattern"
---

# ADR-004: Adopt Intelligent Agent Model

## Context

The core business logic of the BuildingOS platform requires complex reasoning, planning, and execution based on user requests in natural language. A monolithic application structure would be ill-suited for this complexity. A clear pattern was needed to separate the different concerns of the AI-driven workflow.

## Decision

We will structure the core logic of the platform based on an **Intelligent Agent Model**. This model separates the workflow into three distinct agent roles:

1.  **Persona Agent (Guardian Role):** The user-facing agent responsible for security, context management (short-term memory), and translating natural language requests into a structured `Intention`.
2.  **Director Agent:** The strategic agent responsible for taking a structured `Intention`, consulting long-term knowledge, and using a Large Language Model (LLM) to create a detailed, step-by-step `Mission` plan.
3.  **Coordinator Agent:** The tactical agent responsible for executing the `Mission` plan by orchestrating calls to various tools and managing the workflow state.

## Consequences

### Positive

-   **Separation of Concerns:** Each agent has a clear, well-defined responsibility, making the system easier to understand, develop, and maintain.
-   **Modularity:** Each agent can be implemented using the best-fit technology (e.g., Lambda for the Director, Step Functions for the Coordinator).
-   **Scalability:** Each agent can be scaled independently based on its specific workload.
-   **Clarity of Thought:** The model provides a clear mental framework for reasoning about the system's behavior.

### Negative

-   **Increased Number of Components:** The system is composed of more moving parts compared to a monolithic design.
-   **Communication Overhead:** Requires a robust event bus for communication between agents, as defined in ADR-003.
