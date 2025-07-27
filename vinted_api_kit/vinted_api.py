from typing import Optional, Union

from vinted_api_kit.client import VintedHttpClient
from vinted_api_kit.models import CatalogItem, DetailedItem
from vinted_api_kit.services import ItemService


class VintedApi:
    """
    Facade class providing async context management for Vinted API client and services.
    """

    def __init__(
        self, locale=None, proxies=None, client_ip=None, cookies_dir=None, persist_cookies=False
    ):
        """
        Initialize VintedApi with client configuration.

        Args:
            locale (str, optional): Locale for API requests.
            proxies (dict, optional): Proxy configuration.
            client_ip (str, optional): Client IP for headers.
            cookies_dir (str, optional): Directory for storing cookies.
            persist_cookies (bool, optional): Whether to save cookies to disk.
        """
        self._client = VintedHttpClient(
            locale=locale,
            proxies=proxies,
            client_ip=client_ip,
            cookies_dir=cookies_dir,
            persist_cookies=persist_cookies,
        )
        self._items_service = ItemService(self._client)

    async def __aenter__(self):
        """
        Enter async context, return self.
        """
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Exit async context, close the client session.

        Args:
            exc_type: Exception type if any.
            exc_value: Exception value if any.
            traceback: Traceback if any.

        Returns:
            False (do not suppress exceptions)
        """
        await self._client.close()
        return False

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
        return await self._items_service.search_items(
            url, per_page, page, timestamp, raw_data, order
        )

    async def get_item_details(
        self, url: str, raw_data: bool = False
    ) -> Union[DetailedItem, dict]:
        """
        Get detailed information of an item by URL.

        Args:
            url (str): Item URL.
            raw_data (bool): Return raw JSON if True.

        Returns:
            DetailedItem or raw dict.
        """
        return await self._items_service.get_item_details(url, raw_data)
