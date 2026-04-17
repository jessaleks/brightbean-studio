# Research: Security Vulnerability Fixes

**Date**: 2026-04-13

## Decision: Magic Link One-Time Use Fix

**Problem**: `verify_magic_link()` returns `True` even after `is_consumed` is set (lines 104-114 in services.py). It only updates `last_used_at` on replay but still returns success.

**Solution**: Reject authentication if `token.is_consumed` is already True, regardless of expiry.

**Implementation**: Add early return before the consumed check:
```python
if token.is_consumed:
    return None, None, False
```

**Rationale**: The current behavior allows token replay attacks. A leaked token grants access until expiry.

---

## Decision: Approval Workflow State Validation

**Problem**: `approve_post()` accepts targets in "draft", "rejected", and "changes_requested" states (line 133 in services.py).

**Solution**: Only allow approval from "submitted" or "pending_review" states. Reject all others.

**Implementation**: Modify `eligible_from_states` in `_resolve_targets()`:
```python
eligible_from_states={"submitted", "pending_review", "pending_client"}
```

**Rationale**: Drafts must go through submission → review before approval. Bypassing breaks workflow.

---

## Decision: Bundled Approval Precision

**Problem**: Portal approval (client_portal/views.py:121) only checks that at least one child is in "pending_client" before calling `approve_post()`, which advances all eligible children.

**Solution**: Filter targets in `approve_post()` to only include those in "pending_client" status when called from portal context.

**Implementation**: Pass context flag to `approve_post()` or check all children are approvable before calling.

**Rationale**: Should not advance siblings in wrong states.

---

## Decision: Comment Authorization Scope

**Problem**: `update_comment()` and `delete_comment()` in comments.py fetch by comment_id only, with no workspace/post verification.

**Solution**: Pass workspace and post to service functions and verify the comment belongs to them.

**Implementation**:
```python
def update_comment(comment_id, user, workspace, post, body):
    comment = PostComment.objects.filter(
        id=comment_id,
        workspace=workspace,  # ADD
        post=post,             # ADD
        ...
    )
```

**Rationale**: Prevents cross-workspace comment manipulation.

---

## Decision: Client Role Enforcement

**Problem**: `portal_auth_required` decorator (decorators.py:36-46) accepts any WorkspaceMembership, not just CLIENT role.

**Solution**: Add explicit role check:
```python
if membership.workspace_role != "client":
    return redirect("client_portal:magic_link_expired")
```

**Rationale**: Former clients should not retain portal access.

---

## Decision: Rate Limiting IP Validation

**Problem**: `_get_client_ip()` in middleware.py trusts X-Forwarded-For directly without proxy validation.

**Solution**: Check for trusted proxy configuration before using header.

**Implementation**: Add setting for trusted proxy IPs, ignore header if not from trusted source:
```python
TRUSTED_PROXY_IPS = settings.TRUSTED_PROXY_IPS or []
# Validate against trusted proxy before trusting X-Forwarded-For
```

**Rationale**: Prevents IP spoofing attacks.

---

## Technical Details

### Affected Files

| File | Issue | Fix Type |
|------|-------|----------|
| apps/client_portal/services.py:89-114 | Magic link reuse | Logic fix |
| apps/approvals/services.py:125-169 | Approval state bypass | State validation |
| apps/client_portal/views.py:117-127 | Bundled approval | Filter children |
| apps/approvals/comments.py:65-109 | Comment scope | Add workspace/post |
| apps/approvals/views.py:316-355 | Comment scope | Pass context |
| apps/client_portal/decorators.py:35-46 | Client role | Add role check |
| apps/accounts/middleware.py:69-73 | IP spoofing | Proxy validation |

### No Database Migrations Required

All fixes are logic changes. No schema changes needed.

### Testing Strategy

- Unit tests for each service function
- Integration tests for HTTP flows
- Verify rejection scenarios
