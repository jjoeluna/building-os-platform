---
date: "2025-08-05"
tags:
  - "Python"
  - "Environment"
  - "Development"
---

# Lesson: Python Virtual Environment Discipline

## Context

During development and testing of the BuildingOS platform, inconsistencies arose from executing Python commands without activating the proper virtual environment, leading to dependency conflicts and deployment uncertainty.

## Lesson Learned

Working without virtual environments causes dependency mixing with system packages, version inconsistencies, and unreliable deployments. The development environment must mirror production requirements exactly to ensure code reliability.

## Suggested Action

Establish strict virtual environment discipline:
1. **Always activate** virtual environment before development
2. **Verify activation** with `(env)` indicator in prompt
3. **Install dependencies** only within activated environment
4. **Document process** clearly for all team members

Commands for Windows PowerShell:
```powershell
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
# Work with activated environment
deactivate
```
