---
status: "Accepted"
date: "2025-08-03"
author: "Jomil & GitHub Copilot"
tags:
  - "Documentation"
  - "Tooling"
---

# ADR-001: Migrate Documentation from Notion to Docs-as-Code

## Context

The project's primary documentation, including the Solution Architecture Document (SAD), was initially hosted in an external tool (Notion). During an attempt to update the documentation to align with the current codebase, a critical limitation was discovered in the Notion API's capabilities for programmatically updating content blocks.

The available API endpoints did not support safe, transactional updates of existing content. The only method to "update" a block was a destructive sequence of `delete` followed by `append`, which introduced a significant risk of data loss if the second operation failed. This made it impossible for automated agents, like GitHub Copilot, to safely maintain and evolve the documentation as a "living" asset, which is a core principle of the project.

## Decision

We have decided to abandon the use of Notion as our primary documentation platform. All critical project documentation will be migrated into the main Git repository in Markdown format, following a **Docs-as-Code** approach.

This includes:
-   Solution Architecture Document (SAD)
-   Development System Setup Guide
-   Architecture Decision Records (ADRs)
-   Component Registry
-   Lessons Learned Database

A new `/docs` directory will be created in the root of the repository to house this documentation. Structured data (like component status or ADR metadata) will be managed using YAML Frontmatter within each Markdown file.

## Consequences

### Positive

-   **Full Editability:** The documentation can now be safely and reliably read and updated by automated tools and agents.
-   **Version Control:** All documentation is now versioned alongside the source code in Git, providing a clear history of changes.
-   **Single Source of Truth:** Developers no longer need to switch between the codebase and an external tool.
-   **Improved Review Process:** Documentation changes can be included in Pull Requests and undergo the same review process as code.
-   **Offline Access:** The documentation is available locally to anyone who clones the repository.

### Negative

-   **Loss of Notion's UI:** We lose the rich, collaborative user interface and database features of Notion.
-   **Manual Formatting:** Creating tables and complex layouts in Markdown is less user-friendly than in Notion.
-   **Requires Git Knowledge:** Contributing to the documentation now requires a basic understanding of Git (clone, commit, push, pull request).
