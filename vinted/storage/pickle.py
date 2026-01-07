"""Pickle-based cookie storage.

Serialises the internal cookie jar structure using Python's `pickle`.
This approach is compact and fast but relies on the internal layout of
the cookie jar object and performs binary serialisation.
"""

import logging
import pickle
from typing import Any, cast

from .base import CookieStorage

logger = logging.getLogger(__name__)


class PickleStorage(CookieStorage):
    """Persist internal cookie jar using pickle.

    Note: this implementation stores the cookie jar's internal `_cookies`
    mapping directly. It assumes the cookie jar structure used by the
    HTTP client and performs synchronous file operations.
    """

    def save(self, cookies_jar) -> None:
        """Write internal cookie mapping to a binary pickle file."""
        try:
            jar = cast(Any, cookies_jar)
            with self.filepath.open("wb") as f:
                pickle.dump(jar._cookies, f)  # noqa: S301 - intentional
            logger.debug("Cookies saved (pickle): %s", self.filepath)
        except Exception as e:
            logger.error("Failed to save cookies: %s", e, exc_info=True)
            raise

    def load(self, cookies_jar) -> None:
        """Load and merge a pickled cookies mapping into `cookies_jar`."""
        if not self.exists():
            logger.debug("Cookies file not found: %s", self.filepath)
            return

        try:
            jar = cast(Any, cookies_jar)
            with self.filepath.open("rb") as f:
                cookies = pickle.load(f)
                jar._cookies.update(cookies)
            logger.debug("Cookies loaded (pickle): %s", self.filepath)
        except Exception as e:
            logger.error("Failed to load cookies: %s", e, exc_info=True)
            raise
