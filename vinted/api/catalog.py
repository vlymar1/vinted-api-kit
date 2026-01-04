"""Catalog API helpers.

This module implements a thin wrapper around the Vinted catalog
endpoint. It constructs request parameters from a user-provided URL
and returns either raw JSON items or parsed `CatalogItem` instances.
"""

import logging
import time
from typing import Any, Union
from urllib.parse import parse_qsl, urlparse

from ..constants import SortOrder
from ..models import CatalogItem
from .base import BaseAPI

logger = logging.getLogger(__name__)


class CatalogAPI(BaseAPI):
    """Interaction with catalog listing endpoints.

    Methods in this class accept a public Vinted URL and translate it
    into the corresponding API call.
    """

    async def search(
        self,
        url: str,
        per_page: int = 20,
        page: int = 1,
        timestamp: int | None = None,
        order: SortOrder | None = None,
        raw_data: bool = False,
    ) -> Union[list[CatalogItem], list[dict]]:
        """Search catalog items.

        Args:
            url: Public Vinted URL with search filters.
            per_page: Number of items per page.
            page: Page number to fetch.
            timestamp: Optional timestamp to include in request.
            order: Optional order specifier from `SortOrder`.
            raw_data: If True, return raw dictionaries instead of `CatalogItem`.

        Returns:
            List of `CatalogItem` instances or raw item dicts.
        """
        self.session.configure_from_url(url)
        api_url = f"{self.base_url}/api/v2/catalog/items"

        params = self._build_params(url, per_page, page)
        params["time"] = timestamp or int(time.time())

        if order:
            params["order"] = order

        logger.debug("Searching catalog: url=%s, params=%s", api_url, params)

        response = await self.session.request(api_url, params=params)
        data = response.json()
        items: list[dict[Any, Any]] = data.get("items", [])

        logger.debug("Found %d items", len(items))

        if raw_data:
            return items

        return [CatalogItem(raw_data=item) for item in items]

    def _build_params(self, url: str, per_page: int, page: int) -> dict:
        """Build API query params from a public catalog URL.

        The method extracts query parameters and path elements to create
        a dictionary suitable for the internal API endpoint.
        """
        parsed = urlparse(url)
        query_params = parse_qsl(parsed.query)

        catalog_id = self._extract_catalog_id(parsed.path)
        catalog_ids_query = self._join_values(query_params, "catalog[]")

        params = {
            "search_text": "+".join(self._extract_values(query_params, "search_text")),
            "catalog_ids": str(catalog_id) if catalog_id else catalog_ids_query,
            "color_ids": self._join_values(query_params, "color_ids[]"),
            "brand_ids": self._join_values(query_params, "brand_ids[]"),
            "size_ids": self._join_values(query_params, "size_ids[]"),
            "material_ids": self._join_values(query_params, "material_ids[]"),
            "status_ids": self._join_values(query_params, "status[]"),
            "country_ids": self._join_values(query_params, "country_ids[]"),
            "city_ids": self._join_values(query_params, "city_ids[]"),
            "is_for_swap": ",".join("1" for _ in self._extract_values(query_params, "disposal[]")),
            "currency": self._join_values(query_params, "currency"),
            "price_to": self._join_values(query_params, "price_to"),
            "price_from": self._join_values(query_params, "price_from"),
            "page": page,
            "per_page": per_page,
            "order": self._join_values(query_params, "order"),
        }

        return {k: v for k, v in params.items() if v}

    @staticmethod
    def _extract_catalog_id(path: str) -> int | None:
        """Extract catalog id from path if present.

        Path format is expected to be `/catalog/<id>-...`. Returns `None`
        when parsing fails.
        """
        parts = path.split("/")
        if len(parts) > 2 and parts[1] == "catalog":
            catalog_part = parts[2]
            catalog_id_str = catalog_part.split("-")[0]
            try:
                return int(catalog_id_str)
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_values(query_params: list[tuple[str, str]], key: str) -> list[str]:
        """Return list of values for a given query key."""
        return [v for k, v in query_params if k == key]

    def _join_values(self, query_params: list[tuple[str, str]], key: str) -> str:
        """Join multiple values for a query key with commas."""
        values = self._extract_values(query_params, key)
        return ",".join(values)
