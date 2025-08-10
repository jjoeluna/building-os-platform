---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "IaC"
  - "Terraform"
  - "Best Practice"
---

# ADR-012: Refactor IAM Resources into a Reusable Module

## Context

The initial Terraform configuration in `main.tf` defined IAM roles and policy attachments directly. As the number of roles and policies grew, the file became cluttered, and the definitions were not easily reusable. This violated the Don't Repeat Yourself (DRY) principle and made the code harder to maintain.

## Decision

We will refactor all IAM role and policy attachment logic into a single, reusable **Terraform module** located at `terraform/modules/iam_role`.

This module accepts a role name, an assume role policy, and a list of policy ARNs as input. It is responsible for creating the `aws_iam_role` and looping through the list to create all necessary `aws_iam_role_policy_attachment` resources. The root `main.tf` will now instantiate this module for the `lambda_exec_role` and `step_function_exec_role`, passing the required policies as a list.

## Consequences

### Positive

-   **Improved Readability:** The root `main.tf` is significantly cleaner and easier to understand, as the implementation details of the roles are abstracted away.
-   **Enhanced Reusability:** The module provides a standardized way to create any IAM role with attached policies, accelerating future development.
-   **Centralized Logic:** The logic for creating roles is now in one place, making it easier to enforce standards (e.g., consistent tagging) and apply global changes.
-   **Reduced Code Duplication:** Eliminates the need to repeat `aws_iam_role` and `aws_iam_role_policy_attachment` blocks.

### Negative

-   **State Refactoring Complexity:** The initial move from standalone resources to a module required a `terraform state mv` or a destroy/recreate cycle to align the Terraform state with the new code structure. This is a one-time complexity that needs to be managed carefully.
