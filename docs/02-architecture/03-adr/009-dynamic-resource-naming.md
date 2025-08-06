---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "IaC"
  - "Terraform"
  - "Best Practice"
---

# ADR-009: Dynamic Resource Naming by Environment

## Context

To support multiple deployment environments (e.g., dev, stg, prd) from the same Terraform codebase, a strategy was needed for naming cloud resources to ensure they are unique and identifiable to their specific environment. Hardcoding suffixes like `-dev` was identified as an unsustainable practice.

## Decision

We will adopt a **dynamic resource naming** convention. A mandatory `environment` variable will be defined in each environment's configuration (`terraform.tfvars`). All resource names will be constructed by appending this variable to a base name.

Example: `name = "bos-lambda-exec-role-${var.environment}"`

This ensures that the same Terraform code can be applied to different environments, and the resulting resource names will be automatically and correctly suffixed (e.g., `...-dev`, `...-stg`, `...-prd`).

## Consequences

### Positive

-   **Code Reusability:** Allows the exact same Terraform `main.tf` to be used across all environments, adhering to the Don't Repeat Yourself (DRY) principle.
-   **Consistency:** Enforces a consistent and predictable naming scheme for all resources.
-   **Reduced Errors:** Eliminates the risk of manual errors from forgetting to change a hardcoded name when copying configurations for a new environment.
-   **Clarity:** The environment of a resource is immediately identifiable from its name in the AWS Console.

### Negative

-   **Resource Recreation on Refactor:** The initial refactoring of an existing environment to use this pattern may cause Terraform to destroy and recreate resources, as it sees the name changing. This must be planned for.
-   **Variable Dependency:** The codebase is now dependent on the `environment` variable being correctly passed during execution.
