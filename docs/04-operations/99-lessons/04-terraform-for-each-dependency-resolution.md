---
date: "2025-08-05"
tags:
  - "Terraform"
  - "Dependencies"
  - "Deployment"
---

# Lesson: Terraform for_each Dependency Resolution

## Context

During the implementation of the BuildingOS stateless architecture, we encountered a critical Terraform error related to using `for_each` with resources that depend on other resources not yet created.

## Lesson Learned

Terraform's `for_each` cannot use values that are only known during the `apply` phase. When IAM policies reference dynamically created resources, a staged deployment approach is necessary to resolve circular dependencies.

## Suggested Action

For complex infrastructure with interdependent resources:
1. **Staged Deployment**: Remove problematic policies temporarily
2. **Apply Infrastructure**: Deploy base infrastructure first  
3. **Restore Policies**: Add back all policies in second apply
4. **Final Apply**: Complete the infrastructure deployment

This approach resolves `for_each` dependency errors by ensuring all referenced resources exist before they are used in dynamic expressions.
