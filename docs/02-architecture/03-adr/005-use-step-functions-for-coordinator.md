---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "Architecture"
  - "Orchestration"
  - "AWS"
  - "Step Functions"
---

# ADR-005: Use AWS Step Functions for the Coordinator Agent

## Context

The Coordinator Agent is responsible for executing a `Mission` plan, which is a sequence of steps that may involve conditional logic, retries, and parallel execution. A decision was needed on the best technology to implement this tactical orchestration. Using a single, long-running Lambda function was considered against using a dedicated orchestration service.

## Decision

We will implement the **Coordinator Agent** as an **AWS Step Function State Machine**. The definition of the state machine will be generated dynamically or selected based on the `Mission` plan received from the Director Agent.

This approach allows us to define the workflow declaratively using the Amazon States Language (ASL), leveraging native features for state management, error handling, and long-running executions.

## Consequences

### Positive

-   **Resilience and Error Handling:** Step Functions provide built-in, configurable retry and catch mechanisms, making the execution robust.
-   **State Management:** The service automatically manages the state of the workflow, eliminating the need for a custom solution.
-   **Observability:** Provides a visual audit trail of every execution, which is invaluable for debugging complex workflows.
-   **Long-Running Processes:** Can run for up to a year, far exceeding the 15-minute limit of a Lambda function.
-   **Decoupling:** The orchestration logic (the state machine) is decoupled from the task logic (the tool Lambdas).

### Negative

-   **State Definition Complexity:** The Amazon States Language (ASL) in JSON can be verbose and complex to write and manage for very large workflows.
-   **Cost:** Step Functions have a pricing model based on state transitions, which may be more expensive than a single Lambda for very simple, short-lived workflows.
