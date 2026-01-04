"""JSON-based cookie storage.

Serialises the cookie jar into a JSON mapping and restores it back.
The format is stable and human-readable which helps debugging and
manual inspection of persisted cookies.
"""

import json
import logging
from http.cookiejar import Cookie
from typing import Any, cast

from .base import CookieStorage

logger = logging.getLogger(__name__)


class JsonStorage(CookieStorage):
    """Persist cookies as JSON.

    The JSON representation maps a composite key (`domain|path|name`) to
    a small dictionary describing the cookie attributes. Both `save`
    and `load` are synchronous and may raise on I/O errors.
    """

    def save(self, cookies_jar) -> None:
        """Write cookie jar contents to the configured JSON file.

        Args:
            cookies_jar: Cookie jar object from the HTTP client.
        """
        try:
            jar = cast(Any, cookies_jar)
            cookies_dict = self._jar_to_dict(jar)

            with self.filepath.open("w") as f:
                json.dump(cookies_dict, f, indent=2)
            logger.debug("Cookies saved (json): %s", self.filepath)
        except Exception as e:
            logger.error("Failed to save cookies: %s", e, exc_info=True)
            raise

    def load(self, cookies_jar) -> None:
        """Load cookies from the JSON file into `cookies_jar`.

        If the file does not exist the method returns quietly.
        """
        if not self.exists():
            logger.debug("Cookies file not found: %s", self.filepath)
            return

        try:
            with self.filepath.open("r") as f:
                cookies_dict = json.load(f)

            self._dict_to_jar(cookies_dict, cookies_jar)
            logger.debug("Cookies loaded (json): %s", self.filepath)
        except Exception as e:
            logger.error("Failed to load cookies: %s", e, exc_info=True)
            raise

    @staticmethod
    def _jar_to_dict(jar) -> dict:
        """Convert an internal cookie jar structure to a JSON-serialisable dict."""
        result = {}
        for domain, path_dict in jar._cookies.items():
            for path, name_dict in path_dict.items():
                for name, cookie in name_dict.items():
                    key = f"{domain}|{path}|{name}"
                    result[key] = {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain,
                        "path": cookie.path,
                        "secure": cookie.secure,
                        "expires": cookie.expires,
                        "discard": cookie.discard,
                        "comment": cookie.comment,
                        "comment_url": cookie.comment_url,
                        "rest": getattr(cookie, "rest", {}),
                        "rfc2109": getattr(cookie, "rfc2109", False),
                    }
        return result

    @staticmethod
    def _dict_to_jar(cookies_dict: dict, jar) -> None:
        """Restore cookies from the JSON dict into the cookie jar object."""
        jar.clear()
        for key, data in cookies_dict.items():
            cookie = Cookie(
                version=0,
                name=data["name"],
                value=data["value"],
                port=None,
                port_specified=False,
                domain=data["domain"],
                domain_specified=bool(data["domain"]),
                domain_initial_dot=data["domain"].startswith(".") if data["domain"] else False,
                path=data["path"],
                path_specified=bool(data["path"]),
                secure=data.get("secure", False),
                expires=data.get("expires"),
                discard=data.get("discard", False),
                comment=data.get("comment"),
                comment_url=data.get("comment_url"),
                rest=data.get("rest", {}),
                rfc2109=data.get("rfc2109", False),
            )
            jar.set_cookie(cookie)
