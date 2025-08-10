---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "API"
  - "Testing"
  - "Debugging"
---

# ADR-011: Expose All Agents via API Gateway for Debugging

## Context

The `director_agent` is designed to be triggered asynchronously by SNS events. While this is ideal for production, it makes iterative development and testing difficult, as it requires publishing an SNS message to trigger each execution. A more direct invocation method was needed for the development phase.

## Decision

We will expose **all** agent Lambda functions (`health_check`, `persona_agent`, `director_agent`) via unique routes on a single **Amazon API Gateway**. Each agent will have a corresponding `GET` endpoint (e.g., `/health`, `/persona`, `/director`).

This provides a simple, synchronous, and direct HTTP-based trigger for every agent, which can be easily used with tools like `curl` or Postman for rapid testing and debugging.

## Consequences

### Positive

-   **Simplified Debugging:** Allows developers to test each agent in isolation without needing to trigger a full event-driven flow.
-   **Rapid Iteration:** Code changes can be deployed and immediately tested with a simple browser refresh or `curl` command.
-   **Clear Entry Points:** Provides clear, well-defined entry points for each agent's functionality.

### Negative

-   **Production Risk:** The debug endpoints, particularly for event-driven agents like the `director_agent`, should not be used by the production application logic.
-   **Potential for Confusion:** It must be clearly documented that the primary invocation method for the `director_agent` in the actual workflow is SNS, not the API Gateway.
-   **Future Cleanup:** These debug endpoints may need to be secured or removed as the project moves to production to reduce the exposed surface area.
