"""Tests for client portal authentication security fixes."""

from django.test import TestCase
from django.http import HttpRequest
from unittest.mock import MagicMock, patch

from apps.client_portal.decorators import portal_auth_required


class ClientRoleEnforcementTest(TestCase):
    """Test that portal access requires client role."""

    def test_portal_auth_required_rejects_non_client_role(self):
        """portal_auth_required should reject users without client role."""
        request = HttpRequest()
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.session = {"is_portal_session": True, "portal_workspace_id": "workspace-id"}

        workspace = MagicMock()
        workspace.id = "workspace-id"

        membership = MagicMock()
        membership.workspace_role = "admin"

        with patch("apps.client_portal.decorators.Workspace.objects") as mock_ws:
            mock_ws.objects.get.return_value = workspace
            with patch("apps.client_portal.decorators.WorkspaceMembership.objects") as mock_mem:
                mock_mem.filter.return_value.select_related.return_value.first.return_value = membership
                decorated_view = portal_auth_required(lambda req: HttpRequest())
                response = decorated_view(request)

        self.assertEqual(response.url, "client_portal:magic_link_expired")

    def test_portal_auth_required_accepts_client_role(self):
        """portal_auth_required should accept users with client role."""
        request = HttpRequest()
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.session = {"is_portal_session": True, "portal_workspace_id": "workspace-id"}

        workspace = MagicMock()
        workspace.id = "workspace-id"

        membership = MagicMock()
        membership.workspace_role = "client"

        with patch("apps.client_portal.decorators.Workspace.objects") as mock_ws:
            mock_ws.objects.get.return_value = workspace
            with patch("apps.client_portal.decorators.WorkspaceMembership.objects") as mock_mem:
                mock_mem.filter.return_value.select_related.return_value.first.return_value = membership
                mock_view = MagicMock(return_value=HttpRequest())
                decorated_view = portal_auth_required(mock_view)
                response = decorated_view(request)

        mock_view.assert_called_once()
