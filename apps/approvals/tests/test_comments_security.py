"""Tests for comment authorization scope security fixes."""

from django.test import TestCase
from unittest.mock import MagicMock, patch

from apps.approvals.comments import update_comment, delete_comment


class CommentAuthorizationScopeTest(TestCase):
    """Test that comment operations are scoped to workspace and post."""

    def setUp(self):
        self.user = MagicMock()
        self.user.id = "test-user-id"
        self.workspace = MagicMock()
        self.workspace.id = "test-workspace-id"
        self.post = MagicMock()
        self.post.id = "test-post-id"

    def test_update_comment_rejects_wrong_workspace(self):
        """update_comment should reject when comment is in different workspace."""
        with patch("apps.approvals.comments.PostComment.objects") as mock_qs:
            mock_qs.filter.return_value.first.return_value = None
            with self.assertRaises(ValueError) as context:
                update_comment("comment-id", self.user, self.workspace, self.post, "new body")

        self.assertIn("Comment not found", str(context.exception))

    def test_delete_comment_rejects_wrong_workspace(self):
        """delete_comment should reject when comment is in different workspace."""
        with patch("apps.approvals.comments.PostComment.objects") as mock_qs:
            mock_qs.filter.return_value.first.return_value = None
            with self.assertRaises(ValueError) as context:
                delete_comment("comment-id", self.user, self.workspace, self.post)

        self.assertIn("Comment not found", str(context.exception))

    def test_update_comment_rejects_wrong_post(self):
        """update_comment should reject when comment is for different post."""
        different_post = MagicMock()
        different_post.id = "different-post-id"

        with patch("apps.approvals.comments.PostComment.objects") as mock_qs:
            mock_qs.filter.return_value.first.return_value = None
            with self.assertRaises(ValueError) as context:
                update_comment("comment-id", self.user, self.workspace, different_post, "new body")

        self.assertIn("Comment not found", str(context.exception))
