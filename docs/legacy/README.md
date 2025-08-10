# 📚 Legacy Documentation

This directory contains documentation that was moved from the canonical structure defined in `docs/README.md`.

## Why This Directory Exists

The BuildingOS documentation follows a strict structure defined in `docs/README.md`:
- `00-business-context/` - Business context and campaign briefs
- `01-project-vision/` - Project charter and requirements  
- `02-architecture/` - System design and technical decisions
- `03-development/` - Development tools and implementation status
- `04-operations/` - Production maintenance and operations

## Moved Items

### Files Moved from Root
- `LIT760-Campaign-Brief.md` - Moved to `00-business-context/` (duplicate)
- `Questionário de Levantamento de Requisitos.docx` - Out of scope for docs-as-code
- `Questionário de levantamento de requisitos.md` - Out of scope for docs-as-code  
- `sad.md` - Empty/temporary file
- `setup-guide.md` - Duplicate of `03-development/06-setup-guide.md`
- `temporario.md` - Empty/temporary file

### Directories Moved
- `03-operations/` - Consolidated into `04-operations/` per canonical structure
  - Unique lesson `14-terraform-provider-inconsistency-and-solutions.md` preserved in `04-operations/04-lessons/`
- `03-development/` - Files outside canonical index (01-06) moved to `legacy/03-development/`
  - `03-api-fix-plan.md` - API fix planning (superseded by current status)
  - `06-testing-tools-integration.md` - Testing integration guide (superseded)
  - `07-api-status-baseline.md` - API status baseline (superseded)
  - `08-frontend-architecture-adaptation.md` - Frontend architecture (superseded)
  - `08-sns-migration-guide.md` - SNS migration guide (superseded)
  - `09-architect-context-prompt.md` - Duplicate of `04-architect-context-prompt.md`
  - `09-chat-sns-communication-flow.md` - Chat SNS flow (superseded)
  - `10-chat-sns-visual-diagram.md` - Visual diagrams (superseded)
  - `11-websocket-hybrid-implementation.md` - WebSocket implementation (superseded)
  - `12-senior-agent-prompt.md` - Senior agent prompt (superseded)
  - `lessons/` - Development lessons learned (moved to `03-development/lessons/`)

## Lessons Reorganization

**Lessons have been reorganized by domain:**
- **Architecture Lessons:** `docs/02-architecture/lessons/` - API and system architecture lessons
- **Development Lessons:** `docs/03-development/lessons/` - Python, testing, and environment lessons  
- **Operations Lessons:** `docs/04-operations/04-lessons/` - Infrastructure, deployment, and operations lessons

## Migration Notes

- **Date**: August 7, 2025
- **Reason**: Align with canonical documentation structure
- **Impact**: No functional changes, only organizational
- **Next Steps**: Review and potentially delete empty files, archive old questionnaires

## Recovery

If you need to access any of these files, they are preserved here. Consider:
1. Moving relevant content to canonical locations
2. Updating references in other documents
3. Deleting truly obsolete files

---

**Navigation:**
⬅️ Back: [Documentation Index](../README.md)
