# Data Model: Security Vulnerability Fixes

**Date**: 2026-04-13

This feature modifies existing logic in existing models - no schema changes required.

## Existing Entities

### MagicLinkToken (apps/client_portal/models.py)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| user | FK to User | Token owner |
| workspace | FK to Workspace | Workspace scope |
| token | Char(128) | Plaintext token (finding) |
| created_at | DateTime | Creation timestamp |
| expires_at | DateTime | Expiry (30 days default) |
| last_used_at | DateTime | Last use timestamp |
| is_consumed | Boolean | Consumed flag |

**Logic Change**: Reject if `is_consumed=True` before allowing authentication.

---

### Post (apps/approvals/models.py)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| workspace | FK to Workspace | Owning workspace |
| author | FK to User | Post author |
| status | Enum | draft, submitted, pending_review, approved, pending_client, published, rejected, changes_requested |

**Status Flow**:
```
draft → submitted → pending_review → approved → pending_client → published
         ↑              ↓                ↓           ↓            ↓
       rejected ← changes_requested
```

**Logic Change**: `approve_post()` MUST only accept targets in "submitted" or "pending_review" status.

---

### PostComment (apps/approvals/models.py)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| post | FK to Post | Parent post |
| workspace | FK to Workspace | Owning workspace |
| author | FK to User | Comment author |
| body | Text | Comment content |
| deleted_at | DateTime | Soft delete timestamp |

**Logic Change**: `update_comment()` and `delete_comment()` MUST verify comment belongs to specified workspace and post.

---

### WorkspaceMembership (apps/workspaces/models.py)

| Field | Type | Notes |
|-------|------|-------|
| user | FK to User | Member user |
| workspace | FK to Workspace | Member workspace |
| workspace_role | Enum | admin, editor, viewer, client |

**Logic Change**: `portal_auth_required` decorator MUST verify `workspace_role == "client"`.

---

## Validation Rules

### Magic Link Validation

1. Token exists in database
2. Token not expired (`now <= expires_at`)
3. Token not consumed (`is_consumed == False`)
4. On success: mark consumed and update `last_used_at`

### Approval State Validation

1. Target post status in `{"submitted", "pending_review", "pending_client"}`
2. Target platform posts status in same set
3. Reject with clear error for invalid states

### Comment Authorization

1. Comment exists and not deleted
2. Comment.workspace == request.workspace
3. Comment.post == request.post
4. For edit: comment.author == user
5. For delete: author OR user has approve_posts permission in workspace
