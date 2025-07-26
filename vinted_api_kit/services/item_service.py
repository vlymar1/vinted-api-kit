import time
from typing import Optional, Union
from urllib.parse import parse_qsl, urlparse

from curl_cffi.requests.exceptions import HTTPError

from vinted_api_kit.client import VintedHttpClient
from vinted_api_kit.models import CatalogItem, DetailedItem


class ItemService:
    """
    Provides item-related operations using the VintedHttpClient.
    """

    VALID_ORDERS = {"newest_first", "relevance", "price_high_to_low", "price_low_to_high"}

    def __init__(self, client: VintedHttpClient):
        """
        Initialize service with HTTP client.

        Args:
            client (VintedHttpClient): HTTP client instance.
        """
        self.client = client

    async def search_items(
        self,
        url: str,
        per_page: int = 20,
        page: int = 1,
        timestamp: Optional[int] = None,
        raw_data: bool = False,
        order: Optional[str] = None,
    ) -> Union[list[CatalogItem], list[dict], None]:
        """
        Search items on Vinted.

        Args:
            url (str): URL with search filters.
            per_page (int): Items per page.
            page (int): Page number.
            timestamp (Optional[int]): Unix timestamp override.
            raw_data (bool): Return raw JSON data if True.
            order (str): Sorting order.

        Returns:
            List of CatalogItem or raw data list.
        """
        if order and order not in self.VALID_ORDERS:
            raise ValueError(
                f"Invalid order '{order}'. Valid options are: {', '.join(self.VALID_ORDERS)}"
            )
        self.client.configure_from_url(url)
        api_url = f"{self.client.base_url}/api/v2/catalog/items"
        params = self._parse_url(url, per_page=per_page, page=page)
        params["time"] = timestamp or int(time.time())
        if order:
            params["order"] = order
        response = await self.client.request(api_url, params=params)
        data = response.json()
        items = data.get("items", [])

        if raw_data:
            from typing import Any, cast

            return cast(list[dict[str, Any]], items)
        return [CatalogItem(item) for item in items] if items else []

    async def get_item_details(
        self, url: str, raw_data: bool = False
    ) -> Union[DetailedItem, dict]:
        """
        Get detailed info of an item by URL.

        Args:
            url (str): Item URL.
            raw_data (bool): Return raw JSON if True.

        Returns:
            DetailedItem instance or raw dict.
        """
        self.client.configure_from_url(url)
        product_id = urlparse(url).path.split("/")[2].split("-")[0]
        api_url = f"{self.client.base_url}/api/v2/items/{product_id}/details"

        try:
            response = await self.client.request(api_url)
            response.raise_for_status()
            data = response.json()
            product_data = data.get("item", [])
            return DetailedItem(product_data) if not raw_data else product_data
        except HTTPError as err:
            raise err

    def _parse_url(self, url: str, per_page: int = 20, page: int = 1) -> dict:
        """
        Parse and build API query parameters from URL.

        Args:
            url (str): URL to parse.
            per_page (int): Items per page.
            page (int): Page number.

        Returns:
            Dict with query parameters.
        """
        parsed_url = urlparse(url)
        query_params = parse_qsl(parsed_url.query)

        catalog_id = self._extract_catalog_id(parsed_url.path)
        catalog_ids_from_query = self._join_query_values(query_params, "catalog[]")

        params = {
            "search_text": "+".join(self._extract_query_values(query_params, "search_text")),
            "catalog_ids": str(catalog_id) if catalog_id is not None else catalog_ids_from_query,
            "color_ids": self._join_query_values(query_params, "color_ids[]"),
            "brand_ids": self._join_query_values(query_params, "brand_ids[]"),
            "size_ids": self._join_query_values(query_params, "size_ids[]"),
            "material_ids": self._join_query_values(query_params, "material_ids[]"),
            "status_ids": self._join_query_values(query_params, "status[]"),
            "country_ids": self._join_query_values(query_params, "country_ids[]"),
            "city_ids": self._join_query_values(query_params, "city_ids[]"),
            "is_for_swap": ",".join(
                "1" for _ in self._extract_query_values(query_params, "disposal[]")
            ),
            "currency": self._join_query_values(query_params, "currency"),
            "price_to": self._join_query_values(query_params, "price_to"),
            "price_from": self._join_query_values(query_params, "price_from"),
            "page": page,
            "per_page": per_page,
            "order": self._join_query_values(query_params, "order"),
            "time": int(time.time()),
        }

        params_cleaned = {k: v for k, v in params.items() if v}
        return params_cleaned

    @staticmethod
    def _extract_catalog_id(path: str) -> Optional[int]:
        """
        Extract catalog ID from URL path.

        Args:
            path (str): URL path string.

        Returns:
            Catalog ID as int or None if missing.
        """
        path_parts = path.split("/")
        if len(path_parts) > 2 and path_parts[1] == "catalog":
            catalog_part = path_parts[2]
            catalog_id_str = catalog_part.split("-")[0] if "-" in catalog_part else catalog_part
            try:
                return int(catalog_id_str)
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_product_id_from_url(url: str) -> str:
        """
        Extract product ID from item URL.

        Args:
            url (str): Item URL string.

        Returns:
            Product ID string.
        """
        path = urlparse(url).path
        return path.split("/")[2].split("-")[0]

    @staticmethod
    def _extract_query_values(query_params: list[tuple[str, str]], key: str) -> list[str]:
        """
        Get all values for a query key.

        Args:
            query_params (list of tuple): Parsed query pairs.
            key (str): Key to find.

        Returns:
            List of values as strings.
        """
        return [v for k, v in query_params if k == key]

    def _join_query_values(
        self, query_params: list[tuple[str, str]], key: str, sep: str = ","
    ) -> str:
        """
        Join multiple query values for a key into a string.

        Args:
            query_params (list of tuple): Parsed queries.
            key (str): Key to find.
            sep (str): Separator to join strings.

        Returns:
            Joined string or empty string if none.
        """
        values = self._extract_query_values(query_params, key)
        return sep.join(values)
