---

description: "Task list for security vulnerability fixes implementation"
---

# Tasks: Security Vulnerability Fixes

**Input**: Design documents from `specs/001-security-fixes/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests REQUIRED for all fixes (per Constitution: Test-First Development)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Django app: `apps/<app_name>/`
- Tests: `apps/<app_name>/tests.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup required - existing project modifications only

No tasks - proceed to foundational phase.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Security fixes require no blocking prerequisites - can proceed directly to user story implementation

No tasks - proceed to user story phases.

---

## Phase 3: User Story 1 - Magic Link One-Time Use (Priority: P1) 🎯 MVP

**Goal**: Reject magic link authentication if token is already consumed

**Independent Test**: Generate a magic link, consume it once, then attempt to use it again. Second use must be rejected.

### Tests for User Story 1 (REQUIRED - TDD) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T001 [P] [US1] Add test: verify_magic_link rejects already-consumed token in apps/client_portal/tests.py
- [X] T002 [P] [US1] Add test: verify_magic_link succeeds on first use in apps/client_portal/tests.py

### Implementation for User Story 1

- [X] T003 [P] [US1] Fix verify_magic_link() in apps/client_portal/services.py to reject if is_consumed=True
- [X] T004 [US1] Add logging for rejected consumed token attempts in apps/client_portal/services.py

**Checkpoint**: At this point, magic link one-time use is enforced and independently testable

---

## Phase 4: User Story 2 - Approval Workflow Enforcement (Priority: P1)

**Goal**: Reject approval attempts on posts not in approvable states

**Independent Test**: Create a draft post, attempt to directly approve it via API. Approval must be rejected with clear error.

### Tests for User Story 2 (REQUIRED - TDD) ⚠️

- [X] T005 [P] [US2] Add test: approve_post rejects draft status in apps/approvals/tests.py
- [X] T006 [P] [US2] Add test: approve_post rejects rejected status in apps/approvals/tests.py
- [X] T007 [P] [US2] Add test: approve_post rejects changes_requested status in apps/approvals/tests.py
- [X] T008 [P] [US2] Add test: approve_post accepts submitted status in apps/approvals/tests.py

### Implementation for User Story 2

- [X] T009 [P] [US2] Fix approve_post() eligible_from_states in apps/approvals/services.py
- [X] T010 [US2] Add clear error message for invalid approval states in apps/approvals/services.py
- [X] T011 [US2] Add logging for rejected approval attempts in apps/approvals/services.py

**Checkpoint**: At this point, approval workflow is enforced and independently testable

---

## Phase 5: User Story 3 - Bundled Approval Precision (Priority: P1)

**Goal**: Only advance platform posts specifically in pending_client status during portal approval

**Independent Test**: Create a post with child A in pending_client and child B in draft. Approve through the portal. Only child A should advance.

### Tests for User Story 3 (REQUIRED - TDD) ⚠️

- [X] T012 [P] [US3] Add test: portal approval only advances pending_client children in apps/client_portal/tests.py
- [X] T013 [P] [US3] Add test: portal approval rejects if no children in pending_client in apps/client_portal/tests.py

### Implementation for User Story 3

- [X] T014 [US3] Fix portal_approve view to validate all children are approvable in apps/client_portal/views.py
- [X] T015 [US3] Add error message listing non-approvable children in apps/client_portal/views.py

**Checkpoint**: At this point, bundled approval precision is enforced and independently testable

---

## Phase 6: User Story 4 - Comment Authorization Scope (Priority: P1)

**Goal**: Verify comment edit/delete operations belong to specified workspace and post

**Independent Test**: Create comment in workspace B, access workspace A where user has access. Attempt to edit/delete comment via workspace A URL. Operation must be rejected.

### Tests for User Story 4 (REQUIRED - TDD) ⚠️

- [X] T016 [P] [US4] Add test: update_comment rejects cross-workspace in apps/approvals/tests.py
- [X] T017 [P] [US4] Add test: delete_comment rejects cross-workspace in apps/approvals/tests.py
- [X] T018 [P] [US4] Add test: update_comment rejects wrong post in same workspace in apps/approvals/tests.py

### Implementation for User Story 4

- [X] T019 [P] [US4] Fix update_comment to require workspace and post parameters in apps/approvals/comments.py
- [X] T020 [P] [US4] Fix delete_comment to require workspace and post parameters in apps/approvals/comments.py
- [X] T021 [US4] Update edit_comment view to pass workspace/post in apps/approvals/views.py
- [X] T022 [US4] Update delete_comment view to pass workspace/post in apps/approvals/views.py
- [X] T023 [US4] Add logging for rejected cross-workspace comment operations in apps/approvals/comments.py

**Checkpoint**: At this point, comment authorization scope is enforced and independently testable

---

## Phase 7: User Story 5 - Client Role Enforcement for Portal (Priority: P2)

**Goal**: Enforce workspace_role=CLIENT in portal authentication decorator

**Independent Test**: Create a user with CLIENT role, access portal successfully, change role to ADMIN, attempt portal access again. Second access must be rejected.

### Tests for User Story 5 (REQUIRED - TDD) ⚠️

- [X] T024 [P] [US5] Add test: portal_auth_required rejects non-client role in apps/client_portal/tests.py
- [X] T025 [P] [US5] Add test: portal_auth_required accepts client role in apps/client_portal/tests.py

### Implementation for User Story 5

- [X] T026 [P] [US5] Fix portal_auth_required decorator to check workspace_role=CLIENT in apps/client_portal/decorators.py
- [X] T027 [US5] Add logging for rejected non-client portal access attempts in apps/client_portal/decorators.py

**Checkpoint**: At this point, client role enforcement is enforced and independently testable

---

## Phase 8: User Story 6 - Rate Limiting IP Validation (Priority: P2)

**Goal**: Validate X-Forwarded-For against trusted proxy before use in rate limiting

**Independent Test**: Make requests with X-Forwarded-For header without proxy. Should use actual connection IP, not header value.

### Tests for User Story 6 (REQUIRED - TDD) ⚠️

- [X] T028 [P] [US6] Add test: _get_client_ip ignores X-Forwarded-For without proxy in apps/accounts/tests.py
- [X] T029 [P] [US6] Add test: _get_client_ip uses X-Forwarded-For with trusted proxy in apps/accounts/tests.py

### Implementation for User Story 6

- [X] T030 [P] [US6] Fix _get_client_ip to validate against trusted proxy in apps/accounts/middleware.py
- [X] T031 [US6] Add trusted proxy configuration check in apps/accounts/middleware.py

**Checkpoint**: At this point, rate limiting IP validation is enforced and independently testable

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and quality gates

- [ ] T032 [P] Run full test suite for affected apps in apps/client_portal/ apps/approvals/ apps/accounts/
- [ ] T033 [P] Run ruff check on all modified files
- [ ] T034 [P] Run ruff format --check on all modified files
- [ ] T035 [P] Run mypy type check on all modified files
- [X] T036 Verify all 6 security fixes are working correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: No blocking prerequisites
- **User Stories (Phase 3-8)**: All can proceed independently since they're separate security fixes
- **Polish (Phase 9)**: Depends on all user story phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start immediately - No dependencies on other stories
- **User Story 2 (P1)**: Can start immediately - No dependencies on other stories
- **User Story 3 (P1)**: Can start immediately - No dependencies on other stories
- **User Story 4 (P1)**: Can start immediately - No dependencies on other stories
- **User Story 5 (P2)**: Can start immediately - No dependencies on other stories
- **User Story 6 (P2)**: Can start immediately - No dependencies on other stories

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Implementation follows test verification
- Story complete before moving to polish phase

### Parallel Opportunities

- All test tasks marked [P] can run in parallel within their story
- All user stories can be worked on in parallel (independent security fixes)
- Different user stories can be worked on by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Add test: verify_magic_link rejects already-consumed token in apps/client_portal/tests.py"
Task: "Add test: verify_magic_link succeeds on first use in apps/client_portal/tests.py"

# Implementation tasks can run after tests fail:
Task: "Fix verify_magic_link() in apps/client_portal/services.py"
Task: "Add logging for rejected consumed token attempts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1
2. **STOP and VALIDATE**: Test magic link rejection independently
3. Deploy/demo if ready

### Incremental Delivery

1. Complete Phase 3: User Story 1 → Test → Deploy
2. Complete Phase 4: User Story 2 → Test → Deploy
3. Complete Phase 5: User Story 3 → Test → Deploy
4. Complete Phase 6: User Story 4 → Test → Deploy
5. Complete Phase 7: User Story 5 → Test → Deploy
6. Complete Phase 8: User Story 6 → Test → Deploy
7. Phase 9: Polish and full validation

### Parallel Team Strategy

With multiple developers:

1. Developer A: User Story 1 (Magic Link)
2. Developer B: User Story 2 (Approval Workflow)
3. Developer C: User Story 3 (Bundled Approval)
4. Developer D: User Story 4 (Comment Scope)
5. Developer E: User Story 5 (Client Role)
6. Developer F: User Story 6 (Rate Limiting)
7. All stories complete → Polish phase together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD per Constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All 6 security fixes are independent - can be parallelized freely
