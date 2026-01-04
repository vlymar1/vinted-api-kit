"""Abstract cookie storage interface.

Provides an abstract base class for persisting a cookie jar to disk
in different formats (pickle, json, mozilla). Implementations must
implement `save` and `load` and receive a `filepath` to operate on.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class CookieStorage(ABC):
    """Base interface for cookie storage backends.

    Subclasses must implement `save` and `load`. Concrete storage
    classes are responsible for serialising/deserialising the cookie
    jar passed by the HTTP client.

    Args:
        filepath: Path to the file used for persisting cookies.
    """

    def __init__(self, filepath: Path):
        self.filepath = filepath

    @abstractmethod
    def save(self, cookies_jar) -> None:
        """Persist cookies from `cookies_jar` to disk.

        Implementations should raise on unrecoverable errors.
        """

    @abstractmethod
    def load(self, cookies_jar) -> None:
        """Load cookies from disk into the provided `cookies_jar`.

        Implementations should be tolerant to missing or corrupted
        files and raise only when appropriate.
        """

    def exists(self) -> bool:
        """Return True when the underlying cookie file exists on disk."""
        return self.filepath.is_file()

    def clear(self) -> None:
        """Delete the underlying cookie file if present and log the action."""
        if self.exists():
            self.filepath.unlink()
            logger.debug(f"Cookies file deleted: {self.filepath}")
