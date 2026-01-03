"""Low-level API base utilities.

This module provides a small base class that stores a shared
`HttpSession` instance used by higher-level API wrappers.
"""

from ..session import HttpSession


class BaseAPI:
    """Base class for API wrappers.

    Args:
        session: An initialized `HttpSession` used to perform HTTP requests.
    """

    def __init__(self, session: HttpSession):
        self.session = session

    @property
    def base_url(self) -> str:
        """Return configured base URL for API requests.

        Raises:
            ValueError: If the session `base_url` is not configured.

        Returns:
            The base URL (scheme + host) derived from the session.
        """
        if not self.session.base_url:
            raise ValueError("Session base_url not configured")
        return self.session.base_url
