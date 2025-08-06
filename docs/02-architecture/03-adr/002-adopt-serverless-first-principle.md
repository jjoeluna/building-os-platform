---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "Architecture"
  - "Serverless"
  - "AWS"
---

# ADR-002: Adopt Serverless-First Principle

## Context

To minimize operational overhead, reduce costs, and improve scalability, a decision was needed on the default compute and service paradigm for the BuildingOS platform.

## Decision

We will adopt a **Serverless-First** principle for all architectural and implementation choices. This means prioritizing the use of fully managed, serverless services from AWS, such as:
-   **Compute:** AWS Lambda
-   **Orchestration:** AWS Step Functions
-   **Database:** Amazon DynamoDB
-   **Messaging:** Amazon SNS & SQS
-   **API:** Amazon API Gateway

Traditional, provisioned resources (like EC2 or Fargate) will only be considered if a specific technical requirement cannot be met by a serverless alternative.

## Consequences

### Positive

-   **Reduced Operational Overhead:** No servers to manage, patch, or scale.
-   **Pay-per-Value Cost Model:** Costs are directly tied to usage, eliminating idle resource costs.
-   **Automatic Scaling:** Services scale automatically with the demand.
-   **Faster Development Cycles:** Focus on business logic instead of infrastructure management.

### Negative

-   **Potential for Vendor Lock-in:** Deeper integration with a specific cloud provider's ecosystem.
-   **Execution Time Limits:** Services like AWS Lambda have maximum execution time limits (e.g., 15 minutes) that must be considered in the design.
-   **Cold Starts:** Potential for increased latency on initial invocations of compute resources.
