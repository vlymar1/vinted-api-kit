from vinted_api_kit.client import VintedHttpClient
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

    async def search_items(self, *args, **kwargs):
        """
        Search items on Vinted (convenience wrapper).
        """
        return await self._items_service.search_items(*args, **kwargs)

    async def get_item_details(self, *args, **kwargs):
        """
        Get detailed item info (convenience wrapper).
        """
        return await self._items_service.get_item_details(*args, **kwargs)
