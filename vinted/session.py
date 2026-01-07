"""HTTP session wrapper used by API clients.

This module exposes `HttpSession`, a thin wrapper around
`curl_cffi.AsyncSession` that handles cookie persistence, proxy
configuration and simple retry-on-auth semantics used by the library.
"""

import logging
from urllib.parse import urlparse

from curl_cffi import AsyncSession
from curl_cffi.requests import Response
from curl_cffi.requests.exceptions import HTTPError as CurlHTTPError

from vinted.exceptions import VintedAPIError, VintedAuthError, VintedNetworkError

from .auth import AuthManager
from .constants import (
    DEFAULT_HEADERS,
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_UNAUTHORIZED,
)
from .storage import CookieStorage
from .utils import format_proxy_for_log, get_accept_language

logger = logging.getLogger(__name__)


class HttpSession:
    """Session helper that manages cookies, headers and proxy settings.

    The class wraps `curl_cffi.AsyncSession` and provides helpers to
    load/save cookies via a `CookieStorage`, refresh cookies when the
    authentication token is expired, and perform GET requests with a
    minimal retry-on-auth flow.

    Args:
        proxy: Optional proxy host:port (without scheme).
        storage: Optional `CookieStorage` instance for persistence.
    """

    def __init__(
        self,
        proxy: str | None = None,
        storage: CookieStorage | None = None,
    ):
        self.proxy = proxy
        self.base_url: str | None = None
        self.locale: str | None = None

        self.session: AsyncSession = AsyncSession()
        self.auth = AuthManager(self.session)
        self.storage = storage

        self._init_headers()
        self._configure_proxy()

        logger.debug(
            "HttpSession initialized: proxy=%s, storage=%s",
            format_proxy_for_log(proxy),
            storage.__class__.__name__ if storage else None,
        )

    def _init_headers(self) -> None:
        self.session.headers.update(DEFAULT_HEADERS)

    def _configure_proxy(self) -> None:
        if self.proxy:
            proxy_url = f"http://{self.proxy}"
            self.session.proxies.update(
                {
                    "http": proxy_url,
                    "https": proxy_url,
                }
            )

    def configure_from_url(self, url: str) -> None:
        parsed = urlparse(url)
        self.base_url = f"https://{parsed.netloc}"

        domain_parts = parsed.netloc.split(".")
        if len(domain_parts) > 1:
            self.locale = domain_parts[-1]
            accept_language = get_accept_language(self.locale)
            self.session.headers.update({"Accept-Language": accept_language})

        self.session.headers.update({"Referer": self.base_url})
        logger.debug("Configured: base_url=%s, locale=%s", self.base_url, self.locale)

    async def refresh_cookies(self) -> None:
        if not self.base_url:
            raise VintedAPIError("base_url not configured")

        logger.debug("Refreshing session cookies...")

        self._clear_cookies()

        self.session.headers.update({"Referer": ""})

        try:
            response = await self.session.head(self.base_url, impersonate="chrome", verify=True)
            response.raise_for_status()
        except CurlHTTPError as e:
            raise VintedNetworkError("Failed to refresh cookies", e)
        except Exception as e:
            raise VintedNetworkError("Network error during cookie refresh", e)

        logger.debug("Fresh cookies received: %d cookies", len(self.session.cookies))

        if self.storage:
            self.storage.save(self.session.cookies.jar)

        logger.info("Session cookies refreshed successfully")

    def _clear_cookies(self) -> None:
        self.session.cookies.clear()
        if self.storage:
            self.storage.clear()
        logger.debug("Cookies cleared")

    def _load_cookies(self) -> bool:
        if not self.storage:
            return False

        try:
            self.storage.load(self.session.cookies.jar)
            return True
        except Exception as e:
            logger.error("Failed to load cookies: %s", e)
            return False

    async def request(self, url: str, params: dict | None = None) -> Response:
        cookies_loaded = self._load_cookies()

        if cookies_loaded:
            if self.auth.is_token_expired():
                logger.info("Access token expired, refreshing cookies")
                await self.refresh_cookies()
        else:
            # Если куки не были загружены, то рефрешим
            logger.debug("No saved cookies, refreshing...")
            await self.refresh_cookies()

        try:
            response: Response = await self.session.get(
                url=url,
                params=params,
                impersonate="chrome",
                verify=True,
            )
            logger.debug("Request status: %s", response.status_code)
        except CurlHTTPError as e:
            raise VintedNetworkError("HTTP request failed", e)
        except Exception as e:
            raise VintedNetworkError("Network error", e)

        if response.status_code in (HTTP_STATUS_UNAUTHORIZED, HTTP_STATUS_FORBIDDEN):
            logger.warning("Auth failed, refreshing cookies...")
            await self.refresh_cookies()

            try:
                retry_response: Response = await self.session.get(
                    url=url,
                    params=params,
                    impersonate="chrome",
                    verify=True,
                )
                response = retry_response
                logger.debug("Retry status: %s", response.status_code)
            except CurlHTTPError as e:
                raise VintedAuthError(
                    "Authentication failed after retry", status_code=e.code, response=response
                )
            except Exception as e:
                raise VintedNetworkError("Network error on retry", e)

        if response.status_code >= 400:
            raise VintedAPIError(
                f"HTTP {response.status_code}: {response.reason}",
                status_code=response.status_code,
                response=response,
            )

        return response

    async def close(self) -> None:
        await self.session.close()
