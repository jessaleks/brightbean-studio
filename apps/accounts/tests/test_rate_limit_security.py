"""Tests for rate limiting IP validation security fixes."""

from django.test import TestCase, override_settings
from django.http import HttpRequest
from unittest.mock import MagicMock, patch

from apps.accounts.middleware import AuthRateLimitMiddleware


class RateLimitingIPValidationTest(TestCase):
    """Test that rate limiting validates X-Forwarded-For against trusted proxies."""

    def test_get_client_ip_ignores_x_forwarded_for_without_proxy(self):
        """_get_client_ip should ignore X-Forwarded-For when no trusted proxy configured."""
        request = MagicMock()
        request.META = {
            "REMOTE_ADDR": "192.168.1.1",
            "HTTP_X_FORWARDED_FOR": "10.0.0.1, 192.168.1.1",
        }

        with patch("apps.accounts.middleware.settings") as mock_settings:
            mock_settings.TRUSTED_PROXY_IPS = None
            ip = AuthRateLimitMiddleware._get_client_ip(request)

        self.assertEqual(ip, "192.168.1.1")

    @override_settings(TRUSTED_PROXY_IPS=["192.168.1.100"])
    def test_get_client_ip_uses_x_forwarded_for_with_trusted_proxy(self):
        """_get_client_ip should use X-Forwarded-For when from trusted proxy."""
        request = MagicMock()
        request.META = {
            "REMOTE_ADDR": "192.168.1.100",
            "HTTP_X_FORWARDED_FOR": "203.0.113.50, 192.168.1.100",
        }

        ip = AuthRateLimitMiddleware._get_client_ip(request)

        self.assertEqual(ip, "203.0.113.50")

    @override_settings(TRUSTED_PROXY_IPS=["192.168.1.100"])
    def test_get_client_ip_ignores_untrusted_proxy(self):
        """_get_client_ip should ignore X-Forwarded-For when proxy is not trusted."""
        request = MagicMock()
        request.META = {
            "REMOTE_ADDR": "10.0.0.99",
            "HTTP_X_FORWARDED_FOR": "203.0.113.50, 10.0.0.99",
        }

        ip = AuthRateLimitMiddleware._get_client_ip(request)

        self.assertEqual(ip, "10.0.0.99")
