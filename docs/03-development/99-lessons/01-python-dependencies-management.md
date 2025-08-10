---
date: "2025-08-05"
tags:
  - "Python"
  - "Dependencies"
  - "Lambda"
---

# Lesson: Python Dependencies Management in Lambda Functions

## Context

During the implementation of new Lambda agents (Coordinator, Agent_Elevator, Agent_PSIM), we discovered that all agents were missing `requirements.txt` files, which could cause silent runtime failures when functions tried to import unavailable libraries.

## Lesson Learned

Lambda functions fail silently during deployment if Python dependencies are not properly specified. Terraform does not detect missing Python dependencies, so errors only appear in CloudWatch logs during execution. Always create `requirements.txt` files with exact version specifications for all Lambda functions.

## Suggested Action

For all new Lambda agents:
1. **Always create** `requirements.txt` with exact versions
2. **Test locally** with specified dependencies before deployment
3. **Use consistent versions** across related functions
4. **Include minimal dependencies** only what is actually needed

Example format:
```
boto3==1.34.145
requests==2.32.3
PyJWT==2.8.0
```
