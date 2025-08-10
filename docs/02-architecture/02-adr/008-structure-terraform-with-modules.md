---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "IaC"
  - "Terraform"
  - "Best Practice"
---

# ADR-008: Structure Terraform Code with Reusable Modules

## Context

As the BuildingOS platform grows, the amount of Terraform code required to define its infrastructure will increase. A decision was needed on how to structure this code to avoid duplication, promote consistency, and improve maintainability.

## Decision

We will structure our Terraform code using a **reusable module-based architecture**. Common, self-contained pieces of infrastructure will be defined as modules in the `/terraform/modules` directory.

The environment-specific configurations (e.g., in `/terraform/environments/dev`) will then instantiate these modules, passing in environment-specific variables. This approach treats pieces of our infrastructure as "classes" (the modules) that can be instantiated as "objects" (the resources in each environment).

## Consequences

### Positive

-   **Don't Repeat Yourself (DRY):** Reduces code duplication significantly. A bug fix or improvement in a module is instantly available to all environments that use it.
-   **Consistency:** Ensures that resources like DynamoDB tables or Lambda functions are created with the same configuration and best practices everywhere.
-   **Abstraction:** Hides the complexity of a resource's implementation behind a simple module interface, making the root environment configurations easier to read and understand.
-   **Faster Development:** Accelerates the creation of new services and environments by composing existing, tested modules.

### Negative

-   **Initial Overhead:** Requires more upfront effort to design and create a well-defined, reusable module compared to writing monolithic configurations.
-   **Versioning Complexity:** Changes to a module can have wide-ranging impacts. This will require careful versioning and testing of modules as the project matures.
