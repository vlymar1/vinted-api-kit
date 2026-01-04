"""Authentication helpers.

Utilities for JWT token inspection used by the library to determine
whether an access token stored in the session cookies is expired.
"""

import base64
import json
import logging
from datetime import datetime

from curl_cffi import AsyncSession

logger = logging.getLogger(__name__)


class AuthManager:
    """Manage and inspect authentication tokens.

    Args:
        session: An active `curl_cffi.AsyncSession` used to access cookies.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def is_token_expired(self) -> bool:
        """Return True if there is no access token or it is expired.

        Reads the `access_token_web` cookie from the session and checks the
        JWT `exp` claim. If the token is missing or cannot be decoded the
        method returns True (treated as expired).
        """
        access_token = self.session.cookies.get("access_token_web")
        if not access_token:
            return True

        return self._validate_jwt_expiration(access_token)

    @staticmethod
    def _validate_jwt_expiration(token: str) -> bool:
        """Decode a JWT payload and return True when the token is expired.

        The function expects a three-part JWT and uses URL-safe base64
        decoding with padding correction. On any decoding error the token is
        considered expired.

        Args:
            token: JWT string.

        Returns:
            True if current time is greater or equal to the `exp` claim or
            if the token cannot be decoded; otherwise False.
        """
        try:
            payload_b64 = token.split(".")[1]

            padding_needed = (4 - len(payload_b64) % 4) % 4
            payload_b64 += "=" * padding_needed

            payload = json.loads(base64.urlsafe_b64decode(payload_b64))

            exp_timestamp = payload.get("exp", 0)
            current_timestamp = datetime.now().timestamp()
            result: bool = current_timestamp >= exp_timestamp

            return result
        except Exception as e:
            logger.debug("Failed to validate JWT token: %s", e)
            return True
