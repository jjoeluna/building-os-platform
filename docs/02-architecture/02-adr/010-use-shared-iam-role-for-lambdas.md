---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "IAM"
  - "Permissions"
  - "Terraform"
---

# ADR-010: Use a Shared IAM Role for Agent Lambdas (Initial Phase)

## Context

As we add more Lambda functions for the different agents (`persona_agent`, `director_agent`), a decision is needed on the strategy for IAM roles. The options are creating a dedicated, fine-grained IAM role for each function, or using a shared role for a group of related functions.

## Decision

For the initial phase of development, we will use a **single, shared IAM role** (`lambda_exec_role`) for all agent-related Lambda functions. All necessary permissions (e.g., CloudWatch Logs, DynamoDB access, SNS publish, Bedrock invoke) will be attached to this single role.

This decision prioritizes development speed and simplicity at the start of the project.

## Consequences

### Positive

-   **Simplicity:** Reduces the amount of Terraform code and IAM resources to manage initially.
-   **Faster Development:** Avoids the need to create and configure a new role for every new Lambda function.
-   **Centralized Permissions:** All agent permissions are visible in one place.

### Negative

-   **Violation of Least Privilege:** This approach is a deliberate, temporary violation of the principle of least privilege. For example, the `persona_agent` will have permissions to invoke Bedrock models, even though it doesn't need to.
-   **Increased Blast Radius:** If the role is ever compromised, an attacker would have access to all the services it has permissions for, across all agents.
-   **Future Refactoring Required:** As the project matures and moves towards production, this shared role **must** be refactored into more granular, function-specific roles to adhere to security best practices.
