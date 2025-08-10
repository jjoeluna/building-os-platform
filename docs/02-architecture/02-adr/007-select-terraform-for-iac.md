---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "IaC"
  - "Tooling"
  - "Terraform"
---

# ADR-007: Select Terraform for Infrastructure as Code

## Context

To ensure a reproducible, version-controlled, and automated approach to managing cloud infrastructure, a standardized Infrastructure as Code (IaC) tool was required for the project.

## Decision

We will use **HashiCorp Terraform** as the exclusive tool for provisioning and managing all cloud infrastructure resources on AWS. All infrastructure changes must be implemented in Terraform code and deployed through an automated pipeline. Manual changes to the infrastructure in the AWS Console ("click-ops") are explicitly forbidden for production environments.

## Consequences

### Positive

-   **Reproducibility:** Terraform's declarative state ensures that the same configuration results in the same infrastructure every time.
-   **Version Control:** Infrastructure definitions are stored in Git, providing a full history of changes and enabling collaboration.
-   **Automation:** Enables the creation of automated CI/CD pipelines for infrastructure deployment.
-   **Cloud Agnostic (in theory):** While we are using the AWS provider, Terraform's core principles and language are transferable to other cloud providers if needed in the future.
-   **Large Community and Ecosystem:** Benefits from a vast collection of community-contributed modules and extensive documentation.

### Negative

-   **State Management:** Requires careful management of the Terraform state file, which we will mitigate by using a secure S3 backend with state locking.
-   **Learning Curve:** Team members unfamiliar with Terraform and the HCL (HashiCorp Configuration Language) will require training.
-   **Drift Detection:** Requires processes to detect and remediate "drift" (manual changes that cause the real-world infrastructure to differ from the code).
