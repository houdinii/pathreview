"""Integration tests for authentication middleware rejection paths."""

import pytest


@pytest.mark.integration
class TestAuthMiddlewareRejections:
    """Test suite for get_current_user rejection paths (issue #90)."""

    @pytest.mark.skip(reason="stub — implemented in Week 9 (#90)")
    def test_missing_authorization_header_returns_401(self) -> None:
        """Test a missing Authorization header returns 401 'Not authenticated'."""

    @pytest.mark.skip(reason="stub — implemented in Week 9 (#90)")
    def test_malformed_token_returns_401(self) -> None:
        """Test a malformed token returns 401 'Invalid authentication credentials'."""

    @pytest.mark.skip(reason="stub — implemented in Week 9 (#90)")
    def test_expired_token_returns_401(self) -> None:
        """Test an expired token returns the generic 401, not 'Token has expired'."""

    @pytest.mark.skip(reason="stub — implemented in Week 9 (#90)")
    def test_wrong_secret_token_returns_401(self) -> None:
        """Test a token signed with a different secret returns 401."""
