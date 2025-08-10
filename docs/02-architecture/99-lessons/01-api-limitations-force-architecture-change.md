---
date: "2025-08-04"
tags:
  - "API"
  - "Architecture"
  - "Documentation"
---

# Lesson: Third-Party API Limitations Can Force Critical Architectural Changes

## Context

The project initially planned to use Notion as a "living documentation" platform, allowing automated agents to update architectural documents. However, during implementation, we discovered that the Notion API's update mechanism was not transactional. The only way to modify a block was a risky, non-atomic `delete` followed by an `append` operation, which introduced a high risk of data loss.

## Lesson Learned

Do not assume a third-party API will fully support your intended use case, even if it seems plausible from the high-level documentation. Critical and non-standard use cases (like safe, transactional content updates) must be validated with a proof-of-concept (PoC) early in the design phase.

## Suggested Action

For future projects, any critical dependency on an external API must be validated with a small PoC before the architecture is finalized. This failure led us to pivot to a more robust Docs-as-Code approach, which should have been considered as a primary option from the start.
