"""Tests for approval workflow security fixes."""

from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock, patch

from apps.approvals.services import approve_post


class ApprovalWorkflowEnforcementTest(TestCase):
    """Test that approval only works from proper states."""

    def setUp(self):
        self.user = MagicMock()
        self.user.id = "test-user-id"
        self.workspace = MagicMock()
        self.workspace.id = "test-workspace-id"
        self.workspace.approval_workflow_mode = "required_internal_and_client"

    def test_approve_post_rejects_draft_status(self):
        """approve_post should reject posts in draft status."""
        post = MagicMock()
        post.id = "test-post-id"
        post.platform_posts = MagicMock()

        platform_post = MagicMock()
        platform_post.status = "draft"
        post.platform_posts.select_related.return_value = [platform_post]

        with patch("apps.approvals.services._resolve_targets") as mock_resolve:
            mock_resolve.return_value = (post, [], True)
            with self.assertRaises(ValueError) as context:
                approve_post(post, self.user, self.workspace)

        self.assertIn("No posts in approvable state", str(context.exception))

    def test_approve_post_accepts_submitted_status(self):
        """approve_post should accept posts in submitted status."""
        post = MagicMock()
        post.id = "test-post-id"
        post.author = None

        platform_post = MagicMock()
        platform_post.status = "submitted"
        platform_post.can_transition_to.return_value = True

        with patch("apps.approvals.services._resolve_targets") as mock_resolve:
            mock_resolve.return_value = (post, [platform_post], True)
            with patch("apps.approvals.services._transition_or_skip") as mock_transition:
                mock_transition.return_value = True
                result = approve_post(post, self.user, self.workspace)

        self.assertEqual(result, post)
