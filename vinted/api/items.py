"""Item API helpers.

Helpers for fetching detailed information about a single Vinted
item. The module exposes a small wrapper that accepts a public item
URL and returns either a parsed `DetailedItem` or raw JSON.
"""

import logging
from typing import Any, Union
from urllib.parse import urlparse

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
        """Fetch item details.

        Args:
            url: Public Vinted item URL.
            raw_data: If True, return raw JSON dictionary instead of
                a `DetailedItem` instance.

        Returns:
            `DetailedItem` or raw dict depending on `raw_data`.
        """
        self.session.configure_from_url(url)

        product_id = self._extract_product_id(url)
        api_url = f"{self.base_url}/api/v2/items/{product_id}/details"

        logger.debug("Fetching item details: %s", api_url)

        response = await self.session.request(api_url)
        data = response.json()
        item_data: dict[Any, Any] = data.get("item", {})

        logger.debug("Item details fetched successfully")

        if raw_data:
            return item_data

        return DetailedItem(raw_data=item_data)

    @staticmethod
    def _extract_product_id(url: str) -> str:
        """Extract product id from a public item URL path.

        The public path is expected to be `/items/<id>-...` or similar; the
        method extracts the numeric id component.
        """
        path = urlparse(url).path
        return path.split("/")[2].split("-")[0]
