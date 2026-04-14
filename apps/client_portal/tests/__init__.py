"""Tests for client portal security fixes."""

from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock, patch

from apps.client_portal.models import MagicLinkToken
from apps.client_portal.services import verify_magic_link


class MagicLinkOneTimeUseTest(TestCase):
    """Test that magic links work exactly once."""

    def setUp(self):
        self.user = MagicMock()
        self.workspace = MagicMock()
        self.workspace.id = "test-workspace-id"

    def test_verify_magic_link_rejects_already_consumed_token(self):
        """verify_magic_link should reject tokens that have already been consumed."""
        token = MagicLinkToken(
            id="test-token-id",
            user=self.user,
            workspace=self.workspace,
            token="test_token_string",
            expires_at=timezone.now() + timezone.timedelta(days=30),
            is_consumed=True,
        )
        with patch.object(MagicLinkToken.objects, "get") as mock_get:
            mock_get.return_value = token
            user, workspace, is_valid = verify_magic_link("test_token_string")

        self.assertIsNone(user)
        self.assertIsNone(workspace)
        self.assertFalse(is_valid)

    def test_verify_magic_link_succeeds_on_first_use(self):
        """verify_magic_link should succeed on first use."""
        token = MagicLinkToken(
            id="test-token-id",
            user=self.user,
            workspace=self.workspace,
            token="test_token_string",
            expires_at=timezone.now() + timezone.timedelta(days=30),
            is_consumed=False,
        )
        with patch.object(MagicLinkToken.objects, "get") as mock_get:
            mock_get.return_value = token
            with patch.object(token, "save") as mock_save:
                user, workspace, is_valid = verify_magic_link("test_token_string")

        self.assertTrue(is_valid)
        self.assertEqual(user, self.user)
        self.assertEqual(workspace, self.workspace)
