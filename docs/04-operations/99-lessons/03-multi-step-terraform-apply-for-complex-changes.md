---
date: "2025-08-04"
tags:
  - "Terraform"
  - "IaC"
  - "Deployment"
---

# Lesson: Complex Terraform Refactoring May Require a Multi-Step Apply

## Context

While refactoring our IAM resources into a reusable module, and later when adding a new SNS topic and updating the IAM policy that depends on it, we encountered a `Provider produced inconsistent final plan` error. This occurred because Terraform could not resolve the dependency chain in a single plan/apply cycle. Specifically, it tried to use the ARN of a resource that had not yet been created within the same `apply` operation.

## Lesson Learned

For complex changes involving the creation of a new resource and the immediate use of its attributes in another resource (especially within a `for_each` loop in a module), a single `terraform apply` may fail. The dependency graph can become too complex for the provider to resolve in one pass.

The solution is to break the deployment into smaller, atomic steps:
1.  **Isolate the new resource:** Temporarily comment out the parts of the configuration that *consume* the new resource.
2.  **Apply Step 1:** Run `terraform apply` to create only the new resource (e.g., the `aws_iam_policy`).
3.  **Integrate the new resource:** Uncomment the remaining configuration.
4.  **Apply Step 2:** Run `terraform apply` again. Now that the resource exists and its attributes are known, Terraform can successfully plan and apply the rest of the changes.

## Suggested Action

When encountering "inconsistent final plan" or complex dependency errors during an `apply`, immediately consider if the changes can be broken down into smaller, sequential applications. This multi-step approach is a valid and sometimes necessary technique for unblocking complex infrastructure refactoring.
