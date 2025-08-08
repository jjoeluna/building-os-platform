---
date: "2025-08-04"
tags:
  - "Development"
  - "Environment"
  - "Python"
---

# Lesson: Local Environment Must Accurately Mimic the CI/CD and Production Environments

## Context

During development, we encountered linter errors for missing packages (`boto3`) and confusion about where dependencies were being installed. This was caused by inconsistently activating the local Python virtual environment (`.venv`). Commands were sometimes run against the global Python installation instead of the project-specific one.

## Lesson Learned

A virtual environment is only effective if it is consistently used. The activation of the `.venv` must be the first, reflexive step of any development session. The linter in the IDE (VS Code) must also be configured to use the interpreter from within the `.venv` to provide accurate feedback.

## Suggested Action

1.  **Automate Activation:** Create a simple script or VS Code task that activates the virtual environment upon opening the project to reduce human error.
2.  **Standardize Setup:** The `setup-guide.md` should include a step to ensure the VS Code Python interpreter is correctly pointed to `./.venv/Scripts/python.exe`.
3.  **CI Check:** The CI pipeline should always install dependencies from a `requirements.txt` file in a clean environment, which serves as a final check that all dependencies are correctly declared.
