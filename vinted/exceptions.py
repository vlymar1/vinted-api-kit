"""Custom exception hierarchy for the library.

Exceptions are lightweight containers surfaceable to client code. The
hierarchy allows callers to catch broad `VintedError` or more specific
errors such as `VintedAPIError` and `VintedNetworkError`.
"""

from curl_cffi.requests import Response


class VintedError(Exception):
    """Base class for all library-specific exceptions."""


class VintedAPIError(VintedError):
    """Raised for non-network API-level failures.

    Args:
        message: Human readable error message.
        status_code: Optional HTTP status code associated with the error.
        response: Optional original `curl_cffi` response object.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: Response | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class VintedAuthError(VintedAPIError):
    """Authentication related API errors (e.g. invalid or expired token)."""


class VintedRateLimitError(VintedAPIError):
    """Raised when the remote API returns a rate-limit (HTTP 429)."""


class VintedNetworkError(VintedError):
    """Wraps lower-level network exceptions.

    Args:
        message: Human readable message describing the failure.
        original_error: The original exception instance from the transport.
    """

    def __init__(self, message: str, original_error: Exception):
        super().__init__(f"{message}: {original_error}")
        self.original_error = original_error


class VintedConfigError(VintedError):
    """Raised for invalid client configuration."""


class VintedValidationError(VintedError):
    """Raised when input validation fails."""
