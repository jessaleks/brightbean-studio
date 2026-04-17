# Quickstart: Security Vulnerability Fixes

**Date**: 2026-04-13

This feature contains security fixes to existing code. No new setup required.

## Development Setup

1. Activate virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Run migrations (if needed):
   ```bash
   python manage.py migrate
   ```

3. Run tests for affected apps:
   ```bash
   pytest apps/client_portal/ apps/approvals/ apps/accounts/
   ```

## Testing the Fixes

### Magic Link One-Time Use

1. Create a magic link via Django admin or shell
2. Use the link once - should succeed
3. Reuse the link - should fail with "Token already used"

### Approval Workflow Enforcement

1. Create a post in "draft" status
2. Attempt to approve via API
3. Should reject with error "Post must be submitted first"

### Bundled Approval Precision

1. Create a post with multiple platform posts
2. Set one to "pending_client", another to "draft"
3. Approve via portal
4. Only the pending_client post should advance

### Comment Authorization

1. Create comment in workspace B
2. Access workspace A where user has access
3. Attempt to edit/delete comment via workspace A URL
4. Should reject with permission denied

### Client Role Enforcement

1. Access portal as client user
2. Change user's role to admin in workspace
3. Attempt to access portal again
4. Should reject access

### Rate Limiting

1. Make requests with X-Forwarded-For header without proxy
2. Should use actual connection IP, not header value

## Running the Full Test Suite

```bash
# Lint
ruff check apps/client_portal/ apps/approvals/ apps/accounts/

# Format
ruff format --check apps/client_portal/ apps/approvals/ apps/accounts/

# Type check
mypy apps/client_portal/ apps/approvals/ apps/accounts/ --ignore-missing-imports

# Tests
pytest apps/client_portal/ apps/approvals/ apps/accounts/ -v
```

## Affected Test Files

- `apps/client_portal/tests.py` - Magic link tests
- `apps/approvals/tests.py` - Approval and comment tests
- `apps/accounts/tests.py` - Rate limiting tests

## Notes

- All changes are logic-only, no migrations needed
- Tests should verify both positive (allowed) and negative (rejected) scenarios
- Run full CI pipeline before merging: `ruff check` → `ruff format --check` → `mypy` → `pytest`
