"""Catalog API helpers.

This module implements a thin wrapper around the Vinted catalog
endpoint. It constructs request parameters from a user-provided URL
and returns either raw JSON items or parsed `CatalogItem` instances.
"""

import logging
import time
from typing import Any, Union
from urllib.parse import parse_qsl, urljoin, urlparse

from vinted.exceptions import VintedValidationError

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
        self._validate_catalog_url(url)
        self.session.configure_from_url(url)
        api_url = f"{self.base_url}/web/gateway/svc-catalogue/items"

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

        catalog_items = [CatalogItem(raw_data=item) for item in items]
        for catalog_item in catalog_items:
            catalog_item.url = urljoin(f"{self.base_url}/", catalog_item.url)

        return catalog_items

    def _build_params(self, url: str, per_page: int, page: int) -> dict:
        """Build API query params from a public catalog URL.

        The method extracts query parameters and path elements to create
        a dictionary suitable for the internal API endpoint.
        """
        parsed = urlparse(url)
        query_params = parse_qsl(parsed.query)

        catalog_id = self._extract_catalog_id(parsed.path)
        catalog_ids_query = self._join_values(query_params, "catalog[]")

        status_ids = self._extract_values(query_params, "status_ids[]") + self._extract_values(
            query_params, "status[]"
        )

        params = {
            "search_text": "+".join(self._extract_values(query_params, "search_text")),
            "attribute_ids[catalog]": str(catalog_id) if catalog_id else catalog_ids_query,
            "attribute_ids[color]": self._join_values(query_params, "color_ids[]"),
            "attribute_ids[brand]": self._join_values(query_params, "brand_ids[]"),
            "attribute_ids[size]": self._join_values(query_params, "size_ids[]"),
            "attribute_ids[material]": self._join_values(query_params, "material_ids[]"),
            "attribute_ids[status]": ",".join(status_ids),
            "attribute_ids[patterns]": self._join_values(query_params, "patterns_ids[]"),
            "currency": self._join_values(query_params, "currency"),
            "price_to": self._join_values(query_params, "price_to"),
            "price_from": self._join_values(query_params, "price_from"),
            "page": page,
            "per_page": per_page,
            "order": self._join_values(query_params, "order"),
        }

        return {k: v for k, v in params.items() if v}

    @staticmethod
    def _validate_catalog_url(url: str) -> None:
        """Validate basic catalog URL shape without restricting the domain."""
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise VintedValidationError("Invalid catalog URL: expected an absolute HTTP(S) URL")

        path = parsed.path.rstrip("/")
        if path and not path.startswith("/catalog"):
            raise VintedValidationError("Invalid catalog URL: expected path '/catalog'")

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
