"""Configuration dataclass for `VintedClient`.

This module provides a small container for client configuration
options such as proxy, cookie storage directory and format.
"""

from dataclasses import dataclass, field
from pathlib import Path

from ..constants import StorageFormat


@dataclass
class ClientConfig:
    """Client configuration values.

    Attributes:
        proxy: Optional proxy string in format `user:pass@host:port`.
        cookies_dir: Directory where cookie files will be stored.
        persist_cookies: Whether to persist cookies to disk.
        storage_format: One of the supported `StorageFormat` literals.
    """

    proxy: str | None = None
    cookies_dir: Path = field(default_factory=lambda: Path("."))
    persist_cookies: bool = False
    storage_format: StorageFormat = "json"

    def __post_init__(self):
        """Normalize and prepare filesystem state.

        Ensures `cookies_dir` is a `Path` instance and creates the
        directory if it does not exist.
        """
        if isinstance(self.cookies_dir, str):
            self.cookies_dir = Path(self.cookies_dir)

        self.cookies_dir.mkdir(parents=True, exist_ok=True)
