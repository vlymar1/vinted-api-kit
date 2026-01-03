"""Mozilla cookie file storage.

Provides saving/loading cookies in the `MozillaCookieJar` format so
that persisted cookies can be shared with browsers or other tools that
read Netscape/Mozilla cookie files.
"""

import logging
from http.cookiejar import Cookie, MozillaCookieJar

from .base import CookieStorage

logger = logging.getLogger(__name__)


class MozillaStorage(CookieStorage):
    """Persist cookies in Mozilla/Netscape cookiejar format.

    Useful when interoperating with browser tools. Both `save` and
    `load` are synchronous file operations and will raise on I/O errors.
    """

    def save(self, cookies_jar) -> None:
        """Save cookies into a `MozillaCookieJar` file."""
        try:
            jar = MozillaCookieJar(str(self.filepath))

            for domain, path_dict in cookies_jar._cookies.items():
                for path, name_dict in path_dict.items():
                    for name, cookie in name_dict.items():
                        new_cookie = Cookie(
                            version=0,
                            name=cookie.name,
                            value=cookie.value,
                            port=None,
                            port_specified=False,
                            domain=cookie.domain,
                            domain_specified=bool(cookie.domain),
                            domain_initial_dot=cookie.domain.startswith(".")
                            if cookie.domain
                            else False,
                            path=cookie.path,
                            path_specified=bool(cookie.path),
                            secure=cookie.secure,
                            expires=cookie.expires,
                            discard=cookie.discard,
                            comment=cookie.comment,
                            comment_url=cookie.comment_url,
                            rest=getattr(cookie, "rest", {}),
                            rfc2109=getattr(cookie, "rfc2109", False),
                        )
                        jar.set_cookie(new_cookie)

            jar.save(ignore_discard=True, ignore_expires=True)
            logger.debug("Cookies saved (mozilla): %s", self.filepath)
        except Exception as e:
            logger.error("Failed to save cookies: %s", e, exc_info=True)
            raise

    def load(self, cookies_jar) -> None:
        """Load cookies from a `MozillaCookieJar` file into `cookies_jar`."""
        if not self.exists():
            logger.debug("Cookies file not found: %s", self.filepath)
            return

        try:
            jar = MozillaCookieJar(str(self.filepath))
            jar.load(ignore_discard=True, ignore_expires=True)

            cookies_jar.clear()
            for cookie in jar:
                cookies_jar.set_cookie(cookie)

            logger.debug("Cookies loaded (mozilla): %s", self.filepath)
        except Exception as e:
            logger.error("Failed to load cookies: %s", e, exc_info=True)
            raise
