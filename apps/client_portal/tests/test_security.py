"""Tests for client portal security fixes."""

from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock, patch

from apps.client_portal.services import verify_magic_link


class MagicLinkOneTimeUseTest(TestCase):
    """Test that magic links work exactly once."""

    def setUp(self):
        self.user = MagicMock()
        self.user.id = "test-user-id"
        self.workspace = MagicMock()
        self.workspace.id = "test-workspace-id"

    def test_verify_magic_link_rejects_already_consumed_token(self):
        """verify_magic_link should reject tokens that have already been consumed."""
        token = MagicMock()
        token.id = "test-token-id"
        token.user = self.user
        token.workspace = self.workspace
        token.is_expired = False
        token.is_consumed = True

        with patch("apps.client_portal.services.MagicLinkToken.objects") as mock_qs:
            mock_qs.select_related.return_value.get.return_value = token
            user, workspace, is_valid = verify_magic_link("test_token_string")

        self.assertIsNone(user)
        self.assertIsNone(workspace)
        self.assertFalse(is_valid)

    def test_verify_magic_link_succeeds_on_first_use(self):
        """verify_magic_link should succeed on first use."""
        token = MagicMock()
        token.id = "test-token-id"
        token.user = self.user
        token.workspace = self.workspace
        token.is_expired = False
        token.is_consumed = False

        with patch("apps.client_portal.services.MagicLinkToken.objects") as mock_qs:
            mock_qs.select_related.return_value.get.return_value = token
            user, workspace, is_valid = verify_magic_link("test_token_string")

        self.assertTrue(is_valid)
        self.assertEqual(user, self.user)
        self.assertEqual(workspace, self.workspace)
