"""Seller API helpers.

This module wraps the Vinted user profile and wardrobe endpoints. A
seller is identified by a public profile URL such as
`https://www.vinted.com/member/<id>-<login>`.
"""

import logging
from typing import Union
from urllib.parse import urlparse

from vinted.exceptions import VintedValidationError

from ..constants import SortOrder
from ..models import CatalogItem, Seller
from .base import BaseAPI

logger = logging.getLogger(__name__)


class SellerAPI(BaseAPI):
    """Interaction with seller profile and wardrobe endpoints."""

    async def get_info(
        self,
        url: str,
        raw_data: bool = False,
    ) -> Union[Seller, dict]:
        """Fetch a seller profile.

        Args:
            url: Public seller profile URL.
            raw_data: If True, return the raw user dict instead of `Seller`.

        Returns:
            A `Seller` instance or the raw user dict.
        """
        seller_id = self._extract_seller_id(url)
        self.session.configure_from_url(url)

        response = await self.session.request(f"{self.base_url}/api/v2/users/{seller_id}")
        user: dict = response.json().get("user", {})

        if raw_data:
            return user

        return Seller(raw_data=user)

    async def get_items(
        self,
        url: str,
        per_page: int = 20,
        page: int = 1,
        order: SortOrder | None = None,
        raw_data: bool = False,
    ) -> Union[list[CatalogItem], list[dict]]:
        """Fetch items listed by a seller.

        Only items visible on the Vinted domain of `url` are returned, so
        the list may be empty on another market. Vinted currently ignores
        `newest_first` here and returns the `relevance` order.

        Args:
            url: Public seller profile URL.
            per_page: Number of items per page (Vinted caps it at 96).
            page: Page number to fetch.
            order: Optional order specifier from `SortOrder`.
            raw_data: If True, return raw dicts instead of `CatalogItem`.

        Returns:
            List of `CatalogItem` instances or raw item dicts.
        """
        seller_id = self._extract_seller_id(url)
        self.session.configure_from_url(url)

        params: dict = {"page": page, "per_page": per_page}
        if order:
            params["order"] = order

        api_url = f"{self.base_url}/api/v2/wardrobe/{seller_id}/items"
        logger.debug("Fetching seller items: url=%s, params=%s", api_url, params)

        response = await self.session.request(api_url, params=params)
        items: list[dict] = response.json().get("items", [])

        logger.debug("Found %d items", len(items))

        if raw_data:
            return items

        return [CatalogItem(raw_data=item) for item in items]

    @staticmethod
    def _extract_seller_id(url: str) -> str:
        """Extract the seller id from a `/member/<id>-<login>` URL path."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise VintedValidationError("Invalid seller URL: expected an absolute HTTP(S) URL")

        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2 or path_parts[0] != "member":
            raise VintedValidationError("Invalid seller URL: expected path '/member/<id>'")

        seller_id = path_parts[1].split("-")[0]
        if not seller_id.isdigit():
            raise VintedValidationError("Invalid seller URL: seller id must be numeric")

        return seller_id
