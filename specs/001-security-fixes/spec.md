# Feature Specification: Security Vulnerability Fixes

**Feature Branch**: `001-security-fixes`  
**Created**: 2026-04-13  
**Status**: Draft  
**Input**: User description: "review and fix the most pressing issues Findings
1. High: client portal magic links are effectively long-lived bearer tokens, not one-time links. MagicLinkToken.token is stored in plaintext and verify_magic_link() still returns success after is_consumed is already set, only updating last_used_at on later replays. That means any leaked link or DB read of the token field gives reusable portal login until expiry. See apps/client_portal/models.py:38-43 and apps/client_portal/services.py:96-114.
2. High: the approval service can bypass the intended workflow and approve drafts directly. approve_post() accepts targets in draft, rejected, and changes_requested, and the HTTP approve views call it without any additional state gate. A direct POST to the normal approval endpoint can move a draft straight to approved/pending_client, skipping submission/review. See apps/approvals/services.py:132-146 and apps/approvals/views.py:133-141.
3. High: bundled approval can advance the wrong platform posts. Both internal and portal approval views operate on a whole Post, and approve_post() applies to every eligible child platform post under that post. If one child is pending_client but another is still draft or changes_requested, approving the post will also advance that sibling. The portal check only verifies that at least one pending-client child exists. See apps/client_portal/views.py:117-127 and apps/approvals/services.py:132-156.
4. High: comment edit/delete paths are not scoped to the workspace or post in the URL. update_comment() and delete_comment() fetch by comment_id only; the views verify access to the URL workspace, but never prove the comment belongs to that workspace/post. A user who authored a comment in workspace B and has any access to workspace A can edit/delete it through workspace A routes, and a moderator in any workspace can delete arbitrary comments by UUID. See apps/approvals/comments.py:65-109 and apps/approvals/views.py:316-355.
5. Medium: the portal auth decorator does not enforce client role even though the comment says it does. It accepts any WorkspaceMembership for the workspace, not workspace_role=CLIENT. That weakens the boundary around the passwordless portal and allows portal access to continue after role changes away from client. See apps/client_portal/decorators.py:35-46.
6. Medium: auth rate limiting trusts X-Forwarded-For directly. If the app is reachable without a proxy that strips/spoofs that header, attackers can rotate fake IPs to bypass limits or rate-limit other users. See apps/accounts/middleware.py:69-73."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Magic Link One-Time Use (Priority: P1)

A client receives a magic link to approve a post. The link must work exactly once. If the link is used, reused, or intercepted, it must not grant continued access.

**Why this priority**: This is a critical security vulnerability - any leaked token grants indefinite access until expiry.

**Independent Test**: Generate a magic link, consume it once, then attempt to use it again. Second use must be rejected.

**Acceptance Scenarios**:

1. **Given** a valid unused magic link, **When** the client uses it to access the portal, **Then** the client can view the post and authentication succeeds.
2. **Given** a magic link that has already been used once, **When** the client attempts to use it again, **Then** authentication fails with an appropriate error message.
3. **Given** an expired magic link token, **When** the client attempts to use it, **Then** authentication fails.

---

### User Story 2 - Approval Workflow Enforcement (Priority: P1)

A team member attempts to approve a draft post directly. The system must reject this attempt and require the post to go through proper submission and review.

**Why this priority**: Bypassing the approval workflow undermines content governance and client expectations.

**Independent Test**: Create a draft post, attempt to directly approve it via API. Approval must be rejected with clear error.

**Acceptance Scenarios**:

1. **Given** a post in "draft" status, **When** an internal user attempts to approve it, **Then** the system rejects the approval with an error indicating the post must be submitted first.
2. **Given** a post in "rejected" status, **When** an internal user attempts to approve it, **Then** the system rejects the approval.
3. **Given** a post in "changes_requested" status, **When** an internal user attempts to approve it, **Then** the system rejects the approval.
4. **Given** a post in "submitted" status, **When** an internal user attempts to approve it, **Then** the approval succeeds and the post advances to "approved".

---

### User Story 3 - Bundled Approval Precision (Priority: P1)

When a post has multiple platform-specific child posts, approving the parent must only advance the specific child posts that are ready, not unrelated siblings in wrong states.

**Why this priority**: Advancing unrelated posts in the wrong state breaks workflow and causes confusion.

**Independent Test**: Create a post with child A in pending_client and child B in draft. Approve through the portal. Only child A should advance.

**Acceptance Scenarios**:

1. **Given** a post with platform child A in "pending_client" and child B in "draft", **When** the client approves via portal, **Then** only child A advances to approved, child B remains in draft.
2. **Given** a post with all children in "pending_client", **When** approval is requested, **Then** all eligible children advance to approved.
3. **Given** a post with platform children in various non-approvable states, **When** approval is attempted, **Then** the system rejects with clear error indicating which children cannot be approved.

---

### User Story 4 - Comment Authorization Scope (Priority: P1)

Comment edit and delete operations must verify the comment belongs to the specified workspace and post before allowing the operation.

**Why this priority**: Without scope verification, users can modify comments across workspaces they don't own.

**Independent Test**: Create comment in workspace B, access workspace A where user has access. Attempt to edit/delete the comment via workspace A's URL. Operation must be rejected.

**Acceptance Scenarios**:

1. **Given** a comment belonging to workspace B, **When** a user with access to workspace A attempts to edit it via workspace A routes, **Then** the operation is rejected with permission denied.
2. **Given** a comment on a specific post in workspace B, **When** a user attempts to edit it but references a different post in the same workspace, **Then** the operation is rejected.
3. **Given** a comment belonging to workspace B, **When** the comment author edits it within the correct workspace, **Then** the edit succeeds.

---

### User Story 5 - Client Role Enforcement for Portal (Priority: P2)

The client portal authentication must verify the user has the CLIENT role, not just any membership in the workspace.

**Why this priority**: Former clients should not retain portal access after role changes.

**Independent Test**: Create a user with CLIENT role, access portal successfully, change role to ADMIN, attempt portal access again. Second access must be rejected.

**Acceptance Scenarios**:

1. **Given** a user with workspace_role=CLIENT in a workspace, **When** the user accesses the client portal, **Then** access is granted.
2. **Given** a user whose role was changed from CLIENT to another role, **When** the user attempts to access the client portal, **Then** access is rejected.

---

### User Story 6 - Rate Limiting IP Validation (Priority: P2)

Rate limiting must not trust X-Forwarded-For header directly without validation, to prevent IP spoofing attacks.

**Why this priority**: Attackers can bypass rate limits by rotating fake IPs in X-Forwarded-For.

**Acceptance Scenarios**:

1. **Given** direct IP access without proxy, **When** rate limiting is evaluated, **Then** the actual client IP is used.
2. **Given** a request with X-Forwarded-For header, **When** the app is behind a trusted proxy configured, **Then** the last trusted IP in the chain is used.
3. **Given** a request with X-Forwarded-For header, **When** the app is NOT behind a proxy, **Then** the header is ignored and the actual connection IP is used.

---

### Edge Cases

- Magic link used simultaneously by multiple requests (race condition)
- Approval attempted on post with no children in approvable state
- Comment edit after post has been deleted
- Client role changed during active portal session
- Rate limit applied to legitimate users due to header spoofing

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST consume magic link tokens immediately upon successful verification and reject all subsequent uses, even within the expiry window.
- **FR-002**: System MUST store magic link tokens in a way that prevents reuse if the database is compromised (e.g., hash comparison, not plaintext storage).
- **FR-003**: System MUST reject approval attempts on posts in "draft", "rejected", or "changes_requested" status, allowing approval only from "submitted" status.
- **FR-004**: System MUST only advance platform-specific child posts that are specifically in "pending_client" status when processing client approvals.
- **FR-005**: System MUST verify comment edit/delete operations belong to the specified workspace and post before execution.
- **FR-006**: System MUST verify the requesting user has workspace_role=CLIENT for the portal decorator, not just any membership.
- **FR-007**: System MUST validate X-Forwarded-For header against trusted proxy configuration before using it for rate limiting.

### Key Entities

- **MagicLinkToken**: One-time authentication token with consumed flag and timestamp
- **Post**: Content post with approval status and platform-specific children
- **Comment**: Comment linked to specific workspace and post
- **WorkspaceMembership**: User membership with role (CLIENT, ADMIN, etc.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Reused magic links are rejected 100% of the time, preventing unauthorized access.
- **SC-002**: Approval workflow violations are blocked before any state change occurs.
- **SC-003**: Bundled approvals only affect intended children, with zero unintended state advances.
- **SC-004**: Cross-workspace comment operations are rejected 100% of the time.
- **SC-005**: Former clients cannot access portal after role change.
- **SC-006**: Rate limiting uses authentic IPs, preventing spoofing-based bypass.

## Assumptions

- The trusted proxy configuration is available in environment variables or settings
- Magic link tokens are currently stored in plaintext and need migration/hashing strategy
- The approval status flow is: draft → submitted → approved/pending_client → published
- The portal decorator comment incorrectly states CLIENT role is enforced when it does not
- Comment operations currently lack workspace/post scope validation
