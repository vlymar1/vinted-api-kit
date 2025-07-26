import logging
import pickle
from pathlib import Path
from typing import Any, Optional, cast
from urllib.parse import urlparse

import curl_cffi
from curl_cffi import AsyncSession
from curl_cffi.requests import Response
from curl_cffi.requests.exceptions import HTTPError

from vinted_api_kit.client.user_agents import get_random_user_agent

logger = logging.getLogger(__name__)

HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403


class VintedHttpClient:
    """
    Asynchronous HTTP client for Vinted API.

    Manages sessions, headers, proxies, cookies persistence and handles authentication.
    """

    def __init__(
        self,
        locale: Optional[str] = None,
        proxies: Optional[dict[str, str]] = None,
        client_ip: Optional[str] = None,
        cookies_dir: Optional[Path] = None,
        persist_cookies: bool = True,
    ):
        """
        Initialize the HTTP client with optional locale, proxies, client IP and cookie handling.

        Args:
            locale (Optional[str]): Locale code (e.g. 'fr', 'de').
            proxies (Optional[dict]): Proxy settings.
            client_ip (Optional[str]): Client IP for headers.
            cookies_dir (Optional[Path]): Directory to store cookies.
            persist_cookies (bool): Whether to save/load cookies from disk.
        """
        self.locale = locale
        self.proxies = proxies
        self.client_ip = client_ip
        self.base_url: Optional[str] = None
        self.session: AsyncSession = curl_cffi.AsyncSession()
        self.cookies_dir = cookies_dir or Path(".")
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_path = self._generate_cookies_path()
        self.persist_cookies = persist_cookies
        self._init_default_headers()
        if proxies:
            self.session.proxies.update(proxies)  # type: ignore[typeddict-item]
            ip = proxies.get("http", "").split("@")[-1].split(":")[0]
            self._set_x_forwarded_for(ip)
        elif client_ip:
            self._set_x_forwarded_for(client_ip)

    def _generate_cookies_path(self) -> Path:
        """
        Generate file path for cookie storage based on proxies or client IP.

        Returns:
            Path object representing cookies file location.
        """
        if self.proxies:
            proxy_str = self.proxies.get("http") or self.proxies.get("https")
            if proxy_str:
                proxy_uri = urlparse(proxy_str)
                ip = proxy_uri.hostname or "unknown"
                port = proxy_uri.port or 0
                filename = f"cookies_{ip}_{port}.pk"
                return self.cookies_dir / filename
        if self.client_ip:
            ip_safe = self.client_ip.replace(":", "_")
            filename = f"cookies_{ip_safe}.pk"
            return self.cookies_dir / filename
        return self.cookies_dir / "cookies.pk"

    def _init_default_headers(self):
        """
        Set default HTTP headers for all requests.
        """
        self.session.headers.update(
            {
                "User-Agent": get_random_user_agent(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "cache-control": "max-age=0",
                "DNT": "1",
                "Referer": "",
                "Sec-CH-UA": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"macOS"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Money-Object": "true",
            }
        )

    def _set_x_forwarded_for(self, ip) -> None:
        """
        Set 'X-Forwarded-For' HTTP header to the specified IP.
        """
        self.session.headers.update({"X-Forwarded-For": ip})

    def configure_from_url(self, url: str) -> None:
        """
        Configure base URL and locale based on provided URL.

        Args:
            url (str): URL string to parse.
        """
        parsed_url = urlparse(url)
        self.base_url = f"https://{parsed_url.netloc}"
        if not self.locale:
            domain_parts = parsed_url.netloc.split(".")
            if len(domain_parts) > 1:
                self.locale = domain_parts[-1]
        self.session.headers.update({"Referer": self.base_url})

    def save_cookies(self) -> None:
        """
        Persist session cookies to disk if enabled.
        """
        if not self.persist_cookies:
            return
        try:
            with self.cookies_path.open("wb") as f:
                cookies_jar = cast(Any, self.session.cookies.jar)
                pickle.dump(cookies_jar._cookies, f)  # noqa
                logger.debug("Cookies saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")

    def load_cookies(self) -> Optional[dict]:
        """
        Load cookies from disk if available.

        Returns:
            Cookies dictionary or None if not exist/disabled.
        """
        if not self.persist_cookies:
            return None
        if not self.cookies_path.is_file():
            logger.debug("Cookies file does not exist.")
            return None
        try:
            with self.cookies_path.open("rb") as f:
                cookies = pickle.load(f)
            if not isinstance(cookies, dict):
                return None
            logger.debug("Cookies loaded successfully.")
            return cookies
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return None

    async def refresh_session_cookies(self) -> None:
        """
        Refresh session cookies by making a HEAD request to base URL.
        """
        if not self.base_url:
            raise ValueError("base_url is not configured")
        try:
            response = await self.session.head(self.base_url)
            response.raise_for_status()
            self.save_cookies()
            logger.info("Session cookies refreshed.")
        except Exception as e:
            logger.error(f"Failed to refresh session cookies: {e}")

    def _update_auth_headers_from_cookies(self) -> None:
        """
        Update authentication and related headers from stored cookies.
        """
        cookies = self.session.cookies
        access_token_web = cookies.get("access_token_web")
        csrf_token = cookies.get("x-csrf-token")
        anon_id = cookies.get("anon_id")
        accept_language = cookies.get("anonymous-locale")

        if csrf_token:
            self.session.headers.update({"X-Csrf-Token": csrf_token})
        if access_token_web:
            self.session.headers.update({"Authorization": f"Bearer {access_token_web}"})
        if anon_id:
            self.session.headers.update({"X-Anon-Id": anon_id})
        if accept_language:
            self.session.headers.update({"Accept-Language": accept_language})

    async def request(
        self,
        url: str,
        params: Optional[dict] = None,
    ) -> Response:
        """
        Perform an async GET request with cookie and auth management.

        Args:
            url (str): URL for the HTTP GET.
            params (Optional[dict]): Query parameters.

        Returns:
            Response object.

        Raises:
            HTTPError: If response code >= 400.
        """
        loaded_cookies = self.load_cookies()
        cookies_jar = cast(Any, self.session.cookies.jar)
        if loaded_cookies:
            cookies_jar._cookies.update(loaded_cookies)  # noqa
        else:
            await self.refresh_session_cookies()
            loaded_cookies = self.load_cookies()
            if loaded_cookies:
                cookies_jar._cookies.update(loaded_cookies)  # noqa

        self._update_auth_headers_from_cookies()

        response: Response = await self.session.get(
            url=url,
            params=params,
            impersonate="chrome",
            verify=False,
        )

        if response.status_code in (HTTP_STATUS_UNAUTHORIZED, HTTP_STATUS_FORBIDDEN):
            await self.refresh_session_cookies()
            loaded_cookies = self.load_cookies()
            if loaded_cookies:
                cookies_jar._cookies.update(loaded_cookies)  # noqa
            response = await self.session.get(
                url=url,
                params=params,
                impersonate="chrome",
                verify=False,
            )

        if response.status_code >= 400:
            raise HTTPError(
                f"HTTP Error {response.status_code}: {response.reason}",
                code=response.status_code,  # type: ignore[arg-type]
                response=response,
            )

        return response

    async def close(self):
        """
        Close the underlying HTTP session.
        """
        await self.session.close()
