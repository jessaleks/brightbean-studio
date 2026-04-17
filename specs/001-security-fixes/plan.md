# Implementation Plan: Security Vulnerability Fixes

**Branch**: `001-security-fixes` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-security-fixes/spec.md`

## Summary

Fix 6 critical and medium security vulnerabilities in the BrightBean Studio application:
1. Magic link one-time use enforcement (consume on first use, reject subsequent)
2. Approval workflow state validation (reject drafts from bypassing submission)
3. Bundled approval precision (only advance pending_client children)
4. Comment authorization scope (verify workspace/post ownership)
5. Client role enforcement for portal access
6. Rate limiting IP validation (proxy-aware header handling)

These are defensive security fixes - no new features, just hardening existing functionality.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: Django 5.x, pytest, mypy  
**Storage**: PostgreSQL (production) / SQLite (dev) - existing  
**Testing**: pytest with pytest-django  
**Target Platform**: Linux server (Django web application)  
**Project Type**: web-service  
**Performance Goals**: No performance changes - security fixes only  
**Constraints**: Must maintain backward compatibility for existing workflows  
**Scale/Scope**: 6 independent security fixes across 3 Django apps (client_portal, approvals, accounts)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| I. Test-First Development | ✅ PASS | Security fixes will have failing tests before implementation |
| II. Type Safety | ✅ PASS | All changes will include type annotations |
| III. Lint and Format Discipline | ✅ PASS | All changes will pass ruff check/format |
| IV. Integration Testing for External APIs | N/A | No external API changes |
| V. Observability | ✅ PASS | Will add appropriate logging for security events |

**Result**: All gates pass - no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-security-fixes/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - internal fixes)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
apps/
├── client_portal/
│   ├── models.py        # MagicLinkToken model changes
│   ├── services.py      # verify_magic_link() changes
│   ├── decorators.py    # portal_access decorator fix
│   └── views.py         # Approval view changes
├── approvals/
│   ├── services.py      # approve_post() workflow enforcement
│   ├── views.py         # HTTP approval views
│   └── comments.py      # Comment edit/delete scope
└── accounts/
    └── middleware.py   # Rate limiting IP validation
```

**Structure Decision**: Modifications to existing Django apps - no new directory structure needed. Changes are localized to the 3 affected apps identified in the security findings.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all gates pass.
