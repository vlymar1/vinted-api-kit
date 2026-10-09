"""Item API helpers.

Helpers for fetching detailed information about a single Vinted
item. The module exposes a small wrapper that accepts a public item
URL and returns either a parsed `DetailedItem` or raw JSON.
"""

import logging
from typing import Union
from urllib.parse import urlparse

from vinted.exceptions import VintedDeprecatedError, VintedValidationError

from ..models import DetailedItem
from .base import BaseAPI

logger = logging.getLogger(__name__)


class ItemsAPI(BaseAPI):
    """API wrapper for item details endpoint.

    Methods accept a public item URL and perform the internal API call
    to retrieve detailed item data.
    """

    async def get_details(
        self,
        url: str,
        raw_data: bool = False,
    ) -> Union[DetailedItem, dict]:
        """Deprecated: always raises `VintedDeprecatedError`.

        Vinted removed the item details API endpoint.

        Args:
            url: Public Vinted item URL.
            raw_data: If True, return raw JSON dictionary instead of
                a `DetailedItem` instance.
        """
        raise VintedDeprecatedError(
            "item_details() no longer works: Vinted removed the item details API"
        )

    @staticmethod
    def _extract_product_id(url: str) -> str:
        """Extract product id from a public item URL path.

        The public path is expected to be `/items/<id>-...` or similar; the
        method extracts the numeric id component.
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise VintedValidationError("Invalid item URL: expected an absolute HTTP(S) URL")

        if len(path_parts) < 2 or path_parts[0] != "items":
            raise VintedValidationError("Invalid item URL: expected path '/items/<id>'")

        product_id = path_parts[1].split("-")[0]
        if not product_id.isdigit():
            raise VintedValidationError("Invalid item URL: item id must be numeric")

        return product_id
