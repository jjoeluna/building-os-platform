---
date: "2025-08-04"
tags:
  - "Process"
  - "Testing"
  - "DevOps"
---

# Lesson: Incremental Validation is Faster Than Big Bang Debugging

## Context

Throughout the infrastructure build-out, we followed a pattern of implementing a single component or connection and then immediately testing it. For example, we deployed the `health_check` Lambda and tested its API Gateway endpoint before moving on. We tested the SNS -> Lambda connection for the `director_agent` before adding more complex logic.

## Lesson Learned

This incremental, "slice-by-slice" validation proved highly effective. It allowed us to detect and fix issues (e.g., empty zip files, incorrect API Gateway methods, missing IAM permissions) in a small, isolated context. The feedback loop was immediate and the root cause was obvious.

## Suggested Action

Formalize this as a standard development process. For any new feature that spans multiple components:
1.  Define the smallest possible vertical slice that can be tested.
2.  Implement the infrastructure and code for that slice.
3.  Deploy and test the slice in isolation.
4.  Only once the slice is validated, move on to the next one. This "build a little, test a little" approach is far more efficient than building the entire feature and then trying to debug a complex chain of failures.
