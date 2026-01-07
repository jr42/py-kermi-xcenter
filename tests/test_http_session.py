"""Tests for HTTP session management."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from kermi_xcenter.exceptions import AuthenticationError, HttpError
from kermi_xcenter.http.session import HttpSession


class TestHttpSessionCreation:
    """Test HTTP session initialization."""

    def test_session_creation_minimal(self):
        """Test creating session with minimal parameters."""
        session = HttpSession(host="192.168.1.100")
        assert session.host == "192.168.1.100"
        assert session.port == 80
        assert session.password is None
        assert session.timeout == 10.0

    def test_session_creation_with_password(self):
        """Test creating session with password."""
        session = HttpSession(host="192.168.1.100", password="1234")
        assert session.password == "1234"

    def test_session_creation_custom_port(self):
        """Test creating session with custom port."""
        session = HttpSession(host="192.168.1.100", port=8080, timeout=30.0)
        assert session.port == 8080
        assert session.timeout == 30.0

    def test_base_url(self):
        """Test base URL construction."""
        session = HttpSession(host="192.168.1.100", port=8080)
        assert session.base_url == "http://192.168.1.100:8080/api"


class TestHttpSessionAuthentication:
    """Test HTTP session authentication."""

    @pytest.fixture
    def session(self):
        """Create HTTP session instance."""
        return HttpSession(host="192.168.1.100", password="1234")

    @pytest.fixture
    def session_no_password(self):
        """Create HTTP session without password."""
        return HttpSession(host="192.168.1.100")

    @pytest.mark.asyncio
    async def test_login_no_password(self, session_no_password):
        """Test login without password (unauthenticated access)."""
        await session_no_password.login()
        assert session_no_password.is_authenticated is True

    @pytest.mark.asyncio
    async def test_login_success(self, session):
        """Test successful login with password."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json = AsyncMock(return_value={"isValid": True})

        mock_session = MagicMock()
        mock_session.post = MagicMock(
            return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await session._create_session()
            session._session = mock_session

            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

            await session.login()

            assert session.is_authenticated is True

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, session):
        """Test login with invalid password."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json = AsyncMock(return_value={"isValid": False})

        mock_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=context_manager)

        session._session = mock_session

        with pytest.raises(AuthenticationError, match="Invalid password"):
            await session.login()

    @pytest.mark.asyncio
    async def test_login_401_response(self, session):
        """Test login with 401 response."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.headers = {"Content-Type": "application/json"}

        mock_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=context_manager)

        session._session = mock_session

        with pytest.raises(AuthenticationError, match="Authentication required"):
            await session.login()

    @pytest.mark.asyncio
    async def test_login_html_response(self, session):
        """Test login that returns HTML instead of JSON."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}

        mock_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=context_manager)

        session._session = mock_session

        with pytest.raises(HttpError, match="Received HTML instead of JSON"):
            await session.login()

    @pytest.mark.asyncio
    async def test_login_connection_error(self, session):
        """Test login with connection error."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=aiohttp.ClientError("Connection refused"))

        session._session = mock_session

        with pytest.raises(HttpError, match="Connection failed"):
            await session.login()


class TestHttpSessionRequest:
    """Test HTTP session request handling."""

    @pytest.fixture
    def session(self):
        """Create authenticated HTTP session."""
        s = HttpSession(host="192.168.1.100")
        s._authenticated = True
        return s

    @pytest.mark.asyncio
    async def test_request_success(self, session):
        """Test successful API request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json = AsyncMock(
            return_value={"StatusCode": 0, "ResponseData": {"outdoor_temperature": 15.5}}
        )

        mock_aiohttp_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_aiohttp_session.post = MagicMock(return_value=context_manager)

        session._session = mock_aiohttp_session

        result = await session.request("Menu/GetBundlesByCategory", {"DeviceId": "uuid"})

        assert result == {"outdoor_temperature": 15.5}

    @pytest.mark.asyncio
    async def test_request_api_error(self, session):
        """Test API request that returns error status."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json = AsyncMock(
            return_value={
                "StatusCode": 1,
                "DisplayText": "Device not found",
                "DetailedText": "The requested device was not found",
            }
        )

        mock_aiohttp_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_aiohttp_session.post = MagicMock(return_value=context_manager)

        session._session = mock_aiohttp_session

        with pytest.raises(HttpError, match="Device not found"):
            await session.request("Some/Endpoint", {})

    @pytest.mark.asyncio
    async def test_request_non_200_status(self, session):
        """Test API request with non-200 HTTP status."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.headers = {"Content-Type": "application/json"}

        mock_aiohttp_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_aiohttp_session.post = MagicMock(return_value=context_manager)

        session._session = mock_aiohttp_session

        with pytest.raises(HttpError, match="Request failed with status 500"):
            await session.request("Some/Endpoint", {})

    @pytest.mark.asyncio
    async def test_request_max_retries_on_401(self):
        """Test that request raises AuthenticationError after max retries on 401.

        This prevents infinite recursion when authentication keeps failing.
        Regression test for issue #15.
        """
        # Use no password so login() succeeds without making HTTP call
        session = HttpSession(host="192.168.1.100")
        session._authenticated = True

        # Mock 401 response that triggers re-auth
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.headers = {"Content-Type": "application/json"}

        mock_aiohttp_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_aiohttp_session.post = MagicMock(return_value=context_manager)

        session._session = mock_aiohttp_session

        with pytest.raises(AuthenticationError, match="Authentication failed after"):
            await session.request("Some/Endpoint", {})

    @pytest.mark.asyncio
    async def test_request_max_retries_on_html_response(self):
        """Test that request raises AuthenticationError after max retries on HTML response.

        This prevents infinite recursion when session keeps expiring.
        Regression test for issue #15.
        """
        session = HttpSession(host="192.168.1.100")
        session._authenticated = True

        # Mock HTML response (session expired)
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}

        mock_aiohttp_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_aiohttp_session.post = MagicMock(return_value=context_manager)

        session._session = mock_aiohttp_session

        with pytest.raises(AuthenticationError, match="Authentication failed after"):
            await session.request("Some/Endpoint", {})


class TestHttpSessionClose:
    """Test HTTP session close functionality."""

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing session."""
        session = HttpSession(host="192.168.1.100")

        mock_aiohttp_session = AsyncMock()
        session._session = mock_aiohttp_session
        session._authenticated = True

        await session.close()

        mock_aiohttp_session.close.assert_called_once()
        assert session._session is None
        assert session._authenticated is False


class TestHttpSessionLogout:
    """Test HTTP session logout functionality."""

    @pytest.mark.asyncio
    async def test_logout(self):
        """Test logout."""
        session = HttpSession(host="192.168.1.100")
        session._authenticated = True

        mock_response = AsyncMock()
        mock_aiohttp_session = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_aiohttp_session.post = MagicMock(return_value=context_manager)

        session._session = mock_aiohttp_session

        await session.logout()

        assert session._authenticated is False

    @pytest.mark.asyncio
    async def test_logout_not_authenticated(self):
        """Test logout when not authenticated."""
        session = HttpSession(host="192.168.1.100")
        session._authenticated = False
        session._session = None

        # Should not raise
        await session.logout()
        assert session._authenticated is False
