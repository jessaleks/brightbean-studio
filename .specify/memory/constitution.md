<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0 (initial filled constitution)
- Modified principles: N/A (all new)
- Added sections: Core Principles (5), Additional Constraints (3), Development Workflow (3), Governance (3)
- Removed sections: none
- Templates requiring updates: ✅ .specify/templates/plan-template.md (Constitution Check section already aligned)
  ✅ .specify/templates/spec-template.md (already aligned)
  ✅ .specify/templates/tasks-template.md (already aligned)
- Follow-up TODOs: none
-->

# BrightBean Studio Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)
TDD mandatory: Tests written before implementation. Red-Green-Refactor cycle strictly enforced. All new features MUST have failing tests before code is written. Use pytest as the primary test framework.

**Rationale**: Ensures correctness from the start and provides regression protection for a complex multi-platform integration system.

### II. Type Safety
Mypy type checking MUST pass with strict mode enabled. All new code MUST include type annotations. Type hints enable refactoring confidence and catch bugs early.

**Rationale**: This is a large Django application with complex business logic. Type safety prevents runtime errors in production.

### III. Lint and Format Discipline
All code MUST pass `ruff check` and `ruff format --check` before merging. Pre-commit hooks enforce this automatically. No exceptions for new code.

**Rationale**: Consistent code style reduces cognitive load and prevents style-related PR discussions. The CI pipeline includes these checks for a reason.

### IV. Integration Testing for External APIs
All provider integrations (Facebook, Instagram, LinkedIn, TikTok, etc.) MUST have integration tests that verify contract compliance. Mock responses MUST be validated against actual API schemas.

**Rationale**: External APIs change frequently. Integration tests catch breaking changes before they affect users.

### V. Observability
Structured logging required for all services. All API interactions MUST log request/response metadata. Error tracking via Sentry integration required.

**Rationale**: This is a multi-tenant system handling user content across 10+ platforms. Debuggability is essential for support.

## Additional Constraints

### Technology Stack
- **Backend**: Django 5.x with Python 3.12+
- **Database**: PostgreSQL for production, SQLite for local dev
- **Testing**: pytest with pytest-django
- **Type Checking**: mypy with django-stubs
- **Linting**: ruff

### Security Requirements
- All API tokens and credentials MUST be encrypted at rest
- 2FA support required for all user accounts
- No third-party aggregator - all integrations use first-party APIs

### Performance Standards
- All API rate limits MUST be tracked per account
- Background tasks MUST handle retries with exponential backoff
- Publish audit log MUST retain 90 days of history

## Development Workflow

### Quality Gates (CI Pipeline)
All PRs MUST pass in this order:
1. `ruff check` - linting
2. `ruff format --check` - formatting
3. `mypy` - type checking
4. `pytest` - all tests pass
5. `Docker build` - image builds successfully
6. `gitleaks` - no secrets committed

### Code Review Requirements
- All PRs require at least one reviewer
- Complexity increases MUST be justified in PR description
- Constitution compliance MUST be verified in review

### Testing Organization
- `tests/unit/` - Unit tests for isolated logic
- `tests/contract/` - Contract tests for API integrations
- `tests/integration/` - Integration tests for user journeys

## Governance

### Amendment Procedure
1. Changes to this constitution require a PR with full rationale
2. Major changes (backward-incompatible) require approval from project maintainer
3. Changes MUST include version bump rationale
4. All team members MUST be notified of changes

### Versioning Policy
- **MAJOR**: Backward incompatible governance changes or principle removals
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review
- All new features MUST verify compliance with constitution principles
- Implementation plans MUST include "Constitution Check" section
- Violations MUST be documented with justification in complexity tracking table

**Version**: 1.0.0 | **Ratified**: 2026-03-25 | **Last Amended**: 2026-04-13
