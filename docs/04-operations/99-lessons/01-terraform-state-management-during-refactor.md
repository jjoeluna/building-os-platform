---
date: "2025-08-04"
tags:
  - "Terraform"
  - "IaC"
  - "Refactoring"
---

# Lesson: Terraform Refactoring Requires Careful State Management

## Context

While refactoring our Terraform code to move IAM roles from the root `main.tf` into a reusable module, we encountered `EntityAlreadyExists` errors during the `apply` phase. The default behavior of Terraform was to try creating the new module-based resources before destroying the old standalone resources, causing a conflict.

## Lesson Learned

Terraform does not have a native "refactor" or "move" command in its workflow. When moving a resource's definition in the code (e.g., into a module), the state must be manually reconciled. The primary tool for this is `terraform state mv`, which tells Terraform the new address of an existing resource. If the state becomes inconsistent, a more manual process of `terraform state rm` followed by `terraform import` (or a clean destroy and apply) is necessary.

## Suggested Action

Establish a standard operating procedure (SOP) for all Terraform refactoring that includes:
1.  Running `terraform plan` to understand the proposed changes.
2.  Using `terraform state mv` to move the state of each affected resource to its new address in the code.
3.  Running `terraform plan` again to confirm that "No changes" are needed before committing the refactored code.
