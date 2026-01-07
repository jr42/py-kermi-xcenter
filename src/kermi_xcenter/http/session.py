"""HTTP session management with cookie-based authentication."""

import logging
from typing import Any

import aiohttp

from ..exceptions import AuthenticationError, HttpError

logger = logging.getLogger(__name__)


class HttpSession:
    """Manages aiohttp session with cookie-based auth and auto-reconnect.

    The x-center device uses session cookies for authentication. This class
    handles login, session maintenance, and automatic re-authentication when
    the session expires.

    Attributes:
        host: Device hostname or IP address
        port: HTTP port (default 80)
        password: Optional password for authentication
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        host: str,
        port: int = 80,
        password: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize HTTP session.

        Args:
            host: Device hostname or IP address
            port: HTTP port (default 80)
            password: Optional password (last 4 digits of serial, or None for unauthenticated)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None
        self._authenticated = False

    @property
    def base_url(self) -> str:
        """Get base URL for API requests."""
        return f"http://{self.host}:{self.port}/api"

    async def _create_session(self) -> None:
        """Create a new aiohttp client session."""
        if self._session is not None:
            await self._session.close()

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        # Use a cookie jar to persist session cookies
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            cookie_jar=aiohttp.CookieJar(),
        )
        self._authenticated = False

    async def login(self) -> None:
        """Authenticate with the device.

        For devices with authentication enabled, sends the password.
        For unauthenticated devices, this is a no-op that verifies connectivity.

        Raises:
            AuthenticationError: If authentication fails
            HttpError: If connection fails
        """
        if self._session is None:
            await self._create_session()

        assert self._session is not None

        if self.password is None:
            # No password - try to access without auth
            # Just verify we can reach the device
            self._authenticated = True
            logger.debug("No password provided, assuming unauthenticated access")
            return

        try:
            async with self._session.post(
                f"{self.base_url}/Security/Login",
                json={"Password": self.password},
            ) as response:
                # Check for HTML response (wrong endpoint or server error)
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    raise HttpError("Received HTML instead of JSON - check device URL")

                if response.status == 200:
                    data = await response.json()
                    if data.get("isValid"):
                        self._authenticated = True
                        logger.debug("Successfully authenticated with x-center")
                        return
                    else:
                        raise AuthenticationError("Invalid password")
                elif response.status == 401:
                    raise AuthenticationError("Authentication required")
                else:
                    raise HttpError(f"Login failed with status {response.status}")

        except aiohttp.ClientError as e:
            raise HttpError(f"Connection failed: {e}") from e

    async def logout(self) -> None:
        """End the current session."""
        if self._session is not None and self._authenticated:
            try:
                async with self._session.post(f"{self.base_url}/Security/Logout"):
                    pass
            except aiohttp.ClientError:
                pass  # Ignore logout errors
            self._authenticated = False

    async def request(
        self, endpoint: str, data: dict[str, Any] | None = None, *, _retry_count: int = 0
    ) -> Any:
        """Make an authenticated API request.

        Automatically handles session expiry by re-authenticating.

        Args:
            endpoint: API endpoint path (e.g., "Menu/GetBundlesByCategory")
            data: JSON body for the request (default: empty dict)
            _retry_count: Internal retry counter (do not set manually)

        Returns:
            The ResponseData from the API response

        Raises:
            HttpError: If the request fails
            AuthenticationError: If re-authentication fails repeatedly
        """
        max_retries = 2

        if _retry_count > max_retries:
            raise AuthenticationError(
                f"Authentication failed after {max_retries} attempts - "
                "check password or device authentication settings"
            )

        if data is None:
            data = {}

        # Ensure we have a session
        if self._session is None:
            await self._create_session()
            await self.login()

        assert self._session is not None

        url = f"{self.base_url}/{endpoint}"

        try:
            async with self._session.post(url, json=data) as response:
                # Check for session expiry (HTML response)
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    logger.debug(
                        "Session expired, re-authenticating (attempt %d)", _retry_count + 1
                    )
                    self._authenticated = False
                    await self.login()
                    # Retry the request with incremented counter
                    return await self.request(endpoint, data, _retry_count=_retry_count + 1)

                if response.status == 401:
                    logger.debug("Got 401, re-authenticating (attempt %d)", _retry_count + 1)
                    self._authenticated = False
                    await self.login()
                    return await self.request(endpoint, data, _retry_count=_retry_count + 1)

                if response.status != 200:
                    raise HttpError(f"Request failed with status {response.status}")

                result = await response.json()
                self._check_api_error(result)
                return result.get("ResponseData")

        except aiohttp.ClientError as e:
            raise HttpError(f"Request failed: {e}") from e

    def _check_api_error(self, response: dict[str, Any]) -> None:
        """Check API response for errors.

        Args:
            response: Full API response dict

        Raises:
            HttpError: If the response indicates an error
        """
        status_code = response.get("StatusCode", 0)
        if status_code != 0:
            display_text = response.get("DisplayText", "")
            detailed_text = response.get("DetailedText", "")
            exception_data = response.get("ExceptionData")

            error_msg = display_text or detailed_text or f"API error {status_code}"
            if exception_data:
                error_msg = f"{error_msg}: {exception_data}"

            raise HttpError(error_msg)

    async def close(self) -> None:
        """Close the session and release resources."""
        if self._session is not None:
            await self._session.close()
            self._session = None
            self._authenticated = False

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._authenticated
